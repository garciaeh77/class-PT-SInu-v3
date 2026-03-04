"""
Milestone 6 validation: compare classy (Python) output against class CLI output
for SINu massless and massive cases. Both must agree to machine precision
(they use the same underlying C library).

Unit notes:
- CLI cl_lensed file stores dimensionless l(l+1)/(2pi) * C_l
- classy.lensed_cl() returns raw C_l (without l(l+1)/(2pi) factor)
- CLI pk file stores P(k) in (Mpc/h)^3 with k in h/Mpc
- classy.pk(k_Mpc, z) takes k in 1/Mpc, returns P in Mpc^3
  Conversion: P[(Mpc/h)^3] = P[Mpc^3] * h^3; k[1/Mpc] = k[h/Mpc] * h
"""

import os
import sys
import subprocess
import tempfile
import numpy as np

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CLASS_BIN = os.path.join(REPO_ROOT, "class_snu_uptodate", "class")

from classy import Class

BASE_PARAMS = {
    'output': 'tCl,pCl,lCl,mPk',
    'lensing': 'yes',
    'gauge': 'synchronous',
    'h': 0.6732,
    'omega_b': 0.022383,
    'omega_cdm': 0.12011,
    'A_s': 2.1005e-9,
    'n_s': 0.96605,
    'tau_reio': 0.0543,
    'P_k_max_h/Mpc': 1.0,
    'z_pk': 0,
    'l_max_scalars': 2500,
    'log10_G_eff_nu': -1.5,
    'interacting_nu': 1,
}

MASSLESS_EXTRA = {'N_ur': 3.044}
MASSIVE_EXTRA  = {'N_ur': 2.0328, 'N_ncdm': 1, 'm_ncdm': 0.06, 'T_ncdm': 0.71611}

TOLERANCE = 1e-6  # machine-precision (same C library, same seed)


def validate_case(label, extra_params):
    print(f"\n=== {label} ===")
    params = {**BASE_PARAMS, **extra_params}

    # --- Run CLI ---
    with tempfile.TemporaryDirectory() as tmpdir:
        ini_path = os.path.join(tmpdir, "run.ini")
        with open(ini_path, 'w') as f:
            f.write(f"root = {tmpdir}/run_\n")
            for k, v in params.items():
                f.write(f"{k} = {v}\n")

        result = subprocess.run(
            [CLASS_BIN, ini_path],
            capture_output=True, text=True, cwd=REPO_ROOT
        )
        if result.returncode != 0:
            raise RuntimeError(f"class CLI failed:\n{result.stderr[-2000:]}")

        files = os.listdir(tmpdir)
        cl_files = sorted([f for f in files if 'cl_lensed' in f and f.endswith('.dat')])
        pk_files = sorted([f for f in files if f.endswith('_pk.dat')])
        if not cl_files:
            raise RuntimeError(f"No cl_lensed file found; files: {files}")
        if not pk_files:
            raise RuntimeError(f"No pk file found; files: {files}")

        # CLI stores l(l+1)/(2pi) * C_l; columns: l TT EE TE BB phiphi TPhi Ephi
        cl_data = np.loadtxt(os.path.join(tmpdir, cl_files[0]), comments='#')
        ells_cli = cl_data[:, 0]
        # Convert back to raw C_l
        fac = ells_cli * (ells_cli + 1) / (2 * np.pi)
        cl_tt_cli = cl_data[:, 1] / fac
        cl_ee_cli = cl_data[:, 2] / fac

        # CLI pk: k in h/Mpc, P in (Mpc/h)^3
        pk_data = np.loadtxt(os.path.join(tmpdir, pk_files[0]), comments='#')
        k_hMpc_cli = pk_data[:, 0]
        pk_cli_hMpc3 = pk_data[:, 1]

    # --- Run classy ---
    cosmo = Class()
    cosmo.set(params)
    cosmo.compute()
    h = cosmo.h()

    # Lensed C_l (raw, no l(l+1)/2pi)
    cls_lensed = cosmo.lensed_cl(2500)
    ells_py = np.array(cls_lensed['ell'], dtype=float)
    cl_tt_py = np.array(cls_lensed['tt'], dtype=float)
    cl_ee_py = np.array(cls_lensed['ee'], dtype=float)

    # P(k): evaluate at CLI k values (convert h/Mpc → 1/Mpc), excluding boundary
    # Use k up to P_k_max_h/Mpc=1 h/Mpc to stay within computed range
    k_max_safe = 0.99  # h/Mpc — slightly below the CLI k_max to avoid boundary issues
    mask_k = k_hMpc_cli <= k_max_safe
    k_hMpc_use = k_hMpc_cli[mask_k]
    pk_cli_use = pk_cli_hMpc3[mask_k]

    k_Mpc_use = k_hMpc_use * h
    pk_py_mpc3 = np.array([cosmo.pk(k, 0.0) for k in k_Mpc_use])
    pk_py_hMpc3 = pk_py_mpc3 * h**3  # Convert Mpc^3 → (Mpc/h)^3
    pk_cli_hMpc3 = pk_cli_use  # Restrict CLI to same k range

    cosmo.struct_cleanup()
    cosmo.empty()

    # --- Compare ---
    # C_l: match on common ell range
    l_min = max(int(ells_py[0]), int(ells_cli[0]))
    l_max = min(int(ells_py[-1]), int(ells_cli[-1]))
    mask_py  = (ells_py  >= l_min) & (ells_py  <= l_max)
    mask_cli = (ells_cli >= l_min) & (ells_cli <= l_max)

    def compare(a, b, name):
        with np.errstate(divide='ignore', invalid='ignore'):
            peak = np.max(np.abs(b))
            floor = 1e-4 * peak
            mask = np.abs(b) > floor
            if mask.sum() > 0:
                rel = np.abs(a[mask] - b[mask]) / np.abs(b[mask])
                max_rel = rel.max()
            else:
                max_rel = np.max(np.abs(a - b))
        status = "PASS" if max_rel <= TOLERANCE else "FAIL"
        print(f"  {name}: max_rel_diff = {max_rel:.3e}  [{status}]")
        return status == "PASS"

    ok1 = compare(cl_tt_py[mask_py], cl_tt_cli[mask_cli], 'C_l TT (lensed)')
    ok2 = compare(cl_ee_py[mask_py], cl_ee_cli[mask_cli], 'C_l EE (lensed)')
    ok3 = compare(pk_py_hMpc3, pk_cli_hMpc3, 'P(k)')

    overall = "PASS" if all([ok1, ok2, ok3]) else "FAIL"
    print(f"  Overall: {overall}")
    return overall == "PASS"


if __name__ == '__main__':
    all_pass = True
    all_pass &= validate_case("SINu massless", MASSLESS_EXTRA)
    all_pass &= validate_case("SINu massive",  MASSIVE_EXTRA)

    print("\n" + ("=" * 50))
    print("ALL TESTS PASSED" if all_pass else "SOME TESTS FAILED")
    sys.exit(0 if all_pass else 1)
