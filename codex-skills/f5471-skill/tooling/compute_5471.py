# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List


def nz(value: object, default: float = 0.0) -> float:
    if value is None:
        return default
    return float(value)


def infer_categories(inputs: Dict[str, object]) -> List[str]:
    cfc = inputs["cfc"]
    ownership = float(cfc.get("ownership_pct", 0))
    is_cfc = bool(cfc.get("is_cfc", True))
    categories: List[str] = []
    if ownership >= 10:
        categories.append("4")
    if is_cfc:
        categories.append("5")
    return categories


def required_schedules(categories: List[str]) -> List[str]:
    schedules = set()
    if "4" in categories:
        schedules.update(["G", "F"])
    if "5" in categories:
        schedules.update(["F", "H", "J", "M"])
    return sorted(schedules)


def optional_schedules(inputs: Dict[str, object]) -> List[str]:
    cfc = inputs["cfc"]
    compute_tested_income = bool(cfc.get("compute_tested_income", False))
    is_cfc = bool(cfc.get("is_cfc", True))
    out: List[str] = []
    if is_cfc and compute_tested_income:
        out.append("I-1")
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", required=True)
    parser.add_argument("--parsed", required=True)
    parser.add_argument("--outdir", required=True)
    args = parser.parse_args()

    inputs = json.loads(Path(args.inputs).read_text(encoding="utf-8-sig"))
    parsed_dir = Path(args.parsed)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    prior = json.loads((parsed_dir / "prior_year_extract.json").read_text(encoding="utf-8-sig"))
    current = json.loads((parsed_dir / "current_year_extract.json").read_text(encoding="utf-8-sig"))

    strict = bool(inputs.get("facts_lock", {}).get("strict", False))
    fx_pnl = float(inputs["fx_policy"]["pnl"]["rate"])
    fx_bs = float(inputs["fx_policy"]["balance_sheet"]["rate"])

    categories = infer_categories(inputs)
    req_sched = required_schedules(categories)
    opt_sched = optional_schedules(inputs)

    revenue = nz(current["pnl"].get("revenue_functional"))
    expenses = nz(current["pnl"].get("other_expenses_functional"))
    taxes = nz(current["pnl"].get("taxes_functional"))
    book_net = nz(current["pnl"].get("net_income_functional"))

    # Schedule H defaults to minimal adjustments unless explicit adjustments are provided.
    h_line_1 = book_net
    h_line_2_adj = 0.0
    h_current_ep = h_line_1 + h_line_2_adj

    carryforward_overrides = inputs.get("carryforward_overrides", {})
    begin_accum_raw = prior.get("carryforward", {}).get("begin_accum_ep_functional")
    if begin_accum_raw is None:
        begin_accum_raw = carryforward_overrides.get("begin_accum_ep_functional")
    begin_accum = nz(begin_accum_raw, 0.0)

    if strict:
        missing = []
        if inputs.get("salary_to_us_shareholder_eur") is None:
            missing.append("salary_to_us_shareholder_eur")
        if begin_accum_raw is None:
            missing.append("carryforward begin_accum_ep_functional (prior extract or override)")
        if missing:
            raise SystemExit("Strict facts lock failed. Missing: " + ", ".join(missing))

    distributions = 0.0 if not inputs["cfc"].get("has_dividends", False) else nz(inputs.get("declared_dividends_functional", 0.0))
    end_accum = begin_accum + h_current_ep - distributions

    assets = nz(current["balance_sheet"].get("assets_functional"))
    liabilities = nz(current["balance_sheet"].get("liabilities_functional"))
    equity = nz(current["balance_sheet"].get("equity_functional"))
    provisions = nz(current["balance_sheet"].get("provisions_functional"))

    salary_eur = nz(inputs.get("salary_to_us_shareholder_eur"), 0.0)

    cfc_country = str(inputs["cfc"].get("country", "")).upper()
    services_country = str(inputs["cfc"].get("services_performed_country", "")).upper()
    fbc_services_not_expected = cfc_country != "" and services_country == cfc_country
    tested_income_required = "I-1" in opt_sched

    notes = [
        "Deterministic computation from provided inputs and extracted statements.",
        "No legal conclusions inferred by pipeline.",
    ]
    if fbc_services_not_expected:
        notes.append("Fact flag: services performed in same country as CFC.")

    output = {
        "tax_year": int(inputs["tax_year"]),
        "filer_categories": categories,
        "required_schedules": req_sched,
        "optional_schedules": opt_sched,
        "schedule_f": {
            "book_net_income_functional": round(book_net, 2),
            "book_net_income_usd": round(book_net * fx_pnl, 2),
            "revenue_functional": round(revenue, 2),
            "expenses_functional": round(expenses, 2),
            "taxes_functional": round(taxes, 2),
        },
        "schedule_h": {
            "line_1_book_net_income_functional": round(h_line_1, 2),
            "line_2_adjustments_functional": round(h_line_2_adj, 2),
            "current_ep_functional": round(h_current_ep, 2),
        },
        "schedule_j": {
            "begin_accum_ep_functional": round(begin_accum, 2),
            "current_ep_addition_functional": round(h_current_ep, 2),
            "distributions_functional": round(distributions, 2),
            "ending_accum_ep_functional": round(end_accum, 2),
        },
        "schedule_g_balance_sheet": {
            "assets_functional": round(assets, 2),
            "liabilities_functional": round(liabilities + provisions, 2),
            "equity_functional": round(equity, 2),
            "assets_usd": round(assets * fx_bs, 2),
            "liabilities_usd": round((liabilities + provisions) * fx_bs, 2),
            "equity_usd": round(equity * fx_bs, 2),
        },
        "schedule_m": {
            "salary_to_shareholder_functional": round(salary_eur, 2),
            "salary_to_shareholder_usd": round(salary_eur * fx_pnl, 2),
            "dividends_functional": round(distributions, 2),
            "shareholder_loans_present": bool(inputs["cfc"].get("has_shareholder_loans", False)),
        },
        "i1_if_required": {} if not tested_income_required else {"status": "stub_only", "tested_income_functional": round(h_current_ep, 2)},
        "facts_flags": {
            "fbc_services_not_expected": fbc_services_not_expected,
            "tested_income_compute_required": tested_income_required,
        },
        "notes": notes,
    }

    out_path = outdir / "computed_outputs.json"
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print("Wrote", out_path)


if __name__ == "__main__":
    main()
