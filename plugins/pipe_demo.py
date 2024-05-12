import os
import threading

def read(r):
    print('read waiting pipe input start')
    data = os.fdopen(r, 'r').read()
    print(data)
    print('read pipe input done')

def write(w):
    txt = 'hello world'
    print('write pipe input start')
    os.fdopen(w, 'w').write(txt)
    print('write pipe input done')

r, w = os.pipe()
read_thread =  threading.Thread(target=read, args=(r, ))
read_thread.start()

write_thread = threading.Thread(target=write, args=(w, ))
write_thread.start()

read_thread.join()
write_thread.join()



