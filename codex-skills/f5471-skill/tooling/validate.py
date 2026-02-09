# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List


def close_enough(a: float, b: float, tol: float = 0.01) -> bool:
    return abs(a - b) <= tol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", required=True)
    parser.add_argument("--computed", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    inputs = json.loads(Path(args.inputs).read_text(encoding="utf-8-sig"))
    computed = json.loads(Path(args.computed).read_text(encoding="utf-8-sig"))

    fails: List[str] = []
    warnings: List[str] = []

    sf_book = float(computed["schedule_f"]["book_net_income_functional"])
    sh_line1 = float(computed["schedule_h"]["line_1_book_net_income_functional"])
    if not close_enough(sf_book, sh_line1):
        fails.append("Tie-out fail: Schedule F book net income != Schedule H line 1.")

    sh_current = float(computed["schedule_h"]["current_ep_functional"])
    sj_add = float(computed["schedule_j"]["current_ep_addition_functional"])
    if not close_enough(sh_current, sj_add):
        fails.append("Tie-out fail: Schedule H current E&P != Schedule J current-year addition.")

    sj_begin = float(computed["schedule_j"]["begin_accum_ep_functional"])
    sj_dist = float(computed["schedule_j"]["distributions_functional"])
    sj_end = float(computed["schedule_j"]["ending_accum_ep_functional"])
    if not close_enough(sj_begin + sj_add - sj_dist, sj_end):
        fails.append("Tie-out fail: Schedule J rollforward arithmetic mismatch.")

    assets = float(computed["schedule_g_balance_sheet"]["assets_functional"])
    liabilities = float(computed["schedule_g_balance_sheet"]["liabilities_functional"])
    equity = float(computed["schedule_g_balance_sheet"]["equity_functional"])
    drift = assets - (liabilities + equity)
    if abs(drift) > 0.5:
        fails.append(f"Tie-out fail: Balance sheet out of balance by {drift:.2f} (functional currency).")
    elif abs(drift) > 0.01:
        warnings.append(f"Balance sheet minor drift {drift:.2f}; check statement rounding/layout.")

    tested_income_required = bool(computed["facts_flags"]["tested_income_compute_required"])
    if tested_income_required and computed.get("i1_if_required", {}).get("status") == "stub_only":
        warnings.append("Schedule I-1 flagged as required but currently emitted as stub only.")

    if bool(inputs["cfc"]["has_dividends"]) is False:
        if float(computed["schedule_m"]["dividends_functional"]) != 0.0:
            fails.append("Tie-out fail: inputs say no dividends but Schedule M dividends is non-zero.")

    status = "pass" if not fails else "fail"
    result = {"status": status, "warnings": warnings, "fails": fails}
    out = Path(args.out)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("Wrote", out)
    if fails:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
