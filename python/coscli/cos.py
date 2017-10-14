#!/usr/bin/env python
print "tset"
import click

from launch import launch


@click.command()
def cd():
    """Change directory to a package location."""
    click.echo('Hello World!')

@click.command()
def ls():
    """List files in a package."""
    click.echo('Hello World!')

@click.command()
def ed():
    """Edit a file in a package."""
    click.echo('Hello World!')

@click.command()
def cp():
    """Copy files from a package."""
    click.echo('Hello World!')

@click.command()
def run():
    """Run one COS node."""
    click.echo('Hello World!')

@click.command()
def package():
    """Create a package."""
    click.echo('Hello World!')

@click.command()
def param():
    """Get and set COS parameters."""
    click.echo('Hello World!')

@click.command()
def node():
    """Display information about a node."""
    click.echo('Hello World!')

@click.command()
def topic():
    """Display information about a topic."""
    click.echo('Hello World!')

@click.command()
def msg():
    """Display information about a message type."""
    click.echo('Hello World!')


@click.group()
def cli():
    pass

cli.add_command(cd)
cli.add_command(ls)
cli.add_command(ed)
cli.add_command(cp)
cli.add_command(run)
cli.add_command(package)
cli.add_command(param)
cli.add_command(node)
cli.add_command(topic)
cli.add_command(msg)
cli.add_command(launch.launch)

def main():
    cli()

if __name__ == '__main__':
    main()