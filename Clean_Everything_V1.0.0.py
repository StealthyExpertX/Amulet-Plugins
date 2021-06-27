#You may use this plugin for only non commercial purposes aka non Minecraft Marketplace content.

#v1.0.0 - Clean Everything

#Plugin removes blocks or block types based on your mode and currently only ores are supported,
#More modes will be added in updates when possible.

#Twitter: @RedstonerLabs
#Discord: StealthyExpert#8940

import numpy
from typing import TYPE_CHECKING, Tuple

from amulet.api.wrapper import Interface, EntityIDType, EntityCoordType

import wx
import ast
import json
import os
import glob
import random

import re

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

MODES = {
    "Clean Not Ores": "Removes all blocks besides ores in the amulet selection boxes."
}

class RemoveNot(wx.Panel, DefaultOperationUI):
    def __init__(
        self,
        parent: wx.Window,
        canvas: "EditCanvas",
        world: "BaseLevel",
        options_path: str,
    ):
        wx.Panel.__init__(self, parent)
        DefaultOperationUI.__init__(self, parent, canvas, world, options_path)
        self.Freeze()

        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self._sizer)

        options = self._load_options({})
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._sizer.Add(top_sizer, 0, wx.EXPAND | wx.ALL, 5)

        help_button = wx.BitmapButton(
            self, bitmap=image.icon.tablericons.help.bitmap(22, 22)
        )
        top_sizer.Add(help_button)

        def on_button(evt):
            dialog = SimpleDialog(self, "Help Dialog")
            text = wx.TextCtrl(
                dialog,
                value="This script will search the amulet selection and set air blocks where ever it doesn't find a block type matching your MODE selection.\n",
                style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_BESTWRAP,
            )
            dialog.sizer.Add(text, 1, wx.EXPAND)
            dialog.ShowModal()
            evt.Skip()

        help_button.Bind(wx.EVT_BUTTON, on_button)

        self._mode = wx.Choice(self, choices=list(MODES.keys()))
        self._mode.SetSelection(0)
        top_sizer.Add(self._mode, 1, wx.EXPAND | wx.LEFT, 5)
        self._mode.Bind(wx.EVT_CHOICE, self._on_mode_change)

        self._mode_description = wx.TextCtrl(
            self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_BESTWRAP
        )
        self._sizer.Add(self._mode_description, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        self._mode_description.SetLabel(
            MODES[self._mode.GetString(self._mode.GetSelection())]
        )
        self._mode_description.Fit()

        
        self._run_button = wx.Button(self, label="Run Operation")
        self._run_button.Bind(wx.EVT_BUTTON, self._run_operation)
        self._sizer.Add(self._run_button, 0, wx.ALL | wx.ALIGN_CENTRE_HORIZONTAL, 5)

        self.Layout()
        self.Thaw()

    @property
    def wx_add_options(self) -> Tuple[int, ...]:
        return (1,)

    def _on_mode_change(self, evt):
        self._mode_description.SetLabel(
            MODES[self._mode.GetString(self._mode.GetSelection())]
        )
        self._mode_description.Fit()
        self.Layout()
        evt.Skip()

    def _on_pick_block_button(self, evt):
        """Set up listening for the block click"""
        self._show_pointer = True

    def _run_operation(self, _):
        self.canvas.run_operation(lambda: self._clean_everything_but())

    #gets a minecraft block in vanilla format instead of universal.
    def _get_vanilla_block(self, dim, world, x, y, z, trans):
        #barrowed from the amulet api. #thanks gentlegiant.
        cx, cz = block_coords_to_chunk_coords(x, z)
        offset_x, offset_z = x - 16 * cx, z - 16 * cz

        chunk = world.get_chunk(cx, cz, dim)
        runtime_id = chunk.blocks[offset_x, y, offset_z]

        return trans.block.from_universal(chunk.block_palette[runtime_id], chunk.block_entities.get((x, y, z), None))

    def _refresh_chunk(self, dimension, world, x, z):
       cx, cz = block_coords_to_chunk_coords(x, z)
       chunk = world.get_chunk(cx, cz, dimension)
       chunk.changed = True

    def _clean_everything_but(self):
        #gets mode selection.
        op_mode = self._mode.GetString(self._mode.GetSelection())

        #gets world, dimension, selection.
        world = self.world
        dim = self.canvas.dimension
        sel = self.canvas.selection.selection_group

        #list of all ore block names.
        ore_names = ["gold_ore","iron_ore","coal_ore","lapis_ore","emerald_ore","diamond_ore","redstone_ore","copper_ore","quartz_ore"]

        #gets platform & version.
        platform = world.level_wrapper.platform
        world_version = world.level_wrapper.version

        #world format translation manager
        trans = world.translation_manager.get_version(platform, world_version)

        #compiles platform and version into an MC version/platform
        mc_version = (platform, world_version)

        #counters for counting blocks.
        dirty_block = 0
        clean_block = 0

        #air block in minecraft works for java & bedrock basically like writing 'air_block = (0, 0)' in MCEdit.
        air_block = Block("minecraft", "air")

        #loops over x, y, z and gets a vanilla block and sets a block if the block is not in the names list.
        print ("Started editing blocks...")
        for box in sel.merge_boxes().selection_boxes:
            for (x, y, z) in box:
                try:
                    #gets block object
                    (block, tile_entity, _) = self._get_vanilla_block(dim, world, x, y, z, trans)

                    #gets block name and checks if it doesn't exist in ore names and if not set an air block.
                    if block.base_name not in ore_names:
                        world.set_version_block(x, y, z, dim, mc_version, air_block, tile_entity)
                        self._refresh_chunk(dim, world, x, z)
                        dirty_block+=1
                    else:
                        clean_block+=1
                except:
                    pass

        #prints message and block count information.
        print ("Finished editing blocks in the selection boxes!")
        print ("Removed "+str(dirty_block)+" blocks")
        print ("Kept "+str(clean_block)+" blocks")

export = {
    "name": "Clean Everything v1.0",
    "operation": RemoveNot,
}
