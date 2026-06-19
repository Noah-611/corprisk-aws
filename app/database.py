import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./corprisk.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)

    company_name = Column(String(100), nullable=False)
    stock_code = Column(String(20), nullable=False)
    year = Column(Integer, nullable=False)

    revenue = Column(Float, nullable=False)
    operating_income = Column(Float, nullable=False)
    net_income = Column(Float, nullable=False)

    debt_ratio = Column(Float, nullable=False)
    operating_margin = Column(Float, nullable=False)
    net_margin = Column(Float, nullable=False)
    current_ratio = Column(Float, nullable=False)
    equity_ratio = Column(Float, nullable=False)

    risk_score = Column(Integer, nullable=False)
    risk_grade = Column(String(20), nullable=False)
    data_source = Column(String(100), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    Base.metadata.create_all(bind=engine)


def save_analysis_result(result: dict):
    db = SessionLocal()

    try:
        existing = (
            db.query(AnalysisResult)
            .filter(
                AnalysisResult.stock_code == result["stock_code"],
                AnalysisResult.year == result["year"],
            )
            .first()
        )

        if existing:
            existing.company_name = result["company_name"]
            existing.revenue = result["revenue"]
            existing.operating_income = result["operating_income"]
            existing.net_income = result["net_income"]
            existing.debt_ratio = result["debt_ratio"]
            existing.operating_margin = result["operating_margin"]
            existing.net_margin = result["net_margin"]
            existing.current_ratio = result["current_ratio"]
            existing.equity_ratio = result["equity_ratio"]
            existing.risk_score = result["risk_score"]
            existing.risk_grade = result["risk_grade"]
            existing.data_source = result["data_source"]
            existing.created_at = datetime.utcnow()

            db.commit()
            db.refresh(existing)

            return existing

        analysis = AnalysisResult(
            company_name=result["company_name"],
            stock_code=result["stock_code"],
            year=result["year"],
            revenue=result["revenue"],
            operating_income=result["operating_income"],
            net_income=result["net_income"],
            debt_ratio=result["debt_ratio"],
            operating_margin=result["operating_margin"],
            net_margin=result["net_margin"],
            current_ratio=result["current_ratio"],
            equity_ratio=result["equity_ratio"],
            risk_score=result["risk_score"],
            risk_grade=result["risk_grade"],
            data_source=result["data_source"],
        )

        db.add(analysis)
        db.commit()
        db.refresh(analysis)

        return analysis

    finally:
        db.close()

def get_recent_analysis_results(limit: int = 10):
    db = SessionLocal()

    try:
        results = (
            db.query(AnalysisResult)
            .order_by(AnalysisResult.created_at.desc())
            .limit(limit)
            .all()
        )

        return results

    finally:
        db.close()