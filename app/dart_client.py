import os
import io
import json
import zipfile
import xml.etree.ElementTree as ET

import requests
from dotenv import load_dotenv


load_dotenv()

OPEN_DART_API_KEY = os.getenv("OPEN_DART_API_KEY")
BASE_URL = "https://opendart.fss.or.kr/api"
CORP_CODE_CACHE_PATH = "data/corp_codes.json"


def parse_amount(value):
    """
    OpenDART 금액 문자열을 숫자로 변환합니다.
    예: '258,935,494,000,000' -> 258935494000000
    """
    if value is None:
        return 0

    value = str(value).replace(",", "").strip()

    if value == "" or value == "-":
        return 0

    return int(value)


def download_corp_code_list():
    """
    OpenDART에서 전체 기업 고유번호 목록을 다운로드합니다.
    응답은 ZIP 파일이며, 내부 XML 파일을 파싱합니다.
    """
    url = f"{BASE_URL}/corpCode.xml"

    params = {
        "crtfc_key": OPEN_DART_API_KEY,
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()

    zip_file = zipfile.ZipFile(io.BytesIO(response.content))
    xml_filename = zip_file.namelist()[0]

    with zip_file.open(xml_filename) as xml_file:
        tree = ET.parse(xml_file)
        root = tree.getroot()

    corp_list = []

    for item in root.findall("list"):
        corp_code = item.findtext("corp_code")
        corp_name = item.findtext("corp_name")
        stock_code = item.findtext("stock_code")
        modify_date = item.findtext("modify_date")

        corp_list.append({
            "corp_code": corp_code,
            "corp_name": corp_name,
            "stock_code": stock_code,
            "modify_date": modify_date,
        })

    return corp_list


def save_corp_code_cache(corp_list):
    """
    다운로드한 기업 고유번호 목록을 JSON 파일로 저장합니다.
    """
    os.makedirs("data", exist_ok=True)

    with open(CORP_CODE_CACHE_PATH, "w", encoding="utf-8") as file:
        json.dump(corp_list, file, ensure_ascii=False, indent=2)


def load_corp_code_cache():
    """
    저장된 기업 고유번호 캐시 파일을 읽어옵니다.
    """
    if not os.path.exists(CORP_CODE_CACHE_PATH):
        return None

    with open(CORP_CODE_CACHE_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def get_corp_code_list():
    """
    기업 고유번호 목록을 가져옵니다.
    캐시 파일이 있으면 캐시를 사용하고, 없으면 OpenDART에서 다운로드합니다.
    """
    cached_data = load_corp_code_cache()

    if cached_data is not None:
        return cached_data

    corp_list = download_corp_code_list()
    save_corp_code_cache(corp_list)

    return corp_list


def find_corp_by_name(company_name: str):
    """
    기업명으로 OpenDART 고유번호를 찾습니다.
    """
    corp_list = get_corp_code_list()

    for corp in corp_list:
        if corp["corp_name"] == company_name:
            return corp

    return None


def find_corp_by_stock_code(stock_code: str):
    """
    종목코드로 OpenDART 고유번호를 찾습니다.
    기업명은 OpenDART 등록명과 다를 수 있으므로,
    상장사는 종목코드로 찾는 방식이 더 안정적입니다.
    """
    corp_list = get_corp_code_list()

    for corp in corp_list:
        if corp["stock_code"] == stock_code:
            return corp

    return None


def get_company_profile(corp_code: str):
    url = f"{BASE_URL}/company.json"

    params = {
        "crtfc_key": OPEN_DART_API_KEY,
        "corp_code": corp_code,
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    return response.json()


def get_financial_statement(corp_code: str, year: str = "2023", reprt_code: str = "11011"):
    url = f"{BASE_URL}/fnlttSinglAcntAll.json"

    params = {
        "crtfc_key": OPEN_DART_API_KEY,
        "corp_code": corp_code,
        "bsns_year": year,
        "reprt_code": reprt_code,
        "fs_div": "CFS",
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    return response.json()


def find_account_amount(items, account_names):
    """
    OpenDART 재무제표 항목 중 원하는 계정명을 찾아 금액을 반환합니다.
    """
    for name in account_names:
        for item in items:
            account_nm = item.get("account_nm", "")

            if account_nm == name:
                return parse_amount(item.get("thstrm_amount"))

    return 0


def convert_dart_to_financial_data(corp_code: str, year: str = "2023"):
    """
    OpenDART API 응답을 CorpRisk 분석용 데이터 구조로 변환합니다.
    """
    profile = get_company_profile(corp_code)
    statement = get_financial_statement(corp_code, year)

    if statement.get("status") != "000":
        raise ValueError(f"OpenDART API Error: {statement.get('message')}")

    items = statement.get("list", [])

    financial_data = {
        "company_name": profile.get("corp_name"),
        "stock_code": profile.get("stock_code"),
        "year": int(year),

        "revenue": find_account_amount(items, ["매출액", "수익(매출액)", "영업수익"]),
        "operating_income": find_account_amount(items, ["영업이익", "영업이익(손실)"]),
        "net_income": find_account_amount(items, ["당기순이익", "당기순이익(손실)"]),

        "total_assets": find_account_amount(items, ["자산총계"]),
        "total_liabilities": find_account_amount(items, ["부채총계"]),
        "total_equity": find_account_amount(items, ["자본총계"]),

        "current_assets": find_account_amount(items, ["유동자산"]),
        "current_liabilities": find_account_amount(items, ["유동부채"]),
    }

    return financial_data


if __name__ == "__main__":
    stock_code = "035720"

    corp = find_corp_by_stock_code(stock_code)

    print("기업 고유번호 조회 결과")
    print("----------------------")

    if corp is None:
        print("기업을 찾을 수 없습니다.")
    else:
        print("기업명:", corp["corp_name"])
        print("종목코드:", corp["stock_code"])
        print("DART 고유번호:", corp["corp_code"])

        data = convert_dart_to_financial_data(corp["corp_code"], "2023")

        print()
        print("재무 데이터 변환 결과")
        print("----------------------")
        for key, value in data.items():
            print(key, ":", value)