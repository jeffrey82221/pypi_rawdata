# pypi_rawdata

Crawling Data From PyPi and convert JSON into Tabular Data


# Plan 

1. [X] Using pip package to identify package name from `requires_dist` of pypi json file.

```
from pip._vendor.distlib.util import parse_requirement
```

2. [X] Obtain more requirement information including max/min versions, number of release versions, etc.

# How to set up batchwise update framework? 

- [X] Add .github/workflows/job.yml into the Repo
- [X] Add requirements.txt that install batch-framework
- [X] Run requirements.txt using `pip install -r requirements.txt`
- [X] Create src/ with classes inheriting batch_framework ETLBase
- [X] Add template.yml and build_yml.py into Repo
- [X] Connect the ETLGroup object of src/ to GithubActionAdaptor in build_yml.py
- [X] Run build_yml.py 
    - [X] Follow the instruction step in the pop-up browser and Enter the dropbox_access_token obtained from the browser.
    - [X] A DROPBOX_REFRESH_TOKEN.ini file will be created. Make sure it is added into .gitignore
    - [X] Check that etl.yml is also be added into .github/workflows/
- [X] Add `run_task.py` to Repo and connect it with the ETLGroup object.
- [X] Add the following secrets to the REPO

```yml
    DROPBOX_APP_KEY: ${{ secrets.DROPBOX_APP_KEY }}
    DROPBOX_APP_SECRET: ${{ secrets.DROPBOX_APP_SECRET }}
    DROPBOX_REFRESH_TOKEN: ${{ secrets.DROPBOX_REFRESH_TOKEN }}
```

# Setup PostgresDB:

1) Docker Pull Postgres:

`docker pull postgres`

2) Create Persistent Volumn for Postgres:

`docker volume create postgres-data`

3) Create Postgres Container:

`docker run --name postgres-container -e POSTGRES_PASSWORD=password -p 5432:5432 -v postgres-data:/var/lib/postgresql/data -d postgres`

4) Access Postgres DB:

`docker exec -it postgres-container psql -U postgres`

5) Setup Airflow DB in Postgres

```bash
CREATE DATABASE airflow_db;
CREATE USER airflow_user WITH PASSWORD 'airflow_pass';
GRANT ALL PRIVILEGES ON DATABASE airflow_db TO airflow_user;
```

# Setup Airflow:

4) Build Airflow Environment: 

`/usr/local/opt/python@3.7/bin/python3 -m venv airflow_env`

5) Start Airflow Environment:
  
`source airflow_env/bin/activate`
`pip install --upgrade pip`

3) Install Neccessary Packages:

`pip install apache-airflow`
`pip install apache-airflow-providers-celery`
`pip install psycopg2`

4) Initialize Airflow DB

`airflow db init`

5) Go to airflow directory at the Home Directory

`cd [Home Directory]/airflow`

6) Config Airflow: 

Go to ~/airflow

Change airflow.cfg

* change `dags_folder` to the directory where dags.py are located
* change `sql_alchemy_conn` to `postgresql+psycopg2://airflow_user:airflow_pass@localhost/airflow_db`
* change `executor` to CeleryExecutor


7) Run againt db init

`airflow db init`

7) Add User to airflow: 

`airflow users create --username jeffrey --password password --firstname jeffrey --lastname lin --role Admin --email jeffrey82221@icloud.com`

`airflow users list`

8) Start airflow scheduler 

`airflow scheduler`

9) Start a new terminal and start the webserver: 

`source airflow_env/bin/activate`

`airflow webserver`

9) Go to the browser and search http://localhost:8080/home

username: admin 
password: password




