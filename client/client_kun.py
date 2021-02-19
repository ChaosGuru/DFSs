import logging
import json
import os

import click
import rpyc

CACHE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 
                          "cache.json")


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
    cache = {
        "pwd": "/",
        "user": "temp"
    }
    
    save_cache(cache)


@click.group()
def dfs():
    """CLI for client DFS"""
    if not os.path.exists(CACHE_PATH):
        new_user()


@dfs.command()
def pwd():
    data = get_cache()
    click.echo(data["pwd"])


@dfs.command()
@click.argument("file", default="")
def ls(file):
    sensei = get_sensei()

    if sensei:
        data = get_cache()
        res = sensei.get_namespaces(data["pwd"]+file)

        if res:
            print(' '.join(res))


@dfs.command()
@click.argument("name")
def mkdir(name):
    data = get_cache()
    
    sensei = get_sensei()
    if sensei:
        if sensei.create_namespaces(data["pwd"], name):
            click.echo("Directory created succesfully!")
        else:
            click.echo('\n'.join([
                "Error! Failed to create directory.",
                "Check if you entered directory name correctly"
            ]))


@dfs.command()
@click.argument("path")
def cd(path):
    cache = get_cache()
    sensei = get_sensei()

    if sensei:
        if sensei.exists(cache["pwd"] + path):
            cache["pwd"] = cache["pwd"] + path
            save_cache(cache)
            click.echo("Current path: {}".format(cache["pwd"]))
        else:
            click.echo("Error! Path do not exists!")


if __name__=="__main__":
    dfs()