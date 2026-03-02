# Port SINu and EFT/CLASS-PT to Latest CLASS (class_public-master)

This ExecPlan is a living document. The sections Progress, Surprises & Discoveries, Decision Log, and Outcomes & Retrospective must be kept up to date as work proceeds.

This document must be maintained in accordance with .agent/PLANS.md at the repository root.


## Purpose / Big Picture

This plan ports the self-interacting neutrino (SINu) physics and the EFT/CLASS-PT (effective field theory perturbation theory) implementation from an older CLASS fork in the class-SINu-PT/ directory to the current CLASS version in class-SINu-PT_uptodate/, which is based on class_public-master. The goal is to replicate the same physics so that the updated version produces results matching the original to within agreed tolerances.

The SINu implementation adds neutrino self-interactions controlled by the parameter log10_G_eff_nu, with collision terms and tight-coupling approximation (TCA) for the neutrino Boltzmann hierarchy. The EFT/CLASS-PT implementation adds nonlinear perturbation theory corrections (nonlinear_pt) and a spectra module for CMB and matter power spectra, alongside the standard nonlinear options (Halofit, HMcode) from vanilla CLASS. Users will be able to run both vanilla cosmology and SINu/EFT scenarios in synchronous or Newtonian gauge, with massive or massless neutrinos, and compare observables to reference outputs.

CRITICAL: This is a porting task. The physics already works in class-SINu-PT/. We are replicating that implementation in class-SINu-PT_uptodate/ (initialized as a copy of class_public-master). The directories class_public-master/ and class-SINu-PT/ are for reference: class_public-master must never be modified; class-SINu-PT/ source code must not be edited. The only additive change to class-SINu-PT/ is creating validation_data/ to store input files and reference outputs. All new code is written in class-SINu-PT_uptodate/.

A user can verify success by using the same input files stored in class-SINu-PT/validation_data/, running the CLASS executable (or classy) from class-SINu-PT_uptodate/ with those inputs, and comparing key observables to the reference. Background quantities (e.g. H(z), distances), matter power spectrum P(k), CMB angular power spectra C_ℓ (tCl, pCl, lCl), and transfer functions must match the reference to within 0.1% relative accuracy for synchronous gauge and for vanilla runs in Newtonian gauge; for SINu runs in Newtonian gauge a relaxed or optional tolerance applies (SINu is discouraged in Newtonian gauge in the original code). Tests are run via both the ./class CLI and the Python interface (classy). All nonlinear methods (linear, Halofit, HMcode, nonlinear_pt) are kept and tested accordingly.


## Progress

- [x] Phase 0: Bootstrap and version pinning
  - [x] Record class_public-master and class-SINu-PT versions (commit or tarball) in REFERENCE or VERSION file
  - [x] Copy class_public-master into class-SINu-PT_uptodate (overwrite empty directory)
  - [x] Run make clean and make in class-SINu-PT_uptodate (use conda env conda_sinu_pt_uptodate per TESTING_SETUP.md)
  - [x] Run ./class with a vanilla .ini (e.g. default.ini) and confirm output
  - [x] Validate: class-SINu-PT_uptodate builds and runs as vanilla CLASS
- [x] Phase 1: Create validation baseline from class-SINu-PT
  - [x] Create class-SINu-PT/validation_data/ directory
  - [x] Add input files (.ini, .pre) for vanilla runs (SINu/EFT off), synchronous and Newtonian gauge
  - [x] Add input files for SINu runs (synchronous and Newtonian), massive and massless neutrinos
  - [x] Add input files for nonlinear variants (linear, Halofit; HMcode not in class-SINu-PT) where applicable
  - [x] Run class-SINu-PT for each case and save reference outputs into validation_data (via generate_references.sh; build: conda_sinu_pt, OPENBLAS from conda)
  - [x] Document manifest (MANIFEST.md and README in validation_data)
  - [ ] Validate: run generate_references.sh and confirm reference files exist and are readable; same inputs will be used for Phase 4 validation
- [ ] Phase 2a: Port input module
  - [ ] Add SINu parameters to input parsing (log10_G_eff_nu, interacting_nu, nu_tca_on, nu_tca_off, TCA triggers, etc.)
  - [ ] Add EFT/nonlinear_pt and spectra-related input parameters
  - [ ] Add precision parameters for SINu (start_small_k_at_tau_nu_over_tau_h, tight_coupling_trigger_*, full_hierarchy_trigger_*)
  - [ ] Set has_SINu or equivalent flag from parameters
  - [ ] Update explanatory.ini (or default.ini) with SINu/EFT parameter documentation
  - [ ] Validate: compile successfully; test parsing with a minimal SINu .ini
