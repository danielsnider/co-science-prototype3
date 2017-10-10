import click

from launch import launch


@click.command()
@click.option('--count', default=1, help='Number of greetings.')
@click.option('--tr', default=1, help='Number of greetings.')
def one(count, tr):
    """Example script."""
    click.echo('Hello World!')

@click.command()
@click.option('--count', default=1, help='Number of greetings.')
@click.option('--tr', default=1, help='Number of greetings.')
def two(count, tr):
    """Example script."""
    click.echo('Hello World!')

@click.group()
def cli():
    pass

cli.add_command(one)
cli.add_command(two)
cli.add_command(launch.launch)

# eval "$(_YOURSCRIPT_COMPLETE=source yourscript)"
# eval "$(_COS_COMPLETE=source cos)"