
import json
import os
from google.protobuf import json_format


class BlockSaver:

    def __init__(self, out_blockstore_path):
        self.path = out_blockstore_path
        self.next_block = 1

    def save(self, block):
        block_name = str(self.next_block).zfill(16)
        self.next_block += 1
        block_json = json_format.MessageToJson(block)
        # produce compact json
        block_json = json.dumps(json.loads(block_json), separators=(',', ':'))
        path = os.path.join(self.path, block_name)
        with open(path, 'wt') as block_file:
            block_file.write(block_json)
            block_file.flush()
