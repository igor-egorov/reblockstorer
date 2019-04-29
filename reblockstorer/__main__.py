import sys

from .proto import block_pb2
from . import arguments


def main():
    parser = arguments.init_parser()
    params = parser.parse_args()
    print(arguments.validate(parser, params))


if __name__ == "__main__":
    main()
