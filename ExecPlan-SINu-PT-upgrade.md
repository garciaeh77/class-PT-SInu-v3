# Port Self-Interacting Neutrino (SINu) Physics to Latest CLASS

This ExecPlan is a living document. The sections Progress, Surprises & Discoveries, Decision Log, and Outcomes & Retrospective must be kept up to date as work proceeds.

This document must be maintained in accordance with .agent/PLANS.md at the repository root.


## Purpose / Big Picture

The goal is to bring self-interacting neutrino (SINu) physics from an older CLASS fork (class-interacting-neutrinos-PT) into a fresh copy of the latest public CLASS (class_public), producing an updated codebase in class_snu_uptodate. After this work is complete, a user can run the CLASS executable (or its Python wrapper classy) with the parameter log10_G_eff_nu set to enable neutrino self-interactions in the Boltzmann hierarchy, producing modified CMB angular power spectra (C_l) and matter power spectra (P(k)) that reflect the SINu physics.

The EFT/CLASS-PT nonlinear perturbation theory implementation also present in class-interacting-neutrinos-PT is explicitly out of scope for this plan and will be addressed in a separate future ExecPlan.

A user can verify success by running class_snu_uptodate with the same SINu parameter files used for class-interacting-neutrinos-PT and confirming that background quantities, P(k), and C_l match to within the specified tolerances. A comparison test script (compare_outputs.py) is built as part of this plan and runs these checks automatically.


## Progress

- [ ] Milestone 1: Bootstrap, test harness, and vanilla baseline
  - [ ] Record versions of class_public and class-interacting-neutrinos-PT in REFERENCE file
  - [ ] Copy class_public into class_snu_uptodate
  - [ ] Build class_snu_uptodate as vanilla CLASS
  - [ ] Create comparison test framework (compare_outputs.py)
  - [ ] Create vanilla .ini file (synchronous gauge)
  - [ ] Run vanilla cases in class_snu_uptodate and verify output is produced
  - [ ] Run compare_outputs.py to confirm class_snu_uptodate matches class_public (should be identical since it is a copy)
- [ ] Milestone 2: SINu reference data generation
  - [ ] Build class-interacting-neutrinos-PT
  - [ ] Create SINu .ini files (massless/massive neutrinos, synchronous gauge)
  - [ ] Run all cases (vanilla and SINu) through class-interacting-neutrinos-PT and save reference outputs into class-interacting-neutrinos-PT/validation_data/
  - [ ] Measure vanilla baseline difference between class_public and class-interacting-neutrinos-PT (document in Surprises & Discoveries)
  - [ ] Create validation_data/MANIFEST.md documenting each test case
- [ ] Milestone 3: Port SINu to input and background modules
  - [ ] Diff class-interacting-neutrinos-PT vs class_public for input.c, input.h, background.c, background.h to identify SINu-specific changes
  - [ ] Add SINu parameter parsing to class_snu_uptodate/source/input.c
  - [ ] Add SINu fields to class_snu_uptodate/include/background.h and source/background.c
  - [ ] Validate: code compiles
  - [ ] Validate: vanilla regression passes (class_snu_uptodate vanilla output unchanged from Milestone 1)
  - [ ] Validate: SINu .ini file parses without error and parameters are read correctly
  - [ ] Validate: background output with SINu parameters matches reference within 0.01%
- [ ] Milestone 4: Port SINu perturbations (core physics)
  - [ ] Diff class-interacting-neutrinos-PT/source/perturbations.c vs class_public/source/perturbations.c to identify all SINu-specific changes
  - [ ] Port SINu collision terms to class_snu_uptodate/source/perturbations.c
  - [ ] Port TCA (tight-coupling approximation) logic for SINu
  - [ ] Port SINu initial conditions for the perturbation vector
  - [ ] Copy neutrinos_collision_terms/ data directory into class_snu_uptodate
  - [ ] Add any needed SINu precision parameters to perturbations.h
  - [ ] Ensure all ported code compiles as C++ (class_public compiles perturbations.c via .opp rule)
  - [ ] Validate: code compiles
  - [ ] Validate: vanilla regression passes
  - [ ] Validate: SINu P(k) matches reference within 0.1% (synchronous gauge)
  - [ ] Validate: SINu C_l matches reference within 0.1% (synchronous gauge)
  - [ ] Validate: both massive and massless neutrino cases pass
