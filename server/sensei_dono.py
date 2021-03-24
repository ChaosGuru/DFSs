import pickle
import os
import logging
import math
import uuid
from copy import deepcopy
from pprint import pprint
from datetime import datetime

import rpyc
from rpyc.utils.server import ThreadedServer

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("sensei-dono")

# logging.getLogger("SENSEI/33333").propagate = False


class SenseiService(rpyc.Service):
    """This service is used for storing metadata of file namespaces and
    location of replicas of file blocks.

    It also contains methods to communicate with client and
    give instructions to chunk servers.
    """

    def __init__(self):
        log.debug("Creating sensei object")

        self.snapshots_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "snapshots"
        )

        self.namespaces = {}
        self.chunk_locations = {}
        self.chunk_servers = {}

        self.chunk_size = 1000 # 64_000_000 
        self.replica_factor = 3

        self.load_snapshot()

    def save_snapshot(self):
        """Save snaphot of filesystem to a file (temporary).
        Later change to save to backup server.
        Also change to save snapshot periodically.
        """

        log.info("Saving snapshot...")

        snapshot1 = os.path.join(self.snapshots_path, "snapshot1.dat")

        with open(snapshot1, "wb") as f:
            pickle.dump((self.namespaces, self.chunk_locations), f)

    def load_snapshot(self):
        """Loads snapshot of a filesystem from a file.
        Later change to load from server.
        Load only after the server is down.
        """

        log.info("Loading snapshot...")

        snapshot1 = os.path.join(self.snapshots_path, "snapshot1.dat")

        if os.path.exists(snapshot1):
            with open(snapshot1, "rb") as f:
                self.namespaces, self.chunk_locations = pickle.load(f)


    # methods for client communication
    def valid_path(self, path):
        if path.count("//") > 0:
            return False

        return True
    
    def alloc_chunks(self, num):
        log.info("Allocating chunks")

        chunk_servers = sorted(
            self.chunk_servers, 
            key=lambda x: self.chunk_servers[x]["chunks"])

        return chunk_servers[:num]

    def exposed_get_chunk_size(self):
        return self.chunk_size

    def exposed_write_file(self, path, size, force=False):
        log.info(f"Write file on path {path} with size {size}")

        if not self.exposed_create_directory(path, force):
            return None

        num_of_chunks = math.ceil(size/self.chunk_size)

        for i in range(num_of_chunks):
            chunk_uuid = uuid.uuid4()

            log.debug(f"Chunk index: {i}\n Chunk uuid: {chunk_uuid}")

            self.namespaces[path][i] = chunk_uuid

        return self.namespaces[path].values()

    def exposed_read_file(self, path, chunk_index=-1):
        if chunk_index == -1:
            return self.namespaces[path]
        else:
            return {chunk_index: self.namespaces[path][chunk_index]}

    def exposed_get_chunk_location(self, chunk_uuid):
        log.info("Getting chunk locs")

        live_locations = self.chunk_locations.get(chunk_uuid, None)
        
        if not live_locations:
            self.chunk_locations[chunk_uuid] = self.alloc_chunks(
                self.replica_factor)
        elif len(live_locations) != 3:
            self.alloc_chunks(self.replica_factor-live_locations)

        return self.chunk_locations[chunk_uuid]

    def exposed_create_directory(self, path, force=False):
        log.info(f"Creating directory {path}")

        if (not force and path in self.namespaces) \
                or not self.valid_path(path):
            return None

        self.exposed_remove_namespace(path)

        self.namespaces[path] = {}
        return path

    def exposed_get_namespaces(self, path):
        log.info(f"Getting namaspaces for {path}")
        
        return [
            ns for ns in self.namespaces.keys()
                if not ns.startswith("/hidden") \
                    and ns.startswith(path)
        ]

    def exposed_remove_namespace(self, path):
        log.info(f"Removing namespace {path}")
        count = 0

        for ns in [key for key in self.namespaces]:
            if ns.startswith(path) and not ns.startswith("/hidden"):
                name = "/hidden" + ns + datetime.today().strftime("-%Y-%m-%d")
                self.namespaces[name] = self.namespaces[ns]
                del self.namespaces[ns]
                count += 1

        return count

    def exposed_exists(self, path):
        log.info(f"Check if exists {path}")

        return path in self.namespaces

    # methods for chunk communication
    def exposed_register_chunk_server(self, port, num_of_chunks):
        log.info(f"New chunk server with port {port}, chunks {num_of_chunks}")

        self.chunk_servers[('localhost', port)] = {'chunks': num_of_chunks}

    def exposed_update_chunk_data(self, port, num_of_chunks):
        log.debug(f"Chunk server {port} updates its data")

        self.chunk_servers[('localhost', port)]['chunks'] = num_of_chunks

    def get_chunk(self, ip, port):
        try:
            return rpyc.connect(ip, port).root
        except ConnectionRefusedError:
            log.error("Chunk refused connection")

    def diagnostic(self):
        pass
    

    # temp
    def collect_garbage(self):
        log.info("Collecting garbage...")

        for key in [key for key in self.namespaces if key.startswith("/hidden")]:
            log.info(f"Deleting {key}...")

            for chunk in self.namespaces[key].values():
                del self.chunk_locations[chunk]

            del self.namespaces[key]

    def on_connect(self, conn):
        pass

    def on_disconnect(self, conn):
        # self.diagnostic()
        self.collect_garbage()
        self.save_snapshot()


if __name__ == "__main__":
    server = ThreadedServer(SenseiService(), port=33333)
    server.start()