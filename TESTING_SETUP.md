# Conda environments for CLASS codebases (upgrade testing)

This document defines which conda environment to use with which CLASS codebase when executing the SINu/EFT upgrade plan (ExecPlan-SINu-PT-upgrade.md). Use it so that validation data is created with the correct CLASS code and so tests run against the intended build.

**Repository root:** `class-updates-via-cursor-main`  
**CLASS directories:** `class_public-master/`, `class-SINu-PT/`, `class-SINu-PT_uptodate/`

---

## Conda environments (one per CLASS codebase)

| Conda env name           | CLASS directory           | Purpose |
|--------------------------|---------------------------|---------|
| `conda_class_public`     | class_public-master       | Vanilla CLASS (no SINu/EFT). Build and run for sanity checks or vanilla comparison. |
| `conda_sinu_pt`          | class-SINu-PT             | Reference code with SINu + EFT. **Use this to generate all validation_data reference outputs.** |
| `conda_sinu_pt_uptodate` | class-SINu-PT_uptodate    | Ported code (target of upgrade). Use for building, editing, and testing after the port. |

---

## When to use which env (ExecPlan phases)

| Phase / activity | CLASS code to use | Conda env to activate |
|------------------|-------------------|------------------------|
| **Phase 0** — Optional: run vanilla class_public-master (./class or classy) | class_public-master | `conda_class_public` |
| **Phase 1** — Create validation baseline (reference outputs) | **class-SINu-PT** only | **`conda_sinu_pt`** |
| **Phase 1** — Run class-SINu-PT via classy or ./class to fill validation_data | class-SINu-PT | **`conda_sinu_pt`** |
| **Phases 2a–2m** — Port and build in class-SINu-PT_uptodate | class-SINu-PT_uptodate | `conda_sinu_pt_uptodate` |
| **Phase 3** — Port Python wrapper; test classy | class-SINu-PT_uptodate | `conda_sinu_pt_uptodate` |
| **Phase 4** — Integration tests: classy comparison | class-SINu-PT_uptodate | **`conda_sinu_pt_uptodate`** |
| **Phase 4** — Optional: vanilla comparison vs class_public-master | class_public-master | `conda_class_public` |

**Rule of thumb:**  
- **Creating validation_data reference outputs** → **`conda_sinu_pt`** and run from **class-SINu-PT**.  
- **Building or testing the ported code** → **`conda_sinu_pt_uptodate`** and run from **class-SINu-PT_uptodate**.  
- **Running vanilla class_public-master** → **`conda_class_public`** and run from **class_public-master**.

---

## Create and use the environments

Commands assume the repository root is your current directory. Adjust paths if your layout differs.

### 1. Environment for class_public-master (vanilla CLASS)

```bash
conda create -n conda_class_public python=3.10 -y
conda activate conda_class_public
cd class_public-master
make clean && make
cd python && pip install -e . && cd ../..
```

### 2. Environment for class-SINu-PT (reference — use for validation_data)

```bash
conda create -n conda_sinu_pt python=3.10 -y
conda activate conda_sinu_pt
cd class-SINu-PT
make clean && make
cd python && pip install -e . && cd ../..
```

**Use this env whenever you generate or verify reference outputs in class-SINu-PT/validation_data/.**

### 3. Environment for class-SINu-PT_uptodate (ported code)

```bash
conda create -n conda_sinu_pt_uptodate python=3.10 -y
conda activate conda_sinu_pt_uptodate
cd class-SINu-PT_uptodate
make clean && make && make classy
```

Use this env when building, testing, or running classy against the ported code.

---

## Quick reference (for agents and scripts)

- **class_public-master** → `conda_class_public`
- **class-SINu-PT** → `conda_sinu_pt` (and **always** for creating validation_data)
- **class-SINu-PT_uptodate** → `conda_sinu_pt_uptodate` (for Phase 4 classy tests)
