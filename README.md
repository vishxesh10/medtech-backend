# 🩺 MedTech AI — Smart Prescription Digitizer & Management Backend

An AI-powered healthcare backend project designed to digitize handwritten and printed medical prescriptions using **Google Gemini Vision AI**, securely manage patient prescription history in **MongoDB**, and provide clean REST APIs built with **FastAPI**.

---

## 📖 Project Overview

Reading and keeping track of paper prescriptions is difficult for both patients and healthcare providers. Lost prescriptions lead to missed doses, incorrect medicine purchases, and poor health tracking.

**MedTech AI** solves this by:
1. Allowing patients to upload a photo of their medical prescription.
2. Using **Google Gemini AI** to extract structured medical details:
   - Patient Name & Doctor / Clinic Name
   - Prescription Date
   - Diagnosis & Symptoms
   - Medicines List (Name, Dosage, Frequency, Duration, Instructions)
   - General Doctor Advice & Precautions
3. Storing prescriptions securely under the user's authenticated account.
4. Providing full CRUD management (Upload, View History, View Details, Delete, and User Stats).

---

## 🚀 Key Features

- **🔐 User Authentication**: Secure password hashing with `bcrypt` and token-based authentication using **JWT (JSON Web Tokens)**.
- **🤖 AI Prescription OCR**: Seamlessly integrates with Google Gemini (e.g. `gemini-2.5-flash`) for medical document information extraction.
- **🛡️ Comprehensive Error Handling & Validation**:
  - Validates required inputs (email format, minimum password length, non-empty fields).
  - Validates file uploads (only image formats like JPEG, PNG, WEBP allowed).
  - Provides clear, friendly error messages for missing tokens, expired sessions, and invalid IDs.
- **💾 Dual Database Support (Zero-Setup)**:
  - **Memory Mode (`mongomock`)**: Default mode — run the project immediately without installing or running MongoDB!
  - **MongoDB Mode**: Easily connect to local MongoDB or MongoDB Atlas in the cloud.
