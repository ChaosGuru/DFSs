import logging

import click


@click.group()
def main():
    """ Simple CLI that will greet you"""
    pass


@main.command()
@click.argument('name')
def greet(name):
    """This will greet you back with your name"""
    click.echo("Hello, " + name)


@main.command()
def ls():
    """Prints content of working directory"""
    pass


@main.command()
def pwd():
    """Prints working directory"""
    pass