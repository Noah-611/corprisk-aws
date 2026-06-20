# CorpRisk

OpenDART 재무제표 데이터를 활용해 기업의 주요 재무비율과 리스크 등급을 확인할 수 있는 AWS 기반 웹서비스입니다.

사용자는 웹 화면에서 기업명을 검색하고 분석 연도를 선택할 수 있습니다. 서버는 OpenDART API에서 해당 기업의 재무제표 데이터를 조회한 뒤, 부채비율, 유동비율, 영업이익률, 순이익률, 자기자본비율 등을 계산합니다. 계산 결과는 웹 화면에 표시되며, 분석 이력은 데이터베이스에 저장됩니다.

본 프로젝트는 클라우드 컴퓨팅 수업에서 다룬 EC2, ALB, Auto Scaling Group, RDS, S3, Terraform을 종합적으로 적용하기 위해 진행했습니다.

---

## Repository

```text
https://github.com/Noah-611/corprisk-aws
```

## AWS 배포 주소

```text
http://corprisk-alb-746720054.us-east-1.elb.amazonaws.com
```

위 주소는 AWS Application Load Balancer의 DNS 주소입니다.
AWS Academy/Learner Lab 환경에서 생성된 리소스이므로, 실습 환경 종료 또는 리소스 재생성 시 접속이 제한되거나 주소가 변경될 수 있습니다.

---

## 1. 프로젝트 개요

CorpRisk는 기업의 재무 데이터를 조회하고, 재무 안정성과 수익성을 간단히 판단할 수 있도록 만든 재무 리스크 분석 서비스입니다.

기존에는 기업 재무제표를 직접 찾아보고 비율을 계산해야 했지만, 본 서비스에서는 기업명을 입력하면 OpenDART API를 통해 재무제표 데이터를 가져오고, 주요 지표를 자동 계산하여 한 화면에서 확인할 수 있도록 구성했습니다.

분석 결과는 단순 조회에 그치지 않고 RDS MySQL에 저장되며, `/history` 페이지에서 최근 분석 이력을 확인할 수 있습니다. 또한 EC2 한 대에만 배포하는 구조가 아니라, ALB와 Auto Scaling Group을 사용해 두 개의 EC2 인스턴스가 같은 애플리케이션을 제공하도록 구성했습니다.

---

## 2. 주요 기능

### 2.1 기업 검색 및 자동완성

사용자가 기업명을 입력하면 OpenDART 기업 코드 목록을 기반으로 관련 기업을 검색합니다.

예를 들어 `삼성`을 입력하면 삼성전자, 삼성전기, 삼성SDS 등 상장 기업 목록이 자동완성 형태로 표시됩니다.

### 2.2 OpenDART 재무 데이터 조회

선택한 기업의 종목코드를 기준으로 OpenDART 기업 고유번호를 찾고, 해당 기업의 사업보고서 재무제표 데이터를 조회합니다.

조회 대상 연도는 사용자가 선택할 수 있으며, 최근 연도부터 과거 연도까지 분석할 수 있도록 구성했습니다.

### 2.3 재무비율 계산

조회한 재무 데이터를 기반으로 다음 지표를 계산합니다.

| 지표     | 설명             |
| ------ | -------------- |
| 부채비율   | 자기자본 대비 부채 규모  |
| 유동비율   | 단기 부채 상환 여력    |
| 영업이익률  | 매출 대비 영업이익 비율  |
| 순이익률   | 매출 대비 당기순이익 비율 |
| 자기자본비율 | 총자산 중 자기자본 비중  |

### 2.4 리스크 점수 및 등급 산출

계산된 재무비율을 바탕으로 규칙 기반 리스크 점수를 산출합니다.
최종 결과는 낮음, 중간, 높음 단계로 구분하여 표시합니다.

본 프로젝트의 리스크 등급은 투자 판단을 위한 지표가 아니라, 재무 안정성을 학습 목적으로 단순화해 표현한 결과입니다.

