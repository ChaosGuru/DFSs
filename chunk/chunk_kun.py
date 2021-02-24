from sys import argv
import os
import logging

import rpyc
from rpyc.utils.server import ThreadedServer

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("chunk-kun")


class ChunkService(rpyc.Service):
    """Chunk server for storing chunks of files
    """

    def __init__(self, name):
        log.info(f"Creating chunk object with name {name}")

        self.name = name
        self.chunks = {}
        self.loc = os.path.join(os.path.dirname(os.path.realpath(__file__)), 
                                "chunk_servers",
                                name)

        if not os.path.exists(self.loc):
            os.makedirs(self.loc)

    def exposed_write(self, chunk_uuid, data):
        log.info(f"Writing chunk {str(chunk_uuid)}")

        filename = self.get_filename(chunk_uuid)
        self.chunks[chunk_uuid] = filename
        
        with open(filename, "wb") as f:
            f.write(data)

    def exposed_read(self, chunk_uuid):
        log.info(f"Reading chunk {chunk_uuid}")

        with open(self.chunks[chunk_uuid], "rb") as f:
            data = f.read()

        return data

    def get_filename(self, chunk_uuid):
        filename = os.path.join(self.loc, str(chunk_uuid) + ".gfss")

        # log.info(f"Creating filename {filename}")

        return filename


if __name__=="__main__":
    port = argv[1]
    server = ThreadedServer(ChunkService(port), port=port)
    server.start()