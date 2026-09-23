# ResidenceHub

ResidenceHub is a full-stack campus housing operations platform for managing the everyday workflows behind student accommodation: resident profiles, room assignments, maintenance requests, room changes, and fee records.

It combines a Flask REST API with a lightweight HTML/CSS/JavaScript client, giving students a self-service portal and housing staff a focused operations dashboard.

## Product snapshot

| Area | What it supports |
| --- | --- |
| Resident portal | Profile, room and roommate information, maintenance requests, room-change requests, and fees |
| Operations dashboard | Occupancy overview, resident assignment, request processing, maintenance types, and staff profile |
| Access control | JWT-based authentication with separate resident and staff workflows |
| Data layer | SQLAlchemy models backed by SQLite for local development |

## Stack

- **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-JWT-Extended, Flask-CORS
- **Frontend:** HTML5, CSS3, Bootstrap 5, vanilla JavaScript
- **Storage:** SQLite by default; configure another SQLAlchemy-compatible database with `DATABASE_URL`

## Repository layout

```text
.
├── backend/
│   ├── app/
│   │   ├── auth/          # Authentication routes and password helpers
│   │   ├── middlewares/   # Request authentication
│   │   ├── models/        # Users, rooms, requests, fees, and payments
│   │   └── views/         # Resident and operations API blueprints
│   ├── init_db.py         # Create local tables and sample data
│   ├── run.py             # Flask entry point
│   └── requirements.txt
├── frontend/
│   ├── admin/             # Operations dashboard pages
│   ├── student/           # Resident portal pages
│   ├── css/
│   └── js/
└── README.md
```

## Run locally

### 1. Create the environment

```bash
python -m venv .venv
```

Activate it using the command for your shell, then install the backend dependencies:

```bash
pip install -r backend/requirements.txt
```

### 2. Create sample data

```bash
python backend/init_db.py
```

This creates the local SQLite database with sample staff, residents, buildings, rooms, and maintenance types. Generated contact values use reserved `example.invalid` addresses and non-routable phone placeholders. Running it again resets the local database.

### 3. Start the application

```bash
python backend/run.py
```

Open <http://localhost:5000> in a browser. Flask serves both the API and the frontend from the same local process.

## Sample accounts

The seed script creates local-only accounts for exploring both workflows:

| Role | Username | Password |
| --- | --- | --- |
| Operations staff | `admin1` | `123456` |
| Resident | `100000000` | `123456` |

These credentials are for the generated local database only. Use environment variables for application secrets outside local development:

```text
SECRET_KEY=replace-me
JWT_SECRET_KEY=replace-me
DATABASE_URL=sqlite:///path/to/dormitory.db
```

## API surface

The backend exposes JSON endpoints under `/api`:

- `/api/auth` — login, registration, and password changes
- `/api/student` — resident profile, room, adjustment, maintenance, and fee workflows
- `/api/admin` — occupancy, resident assignment, request processing, and configuration workflows

Authenticated requests use the `Authorization: Bearer <token>` header returned by login.

## Development notes

This repository is optimized for local development and review. The wildcard API CORS policy, SQLite storage, seeded sample passwords, and process-local fallback secrets should be replaced or tightened before a real deployment.

## License

Released under the [MIT License](LICENSE).
