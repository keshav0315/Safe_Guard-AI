# SafeGuard AI Backend — How To Use Guide (Hinglish) 🛡️

Yeh guide bilkul aasan **Hinglish** me likhi gayi hai taaki aapko pata chal sake ki kaun si command kab run karni hai, kaise run karni hai, aur us command ko run karne se **kya hoga**.

---

## Table of Contents (Index)
1. [Prerequisites & Virtual Environment (Pehle ye karein)](#1-prerequisites--virtual-environment)
2. [Database Connection Setup (Database kaise connect hoga)](#2-database-connection-setup)
3. [Har Command Ki Detail (Konsi command se kya hota hai)](#3-har-command-ki-detail-konsi-command-se-kya-hota-hai)
4. [Backend Server Start Karna](#4-backend-server-start-karna)
5. [Authentication Testing UI (Bina coding ke test karein)](#5-authentication-testing-ui)
6. [Automated Tests Run Karna](#6-automated-tests-run-karna)
7. [API Documentation (Swagger / OpenAPI)](#7-api-documentation)
8. [Common Errors Aur Unka Solution](#8-common-errors-aur-unka-solution)

---

## 1. Prerequisites & Virtual Environment

Sabse pehle terminal (PowerShell ya CMD) open karein aur backend folder me jayein:
```powershell
cd "c:\Users\kesha_gne9rdf\OneDrive\Documents\Projects\safe_gaurd ai app\backend"
```

### Command: Virtual Environment Activate Karna
```powershell
.\venv\Scripts\Activate.ps1
```
*(Agar CMD use kar rahe hain toh: `.\venv\Scripts\activate.bat`)*

> **Is command se kya hoga?**
> Yeh command aapke project ke isolated Python environment (`venv`) ko active kar deti hai. Isse project ke saare installed packages (Django, DRF, Pytest, JWT, Celery) accessible ho jate hain aur globally koi conflict nahi hota.

---

## 2. Database Connection Setup

Aapke backend me 2 options hain:

### Option A: SQLite (Sabse Aasan — Local Development Ke Liye)
Agar aapke paas PostgreSQL install nahi hai ya aap jaldi se test karna chahte hain:
1. `.env` file open karein.
2. Ye line ensure karein:
   ```env
   USE_SQLITE=True
   ```
> **Isse kya hoga?**
> Backend bina kisi external software ke ek local `db.sqlite3` file me sara data store karega.

---

### Option B: PostgreSQL (Production Ke Liye)

#### Tareeqa 1: Docker Ke Through (Recommended agar Docker hai)
```powershell
docker-compose up -d db redis
```
> **Is command se kya hoga?**
> PostgreSQL 16 container port `5432` par aur Redis container port `6379` par background me start ho jayenge.

#### Tareeqa 2: Local PostgreSQL (pgAdmin / Local Service)
1. pgAdmin me jakar `safeguard_db` naam ka database create karein.
2. `.env` file me check karein:
   ```env
   USE_SQLITE=False
   DB_NAME=safeguard_db
   DB_USER=safeguard_user
   DB_PASSWORD=devpassword
   DB_HOST=localhost
   DB_PORT=5432
   ```

---

## 3. Har Command Ki Detail (Konsi command se kya hota hai)

### 1. `python manage.py makemigrations`
```powershell
.\venv\Scripts\python.exe manage.py makemigrations
```
- **Kyu chalayein:** Jab aap kisi model (`models.py`) me koi naya field add karte hain ya change karte hain.
- **Kya hoga:** Django aapke models ko scan karke migration blueprints files (`safeguard_backend/apps/*/migrations/`) tayar karta hai.

### 2. `python manage.py migrate`
```powershell
.\venv\Scripts\python.exe manage.py migrate
```
- **Kyu chalayein:** Database me tables create karne ke liye. (Setup ke baad sabse pehli zaroori command).
- **Kya hoga:** Saari pending migrations database (SQLite ya PostgreSQL) me execute hongi aur users, contacts, emergencies, tokens, audit tables ban jayenge.

### 3. `python manage.py createsuperuser`
```powershell
.\venv\Scripts\python.exe manage.py createsuperuser
```
- **Kyu chalayein:** Admin panel me login karne ke liye administrator account banane ke liye.
- **Kya hoga:** Terminal aapse Email aur Password mangega. Enter karne ke baad ek full-access admin user ban jayega.

### 4. `python manage.py runserver`
```powershell
.\venv\Scripts\python.exe manage.py runserver
```
- **Kyu chalayein:** Backend development web server start karne ke liye.
- **Kya hoga:** Django server `http://127.0.0.1:8000/` par live ho jayega aur requests accept karna shuru kar dega. Auto-reload on rehta hai (code save karte hi server reload ho jata hai).

---

## 4. Backend Server Start Karna

Backend ko run karne ke steps:
```powershell
# Step 1: Database tables banayein
.\venv\Scripts\python.exe manage.py migrate

# Step 2: Server start karein
.\venv\Scripts\python.exe manage.py runserver
```

Ab aapka server live hai:
- **API Base URL:** `http://127.0.0.1:8000/`
- **Health Check:** `http://127.0.0.1:8000/api/v1/health/`
- **Django Admin:** `http://127.0.0.1:8000/admin/`

---

## 5. Authentication Testing UI

Aapke liye ek standalone UI test dashboard banaya gaya hai jo `testing_ui/` folder me hai.

### Testing UI Kaise Run Karein?
Method 1: Direct Browser me open karein
- `testing_ui/index.html` file par double click karke kisi bhi browser (Chrome/Edge) me open kar lein.

Method 2: Local Python server ke through
```powershell
cd testing_ui
..\venv\Scripts\python.exe run_ui.py
```
*(Ya `python -m http.server 8080` chala kar `http://127.0.0.1:8080` open karein).*

### Testing UI Me Kya-Kya Test Kar Sakte Hain?
1. **Health Check:** Green status pill se pata chalega server chal raha hai ya nahi.
2. **User Registration:** Email, name, phone, password daal kar naya user account create karein.
3. **User Login:** Email aur password se login karke JWT Access Token aur Refresh Token generate karein.
4. **My Profile (`/users/me/`):** Current logged-in user ki details fetch karein aur update karein.
5. **Token Refresh:** Expire hone par naya access token generate karein.
6. **Logout:** Token blacklist karke logout test karein.
7. **Emergency SOS Trigger:** Quick panic alert trigger karke response payload aur status code inspect karein.
8. **Live Inspector:** Har API call ka exact Status Code (200, 201, 400), response time (ms), aur JSON response live display hota hai.

---

## 6. Automated Tests Run Karna

Backend ke automated test suite ko run karne ke liye:
```powershell
.\venv\Scripts\pytest.exe -v
```

> **Is command se kya hoga?**
> Yeh command `tests/` aur `apps/` ke saare unit tests, API tests, aur security tests ko RAM ke andar (in-memory SQLite me) execute karegi aur dikhayegi ki kaun sa test PASS hua aur kaun sa FAIL.

Agar kisi specific test file ko run karna ho:
```powershell
# Sirf auth tests run karne ke liye:
.\venv\Scripts\pytest.exe tests/api/test_auth.py -v

# Sirf emergencies tests run karne ke liye:
.\venv\Scripts\pytest.exe tests/api/test_emergencies.py -v
```

---

## 7. API Documentation

Backend chalne ke baad interactive documentation yahan available hoti hai:
- **Swagger UI:** `http://127.0.0.1:8000/api/docs/`
  *(Yahan se aap directly browser me kisi bhi API ko try kar sakte hain)*
- **ReDoc:** `http://127.0.0.1:8000/api/redoc/`
- **OpenAPI Schema (JSON):** `http://127.0.0.1:8000/api/schema/`

---

## 8. Common Errors Aur Unka Solution

1. **Error: "Port 8000 is already in use"**
   - Solution: Dusra port use karein:
     ```powershell
     .\venv\Scripts\python.exe manage.py runserver 8001
     ```

2. **Error: "No module named ..."**
   - Solution: Virtual environment activate karein (`.\venv\Scripts\Activate.ps1`).

3. **Database connection failed / could not connect to server**
   - Solution: Agar PostgreSQL start nahi hai toh `.env` me `USE_SQLITE=True` kar lein aur `python manage.py migrate` run karein.
