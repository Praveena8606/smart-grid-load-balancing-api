# Smart Grid Load Balancing API

A FastAPI-based backend service for smart grid load management.

## Features

* FastAPI REST API
* Health Check Endpoint
* Load Data Endpoint
* Request Validation with Pydantic
* Docker Support
* Swagger API Documentation

## Installation

```bash
pip install -r requirements.txt
```

## Run Locally

```bash
uvicorn app.main:app --reload
```

## API Documentation

Open in your browser:

```text
http://127.0.0.1:8000/docs
```

## Docker

Build image:

```bash
docker build -t smart-grid-api .
```

Run container:

```bash
docker run -p 8000:8000 smart-grid-api
```