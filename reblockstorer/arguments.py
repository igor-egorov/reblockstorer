# Command line arguments handler

import argparse
import sys
import os
import shutil
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
    parser.add_argument('-p', '--peers', dest='peers', type=path_type,
                        help='A file that specifies peers addresses to put to AddPeer commands.'
                        'Each peer address should be placed on its own line')
    parser.add_argument('-k', '--keydir', dest='keydir', type=path_type,
                        help='[OPTIONAL] Path to save the new keys. '
                        'Will try to create the path if not exists. '
                        'The keys will be saved to OUTBLOCKSTORE directory if not specified.')
    parser.add_argument('-f', '--force', dest='force', action='store_true',
                        help='[OPTIONAL] Forces overwrite of outblockstore and keydir directories.')
    return parser


def terminate(message: str, parser: argparse.ArgumentParser, exit_code: int = 1):
    print(message, file=sys.stderr)
    print('')
    parser.print_help(sys.stderr)
    sys.exit(exit_code)


def reset_dir(path):
    try:
        shutil.rmtree(path)
        os.makedirs(path)
    except Exception as err:
        print('Unable to remove and create the directory {}. {}'.format(path, err))
        sys.exit(3)


def validate(parser: argparse.ArgumentParser, results: argparse.Namespace):
    if not results.blockstore or not results.outblockstore:
        terminate('Please specify required command arguments', parser)
    if not os.path.exists(results.blockstore):
        terminate('Source blockstore path does not exists ({})'.format(
            results.blockstore), parser)
    if not os.path.isdir(results.blockstore):
        terminate('Source blockstore path is not a directory', parser)

    if not os.path.exists(results.outblockstore):
        try:
            os.makedirs(results.outblockstore, exist_ok=True)
        except OSError as err:
            terminate('Unable to create outblockstore directory ({}, OSError {})'.format(
                results.outblockstore, err.errno), parser)
    elif not os.path.isdir(results.outblockstore):
        terminate('Outblockstore path is not a directory', parser)

    if os.listdir(results.outblockstore):
        if not results.force:
            terminate('Outblockstore directory is not empty. '
                      'Use -f to overwrite outblocstore and keydir directories.', parser)
        else:
            reset_dir(results.outblockstore)

    if not results.keydir:
        results.keydir = results.outblockstore

    if not results.peers or not os.path.exists(results.peers):
        terminate('Please specify peers addresses file.', parser)
    else:
        peers = []
        with open(results.peers, 'rt') as peers_file:
            peers_lines = peers_file.readlines()
            for peer_line in peers_lines:
                line = peer_line.strip()
                if line:
                    peers.append(line)
        results.peers = peers

    if not os.path.exists(results.keydir):
        try:
            os.makedirs(results.keydir, exist_ok=True)
        except OSError as err:
            terminate('Unable to create keydir directory ({}, OSError {})'.format(
                results.keydir, err.errno), parser)
    elif not os.path.isdir(results.keydir):
        terminate('Keydir path is not a directory', parser)

    if os.listdir(results.keydir):
        if not results.force:
            terminate('Keydir directory is not empty. '
                      'Use -f to overwrite outblocstore and keydir directories.', parser)
        else:
            reset_dir(results.keydir)

    return results
