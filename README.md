# CorpRisk

## 1. 프로젝트 개요

CorpRisk는 OpenDART API를 기반으로 기업의 재무제표 데이터를 조회하고, 주요 재무비율을 계산하여 기업의 재무 리스크를 분석하는 웹서비스입니다.

사용자는 웹 화면에서 기업을 선택할 수 있으며, 서버는 해당 기업의 종목코드를 기준으로 OpenDART 기업 고유번호를 조회한 뒤 재무제표 데이터를 수집합니다. 이후 부채비율, 영업이익률, 순이익률, 유동비율, 자기자본비율을 계산하고 리스크 점수와 리스크 등급을 제공합니다.

본 프로젝트는 AWS 기반 웹서비스 과제를 위해 제작되었으며, 로컬 개발 단계에서는 SQLite를 사용하고, AWS 배포 단계에서는 RDS MySQL로 확장할 예정입니다.

---

## 2. 프로젝트 목적

이 프로젝트의 목적은 단순한 웹페이지 제작이 아니라, 금융 데이터를 수집하고 분석한 결과를 웹서비스 형태로 제공하는 것입니다.

주요 목표는 다음과 같습니다.

* OpenDART API를 활용한 기업 재무 데이터 수집
* 재무제표 기반 주요 재무비율 계산
* 규칙 기반 재무 리스크 점수 및 등급 산출
* 분석 결과 웹 대시보드 제공
* 분석 결과 DB 저장 및 최근 분석 이력 조회
* AWS 기반 고가용성 웹서비스 구조로 확장

---

## 3. 주요 기능

### 3.1 기업 재무 데이터 조회

사용자가 기업을 선택하면 해당 기업의 종목코드를 기준으로 OpenDART API에서 재무제표 데이터를 조회합니다.

### 3.2 재무비율 계산

수집한 재무 데이터를 기반으로 다음 지표를 계산합니다.

* 부채비율
* 영업이익률
* 순이익률
* 유동비율
* 자기자본비율

### 3.3 재무 리스크 분석

계산된 재무비율을 기반으로 리스크 점수와 리스크 등급을 산출합니다.

리스크 등급은 다음과 같이 구분합니다.

* 낮음
* 중간
* 높음

### 3.4 분석 결과 저장

기업 분석 결과는 DB에 저장됩니다.
동일 기업과 동일 연도의 분석 결과가 이미 존재하는 경우, 새로 중복 저장하지 않고 기존 데이터를 업데이트합니다.

### 3.5 최근 분석 이력 조회

`/history` 페이지에서 최근 분석 결과를 확인할 수 있습니다.

### 3.6 JSON API 제공

웹 화면 외에도 JSON API를 제공합니다.

* `/api/analysis?company_name=삼성전자`
* `/api/history`
* `/health`

---

## 4. 기술 스택

### Backend

* Python
* FastAPI
* Jinja2
* SQLAlchemy

### Data

* OpenDART API
* pandas

### Database

* SQLite for local development
* Amazon RDS MySQL for AWS deployment

### AWS 예정 구성

* EC2
* ALB
* Auto Scaling Group
* RDS MySQL
* S3
* CloudWatch
* Terraform

---

## 5. 로컬 실행 방법

### 5.1 프로젝트 클론

```bash
git clone <repository-url>
cd corprisk-aws
```

### 5.2 가상환경 생성 및 활성화

```bash
python3 -m venv venv
source venv/bin/activate
```

### 5.3 패키지 설치

```bash
pip install -r requirements.txt
```

### 5.4 환경변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 OpenDART API 키를 입력합니다.

```env
OPEN_DART_API_KEY=your_opendart_api_key
```

### 5.5 서버 실행

```bash
uvicorn app.main:app --reload
```

### 5.6 접속 주소

```text
http://127.0.0.1:8000
```

---

## 6. 주요 URL

| URL                               | 설명                |
| --------------------------------- | ----------------- |
| `/`                               | 기업 선택 및 분석 메인 페이지 |
| `/analyze`                        | 기업 분석 요청 처리       |
| `/history`                        | 최근 분석 이력 페이지      |
| `/api/analysis?company_name=삼성전자` | 기업 분석 JSON API    |
| `/api/history`                    | 최근 분석 이력 JSON API |
| `/health`                         | Health Check API  |

---

## 7. 프로젝트 구조

```text
corprisk-aws/
│
├── app/
│   ├── main.py
│   ├── analyzer.py
│   ├── dart_client.py
│   ├── database.py
│   ├── static/
│   │   └── style.css
│   └── templates/
│       ├── index.html
│       ├── result.html
│       └── history.html
│
├── data/
│   └── sample_financials.csv
│
├── docs/
├── terraform/
├── scripts/
│
├── requirements.txt
├── README.md
├── .gitignore
└── .env
```

---

## 8. AWS 확장 계획

로컬 개발 환경에서는 SQLite를 사용하지만, AWS 배포 단계에서는 Amazon RDS MySQL을 사용하여 분석 결과를 저장합니다.

최종 AWS 아키텍처는 다음과 같습니다.

```text
User
  ↓
Application Load Balancer
  ↓
EC2 Auto Scaling Group
  ↓
FastAPI CorpRisk Application
  ↓
Amazon RDS MySQL
  ↓
Amazon S3
  ↓
Amazon CloudWatch
```

AWS 배포 단계에서 적용할 내용은 다음과 같습니다.

* EC2에 FastAPI 애플리케이션 배포
* ALB를 통한 외부 요청 분산
* Auto Scaling Group을 통한 고가용성 구성
* RDS MySQL에 분석 결과 저장
* S3에 원본 데이터 또는 분석 리포트 저장
* CloudWatch를 통한 로그 및 지표 모니터링
* Terraform을 이용한 인프라 코드화

---

## 9. 프로젝트 특징

이 프로젝트는 단순한 정적 웹페이지가 아니라, 외부 금융 데이터 API를 활용하여 데이터를 수집하고, 분석 결과를 DB에 저장하며, 웹 화면과 JSON API를 통해 결과를 제공하는 데이터 중심 웹서비스입니다.

또한 AWS의 EC2, ALB, ASG, RDS, S3, CloudWatch를 활용할 수 있도록 설계하여 클라우드 기반 고가용성 웹서비스 구조로 확장할 수 있습니다.

---

## 10. 주의사항

* `.env` 파일에는 OpenDART API 키가 포함되므로 GitHub에 업로드하지 않습니다.
* `venv/`, `corprisk.db`, `data/corp_codes.json` 파일은 로컬 실행 과정에서 생성되는 파일이므로 GitHub에 업로드하지 않습니다.
* 본 프로젝트는 투자 추천 서비스가 아니며, 기업 재무제표 데이터를 기반으로 한 교육용 분석 웹서비스입니다.
