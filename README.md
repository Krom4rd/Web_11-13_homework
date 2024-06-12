# Homework 13 FastAPI. 
# Email varification, Recovery password, Cloud service, Limiter,
# Docker compose, Securyty


**Installation and launch**

- [ ] **_Activate the virtual environment_**

    python -m venv (venv_name)

    venv\Scripts\activate.bat

- [ ] **_Install dependencies_**
 
    pip install -r requirements.txt

- [ ] **_Create .env file and fill it_**

    example in env_example

- [ ] **_Create and run Docker postgresql containers_**

    docker-compose up

- [ ] **_Perform migrations for postgresql_**

    alembic upgrade head
    
- [ ] **_Run server_**

    uvicorn app.main:app --reload

- [ ] **_To receive documentation, open:_**

    http://127.0.0.1:8000/docs

- [ ] **_Stop server_**

    press ctrl+c

- [ ] **_Stop and remove Docker containers_**

    docker-compose down

