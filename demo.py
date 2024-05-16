"""
Demo pipe-based etl system
"""
from plugins.demo_dropbox_backend import NewDropboxBackend
from batch_framework.filesystem import LocalBackend


def migrate_data():
    import os
    for folder in ['raw']:
        local_fs = LocalBackend(f'./data/canon/{folder}/')
        dropbox_fs = NewDropboxBackend(f'/data/demo/{folder}/')
        for file in os.listdir(f'./data/canon/{folder}/'):
            print('folder:', folder, 'file:', file, 'upload started')
            buff = local_fs.download_core(file)
            buff.seek(0)
            dropbox_fs.upload_core(buff, file)
            print('folder:', folder, 'file:', file, 'uploaded')


if __name__ == '__main__':
    migrate_data()
    