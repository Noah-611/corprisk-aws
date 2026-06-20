from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from app.analyzer import calculate_financial_ratios, search_companies
from app.database import (
    init_db,
    save_analysis_result,
    get_recent_analysis_results,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="CorpRisk", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

def format_eok(value):
    if value is None:
        return "-"

    try:
        value = float(value)
    except (TypeError, ValueError):
        return "-"

    eok = value / 100_000_000

    if abs(eok) >= 1000:
        return f"{eok:,.0f}억 원"
    else:
        return f"{eok:,.1f}억 원"


templates.env.filters["eok"] = format_eok


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {},
    )


@app.post("/analyze", response_class=HTMLResponse)
def analyze(request: Request, company_name: str = Form(...)):
    result = calculate_financial_ratios(company_name)

    if result is not None:
        save_analysis_result(result)

    return templates.TemplateResponse(
        request,
        "result.html",
        {
            "result": result,
        },
    )


@app.get("/history", response_class=HTMLResponse)
def history(request: Request):
    results = get_recent_analysis_results(limit=10)

    return templates.TemplateResponse(
        request,
        "history.html",
        {
            "results": results,
        },
    )


@app.get("/api/companies")
def companies_api(q: str = "", limit: int = 20):
    companies = search_companies(q, limit)

    return {
        "success": True,
        "count": len(companies),
        "data": companies,
    }


@app.get("/api/analysis")
def analysis_api(company_name: str):
    result = calculate_financial_ratios(company_name)

    if result is not None:
        save_analysis_result(result)

    return {
        "success": result is not None,
        "data": result,
    }


@app.get("/api/history")
def history_api():
    results = get_recent_analysis_results(limit=10)

    data = []

    for item in results:
        data.append({
            "id": item.id,
            "company_name": item.company_name,
            "stock_code": item.stock_code,
            "year": item.year,
            "risk_grade": item.risk_grade,
            "risk_score": item.risk_score,
            "data_source": item.data_source,
            "created_at": item.created_at.isoformat(),
        })

    return {
        "success": True,
        "count": len(data),
        "data": data,
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}