- [ ] Phase 2b: Port background module
  - [ ] Add SINu-related fields to background structure in include/background.h (e.g. log10_G_eff_nu, G_eff_nu, interacting_nu)
  - [ ] Add background indices for SINu quantities if needed
  - [ ] Modify background_init to allocate and initialize SINu quantities
  - [ ] Modify background_solve / background_functions to compute or store SINu background terms
  - [ ] Modify background_free to deallocate SINu arrays
  - [ ] Add SINu columns to background output if applicable
  - [ ] Validate: compile and run with SINu parameters set; no crash
- [ ] Phase 2c: Port thermodynamics module
  - [ ] Add any SINu/EFT thermodynamics indices or derived parameters
  - [ ] Ensure HyRec2020 is used (class_public-master); remove or replace older hyrec dependency
  - [ ] Modify thermodynamics_init and thermodynamics_at_z for SINu if needed
  - [ ] Add SINu columns to thermodynamics output if applicable
  - [ ] Validate: compile; compare thermodynamics output to reference for a SINu case (after perturbations port)
- [ ] Phase 2d: Port perturbations module
  - [ ] Add perturbation indices for SINu neutrino hierarchy (or identify equivalent in class_public-master perturbations)
  - [ ] Port SINu Boltzmann equations and collision terms from class-SINu-PT/source/perturbations.c
  - [ ] Port TCA (tight-coupling approximation) for SINu: nu_tca_on, nu_tca_off and trigger parameters
  - [ ] Copy or link neutrinos_collision_terms data into class-SINu-PT_uptodate
  - [ ] Adapt to class_public-master perturbations API (C++ .opp, naming); implement gauge transformations for SINu if needed
  - [ ] Modify perturb_derivs (or equivalent) to include SINu evolution
  - [ ] Validate: compile; run a SINu case and compare perturbation-related outputs to reference
- [ ] Phase 2e: Port transfer module
  - [ ] Add transfer indices for SINu/EFT-related transfer functions if any
  - [ ] Modify transfer_init and transfer_functions to extract SINu transfers
  - [ ] Add SINu/EFT columns to transfer output
  - [ ] Validate: compile; verify transfer output for a SINu run
- [ ] Phase 2f: Port nonlinear module (Halofit/HMcode)
  - [ ] Ensure nonlinear module in class_public-master (fourier.c or equivalent) is used for Halofit/HMcode
  - [ ] Port any SINu-specific warnings or checks from class-SINu-PT/source/nonlinear.c into the corresponding file in class-SINu-PT_uptodate
  - [ ] Validate: compile; run with non_linear = halofit or HMcode
- [ ] Phase 2g: Port nonlinear_pt module
  - [ ] Copy or adapt nonlinear_pt source and headers from class-SINu-PT into class-SINu-PT_uptodate
  - [ ] Integrate pt_matrices and external_Pk data; add OpenBLAS (or equivalent) to build
  - [ ] Wire nonlinear_pt into the pipeline (after transfer, before spectra/harmonic)
  - [ ] Validate: compile with nonlinear_pt; run a nonlinear_pt test case
- [ ] Phase 2h: Port spectra (or integrate with harmonic)
  - [ ] In class_public-master, CMB spectra are in harmonic.c; add or adapt spectra logic for CLASS-PT outputs
  - [ ] Port spectra module from class-SINu-PT or merge its functionality into harmonic/fourier
  - [ ] Ensure mPk, tCl, pCl, lCl and any EFT outputs are produced correctly
  - [ ] Validate: compile; compare P(k) and C_l to reference for vanilla and SINu cases
- [ ] Phase 2i: Port lensing module
  - [ ] Port any SINu/EFT-specific changes in lensing from class-SINu-PT/source/lensing.c
  - [ ] Validate: compile; run with lensing = yes
- [ ] Phase 2j: Port output module
  - [ ] Add any new output options for SINu/EFT (new columns or file types)
  - [ ] Ensure output routines write background, P(k), C_l, transfer functions in the expected format for validation
  - [ ] Validate: output files match format expected by comparison script
- [ ] Phase 2k: Port tools, main, and data
  - [ ] Update main/class.c (or equivalent) to call new modules in correct order
  - [ ] Ensure neutrinos_collision_terms, pt_matrices, external_Pk are on include path and linked
  - [ ] Update Makefile to build all new sources and link OpenBLAS/HyRec2020
  - [ ] Validate: full make class succeeds; ./class runs with SINu and with nonlinear_pt
