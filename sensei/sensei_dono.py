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

logging.getLogger("SENSEI/33333").propagate = False


class SenseiService(rpyc.Service):
    """This service is used for storing metadata of file namespaces and
    location of replicas of file blocks.

    It also contains methods to communicate with client and
    give instructions to chunk servers.
    """

    def __init__(self):
        log.debug("Creating sensei object")

        self.SNAPSHOTS = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "snapshots"
        )

        self.files = {}
        self.chunk_locations = {}
        self.chunk_servers = {
            ("localhost", 40001): {"chunks": 0},
            ("localhost", 40002): {"chunks": 0},
            ("localhost", 40003): {"chunks": 0},
            ("localhost", 40004): {"chunks": 0},
        }

        # self.chunk_size = 64_000_000
        self.chunk_size = 500
        self.replica_factor = 3

        self.load_snapshot()

    def get_chunk(self, ip, port):
        try:
            return rpyc.connect(ip, port).root
        except ConnectionRefusedError:
            log.error("Chunk refused connection")

    def diagnostic(self):
        log.info("Chunk servers diagnostic")

        for chunk in self.chunk_servers:
            chunk_server = self.get_chunk(*chunk)
            state = chunk_server.get_state()

            self.chunk_servers[chunk].update({a:state[a] for a in list(state)})

    def save_snapshot(self):
        """Save snaphot of filesystem to a file (temporary).
        Later change to save to backup server.
        Also change to save snapshot periodically.
        """

        log.info("Saving snapshot...")

        snapshot1 = os.path.join(self.SNAPSHOTS, "snapshot1.dat")

        with open(snapshot1, "wb") as f:
            pickle.dump((self.files, self.chunk_locations), f)

    def load_snapshot(self):
        """Loads snapshot of a filesystem from a file.
        Later change to load from server.
        Load only after the server is down.
        """

        log.info("Loading snapshot...")

        snapshot1 = os.path.join(self.SNAPSHOTS, "snapshot1.dat")

        if os.path.exists(snapshot1):
            with open(snapshot1, "rb") as f:
                self.files, self.chunk_locations = pickle.load(f)

    def valid_path(self, path):
        if path.count("//") > 0:
            return False

        return True
    
    def alloc_chunks(self, num):
        log.info("Allocating chunks")

        chunk_servers = sorted(self.chunk_servers, 
                               key=lambda x: self.chunk_servers[x]["chunks"])
        
        return chunk_servers[:num]

    def exposed_get_chunk_size(self):
        return self.chunk_size

    def exposed_write_file(self, path, size):
        log.info(f"Write file on path {path} with size {size}")

        self.exposed_create_directory(path, force=True)

        # add chunkuuids for each chunk
        for i in range(math.ceil(size/self.chunk_size)):
            chunk_uuid = uuid.uuid1()

            log.debug(f"Chunk index: {i}\n Chunk uuid: {chunk_uuid}")

            self.files[path][i] = chunk_uuid
            self.chunk_locations[chunk_uuid] = \
                self.alloc_chunks(self.replica_factor)

        return self.files[path].values()

    def exposed_read_file(self, path, chunk_index=-1):
        if chunk_index == -1:
            return self.files[path]
        else:
            return {chunk_index: self.files[path][chunk_index]}

    def exposed_get_chunk_location(self, chunks_uuid):
        log.info("Getting chunk locs")
        
        chunks_locs = {ch: self.chunk_locations[ch] for ch in chunks_uuid}

        return chunks_locs

    def exposed_create_directory(self, path, force=False):
        log.info(f"Creating directory {path}")

        if force:
            self.exposed_remove_namespaces(path)

        if not self.valid_path(path) or path.rstrip("/") in self.files:
            return None

        self.files[path.rstrip("/")] = {}
        return path.rstrip("/")

    def exposed_get_namespaces(self, path="/"):
        return [
            ns for ns in self.files.keys()
            if not ns.startswith("/hidden") and ns.startswith(path.rstrip("/") + "/")
        ]

    def exposed_remove_namespaces(self, path):
        log.info(f"Removing namespace {path}")

        for ns in [key for key in self.files]:
            if ns.startswith(path) and not ns.startswith("/hidden"):
                name = "/hidden" + ns + datetime.today().strftime("-%Y-%m-%d")
                self.files[name] = self.files[ns]
                del self.files[ns]

    def exposed_exists(self, path):
        return path in self.files

    # temp
    def collect_garbage(self):
        log.info("Collecting garbage...")

        for key in [key for key in self.files if key.startswith("/hidden")]:
            log.info(f"Deleting {key}...")

            for chunk in self.files[key].values():
                del self.chunk_locations[chunk]

            del self.files[key]

    def on_disconnect(self, conn):
        log.info("♦♦♦♦♦♦♦♦♦♦DISCONNECTION♦♦♦♦♦♦♦♦♦♦")

        # self.diagnostic()
        self.collect_garbage()
        self.save_snapshot()

        pprint(self.files)
        pprint(self.chunk_locations)
        pprint(self.chunk_servers)


if __name__ == "__main__":
    server = ThreadedServer(SenseiService(), port=33333)
    server.start()