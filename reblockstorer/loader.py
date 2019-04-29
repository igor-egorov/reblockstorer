
import os
import sys
import json
from .proto import block_pb2
from google.protobuf import json_format

# todo support sequential block reading

class BlockLoader:

    def __init__(self, blockstore_path):
        self.path = blockstore_path
        self.__parse_blocks()
        print('{} block(s) loaded'.format(len(self.blocks)))

    def __list_files(self):
        self.files = []
        for entry in os.listdir(self.path):
            if os.path.isfile(os.path.join(self.path, entry)):
                self.files.append(entry)
        self.files.sort()
        return self.files

    def __parse_blocks(self):
        self.blocks = []
        for file_block in self.__list_files():
            block = self.__parse_block(file_block)
            self.blocks.append(block)
        return self.blocks

    def __parse_block(self, filename):
        file_path = os.path.join(self.path, filename)
        has_error = True
        try:
            with open(file_path) as json_file:
                json_data = json.load(json_file)
            json_str = json.dumps(json_data)
            block = json_format.Parse(json_str, block_pb2.Block())
            has_error = False
        except json.decoder.JSONDecodeError as err:
            print('JSON is not valid. {}'.format(err), file=sys.stderr)
        except json_format.ParseError as err:
            print('Block JSON representation does not match the schema. {}'.format(
                err), file=sys.stderr)
        finally:
            if has_error:
                print('Unable to parse block {}'.format(
                    file_path), file=sys.stderr)
                sys.exit(2)
        return block
