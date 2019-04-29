# Command line arguments handler

import argparse
import sys
import os
from pathlib import Path


# todo reimplement as a class


def path_type(path):
    return Path(path).absolute()


def init_parser():
    parser = argparse.ArgumentParser(
        description='The tool for keys regeneration for Hyperledger Iroha blockstore')

    parser.add_argument('-b', '--blockstore', dest='blockstore', type=path_type,
                        help='Path to source blockstore directory')
    parser.add_argument('-o', '--outblockstore', dest='outblockstore', type=path_type,
                        help='Path to save the new blockstore. '
                        'Will try to create the path if not exists.')
    parser.add_argument('-k', '--keydir', dest='keydir', type=path_type,
                        help='[OPTIONAL] Path to save the new keys. '
                        'Will try to create the path if not exists. '
                        'The keys will be saved to OUTBLOCKSTORE directory if not specified.')
    return parser


def terminate(message: str, parser: argparse.ArgumentParser, exit_code: int = 1):
    print(message, file=sys.stderr)
    print('')
    parser.print_help(sys.stderr)
    sys.exit(exit_code)


def validate(parser: argparse.ArgumentParser, results: argparse.Namespace):
    if not results.blockstore or not results.outblockstore:
        terminate('Please specify required command arguments', parser)
    if not os.path.exists(results.blockstore):
        terminate('Source blockstore path does not exists ({})'.format(
            results.blockstore), parser)

    if not os.path.exists(results.outblockstore):
        try:
            os.makedirs(results.outblockstore, exist_ok=True)
        except OSError as err:
            terminate('Unable to create outblockstore directory ({}, OSError {})'.format(
                results.outblockstore, err.errno), parser)

    if not results.keydir:
        results.keydir = results.outblockstore

    if not os.path.exists(results.keydir):
        try:
            os.makedirs(results.keydir, exist_ok=True)
        except OSError as err:
            terminate('Unable to create keydir directory ({}, OSError {})'.format(
                results.keydir, err.errno), parser)
    return results
