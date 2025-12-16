# TrailService API - MAL2018 Assessment 2

A RESTful micro-service built with **Flask** and **Flask-RESTx** for managing hiking trail data. This service connects to a SQL Server database and integrates with the University's external Authentication API for security.

**Student ID:** BSCS2509260  
**Module:** MAL2018 Information Management & Retrieval  
**Module Leader:** Dr. Ang Jin Sheng

---

## 🚀 Features

- **CRUD Operations:** Create, Read, Update, and Delete trails via RESTful endpoints
- **Authentication:** Basic Authentication integrated with external University Authentication API
- **Interactive Documentation:** Swagger UI automatically generated for testing
- **Data Persistence:** SQL Server database with stored procedures for security
- **Audit Logging:** Database triggers automatically log trail creation and deletion events

---

## 🛠️ Technologies Used

- **Language:** Python 3.13.2
- **Framework:** Flask 3.0.0 & Flask-RESTx 1.3.0
- **Database:** Microsoft SQL Server (localhost via Docker)
- **Database Driver:** pyodbc 5.0.1 (ODBC Driver 18 for SQL Server)
- **HTTP Requests:** requests 2.31.0 (for external API integration)

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Shahridan04/MAL2018-TrailService-CW2.git
cd MAL2018-TrailService-CW2
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

**Requirements:**
- Flask
- flask-restx
- pyodbc
- requests

### 3. Database Setup

Ensure your SQL Server is running (localhost or Docker).

**Run the database setup scripts in this order:**

1. Open **Azure Data Studio**
2. Connect to your SQL Server (localhost)
3. Open and execute `sql/cw2_tables.sql` (Creates Tables & Triggers)
4. Open and execute `sql/cw2_procedures.sql` (Creates Stored Procedures)

This will create:
- **CW2 schema**
- **3 tables** (User, Trail, TrailLog)
- **5 stored procedures** (sp_CreateTrail, sp_GetAllTrails, etc.)
- **1 trigger** (trg_LogNewTrail)

### 4. Configure Database Connection

Update the connection details in `app.py` if needed:

```python
DB_SERVER = 'localhost'
DB_NAME = 'MAL2017 Trail Database'  # Your database name
DB_USER = 'SA'
DB_PASS = 'YourPassword'  # Your SQL Server password
```

---

## 🏃‍♂️ How to Run

Start the Flask application:

```bash
python app.py
```

The server will start on **http://localhost:8000**

You should see:
```
 * Running on http://0.0.0.0:8000
```

---

## 📖 API Documentation (Swagger UI)

Once running, access the interactive API documentation at:

👉 **http://localhost:8000/swagger**

The Swagger UI provides:
- Interactive endpoint testing
- Authentication interface
- Data model schemas

---

## 🔐 Authentication

Protected endpoints (`POST`, `PUT`, `DELETE`) require authentication via the external University Authentication API.

**How to Authenticate:**

1. Click the **🔒 Authorize** button in Swagger UI
2. Enter the credentials below (Basic Auth)

**Test Accounts:**

| Name | Email | Password | Role |
|------|-------|----------|------|
| Grace Hopper | grace@plymouth.ac.uk | ISAD123! | Admin |
| Tim Berners-Lee | tim@plymouth.ac.uk | COMP2001! | Admin |
| Ada Lovelace | ada@plymouth.ac.uk | insecurePassword | User |

---

## 🔗 API Endpoints

| Method | Endpoint | Description | Auth Required? |
|--------|----------|-------------|----------------|
| **GET** | `/trails/` | Get all trails | ❌ No |
| **GET** | `/trails/{id}` | Get specific trail by ID | ❌ No |
| **POST** | `/trails/` | Create a new trail | ✅ Yes |
| **PUT** | `/trails/{id}` | Update an existing trail | ✅ Yes |
| **DELETE** | `/trails/{id}` | Delete a trail | ✅ Yes |

### Example Request: Create Trail (POST)

**Header:**
```
Authorization: Basic <Base64Credentials>
```

**Body:**
```json
{
  "TrailName": "Beautiful Mountain Trail",
  "Length": 8.5,
  "ElevationGain": 320,
  "RouteType": "Out & Back",
  "Difficulty": "Hard",
  "Duration": 180,
  "Description": "A challenging mountain trail with stunning views",
  "OwnerID": 3
}
```

---

## 🗄️ Database Schema (CW2)

The micro-service uses a normalized SQL Server database with the following structure:

- **User:** User accounts and roles
- **Trail:** Main trail information (linked to User)
- **TrailLog:** Audit log for trail operations (preserves history even after deletion)

All database operations use **stored procedures** to prevent SQL injection and maintain security.

---

## 📁 Project Structure

```
MAL2018-TrailService-CW2/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── README.md               # This file
└── sql/
    ├── cw2_tables.sql      # Creates Tables & Triggers
    └── cw2_procedures.sql  # Creates Stored Procedures
```

---

## 🔒 Security Features

- **SQL Injection Prevention:** All database operations use parameterized stored procedures
- **Authentication:** Integration with external University Authentication API using Basic Auth
- **Input Validation:** Multi-layer validation (Flask-RESTx Models + Database Constraints)
- **Audit Logging:** Automatic logging of trail creation and deletion via database triggers and procedures

---

## 📧 Contact

**Student ID:** BSCS2509260  
**Module:** MAL2018 Information Management & Retrieval  
**Academic Year:** 2024/2025

For assessment-related queries, contact the module leader: **Dr. Ang Jin Sheng**

---

**Note:** This project is submitted as coursework for academic assessment at the University of Plymouth. The implementation demonstrates understanding of RESTful API design, database integration, and security best practices.

**Last Updated:** December 2025
