from src import SimplePyPiCanonicalize
from batch_framework.filesystem import DropboxBackend


etl_obj = SimplePyPiCanonicalize(
    raw_df=DropboxBackend('/data/canon/raw/'),
    tmp_fs=DropboxBackend('/data/canon/tmp/'),
    output_fs=DropboxBackend('/data/canon/output/'),
    partition_fs=DropboxBackend('/data/canon/partition/'),
    download_worker_count=32,
    update_worker_count=8,
    do_update=True
)

if __name__ == '__main__':
    etl_obj.execute()
