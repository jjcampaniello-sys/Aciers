# Optimisation des Fenêtres Procédés & Pilotage Galva (Aciers HSLA)

Application web autonome (PWA) d'analyse métallurgique et d'aide au réglage pour les lignes de galvanisation continue (grade cible type **CR460LA-GI**). 

Elle permet d'analyser l'historique de production (laminage à chaud, laminage à froid, chimie de coulée et recuit continu) afin de **réduire le taux de rejet mécanique sous 5 %** selon trois critères :
* **Limite d'élasticité :** $R_p \ge 460\,\text{MPa}$
* **Résistance à la traction :** $R_m \le 680\,\text{MPa}$
* **Allongement à la rupture :** $A\% > 15\,\%$ *(uniquement en sens longitudinal `L`)*

---

## 🔒 Confidentialité et Architecture Technique
* **100 % Local & Confidentiel :** L'application fonctionne exclusivement dans le navigateur web (HTML5 / JavaScript). Aucune donnée industrielle (`.xlsm`, `.xlsx`, `.csv`) n'est envoyée ni stockée sur GitHub ou sur un serveur externe.
* **Zéro installation :** Accessible depuis n'importe quel navigateur moderne (PC ou mobile) et installable en tant que Progressive Web App (PWA) avec support hors-ligne.

---

## ⚙️ Fonctionnalités Principales

1. **Importation multi-format & Mapping dynamique :**
   * Lecture directe des classeurs Excel avec macros (`.xlsm`), `.xlsx` et `.csv`.
   * Sélection de l'onglet, de la ligne d'en-têtes et association libre des colonnes (mémorisée automatiquement dans le navigateur).
   * Filtrage dynamique par direction d'essai (`BEPROEV_RICHTING` : `L`, `S`, `D`, ou `TOUS`) pour éviter les biais liés à l'anisotropie mécanique.

2. **Indices Métallurgiques & Stratification par Régimes :**
   * Calcul automatique du **Niobium effectif libre** ($\text{Nb}_{\text{eff}}$), du **Carbone équivalent** ($C_{\text{eq}}$) et du **Potentiel HSM** ($\frac{V_{\text{rot}}}{\text{CT} - 400}$).
   * Segmentation automatique des bobines en **3 régimes de recristallisation** :
     * **Régime A (Fortes épaisseurs $\ge 1,4\,\text{mm}$ ou $\%\text{CR} < 58\%$) :** Recristallisation lente, sensibilité au grossissement des précipités de Nb.
     * **Régime B (Transition) :** Épaisseurs intermédiaires ($1,0\text{--}1,4\,\text{mm}$).
     * **Régime C (Fines épaisseurs $\le 1,0\,\text{mm}$ ou $\%\text{CR} > 63\%$) :** Recristallisation rapide, sensibilité à la trempe intercritique.

3. **Extraction de Règles (Arbre de Décision CART) & Cartographie 2D :**
   * Identification automatique des seuils critiques de procédé ($T_{\text{recuit}}$, $\text{CT}$, vitesse de ligne, $V_{\text{rot}}$, $\%\text{CR}$) sur 3 niveaux.
   * Visualisation interactive des fenêtres conformes et des modes de défaillance (`Rejet Doux` $R_p < 460\,\text{MPa}$, `Rejet Dur` $R_m > 680\,\text{MPa}$, `Rejet Ductilité` $A \le 15\,\%$ en sens `L`, et `Rejet Multiple`).
   * Repérage visuel direct de la bobine sélectionnée dans le simulateur sur le nuage de points 2D.

4. **Simulateur Dynamique Feed-Forward (Consigne Galva) :**
   * Calibration automatique par régression multiple (Ridge-OLS) avec **validation croisée (5-fold CV)** sur l'historique du régime concerné.
   * Sélection en un clic par **Code Bobine (`ROL_IDENT`)** ou saisie manuelle.
   * Recommandation du couple optimal **(Température de recuit + Vitesse de ligne)** centré sur le plateau de conformité maximale, accompagnée d'une **grille de sensibilité** ($R_p$, $R_m$, $A\%$ prévus et probabilité de conformité) et d'alertes métallurgiques sur le Potentiel HSM.

---

## 🚀 Guide d'Utilisation Rapide

1. **Charger les données :** Importer le fichier d'export qualité/procédé (`.xlsm`, `.xlsx` ou `.csv`), choisir l'onglet et indiquer le numéro de la ligne des titres (ex. ligne `4`).
2. **Associer les colonnes :** Relier les 6 paramètres obligatoires (`Rp`, `Rm`, `Épaisseur`, `%CR`, `CT`, `T_recuit`) ainsi que les colonnes optionnelles (`Allongement A%`, vitesses `Galva` et `ROT`, chimie `Nb/Ti/N/C/Mn`, direction et code bobine `ROL_IDENT`).
3. **Filtrer la direction :** Sélectionner la direction de référence de la norme (ex. `L` - Longitudinal, qui active automatiquement le contrôle $A\% > 15$).
4. **Analyser et Simuler :**
   * Consulter l'arbre CART et les graphiques 2D par régime pour identifier les fenêtres sûres.
   * Utiliser la **Section 5 (Simulateur)** avant le passage d'une bobine sur ligne de galvanisation pour obtenir sa consigne de recuit et sa vitesse optimales.

---

## 📁 Structure du Dépôt
* `index.html` : Code complet de l'application (interface, décodeur Excel, moteur statistique CART/Ridge-OLS et graphiques Plotly).
* `manifest.json` : Fichier de configuration permettant l'installation sur bureau ou smartphone (PWA).
* `sw.js` : Service Worker assurant la mise en cache et le fonctionnement hors-ligne (optionnel).
* `README.md` : Documentation technique et guide utilisateur.
