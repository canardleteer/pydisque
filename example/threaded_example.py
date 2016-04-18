"""
Experimenting with threads and pydisque.

It could be entirely possible that pydisque or a subset of
it's sublibraries are not thread safe, but so far things
appear to be solid.

Leaving the queue PAUSE stuff out for now, we really don't
support it in the main lib properly.

TODO:
    DisqueThread superclass
    Really need to detect PAUSED queues better then ResponseError
    Manage threads and exiting better
"""
import sys
import json
import time
import logging
import random
import threading
# logging.basicConfig(level=logging.DEBUG)

from pydisque.client import Client, QueuePausedException

# TODO: get rid of this requirement in the main lib
from redis.exceptions import ResponseError

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
            try:
                jerb = self._client.get_job([SHARED_QUEUE])
                print(jerb)
            except ResponseError:
                print(
                    "consumer #%d: Queue paused, skipping." % self._identifier)
            time.sleep(0.1)

class producerThread(threading.Thread):
    def __init__(self, client, identifier):
        self._client = client
        self._identifier = identifier
        self._running = True
        threading.Thread.__init__(self)

    def run(self):
        while(self._running):
            try:
                self._client.add_job(SHARED_QUEUE,
                                    "%d-%d" % (self._identifier, time.time()),
                                    replicate=1, timeout=100)
            except QueuePausedException as e:
                print("producer #%d: Queue was paused, skipping." %
                      self._identifier)
            except ResponseError:
                print(
                    "producer #%d: Queue paused, skipping." % self._identifier)
            time.sleep(0.1)

class pausingThread(threading.Thread):
    def __init__(self, client, identifier):
        self._client = client
        self._identifier = identifier
        self._running = True
        threading.Thread.__init__(self)

    def run(self):
        while(self._running):
            self._client.pause(SHARED_QUEUE, kw_all=True)
            napTimer = random.randint(0,1)
            print("Pausing for: %ds" % napTimer)
            time.sleep(napTimer)
            self._client.pause(SHARED_QUEUE, kw_none=True)

def main():

    client = Client(['localhost:7711'])
    client.connect()

    for i in range(0, PRODUCER_THREADS):
        pt = producerThread(client, i)
        pt.start()

    for i in range(0, CONSUMER_THREADS):
        ct = consumerThread(client, i)
        ct.start()

    pt = pausingThread(client, "0")
    pt.start()

    try:
        while threading.activeCount() > 0:
            time.sleep(0.1)
    except KeyboardInterrupt:
        sys.exit()

if __name__ == "__main__":
        main()
