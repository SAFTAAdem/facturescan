# FactureScan

FactureScan est un prototype Python et Streamlit qui transforme des factures PDF ou TXT en données structurées, vérifiables et exportables.

## Fonctionnalités

- import de plusieurs factures PDF ou TXT ;
- extraction du fournisseur, du numéro, de la date, du montant HT, de la TVA et du TTC ;
- indicateur de confiance pour faciliter la vérification ;
- correction manuelle des résultats dans l'interface ;
- export CSV compatible avec Excel ;
- traitement local sans transmission des documents à une API d'IA externe.

> La version actuelle traite les PDF contenant du texte sélectionnable. L'OCR des documents scannés pourra être ajouté dans une version ultérieure.

## Installation

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

Utilisez `sample_invoice.txt` pour tester rapidement l'application.

## Tests

```powershell
python -m pytest
```

## Technologies

Python, Streamlit, Pandas, pypdf, expressions régulières et Pytest.

## Confidentialité

N'utilisez pas de véritables documents clients dans une démonstration publique.
