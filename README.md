# Metallurgical Process Window Optimization & Line Control

Standalone web application (PWA) for metallurgical data analysis, process window discovery, and feed-forward line setup across **Hot Rolling Mills (HSM)** and **Continuous Annealing / Galvanizing Lines (CAL / CGL)**.

It analyzes historical production data (hot rolling, cold rolling, cast chemistry, and continuous annealing) to **minimize mechanical rejection rates** against user-defined target specifications:
* **Yield Strength ($R_p$ / YS):** $R_p \ge R_{p,\min}$ (e.g., $460\,\text{MPa}$)
* **Ultimate Tensile Strength ($R_m$ / UTS):** $R_m \le R_{m,\max}$ (e.g., $680\,\text{MPa}$)
* **Elongation ($A\%$):** $A\% > A_{\min}$ *(automatically evaluated whenever elongation data is mapped)*

---

## 🧠 Why Physics-Informed Statistical Models Instead of a Neural Network?

Unlike black-box **Neural Networks (Deep Learning)**—which typically require thousands of training coils, hide decision logic, and can extrapolate unpredictably outside historical operating boundaries—this application combines **metallurgical domain equations**, **interpretable CART decision trees**, and **regularized piecewise-spline Ridge regression with Monte-Carlo risk simulation**:

| Criterion | This Application (CART + Spline-Ridge + Monte-Carlo) | Neural Networks (MLP / Deep Learning) |
| :--- | :--- | :--- |
| **Required Dataset Size** | **Small to medium (30–1,000+ coils)** per grade thanks to L2 regularization and built-in metallurgical indices ($\text{Nb}_{\text{eff}}$, $C_{\text{eq}}$). | **Large (typically > 2,000–5,000 coils)**; prone to overfitting noise on typical grade-specific industrial datasets. |
| **Process Interpretability** | **Full transparency:** extracts explicit shop-floor rules (e.g., `T_recuit ≤ 780.5 °C AND CR > 64.15%`). | **Black box:** requires post-hoc explainability layers (SHAP/LIME) to justify setpoints to metallurgists and operators. |
| **Non-Linearity Handling** | **Piecewise splines (P33/P67 knots) + process/chemistry interactions** capture recrystallization plateaus and transformation slopes without polynomial divergence. | Captures high-order interactions well on massive datasets, but can oscillate wildly between sparse data points. |
| **Extrapolation Safety** | **Quantified leverage ($\times k$):** automatically widens $\pm$ uncertainty bands and lowers compliance confidence when inputs leave the historical cloud. | Often produces overconfident predictions far outside the training domain. |
| **Deployment & Privacy** | **100% browser-based (single HTML file, zero backend)**, runs in milliseconds offline. | Usually requires Python servers (PyTorch/TensorFlow) or heavy ONNX runtime pipelines. |

---

## 🔒 Privacy & Technical Architecture
* **100% Local & Confidential:** Runs entirely inside your web browser (HTML5 / JavaScript). No industrial data (`.xlsm`, `.xlsx`, `.xls`, `.csv`) is ever uploaded, transmitted, or stored on GitHub or any external server.
* **Zero Installation:** Works directly in any modern desktop or mobile browser and can be installed as a Progressive Web App (PWA) with offline support.

---

## ⚙️ Key Features

### 1. Multi-Route & Multi-Grade Support
* **Selectable Process Route:**
  * **Hot Rolling + Annealing / Galva:** Full process analysis from hot-band through cold reduction (`%CR`) and continuous annealing (`T_anneal`, line speed).
  * **Hot Rolling Only (Stop at Coiling `CT`):** Automatically makes cold-rolling and annealing columns optional and switches the simulator to direct hot-rolled property prediction and `CT` sensitivity analysis.
* **Selectable Steel Family:**
  * **HSLA (Microalloyed Nb/Ti):** Evaluates effective free Niobium ($\text{Nb}_{\text{eff}}$), IIW Carbon Equivalent ($C_{\text{eq}}$), and precipitation hardening potential.
  * **C-Mn / Mild Steel:** Evaluates ferrite grain refinement vs. coarsening driven by ROT cooling and coiling temperature (`CT`).
  * **DP / AHSS (Multiphase):** Supports extended hardenability chemistry (`Si`, `Cr`, `Mo`, `B`), computes an extended hardenability $C_{\text{eq}}$, and estimates **Andrews critical temperatures ($Ac_1$ and $Ac_3$)** to benchmark the intercritical annealing window.

### 2. Multi-Format Import & Dynamic Column Mapping
* Direct client-side parsing of macro-enabled Excel workbooks (`.xlsm`), `.xlsx`, `.xls`, and `.csv` files.
* Interactive selection of worksheet, header row number, and column mapping (automatically saved in `localStorage`).
* Fixed test direction filtering (`L`, `S`, `D`) to prevent mechanical anisotropy bias.

