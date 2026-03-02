#!/usr/bin/env python3
"""
Compare CLASS output files between a reference directory and a test directory.

For each .dat file present in both directories, reads the numeric columns and
computes the maximum relative difference per column. Reports PASS/FAIL per
file based on configurable tolerances.

Handles cross-version comparison where:
  - Column counts may differ (matches by column name)
  - Row grids may differ (interpolates test onto reference grid)
  - Spectra may cross zero (uses scale-aware relative difference)

Usage:
    python compare_outputs.py --reference <ref_dir> --test <test_dir> \
        [--bg-tolerance 0.0001] [--cl-tolerance 0.001] [--pk-tolerance 0.001]
"""

import argparse
import os
import re
import sys
import numpy as np


def classify_file(filename):
    """Classify a CLASS output file by its content type based on filename."""
    name = filename.lower()
    if "background" in name:
        return "background"
    if "pk" in name or "power_spectrum" in name:
        return "pk"
    if "cl" in name:
        return "cl"
    return "unknown"


def read_class_dat(filepath):
    """Read a CLASS .dat file, skipping comment lines starting with '#'.

    Returns (header_lines, data) where header_lines is a list of comment
    lines and data is a 2D numpy array of shape (nrows, ncols).
    """
    header_lines = []
    data_lines = []
    with open(filepath, "r") as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("#"):
                header_lines.append(stripped)
            else:
                data_lines.append(stripped)

    if not data_lines:
        return header_lines, np.array([])

    data = []
    for line in data_lines:
        vals = line.split()
        try:
            row = [float(v) for v in vals]
            data.append(row)
        except ValueError:
            continue

    return header_lines, np.array(data) if data else np.array([])


def column_names_from_header(header_lines):
    """Extract column names from the last comment line (CLASS convention).

    CLASS headers use the format: # 1:name1  2:name with spaces  3:name [unit]
    """
    if not header_lines:
        return []
    last = header_lines[-1].lstrip("#").strip()
    parts = re.split(r'\s+(?=\d+:)', last)
    return [p.strip() for p in parts if p.strip()]


def strip_col_number(col_name):
    """Strip the leading 'N:' from a column name, returning just the name."""
    m = re.match(r'\d+:(.*)', col_name)
    return m.group(1).strip() if m else col_name.strip()


def match_columns_by_name(ref_names, test_names):
    """Match columns between ref and test by their stripped names.

    Returns (ref_indices, test_indices, matched_names) for columns
    that appear in both, preserving the ref ordering.
    """
    ref_stripped = [(i, strip_col_number(n)) for i, n in enumerate(ref_names)]
    test_map = {}
    for i, n in enumerate(test_names):
        sn = strip_col_number(n)
        test_map[sn] = i

    ref_indices = []
    test_indices = []
    matched_names = []
    for ri, rn in ref_stripped:
        if rn in test_map:
            ref_indices.append(ri)
            test_indices.append(test_map[rn])
            matched_names.append(rn)

    return ref_indices, test_indices, matched_names


def interpolate_to_ref_grid(ref_x, ref_data, test_x, test_data, col_indices):
    """Interpolate test columns onto the reference x-grid.

    Uses linear interpolation in log-log space for positive-definite data
    and linear interpolation in linear space otherwise. Only interpolates
    within the overlapping range.

    Returns (common_ref_data, interpolated_test_data, valid_mask) where
    valid_mask indicates rows that are within the overlapping range.
    """
    x_min = max(ref_x.min(), test_x.min())
    x_max = min(ref_x.max(), test_x.max())
    valid = (ref_x >= x_min * 0.999) & (ref_x <= x_max * 1.001)

    ref_x_valid = ref_x[valid]
    interp_data = np.zeros((valid.sum(), len(col_indices)))

    for i, ci in enumerate(col_indices):
        test_col = test_data[:, ci]
        ref_col_valid = ref_data[valid, col_indices[i] if i < len(col_indices) else ci]

        all_positive = np.all(test_col > 0) and np.all(ref_col_valid > 0)

        if all_positive and np.all(test_x > 0) and np.all(ref_x_valid > 0):
            interp_data[:, i] = np.exp(np.interp(
                np.log(ref_x_valid), np.log(test_x), np.log(test_col)
            ))
        else:
            interp_data[:, i] = np.interp(ref_x_valid, test_x, test_col)

    return ref_data[valid], interp_data, valid


