#You may use this plugin for only non commercial purposes aka non Minecraft Marketplace content.

#Twitter: @RedstonerLabs
#Discord: StealthyExpert#8940

from typing import TYPE_CHECKING, Tuple
from amulet.api.wrapper import Interface, EntityIDType, EntityCoordType

import wx.richtext

import numpy as np
import urllib.request
import wx
import ast

import math
from math import remainder

import json
import os
import string
import os.path
from os import path

from ctypes import windll
from distutils.version import LooseVersion, StrictVersion

#code for future auto install of any external requirements possibly?!
# try:
    # import requests
    # import urllib2
# except:
    # #future pip auto install support.
    # #https://raw.githubusercontent.com/pypa/get-pip/main/public/get-pip.py

import glob
import random
import re
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen

from amulet.api.data_types import Dimension
from amulet.api.selection import SelectionGroup
from amulet_nbt import TAG_String, TAG_Int, TAG_Byte, TAG_List, TAG_Long, TAG_Compound

from amulet_map_editor.api.wx.ui.base_select import EVT_PICK
from amulet_map_editor.api.wx.ui.simple import SimpleDialog
from amulet_map_editor.api.wx.ui.block_select import BlockDefine
from amulet_map_editor.api.wx.ui.block_select import BlockSelect
from amulet_map_editor.programs.edit.api.operations import DefaultOperationUI
from amulet_map_editor.api.wx.ui.base_select import BaseSelect
from amulet_map_editor.api import image
from amulet.utils import block_coords_to_chunk_coords
from amulet.api.block import Block

import PyMCTranslate

from amulet_map_editor.api.wx.ui.base_select import BaseSelect

if TYPE_CHECKING:
    from amulet.api.level import BaseLevel
    from amulet_map_editor.programs.edit.api.canvas import EditCanvas

class FindOpenedChests(wx.Panel, DefaultOperationUI):
    def __init__(
        self,
        parent: wx.Window,
        canvas: "EditCanvas",
        world: "BaseLevel",
        options_path: str,
    ):

        #sets the UI pannel
        wx.Panel.__init__(self, parent)
        DefaultOperationUI.__init__(self, parent, canvas, world, options_path)
        self.Freeze()

        self._sizer = wx.FlexGridSizer(0, 1, 2, 0) #verticle shape top to bottom for main dialog.
        self.SetSizer(self._sizer)

        #loads the default options to be overwitten later.
        options = self._load_options({})

        #creates a box sizer object and sets it.
        top_sizer = wx.FlexGridSizer(0, 1, 2, 0)
        self._sizer.Add(top_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 1)
        
        self._run_button = wx.Button(self, label="Run Operation")
        self._run_button.Bind(wx.EVT_BUTTON, self._run_operation)
        self._sizer.Add(self._run_button, 0, wx.ALL | wx.ALIGN_CENTRE_HORIZONTAL, 5)

        self.Layout()
        self.Thaw()

    @property #handles the wx add option size (height, width) default is (0, 0) 
    #interesting to note that ommiting the 0 on the second index of the tuple works?
    def wx_add_options(self) -> Tuple[int, ...]:
        return (0,)

    #barrowed some stuff from the amulet api. #thanks gentlegiant
    def _get_vanilla_block(self, dim, world, x, y, z, trans):
        cx, cz = block_coords_to_chunk_coords(x, z)
        offset_x, offset_z = x - 16 * cx, z - 16 * cz

        chunk = world.get_chunk(cx, cz, dim)
        runtime_id = chunk.blocks[offset_x, y, offset_z]

        universal_bk = chunk.block_palette[runtime_id]
        universal_be = chunk.block_entities.get((x, y, z), None)
        return trans.block.from_universal(universal_bk, universal_be)

    #gets name id from a tileentity
    def _get_be_id(self, te):
        if "minecraft:" not in te.namespaced_name:
            return str(te.namespaced_name).split(":")[1]
        return te.namespaced_name

    def _run_operation(self, _):
        self.canvas.run_operation(lambda: self._get_chest())

    #main preform method.
    def _get_chest(self):
        world = self.world
        dim = self.canvas.dimension
        sel = self.canvas.selection.selection_group

        #gets platform & version.
        platform = world.level_wrapper.platform
        world_version = world.level_wrapper.version

        #compiles platform and version into an MC version/platform
        mc_version = (platform, world_version)

        containers_count = 0
        containers_found = []

        #world format translation manager
        trans = world.translation_manager.get_version(platform, world_version)
        for box in sel.merge_boxes().selection_boxes:

            #loops over the current selection box's x, y, z coordinates.
            for (x, y, z) in box:
                #handles the case where a chunk may not be able to be read.
                #gets info about the block (the_block, nbt_data, water_logged_blocks)
                (block, block_entity, extras) = self._get_vanilla_block(dim, world, x, y, z, trans)
                
                #checks if the block has a block entity or not.
                if block_entity is not None:

                    #checks if the "Items" tag is in the block_entity,
                    #modifies and creates new nbt in the block_entity.
                    #adds the block_entity_id to a list.
                    block_entity_id = self._get_be_id(block_entity)
                    if "Items" in block_entity.nbt:
                        if block_entity_id in ["Chest", "Barrel"]:
                            if len(block_entity.nbt["Items"]) > 0 or "LootTable" not in block_entity.nbt:

                                #sets the block_entity block with updated NBT.
                                world.set_version_block(x, y, z, dim, mc_version, block, block_entity)

                                #counts + 1 for every block_entity it finds.
                                containers_count+=1
                                if block_entity_id not in containers_found:
                                    containers_found.append((block_entity_id, x, y, z))

        #completion message and block_entity meta.
        print ("Finished processing!")
        print ()
        print ("MC Platform: "+str(platform))
        print ("MC Version: "+str(world_version))
        print ()
        print ("Total empty containers found: "+str(containers_count))

        #Checks if there were more than 0 containers.
        if containers_count > 0:
            print ()
            print ("Types of containers found: ")
            print ('\n'.join(map(str, list(containers_found)))) 
        else:
            wx.MessageBox("(ERROR!) There are no valid containers found!/nPlease try again...")

#simple export options.
export = {
    "name": "Find Opened Chest & Barrels",
    "operation": FindOpenedChests,
}