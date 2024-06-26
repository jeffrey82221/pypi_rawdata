"""
Build ETL.yml into github action
"""
from main import get_etl_obj
from batch_framework.adaptor import GithubActionAdaptor

if __name__ == '__main__':
    etl_obj = get_etl_obj(mode='incremental', local=False)
    adaptor = GithubActionAdaptor(etl_group=etl_obj)
    adaptor.create_yml(
        job_yml_path='./.github/workflows/job.yml',
        template_yml_path='./template.yml',
        target_yml_path='./.github/workflows/etl.yml'
    )
