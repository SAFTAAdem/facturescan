from __future__ import annotations

import io

import pandas as pd
import streamlit as st
from pypdf import PdfReader

from src.extractor import extract_invoice_fields


st.set_page_config(page_title="FactureScan", page_icon="🧾", layout="wide")

st.title("🧾 FactureScan")
st.caption("Transformez vos factures PDF en tableau exploitable, sans envoi vers une IA externe.")

with st.sidebar:
    st.header("Mode d’emploi")
    st.markdown(
        """
        1. Déposez une ou plusieurs factures.
        2. Vérifiez les champs extraits.
        3. Corrigez directement le tableau si nécessaire.
        4. Téléchargez le résultat au format CSV.
        """
    )
    st.info("Prototype de portfolio : utilisez uniquement des documents fictifs ou anonymisés.")


def read_uploaded_file(uploaded_file) -> str:
    """Return text from a PDF or UTF-8 text file."""
    if uploaded_file.type == "application/pdf" or uploaded_file.name.lower().endswith(".pdf"):
        reader = PdfReader(io.BytesIO(uploaded_file.getvalue()))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return uploaded_file.getvalue().decode("utf-8", errors="replace")


uploaded_files = st.file_uploader(
    "Déposez vos factures",
    type=["pdf", "txt"],
    accept_multiple_files=True,
    help="Les PDF doivent contenir du texte sélectionnable. L’OCR des scans sera ajouté plus tard.",
)

if not uploaded_files:
    st.markdown(
        """
        ### Démonstration

        Cette première version reconnaît notamment le numéro de facture, la date, les montants
        HT, TVA et TTC. Un fichier d’exemple est fourni dans le projet.
        """
    )
    st.stop()

rows: list[dict[str, object]] = []
failed_files: list[str] = []

for uploaded_file in uploaded_files:
    try:
        text = read_uploaded_file(uploaded_file)
        if not text.strip():
            failed_files.append(f"{uploaded_file.name} : aucun texte détecté")
            continue
        result = extract_invoice_fields(text)
        rows.append({"Fichier": uploaded_file.name, **result})
    except Exception as exc:  # Keep other invoices usable if one file is malformed.
        failed_files.append(f"{uploaded_file.name} : {exc}")

if failed_files:
    st.warning("Certains fichiers n’ont pas pu être traités :\n\n" + "\n\n".join(failed_files))

if not rows:
    st.error("Aucune facture exploitable n’a été trouvée.")
    st.stop()

st.subheader("Résultats à vérifier")
st.caption("Tous les champs sont modifiables. Une vérification humaine reste indispensable.")

edited_df = st.data_editor(
    pd.DataFrame(rows),
    use_container_width=True,
    hide_index=True,
    num_rows="fixed",
    column_config={
        "Montant HT": st.column_config.NumberColumn(format="%.2f €"),
        "TVA": st.column_config.NumberColumn(format="%.2f €"),
        "Montant TTC": st.column_config.NumberColumn(format="%.2f €"),
    },
)

csv_data = edited_df.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    "Télécharger le tableau CSV",
    data=csv_data,
    file_name="factures_extraites.csv",
    mime="text/csv",
    type="primary",
)

with st.expander("Voir le texte détecté"):
    for uploaded_file in uploaded_files:
        try:
            st.markdown(f"**{uploaded_file.name}**")
            st.code(read_uploaded_file(uploaded_file), language=None)
        except Exception:
            pass
