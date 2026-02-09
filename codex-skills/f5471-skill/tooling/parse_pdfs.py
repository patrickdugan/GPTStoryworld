# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from pypdf import PdfReader


RE_DE_AMOUNT = re.compile(r"-?\d{1,3}(?:\.\d{3})*(?:,\d{2})")
RE_SIMPLE_AMT = re.compile(r"(-?\d[\d,]*\.?\d{0,2})")


def de_to_float(value: str) -> float:
    return float(value.replace(".", "").replace(",", "."))


def read_pdf_lines(path: Path) -> List[str]:
    reader = PdfReader(str(path))
    text = "\n".join((p.extract_text() or "") for p in reader.pages)
    return [line.strip() for line in text.splitlines() if line.strip()]


def find_de_label_amount(lines: List[str], label: str) -> Optional[float]:
    label_lower = label.lower()
    for line in lines:
        if label_lower not in line.lower():
            continue
        amounts = RE_DE_AMOUNT.findall(line)
        if not amounts:
            continue
        try:
            return de_to_float(amounts[0])
        except Exception:
            continue
    return None


def find_plain_amount(lines: List[str], label: str) -> Optional[float]:
    label_lower = label.lower()
    for line in lines:
        if label_lower not in line.lower():
            continue
        m = RE_SIMPLE_AMT.search(line.replace("$", "").replace("USD", ""))
        if not m:
            continue
        try:
            return float(m.group(1).replace(",", ""))
        except Exception:
            continue
    return None


def extract_prior_year(lines: List[str]) -> Dict[str, object]:
    # These are best-effort fields. Missing values remain null and are resolved downstream.
    out = {
        "carryforward": {
            "begin_accum_ep_functional": None,
            "begin_total_assets_functional": None,
            "begin_total_liabilities_functional": None,
            "begin_total_equity_functional": None,
        },
        "prior_year_filer_categories": [],
        "source_notes": [],
    }
    return out


def extract_current_year(lines: List[str]) -> Dict[str, object]:
    revenue = find_de_label_amount(lines, "Umsatzerl")
    expenses = find_de_label_amount(lines, "Sonstige Aufwendungen")
    taxes = find_de_label_amount(lines, "Steuern")
    net_income = find_de_label_amount(lines, "Jahres")
    assets = find_de_label_amount(lines, "Umlaufverm")
    equity = find_de_label_amount(lines, "Eigenkapital")
    liabilities = find_de_label_amount(lines, "Verbindlichkeiten")
    provisions = find_de_label_amount(lines, "Ruckstellungen") or find_de_label_amount(lines, "Rückstellungen")
    retained_reserve = find_de_label_amount(lines, "Gewinnrucklagen") or find_de_label_amount(lines, "Gewinnrücklagen")
    balance_profit = find_de_label_amount(lines, "Bilanzgewinn")

    return {
        "pnl": {
            "revenue_functional": revenue,
            "other_expenses_functional": expenses,
            "taxes_functional": taxes,
            "net_income_functional": net_income,
        },
        "balance_sheet": {
            "assets_functional": assets,
            "equity_functional": equity,
            "liabilities_functional": liabilities,
            "provisions_functional": provisions,
            "retained_reserve_functional": retained_reserve,
            "balance_profit_functional": balance_profit,
        },
        "source_notes": [],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", required=True)
    parser.add_argument("--outdir", required=True)
    args = parser.parse_args()

    inputs_path = Path(args.inputs)
    outdir = Path(args.outdir)
    parsed_dir = outdir / "parsed"
    parsed_dir.mkdir(parents=True, exist_ok=True)

    inputs = json.loads(inputs_path.read_text(encoding="utf-8-sig"))
    docs = inputs.get("documents", {})
    prior_pdf = Path(docs.get("prior_year_5471_pdf", ""))
    current_pdf = Path(docs.get("current_year_financials_pdf", ""))

    if not prior_pdf.exists():
        raise SystemExit(f"Missing prior-year PDF: {prior_pdf}")
    if not current_pdf.exists():
        raise SystemExit(f"Missing current-year PDF: {current_pdf}")

    prior_lines = read_pdf_lines(prior_pdf)
    current_lines = read_pdf_lines(current_pdf)

    prior = extract_prior_year(prior_lines)
    current = extract_current_year(current_lines)

    (parsed_dir / "prior_year_extract.json").write_text(json.dumps(prior, indent=2), encoding="utf-8")
    (parsed_dir / "current_year_extract.json").write_text(json.dumps(current, indent=2), encoding="utf-8")
    print("Wrote", parsed_dir / "prior_year_extract.json")
    print("Wrote", parsed_dir / "current_year_extract.json")


if __name__ == "__main__":
    main()
