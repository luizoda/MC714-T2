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
        self.token = False
        if self.id == 1:
            self.token = True
        self.token_mutex = Condition()
        logger.info("Test logging")

    def run(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
        mensagem_pb2_grpc.add_TokenRingServicer_to_server(self, server)
        server.add_insecure_port(f"[::]:{self.port}")
        server.start()
        thread = Thread(target = self.wait_token)
        thread.start()
        server.wait_for_termination()

    def wait_token(self):
        while True:
            self.token_mutex.acquire()
            while not self.token:
                self.token_mutex.wait()
            self.critical_section()
            self.token = False
            self.token_mutex.release()
            prox = self.id + 1
            if prox == 5:
                prox = 1
            port = port_from_i32(prox)
            stub = TokenRingStub(grpc.insecure_channel(port))
            stub.PassToken(TokenRequest(), timeout = 5)

    def critical_section(self):
        logger.info(f"{self.id} is in the critical section")
        time.sleep(random.uniform(1, 3))
        logger.info(f"{self.id} is leaving the critical section")

    def PassToken(self, request: TokenRequest, context):
        self.token_mutex.acquire()
        self.token = True
        self.token_mutex.notify()
        self.token_mutex.release()
        return TokenResponse()

if __name__ == "__main__":
    cur_id = int(os.environ.get("ID"))
    port = os.environ.get("PORT")
    service = Device(cur_id, port)
    service.run()