import re

# Restrict account matches by statement section, preventing balance-sheet,
# income-statement and cash-flow rows with similar names from being mixed.
ACCOUNT_MAP = {
    "total_assets": (["자산총계", "총자산"], ["BS"]),
    "cash": (["현금및현금성자산", "현금및현금성자산과현금성자산"], ["BS"]),
    "receivables": (["매출채권및기타채권", "매출채권"], ["BS"]),
    "inventory": (["재고자산"], ["BS"]),
    "ppe": (["유형자산"], ["BS"]),
    "current_assets": (["유동자산", "유동자산계"], ["BS"]),
    "current_liabilities": (["유동부채", "유동부채계"], ["BS"]),
    "total_liabilities": (["부채총계", "총부채"], ["BS"]),
    "equity": (["자본총계", "총자본"], ["BS"]),
    "revenue": (["매출액", "수익(매출액)", "영업수익", "매출"], ["IS", "CIS"]),
    "gross_profit": (["매출총이익"], ["IS", "CIS"]),
    "operating_income": (["영업이익", "영업이익(손실)"], ["IS", "CIS"]),
    "pretax_income": (["법인세비용차감전순이익", "법인세비용차감전순손익"], ["IS", "CIS"]),
    "net_income": (["당기순이익", "당기순이익(손실)", "분기순이익", "반기순이익"], ["IS", "CIS"]),
    "controlling_net_income": (
        ["지배기업의 소유주에게 귀속되는 당기순이익", "지배기업 소유주지분 순이익"],
        ["IS", "CIS"],
    ),
    "interest_expense": (["이자비용", "금융비용"], ["IS", "CIS"]),
    "depreciation": (["감가상각비"], ["CF", "IS", "CIS"]),
    "amortization": (["무형자산상각비", "무형자산상각"], ["CF", "IS", "CIS"]),
    "cfo": (["영업활동으로 인한 현금흐름", "영업활동현금흐름"], ["CF"]),
    "cfi": (["투자활동으로 인한 현금흐름", "투자활동현금흐름"], ["CF"]),
    "cff": (["재무활동으로 인한 현금흐름", "재무활동현금흐름"], ["CF"]),
    "capex_ppe": (["유형자산의 취득", "유형자산 취득"], ["CF"]),
    "capex_intangible": (["무형자산의 취득", "무형자산 취득"], ["CF"]),
}

DEBT_ACCOUNTS = {
    "단기차입금", "유동성장기차입금", "유동성장기부채", "유동성사채",
    "장기차입금", "사채", "리스부채", "유동성리스부채", "장기리스부채",
}


def normalize(text):
    return re.sub(r"[\s·\u00a0]", "", str(text or "")).replace("(손실)", "").replace("(수익)", "")


def to_num(value):
    if value is None:
        return None
    raw = str(value).strip().replace(",", "")
    if raw in {"", "-"}:
        return None
    try:
        return float(raw)
    except (ValueError, TypeError):
        return None


def _pick(rows, aliases, statement_types):
    wanted = {normalize(a) for a in aliases}
    candidates = [
        row for row in rows
        if row.get("sj_div") in statement_types
        and normalize(row.get("account_nm")) in wanted
    ]
    if not candidates:
        candidates = [
            row for row in rows
            if row.get("sj_div") in statement_types
            and any(a and a in normalize(row.get("account_nm")) for a in wanted)
        ]
    candidates.sort(key=lambda row: (
        normalize(row.get("account_nm")) not in wanted,
        to_num(row.get("thstrm_amount")) is None,
    ))
    for row in candidates:
        value = to_num(row.get("thstrm_amount"))
        if value is not None:
            return value
    return None


def extract(rows):
    output = {
        key: _pick(rows, aliases, sections)
        for key, (aliases, sections) in ACCOUNT_MAP.items()
    }

    # Sum only exact debt components from the balance sheet to avoid broad
    # substring matching and double-counting subtotal rows.
    debt_names = {normalize(name) for name in DEBT_ACCOUNTS}
    debt_values = [
        to_num(row.get("thstrm_amount"))
        for row in rows
        if row.get("sj_div") == "BS"
        and normalize(row.get("account_nm")) in debt_names
        and to_num(row.get("thstrm_amount")) is not None
    ]
    output["interest_debt"] = sum(debt_values) if debt_values else None

    capex = [
        abs(output[key]) for key in ("capex_ppe", "capex_intangible")
        if output.get(key) is not None
    ]
    output["capex"] = sum(capex) if capex else None

    if output.get("operating_income") is not None:
        output["ebitda"] = (
            output["operating_income"]
            + abs(output.get("depreciation") or 0)
            + abs(output.get("amortization") or 0)
        )
    else:
        output["ebitda"] = None
    return output
