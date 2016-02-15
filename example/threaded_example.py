"""
Experimenting with threads and pydisque.

It could be entirely possible that pydisque or a subset of
it's sublibraries are not thread safe, this should help
test that.
"""
import json
import time
import logging
import random
import threading
# logging.basicConfig(level=logging.DEBUG)

from pydisque.client import Client

PRODUCER_THREADS=4
CONSUMER_THREADS=4
SHARED_QUEUE="threadTest.%d" % time.time()

class consumerThread(threading.Thread):
    def __init__(self, client, identifier):
        self._client = client
        self._identifier = identifier
        self._running = True
        threading.Thread.__init__(self)

    def run(self):
        while self._running:
            jerb = self._client.get_job([SHARED_QUEUE])
            print(jerb)

class producerThread(threading.Thread):
    def __init__(self, client, identifier):
        self._client = client
        self._identifier = identifier
        self._running = True
        threading.Thread.__init__(self)

    def run(self):
        while(self._running):
            self._client.add_job(SHARED_QUEUE,
                                "%d-%d" % (self._identifier, time.time()),
                                replicate=1, timeout=100)

def main():

    client = Client(['localhost:7711'])
    client.connect()

    for i in range(0, PRODUCER_THREADS):
        pt = producerThread(client, i)
        pt.start()

    for i in range(0, CONSUMER_THREADS):
        ct = consumerThread(client, i)
        ct.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        sys.quit()

if __name__ == "__main__":
        main()
