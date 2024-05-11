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

# How to initialize the Data First Time ?

- [ ] Using `LocalBackend` in main.py to locally store and run the data flow.
    - [ ] First Run:
        - [ ] Make sure small `test_count` works.
        - [ ] Set up large `download_worker_count` and remove `test_count` to download all data and process them fast.
    - [ ] Second run:
        - [ ] Set up large `update_worker_count` and update the data fast.


# How to setup day 2 data flow in github action?

- [ ] Migrade all data to DropBox using `migrade.py`
- [X] Run build_yml.py 
    - [X] Follow the instruction step in the pop-up browser and Enter the dropbox_access_token obtained from the browser.
    - [X] A DROPBOX_REFRESH_TOKEN.ini file will be created. Make sure it is added into .gitignore
    - [X] Check that etl.yml is also be added into .github/workflows/
- [X] Add `run_task.py` to Repo and connect it with the ETLGroup object.
- [X] Add the following secrets to the github REPO

```yml
    DROPBOX_APP_KEY: ${{ secrets.DROPBOX_APP_KEY }}
    DROPBOX_APP_SECRET: ${{ secrets.DROPBOX_APP_SECRET }}
    DROPBOX_REFRESH_TOKEN: ${{ secrets.DROPBOX_REFRESH_TOKEN }}
```
- [ ] Locally Test the Dropbox works for the data flow
    - [ ] Change all `LocalBackend` to `DropboxBackend`
    - [ ] git push the `etl.yml` generated to Github.
    - [ ] Check if the Github Action run succesfully.

