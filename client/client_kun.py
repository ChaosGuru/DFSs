import logging
import json
import os

import click
import rpyc

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("client-kun")

DIR_PATH = os.path.dirname(os.path.realpath(__file__))


def get_sensei():
    try:
        return rpyc.connect("localhost", 33333).root
    except ConnectionRefusedError:
        log.error("Sensei refused connection.")
        click.echo("Server refusing connection.")


def get_chunk(ip, port):
    try:
        return rpyc.connect(ip, port).root
    except ConnectionRefusedError:
        log.error("Chunk refused connection.")


def save_cache(data):
    with open(os.path.join(DIR_PATH, "cache.json"), "w") as f:
        json.dump(data, f)

    # breakpoint()


def get_cache():
    if not os.path.exists(os.path.join(DIR_PATH, "cache.json")):
        save_cache({"pwd": "/", "user": "temp"}) 

    with open(os.path.join(DIR_PATH, "cache.json"), "r") as f:
        data = json.load(f)

    return data


def new_user():
    cache = {"pwd": "/", "user": "temp"}

    save_cache(cache)


def make_path(name):
    pwd = get_cache()["pwd"]

    if name.startswith('/'):
        return name
    else:
        return pwd.rstrip("/") + "/" + name


@click.group()
def dfs():
    """CLI for client DFS"""
    if not os.path.exists(os.path.join(DIR_PATH, "cache.json")):
        new_user()


@dfs.command()
def pwd():
    """Prints current directory"""
    data = get_cache()
    click.echo(data["pwd"])


@dfs.command()
@click.argument("path", default="")
def ls(path):
    """Prints directories and files"""
    sensei = get_sensei()

    if sensei:
        data = get_cache()
        res = sensei.get_namespaces(make_path(path))
        res = [r.replace(data["pwd"], "", 1).lstrip("/").split("/")[0] 
            for r in res]

        if res:
            click.echo(" ".join(set(res)))


@dfs.command()
@click.argument("path", default="")
def tree(path):
    """Print directory tree"""
    sensei = get_sensei()

    if sensei:
        res = sensei.get_namespaces(make_path(path))

        if res:
            click.echo("\n".join(sorted(res)))


@dfs.command()
@click.argument("name")
def mkdir(name):
    """Creates new directory"""
    sensei = get_sensei()
    dir_name = make_path(name)

    if sensei:
        if sensei.create_directory(dir_name):
            click.echo(dir_name)
        else:
            click.echo("Error! Failed to create directory.")


@dfs.command()
@click.argument("path")
def cd(path):
    """Changes working directory"""
    cache = get_cache()
    sensei = get_sensei()

    if sensei:
        if path == "/":
            cache["pwd"] = "/"
        elif path == "..":
            cache["pwd"] = "/" + "/".join(cache["pwd"].split("/")[:-1]).lstrip("/")
        elif sensei.exists(make_path(path)):
            cache["pwd"] = make_path(path)
        else:
            click.echo("Error! Path do not exists!")

        save_cache(cache)
        click.echo(cache["pwd"])


@dfs.command()
@click.argument("name")
def rm(name):
    """Removes namespace"""
    sensei = get_sensei()

    if sensei:
        namespace = make_path(name)
        sensei.remove_namespaces(namespace)

        click.echo(f"Namespace {namespace} removed!")


@dfs.command()
@click.argument("filename")
def put(filename):
    "Put file to DFSs"

    sensei = get_sensei()
    file_size = os.path.getsize(filename)

    if sensei:
        chunks_uuid = sensei.write_file(make_path(filename), file_size)
        chunks_locs = sensei.get_chunk_location(list(chunks_uuid))
        chunk_size = sensei.get_chunk_size()

        with open(os.path.join(DIR_PATH, filename), "rb") as f:
            for uuid in chunks_uuid:
                data = f.read(chunk_size)

                for loc in chunks_locs[uuid]:
                    chunk = get_chunk(*loc)

                    chunk.write(uuid, data)


@dfs.command()
@click.argument("filename")
def get(filename):
    "Get file from DFSs"

    sensei = get_sensei()
    if not sensei:
        return None

    file_path = make_path(filename)
    chunks_uuid = sensei.read_file(file_path)
    chunks_uuid = {k:chunks_uuid[k] for k in chunks_uuid}

    chunks_locs = sensei.get_chunk_location(chunks_uuid.values())
    file_data = []

    if not os.path.exists(os.path.join(DIR_PATH, "saved_files")):
        os.mkdir(os.path.join(DIR_PATH, "saved_files"))

    save_path = os.path.join(DIR_PATH, "saved_files", *file_path.split('/')[:-1])

    if not os.path.exists(save_path):
        os.makedirs(save_path)

    with open(os.path.join(save_path, file_path.split('/')[-1]), "wb") as f:
        for key, uuid in chunks_uuid.items():
            for location in chunks_locs[uuid]:
                chunk = get_chunk(*location)
                data = chunk.read(uuid)

                if data:
                    f.write(data)
                    break


if __name__ == "__main__":
    dfs()