# elo-riders-CoreAPI
## Description
Microservice component with logic and connection with DB and AI Server.

## Endpoints
- GET /ping | Component health status (Return component name)
- GET /users/ping | API health status (Importante para el despliegue)
- GET /users/ | Get all users information
- POST /users/ | Create user information
  ```json
    {
        "username": "david",
        "email": "david@email.com",
        "password": "123",
        "name": "David",
        "lastname": "Davidson",
        "gender": "MALE",
        "profile": "BIKER",
        "address": "Midland",
        "phone": "42334345",
        "birthdate": "1947-05-13",
        "membership_level": "NO"
    }
  ```
- GET /users/login | Get elo score and location data
- GET /users/user/{id} | Get user information by id
- GET /users/friends | Get all users close with Elo score
- DELETE /users/user/{id} | Delete user information by id
- POST /sensors/data | Get all users information
  ```json
  {
        "user_id": 1,
        "last_month_miles": 50,
        "total_miles": 500,
        "avg_speed": 95.5,
        "braking_events": 20,
        "heart_rate": 150,
        "blood_pressure": 110,
        "stress_level": 80,
        "sleep_quality": 3,
        "latitude": 4.6752640,
        "longitude": -74.0488979
  }
  ```
- GET /sensors/data/{id} | Get user sensors data by id
- GET /events | Get all events

## Environment variables
- PORT : 5001 | Exposed port
- DATABASE_URL | DB URI
- OLLAMA_ENDPOINT | IP AI server

## Build
### Local execution
```shell
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r src/requirements.txt
export DEV_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/core-api-db
export FLASK_APP=src/app.py PYTHONPATH=./ FLASK_ENV=development TESTING=False FLASK_DEBUG=True FLASK_APP_NAME=core-api
gunicorn --bind 0.0.0.0:9000 manage:app --log-level debug --reload
```

### Container execution
```shell
docker build -t core-api:1.0.0 .
docker run -e PORT=5000 -p 5001:5000 --name core-api core-api:1.0.0
```