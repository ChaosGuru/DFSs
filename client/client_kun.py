import logging
import json
import os

import click
import rpyc

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("client-kun")

DIR_PATH = os.path.dirname(os.path.realpath(__file__))


def get_sensei():
    data = get_metadata()

    try:
        return rpyc.connect('localhost', 33333).root
    except ConnectionRefusedError:
        log.error('Sensei refused connection.')
        click.echo('Server refusing connection.')

        return None


def get_chunk(ip, port):
    try:
        return rpyc.connect(ip, port).root
    except ConnectionRefusedError:
        log.error("Chunk refused connection.")

        return None


def save_metadata(data):
    with open(os.path.join(DIR_PATH, "metadata.json"), "w") as f:
        json.dump(data, f)


def get_metadata():
    if not os.path.exists(os.path.join(DIR_PATH, "metadata.json")):
        save_metadata({"pwd": "/", "user": "user_uuid"}) 

    with open(os.path.join(DIR_PATH, "metadata.json"), "r") as f:
        data = json.load(f)

    return data


def make_path(name):
    pwd = get_metadata()["pwd"]

    path = name if name.startswith('/') else pwd + name

    return path.rstrip('/') + '/'


@click.group()
def dfs():
    """CLI for client DFS"""

    # create new user metadata if not exists
    # get_metadata()


@dfs.command()
def pwd():
    """Prints current directory"""
    data = get_metadata()
    click.echo(data["pwd"])


@dfs.command()
@click.argument("path", default="")
def ls(path):
    """Prints directories and files"""
    sensei = get_sensei()

    if sensei:
        data = get_metadata()
        full_path = make_path(path)
        namespaces = sensei.get_namespaces(full_path)

        res = [r.replace(full_path, '', 1).split("/")[0] for r in namespaces]

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

            if sensei.exists(dir_name):
                click.echo("Path already exists!")


@dfs.command()
@click.argument("path")
def cd(path):
    """Changes working directory"""
    data = get_metadata()
    sensei = get_sensei()

    if sensei:
        if path == "/":
            data["pwd"] = "/"
        elif path == "..":
            data["pwd"] = "/".join(data["pwd"].split("/")[:-2]) + '/'
        elif sensei.exists(make_path(path)):
            data["pwd"] = make_path(path)
        else:
            click.echo("Error! Path do not exists!")

        save_metadata(data)
        click.echo(data["pwd"])


@dfs.command()
@click.argument("path")
def rm(path):
    """Removes namespace"""
    sensei = get_sensei()
    namespace = make_path(path)

    if sensei:
        if not sensei.exists(namespace):
            click.echo("Error! Path do not exists!")
        else: 
            dels = sensei.remove_namespace(namespace)
            click.echo(f"Removed {dels} elements in namespace {namespace}")


@dfs.command()
@click.option('--force', is_flag=True, help='Forces file writing.')
@click.argument('filename')
def put(filename, force):
    """Put file to DFSs"""

    if not filename.startswith('/'):
        filename = os.path.join(DIR_PATH, filename)

    sensei = get_sensei()
    file_size = os.path.getsize(filename)

    if not sensei:
        return None

    chunks_uuid = sensei.write_file(make_path(filename.split('/')[-1]), file_size, force)
    chunk_size = sensei.get_chunk_size()

    if not chunks_uuid:
        click.echo('Server refused file writing.')
        return None

    with open(filename, 'rb') as f:
        for uuid in chunks_uuid:
            data = f.read(chunk_size)
            locs = sensei.get_chunk_location(uuid)

            for loc in locs:
                chunk = get_chunk(*loc)

                chunk.write(uuid, data)


@dfs.command()
@click.argument('filename')
def get(filename):
    'Get file from DFSs'

    sensei = get_sensei()
    if not sensei:
        return None

    file_path = make_path(filename)
    chunks_uuid = sensei.read_file(file_path)
    chunks_uuid = {k:chunks_uuid[k] for k in chunks_uuid}


    save_path = create_save_folder(file_path)

    with open(os.path.join(save_path, file_path.split('/')[-2]), "wb") as f:
        for key, uuid in chunks_uuid.items():
            locs = sensei.get_chunk_location(uuid)

            for loc in locs:
                chunk = get_chunk(*loc)
                data = chunk.read(uuid)

                if data:
                    f.write(data)
                    break


def create_save_folder(file_path):
    # if not os.path.exists(os.path.join(DIR_PATH, "saved_files")):
    #     os.mkdir(os.path.join(DIR_PATH, "saved_files"))

    save_path = os.path.join(DIR_PATH, "saved_files", *file_path.split('/')[:-2])

    if not os.path.exists(save_path):
        os.makedirs(save_path)

    return save_path


if __name__ == "__main__":
    dfs()