# Cat Management System

A full-stack CRUD application created as a learning project during my studies at **John Bryce**.

The project brings together a Python REST API, a SQLite database, and a JavaScript frontend. It focuses on the basics of managing data through an API and deploying the frontend and backend separately.

[Live demo](https://catmanager.netlify.app/) · [API documentation](https://catscrudrender.onrender.com/docs)

## Features

- Add cats with a name, breed, age, and weight.
- View saved cats in a table.
- Edit an existing cat through a modal form.
- Delete a cat after confirmation.
- Store records in SQLite through SQLAlchemy.
- Explore and try API requests through FastAPI's interactive documentation.

## Tech stack

| Layer | Technologies |
| --- | --- |
| Frontend | HTML, CSS, JavaScript, Tailwind CSS, Axios |
| Backend | Python, FastAPI, Pydantic, Uvicorn |
| Database | SQLite, SQLAlchemy |
| Deployment | Netlify frontend, Render backend |

The frontend sends HTTP requests to the FastAPI backend. The backend uses Pydantic models for request and response data and SQLAlchemy to read and write SQLite records.

## Run locally

You will need Git and Python. Python 3.12 was used to verify the backend locally. The frontend loads Tailwind CSS and Axios from a CDN, so an internet connection is also needed.

### 1. Clone the repository

```bash
git clone https://github.com/NimLordia/catscrudrender.git
cd catscrudrender
python -m venv .venv
```

Activate the virtual environment:

**Windows PowerShell**

```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
source .venv/bin/activate
```

If your system uses `python3` instead of `python`, use that command when creating the virtual environment.

### 2. Start the backend

From the repository root, with the virtual environment active:

```bash
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

- API: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Interactive documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

The application uses `cats.db` in the current working directory and creates the database tables on startup if needed. Run the backend from the repository root to use the database included in this repository.

### 3. Connect and start the frontend

In `frontend/script.js`, change the API URL to your local backend:

```javascript
const API_URL = 'http://127.0.0.1:8000';
```

The checked-in value points to the deployed Render API. Change it before testing locally so that your frontend uses your local database.

In a second terminal, from the repository root, run:

```bash
python -m http.server 5500 --directory frontend
```

Open [http://localhost:5500](http://localhost:5500). Port `5500` is included in the backend's allowed CORS origins.

## API endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/` | Return a health status and timestamp |
| `POST` | `/cats/` | Create a cat |
| `GET` | `/cats/` | List cats; accepts `skip` and `limit` query parameters |
| `GET` | `/cats/{cat_id}` | Get one cat |
| `PUT` | `/cats/{cat_id}` | Replace a cat's editable fields |
| `DELETE` | `/cats/{cat_id}` | Delete a cat |

Example request body for creating or updating a cat:

```json
{
  "name": "Luna",
  "breed": "Domestic Shorthair",
  "age": 2.5,
  "weight": 4.2
}
```

The API assigns an `id` when a cat is created. Updates require all four editable fields. The list endpoint returns up to 100 records by default.

## Project structure

```text
catscrudrender/
├── frontend/
│   ├── index.html       # Form, table, and edit modal
│   ├── script.js        # API requests and UI interactions
│   └── style.css        # Custom styling
├── main.py             # FastAPI app, models, database setup, and routes
├── cats.db             # SQLite database
├── requirements.txt    # Pinned Python dependencies
└── README.md
```

## Learning scope and next steps

This is a study project demonstrating a complete CRUD flow. It includes request logging, explicit CORS origins, and a health endpoint, while keeping the application small enough to follow in a few files.

Areas for further practice include stronger input validation, safer frontend event handling, automated tests, pagination controls, and improved loading, error, and accessibility states. The application currently has no user accounts or access controls.

SQLite persistence on a hosted service depends on its storage configuration; the repository does not configure persistent storage for Render.