- [ ] Phase 3: Port Python wrapper and remaining updates
  - [ ] Add SINu and EFT parameters to python/cclassy.pxd (structure declarations)
  - [ ] Add parameter setters/getters in python/classy.pyx for log10_G_eff_nu and other SINu/EFT parameters
  - [ ] Add get methods for background, P(k), C_l, transfer functions consistent with class-SINu-PT classy interface
  - [ ] Update python/setup.py or build so classy links against updated library
  - [ ] Validate: make classy or pip install .; run a short Python script that sets SINu params, computes, and retrieves observables
- [ ] Phase 4: Build and integration testing
  - [ ] Clean build: make clean; make class; make classy (or equivalent)
  - [ ] Implement comparison script (e.g. compare_outputs.py) that runs class-SINu-PT_uptodate with input files from validation_data and compares to reference
  - [ ] Run tests via ./class for all validation_data cases (vanilla, SINu, both gauges, massive/massless, nonlinear options)
  - [ ] Run tests via classy with same parameter sets
  - [ ] Apply 0.1% tolerance for synchronous and vanilla Newtonian; relaxed for SINu in Newtonian
  - [ ] Compare background quantities, P(k), C_l, transfer functions; report PASS/FAIL per quantity
  - [ ] Optionally: run vanilla test (SINu off) and compare to class_public-master output; check for memory leaks (valgrind)
- [ ] Phase 5: Documentation
  - [ ] Create validation_data/README.md (or test-suite README) explaining how to generate references and run regression tests (./class and classy)
  - [ ] Document SINu and EFT physics in code comments (perturbations, background, input, nonlinear_pt)
  - [ ] Create example notebooks: SINu with massive neutrinos, SINu with massless neutrinos, EFT/CLASS-PT usage


## Surprises & Discoveries

This section will document unexpected behaviors, bugs, optimizations, or insights discovered during implementation. As work proceeds, observations will be recorded here with evidence.


## Decision Log

- Decision: Use class_public-master as the single base; do not modify class_public-master or class-SINu-PT source. All new code lives in class-SINu-PT_uptodate. Only additive change to class-SINu-PT is validation_data/.
  Rationale: User requirement and AGENTS.md.
  Date/Author: Plan creation.

- Decision: Tolerances: 0.1% for synchronous gauge and vanilla Newtonian; relaxed/optional for SINu in Newtonian gauge.
  Rationale: User requirement.
  Date/Author: Plan update.

- Decision: Keep all nonlinear methods (Halofit, HMcode, nonlinear_pt) and test them accordingly.
  Rationale: User requirement.
  Date/Author: Plan update.

- Decision: Run regression tests using both ./class and classy.
  Rationale: User requirement.
  Date/Author: Plan update.

- Decision: Store validation inputs and reference outputs in class-SINu-PT/validation_data/; use same input files to validate class-SINu-PT_uptodate.
  Rationale: User requirement.
  Date/Author: Plan update.

- Decision: Standardize on HyRec2020 in class-SINu-PT_uptodate.
  Rationale: User requirement.
  Date/Author: Plan update.

- Decision: Phase 2 split into independent phases per module (2a–2k); Phase 3 single phase.
  Rationale: User requirement.
  Date/Author: Plan update.


## Outcomes & Retrospective

This section will summarize outcomes, gaps, and lessons learned at major milestones or at completion.


## Context and Orientation

The repository root is class-updates-via-cursor-main. Three directories matter. class_public-master/ contains the latest vanilla CLASS (from lesgourg/class_public) with no SINu or EFT/CLASS-PT physics; it must never be modified. class-SINu-PT/ contains an older CLASS fork with SINu (self-interacting neutrinos, arXiv:2309.03941) and CLASS-PT (EFT perturbation theory) already implemented; its source code must not be edited—only the additive creation of validation_data/ is allowed. class-SINu-PT_uptodate/ is the target: it starts as a copy of class_public-master and receives all ported SINu and EFT code.

CLASS is organized into modules: background (expansion, densities), thermodynamics (ionization, HyRec), perturbations (Boltzmann hierarchy), transfer (transfer functions), primordial (initial conditions), fourier (nonlinear Halofit/HMcode in current CLASS), harmonic (CMB spectra in current CLASS), lensing, output. In class-SINu-PT the older layout uses spectra instead of harmonic and nonlinear instead of fourier; the port must map SINu/EFT features onto the class_public-master layout (harmonic, fourier, C++ perturbations where applicable).

