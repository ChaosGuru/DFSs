import pickle
import os
import logging
from copy import deepcopy

import rpyc
from rpyc.utils.server import ThreadedServer

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("sensei-dono")

logging.getLogger("SENSEI/33333").propagate = False


class SenseiService(rpyc.Service):
    def __init__(self):
        log.debug("Creating sensei object")

        # 1D dict because for oprimization for large files !! make a report
        self.files = {}
        self.chunk_locations = {}

        self.load_snapshot()

        from pprint import pprint
        pprint(self.files)

    def save_snapshot(self):
        log.info("Saving snapshot...")

        # temporary solution, change to another folder and servers
        data_path = os.path.dirname(os.path.realpath(__file__))

        snapshots_path = os.path.join(data_path, "snapshots")
        snapshot1 = os.path.join(snapshots_path, "snapshot1.dat")

        with open(snapshot1, "wb") as f:
            pickle.dump(self.files, f)

    def load_snapshot(self):
        log.info("Loading snapshot...")

        data_path = os.path.dirname(os.path.realpath(__file__))
        snapshot1 = os.path.join(data_path, "snapshots", "snapshot1.dat")

        with open(snapshot1, "rb") as f:
            self.files = pickle.load(f)

    def load_chunks(self):
        # rewrite to load from logs

        self.filename_chunks = {
            "users/oleg/my_folder/file1.txt": "some code",
        }

    def get_path_obj(self, path):
        path_dirs = list(filter(None, path.split("/")))
        obj = self.files

        try:
            for directory in path_dirs:
                obj = obj[directory]
        except KeyError:
            return None

        return obj

    def valid_name(self, name):
        if isinstance(name, str):
            return True
        
        return False
    
    def get_dict_from_path(self, path):
        pass

    def get_chunk_code(self, path):
        pass

    def exposed_create_directory(self, directory, path):
        path_obj = self.get_path_obj(path)

        if not path_obj or not self.valid_name(directory) \
                or directory in path_obj.keys():
            # custom error
            return False

        log.info(f"Creating directory '{directory}' on path {path}")
        path_obj[directory] = {}
        
        return True

    def exposed_get_dirs_and_files(self, path):
        path_obj = self.get_path_obj(path)

        if not path_obj:
            return None
        
        return list(path_obj.keys())

    def remove_directory(self, path):
        pass

    def put_file(self, path):
        pass

    def get_file(self, path):
        pass

    def on_disconnect(self, conn):
        self.save_snapshot()


if __name__=="__main__":
    server = ThreadedServer(SenseiService(), port=33333)
    server.start()

    # after = Sensei()
    # after.save_snapshot()