### 3. Metallurgical Indices & Thickness Stratification
* Automatic calculation of:
  * **Effective Free Niobium:** $\text{Nb}_{\text{eff}} = \text{Nb} - \max\left(0,\, 6.64 \cdot (\text{N} - 0.292 \cdot \text{Ti})\right)$
  * **Carbon Equivalent ($C_{\text{eq}}$):** Standard IIW ($C + \text{Mn}/6$) for HSLA/C-Mn, or extended hardenability formula ($C + \frac{\text{Mn}+\text{Si}}{6} + \frac{\text{Cr}+\text{Mo}}{5} + 5\text{B}$) for DP/AHSS.
  * **HSM Cooling Potential:** $\frac{V_{\text{rot}}}{\text{CT} - 400}$
* Flexible gauge stratification: **Single Regime** mode (using thickness `Th` directly as a model feature) or **3-Regime Split** (`Thin`, `Medium`, `Thick`) based on user-defined thickness thresholds.

### 4. Visual CART Decision Tree & 2D Operating Windows
* **Hierarchical Branch Tree & Rules Table:** Gini-impurity CART splitting displaying both the visual ASCII branch hierarchy and a ranked summary table of terminal leaves (`Compliant`, `Soft Reject`, `Hard Reject`, `Ductility Reject`, `Multiple Reject`).
* **Interactive 2D Scatter Plots (Plotly):** Explore any pair of process or chemistry variables colored by compliance status with detailed coil tooltips.

### 5. Feed-Forward Simulator with Splines & Distance-Based Uncertainty
* **Coil-Grouped 5-Fold Cross-Validation:** Automatically selects the best model complexity (`linear`, `quadratic + interactions`, or `piecewise spline + interactions`) based on out-of-sample cross-validation error grouped by `CoilID`.
* **Flexible Optimization & What-If Simulation:**
  * Load any historical coil by `CoilID` in one click or enter parameters manually.
  * Leave `Annealing Temp` and/or `Line Speed` blank to let the optimizer find the safest operating plateau, or enter fixed values to simulate specific line settings.
  * In **Hot Rolling Only** mode, predicts $R_p$, $R_m$, $A\%$ at the entered `CT` and displays a sensitivity table across $\text{CT} \pm 20\,^\circ\text{C}$.
* **Joint Compliance Probability & Leverage Uncertainty ($\times k$):**
  * Uses correlated Cholesky + Monte-Carlo draws (2,500 samples) to compute the **joint probability** of meeting $R_p$, $R_m$, and $A\%$ simultaneously.
  * Computes a **leverage-based uncertainty multiplier ($\times k$)** from the statistical distance to the historical training cloud, automatically widening predicted $\pm$ intervals and lowering compliance confidence when extrapolating outside historical ranges.

---

## 🚀 Quick Start Guide
1. **Load Data:** Upload a quality/process export file (`.xlsm`, `.xlsx`, `.xls`, or `.csv`), select the target sheet, and specify the header row index.
2. **Select Route, Grade & Criteria:** Choose the **Process route** (`Hot Rolling + Annealing / Galva` or `Hot Rolling only`), **Steel family** (`HSLA`, `C-Mn`, or `DP / AHSS`), test direction, and mechanical specification limits ($R_{p,\min}$, $R_{m,\max}$, $A_{\min}$).
3. **Map Columns:** Map the required columns (marked with `*` dynamically according to the selected route) and optional chemistry/process variables (`V_rot`, `Nb`, `Ti`, `N`, `C`, `Mn`, `Si`, `Cr`, `Mo`, `B`, `CoilID`, `LENGTH_POS_MOTHER`, `TEMP_START_F7`), then click **Run Analysis**.
4. **Analyze & Simulate:**
   * Review rejection KPIs, the visual **CART branch tree**, and 2D scatter windows in Sections 3 & 4.
   * Use **Section 5 (Simulator)** to predict properties or determine optimal annealing setpoints and sensitivity grids for upcoming coils.

---

## 📁 Repository Structure
* `index.html`: Complete standalone application (UI, Excel parser, CART / Piecewise-Spline Ridge / Monte-Carlo engine, and Plotly visualizations).
* `manifest.json`: Progressive Web App (PWA) manifest for desktop/mobile installation.
* `sw.js`: Service Worker for offline caching (optional).
* `.github/workflows/check-html.yml`: Automated GitHub Actions syntax check for inline JavaScript on push/PR (optional).
* `README.md`: Technical documentation and user guide.