- **📚 Interactive API Documentation**: Built-in Swagger UI at `http://127.0.0.1:8000/docs`.

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Framework** | [FastAPI](https://fastapi.tiangolo.com/) | Modern, high-performance web framework for Python |
| **Server** | [Uvicorn](https://www.uvicorn.org/) | Lightning-fast ASGI server |
| **AI / Vision** | [Google Gemini AI](https://aistudio.google.com/) | Optical Character Recognition (OCR) and medical data extraction |
| **Database** | [MongoDB](https://www.mongodb.com/) / [MongoMock](https://github.com/mongomock/mongomock) | NoSQL document storage with in-memory fallback |
| **Authentication** | [PyJWT](https://pyjwt.readthedocs.io/) & [Bcrypt](https://pypi.org/project/bcrypt/) | Secure token generation and salted password hashing |
| **Data Validation** | [Pydantic v2](https://docs.pydantic.dev/) | Request and response schema validation |
| **Image Handling** | [Pillow (PIL)](https://python-pillow.org/) | Image verification and preprocessing |

---

## 📂 Project Structure

```text
medtech-backend/
├── api/
│   └── routes.py           # All REST API endpoints (Auth, Prescriptions, Health)
├── database/
│   ├── database.py         # MongoDB connection & index setup with memory fallback
│   └── __init__.py
├── models/
│   ├── models.py           # Pydantic schemas for requests and responses
│   └── __init__.py
├── services/
│   └── gemini_service.py   # Google Gemini API integration and extraction prompt
├── tests/
│   ├── conftest.py         # Pytest configuration and in-memory test DB fixture
│   ├── test_auth.py        # Authentication unit & integration tests
│   ├── test_prescription.py# Prescription upload, extraction, and scoping tests
│   └── test_system.py      # Health check and root route tests
├── utils/
│   ├── auth.py             # Password hashing, JWT creation & token dependency
│   └── json_parser.py      # Safe JSON parser from AI output
├── app.py                  # FastAPI application entry point & exception handlers
├── config.py               # Application configuration and environment variables
├── db.py                   # Compatibility alias for database module
├── .env                    # Local environment variables
├── .env.example            # Sample template for environment variables
└── pyproject.toml          # Project metadata and dependencies
```

---

## ⚙️ Setup & Installation Guide

### Step 1: Clone the repository & navigate to directory
```bash
git clone <your-repo-url>
cd medtech/medtech-backend
```

### Step 2: Create and activate virtual environment
**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install dependencies
```bash
pip install -e .
```
*(Alternatively: `pip install fastapi uvicorn pymongo mongomock bcrypt pyjwt pillow google-genai python-dotenv python-multipart email-validator`)*

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Open `.env` and configure:
```env
# Set to 'memory' to run immediately without a local MongoDB server
DATABASE_MODE=memory

# Add your free Gemini API Key from https://aistudio.google.com/app/apikey
GEMINI_KEY=your_gemini_api_key_here
```

### Step 5: Start the development server
```bash
uvicorn app:app --reload --port 8000
```
Open your browser and visit:
- **Root URL**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Swagger Interactive API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Alternative ReDoc UI**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 📡 API Endpoints Reference

### 1. System & Health
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | API welcome message & links | No |
| `GET` | `/health` | Server health check (`{"status": "ok"}`) | No |
| `GET` | `/version` | App name and current version | No |

### 2. Authentication
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/register` | Register a new user (`name`, `email`, `password`) | No |
| `POST` | `/auth/login` | Login, get JWT token, and auto-set `access_token` cookie | No |
| `POST` | `/auth/logout` | Logout user and clear authentication cookie | No |
| `GET` | `/auth/me` | Get profile details of the logged-in user | **Yes** (Bearer Token or Cookie) |
| `GET` | `/auth/verify` | Verify if current JWT token is active and valid | **Yes** (Bearer Token or Cookie) |

### 3. Prescriptions
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/extract-prescription` | Upload prescription image & extract AI data | **Yes** (Bearer Token or Cookie) |
| `GET` | `/prescriptions` | List all prescriptions for current user | **Yes** (Bearer Token or Cookie) |
| `GET` | `/prescriptions/{id}` | Get full details of a specific prescription | **Yes** (Bearer Token or Cookie) |
| `DELETE`| `/prescriptions/{id}` | Delete a prescription record by ID | **Yes** (Bearer Token or Cookie) |
| `GET` | `/prescriptions/stats/summary`| Get summary statistics (e.g. total uploads) | **Yes** (Bearer Token or Cookie) |

---

## 🧪 Testing the API

You can test all endpoints directly using the **Swagger UI** at `http://127.0.0.1:8000/docs`:

1. Click **`POST /auth/register`** -> **Try it out**:
   ```json
   {
     "name": "Jane Doe",
     "email": "jane@example.com",
     "password": "mypassword123"
   }
   ```
2. Click **`POST /auth/login`** -> **Try it out**:
   ```json
   {
     "email": "jane@example.com",
     "password": "mypassword123"
   }
   ```
3. Copy the returned `access_token`. Click the **Authorize 🔓** button at the top right of the Swagger page and paste the token.
4. Click **`POST /extract-prescription`** -> Upload an image of a medical prescription.
5. Inspect the structured JSON output returned with medicines, dosage, and doctor notes!

---

## 🛡️ Error Handling Details

The application implements explicit, friendly error handling for required fields:

| Scenario | HTTP Status | Response Detail |
| :--- | :--- | :--- |
| Password < 6 characters | `422 Unprocessable` | `"body -> password: String should have at least 6 characters"` |
| Invalid email format | `422 Unprocessable` | `"body -> email: value is not a valid email address"` |
| Duplicate email signup | `400 Bad Request` | `"Email already registered"` |
| Wrong login credentials | `401 Unauthorized` | `"Incorrect email or password"` |
| Missing Bearer token | `401 Unauthorized` | `"Authentication required. Please log in."` |
| Expired Bearer token | `401 Unauthorized` | `"Your login session has expired. Please log in again."` |
| Non-image file uploaded | `415 Unsupported Media` | `"Only image uploads are supported"` |
| Missing Gemini API key | `400 Bad Request` | `"Gemini API key is missing. Please set GEMINI_KEY in your .env file."` |
| Gemini temporarily unavailable | `503 Service Unavailable` | `"Gemini AI is temporarily unavailable due to high demand. Please try again shortly."` |
| Non-existent Prescription ID | `404 Not Found` | `"Prescription not found"` |

---

## 💡 Future Enhancements

- 📱 Medicine reminder notifications via WhatsApp / SMS.
- ⚠️ Automated drug-to-drug allergy and interaction warnings.
- 📄 Export digitized prescription report as downloadable PDF.
- 🌐 Multilingual support for prescription translation.

---

## 👤 Author
Developed as an AI-powered MedTech showcase project for demonstrating clean API design, authentication, and computer vision integration.
