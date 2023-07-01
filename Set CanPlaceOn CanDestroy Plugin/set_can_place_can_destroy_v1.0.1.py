#Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0) license.
#By StealthyX - @RedstonerLabs - StealthyX#8940

from amulet.api.selection import SelectionGroup
from amulet.api.level import BaseLevel
from typing import TYPE_CHECKING, Optional, Callable
from amulet.api.data_types import Dimension
from amulet_map_editor.programs.edit.api.canvas import EditCanvas
from amulet_map_editor.programs.edit.api.operations import DefaultOperationUI
from amulet_map_editor.api.wx.ui.simple import SimpleDialog
from amulet.api.level import World
import amulet
import PyMCTranslate
from typing import TYPE_CHECKING, Tuple
from amulet.api.wrapper import Interface, EntityIDType, EntityCoordType

import numpy
import urllib.request
import wx
import ast
import json
import os
import string
import os.path
from os import path

from ctypes import windll
from pkg_resources import packaging

import glob
import random
import re
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen

from amulet.api.data_types import Dimension
from amulet.api.selection import SelectionGroup
from amulet_nbt import  *

from amulet_map_editor.api.wx.ui.base_select import EVT_PICK
from amulet_map_editor.api.wx.ui.simple import SimpleDialog
from amulet_map_editor.api.wx.ui.block_select import BlockDefine
from amulet_map_editor.api.wx.ui.block_select import BlockSelect
from amulet_map_editor.programs.edit.api.operations import DefaultOperationUI
from amulet_map_editor.api.wx.ui.base_select import BaseSelect
from amulet_map_editor.api import image
from amulet.utils import block_coords_to_chunk_coords
from amulet.api.block import Block

from amulet.api.errors import ChunkLoadError, ChunkDoesNotExist
from amulet_map_editor.programs.edit.api.operations import (
    SimpleOperationPanel,
    OperationSilentAbort,
)

canplaceon = "CanPlaceOn"
candestroy = "CanDestroy"
plugin_title = str(canplaceon)+" / "+str(candestroy)+" Plugin"

operation_options = {
    plugin_title: ["label"],
    "This plugin sets the '"+str(canplaceon)+"' & '"+str(candestroy)+"' Tags": ["label"],
    "It edits containers that hold various items, and applies those edits.": ["label"],
    "If left blank, it will use a list of all block identifiers.": ["label"],
    "Example of Usage: 'stone, grass, dirt'": ["label"],
    str(canplaceon)+":": [
        "bool",
        True,
    ],
    str(candestroy)+":": [
        "bool",
        True,
    ],
    "Block Ids for "+str(canplaceon)+":": ["str", "grass, dirt, stone"],
    "Block Ids for "+str(candestroy)+":": ["str", "grass, dirt, stone"],
}

def _get_vanilla_block(dim, world, x, y, z, trans):
    #barrowed from the amulet api. #thanks gentlegiant.
    cx, cz = block_coords_to_chunk_coords(x, z)
    offset_x, offset_z = x - 16 * cx, z - 16 * cz

    chunk = world.get_chunk(cx, cz, dim)
    runtime_id = chunk.blocks[offset_x, y, offset_z]

    universal_bk = chunk.block_palette[runtime_id]
    universal_be = chunk.block_entities.get((x, y, z), None)
    (block, block_entity, _) =  trans.block.from_universal(universal_bk, universal_be)
    return (block, block_entity)

def parse_list_of_blocks(string_of_blocks):
    if len(string_of_blocks) > 0:
        try:
            string_of_blocks = re.findall(r'\b[\w\d_]+\b', string_of_blocks)
            return [True, string_of_blocks]
        except:
            raise ValueError("[ERROR!] Use this format grass, dirt, stone")
    else:
        return [False, None]

def add_nbttags(all_blocks, has_custom_block, block_dict_use):
    blocks_idsX = ListTag()
    if not has_custom_block:
        #fills it with all vanilla blocks 
        #for the current platform and version.
        for idx, block_id in enumerate(all_blocks):
            if "minecraft:" in block_id:
                blocks_idsX.append(StringTag(block_id))
            else:
                blocks_idsX.append(StringTag("minecraft:"+block_id))
        else:
            return blocks_idsX
    else:
        for block_id in block_dict_use:
            if "minecraft:" in block_id:
                blocks_idsX.append(StringTag(block_id))
            else:
                blocks_idsX.append(StringTag("minecraft:"+block_id))
        return blocks_idsX

def get_block_lists(world, platform, version):
    translation_manager = PyMCTranslate.TranslationManager
    version = world.translation_manager.get_version(platform, version)
    base_names = version.block.base_names("minecraft", True)
    return base_names

def template_function(world: BaseLevel, dimension: Dimension, selection: SelectionGroup, options: dict):
    chunk_coordinates = selection.chunk_locations()

    world = world
    platform = world.level_wrapper.platform
    world_version = world.level_wrapper.version

    all_blocks = get_block_lists(world, platform, world_version)

    can_place_on_check = options[canplaceon+":"]
    can_destroy_check = options[candestroy+":"]
    raw_can_place_list = options["Block Ids for "+canplaceon+":"]
    raw_can_destroy_list = options["Block Ids for "+candestroy+":"]

    blocks_can_place = parse_list_of_blocks(raw_can_place_list)[1]
    blocks_can_destroy = parse_list_of_blocks(raw_can_destroy_list)[1]

    blocks_can_place_check = parse_list_of_blocks(raw_can_place_list)[0]
    blocks_can_destroy_check = parse_list_of_blocks(raw_can_destroy_list)[0]


    block_dict_check = {
        canplaceon: blocks_can_place_check,
        candestroy: blocks_can_destroy_check
    }

    block_dict_use = {
        canplaceon: blocks_can_place,
        candestroy: blocks_can_destroy
    }

    trans = world.translation_manager.get_version(platform, world_version)
    mc_version = (platform, world_version)

    for chunk_coords in chunk_coordinates:
        cx, cz = chunk_coords
        print ("Started editing...")

        try:
            chunk = world.get_chunk(cx, cz, dimension)
            block_entities = chunk.block_entities
            be_keys = chunk.block_entities

            for be_coordinates in be_keys.keys():
                if be_coordinates in selection: 
                    (x, y, z) = be_coordinates 
                    (block, block_entity) = _get_vanilla_block(dimension, world, x, y, z, trans)

                    if block_entity is not None:
                        if "Items" in block_entity.nbt:
                            #loops over each item in the container.
                            for ind, item in enumerate(block_entity.nbt["Items"]):
                                if can_place_on_check:
                                    bk_list1 = add_nbttags(all_blocks, block_dict_check.get(canplaceon), block_dict_use.get(canplaceon))
                                    block_entity.nbt["Items"][ind][canplaceon] = bk_list1

                                if can_destroy_check:
                                    bk_list2 = add_nbttags(all_blocks, block_dict_check.get(candestroy), block_dict_use.get(candestroy))
                                    block_entity.nbt["Items"][ind][candestroy] = bk_list2

                            world.set_version_block(x, y, z, dimension, mc_version, block, block_entity)

        except ChunkLoadError:
            print(f'Chunk error at {chunk_coords}')
        print ("Completed editing!")

export = {
    "name": plugin_title,
    "operation": template_function,
    "options": operation_options,
}