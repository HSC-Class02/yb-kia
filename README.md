[![🔗 대시보드 바로가기](https://img.shields.io/badge/%F0%9F%94%97-%EB%8C%80%EC%8B%9C%EB%B3%B4%EB%93%9C%20%EB%B0%94%EB%A1%9C%EA%B0%80%EA%B8%B0-183B56?style=for-the-badge&logo=github&logoColor=white)](https://hsc-class02.github.io/yb-kia/)

# 기아(Kia) DART 재무분석 Agent

기아(주)(KIA CORPORATION, 종목코드 `000270`, DART 고유번호 `00106641`)의 OpenDART 정기보고서 재무제표를 수집하고 핵심 재무비율 및 추세를 분석해 GitHub Pages 대시보드로 배포하는 프로젝트입니다.

## Dashboard

**[🔗 기아 재무분석 대시보드 열기](https://hsc-class02.github.io/yb-kia/)**

- **Annual:** 사업보고서 기준 연간 재무제표
- **Half-year:** 반기보고서 공시 수치
- **Quarterly:** 1분기·3분기 보고서 공시 수치
- **Peer Firms:** 국내 완성차 및 자동차 부품 업계의 참고 비교기업

## Data collection

- **데이터 출처:** [OpenDART](https://opendart.fss.or.kr/)
- **대상 기업:** 기아(주) / KIA CORPORATION
- **DART 고유번호:** `00106641` · **종목코드:** `000270`
- **재무수치 수집 범위:** 2015년 이후 OpenDART 전체 재무제표 API에서 이용 가능한 데이터. 공시 목록은 가용 범위에서 보관합니다.
- **보고서:** 사업보고서(`11011`), 반기보고서(`11012`), 1분기보고서(`11013`), 3분기보고서(`11014`)
- **기준:** 연결(CFS) 우선. 연결자료가 없으면 별도(OFS)를 조회하고 데이터 행에 기준을 명시합니다.

> OpenDART 전체 재무제표 API의 사업연도 자료는 2015년 이후부터 제공됩니다. 자료가 없는 수치는 0으로 채우지 않고 결측으로 둡니다. 분기·반기 값은 공시된 기간 기준으로 표시하며, 누적 값을 임의로 단일 분기 실적으로 환산하지 않습니다.

## 주요 분석 지표

매출액, 매출총이익, 영업이익, 당기순이익, 총자산, 총부채, 자본총계, 영업·투자·재무 현금흐름, CAPEX, 잉여현금흐름(FCF), 매출성장률, 영업이익률, 순이익률, ROA, ROE, 부채비율, 유동비율, 순차입금, EBITDA 등. 계정명이나 공시 여부에 따라 일부 항목은 표시되지 않을 수 있습니다.

## Automatic update & deployment

GitHub Actions가 **매월 1일 오전 9시(한국시간)** 데이터를 수집하고 `dashboard/data.json`을 갱신합니다. 수동 실행도 지원하며 GitHub Pages workflow로 대시보드를 배포합니다.

### 최초 설정

1. **Settings → Secrets and variables → Actions → New repository secret**으로 이동합니다.
2. Secret 이름을 `DART_API_KEY`로 설정하고 OpenDART에서 발급한 API 인증키를 값으로 저장합니다. workflow는 `OPENDART_API_KEY`라는 대체 이름도 확인합니다.
3. **Settings → Pages**에서 배포 소스를 GitHub Actions로 설정합니다.
4. **Actions → Update Kia financial data → Run workflow**를 실행해 초기 데이터를 가져옵니다.

API 키를 코드, README, 대시보드 데이터에 직접 넣지 마세요.

## 국내 Peer Firms

아래 기업은 국내 완성차 및 자동차 부품 밸류체인 기준의 참고 비교군입니다. 사업 믹스, 수직계열화, 연결/별도 범위가 서로 다르므로 동종기업처럼 단순 비교하지 않도록 유의해야 합니다.

| 기업 | 주요 사업 / 비교 관점 | 구분 | 비교 활용 |
|---|---|---|---|
| [현대자동차](https://www.hyundai.com/worldwide/ko) | 글로벌 완성차, SUV·전기차·하이브리드 | 상장, 현대차그룹 계열 | 핵심 완성차 비교군 |
| [KG모빌리티](https://www.kg-mobility.com/) | SUV 및 완성차 제조 | 상장 완성차 업체 | 국내 OEM 비교군 |
| [현대모비스](https://www.mobis.com/) | 모듈·핵심부품·전동화 | 상장, 현대차그룹 계열 | 부품/전동화 밸류체인 참고 |
| [HL만도](https://www.hlmando.com/) | 제동·조향·현가 등 자동차 부품 | 상장 부품사 | 부품 공급망 및 기술투자 참고 |
| [에스엘](https://www.slworld.com/) | 자동차 램프 및 전장 부품 | 상장 부품사 | 전장·램프 부품 비교 |
| [한온시스템](https://www.hanonsystems.com/) | 자동차 열관리 시스템 | 상장 부품사 | 전기차 열관리와 부품 수익성 참고 |
| [서연이화](https://www.seoyoneh.com/) | 자동차 내·외장 부품 | 상장 부품사 | 내장재·부품 공급망 참고 |
| [SNT모티브](https://www.sntmotiv.com/) | 구동·전장·모터 부품 | 상장 부품사 | 모터·전동화 부품 참고 |

Peer firms 표는 비교기업 목록이며 각 기업의 재무데이터까지 자동 수집한다는 뜻은 아닙니다. 현대자동차와 기아는 같은 그룹에 속하므로 그룹 관계와 연결재무제표 범위를 고려해 해석하세요.

## Repository structure

| 경로 | 역할 |
|---|---|
| `src/dart_client.py` | OpenDART API 클라이언트 |
| `src/parser.py` | 재무제표 계정 정규화 및 수치 추출 |
| `src/analysis.py` | 성장률·수익성·안정성·현금흐름 지표 계산 |
| `scripts/update.py` | 기간별 데이터 수집 및 대시보드 JSON 생성 |
| `dashboard/index.html` | 재무 분석 대시보드 |
| `dashboard/data.json` | 화면에서 읽는 최신 데이터 |
| `.github/workflows/update.yml` | 월간 데이터 갱신 |
| `.github/workflows/pages.yml` | GitHub Pages 배포 |
