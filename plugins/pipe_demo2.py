import time
import threading
from typing import Iterator

class Pipe:
    """
    FIFO pipe for connecting a writing thread with 
    a reading thread
    """
    def __init__(self, max_size=8, wait_duration=0.01):
        self._max_size = max_size
        self._current_size = 0
        self._array = []
        self._index = -1
        self._on = True
        self._wait_duration = wait_duration
        self._total_size = None

    def send_input(self, input_element):
        assert self._on, 'pipe already closed'
        while self._current_size >= self._max_size:
            time.sleep(self._wait_duration)
        self._array.append(input_element)
        self._current_size += 1
    
    def generate_output(self) -> Iterator:
        while self._current_size == 0:
            time.sleep(self._wait_duration)
        while self._on or self._index < len(self._array) - 1:
            self._index += 1
            yield self._array[self._index]
            self._current_size -= 1
            while self._on and self._current_size == 0:
                time.sleep(self._wait_duration)
    
    def load_input(self, input_pipe: Iterator):
        assert self._total_size is not None
        for element in input_pipe:
            self.send_input(element)

    def __getitem__(self, idx: int):
        if idx >= self._total_size:
            raise IndexError
        self._index += 1
        assert idx == self._index
        while idx >= len(self._array):
            time.sleep(self._wait_duration)
        result = self._array[idx]
        self._current_size -= 1
        return result
    
    def set_total_size(self, count: int):
        self._total_size = count

    def __len__(self):
        while self._total_size is None:
            time.sleep(self._wait_duration)
        return self._total_size

    def close(self):
        self._on = False

def read(pipe):
    print('read start')
    # for e in pipe.generate_output():
    #     print(e)
    for i in range(len(pipe)):
        print(pipe[i])
    print('read end')

def write(pipe):
    pipe.set_total_size(19)
    for i in range(len(pipe)):
        pipe.send_input(i)
    pipe.close()

if __name__ == '__main__':
    pipe = Pipe(5)
    read_thread =  threading.Thread(target=read, args=(pipe, ))
    read_thread.start()

    write(pipe)
    read_thread.join()