### 2.5 분석 연도 선택

결과 화면에서 분석 연도를 드롭다운 방식으로 선택할 수 있습니다.
연도를 변경하면 해당 연도의 재무제표를 다시 조회하고, 선택 연도 기준으로 재무비율과 리스크 등급을 다시 계산합니다.

### 2.6 과거 재무 추이 그래프

최근 여러 연도의 재무 데이터를 조회하여 주요 지표의 흐름을 그래프로 확인할 수 있습니다.

그래프에서 확인 가능한 항목은 다음과 같습니다.

* 매출액
* 영업이익
* 당기순이익
* 부채비율
* 유동비율
* 자기자본비율
* 영업이익률
* 순이익률
* 매출증가율
* 영업이익증가율
* 순이익증가율

### 2.7 분석 결과 저장 및 이력 조회

분석 결과는 DB에 저장됩니다.
AWS 배포 환경에서는 RDS MySQL을 사용하며, 여러 EC2 인스턴스가 같은 데이터베이스를 공유합니다.

`/history` 페이지에서 최근 분석 결과를 확인할 수 있습니다.

### 2.8 API 제공

웹 화면뿐 아니라 JSON API도 함께 제공합니다.

| URL                                 | 설명                   |
| ----------------------------------- | -------------------- |
| `/`                                 | 메인 페이지               |
| `/analyze`                          | 기업 분석 요청 처리          |
| `/history`                          | 분석 이력 페이지            |
| `/api/companies?q=삼성`               | 기업 검색 API            |
| `/api/analysis?company_name=005930` | 기업 분석 JSON API       |
| `/api/history`                      | 최근 분석 이력 JSON API    |
| `/health`                           | ALB Health Check API |

---

## 3. 시스템 아키텍처

```text
User
  ↓
Application Load Balancer
  ↓
EC2 Auto Scaling Group
  ↓
FastAPI Application
  ↓
Amazon RDS MySQL
```

보조 구성은 다음과 같습니다.

```text
Terraform → AWS 인프라 생성 및 관리
S3        → 리포트/산출물 저장용 버킷 구성
OpenDART  → 기업 재무제표 데이터 수집
```

본 프로젝트는 ALB 뒤에 EC2 인스턴스 2대를 배치했습니다.
두 인스턴스는 동일한 FastAPI 애플리케이션을 실행하며, 분석 결과는 공통 RDS MySQL에 저장됩니다.

---

## 4. 사용 기술

### Backend

* Python
* FastAPI
* Jinja2
* SQLAlchemy

### Data

* OpenDART API
* pandas

### Database

* SQLite: 로컬 개발 환경
* Amazon RDS MySQL: AWS 배포 환경

### Frontend

* HTML
* CSS
* JavaScript
* Chart.js

### AWS

* EC2
* Application Load Balancer
* Auto Scaling Group
* RDS MySQL
* S3
* Security Group
* Launch Template
* Target Group

### Infrastructure as Code

* Terraform

---

## 5. AWS 구성

### 5.1 EC2

FastAPI 애플리케이션을 실행하는 서버입니다.
Launch Template의 user data를 통해 인스턴스 생성 시 GitHub 저장소를 clone하고, 필요한 패키지를 설치한 뒤 systemd 서비스로 애플리케이션을 실행하도록 구성했습니다.

### 5.2 ALB

사용자의 요청을 EC2 인스턴스에 분산합니다.
Target Group의 health check 경로는 `/health`로 설정했습니다.

### 5.3 Auto Scaling Group

두 개의 EC2 인스턴스를 유지하도록 구성했습니다.
인스턴스 하나가 교체되거나 실패하더라도 다른 인스턴스가 서비스를 계속 제공할 수 있도록 구성했습니다.

### 5.4 RDS MySQL

분석 결과 이력을 저장하는 데이터베이스입니다.
로컬에서는 SQLite를 사용하지만, AWS 배포 환경에서는 RDS MySQL 연결 문자열을 환경변수로 주입하여 사용합니다.

