import os
import io
from fsspec.implementations.dirfs import DirFileSystem
import tqdm
import base64
from split_file_reader.split_file_writer import SplitFileWriter
from split_file_reader import SplitFileReader
from concurrent.futures import ThreadPoolExecutor
from batch_framework.filesystem import DropboxBackend

__all__ = ['NewDropboxBackend']
    
class NewDropboxBackend(DropboxBackend):
    def _upload_core(self, file_obj: io.BytesIO, remote_path: str):
        """Upload file object to local storage

        Args:
            file_obj (io.BytesIO): file to be upload
            remote_path (str): remote file path
        """
        assert '.' in remote_path, f'requires file ext .xxx provided in `remote_path` but it is {remote_path}'
        file_name = remote_path.split('.')[0]
        ext = remote_path.split('.')[1]
        if self._fs.exists(file_name):
            self._fs.rm(file_name)
        self._fs.mkdir(file_name)
        assert self._fs.exists(file_name), f'{file_name} folder make failed'
        dfs = DirFileSystem(f'/{file_name}', self._fs)

        chunks = []
        def gen(lst):
            while True:
                lst.append(io.BytesIO())
                yield lst[-1]
        file_obj.seek(0)
        with SplitFileWriter(gen(chunks), 1000000) as sfw:
            sfw.write(file_obj.getbuffer())
        # total_size = len(chunks)
        # print('number of chunks:', total_size)
        with ThreadPoolExecutor(max_workers=8) as executor:
            input_pipe = enumerate(chunks)
            input_pipe = map(lambda x: (dfs, x[0], ext, x[1]), input_pipe)
            output_pipe = executor.map(self._upload_chunk, input_pipe)
            output = list(tqdm.tqdm(output_pipe, desc=f'Upload {remote_path}'))
        total_size = len(output)
        print('number of chunks:', total_size)
        with dfs.open('total.txt', 'w') as f:
            f.write(str(total_size))
        print(f'Done upload {total_size} files')
    
    def _upload_chunk(self, x):
        dfs, index, ext, chunk = x
        chunk.seek(0)
        with dfs.open(f'{index}.{ext}', 'w') as f:
            data = base64.b64encode(chunk.read()).decode()
            f.write(data)

    def download_core(self, remote_path: str) -> io.BytesIO:
        """Download file from remote storage

        Args:
            remote_path (str): remote file path

        Returns:
            io.BytesIO: downloaded file
        """
        assert '.' in remote_path, f'requires file ext .xxx provided in `remote_path` but it is {remote_path}'
        file_name = remote_path.split('.')[0]
        ext = remote_path.split('.')[1]
        assert self._fs.exists(
            f'{file_name}'), f'{file_name} folder does not exists for FileSystem: {self._fs}'
        dfs = DirFileSystem(file_name, self._fs)
        with dfs.open('total.txt', 'r') as f:
            total_size = int(f.read())
        print(f'Start download {total_size} files')
        with ThreadPoolExecutor(max_workers=4) as executor:
            input_pipe = range(total_size)
            input_pipe = map(lambda x: (dfs, x, ext), input_pipe)
            chunks = executor.map(self._download_chunk, input_pipe)
            chunks = list(tqdm.tqdm(chunks, 
                                    desc=f'Download {remote_path}',
                                    total=total_size
                                    ))
            with SplitFileReader(chunks) as sfw:
                result = io.BytesIO(sfw.read())
            result.seek(0)
        print(f'Done download {total_size} files')
        return result
        
    def _download_chunk(self, x):
        dfs, index, ext = x
        with dfs.open(f'{index}.{ext}', 'r') as f:
            chunk = io.BytesIO(base64.b64decode(f.read()))
        return chunk