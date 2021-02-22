import logging
import json
import os

import click
import rpyc

CACHE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "cache.json")


def get_sensei():
    try:
        return rpyc.connect("localhost", 33333).root
    except ConnectionRefusedError:
        print("Warning! Server refused connection.")


def save_cache(data):
    with open(CACHE_PATH, "w") as f:
        json.dump(data, f)

    # breakpoint()


def get_cache():
    if not os.path.exists(CACHE_PATH):
        return None

    with open(CACHE_PATH, "r") as f:
        data = json.load(f)

    return data


def new_user():
    cache = {"pwd": "/", "user": "temp"}

    save_cache(cache)


@click.group()
def dfs():
    """CLI for client DFS"""
    if not os.path.exists(CACHE_PATH):
        new_user()


@dfs.command()
def pwd():
    """Prints current directory"""
    data = get_cache()
    click.echo(data["pwd"])


@dfs.command()
@click.argument("dir", default="")
def ls(dir):
    """Prints directories and files"""
    sensei = get_sensei()

    if sensei:
        data = get_cache()
        res = sensei.get_namespaces(data["pwd"] + dir)
        res = [r.replace(data["pwd"], "", 1).lstrip("/").split("/")[0] 
            for r in res]

        if res:
            click.echo(" ".join(set(res)))


@dfs.command()
@click.argument("dir", default="")
def tree(dir):
    """Print directory tree"""
    sensei = get_sensei()

    if sensei:
        data = get_cache()
        res = sensei.get_namespaces(data["pwd"] + dir)

        if res:
            click.echo("\n".join(sorted(res)))


@dfs.command()
@click.argument("name")
def mkdir(name):
    """Creates new directory"""
    data = get_cache()
    sensei = get_sensei()
    dir_name = data["pwd"].rstrip("/") + "/" + name

    if sensei:
        if sensei.create_directory(dir_name):
            click.echo(dir_name)
        else:
            click.echo(
                "\n".join(
                    [
                        "Error! Failed to create directory.",
                    ]
                )
            )


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
        elif sensei.exists(cache["pwd"].rstrip("/") + "/" + path):
            cache["pwd"] = cache["pwd"].rstrip("/") + "/" + path
        else:
            click.echo("Error! Path do not exists!")

        save_cache(cache)
        click.echo(cache["pwd"])


@dfs.command
@click.argument("path")
def rm(path):
    """Removes namespace"""
    pass


if __name__ == "__main__":
    dfs()