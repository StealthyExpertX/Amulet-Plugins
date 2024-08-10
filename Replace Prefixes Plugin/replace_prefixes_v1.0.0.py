#misc imports.
from typing import TYPE_CHECKING

#numpy imports.
import numpy as np

#amulet imports.
from amulet.api.block import Block
from amulet.api.level import BaseLevel
from amulet.api.selection import SelectionGroup
from amulet.api.data_types import Dimension

#system imports.
import traceback
import time
import os

#old and new prefix keys for operation_options.
old_prefix_key = "Old Prefix: "
new_prefix_key = "New Prefix: "

#plugin options.
operation_options = {
    "Plugin replaces old prefix in blocks with a new prefix.": ["label"],
    old_prefix_key: ["str", "prefix1"],
    new_prefix_key: ["str", "prefix12"],
}

#the main function.
def replace_prefixes(world: BaseLevel, dimension: Dimension, selection: SelectionGroup, options: dict):
    try:
        #old prefix & new prefix options.
        old_prefix = options[old_prefix_key]
        new_prefix = options[new_prefix_key]

        #start the time tracking.
        start_time = time.time()

        #start looping over chunks in the selection.
        print(f"Replacing all prefixes now...'")
        for chunk_coords, box in world.get_coord_box(dimension, selection):

            #check if the chunk exists.
            if not world.has_chunk(*chunk_coords, dimension):
                continue

            #get the chunk.
            chunk = world.get_chunk(*chunk_coords, dimension)

            #get the block palette.
            block_palette = chunk.block_palette

            #check if our prefix is in the palette.
            prefix_in_palette = False
            for block in block_palette.blocks:
                if block.namespace.startswith(old_prefix):
                    prefix_in_palette = True #if true check and mark the chunk.
                    break

            #if not in the palette, skip chunk.
            if not prefix_in_palette:
                continue

            #temp tracking replace mask per chunk.
            old_blocks = []
            replace_blocks = {}

            #loop over the block palette and check which ones need prefixes edited.
            for block_id, block in block_palette.items():
                if block.namespace.startswith(old_prefix):
                    new_namespace = block.namespace.replace(old_prefix, new_prefix)

                    #check if block properties have prefixes that match too.
                    if any(key.startswith(old_prefix) for key in block.properties.keys()):
                        new_properties = {key.replace(old_prefix, new_prefix): value for key, value in block.properties.items()}
                    else:
                        new_properties = block.properties

                    #create a new block for replacing from scratch.
                    new_block = Block(
                        new_namespace,
                        block.base_name,
                        new_properties,
                        block.extra_blocks
                    )

                    #register the block to the block manager.
                    new_block_id = block_palette.get_add_block(new_block)

                    #save blocks for later for the replace mask.
                    old_blocks.append(block_id)
                    replace_blocks[block_id] = new_block_id

            #loop over selection again with chunk slices and replace the block palettes super fast using the replace mask.
            for chunk_slice, slices, _ in world.get_chunk_slice_box(dimension, box):
                blocks = chunk_slice.blocks[slices]
                repl_mask = np.isin(blocks, old_blocks)

                if np.any(repl_mask):
                    blocks[repl_mask] = np.vectorize(replace_blocks.get)(blocks[repl_mask])

                    chunk_slice.blocks[slices] = blocks
                    chunk_slice.changed = True

        #stop tracking time.
        end_time = time.time()

        #clear console and print finished/completed message.
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"Replaced all prefixes in {end_time - start_time:.2f} seconds.")

    #handle rare exceptions.
    except Exception as e:
        print("\nsomething went wrong while replacing - [error]: \n" + str(e) + "\n\n" + str(traceback.format_exc()))

#register the plugin.
export = {
    "name": "replace prefixes",
    "operation": replace_prefixes,
    "options": operation_options,
}