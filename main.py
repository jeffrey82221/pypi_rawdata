"""
Statistics at my mac mini:

worker=1 with count 8192 => 2~3 hr ~ 100 KB / s
worker=4 with count 8192 => 30 min
worker=16 with count 8192 => 10 min ~ 10 MB / s
worker=64 with count 8192 => 5 min ~ 20 MB / s

=> Best number of worker=32 

TODO: Setup First Run and Migrade to the Cloud 

- [X] Build first Run python file
- [X] Build migrate data python file 
- [X] Build incremental run python file
- [ ] Build incremental run etl.yml
"""
from src import SimplePyPiCanonicalize
from batch_framework.filesystem import DropboxBackend
from batch_framework.filesystem import LocalBackend

def get_etl_obj(mode='incremental', local=False, test_count=64):
    assert mode in ['test', 'first_run', 'incremental']
    if mode in ['first_run', 'test']:
        assert local, 'must run first_run or test locally'
    if not local:
        assert mode == 'incremental'
        etl_obj = SimplePyPiCanonicalize(
            tmp_fs=DropboxBackend('/data/canon/tmp/'),
            partition_fs=DropboxBackend('/data/canon/partition/'),
            raw_df=DropboxBackend('/data/canon/raw/'),
            download_worker_count=1,
            update_worker_count=64,
            do_update=True
        )
    else:
        if mode == 'test':
            etl_obj = SimplePyPiCanonicalize(
                tmp_fs=LocalBackend('data/canon/tmp/'),
                partition_fs=LocalBackend('data/canon/partition/'),
                raw_df=LocalBackend('data/canon/raw/'),
                download_worker_count=8, # FIRST RUN: 64,
                update_worker_count=8,
                test_count=test_count,
                do_update=True
            )
        elif mode == 'first_run':
            etl_obj = SimplePyPiCanonicalize(
                tmp_fs=LocalBackend('data/canon/tmp/'),
                partition_fs=LocalBackend('data/canon/partition/'),
                raw_df=LocalBackend('data/canon/raw/'),
                download_worker_count=64, # FIRST RUN: 64,
                update_worker_count=64,
                do_update=False
            )
        elif mode == 'incremental':
            etl_obj = SimplePyPiCanonicalize(
                tmp_fs=LocalBackend('data/canon/tmp/'),
                partition_fs=LocalBackend('data/canon/partition/'),
                raw_df=LocalBackend('data/canon/raw/'),
                download_worker_count=64,
                update_worker_count=64,
                do_update=True
            )
    return etl_obj

def migrate_data():
    import os
    for folder in ['raw', 'tmp']:
        local_fs = LocalBackend(f'./data/canon/{folder}/')
        dropbox_fs = DropboxBackend(f'/data/canon/{folder}/')
        for file in os.listdir(f'./data/canon/{folder}/'):
            print('folder:', folder, 'file:', file, 'upload started')
            buff = local_fs.download_core(file)
            buff.seek(0)
            dropbox_fs.upload_core(buff, file)
            print('folder:', folder, 'file:', file, 'uploaded')


if __name__ == '__main__':
    # get_etl_obj(mode='debug', local=True).execute()
    # get_etl_obj(mode='first_run', local=True).execute()
    # get_etl_obj(mode='incremental', local=True).execute()
    # migrate_data()
    get_etl_obj(mode='incremental', local=False).execute()