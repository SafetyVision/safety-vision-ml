import threading
import time

def print_hi():
    while(True):
        time.sleep(2)
        print('hi')


thr = threading.Thread(target=print_hi)
thr.start()
while(True):
    print('yo')
    time.sleep(2)