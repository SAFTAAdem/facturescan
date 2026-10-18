from __future__ import annotations

import re
from datetime import datetime


MONEY_PATTERN = r"([0-9][0-9 .\u202f]*(?:[,.][0-9]{1,2})?)\s*(?:€|EUR)?"


def _clean_money(value: str | None) -> float | None:
    if not value:
        return None
    normalized = re.sub(r"[ .\u202f]", "", value).replace(",", ".")
    try:
        return round(float(normalized), 2)
    except ValueError:
        return None


def _first_match(patterns: list[str], text: str, flags: int = re.IGNORECASE) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text, flags)
        if match:
            return match.group(1).strip()
    return None


def _normalize_date(value: str | None) -> str | None:
    if not value:
        return None
    for date_format in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d.%m.%Y"):
        try:
            return datetime.strptime(value, date_format).date().isoformat()
        except ValueError:
            continue
    return value


def _guess_supplier(text: str) -> str | None:
    ignored = ("facture", "invoice", "date", "client", "n°", "numero", "numéro")
    for raw_line in text.splitlines()[:12]:
        line = " ".join(raw_line.split()).strip(" -:|")
        if len(line) >= 3 and not any(word in line.lower() for word in ignored):
            return line[:100]
    return None


def extract_invoice_fields(text: str) -> dict[str, object]:
    """Extract common French invoice fields using transparent regex rules."""
    compact_text = text.replace("\u00a0", " ")

    invoice_number = _first_match(
        [
            r"(?:facture|invoice)\s*(?:n[°oº]?|num[eé]ro|#)?\s*[:\-]?\s*([A-Z0-9][A-Z0-9_./-]+)",
            r"(?:n[°oº]|num[eé]ro)\s*(?:de\s+facture)?\s*[:\-]?\s*([A-Z0-9][A-Z0-9_./-]+)",
        ],
        compact_text,
    )
    invoice_date = _first_match(
        [
            r"(?:date\s+(?:de\s+)?facture|date|émise?\s+le)\s*[:\-]?\s*(\d{1,2}[./-]\d{1,2}[./-]\d{4})",
            r"\b(\d{4}-\d{2}-\d{2})\b",
        ],
        compact_text,
    )
    amount_excl_tax = _clean_money(
        _first_match(
            [
                rf"(?:total\s+)?(?:montant\s+)?H\.?\s*T\.?\s*[:\-]?\s*{MONEY_PATTERN}",
                rf"total\s+hors\s+taxe[s]?\s*[:\-]?\s*{MONEY_PATTERN}",
            ],
            compact_text,
        )
    )
    vat_amount = _clean_money(
        _first_match(
            [
                rf"(?:montant\s+)?T\.?\s*V\.?\s*A\.?(?:\s*\([^)]+\))?\s*[:\-]?\s*{MONEY_PATTERN}",
                rf"taxe\s+sur\s+la\s+valeur\s+ajout[eé]e\s*[:\-]?\s*{MONEY_PATTERN}",
            ],
            compact_text,
        )
    )
    amount_incl_tax = _clean_money(
        _first_match(
            [
                rf"(?:net\s+[àa]\s+payer|total\s+T\.?\s*T\.?\s*C\.?)\s*[:\-]?\s*{MONEY_PATTERN}",
                rf"total\s+toutes\s+taxes\s+comprises\s*[:\-]?\s*{MONEY_PATTERN}",
            ],
            compact_text,
        )
    )

    detected = sum(
        value is not None
        for value in (invoice_number, invoice_date, amount_excl_tax, vat_amount, amount_incl_tax)
    )
    confidence = "Élevée" if detected >= 4 else "Moyenne" if detected >= 2 else "Faible"

    return {
        "Fournisseur": _guess_supplier(compact_text),
        "N° facture": invoice_number,
        "Date": _normalize_date(invoice_date),
        "Montant HT": amount_excl_tax,
        "TVA": vat_amount,
        "Montant TTC": amount_incl_tax,
        "Confiance": confidence,
    }
