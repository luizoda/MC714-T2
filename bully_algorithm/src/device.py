import grpc
from concurrent import futures
from threading import Thread, Condition
import time
import os
import random

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
        self.running_election = False
        self.coordinator: int = None
        self.running_election_mutex = Condition()
        self.coordinator_mutex = Condition()
        logger.info("Test logging")

    def run(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
        mensagem_pb2_grpc.add_BullyServicer_to_server(self, server)
        server.add_insecure_port(f"[::]:{self.port}")
        server.start()
        thread = Thread(target = self.define_coordinator_for_device)
        thread.start()
        server.wait_for_termination()

    def check_coordinator_status(self):
        logger.info(f"Checking status of coordinator {self.coordinator}")
        try:
            port = port_from_i32(self.coordinator)
            stub = BullyStub(grpc.insecure_channel(port))
            stub.Ok(IdRequest(id = self.id), timeout = 5)
        except:
            logger.info(f"Failed to check status of coordinator {self.coordinator}")
            self.coordinator = None
            time.sleep(1)

    def define_coordinator_for_device(self):
        while True:
            self.coordinator_mutex.acquire()
            if self.coordinator is None:
                time.sleep(1)
                self.coordinator_mutex.notify()
                self.coordinator_mutex.release()
                thread = Thread(target = self.run_election)
                thread.start()
            elif self.coordinator != self.id:
                self.check_coordinator_status()
                self.coordinator_mutex.notify()
                self.coordinator_mutex.release()
                time.sleep(1)
            else:
                self.coordinator_mutex.notify()
                self.coordinator_mutex.release()

    def run_election(self):
        self.running_election_mutex.acquire()
        self.running_election = True
        self.running_election_mutex.notify()
        self.running_election_mutex.release()

        received_response = False

        for i in range(self.id + 1, 5):
            try:
                port = port_from_i32(i)
                stub = BullyStub(grpc.insecure_channel(port))
                stub.Election(IdRequest(id = self.id), timeout = 5)
                received_response = True
            except:
                pass
        
        logger.info(f"ran election for {self.id}, received response = {received_response}")

        if received_response:
            time.sleep(5)
        else:
            self.coordinator_mutex.acquire()
            self.coordinator = self.id
            self.coordinator_mutex.notify()
            self.coordinator_mutex.release()
            for i in range(1, 5) :
                if i == self.id:
                    continue
                try:
                    port = port_from_i32(i)
                    stub = BullyStub(grpc.insecure_channel(port))
                    logger.info("send victory message")
                    stub.Victory(IdRequest(id = self.id), timeout = 5)
                    logger.info(f"{self.id} is coordinator")
                except:
                    pass


        self.running_election_mutex.acquire()
        self.running_election = False
        self.running_election_mutex.notify()
        self.running_election_mutex.release()
    
    def Election(self, request: IdRequest, context):
        logging.info(f"{self.id} received election message from {request.id}")
        self.running_election_mutex.acquire()
        if self.running_election == False:
            self.running_election = True
            self.running_election_mutex.notify()
            self.running_election_mutex.release()
            thread = Thread(target=self.run_election)
            thread.start()
        else:
            self.running_election_mutex.notify()
            self.running_election_mutex.release()
        return IdResponse()
            
    def Alive(self, request: IdRequest, context):
        logger.info(f"{self.id} received alive message from {request.id}")
        return IdResponse()

    def Victory(self, request: IdRequest, context):
        logger.info(f"{self.id} received victory message from {request.id}")
        self.coordinator_mutex.acquire()
        self.coordinator = request.id
        self.coordinator_mutex.notify()
        self.coordinator_mutex.release()
        return IdResponse()

    def Ok(self, request: IdRequest, context):
        logger.info(f"{self.id} received ok message from {request.id}")
        return IdResponse()

if __name__ == "__main__":
    cur_id = int(os.environ.get("ID"))
    port = os.environ.get("PORT")
    service = Device(cur_id, port)
    service.run()