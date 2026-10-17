import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.dart_client import DartClient
from src.parser import extract
from src.analysis import calculate_annual, calculate_period

CORP_CODE = "00106641"
COMPANY_NAME = "기아"
START_YEAR = 2015
REPORTS = [
    ("annual", "11011", "사업보고서"),
    ("half_year", "11012", "반기보고서"),
    ("quarterly", "11013", "1분기보고서"),
    ("quarterly", "11014", "3분기보고서"),
]


def save_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def fetch_period(client, year, report_code):
    rows = client.financials(CORP_CODE, year, report_code, "CFS")
    if rows:
        return rows, "CFS"
    rows = client.financials(CORP_CODE, year, report_code, "OFS")
    if rows:
        return rows, "OFS"
    return [], None


def period_row(rows, year, category, report_code, report_name, basis):
    values = extract(rows)
    values.update({
        "year": int(year),
        "period_id": f"{year}-{report_code}",
        "period_name": f"{year}년 {report_name}",
        "category": category,
        "report_code": report_code,
        "financial_basis": basis,
        "source_account_count": len(rows),
    })
    return values


def main():
    if not (os.getenv("DART_API_KEY") or os.getenv("OPENDART_API_KEY")):
        raise RuntimeError("Repository Secret DART_API_KEY 또는 OPENDART_API_KEY를 설정해야 합니다.")

    client = DartClient()
    now = datetime.now(timezone.utc)
    current_year = now.year
    annual, half_year, quarterly = {}, [], []
    warnings = []
    count = 0

    # Archive the available filing list. Numeric financial statements are collected
    # from 2015 because that is the supported start of the full-statement API.
    try:
        filings = client.filings(CORP_CODE, start="20100101", end=now.strftime("%Y%m%d"))
        save_json(ROOT / "data" / "raw" / "filings.json", filings)
    except Exception as exc:
        filings = []
        warnings.append(f"공시 목록 조회: {exc}")

    for year in range(START_YEAR, current_year + 1):
        for category, report_code, report_name in REPORTS:
            if category == "annual" and year == current_year:
                continue
            try:
                rows, basis = fetch_period(client, year, report_code)
                if not rows:
                    continue
                row = period_row(rows, year, category, report_code, report_name, basis)
                if category == "annual":
                    annual[str(year)] = row
                elif category == "half_year":
                    half_year.append(calculate_period(row))
                else:
                    quarterly.append(calculate_period(row))
                count += 1
                print(f"[OK] {row['period_name']}: {len(rows)} accounts ({basis})")
            except Exception as exc:
                message = f"{year} {report_name}: {exc}"
                warnings.append(message)
                print(f"[WARN] {message}")

    if count == 0:
        raise RuntimeError("재무 데이터를 한 건도 받지 못했습니다. OpenDART API 키와 API 응답을 확인하세요.")

    annual = calculate_annual(annual)
    annual_periods = [annual[y] for y in sorted(annual, key=int)]
    half_year.sort(key=lambda x: (x["year"], x["report_code"]))
    quarterly.sort(key=lambda x: (x["year"], x["report_code"]))
    years = sorted(int(y) for y in annual)
    output = {
        "company": {"name": COMPANY_NAME, "english_name": "KIA CORPORATION",
                    "corp_code": CORP_CODE, "stock_code": "000270"},
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "latest_year": max(years) if years else None,
        "data_coverage": {
            "requested_start_year": START_YEAR,
            "first_annual_year": min(years) if years else None,
            "last_annual_year": max(years) if years else None,
            "annual_records": len(annual_periods),
            "half_year_records": len(half_year),
            "quarterly_records": len(quarterly),
        },
        "years": annual,
        "periods": {"annual": annual_periods, "half_year": half_year, "quarterly": quarterly},
        "filings": filings[:100],
        "methodology": {
            "basis": "연결(CFS) 우선, 불가능한 경우 별도(OFS) 대체",
            "notes": [
                "수치는 OpenDART 정기보고서의 전체 재무제표 API에서 가져왔습니다.",
                "ROA/ROE/자산회전율은 직전 사업연도 기말 잔액이 있을 때 평균 자산·자본으로 계산합니다.",
                "반기·분기 금액은 공시된 보고 기간을 유지하며 누적 값을 임의로 단일 분기 실적으로 환산하지 않습니다.",
                "자료가 없는 항목은 0이 아닌 null로 유지합니다.",
                "FCF는 영업현금흐름과 CAPEX 계정이 모두 확인된 경우에만 계산합니다.",
            ],
        },
        "collection_warnings": warnings[-50:],
    }
    save_json(ROOT / "data" / "processed" / "latest.json", output)
    save_json(ROOT / "dashboard" / "data.json", output)
    print(f"[DONE] annual={len(annual_periods)}, half_year={len(half_year)}, quarterly={len(quarterly)}")


if __name__ == "__main__":
    main()
