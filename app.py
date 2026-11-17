import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.model_selection import train_test_split

st.set_page_config(page_title="Optimisation HSLA - PWA", layout="wide")
st.title("Analyse Métallurgique & Fenêtres Procédés (HSLA)")

uploaded_file = st.sidebar.file_uploader("Charger votre fichier (.xlsm, .xlsx, .csv)", type=["xlsm", "xlsx", "csv"])

if uploaded_file is not None:
    # 1. Lecture multi-format et choix de l'onglet
    if uploaded_file.name.endswith('.csv'):
        df_raw = pd.read_csv(uploaded_file)
    else:
        excel_file = pd.ExcelFile(uploaded_file, engine='openpyxl')
        onglet = st.sidebar.selectbox("Sélectionnez l'onglet des données :", excel_file.sheet_names)
        ligne_entete = st.sidebar.number_input("Ligne des en-têtes (0 = 1ère ligne) :", min_value=0, max_value=20, value=0)
        df_raw = pd.read_excel(excel_file, sheet_name=onglet, header=ligne_entete)

    st.sidebar.success(f"{len(df_raw)} lignes détectées.")
    cols = ["(Non disponible)"] + list(df_raw.columns)

    # 2. Association interactive des colonnes
    with st.expander("1. Associer les colonnes de votre fichier Excel", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        col_rp = c1.selectbox("Limite d'élasticité (Rp) *", cols)
        col_rm = c2.selectbox("Résistance traction (Rm) *", cols)
        col_th = c3.selectbox("Épaisseur finale (mm) *", cols)
        col_cr = c4.selectbox("Réduction à froid (%CR) *", cols)

        c5, c6, c7, c8 = st.columns(4)
        col_ct = c5.selectbox("Temp. Bobinage (CT) *", cols)
        col_trec = c6.selectbox("Temp. Recuit Galva *", cols)
        col_vgalva = c7.selectbox("Vitesse ref. Galva", cols)
        col_vrot = c8.selectbox("Vitesse ref. ROT", cols)

        c9, c10, c11, c12 = st.columns(4)
        col_nb = c9.selectbox("Niobium (Nb wt%)", cols)
        col_ti = c10.selectbox("Titane (Ti wt%)", cols)
        col_n = c11.selectbox("Azote (N wt%)", cols)
        col_c = c12.selectbox("Carbone (C wt%)", cols)
        col_mn = c1.selectbox("Manganèse (Mn wt%)", cols)

    obligatoires = [col_rp, col_rm, col_th, col_cr, col_ct, col_trec]
    if "(Non disponible)" in obligatoires:
        st.warning("Veuillez sélectionner au moins les 6 colonnes marquées d'un astérisque (*) pour lancer l'analyse.")
        st.stop()

    # Préparation du tableau propre
    df = pd.DataFrame()
    df['Rp'] = pd.to_numeric(df_raw[col_rp], errors='coerce')
    df['Rm'] = pd.to_numeric(df_raw[col_rm], errors='coerce')
    df['Th'] = pd.to_numeric(df_raw[col_th], errors='coerce')
    df['CR'] = pd.to_numeric(df_raw[col_cr], errors='coerce')
    df['CT'] = pd.to_numeric(df_raw[col_ct], errors='coerce')
    df['T_recuit'] = pd.to_numeric(df_raw[col_trec], errors='coerce')

    opt_map = {'V_ref_galva': col_vgalva, 'V_ref_ROT': col_vrot, 'Nb': col_nb, 'Ti': col_ti, 'N': col_n, 'C': col_c, 'Mn': col_mn}
    for k, v in opt_map.items():
        if v != "(Non disponible)":
            df[k] = pd.to_numeric(df_raw[v], errors='coerce')

    df = df.dropna(subset=['Rp', 'Rm', 'Th', 'CR', 'CT', 'T_recuit']).copy()

    # 3. Calculs métallurgiques et Statut Qualité
    conditions = [(df['Rp'] < 460) & (df['Rm'] > 610), (df['Rp'] < 460), (df['Rm'] > 610)]
    choices = ['Double_Rejet', 'Rejet_Doux (Rp<460)', 'Rejet_Dur (Rm>610)']
    df['Statut'] = np.select(conditions, choices, default='Conforme')
    df['Est_Conforme'] = (df['Statut'] == 'Conforme').astype(int)

    if all(x in df.columns for x in ['Nb', 'N', 'Ti']):
        df['Nb_eff'] = df['Nb'] - np.maximum(0, 6.64 * (df['N'] - 0.292 * df['Ti']))
    if all(x in df.columns for x in ['C', 'Mn']):
        df['C_eq'] = df['C'] + df['Mn'] / 6.0

    # Segmentation par Régime Procédé
    def classer_regime(r):
        if r['Th'] >= 1.4 or r['CR'] < 58:
            return 'Régime A (Fortes ép. / Bas %CR)'
        elif r['Th'] <= 1.0 or r['CR'] > 63:
            return 'Régime C (Fines ép. / Haut %CR)'
        return 'Régime B (Transition)'

    df['Regime'] = df.apply(classer_regime, axis=1)

    # 4. Tableau de bord et Arbre de Décision
    st.header("2. Diagnostic Global & Régimes Métallurgiques")
    m1, m2, m3 = st.columns(3)
    m1.metric("Taux de Rejet Global", f"{(1 - df['Est_Conforme'].mean())*100:.1f} %", "Cible : < 5.0 %", delta_color="inverse")
    m2.metric("Rejets Doux (Rp < 460)", f"{(df['Statut'] == 'Rejet_Doux (Rp<460)').mean()*100:.1f} %")
    m3.metric("Rejets Durs (Rm > 610)", f"{(df['Statut'] == 'Rejet_Dur (Rm>610)').mean()*100:.1f} %")

    st.plotly_chart(px.histogram(df, x="Regime", color="Statut", barmode="group", title="Rejets par Régime Procédé"), use_container_width=True)

    st.header("3. Extraction des Fenêtres Opératoires (Arbre CART)")
    reg_sel = st.selectbox("Choisir le régime à optimiser :", sorted(df['Regime'].unique()))
    df_sub = df[df['Regime'] == reg_sel]

    features = [c for c in ['CT', 'T_recuit', 'V_ref_galva', 'V_ref_ROT', 'CR', 'Th', 'Nb_eff', 'C_eq'] if c in df_sub.columns]
    if len(df_sub) >= 30:
        X = df_sub[features].fillna(df_sub[features].median())
        y = df_sub['Statut']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

        clf = DecisionTreeClassifier(max_depth=3, min_samples_leaf=15, random_state=42)
        clf.fit(X_train, y_train)
        st.subheader("Règles extraites (Validation croisée 75% / 25%)")
        st.code(export_text(clf, feature_names=features), language="text")

        c_x, c_y = st.columns(2)
        ax_x = c_x.selectbox("Paramètre X :", features, index=0)
        ax_y = c_y.selectbox("Paramètre Y :", features, index=min(1, len(features)-1))
        st.plotly_chart(px.scatter(df_sub, x=ax_x, y=ax_y, color="Statut", hover_data=['Rp', 'Rm'] + features), use_container_width=True)
    else:
        st.info("Effectif insuffisant dans ce régime (< 30 bobines) pour extraire des règles statistiques fiables.")
