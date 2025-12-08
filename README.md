# Jeonse-Main Server
메인 API 서버
AWS EC2(Ubuntu) + Node.js + Express + MySQL 환경으로 구성

---

##  서버 정보

- **배포 서버 주소 (Public IP):** http://54.180.88.230
- **포트:** 80
- **헬스체크**:  
  - http://54.180.88.230/health  
  - http://54.180.88.230/db-health

---

##  프로젝트 구조

```
jeonse-main/
├── index.js          # 메인 서버 파일 (Express)
├── db.js             # MySQL 연결 설정 파일
├── routes/           # API 라우터 폴더 (확장 예정)
│   ├── health.js     # 서버 헬스체크 라우터
│   └── analysis.js   # 분석 API 라우터
├── package.json
├── .env              # 환경변수 파일 (GitHub 업로드 금지)
└── README.md
```

---

##  환경 변수(.env)

> **GitHub 업로드X**

EC2 서버 내부의 .env 내용:

```
DB_HOST=localhost
DB_USER=jeonse_user
DB_PASSWORD=jeonse1234!
DB_NAME=jeonse_db
PORT=80
```

---

##  Database(MySQL) 정보

- **DB 이름:** `jeonse_db`
- **DB 유저:** `jeonse_user`
- **DB 비밀번호:** `jeonse1234!`
- **EC2 내부 접속 방법:**

```bash
sudo mysql -u root
# or
mysql -u jeonse_user -p
```

---

## 서버 실행 방법

PM2로 실행

```bash
pm2 start index.js --name jeonse-main
pm2 status
pm2 restart jeonse-main
pm2 logs jeonse-main
```

---

## 로컬 개발 환경에서 실행

1) **레포지토리 클론**
```bash
git clone https://github.com/P-Proj.Team23/jeonse-main.git
cd jeonse-main
```

2) **패키지 설치**
```bash
npm install
```

3) **.env 파일 생성**
```
DB_HOST=localhost
DB_USER=jeonse_user
DB_PASSWORD=jeonse1234!
DB_NAME=jeonse_db
PORT=3000
```

4) **로컬 서버 실행**
```bash
node index.js
```

5) **정상 동작 확인**
- http://localhost:3000/health  
- http://localhost:3000/db-health  

---

## API 테스트

### Health Check
```
GET /health
```

### DB 연결 테스트
```
GET /db-health
```

### 전세 분석 요청 (더미 API)
```
POST /analysis/request
Content-Type: application/json

{
  "address": "서울시 ...",
  "deposit": 200000000,
  "jeonseType": "아파트"
}
```

---

##  Dependencies

- express
- cors
- mysql2
- dotenv
- pm2 *(운영 환경)*

