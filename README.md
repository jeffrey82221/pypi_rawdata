# pypi_rawdata
Crawling Data From PyPi


# How to set up batchwise update framework? 

- [ ] Add .github/workflows/job.yml into the Repo
- [ ] Add requirements.txt that install batch-framework
- [ ] Run requirements.txt using `pip install -r requirements.txt`
- [ ] Create src/ with classes inheriting batch_framework ETLBase

- [ ] Add the following secrets to the REPO

```yml
    DROPBOX_APP_KEY: ${{ secrets.DROPBOX_APP_KEY }}
    DROPBOX_APP_SECRET: ${{ secrets.DROPBOX_APP_SECRET }}
    DROPBOX_REFRESH_TOKEN: ${{ secrets.DROPBOX_REFRESH_TOKEN }}
```