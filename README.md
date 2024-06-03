# Homework 11 FastAPI

**Installation and launch**

- [ ] **_Activate the virtual environment_**

    python -m venv (venv_name)

    venv\Scripts\activate.bat

- [ ] **_Install dependencies_**
 
    pip install -r requirements.txt

- [ ] **_Create and run Docker postgresql container_**

    docker run --name homework_11 -p 5432:5432 -e POSTGRES_PASSWORD=password -d postgres

- [ ] **_Perform migrations for postgresql_**

    alembic upgrade head
    
- [ ] **_Run server_**

    uvicorn app.main:app

- [ ] **_To receive documentation, open:_**

    http://127.0.0.1:8000/docs

