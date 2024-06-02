"""
Demo pipe-based etl system
"""
from batch_framework.filesystem import LocalBackend, DropboxBackend


def migrate_data():
    import os
    for folder in ['raw']:
        local_fs = LocalBackend(f'./data/canon/{folder}/')
        dropbox_fs = DropboxBackend(f'/data/demo/{folder}/')
        for file in os.listdir(f'./data/canon/{folder}/'):
            print('folder:', folder, 'file:', file, 'upload started')
            buff = local_fs.download_core(file)
            buff.seek(0)
            dropbox_fs.upload_core(buff, file)
            print('folder:', folder, 'file:', file, 'uploaded')


if __name__ == '__main__':
    migrate_data()
    