SINu adds neutrino self-interactions via an effective coupling G_eff_nu (input as log10_G_eff_nu), collision terms from precomputed tables (neutrinos_collision_terms), and TCA switches (nu_tca_on, nu_tca_off and trigger parameters). EFT/CLASS-PT adds nonlinear_pt (with pt_matrices and external_Pk), a spectra module, and nonlinear.c; the updated code must retain Halofit and HMcode from class_public-master and add nonlinear_pt and any spectra logic. Recombination in class-SINu-PT_uptodate uses HyRec2020 (from class_public-master), not the older hyrec in class-SINu-PT.


## Plan of Work

The work proceeds in phases. Phase 0 bootstraps class-SINu-PT_uptodate from class_public-master and records versions. Phase 1 builds the validation baseline by running class-SINu-PT with chosen input files and saving reference outputs in class-SINu-PT/validation_data/. Phases 2a through 2k port SINu and EFT module by module into class-SINu-PT_uptodate. Phase 3 ports the Python wrapper. Phase 4 runs integration tests using the same input files and compares to validation_data. Phase 5 adds documentation and example notebooks.

**Phase 0 — Bootstrap and version pinning.** In the repository root, create a REFERENCE or VERSION file. Record the exact version or commit of class_public-master (e.g. git rev-parse HEAD if it is a git clone) and of class-SINu-PT (commit hash or tarball name). Copy the entire class_public-master directory into class-SINu-PT_uptodate, overwriting the existing empty class-SINu-PT_uptodate directory. Change directory to class-SINu-PT_uptodate. Run make clean and then make (or make class as required by the Makefile). Confirm that the class executable is built. Run ./class with an existing .ini file from class_public-master (e.g. default.ini or explanatory.ini with minimal options). Confirm that CLASS runs and produces output files (e.g. in the output/ directory specified in the .ini). At the end of Phase 0, class-SINu-PT_uptodate is a working vanilla CLASS with no SINu or EFT code yet.

**Phase 1 — Create validation baseline.** Create the directory class-SINu-PT/validation_data/. This directory will hold all input files and all reference outputs. Define a set of test cases: (1) vanilla, synchronous gauge; (2) vanilla, Newtonian gauge; (3) SINu on, synchronous, massless neutrinos; (4) SINu on, synchronous, massive neutrinos; (5) SINu on, Newtonian, massless; (6) SINu on, Newtonian, massive; and additional cases for nonlinear options (linear, Halofit, HMcode, nonlinear_pt) as applicable. For each case, create an .ini file (and .pre if needed) and place it in validation_data/ with a clear name (e.g. vanilla_sync.ini, sinu_sync_massless.ini). From the class-SINu-PT directory, run the class executable with each .ini, e.g. ./class validation_data/vanilla_sync.ini. Save the resulting output files (background, thermodynamics if needed, matter power spectrum, CMB C_l, transfer functions) into validation_data/, either in a single directory or in per-case subdirectories (e.g. validation_data/reference_vanilla_sync/). Document in a manifest (e.g. validation_data/MANIFEST or README) which .ini produces which reference set and what observables are stored. The same .ini files will later be used in class-SINu-PT_uptodate to run the ported code and compare outputs to these references.

**Phase 2a — Port input module.** Open class-SINu-PT_uptodate/source/input.c for editing. Use class-SINu-PT/source/input.c as a read-only reference. Search in class-SINu-PT for log10_G_eff_nu, interacting_nu, nu_tca_on, nu_tca_off, and any TCA or precision parameters (start_small_k_at_tau_nu_over_tau_h, tight_coupling_trigger_tau_nu_over_tau_h, tight_coupling_trigger_tau_nu_over_tau_k, full_hierarchy_trigger_tau_nu_over_tau_k). In class-SINu-PT_uptodate/source/input.c, in the function that reads parameters (e.g. input_read_parameters or equivalent), add parsing for these parameters. Parse log10_G_eff_nu as a double and set G_eff_nu from it (e.g. pow(10, log10_G_eff_nu)). Parse interacting_nu as an integer or flag. Parse the TCA and precision parameters. Add any EFT or nonlinear_pt-specific input parameters used in class-SINu-PT. In class-SINu-PT_uptodate/include/input.h, add declarations for the new parameters to the relevant structure (e.g. precision or background). Set a flag such as has_SINu when log10_G_eff_nu is set and interacting_nu is enabled. Update class-SINu-PT_uptodate/explanatory.ini or default.ini with comments documenting the SINu and EFT parameters. Validate by compiling (make clean; make) and running ./class with a minimal .ini that sets log10_G_eff_nu and other SINu parameters; the run should not crash and parameters should be read correctly (e.g. check verbose output or a simple test that reads back parameters).

