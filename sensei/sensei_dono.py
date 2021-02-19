import pickle
import os
import logging
from copy import deepcopy
from pprint import pprint

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

        self.SNAPSHOTS = os.path.join(os.path.dirname(os.path.realpath(__file__)), 
                                 "snapshots")

        self.files = {}
        self.chunk_locations = {}

        self.load_snapshot()

    def save_snapshot(self):
        """Save snaphot of filesystem to a file (temporary). 
        Later change to save to backup server.
        Also change to save snapshot periodically.
        """

        log.info("Saving snapshot...")

        snapshot1 = os.path.join(self.SNAPSHOTS, "snapshot1.dat")

        with open(snapshot1, "wb") as f:
            pickle.dump(self.files, f)

    def load_snapshot(self):
        """Loads snapshot of a filesystem from a file.
        Later change to load from server.
        Load only after the server is down.
        """

        log.info("Loading snapshot...")

        snapshot1 = os.path.join(self.SNAPSHOTS, "snapshot1.dat")

        if os.path.exists(snapshot1):
            with open(snapshot1, "rb") as f:
                self.files = pickle.load(f)

    def exposed_create_namespaces(self, path, directory):
        log.info(f"Creating directory '{directory}' on path {path}")

        self.files[path+directory] = {}
        
        return True

    def exposed_get_namespaces(self, path="/"):
        return [ns for ns in self.files.keys() if not ns.startswith('/hidden')]

    def exposed_remove_namespaces(self, path):
        for ns in self.files.keys():
            if ns.startswith(path) and not ns.startswith('/hidden'):
                self.files['/hidden' + ns] = self.files[ns]
                del self.files[ns]

    def exposed_exists(self, path):
        return path in self.files

    # temp
    def collect_garbage(self):
        log.info("Collecting garbage...")
        for key in [key for key in self.files if key.startswith('/hidden')]:
            del self.files[key]

    def on_disconnect(self, conn):
        pprint(self.files)
        self.collect_garbage()
        self.save_snapshot()


if __name__=="__main__":
    server = ThreadedServer(SenseiService(), port=33333)
    server.start()