### 5.5 S3

프로젝트 산출물 또는 리포트 저장을 위한 버킷을 구성했습니다.
향후 분석 결과를 CSV 또는 PDF 리포트로 생성할 경우 S3에 저장하는 방식으로 확장할 수 있습니다.

### 5.6 Terraform

VPC 기본 리소스를 조회하고, Security Group, RDS, S3, Launch Template, Auto Scaling Group, ALB, Target Group 등을 코드로 관리했습니다.

---

## 6. 실행 방법

### 6.1 프로젝트 클론

```bash
git clone https://github.com/Noah-611/corprisk-aws.git
cd corprisk-aws
```

### 6.2 가상환경 생성 및 활성화

```bash
python3 -m venv venv
source venv/bin/activate
```

### 6.3 패키지 설치

```bash
pip install -r requirements.txt
```

### 6.4 환경변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 OpenDART API 키를 입력합니다.

```env
OPEN_DART_API_KEY=your_opendart_api_key
```

RDS를 사용하는 경우에는 DB 연결 정보도 함께 설정합니다.

```env
DATABASE_URL=mysql+pymysql://user:password@host:3306/dbname
```

### 6.5 로컬 서버 실행

```bash
uvicorn app.main:app --reload
```

### 6.6 로컬 접속 주소

```text
http://127.0.0.1:8000
```

### 6.7 AWS 배포 접속 주소

```text
http://corprisk-alb-746720054.us-east-1.elb.amazonaws.com
```

AWS 배포 주소는 ALB DNS 주소이며, 실습 환경 종료 또는 리소스 재생성 시 변경될 수 있습니다.

---

## 7. Terraform 실행 방법

Terraform 설정 파일은 `terraform/` 디렉터리에 있습니다.

```bash
cd terraform
terraform init
terraform validate
terraform plan
terraform apply
```

배포에 필요한 값은 `terraform.tfvars`에 설정합니다.
단, `terraform.tfvars`에는 민감 정보가 포함될 수 있으므로 GitHub에 업로드하지 않습니다.

---

## 8. 프로젝트 구조