**Phase 2b — Port background module.** Open class-SINu-PT_uptodate/include/background.h and class-SINu-PT/include/background.h (read-only). In class-SINu-PT, identify fields added for SINu (e.g. log10_G_eff_nu, G_eff_nu, interacting_nu, and any indices). Add the same fields to the background structure in class-SINu-PT_uptodate/include/background.h. Open class-SINu-PT_uptodate/source/background.c and class-SINu-PT/source/background.c (read-only). In background_init, add allocation or initialization for SINu quantities when has_SINu (or equivalent) is true; add index assignments for any new background quantities. In background_solve or the function that fills the background vector, add computation or storage of SINu-related quantities (e.g. G_eff_nu). In background_functions, ensure the background vector is filled with SINu quantities at each time step if needed. In background_free, add deallocation for any SINu arrays. In the background output functions (e.g. background_output_titles and background_output_data), add columns for SINu quantities if the reference output includes them. Validate by compiling and running with a SINu .ini; the code should run without errors. Full comparison to reference will happen in Phase 4.

**Phase 2c — Port thermodynamics module.** Open class-SINu-PT_uptodate/source/thermodynamics.c and include/thermodynamics.h. Compare with class-SINu-PT (read-only). In class_public-master, HyRec is HyRec2020 (external/HyRec2020); ensure class-SINu-PT_uptodate does not use the older hyrec from class-SINu-PT. Add any SINu-specific thermodynamics indices or derived parameters (e.g. for neutrino interaction rates if stored here). Modify thermodynamics_init and thermodynamics_at_z to interpolate or compute SINu-related thermodynamics quantities if required by the perturbations module. Add SINu columns to thermodynamics output if the reference thermodynamics files include them. Validate by compiling; after Phase 2d, thermodynamics output can be compared to reference.

**Phase 2d — Port perturbations module.** This is the core SINu phase. Open class-SINu-PT_uptodate/source/perturbations.c (or .cpp if class_public-master uses C++) and include/perturbations.h. Use class-SINu-PT/source/perturbations.c as read-only reference. In class-SINu-PT, the neutrino Boltzmann equations are modified to include self-interaction collision terms; the collision terms are read from the neutrinos_collision_terms directory. Port the following: (1) Add perturbation vector indices for any new SINu neutrino variables (if not already covered by the standard neutrino hierarchy). (2) In the function that initializes the perturbation vector (e.g. perturb_vector_init), extend the vector size and assign indices for SINu. (3) In the initial conditions function, set initial values for SINu perturbations consistent with class-SINu-PT. (4) In the derivatives function (e.g. perturb_derivs), add the SINu collision terms and TCA. The TCA is controlled by nu_tca_on and nu_tca_off and trigger parameters (start_small_k_at_tau_nu_over_tau_h, tight_coupling_trigger_tau_nu_over_tau_h, tight_coupling_trigger_tau_nu_over_tau_k, full_hierarchy_trigger_tau_nu_over_tau_k). (5) Load or link the neutrinos_collision_terms data (copy the neutrinos_collision_terms directory from class-SINu-PT into class-SINu-PT_uptodate or set paths). (6) If class_public-master uses C++ for perturbations, adapt the SINu code to C++ or ensure C code is called correctly. (7) Implement gauge transformations for SINu perturbations (synchronous and Newtonian) so that both gauges are supported. Validate by compiling and running a SINu case; compare perturbation-related observables (e.g. from transfer or spectra) to reference once transfer and spectra are ported.

**Phase 2e — Port transfer module.** Open class-SINu-PT_uptodate/include/transfer.h and source/transfer.c (or .cpp). Compare with class-SINu-PT (read-only). Add transfer indices for SINu-related transfer functions (e.g. density and velocity for neutrino or other species affected by SINu). In transfer_init, increment the transfer type count and assign indices when has_SINu. In the function that fills transfer functions from perturbation sources, extract SINu transfer functions and store them. In the transfer output section, add columns for SINu transfers so that the output format matches the reference. Validate by compiling and running a SINu case; check that transfer output files contain the expected columns.

**Phase 2f — Port nonlinear module (Halofit/HMcode).** In class_public-master, nonlinear corrections are in fourier.c (not nonlinear.c). Open class-SINu-PT_uptodate/source/fourier.c and class-SINu-PT/source/nonlinear.c (read-only). In class-SINu-PT, search for any SINu-specific logic (e.g. warnings when SINu and Halofit are both enabled). Port such logic to fourier.c (e.g. in fourier_init). Ensure Halofit and HMcode remain available and unchanged from class_public-master. Validate by compiling and running with non_linear = halofit or HMcode.

