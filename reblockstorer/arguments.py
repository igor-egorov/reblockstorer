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
                        help='Path to source blockstore directory.')
    parser.add_argument('-o', '--outblockstore', dest='outblockstore', type=path_type,
                        help='Path to save the new blockstore. '
                        'Will try to create the path if not exists.')
    parser.add_argument('-p', '--peers', dest='peers', type=path_type,
                        help='[OPTIONAL] A file that specifies peers addresses to put to AddPeer commands. '
                        'Each peer address should be placed on its own line. '
                        'If omitted, then peers addresses will remain unmodified.')
    parser.add_argument('-k', '--keydir', dest='keydir', type=path_type,
                        help='[OPTIONAL] Path to save the new keys. '
                        'Will try to create the path if not exists. '
                        'The keys will be saved to OUTBLOCKSTORE directory if not specified.')
    parser.add_argument('-e', '--existingkeys', dest='existingkeys', type=path_type,
                        help='[OPTIONAL] Path to a folder with existing key pairs which should not be recreated and overwritten. '
                        'A keypair is represented by a couple of files with the same name but different extensions: .priv and .pub. '
                        'Each file contains a string without any trailing characters with hex representation of the key.')
    parser.add_argument('-r', '--resignblocksonly', dest='resignblocksonly', action='store_true',
                        help='[OPTIONAL] Prevents users\' keys recreation and user\' transactions re-signing. '
                        'Only block signatures are get recalculated. '
                        'This option can be used only when peers\' keypairs are known and specified via existing keys parameter -e.')
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
    if not results.blockstore.exists():
        terminate('Source blockstore path does not exists ({})'.format(
            results.blockstore), parser)
    if not results.blockstore.is_dir():
        terminate('Source blockstore path is not a directory', parser)

    if not results.outblockstore.exists():
        try:
            results.outblockstore.mkdir(exist_ok=True)
        except OSError as err:
            terminate('Unable to create outblockstore directory ({}, OSError {})'.format(
                results.outblockstore, err.errno), parser)
    elif not results.outblockstore.is_dir():
        terminate('Outblockstore path is not a directory', parser)

    try:
        next(results.outblockstore.iterdir())
        if not results.force:
            terminate('Outblockstore directory is not empty. '
                      'Use -f to overwrite outblockstore and keydir directories.', parser)
        else:
            reset_dir(results.outblockstore)
    except StopIteration:
        pass

    if not results.keydir:
        results.keydir = results.outblockstore

    if results.existingkeys:
        if not results.existingkeys.exists():
            terminate('The path {} does not exists.'.format(
                results.existingkeys), parser)
        if not results.existingkeys.is_dir():
            terminate('The path {} is not a directory.'.format(
                results.existingkeys), parser)

    if results.resignblocksonly:
        if not results.existingkeys:
            terminate(
                'You have to specify peers\' keypairs to re-sign blocks via -e parameter.', parser)
        if results.peers:
            terminate('Not possible to assign new addresses to peers when -r option is specified. '
                      'This will lead to the need of transactions re-signing which is prohibited by -r option.', parser)

    if not results.peers:
        print('Peers addresses will remain the same.')
    elif not results.peers.exists():
        terminate(
            'Please specify the correct path to the peers\' addresses file.', parser)
    else:
        peers = []
        with open(results.peers, 'rt') as peers_file:
            peers_lines = peers_file.readlines()
            for peer_line in peers_lines:
                line = peer_line.strip()
                if line:
                    peers.append(line)
        results.peers = peers

    if not results.keydir.exists():
        try:
            results.keydir.mkdir(exist_ok=True)
        except OSError as err:
            terminate('Unable to create keydir directory ({}, OSError {})'.format(
                results.keydir, err.errno), parser)
    elif not results.keydir.is_dir():
        terminate('Keydir path is not a directory', parser)

    try:
        next(results.keydir.iterdir())
        if not results.force:
            terminate('Keydir directory is not empty. '
                      'Use -f to overwrite outblocstore and keydir directories.', parser)
        else:
            reset_dir(results.keydir)
    except StopIteration:
        pass

    return results