def compute_relative_diff(ref_col, test_col):
    """Compute scale-aware maximum relative difference for a single column.

    Uses |ref - test| / scale where scale = max(|ref|, |test|, floor).
    The floor prevents division by zero near zero crossings and is set
    to 1e-4 * max(|ref|) across the full column.
    """
    abs_diff = np.abs(ref_col - test_col)
    peak = max(np.max(np.abs(ref_col)), np.max(np.abs(test_col)), 1e-100)
    floor = 1e-4 * peak
    scale = np.maximum(np.maximum(np.abs(ref_col), np.abs(test_col)), floor)
    rel = abs_diff / scale
    return np.max(rel)


def find_matching_files(ref_dir, test_dir):
    """Find .dat files that exist in both directories.

    Matches by file type suffix (background, cl, cl_lensed, pk),
    handling different CLASS naming conventions.
    """
    ref_files = {f for f in os.listdir(ref_dir) if f.endswith(".dat")}
    test_files = {f for f in os.listdir(test_dir) if f.endswith(".dat")}

    direct_matches = ref_files & test_files
    if direct_matches:
        return sorted(direct_matches)

    known_types = ["cl_lensed", "background", "cl", "pk"]

    def type_key(fname):
        base = fname[:-4]
        for t in known_types:
            if base.endswith(t):
                return t
        return fname

    ref_by_type = {}
    for f in ref_files:
        ref_by_type[type_key(f)] = f

    test_by_type = {}
    for f in test_files:
        test_by_type[type_key(f)] = f

    matches = []
    for key in sorted(set(ref_by_type.keys()) & set(test_by_type.keys())):
        matches.append((ref_by_type[key], test_by_type[key]))

    return matches


def compare_file(ref_path, test_path, ref_name, file_type, tol):
    """Compare a single pair of files. Returns True if all columns pass."""

    ref_headers, ref_data = read_class_dat(ref_path)
    test_headers, test_data = read_class_dat(test_path)

    ref_col_names = column_names_from_header(ref_headers)
    test_col_names = column_names_from_header(test_headers)

    print(f"--- {ref_name} (type: {file_type}, tolerance: {tol*100:.4f}%) ---")

    if ref_data.size == 0:
        print("  SKIP: No numeric data in reference file.")
        return True
    if test_data.size == 0:
        print("  FAIL: No numeric data in test file.")
        return False

    use_name_matching = (ref_data.shape[1] != test_data.shape[1]) and ref_col_names and test_col_names
    if use_name_matching:
        ref_idx, test_idx, matched = match_columns_by_name(ref_col_names, test_col_names)
        print(f"  INFO: Column counts differ (ref={ref_data.shape[1]}, test={test_data.shape[1]}). "
              f"Matching {len(matched)} columns by name.")
    else:
        ncols = min(ref_data.shape[1], test_data.shape[1])
        ref_idx = list(range(ncols))
        test_idx = list(range(ncols))
        matched = [strip_col_number(ref_col_names[i]) if i < len(ref_col_names) else f"col_{i}"
                    for i in range(ncols)]
        if ref_data.shape[1] != test_data.shape[1]:
            print(f"  WARNING: Column count differs (ref={ref_data.shape[1]}, test={test_data.shape[1]}).")

    needs_interpolation = (ref_data.shape[0] != test_data.shape[0])
    if not needs_interpolation:
        first_ref_col = ref_data[:, ref_idx[0]]
        first_test_col = test_data[:, test_idx[0]]
        if np.max(np.abs(first_ref_col - first_test_col)) > 1e-10 * np.max(np.abs(first_ref_col)):
            needs_interpolation = True

    if needs_interpolation and len(ref_idx) > 1:
        ref_x = ref_data[:, ref_idx[0]]
        test_x = test_data[:, test_idx[0]]

        # np.interp requires ascending x; reverse if descending
        if ref_x[0] > ref_x[-1]:
            ref_data = ref_data[::-1]
            ref_x = ref_x[::-1]
        if test_x[0] > test_x[-1]:
            test_data_sorted = test_data[::-1]
            test_x = test_x[::-1]
        else:
            test_data_sorted = test_data

        print(f"  INFO: Grids differ (ref={ref_data.shape[0]} rows, test={test_data_sorted.shape[0]} rows). "
              f"Interpolating test onto reference grid in overlap region.")

        x_min = max(ref_x.min(), test_x.min())
        x_max = min(ref_x.max(), test_x.max())
        valid = (ref_x >= x_min * 0.999) & (ref_x <= x_max * 1.001)
        ref_x_valid = ref_x[valid]

        if valid.sum() == 0:
            print("  FAIL: No overlapping range between grids.")
            return False

        print(f"  INFO: Comparing {valid.sum()} points in range [{x_min:.4e}, {x_max:.4e}].")

        file_pass = True
        name0 = matched[0]
        x_diff = compute_relative_diff(ref_x_valid, np.interp(ref_x_valid, test_x, test_x))
        status = "PASS" if x_diff <= tol else "FAIL"
        if status == "FAIL":
            file_pass = False
        print(f"  {status}  {name0:>30s}  max_rel_diff = {x_diff:.6e}")

        for j in range(1, len(ref_idx)):
            ri, ti = ref_idx[j], test_idx[j]
            ref_col = ref_data[valid, ri]
            test_col_raw = test_data_sorted[:, ti]

            all_positive = np.all(test_col_raw > 0) and np.all(ref_col > 0)
            if all_positive and np.all(test_x > 0) and np.all(ref_x_valid > 0):
                test_col = np.exp(np.interp(
                    np.log(ref_x_valid), np.log(test_x), np.log(test_col_raw)
                ))
            else:
                test_col = np.interp(ref_x_valid, test_x, test_col_raw)

            max_diff = compute_relative_diff(ref_col, test_col)
            name = matched[j]
            status = "PASS" if max_diff <= tol else "FAIL"
            if status == "FAIL":
                file_pass = False
            print(f"  {status}  {name:>30s}  max_rel_diff = {max_diff:.6e}")

        return file_pass

    nrows = min(ref_data.shape[0], test_data.shape[0])
    if ref_data.shape[0] != test_data.shape[0]:
        print(f"  WARNING: Row count differs (ref={ref_data.shape[0]}, test={test_data.shape[0]}). "
              f"Comparing first {nrows} rows.")

    file_pass = True
    for j in range(len(ref_idx)):
        ri, ti = ref_idx[j], test_idx[j]
        ref_col = ref_data[:nrows, ri]
        test_col = test_data[:nrows, ti]
        max_diff = compute_relative_diff(ref_col, test_col)
        name = matched[j]
        status = "PASS" if max_diff <= tol else "FAIL"
        if status == "FAIL":
            file_pass = False
        print(f"  {status}  {name:>30s}  max_rel_diff = {max_diff:.6e}")

    return file_pass