**Phase 2g — Port nonlinear_pt module.** class-SINu-PT contains source/nonlinear_pt.c and include/nonlinear_pt.h, and relies on pt_matrices/, external_Pk/, and OpenBLAS. Copy nonlinear_pt.c and nonlinear_pt.h into class-SINu-PT_uptodate (source/ and include/). Copy or link the pt_matrices and external_Pk directories into class-SINu-PT_uptodate. Update the Makefile to compile nonlinear_pt.c and to link OpenBLAS (e.g. -lopenblas or path to libopenblas). In the main pipeline (main/class.c or equivalent), ensure nonlinear_pt is called after transfer and before spectra/harmonic when requested. Adapt any API differences: class_public-master may pass harmonic or fourier structures instead of spectra; ensure nonlinear_pt receives the inputs it needs (transfer functions, P(k), etc.) from the current module layout. Validate by compiling and running a run that requests nonlinear_pt; the code should complete and produce output.

**Phase 2h — Port spectra / integrate with harmonic.** In class_public-master, CMB and matter power spectra are computed in harmonic.c and fourier.c. class-SINu-PT has a separate spectra.c. Either (1) port spectra.c into class-SINu-PT_uptodate and wire it to harmonic/fourier (e.g. spectra calls harmonic and fourier and adds EFT outputs), or (2) merge the spectra logic from class-SINu-PT into harmonic.c and fourier.c. Ensure that output options mPk, tCl, pCl, lCl (and any EFT-specific outputs) are produced in the same format as the reference. Validate by comparing P(k) and C_l from a few runs to the reference files in validation_data.

**Phase 2i — Port lensing module.** Open class-SINu-PT_uptodate/source/lensing.c and class-SINu-PT/source/lensing.c (read-only). Port any SINu or EFT-specific changes (e.g. lensed Cl with SINu). If there are no substantive changes, ensure lensing runs correctly with the ported modules. Validate by running with lensing = yes.

**Phase 2j — Port output module.** Open class-SINu-PT_uptodate/source/output.c and class-SINu-PT/source/output.c (read-only). Add any new output columns or file types for SINu/EFT. Ensure that the file formats (column order, headers) match what the Phase 4 comparison script expects (aligned with validation_data reference files). Validate by inspecting output files.

**Phase 2k — Port tools, main, and data.** Open class-SINu-PT_uptodate/main/class.c (or the main entry file). Ensure the call order of modules matches the pipeline: input, background, thermodynamics, perturbations, transfer, nonlinear/fourier, nonlinear_pt (if used), harmonic/spectra, lensing, output. Add or adjust calls so that SINu and nonlinear_pt are integrated. Ensure include paths and link targets include neutrinos_collision_terms, pt_matrices, external_Pk, and HyRec2020. Update the Makefile so that all new .c files are compiled and linked and that OpenBLAS and HyRec2020 are found. Validate by running make clean; make; ./class with a full SINu .ini and a full nonlinear_pt .ini; both should run to completion.

**Phase 3 — Port Python wrapper.** Open class-SINu-PT_uptodate/python/cclassy.pxd and class-SINu-PT/python/cclassy.pxd (read-only). Add structure declarations for any new parameters or derived quantities (e.g. log10_G_eff_nu, G_eff_nu, or derived SINu/EFT quantities). Open class-SINu-PT_uptodate/python/classy.pyx and class-SINu-PT/python/classy.pyx (read-only). Add set() handling for SINu and EFT parameters so that users can call cosmo.set({'log10_G_eff_nu': -1.5, ...}). Add get methods for observables (background, get_pk, get_cl, transfer functions) so that the interface matches class-SINu-PT where applicable. Update the build (setup.py or Makefile) so that the Python extension links against the updated library. Validate by running make classy or pip install . from the python directory, then running a Python script that instantiates Class, sets SINu parameters, calls compute(), and retrieves at least one observable (e.g. P(k) or C_l).

