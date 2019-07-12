import sys

from . import arguments
from .loader import BlockLoader
from .saver import BlockSaver
from .keystore import Keystore
from .processor import Processor


def main():
    parser = arguments.init_parser()
    params = parser.parse_args()
    params = arguments.validate(parser, params)
    block_loader = BlockLoader(params.blockstore)
    block_saver = BlockSaver(params.outblockstore)
    keystore = Keystore(params.keydir)
    processor = Processor(block_loader, block_saver, keystore, params.peers)
    processor.process()
    print('Processing finished.')


if __name__ == "__main__":
    main()
