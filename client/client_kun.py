import logging
import json
import os

import click
import rpyc


def get_sensei():
    return rpyc.connect("localhost", 33333).root


def save_cache(data):
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 
            "cache.json"), "w") as f:
        json.dump(data, f)


def get_cache():
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 
            "cache.json"), "r") as f:
        data = json.load(f)

    return data


@click.group()
def dfs():
    """CLI for client DFS"""
    pass


@dfs.command()
def pwd():
    data = get_cache()
    click.echo(data["pwd"])


@dfs.command()
@click.argument("file", default="")
def ls(file):
    sensei = get_sensei()
    data = get_cache()
    res = sensei.get_dirs_and_files(data["pwd"]+file)

    if res:
        print(' '.join(res))


@dfs.command()
@click.argument("name")
def mkdir(name):
    data = get_cache()
    
    sensei = get_sensei()
    if sensei.create_directory(name, data["pwd"]):
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

    if get_sensei().exists(cache["pwd"] + path):
        cache["pwd"] = cache["pwd"] + path
        save_cache(cache)
        click.echo("Current path: {}".format(cache["pwd"]))
    else:
        click.echo("Error! Path do not exists!")


if __name__=="__main__":
    dfs()