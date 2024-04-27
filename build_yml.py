"""
Build ETL.yml into github action
"""
from src import SimplePyPiCanonicalize
from batch_framework.adaptor import GithubActionAdaptor
from batch_framework.filesystem import DropboxBackend

if __name__ == '__main__':
    etl_obj = SimplePyPiCanonicalize(
        raw_df=DropboxBackend('/data/canon/raw/'),
        tmp_fs=DropboxBackend('/data/canon/tmp/'),
        output_fs=DropboxBackend('/data/canon/output/'),
        partition_fs=DropboxBackend('/data/canon/partition/'),
        download_worker_count=8,
        update_worker_count=8,
        test_count=100,
        do_update=True
    )
    adaptor = GithubActionAdaptor(etl_group=etl_obj)
    adaptor.create_yml(
        job_yml_path='./.github/workflows/job.yml',
        template_yml_path='./template.yml',
        target_yml_path='./.github/workflows/etl.yml'
    )