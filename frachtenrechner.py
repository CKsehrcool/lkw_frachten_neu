import streamlit as st
import pandas as pd
from utils import calculate_freight,load_nk_data

# Daten laden
dsv_data = pd.read_excel("dsv.xlsx", sheet_name=None)
dachser_data = pd.read_excel("dachser.xlsx", sheet_name=None)
gwk_dsv = pd.read_excel("dsv.xlsx", sheet_name="GWK")
gwk_dachser = pd.read_excel("dachser.xlsx", sheet_name="GWK")
zonen = pd.read_excel("dsv.xlsx", sheet_name="Zonen")
zustelloptionen, nebendaten = load_nk_data()

st.title("Frachtenrechner für LKW-Transporte")

# Auswahlfelder
länder = sorted(set(dachser_data.keys()).union({"DE"}))
land = st.selectbox("Land", länder)
plz = st.text_input("PLZ (2-stellig) / GB Buchstaben (1 oder e -stellig)", max_chars=2)
gewicht = st.number_input("Gewicht (kg)", min_value=1, step=1)

if st.button("Berechnen"):
    tariftyp = "Dachser" if land != "DE" else "DSV"

    # England-Spezialfall: Mapping gegen zweite Spalte
    zone = None
    if land == "GB":
        if "PLZ_2" in zonen.columns and "GB" in zonen.columns:
            plz_upper = plz.upper().strip()
            row = zonen[zonen["PLZ_2"].astype(str).str.upper() == plz_upper]
            if not row.empty:
                zone = row["GB"].values[0]
    else:
        if "PLZ_2" in zonen.columns and land in zonen.columns:
            row = zonen[zonen["PLZ_2"].astype(str) == plz]
            if not row.empty:
                zone = row[land].values[0]

    if not zone:
        st.markdown(f"**Frachtkosten:** Keine Zone gefunden für PLZ {plz}")
        st.markdown(f"**Verwendeter Tariftyp:** {tariftyp}")
    else:
        # Tarife und Gewichtsstufen ermitteln
        if tariftyp == "DSV":
            result = calculate_freight(dsv_data, gwk_dsv, land, zone, gewicht)
        else:
            result = calculate_freight(dachser_data, gwk_dachser, land, zone, gewicht)

        if isinstance(result, str):
            st.markdown(f"**Frachtkosten:** {result}")
        else:
            st.markdown(f"**Frachtkosten:** {result['rate']} €")
        st.markdown(f"**Verwendeter Tariftyp:** {result['type']} ({tariftyp})")

        # Zustelloptionen
        if not zustelloptionen.empty:
            zustell = zustelloptionen[zustelloptionen["Land"] == land]
            if not zustell.empty:
                st.subheader("Zustelloptionen")
                st.dataframe(zustell[["Zustelloption", "Kosten", "Bemerkung"]])

        # Sonstige Nebenkosten
        if not nebendaten.empty:
            st.subheader("Sonstige Nebenkosten")
            anzeige = nebendaten.copy()
            if "Kosten" in anzeige.columns:
                anzeige["Kosten"] = anzeige["Kosten"].apply(
                    lambda x: f"{x:.2f} €" if isinstance(x, (int, float)) else x
                )
            st.dataframe(anzeige[["sonstige Nebenkosten", "Kosten", "Bemerkung"]])
