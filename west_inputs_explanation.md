# WEST Input Files and Keywords Explanation

This document explains the purpose of the two input files `ddh_wbse_init.in` and `ddh_sc_wbse.in` used in the **WEST (Without-Empty-States)** code, along with descriptions of each of the keywords defined within them.

For official details, refer to the [WEST Manual](https://west-code.org/doc/West/latest/manual.html).

---

## 1. Overview of the Input Files

### `ddh_wbse_init.in`
* **Purpose**: This file is used for the **initialization phase** of the Bethe-Salpeter Equation (BSE) or Time-Dependent Density Functional Theory (TDDFT) calculation. It is typically passed as input to the `wbse_init.x` executable.
* **What it does**: It configures the orbital localization (e.g., using Wannier functions) and sets up the calculation of the screened exchange integrals. By doing so, it prepares the localized basis set representation that allows WEST to compute excited states without needing explicit calculation of empty (unoccupied) electronic states.

### `ddh_sc_wbse.in`
* **Purpose**: This file is used for the **main calculation phase** to solve for excitation energies, absorption spectra, or excited-state properties. It is typically passed as input to the `wbse.x` executable.
* **What it does**: It defines the solver type (Davidson diagonalization), details the eigenvalues to compute (40 lowest states), convergence criteria, preconditioning, analytical forces for the first excited state, and low-rank exact exchange approximation.

---

## 2. Keyword Dictionary

Here is a detailed breakdown of the keywords present in these files, organized by input block.

### Section: `input_west`
This block defines the general input/output directories and prefix parameters for the run.

| Keyword | Type | Value | Meaning |
| :--- | :--- | :--- | :--- |
| **`qe_prefix`** | String | `ddh` | Prefix used for the Quantum ESPRESSO save directory (`.save` folder). This must match the prefix used in the preceding DFT ground-state calculation. |
| **`west_prefix`** | String | `ddh_west` | Prefix prepended to the WEST save and restart directories (e.g., `ddh_west.save`). |
| **`outdir`** | String | `./` | The directory where input, output, temporary, and restart files are read/written. Here, it is set to the current directory. |

---

### Section: `wbse_init_control`
This block configures the initialization run settings for `wbse_init.x`.

| Keyword | Type | Value | Meaning |
| :--- | :--- | :--- | :--- |
| **`wbse_init_calculation`** | String | `S` | Specifies the type of initialization calculation. `S` stands for starting from scratch to calculate the screened exchange integrals. |
| **`solver`** | String | `TDDFT` | Specifies the theory or method used for calculating excitations. `TDDFT` refers to Time-Dependent Density Functional Theory. |
| **`localization`** | String | `W` | Selects the localization technique for the wavefunctions. `W` specifies Wannier functions, which map the Kohn-Sham orbitals into localized representations to reduce computation. |
| **`overlap_thr`** | Float | `0.001` | The threshold for localized orbital overlaps. If the overlap between two localized orbitals is smaller than this value, the corresponding screened exchange integral is skipped to accelerate calculations. |

---

### Section: `wbse_control`
This block configures the main solver run settings for `wbse.x` (only present in `ddh_sc_wbse.in`).

| Keyword | Type | Value | Meaning |
| :--- | :--- | :--- | :--- |
| **`wbse_calculation`** | String | `D` | Specifies the solver algorithm. `D` stands for **Davidson diagonalization**, an iterative method used to find the lowest eigenvectors/eigenvalues. (Alternatively, `L` is for Lanczos spectrum calculations). |
| **`n_liouville_eigen`** | Integer | `40` | The number of Liouville eigenvalues (excitation energies) and eigenvectors to calculate. |
| **`n_liouville_maxiter`** | Integer | `300` | The maximum number of Davidson iterations allowed before the solver stops. |
| **`trev_liouville`** | Float | `0.000005` | Absolute convergence threshold for the Liouville eigenvalues. Convergence is achieved when residual norms fall below this. |
| **`trev_liouville_rel`** | Float | `0.00001` | Relative convergence threshold for the Liouville eigenvalues. |
| **`l_pre_shift`** | Boolean | `False` | Specifies whether to apply a diagonal shift to the preconditioner. Here it is turned off (`False`). |
| **`l_preconditioning`** | Boolean | `True` | Enables preconditioning during the Davidson diagonalization to accelerate convergence. |
| **`l_forces`** | Boolean | `True` | Flag to enable calculation of analytical forces (gradients) for the excited state. Required for excited-state geometry optimization. |
| **`forces_state`** | Integer | `1` | The index of the excited state for which analytical forces are computed. `1` corresponds to the first excited state. |
| **`n_exx_lowrank`** | Integer | `200` | Specifies the rank for the low-rank approximation of the Exact Exchange (EXX) potential, saving significant memory and CPU resources. |
