#You may use this plugin for only non commercial purposes aka non Minecraft Marketplace content.
#This plugin only works if Minecraft Bedrock is installed on Windows10 OS!

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
    "Remove Not Ore": "Removes all blocks besides ore types in the selection boxes.",
    "Remove Not Sign": "Removes all blocks besides sign types in the selection boxes.",
    "Remove Not Glass": "Removes all blocks besides glass types in the selection boxes.",
    "Remove Not TileEntity": "Removes all blocks besides Tile Entity types in the selection boxes."
}

for rmode in get_all_block_types():
    MODES["Remove Not "+str(rmode).title()] = "Removes all blocks besides "+str(rmode.lower())+" types in the selection boxes.",

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
                value="This script will search the amulet selection and find containers such as chest, barrels, ect and set them with the selected loot operation.\n",
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
        self.canvas.run_operation(lambda: self._show_coordinates())

    def _get_vanilla_block(self, dim, world, x, y, z, trans):
        #barrowed from the amulet api. #thanks gentlegiant.
        cx, cz = block_coords_to_chunk_coords(x, z)
        offset_x, offset_z = x - 16 * cx, z - 16 * cz

        chunk = world.get_chunk(cx, cz, dim)
        runtime_id = chunk.blocks[offset_x, y, offset_z]

        return trans.block.from_universal(chunk.block_palette[runtime_id], chunk.block_entities.get((x, y, z), None))

    def _show_coordinates(self):
        op_mode = self._mode.GetString(self._mode.GetSelection())

        world = self.world

        sel = self.canvas.selection.selection_group
        dim = self.canvas.dimension

        stair_types = [
            "brick_stairs",
            "stone_brick_stairs",
            "nether_brick_stairs",
            "sandstone_stairs",
            "spruce_stairs",
            "birch_stairs",
            "jungle_stairs",
            "oak_stairs",
            "quartz_stairs",
            "acacia_stairs",
            "dark_oak_stairs",
            "stone_stairs",
            "red_sandstone_stairs",
            "purpur_stairs",
            "prismarine_stairs",
            "dark_prismarine_stairs",
            "prismarine_bricks_stairs",
            "crimson_stairs",
            "warped_stairs",
            "cut_copper_stairs",
            "exposed_cut_copper_stairs",
            "weathered_cut_copper_stairs",
            "oxidized_cut_copper_stairs",
            "waxed_cut_copper_stairs",
            "waxed_exposed_cut_copper_stairs",
            "waxed_weathered_cut_copper_stairs",
            "granite_stairs",
            "stairs",
            "diorite_stairs",
            "andesite_stairs",
            "polished_granite_stairs",
            "polished_diorite_stairs",
            "polished_andesite_stairs",
            "mossy_stone_brick_stairs",
            "smooth_red_sandstone_stairs",
            "smooth_sandstone_stairs",
            "end_brick_stairs",
            "mossy_cobblestone_stairs",
            "normal_stone_stairs",
            "red_nether_brick_stairs",
            "smooth_quartz_stairs",
            "polished_blackstone_brick_stairs",
            "blackstone_stairs",
            "cobbled_deepslate_stairs",
            "polished_deepslate_stairs",
            "deepslate_tile_stairs",
            "deepslate_brick_stairs",
            "polished_blackstone_stairs",
            "waxed_oxidized_cut_copper_stairs"
        ]

        sign_types = [
            "birch_standing_sign",
            "birch_wall_sign",
            "jungle_standing_sign",
            "jungle_wall_sign",
            "acacia_standing_sign",
            "acacia_wall_sign",
            "darkoak_standing_sign",
            "darkoak_wall_sign",
            "spruce_wall_sign",
            "spruce_standing_sign",
            "crimson_standing_sign",
            "warped_standing_sign",
            "crimson_wall_sign",
            "warped_wall_sign",
            "sign",
            "wall_sign"
        ]

        glass_types = [
            "glass",
            "stained_glass",
            "hard_glass",
            "hard_stained_glass",
            "tinted_glass",
            "hard_stained_glass_pane",
            "hard_glass_pane",
            "glass_pane",
            "stained_glass_pane",
            "white_stained_glass_pane",
            "orange_stained_glass_pane",
            "magenta_stained_glass_pane",
            "light_blue_stained_glass_pane",
            "yellow_stained_glass_pane",
            "lime_stained_glass_pane",
            "pink_stained_glass_pane",
            "gray_stained_glass_pane",
            "light_gray_stained_glass_pane",
            "purple_stained_glass_pane",
            "blue_stained_glass_pane",
            "brown_stained_glass_pane",
            "green_stained_glass_pane",
            "red_stained_glass_pane",
            "black_stained_glass_pane"
        ]

        glass_types = [
            "glass",
            "stained_glass",
            "hard_glass",
            "hard_stained_glass",
            "tinted_glass",
            "hard_stained_glass_pane",
            "hard_glass_pane",
            "glass_pane",
            "stained_glass_pane",
            "white_stained_glass_pane",
            "orange_stained_glass_pane",
            "magenta_stained_glass_pane",
            "light_blue_stained_glass_pane",
            "yellow_stained_glass_pane",
            "lime_stained_glass_pane",
            "pink_stained_glass_pane",
            "gray_stained_glass_pane",
            "light_gray_stained_glass_pane",
            "purple_stained_glass_pane",
            "blue_stained_glass_pane",
            "brown_stained_glass_pane",
            "green_stained_glass_pane",
            "red_stained_glass_pane",
            "black_stained_glass_pane"
        ]

        wool_types = [
            "wool",
            "orange_wool",
            "magenta_wool",
            "light_blue_wool",
            "yellow_wool",
            "lime_wool",
            "pink_wool",
            "gray_wool",
            "light_gray_wool",
            "cyan_wool",
            "purple_wool",
            "blue_wool",
            "brown_wool",
            "green_wool",
            "red_wool",
            "black_wool"
        ]

        ore_types = [
            "gold_ore",
            "iron_ore",
            "coal_ore",
            "lapis_ore",
            "emerald_ore",
            "diamond_ore",
            "redstone_ore",
            "copper_ore",
            "quartz_ore"
        ]

        tile_types = [
            "barrel",
            "chest",
            "dispenser",
            "dropper",
            "trapped_chest",
            "ender_chest",
            "furnace",
            "lit_furnace",
            "standing_sign",
            "portal",
            "end_gateway",
            "structure_block",
            "command_block",
            "soul_campfire",
            "lectern",
            "smoker",
            "lit_smoker",
            "bell",
            "campfire",
            "lava_cauldron",
            "jigsaw",
            "lit_blast_furnace",
            "blast_furnace",
            "stickypistonarmcollision",
            "bee_nest",
            "beehive",
            "standing_banner",
            "wall_banner",
            "daylight_detector_inverted",
            "jukebox",
            "mob_spawner",
            "beacon",
            "skull",
            "hopper",
            "piston",
            "pistonarmcollision",
            "sticky_piston",
            "enchanting_table",
            "brewing_stand",
            "end_portal",
            "cauldron",
            "daylight_detector",
            "unpowered_comparato",
            "powered_comparator",
            "repeating_command_block",
            "chain_command_block",
            "chalkboard"
        ]

        selected_types = []

        platform = world.level_wrapper.platform
        world_version = world.level_wrapper.version

        trans = world.translation_manager.get_version(platform, world_version)

        mc_version = (platform, world_version)

        print ("Started editing blocks...")
        for box in sel.merge_boxes().selection_boxes:
            for (x, y, z) in box:
                try:
                    (block, block_entity, extras) = self._get_vanilla_block(dim, world, x, y, z, trans)
                    if block.base_name not in selected_types:
                        air_block = Block("minecraft", "air")
                        world.set_version_block(x, y, z, dim, mc_version, air_block, {})
                except:
                    pass
        print ("Finished editing blocks!")

export = {
    "name": "Remove Not",
    "operation": RemoveNot,
}