- [ ] Milestone 5: Port remaining SINu changes and integration
  - [ ] Diff and assess thermodynamics module for SINu-specific changes; port if any
  - [ ] Diff and assess transfer module for SINu-specific changes; port if any
  - [ ] Diff and assess lensing module for SINu-specific changes; port if any
  - [ ] Diff and assess output module for SINu-specific changes; port if any
  - [ ] Validate: full test suite passes (all vanilla and SINu cases, synchronous gauge, both neutrino mass options)
- [ ] Milestone 6: Python wrapper
  - [ ] Add SINu parameter declarations to python/cclassy.pxd
  - [ ] Add SINu parameter handling to python/classy.pyx
  - [ ] Build classy (make classy or pip install)
  - [ ] Validate: Python script sets SINu parameters, computes, and retrieves P(k) and C_l
  - [ ] Validate: classy results match CLI results for the same input parameters
- [ ] Milestone 7: Documentation
  - [ ] Create validation_data/README.md explaining how to generate references and run tests
  - [ ] Add code comments documenting the SINu physics in perturbations, background, and input
  - [ ] Create example Jupyter notebooks (SINu with massive neutrinos, SINu with massless neutrinos)


## Surprises & Discoveries

(To be populated as work proceeds.)


## Decision Log

- Decision: Focus on SINu only; defer EFT/CLASS-PT (nonlinear_pt, spectra module, pt_matrices, external_Pk, OpenBLAS dependency) to a separate future ExecPlan.
  Rationale: Reduce scope and complexity. SINu and EFT/CLASS-PT are independent physics implementations. SINu is the priority.
  Date/Author: 2026-03-02, user direction.

- Decision: Use 0.1% relative tolerance for P(k) and C_l in synchronous gauge; use 0.01% for background quantities.
  Rationale: Background equations should be nearly identical between CLASS versions, so tighter tolerance catches bugs. P(k) and C_l may show small differences due to the CLASS version upgrade (different recombination code, bug fixes, etc.), so 0.1% accommodates those while still catching real porting errors.
  Date/Author: 2026-03-02, user direction.

- Decision: Defer Newtonian gauge validation for SINu to future work. All testing and validation in this plan uses synchronous gauge only.
  Rationale: The SINu implementation in Newtonian gauge is not yet stable even in the original class-interacting-neutrinos-PT code. Validating against an unstable reference would produce unreliable results. Newtonian gauge support should be revisited once the synchronous gauge port is complete and the Newtonian gauge behavior in the original code is better understood.
  Date/Author: 2026-03-02, user direction.

- Decision: Create the test harness (compare_outputs.py) before any porting work; run numerical validation at every milestone.
  Rationale: Catch bugs early. User specifically requested testing outputs at every step, not just compilation.
  Date/Author: 2026-03-02, user direction.

- Decision: class_public and class-interacting-neutrinos-PT are read-only. All new code goes in class_snu_uptodate. Only additive change to class-interacting-neutrinos-PT is creating validation_data/ to store reference inputs and outputs.
  Rationale: User requirement and AGENTS.md.
  Date/Author: 2026-03-02.

- Decision: No separate TESTING_SETUP.md file. All build and environment instructions are embedded in this ExecPlan for self-containment.
  Rationale: PLANS.md requires the ExecPlan to be fully self-contained.
  Date/Author: 2026-03-02.

- Decision: Validation compares class_snu_uptodate (with SINu ported) against class-interacting-neutrinos-PT (original SINu implementation). The comparison measures whether the port reproduces the original physics. Any baseline differences due to the CLASS version upgrade (e.g., HyRec2020 vs older hyrec) are expected and will be documented.
  Rationale: The two CLASS versions differ in recombination, some numerics, and potentially bug fixes. A small vanilla baseline difference is expected and does not indicate a porting error.
  Date/Author: 2026-03-02.


## Outcomes & Retrospective

(To be populated at major milestones and at completion.)

**Deferred items for future ExecPlans:**
- Newtonian gauge validation for SINu (deferred because Newtonian gauge accuracy is not yet stable in the original class-interacting-neutrinos-PT code; revisit once synchronous gauge port is validated and Newtonian gauge behavior is better characterized).
- EFT/CLASS-PT port (nonlinear_pt, spectra module, pt_matrices, external_Pk, OpenBLAS dependency).


