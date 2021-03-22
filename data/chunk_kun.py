from sys import argv
from os import makedirs
from os.path import join, dirname, realpath, exists
import logging

import rpyc
from rpyc.utils.server import ThreadedServer

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("chunk-kun")


class ChunkService(rpyc.Service):
    """
    Chunk server for storing chunks of files
    """

    def __init__(self, name):
        log.info(f"Starting chunk server {name}...")

        self.name = name
        self.chunks = {}
        self.loc = join(dirname(realpath(__file__)), "chunk_servers", name)

        if not exists(self.loc):
            makedirs(self.loc)

        # get status of their filesytem and all metadata

        # ping sensei server

    def exposed_write(self, chunk_uuid, data):
        log.info(f"Chunk server {self.name} writes chunk {str(chunk_uuid)}")

        filename = self.get_filename(chunk_uuid)
        self.chunks[str(chunk_uuid)] = filename
        
        with open(filename, "wb") as f:
            f.write(data)

    def exposed_read(self, chunk_uuid):
        log.info(f"Chunk server {self.name} reads chunk {str(chunk_uuid)}")

        filename = self.chunks[str(chunk_uuid)]
        
        with open(filename, "rb") as f:
            data = f.read()

        return data

    def exposed_get_state(self):
        return {"chunks": len(self.chunks)}

    def get_filename(self, chunk_uuid):
        log.debug(f"Chunk server {self.name} gets filename {str(chunk_uuid)}")

        filename = join(self.loc, str(chunk_uuid) + ".gfss")

        return filename


if __name__=="__main__":
    port = argv[1]
    server = ThreadedServer(ChunkService(port), port=port)
    server.start()