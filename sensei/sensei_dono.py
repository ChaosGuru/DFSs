import pickle
import os
import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("sensei")


class Sensei:
    def __init__(self):
        log.info("Creating sensei object")
        # get namaspaces from snaphot
        self.namaspaces = {}
        self.load_namespaces()

        # get filename-chunk mapping from logs ????
        self.filename_chunks = {}
        self.load_chunks()

        # get chunk replicas location from chunks
        self.chunk_locations = {}

        from pprint import pprint
        pprint(self.namaspaces)

    def save_data(self):
        log.info("Saving data...")

        # temporary solution, change to another folder and servers
        data_path = os.path.dirname(os.path.realpath(__file__))

        snapshots_path = os.path.join(data_path, "snapshots")
        snapshot1 = os.path.join(snapshots_path, "snapshot1.dat")

        with open(snapshot1, "wb") as f:
            pickle.dump(self.namaspaces, f)

        # add to save filename-chunk mapping to logs

    def load_namespaces(self):
        log.info("Loading namespaces...")

        data_path = os.path.dirname(os.path.realpath(__file__))
        snapshot1 = os.path.join(data_path, "snapshots", "snapshot1.dat")

        with open(snapshot1, "rb") as f:
            self.namaspaces = pickle.load(f)

    def load_chunks(self):
        # rewrite to load from logs

        self.filename_chunks = {
            "users/oleg/my_folder/file1.txt": "some code",
        }

    def get_chunk_code(self, path):
        pass

    def create_directory(self, path):
        pass

    def remove_directory(self, path):
        pass

    def put_file(self, path):
        pass

    def get_file(self, path):
        pass


if __name__=="__main__":
    # print(os.path.dirname(os.path.realpath(__file__)))
    after = Sensei()
    after.save_data()