## Context and Orientation

The repository root is at the top level of snu-class-update. Three directories are relevant:

**class_public/** contains the latest vanilla CLASS (from lesgourg/class_public). This directory must never be modified (per AGENTS.md). It serves as the base for the updated code and as a reference for vanilla behavior. Its module layout is: source files in source/ (background.c, thermodynamics.c, perturbations.c, transfer.c, primordial.c, fourier.c, harmonic.c, lensing.c, distortions.c, output.c, input.c), headers in include/, and the main entry point in main/class.c. In this version of CLASS, CMB angular power spectra are computed in harmonic.c and matter power spectrum and nonlinear corrections (Halofit, HMcode) are in fourier.c. The Makefile compiles perturbations.c as C++ via a .opp rule (the file is C code but compiled with a C++ compiler to enable certain features). Recombination uses HyRec2020 (located in external/HyRec2020/).

**class-interacting-neutrinos-PT/** contains an older CLASS fork with two added capabilities: SINu (self-interacting neutrinos, arXiv:2309.03941) and EFT/CLASS-PT (perturbation theory). Only SINu is in scope for this plan. Its source code must not be edited; only the additive creation of a validation_data/ directory is allowed. Its module layout differs from class_public: it uses spectra.c instead of harmonic.c for CMB spectra, nonlinear.c instead of fourier.c for nonlinear corrections, and has an additional nonlinear_pt.c for EFT/CLASS-PT. It does not have distortions.c. All source files are compiled as plain C (no .opp rules). Recombination uses an older version of hyrec (not HyRec2020). The directory neutrinos_collision_terms/ at the root of class-interacting-neutrinos-PT contains precomputed collision integral data tables (.dat files) required by the SINu perturbation equations.

**class_snu_uptodate/** is the target directory, currently empty. It will be initialized as a copy of class_public and then receive the ported SINu code.

**What SINu adds to CLASS:** SINu modifies the neutrino Boltzmann hierarchy to include self-interaction collision terms. The interaction strength is parameterized by log10_G_eff_nu, the base-10 logarithm of an effective Fermi-like coupling constant G_eff for neutrinos. When the flag interacting_nu is enabled and log10_G_eff_nu is set, collision terms are added to the neutrino multipole equations in the perturbations module. The collision term integrals are precomputed and stored in the neutrinos_collision_terms/ directory as .dat files (e.g. Coll_integrals_11_qbins.dat for 11-bin momentum sampling, Coll_integrals_5_qbins.dat for 5-bin, and Massless_alpha_l.dat for massless neutrino angular coefficients). A tight-coupling approximation (TCA) is used when the collision rate is large relative to the expansion rate, controlled by nu_tca_on and nu_tca_off switches and trigger parameters such as tight_coupling_trigger_tau_nu_over_tau_h and full_hierarchy_trigger_tau_nu_over_tau_k. The SINu changes are concentrated in: (1) input.c — parameter parsing, (2) background.h/background.c — storing G_eff_nu and related fields, and (3) perturbations.c — collision terms, TCA, and modified Boltzmann equations. Changes to other modules (thermodynamics, transfer, lensing, output) may be minimal or nonexistent and will be determined by diffing.

**What is NOT in scope:** The EFT/CLASS-PT implementation (nonlinear_pt.c, nonlinear_pt.h, spectra.c, spectra.h, fft.h, pt_matrices/, external_Pk/, and the OpenBLAS dependency) is deferred to a future plan. The updated code in class_snu_uptodate will use class_public's harmonic.c and fourier.c for spectra and nonlinear corrections. Halofit and HMcode from class_public remain available and unchanged.

**Key technical difference:** class_public compiles perturbations.c as C++ (via the Makefile's .opp rule). class-interacting-neutrinos-PT compiles everything as plain C. When porting SINu code from perturbations.c, it must be adapted to compile cleanly as C++. Common issues include: implicit void* casts (C allows void* to any pointer type implicitly; C++ requires explicit casts), variable-length arrays (not standard C++), and declaration placement (C99 allows declarations after statements; some C++ compilers are strict about this in certain contexts). These will need to be addressed during Milestone 4.


## Plan of Work

The work is organized into seven milestones. Each milestone produces testable, verifiable results. The test harness is built first (Milestone 1) and used from that point forward. Every subsequent milestone runs the full test suite to catch regressions. The milestones are designed so that a failure at any point can be debugged in isolation — you always know which milestone introduced a problem.

**Milestone 1 — Bootstrap, Test Harness, and Vanilla Baseline.** This milestone establishes the working environment and testing infrastructure before any SINu code is written. First, record the exact versions of class_public and class-interacting-neutrinos-PT in a REFERENCE file at the repository root (using git commit hashes if available, or "no-git" otherwise). Then copy the entire class_public directory into class_snu_uptodate, replacing the empty directory. Build class_snu_uptodate by running make in that directory (after make clean if needed). Confirm the build produces the class executable by running ./class with a vanilla .ini file and checking that output files are produced.

Next, create the test harness: a Python script compare_outputs.py at the repository root. This script takes two directories of CLASS output files (a "reference" directory and a "test" directory), reads the .dat files (background, P(k), C_l), and computes column-by-column relative differences. It reports the maximum relative difference per quantity and returns PASS or FAIL based on configurable tolerances (default: 0.01% for background, 0.1% for P(k) and C_l). The script should handle the standard CLASS output format: lines beginning with # are headers/comments, data is whitespace-separated columns, and the first column is typically the independent variable (z for background, k for P(k), l for C_l).

Create a vanilla .ini file (stored in a tests/ directory at the repository root or in class_snu_uptodate) for synchronous gauge. It requests output = tCl, pCl, lCl, mPk with lensing = yes and uses standard Planck-like cosmological parameters. Run class_snu_uptodate with this file and save the outputs. Run class_public with the same file and save its outputs. Use compare_outputs.py to confirm the two sets of outputs are identical (they should be, since class_snu_uptodate is a copy of class_public at this point). This validates both the build and the test harness.

**Milestone 2 — SINu Reference Data Generation.** This milestone produces the reference outputs that all subsequent milestones will validate against. Build class-interacting-neutrinos-PT (this requires the older hyrec and may require OpenBLAS for the nonlinear_pt module that is part of its build; install dependencies as needed). Create a set of .ini files for the SINu test cases. The test matrix is:

- Vanilla (SINu off), synchronous gauge
- SINu on, synchronous gauge, massless neutrinos (N_ur includes interacting species)
- SINu on, synchronous gauge, massive neutrinos (N_ncdm includes interacting species)

Newtonian gauge cases are intentionally excluded from this plan (see Decision Log). The SINu implementation in Newtonian gauge is not yet stable in the original code and should be revisited in future work once the synchronous gauge port is validated and the Newtonian gauge behavior is better characterized.

Each .ini requests background output, P(k), and C_l (TT, EE, TE, and lensed). Place these .ini files in class-interacting-neutrinos-PT/validation_data/. Run class-interacting-neutrinos-PT with each .ini and save the outputs into per-case subdirectories under validation_data/ (e.g. validation_data/ref_vanilla_sync/, validation_data/ref_sinu_sync_massless/, etc.).

Also run the vanilla cases through class_snu_uptodate (which is still just class_public at this point) and compare the vanilla outputs from the two CLASS versions using compare_outputs.py. Document the baseline vanilla differences in the Surprises & Discoveries section. These differences arise from the CLASS version upgrade (different recombination code, numerical improvements, bug fixes) and represent the floor below which we cannot expect SINu outputs to agree. Create a validation_data/MANIFEST.md listing each test case, its .ini file, and which reference outputs are stored.

The exact parameter names and values for SINu (log10_G_eff_nu, interacting_nu, etc.) should be determined by reading class-interacting-neutrinos-PT/source/input.c. A good starting value for testing is log10_G_eff_nu = -1.5 (moderate self-interaction). The .ini files should use cosmological parameters consistent between vanilla and SINu cases so that differences are solely due to the SINu physics.

**Milestone 3 — Port SINu to Input and Background.** This milestone adds SINu parameter parsing and background data structures to class_snu_uptodate without yet modifying the physics (perturbations). Begin by diffing the input and background modules between class-interacting-neutrinos-PT and class_public to produce a precise list of SINu-specific additions. Use these diffs as the guide for what to port.

In class_snu_uptodate/source/input.c, add parsing for: log10_G_eff_nu (double), interacting_nu (int or flag), nu_tca_on (int), nu_tca_off (int), and the TCA/precision trigger parameters. Compute G_eff_nu = pow(10, log10_G_eff_nu) when log10_G_eff_nu is set. Set a has_SINu or equivalent flag. In class_snu_uptodate/include/background.h, add SINu fields to the background structure: at minimum log10_G_eff_nu, G_eff_nu, and interacting_nu. In class_snu_uptodate/source/background.c, initialize these fields and add any SINu-related background computation (most SINu physics is in perturbations, so background changes may be minimal — primarily storing the coupling constant).

Validate by compiling and running the vanilla cases. Use compare_outputs.py to confirm that vanilla outputs are unchanged from Milestone 1 (regression test). Then run with a SINu .ini file. At this stage, the SINu parameters should be parsed and stored, but the perturbation equations have not been modified, so the physics output will not yet reflect SINu. The key check is that the code compiles, runs without crashing, and the parameters are correctly read (verify via verbose output or by adding a temporary print statement). Also compare the background output to the SINu reference to check whether the background is already close (it should be, since SINu primarily affects perturbations, not the background expansion).

**Milestone 4 — Port SINu Perturbations (Core Physics).** This is the central milestone where the SINu physics is actually implemented. The perturbations module is where the neutrino Boltzmann hierarchy is solved, and this is where the self-interaction collision terms and TCA are added.

Begin by producing a detailed diff of class-interacting-neutrinos-PT/source/perturbations.c against class_public/source/perturbations.c. This diff will be large (both files are ~400 KB), so focus on identifying SINu-specific blocks. Search for log10_G_eff_nu, G_eff_nu, interacting_nu, nu_tca, collision, and related terms in class-interacting-neutrinos-PT/source/perturbations.c. These mark the SINu-specific code. The key additions are:

1. Perturbation vector indices for SINu neutrino variables (if the SINu implementation uses additional variables beyond the standard neutrino hierarchy, or if it modifies how the hierarchy is truncated).

2. Initial conditions for SINu perturbations (in the function that sets initial values for the perturbation vector).

3. The SINu collision terms in the derivatives function (perturb_derivs or equivalent). These terms modify the time derivatives of the neutrino multipoles by adding collision integrals that depend on the coupling G_eff_nu and the precomputed tables from neutrinos_collision_terms/.

4. TCA logic: when the collision rate is high (early times or large G_eff_nu), the code switches to a tight-coupling approximation that replaces the full hierarchy with a truncated set of equations. The switches nu_tca_on and nu_tca_off and the trigger parameters control when this approximation is activated and deactivated.

5. Loading of the neutrinos_collision_terms data files. Copy the entire neutrinos_collision_terms/ directory from class-interacting-neutrinos-PT into class_snu_uptodate. Ensure the code can find these files (check the path used in the source; it may be relative to the executable or specified in the .ini).

6. Any gauge-specific logic for SINu in synchronous gauge. (Newtonian gauge support is deferred; see Decision Log. However, if the SINu code contains Newtonian gauge branches, port them as-is for completeness — they simply will not be validated in this plan.)

Port each piece into class_snu_uptodate/source/perturbations.c. As you port, ensure the code compiles as C++ (the class_public Makefile compiles perturbations.c via the .opp rule). Specific C-to-C++ issues to watch for: cast all void* returns (e.g. from malloc, calloc, realloc) to the target pointer type explicitly; replace any variable-length arrays with malloc/free; ensure all variables are declared before use in each scope (or at least that the C++ compiler accepts the placement).

Also check class_snu_uptodate/include/perturbations.h for any SINu-specific additions needed (new indices, flags, or structure fields).

Validate after this milestone by running all test cases through class_snu_uptodate:
- Vanilla case (synchronous gauge): must still match class_public (regression test, should be within machine precision since SINu is off).
- SINu cases (synchronous gauge, massive and massless): compare P(k), C_l, and background to the reference outputs from Milestone 2. Apply 0.01% tolerance for background and 0.1% tolerance for P(k) and C_l. If the vanilla baseline difference measured in Milestone 2 is close to 0.1%, the SINu tolerance may need adjustment; document this in the Decision Log.

This milestone is the most labor-intensive. If any SINu test case fails tolerance, diff the ported perturbations code against the original in class-interacting-neutrinos-PT to find missing or incorrect logic.

**Milestone 5 — Port Remaining SINu Changes and Integration.** After the core perturbations port in Milestone 4, check whether other modules need SINu-specific changes. For each of the following modules, diff the class-interacting-neutrinos-PT version against the class_public version and look for SINu-specific code (search for G_eff_nu, interacting_nu, SINu, and related terms):

- thermodynamics.c / thermodynamics.h — SINu may not affect thermodynamics at all, since the self-interactions are in the perturbation equations, not in recombination or ionization history. If there are changes, port them.
- transfer.c / transfer.h — SINu may add transfer function types for interacting neutrinos, or it may not require changes if the standard transfer machinery handles the modified perturbation sources.
- lensing.c — Unlikely to have SINu-specific changes; lensing depends on the lensing potential which is computed from the standard perturbation sources.
- output.c — May have changes to output additional columns or file types for SINu observables.

Port any SINu-specific changes found. Validate by running the full test suite (vanilla and SINu cases, synchronous gauge). All cases must pass within tolerance.

Also verify at this stage that the nonlinear options from class_public (Halofit, HMcode) still work correctly when SINu is enabled. Run a SINu case with non_linear = halofit and confirm the code does not crash. (Full numerical validation of nonlinear P(k) with SINu is optional at this stage since the reference code may not have comparable HMcode output.)

**Milestone 6 — Python Wrapper.** Port the SINu parameter interface to classy (the Python wrapper for CLASS). Open class-interacting-neutrinos-PT/python/cclassy.pxd and python/classy.pyx as read-only references. In class_snu_uptodate/python/cclassy.pxd, add C-level declarations for any SINu fields in the background or other structures that need to be accessed from Python (e.g. G_eff_nu, interacting_nu). In class_snu_uptodate/python/classy.pyx, ensure that SINu parameters (log10_G_eff_nu, interacting_nu, etc.) can be passed via the set() method and that compute() runs the SINu physics when these are set. Add or verify get methods for retrieving P(k), C_l, and background quantities.

Build classy (make classy or cd python && pip install .). Validate by writing a short Python script that: (1) instantiates the Class object, (2) sets cosmological parameters including SINu parameters, (3) calls compute(), (4) retrieves P(k) and C_l, and (5) compares them to the reference. The Python results should match the CLI results from Milestone 4 to within machine precision (since both use the same underlying C library).

**Milestone 7 — Documentation.** Create validation_data/README.md in class-interacting-neutrinos-PT explaining: what the validation data is, how to regenerate it (build class-interacting-neutrinos-PT and run the .ini files), and how to run the regression tests (build class_snu_uptodate and run compare_outputs.py). Add brief comments in the ported source code (perturbations.c, background.c, input.c) explaining the SINu physics: what the collision terms represent, what the TCA does, and what the trigger parameters control. Create two example Jupyter notebooks in class_snu_uptodate/notebooks/: one demonstrating SINu with massive neutrinos and one with massless neutrinos. Each notebook should use classy to compute and plot C_l and P(k) with and without SINu, showing the effect of the self-interaction.


## Concrete Steps

All paths are relative to the repository root. Commands should be run from the repository root unless otherwise specified.

**Milestone 1 — Bootstrap, Test Harness, and Vanilla Baseline:**

    # Record versions
    echo "class_public: $(cd class_public && git rev-parse HEAD 2>/dev/null || echo 'no-git')" > REFERENCE
    echo "class-interacting-neutrinos-PT: $(cd class-interacting-neutrinos-PT && git rev-parse HEAD 2>/dev/null || echo 'no-git')" >> REFERENCE

    # Copy class_public to class_snu_uptodate
    rm -rf class_snu_uptodate
    cp -r class_public class_snu_uptodate

    # Build class_snu_uptodate
    cd class_snu_uptodate
    make clean
    make

    # Test with a vanilla .ini (use explanatory.ini or create a minimal one)
    ./class <vanilla_sync.ini>

(The exact .ini file name depends on what is available; if no suitable .ini exists, create one with the parameters described in the Plan of Work.)

Create compare_outputs.py at the repository root. The script should accept arguments like:

    python compare_outputs.py --reference <ref_dir> --test <test_dir> --bg-tolerance 0.0001 --cl-tolerance 0.001 --pk-tolerance 0.001

It reads all .dat files in both directories, matches them by filename, and compares them column by column. Output is a per-file, per-column report of maximum relative difference and PASS/FAIL.

Create vanilla .ini files in a tests/ directory. Run class_snu_uptodate and class_public with each and compare:

    cd class_public
    ./class ../tests/vanilla_sync.ini
    cd ../class_snu_uptodate
    ./class ../tests/vanilla_sync.ini
    cd ..
    python compare_outputs.py --reference class_public/output --test class_snu_uptodate/output

(Adjust output paths to match the root parameter in the .ini files.)

**Milestone 2 — SINu Reference Data Generation:**

    # Build class-interacting-neutrinos-PT
    cd class-interacting-neutrinos-PT
    make clean
    make

    # Create validation_data directory and .ini files
    mkdir -p validation_data

    # Create .ini files (vanilla_sync.ini, sinu_sync_massless.ini, sinu_sync_massive.ini)
    # Place them in validation_data/

    # Run each case and save outputs
    ./class validation_data/vanilla_sync.ini
    mkdir -p validation_data/ref_vanilla_sync
    cp output/* validation_data/ref_vanilla_sync/

    # Repeat for each test case...

    # Measure vanilla baseline between the two CLASS versions
    cd ..
    python compare_outputs.py \
      --reference class-interacting-neutrinos-PT/validation_data/ref_vanilla_sync \
      --test class_snu_uptodate/output

(Ensure .ini files use the same root prefix so output file names match, or adjust the comparison script to handle different prefixes.)

**Milestones 3–5 — Porting:**

All edits are made in class_snu_uptodate/. After each set of edits:

    cd class_snu_uptodate
    make clean
    make

Then run the full test suite:

    # Vanilla regression
    ./class ../tests/vanilla_sync.ini
    cd ..
    python compare_outputs.py --reference class_public/output --test class_snu_uptodate/output

    # SINu validation (after Milestone 4)
    cd class_snu_uptodate
    ./class ../class-interacting-neutrinos-PT/validation_data/sinu_sync_massless.ini
    cd ..
    python compare_outputs.py \
      --reference class-interacting-neutrinos-PT/validation_data/ref_sinu_sync_massless \
      --test class_snu_uptodate/output

    # Repeat for each SINu test case

**Milestone 6 — Python Wrapper:**

    cd class_snu_uptodate
    make classy
    # or: cd python && pip install .

    # Test with a Python script:
    python -c "
    from classy import Class
    cosmo = Class()
    cosmo.set({'output': 'tCl,pCl,lCl,mPk', 'lensing': 'yes',
               'log10_G_eff_nu': -1.5, 'interacting_nu': 1,
               ...})  # add cosmological parameters
    cosmo.compute()
    cls = cosmo.lensed_cl()
    pk = cosmo.pk(0.1, 0)
    print('C_l TT at l=100:', cls['tt'][100])
    print('P(k=0.1):', pk)
    cosmo.struct_cleanup()
    cosmo.empty()
    "

**Milestone 7 — Documentation:**

    # Create documentation files (no shell commands needed; create via editor)
    # Notebooks in class_snu_uptodate/notebooks/


## Validation and Acceptance

The implementation is accepted when all of the following hold:

**Build.** From class_snu_uptodate/, make class and make classy both complete without error.

**Vanilla regression.** Running class_snu_uptodate with vanilla .ini files (SINu off) produces output that matches class_public output to within machine precision (since class_snu_uptodate started as a copy of class_public). This ensures the SINu port has not broken any existing physics.

**SINu validation — background.** For all SINu test cases (synchronous gauge, massive and massless neutrinos), background quantities (H(z), distances, densities) from class_snu_uptodate match the reference from class-interacting-neutrinos-PT to within 0.01% relative accuracy. (Background differences should be small because SINu primarily affects perturbations, not the expansion history.)

**SINu validation — P(k) and C_l.** For all SINu test cases (synchronous gauge), matter power spectrum P(k) and CMB angular power spectra C_l (TT, EE, TE, lensed) from class_snu_uptodate match the reference to within 0.1% relative accuracy. Newtonian gauge validation is deferred (see Decision Log).

**Both interfaces.** The same validation passes when class_snu_uptodate is driven by the CLI (./class) and by the Python wrapper (classy).

**Nonlinear options.** Running with non_linear = halofit or non_linear = hmcode from class_public completes without error when SINu is enabled. (Numerical accuracy of nonlinear corrections in the presence of SINu is not validated in this plan, since the reference code uses different nonlinear modules.)

**Documentation.** validation_data/README.md exists and explains how to regenerate references and run tests. Example notebooks run successfully.


## Idempotence and Recovery

Each milestone can be resumed from where it left off. If a milestone is partially complete, continue editing in class_snu_uptodate without reverting prior work. A failed compilation does not corrupt the source tree; fix the code and rerun make.

To start completely over: remove class_snu_uptodate and copy class_public again. The validation_data/ in class-interacting-neutrinos-PT persists and does not need to be regenerated.

class_public and class-interacting-neutrinos-PT (except validation_data/) remain unchanged throughout and serve as stable references. If a SINu test case fails tolerance, diff the ported code in class_snu_uptodate against the original in class-interacting-neutrinos-PT to find missing or incorrect logic.

If the Python wrapper fails to build, ensure that cclassy.pxd declarations match the C header files and that the library (.so or .dylib) was built with the same compiler flags used for make class.

The compare_outputs.py script is idempotent: it reads files and reports results without modifying anything.


## Artifacts and Notes

(To be populated with build output transcripts, comparison results, diffs, and other evidence as work proceeds.)


## Interfaces and Dependencies

The following are the SINu-specific interfaces and dependencies. Exact names, types, and function signatures should be determined by reading class-interacting-neutrinos-PT source files (read-only) and replicated in class_snu_uptodate.

**Input parameters (source/input.c):** The following parameters must be parsed from the .ini file: log10_G_eff_nu (double, the log base 10 of the effective neutrino self-interaction coupling), interacting_nu (int flag, enables SINu), nu_tca_on (int, enables neutrino tight-coupling approximation), nu_tca_off (int, disables neutrino TCA at some point), and precision/trigger parameters including start_small_k_at_tau_nu_over_tau_h, tight_coupling_trigger_tau_nu_over_tau_h, tight_coupling_trigger_tau_nu_over_tau_k, and full_hierarchy_trigger_tau_nu_over_tau_k. The exact parameter names and their roles should be confirmed by searching class-interacting-neutrinos-PT/source/input.c.

**Background structure (include/background.h):** Add to the background structure: double log10_G_eff_nu, double G_eff_nu (computed as pow(10, log10_G_eff_nu)), int interacting_nu. These fields are set during input parsing and read during perturbation evolution.

**Perturbations (include/perturbations.h, source/perturbations.c):** The perturbation vector may need additional indices for SINu neutrino variables (to be determined from the diff). The derivatives function (perturb_derivs or equivalent) must be extended with SINu collision terms. The collision terms depend on precomputed integrals loaded from neutrinos_collision_terms/ data files. TCA logic must be added with the appropriate trigger conditions. All ported code must compile as C++.

**Data files:** The directory neutrinos_collision_terms/ must be copied from class-interacting-neutrinos-PT into class_snu_uptodate. It contains: Coll_integrals_11_qbins.dat, Coll_integrals_5_qbins.dat, and Massless_alpha_l.dat. The code in perturbations.c reads these files at runtime; the path may be hardcoded relative to the executable or configurable via the .ini.

**Python wrapper (python/cclassy.pxd, python/classy.pyx):** Expose log10_G_eff_nu and interacting_nu for the set() method. Ensure compute() invokes the SINu-modified perturbation solver when these parameters are set. The get methods for P(k), C_l, and background quantities should work without modification if they already use the standard CLASS output structures.

**Build dependencies:** class_snu_uptodate requires only what class_public requires (C compiler with C++ support, make, Python 3 with Cython for classy, HyRec2020 which is already in external/). No additional external libraries (OpenBLAS, etc.) are needed for the SINu-only port since those are required only by nonlinear_pt which is out of scope.
