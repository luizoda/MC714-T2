import grpc
from concurrent import futures
from threading import Thread, Condition
import time
import random
import os

from proto import mensagem_pb2
from proto import mensagem_pb2_grpc

from proto.mensagem_pb2 import *
from proto.mensagem_pb2_grpc import *

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

os.environ["GRPC_VERBOSITY"] = "ERROR"

def port_from_i32(i: int) -> str:
    return f"localhost:5005{i}"

class Device():
    def __init__(self, id: int, port: str):
        self.id = id
        self.port = port
        self.timestamp = 0
        self.timestamp_mutex = Condition()
        logger.info("Test logging")

    def run(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
        mensagem_pb2_grpc.add_ClockServicer_to_server(self, server)
        server.add_insecure_port(f"[::]:{self.port}")
        server.start()
        thread = Thread(target = self.events)
        thread.start()
        server.wait_for_termination()

    def events(self):
        while True:
            time.sleep(random.uniform(5, 10))
            random_number_of_internal_events = random.randint(0, 3)
            for _ in range(random_number_of_internal_events):
                self.internal_event()
            self.event_happen()

    def event_happen(self):
        self.timestamp_mutex.acquire()
        self.timestamp = self.timestamp + 1
        cur_time = self.timestamp
        self.timestamp_mutex.notify()
        self.timestamp_mutex.release()

        for i in range(1, 5) :
                if i == self.id:
                    continue
                try:
                    port = port_from_i32(i)
                    stub = ClockStub(grpc.insecure_channel(port))
                    stub.Time(TimeRequest(timestamp = cur_time), timeout = 5)
                    logger.info(f"{self.id} sent timestamp to {i}")
                except:
                    pass

    def internal_event(self):
        self.timestamp_mutex.acquire()
        self.timestamp = self.timestamp + 1
        self.timestamp_mutex.notify()
        self.timestamp_mutex.release()

    def Time(self, request: TimeRequest, context):
        self.timestamp_mutex.acquire()
        if request.timestamp > self.timestamp:
            self.timestamp = request.timestamp
            logger.info(f"{self.id} time set to {request.timestamp}")
        else:
            self.timestamp = self.timestamp + 1
        self.timestamp_mutex.notify()
        self.timestamp_mutex.release()
        return TimeResponse()

if __name__ == "__main__":
    cur_id = int(os.environ.get("ID"))
    port = os.environ.get("PORT")
    service = Device(cur_id, port)
    service.run()