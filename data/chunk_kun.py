from sys import argv
from os import makedirs, listdir
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

    def __init__(self, port):
        logging.getLogger("CHUNK/%s" % port).propagate = False

        self.port = port
        self.chunks = {}
        self.loc = join(dirname(realpath(__file__)), "chunk_servers", port)

        if not exists(self.loc):
            makedirs(self.loc)

        self.scan_filesystem()
        self.greet_sensei()

    def exposed_write(self, chunk_uuid, data):
        log.info(f"Chunk server {self.port} writes chunk {str(chunk_uuid)}")

        filename = self.make_filename(chunk_uuid)
        self.chunks[str(chunk_uuid)] = filename
        
        with open(filename, "wb") as f:
            f.write(data)

        self.updata_data_on_sensei()

    def exposed_read(self, chunk_uuid):
        log.info(f"Chunk server {self.port} reads chunk {str(chunk_uuid)}")

        filename = self.chunks[str(chunk_uuid)]
        
        with open(filename, "rb") as f:
            data = f.read()

        return data

    def exposed_get_state(self):
        return {"chunks": len(self.chunks)}

    def make_filename(self, chunk_uuid):
        log.debug(f"Chunk server {self.port} makes filename {str(chunk_uuid)}")

        filename = join(self.loc, str(chunk_uuid) + '.gfss')

        return filename

    def scan_filesystem(self):
        log.debug(f"Chunk server {self.port} file system scan")

        files = listdir(self.loc)

        for f in files:
            self.chunks[f.rstrip('.gfss')] = f

    def greet_sensei(self):
        log.debug(f"Chunk server {self.port} greets sensei")

        sensei = self.get_sensei()

        if sensei:
            sensei.register_chunk_server(int(self.port), len(self.chunks))

    def updata_data_on_sensei(self):
        log.debug(f"Chunk server {self.port} updates data on sensei")

        sensei = self.get_sensei()

        if sensei:
            sensei.update_chunk_data(int(self.port), len(self.chunks))


    def get_sensei(self):
        try:
            return rpyc.connect('localhost', 33333).root
        except ConnectionRefusedError:
            log.error('Sensei refused connection.')
            return None


if __name__=="__main__":
    port = argv[1]
    server = ThreadedServer(ChunkService(port), port=port)
    server.start()