#!/usr/bin/env python3
"""
Compare CLASS output files between a reference directory and a test directory.

For each .dat file present in both directories, reads the numeric columns and
computes the maximum relative difference per column. Reports PASS/FAIL per
file based on configurable tolerances.

Usage:
    python compare_outputs.py --reference <ref_dir> --test <test_dir> \
        [--bg-tolerance 0.0001] [--cl-tolerance 0.001] [--pk-tolerance 0.001]
"""

import argparse
import os
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
    Column names are delimited by the N: prefix pattern.
    """
    import re
    if not header_lines:
        return []
    last = header_lines[-1].lstrip("#").strip()
    parts = re.split(r'\s+(?=\d+:)', last)
    return [p.strip() for p in parts if p.strip()]


def compute_relative_diff(ref_data, test_data):
    """Compute column-wise maximum relative difference.

    Returns a list of (col_index, max_rel_diff) tuples.
    For columns where ref values are all zero, uses absolute difference.
    """
    if ref_data.size == 0 or test_data.size == 0:
        return []

    nrows = min(ref_data.shape[0], test_data.shape[0])
    ncols = min(ref_data.shape[1], test_data.shape[1])
    results = []

    for c in range(ncols):
        ref_col = ref_data[:nrows, c]
        test_col = test_data[:nrows, c]

        abs_diff = np.abs(ref_col - test_col)
        denom = np.abs(ref_col)
        mask = denom > 1e-30
        if np.any(mask):
            rel = abs_diff[mask] / denom[mask]
            max_rel = np.max(rel)
        else:
            max_rel = np.max(abs_diff) if abs_diff.size > 0 else 0.0

        results.append((c, max_rel))

    return results


def find_matching_files(ref_dir, test_dir):
    """Find .dat files that exist in both directories.

    Matches by stripping any common prefix from filenames. CLASS output
    files are named as <root>_<type>.dat. We match by the suffix after
    the last underscore-delimited root prefix.
    """
    ref_files = {f for f in os.listdir(ref_dir) if f.endswith(".dat")}
    test_files = {f for f in os.listdir(test_dir) if f.endswith(".dat")}

    direct_matches = ref_files & test_files
    if direct_matches:
        return sorted(direct_matches)

    def suffix_key(fname):
        parts = fname.split("_")
        if len(parts) >= 2:
            return "_".join(parts[-2:]) if "cl" in parts[-1].lower() or "pk" in parts[-1].lower() else parts[-1]
        return fname

    ref_by_suffix = {}
    for f in ref_files:
        ref_by_suffix[suffix_key(f)] = f

    test_by_suffix = {}
    for f in test_files:
        test_by_suffix[suffix_key(f)] = f

    matches = []
    for key in sorted(set(ref_by_suffix.keys()) & set(test_by_suffix.keys())):
        matches.append((ref_by_suffix[key], test_by_suffix[key]))

    return matches


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

        ref_headers, ref_data = read_class_dat(ref_path)
        test_headers, test_data = read_class_dat(test_path)

        col_names = column_names_from_header(ref_headers)

        print(f"--- {ref_name} (type: {file_type}, tolerance: {tol*100:.4f}%) ---")

        if ref_data.size == 0:
            print("  SKIP: No numeric data in reference file.")
            continue
        if test_data.size == 0:
            print("  FAIL: No numeric data in test file.")
            all_pass = False
            continue

        if ref_data.shape[0] != test_data.shape[0]:
            print(f"  WARNING: Row count differs (ref={ref_data.shape[0]}, test={test_data.shape[0]}). "
                  f"Comparing first {min(ref_data.shape[0], test_data.shape[0])} rows.")
        if ref_data.shape[1] != test_data.shape[1]:
            print(f"  WARNING: Column count differs (ref={ref_data.shape[1]}, test={test_data.shape[1]}). "
                  f"Comparing first {min(ref_data.shape[1], test_data.shape[1])} columns.")

        diffs = compute_relative_diff(ref_data, test_data)
        file_pass = True

        for col_idx, max_diff in diffs:
            name = col_names[col_idx] if col_idx < len(col_names) else f"col_{col_idx}"
            status = "PASS" if max_diff <= tol else "FAIL"
            if status == "FAIL":
                file_pass = False
            print(f"  {status}  {name:>30s}  max_rel_diff = {max_diff:.6e}")

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
