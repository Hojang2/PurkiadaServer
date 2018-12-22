#!/usr/bin/env python3

import click


@click.command()
@click.option('--server', type=click.Path(exists=True), help='Path to server')
@click.option('--host', default='0.0.0.0', help='Address on where will be server running')
@click.option('--port', default=9600, help='Port on where the app will run')
def main(server, host, port) -> None:
    """

    The main file for running Purkyada server

    """

    pass


if __name__ == '__main__':
    main()
