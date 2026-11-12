# 🛡️ SafeGuard AI — Interactive Testing Dashboard

Modern, lightweight, standalone developer dashboard built specifically for interactively testing and verifying all SafeGuard AI backend APIs without needing Postman or curl.

---

## ⚡ Quick Start (Kaise Run Karein)

### Option 1: Python Launcher (Recommended)
Open your terminal inside the `backend/` directory or `testing_ui/` folder:

```bash
# Agar aap backend directory mein hain:
python testing_ui/run_ui.py

# Ya direct testing_ui folder mein:
cd testing_ui
python run_ui.py
```
Yeh script automatically browser mein `http://127.0.0.1:8080` open kar degi aur backend status check karke console par display karegi.

---

### Option 2: Direct Browser Open (Double Click)
Aap direct `testing_ui/index.html` file par double-click karke kisi bhi browser (Chrome, Edge, Firefox, Brave) mein open kar sakte hain.

---

## 📋 Prerequisites (Zaroori Cheezein)

1. **SafeGuard Django Backend Server Running**:
   Make sure the Django backend is running in another terminal window:
   ```bash
   cd backend
   python manage.py runserver
   ```
   *Default API URL:* `http://127.0.0.1:8000`

2. **CORS Development Settings**:
   Development mode mein `CORS_ALLOW_ALL_ORIGINS=True` enabled hai, isliye browser fetch requests seamlessly execute hongi.

---

## 🎯 Features & Walkthrough (Features Ki Jankari)

### 1. 🩺 Server Health Check (`GET /api/v1/health/`)
- Backend live hai ya nahi verify karein.
- Response time (ms), service status (`healthy`), aur version inspect karein.
- One-click Swagger UI (`/api/docs/`) aur Django Admin (`/admin/`) links.

### 2. 🔐 Authentication Suite
- **User Registration (`POST /api/v1/auth/register/`)**:
  - Email, Display Name, Phone Number, Password, Password Confirm, Preferred Language.
  - **"Auto-fill Sample Data"** button se 1 second mein dummy user generate karein.
  - Registration successful hote hi login form automatically fill ho jata hai!
- **User Login (`POST /api/v1/auth/token/`)**:
  - Authenticate karke Access Token & Refresh Token acquire karein.
  - Access & Refresh tokens state aur browser `localStorage` mein store ho jaate hain.
  - One-click copy buttons for tokens.
  - Decoded JWT payload viewer: `user_id`, `token_type`, expiry timestamp, live countdown timer!
- **Token Refresh (`POST /api/v1/auth/token/refresh/`)**:
  - Refresh token use karke naya Access Token acquire karein.
- **Blacklist / Logout (`POST /api/v1/auth/token/blacklist/`)**:
  - Current refresh token ko blacklist karke user ko log out karein.

### 3. 👤 User Profile Management
- **Fetch Profile (`GET /api/v1/users/me/`)**:
  - Logged-in user ka details card (Email, Name, Phone, Language, Role, Bio, Emergency Message).
- **Update Profile (`PATCH /api/v1/users/me/`)**:
  - Live edit name, phone number, language, bio, aur emergency SOS broadcast message.

### 4. 🚨 Emergency SOS Alert Simulator (`POST /api/v1/emergencies/sos/`)
- Real-world emergency workflows simulate karne ke liye:
  - Event types: `sos`, `panic`, `test`.
  - Auto-generated UUID v4 `idempotency_key` (duplicate tap safety test karne ke liye).
  - Quick City GPS Presets: **Delhi**, **Mumbai**, **Bengaluru**.
  - **"Device GPS"** button: Browser Geolocation API se aapki live latitude/longitude automatically populate karega.
  - Emergency history quick fetch (`GET /api/v1/emergencies/`).

### 5. ⚡ Custom Request Explorer
- Kisi bhi SafeGuard API endpoint (`/api/v1/contacts/`, `/api/v1/locations/snapshots/`, `/api/v1/notifications/`, `/api/v1/audit/`) par GET, POST, PUT, PATCH, DELETE requests execute karein.
- JSON body editor with "Prettify JSON" formatter.
- Auto Bearer token injection.

### 6. 🔍 Live Response Inspector (Right Column)
- **Status Pills**: Color-coded HTTP status codes (200 OK, 201 Created, 400 Bad Request, 401 Unauthorized, 500 Error).
- **Response Latency**: Live millisecond round-trip time.
- **Formatted JSON View**: Full syntax highlighting (keys, strings, numbers, booleans, null) with 1-click "Copy JSON".
- **Request Sent View**: Inspect exact headers, URL, and body payload that was dispatched.
- **Response Headers View**: View all server response headers.
- **History Log**: Recent 15 API requests track karta hai. Kisi bhi purani request par click karke usko wapas inspector mein load kiya ja sakta hai.

### 7. 🎨 UI & Ergonomics
- Dark / Light Mode toggle (sun/moon icon).
- Floating Toast notifications for clear feedback and DRF field-specific validation errors.
- Fully responsive design using Tailwind CSS.

---

## 🛠️ Folder Structure

```
testing_ui/
├── index.html       # Single-page UI dashboard
├── app.js           # Client-side API runner, state & token manager
├── styles.css       # Custom styles, syntax highlighting & animations
├── run_ui.py        # Local lightweight HTTP server & browser launcher
└── README.md        # Documentation and user guide
```

---

## 💡 Troubleshooting

- **Backend Status Shows "Offline"**:
  - Make sure backend server is running: `python manage.py runserver 127.0.0.1:8000`.
  - Check the Base URL input at top of the page; it should be `http://127.0.0.1:8000`.
- **401 Unauthorized Errors**:
  - Go to the **Auth & Tokens** tab and login to obtain a fresh JWT token.
- **Port 8080 Already in Use**:
  - `run_ui.py` automatically detects occupied ports and chooses the next available port (e.g. 8081).