**Phase 4 — Build and integration testing.** In class-SINu-PT_uptodate, run make clean, make class, and make classy (or equivalent). Implement a comparison script (e.g. compare_outputs.py in the repo root or in class-SINu-PT_uptodate). The script should: (1) For each input file in class-SINu-PT/validation_data/, run class-SINu-PT_uptodate (either by invoking ./class with that .ini or by using classy with the same parameters). (2) Load the reference outputs from validation_data for that case. (3) Compare background quantities, P(k), C_l, and transfer functions (as available) between the new run and the reference. (4) Apply 0.1% relative tolerance for synchronous gauge and for vanilla Newtonian; apply relaxed or optional tolerance for SINu in Newtonian gauge. (5) Report PASS or FAIL per quantity and per case. Run the script for all validation cases. Run tests via both the CLI (./class) and classy. Optionally run a vanilla test (SINu and EFT off) and compare to class_public-master output to ensure no regression. Optionally run valgrind to check for memory leaks. Document how to run the comparison (e.g. from repo root: python compare_outputs.py --cli and python compare_outputs.py --classy).

**Phase 5 — Documentation.** Create validation_data/README.md (in class-SINu-PT) or a test-suite README in class-SINu-PT_uptodate that explains: how to generate reference data (run class-SINu-PT with the validation_data .ini files and save outputs), how to run regression tests (run class-SINu-PT_uptodate with the same .ini files, then run the comparison script), what each parameter file tests (vanilla vs SINu, gauges, neutrino type, nonlinear method), and how to interpret results (0.1% vs relaxed for SINu+Newtonian). Add comments in the source code (perturbations, background, input, nonlinear_pt) documenting the SINu and EFT physics (e.g. Boltzmann equations with collision terms, TCA, EFT kernels). Create example Jupyter notebooks under class-SINu-PT_uptodate/notebooks/: one for SINu with massive neutrinos, one for SINu with massless neutrinos, and one for EFT/CLASS-PT usage. The notebooks should be runnable with the updated code and classy.


## Concrete Steps

The following commands assume the working directory is the repository root (class-updates-via-cursor-main). **For which conda environment to use with each CLASS codebase (class_public-master, class-SINu-PT, class-SINu-PT_uptodate) when running classy or creating validation data, see TESTING_SETUP.md.**

**Phase 0 — Bootstrap:**

    # Record versions (adjust paths if your repo layout differs)
    echo "class_public-master: $(cd class_public-master && git rev-parse HEAD 2>/dev/null || echo 'no-git')" > REFERENCE
    echo "class-SINu-PT: $(cd class-SINu-PT && git rev-parse HEAD 2>/dev/null || echo 'no-git')" >> REFERENCE

    # Copy class_public-master to class-SINu-PT_uptodate (overwrites existing)
    rm -rf class-SINu-PT_uptodate
    cp -r class_public-master class-SINu-PT_uptodate

    # Build and run inside conda env per TESTING_SETUP.md
    conda activate conda_sinu_pt_uptodate   # create first: conda create -n conda_sinu_pt_uptodate python=3.10 -y
    cd class-SINu-PT_uptodate
    make clean
    make
    ./class default.ini

(Confirm that output files appear. If default.ini is not present, use another .ini from class_public-master.)

