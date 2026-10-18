from src.extractor import extract_invoice_fields


def test_extract_sample_invoice():
    text = """
    DATA NOVA CONSEIL
    FACTURE N° DN-2026-001
    Date de facture : 18/10/2026
    Total HT : 750,00 €
    TVA (20 %) : 150,00 €
    Total TTC : 900,00 €
    """

    result = extract_invoice_fields(text)

    assert result["Fournisseur"] == "DATA NOVA CONSEIL"
    assert result["N° facture"] == "DN-2026-001"
    assert result["Date"] == "2026-10-18"
    assert result["Montant HT"] == 750.0
    assert result["TVA"] == 150.0
    assert result["Montant TTC"] == 900.0
    assert result["Confiance"] == "Élevée"


def test_missing_fields_do_not_crash():
    result = extract_invoice_fields("ACME\nDocument incomplet")

    assert result["Fournisseur"] == "ACME"
    assert result["Montant TTC"] is None
    assert result["Confiance"] == "Faible"