def main():
    parser = argparse.ArgumentParser(description="Compare CLASS output files")
    parser.add_argument("--reference", required=True, help="Reference output directory")
    parser.add_argument("--test", required=True, help="Test output directory")
    parser.add_argument("--bg-tolerance", type=float, default=0.0001,
                        help="Relative tolerance for background files (default: 0.0001 = 0.01%%)")
    parser.add_argument("--cl-tolerance", type=float, default=0.001,
                        help="Relative tolerance for Cl files (default: 0.001 = 0.1%%)")
    parser.add_argument("--pk-tolerance", type=float, default=0.001,
                        help="Relative tolerance for P(k) files (default: 0.001 = 0.1%%)")
    args = parser.parse_args()

    if not os.path.isdir(args.reference):
        print(f"ERROR: Reference directory not found: {args.reference}")
        sys.exit(1)
    if not os.path.isdir(args.test):
        print(f"ERROR: Test directory not found: {args.test}")
        sys.exit(1)

    tolerances = {
        "background": args.bg_tolerance,
        "cl": args.cl_tolerance,
        "pk": args.pk_tolerance,
        "unknown": args.cl_tolerance,
    }

    matches = find_matching_files(args.reference, args.test)

    if not matches:
        print("ERROR: No matching .dat files found between reference and test directories.")
        print(f"  Reference files: {sorted(os.listdir(args.reference))}")
        print(f"  Test files: {sorted(os.listdir(args.test))}")
        sys.exit(1)

    all_pass = True
    print(f"\n{'='*70}")
    print(f"CLASS Output Comparison")
    print(f"  Reference: {args.reference}")
    print(f"  Test:      {args.test}")
    print(f"{'='*70}\n")

    for match in matches:
        if isinstance(match, tuple):
            ref_name, test_name = match
        else:
            ref_name = test_name = match

        ref_path = os.path.join(args.reference, ref_name)
        test_path = os.path.join(args.test, test_name)

        file_type = classify_file(ref_name)
        tol = tolerances[file_type]

        file_pass = compare_file(ref_path, test_path, ref_name, file_type, tol)
        if not file_pass:
            all_pass = False
        print()

    print(f"{'='*70}")
    if all_pass:
        print("OVERALL: PASS")
    else:
        print("OVERALL: FAIL")
    print(f"{'='*70}")

    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
