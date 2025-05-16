import streamlit as st
import pandas as pd
from utils import calculate_freight, load_nk_data

st.title("Frachtenrechner für LKW-Transporte")

# Eingabefelder
land = st.selectbox("Land", ["DE", "AT", "CH", "FR", "GB"])
plz = st.text_input("PLZ (2-stellig bzw. Anfangszeichen bei GB)", max_chars=4)
gewicht = st.number_input("Gewicht (kg)", min_value=1, step=1)

# Daten einlesen
zonen = pd.read_excel("dsv.xlsx", sheet_name="Zonen", dtype=str)
gwk_dsv = pd.read_excel("dsv.xlsx", sheet_name="GWK")
gwk_dachser = pd.read_excel("dachser.xlsx", sheet_name="GWK")
dsv_tarife = pd.read_excel("dsv.xlsx", sheet_name=None)
dachser_tarife = pd.read_excel("dachser.xlsx", sheet_name=None)
zustelloptionen, nebendaten = load_nk_data()

if st.button("Berechnen"):
    plz = plz.strip()
    zone = None

    # GB Spezialfall
    if land == "GB":
        if "PLZ_2" in zonen.columns and "GB" in zonen.columns:
            row = zonen[zonen["PLZ_2"].str.upper() == plz.upper()]
            if not row.empty:
                zone = row["GB"].values[0]
    else:
        if "PLZ_2" in zonen.columns and land in zonen.columns:
            row = zonen[zonen["PLZ_2"] == plz]
            if not row.empty:
                zone = row[land].values[0]

    if zone is None or pd.isna(zone):
        st.error(f"Keine passende Zone für PLZ '{plz}' in Land '{land}' gefunden.")
    else:
        tariftyp = "DSV" if land == "DE" else "Dachser"
        result = calculate_freight(
            dsv_tarife if tariftyp == "DSV" else dachser_tarife,
            gwk_dsv if tariftyp == "DSV" else gwk_dachser,
            land,
            zone,
            gewicht
        )
        if isinstance(result, str):
            st.markdown(f"**Frachtkosten:** {result}")
        else:
            st.markdown(f"**Frachtkosten:** {result['rate']}")
            st.markdown(f"**Verwendeter Tariftyp:** {result['type']}")

        # Zusatzanzeigen
        zustell = zustelloptionen[zustelloptionen["Land"] == land]
        if not zustell.empty:
            st.subheader("Zustelloptionen")
            st.dataframe(zustell[["Zustelloption", "Kosten", "Bemerkung"]])

        neben = nebendaten[nebendaten["Land"] == land]
        if not neben.empty:
            st.subheader("Sonstige Nebenkosten")
            neben["Kosten"] = neben["Kosten"].apply(
                lambda x: f"{x:.2f} €" if isinstance(x, (float, int)) else x
            )
            st.dataframe(neben[["sonstige Nebenkosten", "Kosten", "Bemerkung"]])
