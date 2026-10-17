import os
from datetime import date
import requests

BASE = "https://opendart.fss.or.kr/api"


class DartError(RuntimeError):
    """OpenDART API error with a readable message."""


class DartClient:
    def __init__(self, api_key=None, timeout=60):
        self.api_key = api_key or os.getenv("DART_API_KEY") or os.getenv("OPENDART_API_KEY")
        if not self.api_key:
            raise DartError("DART_API_KEY (또는 OPENDART_API_KEY) Secret을 설정하세요.")
        self.timeout = timeout
        self.session = requests.Session()

    def get(self, endpoint, params):
        request_params = dict(params)
        request_params["crtfc_key"] = self.api_key
        response = self.session.get(
            f"{BASE}/{endpoint}", params=request_params, timeout=self.timeout
        )
        response.raise_for_status()
        try:
            data = response.json()
        except ValueError as exc:
            raise DartError(f"{endpoint}: JSON 응답을 읽을 수 없습니다.") from exc
        status = str(data.get("status", ""))
        if status == "013":  # No data for this period.
            return data
        if status != "000":
            raise DartError(f"DART API 오류 {status}: {data.get('message', '알 수 없는 오류')}")
        return data

    def financials(self, corp_code, year, report_code, fs_div="CFS"):
        data = self.get("fnlttSinglAcntAll.json", {
            "corp_code": corp_code,
            "bsns_year": str(year),
            "reprt_code": str(report_code),
            "fs_div": fs_div,
        })
        return data.get("list", []) or []

    def filings(self, corp_code, start="20100101", end=None, page_count=100):
        end = end or date.today().strftime("%Y%m%d")
        data = self.get("list.json", {
            "corp_code": corp_code,
            "bgn_de": start,
            "end_de": end,
            "pblntf_ty": "A",
            "sort": "date",
            "sort_mth": "desc",
            "page_no": 1,
            "page_count": page_count,
        })
        return data.get("list", []) or []
