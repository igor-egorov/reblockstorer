import sys

from . import arguments
from . import loader


def main():
    parser = arguments.init_parser()
    params = parser.parse_args()
    params = arguments.validate(parser, params)
    loader.BlockLoader(params.blockstore)


if __name__ == "__main__":
    main()
