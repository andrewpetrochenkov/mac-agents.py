#!/usr/bin/env python
"""generate launchd.plist from python file(s)"""
import click
import mac_agents

MODULE_NAME = "mac_agents.create"
PROG_NAME = 'python -m %s' % MODULE_NAME
USAGE = 'python -m %s path ...' % MODULE_NAME


@click.command()
@click.argument('path', nargs=-1, required=True)
def _cli(path):
    for f in path:
        mac_agents.create(f)


if __name__ == '__main__':
    _cli(prog_name=PROG_NAME)