```text
corprisk-aws/
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
├── docs/
│   ├── report.md
│   └── images/
│
├── terraform/
│   ├── alb.tf
│   ├── asg.tf
│   ├── data.tf
│   ├── ec2.tf
│   ├── outputs.tf
│   ├── provider.tf
│   ├── rds.tf
│   ├── s3.tf
│   ├── security_group.tf
│   └── variables.tf
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 9. 실행 결과

### 9.1 메인 화면

![메인 화면](docs/images/01-main-page.png)

### 9.2 기업 검색 자동완성

![기업 검색 자동완성](docs/images/02-search-autocomplete.png)

### 9.3 분석 결과 화면

![분석 결과](docs/images/03-analysis-result.png)

### 9.4 분석 연도 선택

![분석 연도 선택](docs/images/04-year-selector.png)

### 9.5 과거 재무 추이 그래프

![과거 재무 추이 그래프](docs/images/05-history-chart.png)

### 9.6 분석 이력 페이지

![분석 이력](docs/images/06-history-page.png)

---

## 10. AWS 배포 검증

### 10.1 Target Group Health Check

ALB Target Group에서 EC2 인스턴스 2대가 모두 healthy 상태임을 확인했습니다.

![Target Group Healthy](docs/images/07-target-group-healthy.png)

### 10.2 Auto Scaling Group

Auto Scaling Group에서 EC2 인스턴스 2대가 InService 상태로 유지되는 것을 확인했습니다.

![Auto Scaling Group](docs/images/08-asg-instances.png)

### 10.3 RDS

RDS MySQL 인스턴스를 생성하고, AWS 배포 환경에서 분석 결과 이력 저장용 데이터베이스로 사용했습니다.

![RDS](docs/images/09-rds.png)

### 10.4 Benchmark

ApacheBench(ab)를 사용하여 ALB의 `/health` 엔드포인트를 대상으로 간단한 요청 테스트를 수행했습니다.

```bash
ab -n 100 -c 10 http://corprisk-alb-746720054.us-east-1.elb.amazonaws.com/health
```

해당 테스트를 통해 ALB를 통한 요청 처리가 정상적으로 완료되는 것을 확인했습니다.

![Benchmark](docs/images/10-benchmark.png)

---

## 11. 구현 과정에서 해결한 문제

### 11.1 OpenDART 기업 코드 조회

OpenDART 재무제표 API를 호출하려면 일반 기업명이 아니라 기업 고유번호가 필요했습니다.
이를 해결하기 위해 OpenDART 기업 코드 목록을 내려받아 종목코드와 기업 고유번호를 매핑했습니다.

### 11.2 EC2 배포 자동화

EC2 인스턴스를 수동으로 설정하지 않기 위해 Launch Template의 user data에서 애플리케이션 clone, 패키지 설치, 환경변수 생성, systemd 서비스 등록을 자동화했습니다.

### 11.3 GitHub URL 오타 문제

초기 배포 과정에서 user data에 전달되는 GitHub 저장소 URL에 오타가 있어 EC2가 애플리케이션 코드를 정상적으로 clone하지 못했습니다.
EC2 console output을 확인하여 원인을 찾았고, Terraform 변수 값을 수정한 뒤 다시 배포하여 해결했습니다.

### 11.4 Python 버전 차이

로컬 개발 환경은 Python 3.12였지만, EC2 환경에서는 Python 3.9가 사용되었습니다.
이 과정에서 Python 3.10 이상에서 지원되는 타입 힌트 문법이 EC2에서 오류를 발생시켰고, `Optional[str]` 형태로 수정하여 배포 환경에서도 실행되도록 정리했습니다.

### 11.5 ALB Health Check

애플리케이션 정상 실행 여부를 ALB가 확인할 수 있도록 `/health` 엔드포인트를 추가했습니다.
Target Group health check가 해당 경로를 호출하도록 구성하여 인스턴스 교체 과정에서 정상 인스턴스만 트래픽을 받도록 했습니다.

---

## 12. 한계점 및 개선 방향

현재 프로젝트는 교육용 과제 범위에 맞춰 구현했기 때문에 몇 가지 한계가 있습니다.

첫째, 리스크 등급 산출 방식은 규칙 기반입니다.
향후에는 산업별 평균 재무비율이나 과거 부도 기업 데이터를 활용해 더 정교한 평가 기준을 만들 수 있습니다.

둘째, OpenDART 사업보고서 데이터는 기업별 공시 시점에 따라 조회 가능한 연도가 다를 수 있습니다.
현재는 조회 가능한 연도를 선택하는 방식으로 처리했지만, 향후에는 조회 가능한 연도만 자동으로 필터링하는 기능을 추가할 수 있습니다.

셋째, 현재 S3는 산출물 저장용으로 구성되어 있습니다.
향후에는 분석 결과를 CSV 또는 PDF 리포트로 생성하여 S3에 저장하고 다운로드하는 기능으로 확장할 수 있습니다.

넷째, 현재는 단일 기업 분석 중심입니다.
향후에는 여러 기업을 동시에 비교하는 기능을 추가할 수 있습니다.

---

## 13. 주의사항

* `.env` 파일은 GitHub에 업로드하지 않습니다.
* `terraform.tfvars`는 GitHub에 업로드하지 않습니다.
* `terraform.tfstate`와 `.terraform/` 디렉터리는 GitHub에 업로드하지 않습니다.
* OpenDART API Key, DB 비밀번호, AWS Credential은 저장소에 포함하지 않습니다.
* 본 프로젝트는 투자 추천 서비스가 아니며, 재무제표 데이터를 활용한 교육용 분석 웹서비스입니다.
