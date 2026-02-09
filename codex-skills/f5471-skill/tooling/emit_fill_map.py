# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--computed", required=True)
    parser.add_argument("--validation", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    computed = json.loads(Path(args.computed).read_text(encoding="utf-8-sig"))
    validation = json.loads(Path(args.validation).read_text(encoding="utf-8-sig"))

    fill_map = {
        "tax_year": computed["tax_year"],
        "status_gate": validation["status"],
        "fields": [
            {"field": "Form5471.Category4", "value": "4" in computed["filer_categories"], "page": 1},
            {"field": "Form5471.Category5", "value": "5" in computed["filer_categories"], "page": 1},
            {"field": "ScheduleF.BookNetIncomeFunctional", "value": computed["schedule_f"]["book_net_income_functional"], "page": 3},
            {"field": "ScheduleH.Line1BookNetIncome", "value": computed["schedule_h"]["line_1_book_net_income_functional"], "page": 5},
            {"field": "ScheduleH.CurrentEP", "value": computed["schedule_h"]["current_ep_functional"], "page": 5},
            {"field": "ScheduleJ.BeginAccumEP", "value": computed["schedule_j"]["begin_accum_ep_functional"], "page": 6},
            {"field": "ScheduleJ.CurrentYearEP", "value": computed["schedule_j"]["current_ep_addition_functional"], "page": 6},
            {"field": "ScheduleJ.Distributions", "value": computed["schedule_j"]["distributions_functional"], "page": 6},
            {"field": "ScheduleJ.EndAccumEP", "value": computed["schedule_j"]["ending_accum_ep_functional"], "page": 6},
            {"field": "ScheduleM.SalaryToShareholder", "value": computed["schedule_m"]["salary_to_shareholder_functional"], "page": 7},
            {"field": "ScheduleM.Dividends", "value": computed["schedule_m"]["dividends_functional"], "page": 7}
        ],
        "formatting": {
            "round_decimals": 2,
            "currency": "functional_currency_default"
        },
        "notes": computed.get("notes", []),
        "warnings": validation.get("warnings", []),
        "fails": validation.get("fails", [])
    }

    out = Path(args.out)
    out.write_text(json.dumps(fill_map, indent=2), encoding="utf-8")
    print("Wrote", out)


if __name__ == "__main__":
    main()
