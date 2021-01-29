import logging
import json

import click
import rpyc


def get_sensei():
    return rpyc.connect("localhost", 33333).root


def save_cache(data):
    with open("cache.json", "w") as f:
        json.dump(data, f)


def get_cache():
    with open("cache.json", "r") as f:
        data = json.load(f)

    return data


@click.group()
def main():
    """CLI for client DFS"""
    pass


@main.command()
def ls():
    """Prints content of working directory"""
    # pass

    sensei = get_sensei()
    data = get_cache()
    res = sensei.get_dirs_and_files(data["pwd"])

    for l in res:
        print(l, end=' ')


@main.command()
def pwd():
    """Prints working directory"""
    
    data = get_cache()
    click.echo(data["pwd"])


@main.command()
@click.argument("name")
def mkdir(name):
    """Create directory on current pwd with the <name>"""

    data = get_cache()
    
    sensei = get_sensei()
    if sensei.create_directory(name, data["pwd"]):
        click.echo("Directory created succesfully!")
    else:
        click.echo("""Error! Failed to create directory. 
            Check if you entered directory name correctly""")


if __name__=="__main__":
    main()