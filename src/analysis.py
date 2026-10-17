def safe_div(numerator, denominator):
    if numerator is None or denominator in (None, 0):
        return None
    return numerator / denominator


def average_if_available(current, previous):
    if current is None or previous is None:
        return None
    return (current + previous) / 2


def calculate_period(period):
    period["gross_margin"] = safe_div(period.get("gross_profit"), period.get("revenue"))
    period["operating_margin"] = safe_div(period.get("operating_income"), period.get("revenue"))
    period["net_margin"] = safe_div(period.get("net_income"), period.get("revenue"))
    period["debt_ratio"] = safe_div(period.get("total_liabilities"), period.get("equity"))
    period["equity_ratio"] = safe_div(period.get("equity"), period.get("total_assets"))
    period["current_ratio"] = safe_div(period.get("current_assets"), period.get("current_liabilities"))
    period["net_debt"] = (
        period["interest_debt"] - period["cash"]
        if period.get("interest_debt") is not None and period.get("cash") is not None
        else None
    )
    period["fcf"] = (
        period["cfo"] - period["capex"]
        if period.get("cfo") is not None and period.get("capex") is not None
        else None
    )
    return period


def make_signals(row):
    signals = []
    growth, margin = row.get("revenue_growth"), row.get("operating_margin")
    if growth is not None and margin is not None and growth > 0 and margin < 0:
        signals.append("매출은 성장했지만 영업이익률이 음수입니다. 비용 구조와 제품 믹스를 확인하세요.")
    if row.get("net_income") is not None and row.get("cfo") is not None:
        if row["net_income"] > 0 and row["cfo"] < 0:
            signals.append("순이익은 양수지만 영업현금흐름은 음수입니다. 운전자본과 이익의 현금 전환을 점검하세요.")
    if row.get("fcf") is not None and row["fcf"] < 0 and row.get("capex") not in (None, 0):
        signals.append("잉여현금흐름(FCF)이 음수입니다. 설비투자와 현금 조달 계획을 함께 확인하세요.")
    if row.get("roe") is not None and row.get("debt_ratio") is not None:
        signals.append("ROE는 수익성과 레버리지의 영향을 모두 받으므로 부채비율과 함께 해석하세요.")
    return signals


def calculate_annual(series):
    years = sorted(series, key=int)
    for index, year in enumerate(years):
        row = series[year]
        previous = series[years[index - 1]] if index else None
        prior_revenue = previous.get("revenue") if previous else None
        current_revenue = row.get("revenue")
        revenue_ratio = safe_div(current_revenue, prior_revenue)
        row["revenue_growth"] = revenue_ratio - 1 if revenue_ratio is not None else None

        avg_assets = average_if_available(
            row.get("total_assets"), previous.get("total_assets") if previous else None
        )
        avg_equity = average_if_available(
            row.get("equity"), previous.get("equity") if previous else None
        )
        row["gross_margin"] = safe_div(row.get("gross_profit"), row.get("revenue"))
        row["operating_margin"] = safe_div(row.get("operating_income"), row.get("revenue"))
        row["net_margin"] = safe_div(row.get("net_income"), row.get("revenue"))
        row["ebitda_margin"] = safe_div(row.get("ebitda"), row.get("revenue"))
        row["roa"] = safe_div(row.get("net_income"), avg_assets)
        row["roe"] = safe_div(row.get("net_income"), avg_equity)
        row["current_ratio"] = safe_div(row.get("current_assets"), row.get("current_liabilities"))
        row["quick_ratio"] = (
            safe_div(row["current_assets"] - row["inventory"], row.get("current_liabilities"))
            if row.get("current_assets") is not None and row.get("inventory") is not None
            else None
        )
        row["debt_ratio"] = safe_div(row.get("total_liabilities"), row.get("equity"))
        row["equity_ratio"] = safe_div(row.get("equity"), row.get("total_assets"))
        row["debt_to_assets"] = safe_div(row.get("interest_debt"), row.get("total_assets"))
        row["interest_coverage"] = safe_div(row.get("operating_income"), row.get("interest_expense"))
        row["net_debt"] = (
            row["interest_debt"] - row["cash"]
            if row.get("interest_debt") is not None and row.get("cash") is not None
            else None
        )
        row["net_debt_ebitda"] = safe_div(row.get("net_debt"), row.get("ebitda"))
        row["asset_turnover"] = safe_div(row.get("revenue"), avg_assets)
        row["cfo_to_net_income"] = safe_div(row.get("cfo"), row.get("net_income"))
        row["fcf"] = (
            row["cfo"] - row["capex"]
            if row.get("cfo") is not None and row.get("capex") is not None
            else None
        )
        row["signals"] = make_signals(row)
    return series
