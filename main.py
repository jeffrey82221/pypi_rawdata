"""
Statistics at my mac mini:

worker=1 with count 8192 => 2~3 hr ~ 100 KB / s
worker=4 with count 8192 => 30 min
worker=16 with count 8192 => 10 min ~ 10 MB / s
worker=64 with count 8192 => 5 min ~ 20 MB / s

=> Best number of worker=32 
"""
from src import SimplePyPiCanonicalize
from batch_framework.filesystem import DropboxBackend
etl_obj = SimplePyPiCanonicalize(
    raw_df=DropboxBackend('/data/canon/raw/'),
    tmp_fs=DropboxBackend('/data/canon/tmp/'),
    output_fs=DropboxBackend('/data/canon/output/'),
    partition_fs=DropboxBackend('/data/canon/partition/'),
    download_worker_count=64,
    update_worker_count=1,
    # test_count=8192,
    do_update=True
)
if __name__ == '__main__':
    etl_obj.execute()
    