**Phase 1 — Validation baseline:**

    # Create validation_data in class-SINu-PT
    mkdir -p class-SINu-PT/validation_data

    # Create .ini files (e.g. vanilla_sync.ini, sinu_sync_massless.ini, ...) and place in validation_data/
    # Then run class-SINu-PT for each and save outputs:
    cd class-SINu-PT
    ./class validation_data/vanilla_sync.ini
    mkdir -p validation_data/reference_vanilla_sync
    cp output/*.dat validation_data/reference_vanilla_sync/   # adjust to actual output paths and names

    # Repeat for each test case; document in validation_data/README or MANIFEST

**Phases 2a–2k and 3 — Editing:**

Edit only files in class-SINu-PT_uptodate/. Use class-SINu-PT/ and class_public-master/ as read-only references. After each phase (or group of edits), test compilation:

    cd class-SINu-PT_uptodate
    make clean
    make

Run a minimal test:

    ./class validation_data/vanilla_sync.ini

(Use an .ini that exists in validation_data; if validation_data is under class-SINu-PT, run e.g. ./class ../class-SINu-PT/validation_data/vanilla_sync.ini from class-SINu-PT_uptodate.)

**Phase 4 — Integration testing:**

    cd class-SINu-PT_uptodate
    make clean
    make
    make classy   # or: cd python && pip install .

    # Run comparison script (implement compare_outputs.py to use validation_data inputs and references)
    python compare_outputs.py --cli
    python compare_outputs.py --classy

Example comparison (Python) for one observable:

    import numpy as np
    new_pk = np.loadtxt('class-SINu-PT_uptodate/output/..._pk.dat')
    ref_pk = np.loadtxt('class-SINu-PT/validation_data/reference_vanilla_sync/..._pk.dat')
    reldiff = np.abs(new_pk[:,1] - ref_pk[:,1]) / (np.abs(ref_pk[:,1]) + 1e-30)
    print('Max P(k) relative error:', np.max(reldiff))   # expect < 0.001 for 0.1% tolerance

**Phase 5 — Documentation:**

    # Add validation_data/README.md and/or test-suite README
    # Add code comments in source files
    # Create notebooks in class-SINu-PT_uptodate/notebooks/


## Validation and Acceptance

After completing Phase 4, the implementation is accepted if the following hold.

- **Build:** From class-SINu-PT_uptodate, `make class` and `make classy` (or equivalent) complete without error.
- **CLI run:** Executing `./class` with any validation_data input file (e.g. `./class ../class-SINu-PT/validation_data/vanilla_sync.ini`) completes without error and produces the expected output files (background, mPk, C_l, transfer functions as requested in the .ini).
- **Regression — synchronous and vanilla Newtonian:** For all validation cases in synchronous gauge and for vanilla cases in Newtonian gauge, the comparison script reports PASS: relative differences for background quantities, P(k), C_l, and transfer functions are less than 0.1%.
- **Regression — SINu in Newtonian gauge:** For SINu cases in Newtonian gauge, the comparison may use a relaxed or optional tolerance; document the criterion and ensure the script does not falsely fail.
- **Regression — both drivers:** The same comparisons pass when the updated code is run via the CLI and via the Python interface (classy).
- **Nonlinear options:** Tests for linear, Halofit, HMcode, and nonlinear_pt (where applicable) complete and comparisons are consistent with the chosen tolerances.
- **Documentation:** validation_data/README (or test-suite README) explains how to generate references and run regression tests. Example notebooks run successfully with the updated code and classy.


## Idempotence and Recovery

Phases can be resumed: if Phase N is partially done, continue editing in class-SINu-PT_uptodate without reverting prior work. A failed compile does not corrupt the tree; fix the code and re-run make. To start over, remove class-SINu-PT_uptodate and copy class_public-master again; re-apply changes (or use patches). class_public-master and class-SINu-PT (except validation_data/) remain unchanged and serve as stable references. If comparison fails, diff the ported code against class-SINu-PT (read-only) to find missing or incorrect logic. If the Python wrapper fails to build, ensure cclassy.pxd and the C headers match and that the library is built with the same compiler flags.


## Artifacts and Notes

This section will be populated with transcripts, diffs, or snippets as implementation proceeds (e.g. successful build output, sample comparison script output, valgrind summary).


## Interfaces and Dependencies

The following are the main interfaces and dependencies for the SINu and EFT port. Exact names and types should be taken from class-SINu-PT (read-only) and replicated in class-SINu-PT_uptodate; the list below is indicative.

**Background (include/background.h):** The background structure should contain SINu-related fields, e.g. `double log10_G_eff_nu`, `double G_eff_nu`, `int interacting_nu`, and any indices for SINu quantities used in the background vector. See class-SINu-PT/include/background.h.

**Input (source/input.c, include/input.h):** Parameters to parse include log10_G_eff_nu, interacting_nu, nu_tca_on, nu_tca_off, start_small_k_at_tau_nu_over_tau_h, tight_coupling_trigger_tau_nu_over_tau_h, tight_coupling_trigger_tau_nu_over_tau_k, full_hierarchy_trigger_tau_nu_over_tau_k, and any EFT/nonlinear_pt parameters. See class-SINu-PT/source/input.c.

**Perturbations (include/perturbations.h, source/perturbations.c or .cpp):** Perturbation vector indices for the SINu neutrino hierarchy; collision term data from neutrinos_collision_terms; TCA logic and trigger parameters. See class-SINu-PT/source/perturbations.c.

**Transfer, nonlinear (fourier), nonlinear_pt, spectra/harmonic, lensing, output:** Add or adapt indices and output columns so that SINu and EFT observables are produced in the same format as the reference. See corresponding files in class-SINu-PT.

**Data and externals:** neutrinos_collision_terms/ (from class-SINu-PT), pt_matrices/, external_Pk/; OpenBLAS for nonlinear_pt; HyRec2020 from class_public-master (external/HyRec2020). Ensure Makefile and include paths point to these.

**Python (python/cclassy.pxd, python/classy.pyx):** Expose log10_G_eff_nu and other SINu/EFT parameters for set(); expose get methods for background, P(k), C_l, and transfer functions so that classy matches class-SINu-PT usage where applicable.
