# Smart Grid Load Balancing API Architecture

User
│
▼

Swagger UI / API Client
│
▼

FastAPI Application
│
├── Health Endpoint
├── Load Endpoint
├── Alerts Endpoint
├── Dashboard Endpoint
├── Grid Status Endpoint
├── Prediction Endpoint
└── Recommendations Endpoint
│
▼

SQLAlchemy ORM
│
▼

SQLite Database
│
▼

Load Records
(area, current_load, max_capacity)
