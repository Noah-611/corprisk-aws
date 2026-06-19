import pandas as pd
import re
from app.dart_client import (
    find_corp_by_stock_code,
    get_financial_statement,
    convert_dart_to_financial_data,
    search_corporations,
)


COMPANY_MAPPINGS = [
    {
        "display_name": "삼성전자",
        "stock_code": "005930",
    },
    {
        "display_name": "네이버",
        "stock_code": "035420",
    },
    {
        "display_name": "카카오",
        "stock_code": "035720",
    },
    {
        "display_name": "LG에너지솔루션",
        "stock_code": "373220",
    },
    {
        "display_name": "현대자동차",
        "stock_code": "005380",
    },
    {
        "display_name": "SK하이닉스",
        "stock_code": "000660",
    },
    {
        "display_name": "기아",
        "stock_code": "000270",
    },
    {
        "display_name": "셀트리온",
        "stock_code": "068270",
    },
]


def load_financial_data():
    return pd.read_csv("data/sample_financials.csv")


def get_company_names():
    return [company["display_name"] for company in COMPANY_MAPPINGS]


def find_company_mapping(display_name: str):
    for company in COMPANY_MAPPINGS:
        if company["display_name"] == display_name:
            return company

    return None


def get_sample_financial_data(company_name: str):
    df = load_financial_data()
    company = df[df["company_name"] == company_name]

    if company.empty:
        return None

    row = company.iloc[0]

    return {
        "company_name": row["company_name"],
        "stock_code": str(row["stock_code"]).zfill(6),
        "year": int(row["year"]),
        "revenue": int(row["revenue"]),
        "operating_income": int(row["operating_income"]),
        "net_income": int(row["net_income"]),
        "total_assets": int(row["total_assets"]),
        "total_liabilities": int(row["total_liabilities"]),
        "total_equity": int(row["total_equity"]),
        "current_assets": int(row["current_assets"]),
        "current_liabilities": int(row["current_liabilities"]),
        "data_source": "샘플 CSV 데이터",
    }

def extract_stock_code(keyword: str):
    """
    '삼성전자 (005930)' 또는 '005930'에서 6자리 종목코드를 추출한다.
    """
    if not keyword:
        return None

    match = re.search(r"(\d{6})", keyword)

    if match:
        return match.group(1)

    return None


def search_companies(query: str, limit: int = 20):
    """
    화면 자동완성용 기업 검색 함수.
    """
    return search_corporations(query, limit)


def find_company_by_query(keyword: str):
    """
    기업명 또는 종목코드 입력값으로 OpenDART 기업 정보를 찾는다.
    """
    keyword = (keyword or "").strip()

    if not keyword:
        return None

    stock_code = extract_stock_code(keyword)

    if stock_code:
        return find_corp_by_stock_code(stock_code)

    candidates = search_corporations(keyword, limit=30)

    if not candidates:
        return None

    for item in candidates:
        if item["corp_name"] == keyword:
            return item

    return candidates[0]

def get_financial_data(company_name: str):
    """
    입력된 기업명 또는 종목코드를 기준으로 OpenDART에서 재무 데이터를 조회한다.

    지원 입력 예시:
    - 삼성전자
    - 005930
    - 삼성전자 (005930)
    - SK하이닉스
    """

    company = find_company_by_query(company_name)

    if company is None:
        print(f"[WARN] 기업을 찾을 수 없습니다: {company_name}")
        return None

    corp_code = company.get("corp_code")
    stock_code = company.get("stock_code")
    display_name = company.get("corp_name")

    print(f"[INFO] OpenDART 조회 대상: {display_name} ({stock_code}) / corp_code={corp_code}")

    dart_data = get_financial_statement(
        corp_code,
        "2023",
        "11011"
    )

    if dart_data is None:
        print(f"[WARN] OpenDART 재무제표 조회 실패: {display_name} ({stock_code})")
        return None

    financial_data = convert_dart_to_financial_data(
        dart_data,
        display_name,
        stock_code,
        "2023"
    )

    if financial_data is None:
        print(f"[WARN] OpenDART 재무 데이터 변환 실패: {display_name} ({stock_code})")
        return None

    financial_data["company_name"] = display_name
    financial_data["stock_code"] = stock_code
    financial_data["year"] = "2023"
    financial_data["data_source"] = "OpenDART API"

    return financial_data

def safe_ratio(numerator, denominator):
    if denominator == 0:
        return 0

    return numerator / denominator * 100


def calculate_financial_ratios(company_name: str):
    data = get_financial_data(company_name)

    if data is None:
        return None

    revenue = data["revenue"]
    operating_income = data["operating_income"]
    net_income = data["net_income"]
    total_assets = data["total_assets"]
    total_liabilities = data["total_liabilities"]
    total_equity = data["total_equity"]
    current_assets = data["current_assets"]
    current_liabilities = data["current_liabilities"]

    debt_ratio = safe_ratio(total_liabilities, total_equity)
    operating_margin = safe_ratio(operating_income, revenue)
    net_margin = safe_ratio(net_income, revenue)
    current_ratio = safe_ratio(current_assets, current_liabilities)
    equity_ratio = safe_ratio(total_equity, total_assets)

    risk_score = 0
    risk_reasons = []

    if debt_ratio > 200:
        risk_score += 30
        risk_reasons.append("부채비율이 200%를 초과하여 재무 부담이 높을 수 있습니다.")

    if current_ratio < 100:
        risk_score += 30
        risk_reasons.append("유동비율이 100% 미만으로 단기 지급능력이 부족할 수 있습니다.")

    if operating_margin < 0:
        risk_score += 25
        risk_reasons.append("영업이익률이 음수로, 본업에서 손실이 발생하고 있습니다.")

    if net_margin < 0:
        risk_score += 15
        risk_reasons.append("순이익률이 음수로, 최종 수익성이 좋지 않습니다.")

    if risk_score >= 60:
        risk_grade = "높음"
    elif risk_score >= 30:
        risk_grade = "중간"
    else:
        risk_grade = "낮음"

    if not risk_reasons:
        risk_reasons.append("주요 재무 지표가 비교적 안정적인 수준입니다.")

    return {
        "company_name": data["company_name"],
        "stock_code": str(data["stock_code"]).zfill(6),
        "year": int(data["year"]),
        "revenue": int(revenue),
        "operating_income": int(operating_income),
        "net_income": int(net_income),
        "debt_ratio": round(debt_ratio, 2),
        "operating_margin": round(operating_margin, 2),
        "net_margin": round(net_margin, 2),
        "current_ratio": round(current_ratio, 2),
        "equity_ratio": round(equity_ratio, 2),
        "risk_score": risk_score,
        "risk_grade": risk_grade,
        "risk_reasons": risk_reasons,
        "data_source": data.get("data_source", "알 수 없음"),
    }

