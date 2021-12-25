#You may use this plugin for only non commercial purposes aka non Minecraft Marketplace content.

#This loot table plugin supports java, bedrock and possibly other platforms!
#I gave it my best shot so let me know if it works on mac-os or linux?

#Currently it updates the UI based on the platform and version of the world,
#This plugin was designed to make adding loot tables to containers easier 
#and to work on as many platforms and versions of Minecraft as possible.

#Twitter: @RedstonerLabs
#Discord: StealthyExpert#8940


#VERSION DOCS this is for tracking loot tables between versions.

# Cave & Cliffs #Added no loot tables.
# JAVA: 2724
# BEDROCK: (1,17,0)

# Nether Update #ADDED THE nether loot tables.
# JAVA: 2566
# BEDROCK: (1,16,0)

# Buzzy Bees #Added no loot tables but removed one on java but not bedrock.
# JAVA: 2225
# BEDROCK: (1,14,0)

# Village & Pillage #ADDED THE "village" loot tables directory and added new loot tables for villages.
# JAVA: 1952
# BEDROCK: (1,10,0)

# Update Aquatic #ADDED THE ocean treasure loot tables.
# JAVA: 1519
# BEDROCK: (1,5,0)


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

#used to see if the user has internet - the code this is connected to grabs a template behavior pack and extracts loot_tables.
test_url = 'http://google.com'

#operation mode types.
operation_modes = {
    "Randomize": "Set containers with randomized vanilla loot tables.",
    "Vanilla": "Set containers with a selected vanilla loot table name.",
    "Custom": "Set containers with a custom inputed loot table path.",
    "Remove LootTables": "Remove loot table nbt in containers.",
}

loot_table_seed = 0

#selected loot table path for the custom operation.
selected_custom_table = "loot_tables/custom.json"

#supported platform types to look for.
platform_names = ['java', 'bedrock']

#bedrock op loot tables.
#these loot tables contain items that are considered too op and have high enchants & loot, etc.
#updated to bedrock_1.17.0 & java_1.17
hardcoded_ops = [
    "loot_tables/chests/bastion_treasure.json",
    "loot_tables/chests/shipwrecksupply.json",
    "loot_tables/chests/buriedtreasure.json",
    "loot_tables/chests/end_city_treasure.json",
    "loot_tables/chests/spawn_bonus_chest.json",
    "loot_tables/chests/shipwrecktreasure.json"
]

#this table is hardcoded for bedrock, for the edge case that all other loot tables extractions fail for bedrock but only for the current update.
loots_hardcoded = [
    "loot_tables/chests/abandoned_mineshaft.json",
    "loot_tables/chests/bastion_bridge.json",
    "loot_tables/chests/bastion_hoglin_stable.json",
    "loot_tables/chests/bastion_other.json",
    "loot_tables/chests/bastion_treasure.json",
    "loot_tables/chests/buriedtreasure.json",
    "loot_tables/chests/desert_pyramid.json",
    "loot_tables/chests/dispenser_trap.json",
    "loot_tables/chests/end_city_treasure.json",
    "loot_tables/chests/igloo_chest.json",
    "loot_tables/chests/jungle_temple.json",
    "loot_tables/chests/monster_room.json",
    "loot_tables/chests/nether_bridge.json",
    "loot_tables/chests/pillager_outpost.json",
    "loot_tables/chests/ruined_portal.json",
    "loot_tables/chests/shipwreck.json",
    "loot_tables/chests/shipwrecksupply.json",
    "loot_tables/chests/shipwrecktreasure.json",
    "loot_tables/chests/simple_dungeon.json",
    "loot_tables/chests/spawn_bonus_chest.json",
    "loot_tables/chests/stronghold_corridor.json",
    "loot_tables/chests/stronghold_crossing.json",
    "loot_tables/chests/stronghold_library.json",
    "loot_tables/chests/underwater_ruin_big.json",
    "loot_tables/chests/underwater_ruin_small.json",
    "loot_tables/chests/village_blacksmith.json",
    "loot_tables/chests/village_two_room_house.json",
    "loot_tables/chests/woodland_mansion.json",
    "loot_tables/chests/village/village_armorer.json",
    "loot_tables/chests/village/village_butcher.json",
    "loot_tables/chests/village/village_cartographer.json",
    "loot_tables/chests/village/village_desert_house.json",
    "loot_tables/chests/village/village_fletcher.json",
    "loot_tables/chests/village/village_mason.json",
    "loot_tables/chests/village/village_plains_house.json",
    "loot_tables/chests/village/village_savanna_house.json",
    "loot_tables/chests/village/village_shepherd.json",
    "loot_tables/chests/village/village_snowy_house.json",
    "loot_tables/chests/village/village_taiga_house.json",
    "loot_tables/chests/village/village_tannery.json",
    "loot_tables/chests/village/village_temple.json",
    "loot_tables/chests/village/village_toolsmith.json",
    "loot_tables/chests/village/village_weaponsmith.json"
]

#this table is hardcoded for bedrock & java - techically universally supported btw both platforms.
#for the edge case that all other loot tables extraction methods fail but only for the current update.
loots_universal_table = [
    "loot_tables/chests/abandoned_mineshaft.json",
    "loot_tables/chests/bastion_bridge.json",
    "loot_tables/chests/bastion_hoglin_stable.json",
    "loot_tables/chests/bastion_other.json",
    "loot_tables/chests/bastion_treasure.json",
    "loot_tables/chests/buriedtreasure.json",
    "loot_tables/chests/desert_pyramid.json",
    "loot_tables/chests/end_city_treasure.json",
    "loot_tables/chests/igloo_chest.json",
    "loot_tables/chests/jungle_temple.json",
    "loot_tables/chests/nether_bridge.json",
    "loot_tables/chests/pillager_outpost.json",
    "loot_tables/chests/ruined_portal.json",
    "loot_tables/chests/simple_dungeon.json",
    "loot_tables/chests/spawn_bonus_chest.json",
    "loot_tables/chests/stronghold_corridor.json",
    "loot_tables/chests/stronghold_crossing.json",
    "loot_tables/chests/stronghold_library.json",
    "loot_tables/chests/underwater_ruin_big.json",
    "loot_tables/chests/underwater_ruin_small.json",
    "loot_tables/chests/woodland_mansion.json",
    "loot_tables/chests/village/village_armorer.json",
    "loot_tables/chests/village/village_butcher.json",
    "loot_tables/chests/village/village_cartographer.json",
    "loot_tables/chests/village/village_desert_house.json",
    "loot_tables/chests/village/village_fletcher.json",
    "loot_tables/chests/village/village_mason.json",
    "loot_tables/chests/village/village_plains_house.json",
    "loot_tables/chests/village/village_savanna_house.json",
    "loot_tables/chests/village/village_shepherd.json",
    "loot_tables/chests/village/village_snowy_house.json",
    "loot_tables/chests/village/village_taiga_house.json",
    "loot_tables/chests/village/village_tannery.json",
    "loot_tables/chests/village/village_temple.json",
    "loot_tables/chests/village/village_toolsmith.json",
    "loot_tables/chests/village/village_weaponsmith.json"
]

#loot table settings for randomizing.
quality_names = ['Epic Quality', "Normal Quality"] 

#loot table version mapping for bedrock.
#remove these loot strings or rename their paths durring universal loot table conversion.
bedrock_remove_tables = {
    "pre_1.16.0":{
        "loot_tables/chests/bastion_bridge.json": None,
        "loot_tables/chests/bastion_hoglin_stable.json": None,
        "loot_tables/chests/bastion_other.json": None,
        "loot_tables/chests/bastion_treasure.json": None,
        "loot_tables/chests/ruined_portal.json": None
    },
    "pre_1.10.0":{
        "loot_tables/chests/village/village_armorer.json": None,
        "loot_tables/chests/village/village_butcher.json": None,
        "loot_tables/chests/village/village_cartographer.json": None,
        "loot_tables/chests/village/village_desert_house.json": None,
        "loot_tables/chests/village/village_mason.json": None,
        "loot_tables/chests/village/village_plains_house.json": None,
        "loot_tables/chests/village/village_savanna_house.json": None,
        "loot_tables/chests/village/village_shepherd.json": None,
        "loot_tables/chests/village/village_snowy_house.json": None,
        "loot_tables/chests/village/village_taiga_house.json": None,
        "loot_tables/chests/village/village_tannery.json": None,
        "loot_tables/chests/village/village_temple.json": None,
        "loot_tables/chests/village/village_toolsmith.json": None,
        "loot_tables/chests/village/village_weaponsmith.json": None
    },
    "pre_1.4.0":{
        "loot_tables/chests/buriedtreasure.json": None,
        "loot_tables/chests/buriedtreasure.json": None,
        "loot_tables/chests/shipwrecksupply.json": None,
        "loot_tables/chests/shipwrecktreasure.json": None,
        "loot_tables/chests/underwater_ruin_big.json": None,
        "loot_tables/chests/underwater_ruin_small.json": None,
    },
    '*': { #any version renaming or deletion.
        "loot_tables/chests/jungle_temple_dispenser.json": "loot_tables/chests/dispenser_trap.json",
        "loot_tables/chests/shipwreck_map.json": "loot_tables/chests/shipwreck.json",
        "loot_tables/chests/shipwreck_supply.json": "loot_tables/chests/shipwrecksupply.json",
        "loot_tables/chests/shipwreck_treasure.json": "loot_tables/chests/shipwrecktreasure.json"
    }
}

#loot table version mapping for java.
#remove these loot strings ore remove them durring universal loot table conversion.
java_remove_tables = {
    'pre_2566':{ #pre java nether update.
        "loot_tables/chests/bastion_bridge.json": None,
        "loot_tables/chests/bastion_hoglin_stable.json": None,
        "loot_tables/chests/bastion_other.json": None,
        "loot_tables/chests/bastion_treasure.json": None,
        "loot_tables/chests/ruined_portal.json": None
    },
    'pre_2225':{ #pre java busy bees.
        "loot_tables/chests/village_blacksmith.json": None
    },
    'pre_1952':{ #pre java village & pillage.
        "loot_tables/chests/village/village_armorer.json": None,
        "loot_tables/chests/village/village_butcher.json": None,
        "loot_tables/chests/village/village_cartographer.json": None,
        "loot_tables/chests/village/village_desert_house.json": None,
        "loot_tables/chests/village/village_mason.json": None,
        "loot_tables/chests/village/village_plains_house.json": None,
        "loot_tables/chests/village/village_savanna_house.json": None,
        "loot_tables/chests/village/village_shepherd.json": None,
        "loot_tables/chests/village/village_snowy_house.json": None,
        "loot_tables/chests/village/village_taiga_house.json": None,
        "loot_tables/chests/village/village_tannery.json": None,
        "loot_tables/chests/village/village_temple.json": None,
        "loot_tables/chests/village/village_toolsmith.json": None,
        "loot_tables/chests/village/village_weaponsmith.json": None
    },
    'pre_1519':{ #pre java update aquatic.
        "loot_tables/chests/buriedtreasure.json": None,
        "loot_tables/chests/shipwreck.json": None,
        "loot_tables/chests/shipwrecksupply.json": None,
        "loot_tables/chests/shipwrecktreasure.json": None,
        "loot_tables/chests/underwater_ruin_big.json": None,
        "loot_tables/chests/underwater_ruin_small.json": None,
        "loot_tables/chests/shipwreck_map.json": None,
        "loot_tables/chests/shipwreck_supply.json": None,
        "loot_tables/chests/shipwreck_treasure.json": None
    },
    '*': { #any version of minecraft java.
        "loot_tables/chests/village_two_room_house.json": None,
        "loot_tables/chests/monster_room.json": None,
        "loot_tables/chests/dispenser_trap.json": "loot_tables/chests/jungle_temple_dispenser.json",
        "loot_tables/chests/shipwreck.json": "loot_tables/chests/shipwreck_map.json",
        "loot_tables/chests/shipwrecksupply.json": "loot_tables/chests/shipwreck_supply.json",
        "loot_tables/chests/shipwrecktreasure.json": "loot_tables/chests/shipwreck_treasure.json"
        
    }
    #anything not defined will convert as is.
}

#loot table version mapping for universal.
#remove these loot strings durring universal loot table conversion.
#these are not compatiable in some versions / platforms we remove them in the list generation in a worse case.
universal_remove_tables = {
    "loot_tables/chests/bastion_bridge.json": None,
    "loot_tables/chests/bastion_hoglin_stable.json": None,
    "loot_tables/chests/bastion_other.json": None,
    "loot_tables/chests/bastion_treasure.json": None,
    "loot_tables/chests/ruined_portal.json": None,
    "loot_tables/chests/jungle_temple_dispenser.json":None,
    "loot_tables/chests/dispenser_trap.json": None,
    "loot_tables/chests/shipwreck_map.json": None,
    "loot_tables/chests/shipwreck.json": None,
    "loot_tables/chests/shipwrecktreasure.json": None,
    "loot_tables/chests/shipwreck_treasure.json": None,
    "loot_tables/chests/shipwreck_supply.json": None,
    "loot_tables/chests/shipwrecksupply.json": None,
    "loot_tables/chests/monster_room.json": None,
    "loot_tables/chests/village_two_room_house.json": None,
    "loot_tables/chests/village_blacksmith.json": None,
    "loot_tables/chests/village/village_armorer.json": None,
    "loot_tables/chests/village/village_butcher.json": None,
    "loot_tables/chests/village/village_cartographer.json": None,
    "loot_tables/chests/village/village_desert_house.json": None,
    "loot_tables/chests/village/village_mason.json": None,
    "loot_tables/chests/village/village_plains_house.json": None,
    "loot_tables/chests/village/village_savanna_house.json": None,
    "loot_tables/chests/village/village_shepherd.json": None,
    "loot_tables/chests/village/village_snowy_house.json": None,
    "loot_tables/chests/village/village_taiga_house.json": None,
    "loot_tables/chests/village/village_tannery.json": None,
    "loot_tables/chests/village/village_temple.json": None,
    "loot_tables/chests/village/village_toolsmith.json": None,
    "loot_tables/chests/village/village_weaponsmith.json": None
}

#wasn't able to data drive the tile_entity list of ids for containers.
#will revisit this at a later date and make this data driven and the UI as well possibly from a github repo.
chkdict = {
    "All Containers": "*",
    "Barrels": [
        "minecraft:barrel",
        "Barrel"
    ],
    "Chests": [
        "minecraft:chest",
        "minecraft:trapped_chest",
        "Chest",
        "TrappedChest"
    ],
    "Dispensers": [
        "minecraft:dispenser",
        "Dispenser"
    ],
    "Droppers": [
        "minecraft:dropper",
        "Dropper"
    ],
    "Hoppers": [
        "minecraft:hopper",
        "Hopper"
    ],
    "ShulkerBoxes": [
        "minecraft:shulker_box",
        "ShulkerBox"
    ]
}

#global objects.
plat = None
loot_table_src = {}

class TabOne(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        
        tab1text = "This plugin allows you to do loot table based operations,\n"\
        "- 'Vanilla' which allows you to set vanilla loot tables using the path list supplied in this plugin."\
        "- 'Random' which allows you to set fully random loot tables."\
        "- 'Custom' which allows you to set custom loot table paths supplied by the user."\
        "- 'Remove' which allows you to remove custom loot tables from containers in the selection."\
        "- 'Clear' which allows you to remove items from containers in the selection.\n"
        "- 'Replace' which allows you to replace loot tables in containers in the selection.\n"
        t = wx.StaticText(self, 0, tab1text)
        self._sizer2 = wx.FlexGridSizer(0, 4, 0, 4) #verticle shape top to bottom for main dialog.
        self._sizer2.Add(t, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 2)
        self.SetSizer(self._sizer2)


        "\n           MULTIBLES"\
        "\n           you can use commas or colons or semi colons to seperate more then one loot table."\
        "\n           example (1): loot_tables/custom/loot_table_1.json, loot_tables/custom/loot_table_2.json"\
        "\n           example (2): loot_tables/custom/loot_table_1.json: loot_tables/custom/loot_table_2.json"\
        "\n           example (3): loot_tables/custom/loot_table_1.json; loot_tables/custom/loot_table_2.json\n"\
        # "\n           WEIGHTED RANDOM"\
        # "\n           you can use % or = characters prefixing followed by a chance for each loot table to assign a random chance for that table to be used."\
        # "\n           if you do not assign a % or = chance to a loot table it will have the remaining chance will be applied to all objects."\
        # "\n           note all %'s used must add upto 100% and not above 100% as this is invalid."\
        # "\n           example (1): 10%loot_tables/custom/loot_table_1.json, 90%loot_tables/custom/loot_table_2.json"\
        # "\n           example (2): 10=loot_tables/custom/loot_table_1.json, 90=loot_tables/custom/loot_table_2.json\n"\
        # "\n           VARIABLES"\
        # "\n           you can use variables to assign cool functions to your strings such as\n"\
        # "\n           <RANDOM> which will insert any random loot table."\
        # "\n           <RANDOM_RARE> which will insert a random loot table from high quality loot tables list."\
        # "\n           <RANDOM_COMMON> which will insert a random loot table from high quality loot tables."\
        # "\n           <RANDOM_VILLAGE> which will insert a random loot table from village loot tables."\
        # "\n           <RANDOM_OCEAN> which will insert a random loot table from ocean loot tables."\
        # "\n           <RANDOM_NETHER> which will insert a random loot table from nether loot tables."\
        # "\n           example (1): <RANDOM>, loot_tables/custom/loot_table_2.json"\
        # "\n           example (2): loot_tables/custom/loot_table_1.json, <RANDOM_RARE>"\
        # "\n           example (3): <RANDOM_COMMON>"\
        # "\n           example (4): 30%loot_tables/custom/loot_table_1.json, 70%<RANDOM_OCEAN>\n"

class TabTwo(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        tab1text ="\nyou can use a single loot table as well like this. \nexample: loot_tables/custom/loot_table_1.json"\

        t = wx.StaticText(self, 0, tab1text)
        self._sizer2 = wx.FlexGridSizer(0, 4, 0, 4) #verticle shape top to bottom for main dialog.
        self._sizer2.Add(t, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 2)
        self.SetSizer(self._sizer2)

class TabThree(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        tab1text ="you can use commas or colons or semi colons to seperate more then one loot table.\n"\
        "usage examples:\n"\
        "loot_tables/custom/loot_table_1.json, loot_tables/custom/loot_table_2.json\n"\
        "loot_tables/custom/loot_table_1.json: loot_tables/custom/loot_table_2.json\n"\
        "loot_tables/custom/loot_table_1.json; loot_tables/custom/loot_table_2.json"

        t = wx.StaticText(self, 0, tab1text)
        self._sizer2 = wx.FlexGridSizer(0, 4, 0, 4) #verticle shape top to bottom for main dialog.
        self._sizer2.Add(t, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 2)
        self.SetSizer(self._sizer2)

class SetLootTables(wx.Panel, DefaultOperationUI):
    def __init__(
        self,
        parent: wx.Window,
        canvas: "EditCanvas",
        world: "BaseLevel",
        options_path: str,
    ):

        platform = world.level_wrapper.platform
        world_version = world.level_wrapper.version
        
        #global variables, yes I know this is bad but needed for the context to get it working!
        global check_var
        global plat #plat is a global platform & version tuple object.
        global loot_table_src #made loot table source that gets generated to populate the list.
        global sel_block_entities #selected block entities to fill.
        global all_block_entities #all the block entities as one object.
        global startup
        global text_change_bool

        self.check_var = False
        self.startup = True
        self.text_change_bool = True

        #sets platform and world version as the plat object.
        plat = (platform, world_version)

        #gathers the loot tables and formats them to populate the loot table list.
        loot_table_src = {}
        for tbls in self._loot_table_strs((platform, world_version)):
            loot_table_src[os.path.basename(tbls)] = tbls

        #sets the UI pannel
        wx.Panel.__init__(self, parent)
        DefaultOperationUI.__init__(self, parent, canvas, world, options_path)
        self.Freeze()

        self._sizer = wx.FlexGridSizer(0, 1, 2, 0) #verticle shape top to bottom for main dialog.
        self.SetSizer(self._sizer)

        #info button
        top_sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        self._sizer.Add(top_sizer2, 0, wx.EXPAND | wx.ALL, 5)

        help_button = wx.BitmapButton(
            self, bitmap=image.icon.tablericons.help.bitmap(22, 22)
        )
        top_sizer2.Add(help_button, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 1)

        #loads the default options to be overwitten later.
        options = self._load_options({})

        #creates a box sizer object and sets it.
        top_sizer = wx.FlexGridSizer(0, 1, 2, 0)
        self._sizer.Add(top_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 1)

        #info button event brings up a panel with tabs / infomation.
        def _on_button(evt):
            #creates the button with the default content.
            dialog = SimpleDialog(self, "Plugin Info")
            
            #creates a notebook object.
            notebooks = wx.Notebook(dialog)
            

            # Create the tab windows.
            tab1 = TabOne(notebooks)
            tab2 = TabTwo(notebooks)
            tab3 = TabThree(notebooks)

            # Add the panels to the tabs to name them.
            notebooks.AddPage(tab1, "Operation Modes")
            notebooks.AddPage(tab2, "Basic Usage")
            notebooks.AddPage(tab3, "Multible Usage")

            #handle sizers and shows and skip calls.
            dialog.sizer.Add(notebooks, 3, wx.ALL, 3)
            dialog.ShowModal()
            evt.Skip()

        help_button.Bind(wx.EVT_BUTTON, _on_button)

        #text label for mode description
        self._label_txt1=wx.StaticText(self, 0, label=' Loot Mode (Description)')
        self._sizer.Add(self._label_txt1, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 0)

        #text label for mode selection
        self._label_txt2=wx.StaticText(self, 0, label=' Choose (Loot Mode)')
        top_sizer.Add(self._label_txt2, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 0)

        #choicebox for operation mode selection.
        self._mode = wx.Choice(self, choices=list(operation_modes.keys()))
        self._mode.SetSelection(1)
        top_sizer.Add(self._mode, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 1)

        #text label for loot table selection
        self._label_txt3=wx.StaticText(self, 0, label=' Choose (Loot Table)')
        top_sizer.Add(self._label_txt3, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 0)

        #choicebox for loot table selection.
        self._sel_loot = wx.Choice(self, choices=list(loot_table_src.keys()))
        self._sel_loot.SetSelection(0)
        top_sizer.Add(self._sel_loot, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 0)

        #handles operation_mode changes.
        self._mode.Bind(wx.EVT_CHOICE, self._on_mode_change)

        #custom loot tables textbox
        self._label_txt4=wx.StaticText(self, 0, label=' Write (Custom Loot Tables)')
        
        
        #set a font.
        #self._label_txt4.SetFont(wx.Font(12, wx.ROMAN, wx.ITALIC, wx.NORMAL))
        top_sizer.Add(self._label_txt4, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 0)

        # #custom loot tables textbox
        # self.loot_textbox = wx.TextCtrl(
            # self, style=wx.TE_MULTILINE | wx.HSCROLL | wx.TE_NO_VSCROLL | wx.TE_BESTWRAP, size=(-1, -1)
        # )
        #GetMultilineTextExtent()
        self.loot_textbox = wx.richtext.RichTextCtrl(self,style=wx.TE_MULTILINE, size=(280,150))
        self.loot_textbox.SetValue("loot_tables/folder_name/table_name.json")
        self.loot_textbox.SetStyle(0, 1000, wx.TextAttr((169, 169, 169, 255), (255, 255, 255, 128)))
        self.loot_textbox.Bind(wx.EVT_TEXT, self._changed_text, self.loot_textbox)
        self.loot_textbox.Bind(wx.EVT_SET_FOCUS, self._changed_text_focus, self.loot_textbox)
        self.loot_textbox.Bind(wx.EVT_KILL_FOCUS, self._changed_text_unfocus, self.loot_textbox)

        top_sizer.Add(self.loot_textbox, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 0)
        
        #text label & spin ctrl for loot table seed
        self._label_txt5=wx.StaticText(self, 0, label=' Choose (Loot Seed)')
        top_sizer.Add(self._label_txt5, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 0)

        self.spin_ctrl = wx.SpinCtrl(self, 0, style=wx.SP_ARROW_KEYS|wx.TE_PROCESS_ENTER)
        self.spin_ctrl.SetRange(int(-2147483648),int(2147483647))

        self.spin_ctrl.Bind(wx.EVT_SPINCTRL, self._on_seed_change)
        self.spin_ctrl.Bind(wx.EVT_TEXT_ENTER, self._on_seed_enter)
        self.spin_ctrl.Bind(wx.EVT_SET_FOCUS, self._on_seed_set_focus)
        self.spin_ctrl.Bind(wx.EVT_KILL_FOCUS, self._on_seed_kill_focus)
        self.spin_ctrl.Bind(wx.EVT_LEAVE_WINDOW, self._on_seed_leave)
        self.spin_ctrl.Bind(wx.EVT_ENTER_WINDOW, self._on_seed_join)
        top_sizer.Add(self.spin_ctrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 0)
        loot_table_seed = 0

        #description text box.
        self._mode_description = wx.TextCtrl(
            self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_BESTWRAP
        )
        self._sizer.Add(self._mode_description, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 0)

        #sets the description label.
        self._mode_description.SetLabel(
            operation_modes[self._mode.GetString(self._mode.GetSelection())]
        )

        self.checklist = wx.CheckListBox(self, 2, pos = (80,10),choices=list(chkdict.keys()) , style=0)
        self.Bind(wx.EVT_LISTBOX, self._click_skipper, self.checklist)
        self.Bind(wx.EVT_CHECKLISTBOX, self._check_list_args, self.checklist)
        self.checklist.Check(0, check=False)
        self.checklist.Check(1, check=False)
        self.checklist.Check(2, check=True)
        self.checklist.Check(3, check=False)
        self.checklist.Check(4, check=False)
        self.checklist.Check(5, check=False)
        self.checklist.Check(6, check=False)
        self._sizer.Add(self.checklist, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 0)

        #quality radio box
        #majorDimension = 1 == HORIZONTAL radios
        #majorDimension = 0 == VERTICAL radios
        self._radio1 = wx.RadioBox(self, label = 'Choose (Loot Option)', pos = (80,10), choices = quality_names,majorDimension = 1, style = 0) 
        self._radio1.Bind(wx.EVT_RADIOBOX,self._on_radio_box)
        self._sizer.Add(self._radio1, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 0)

        self._ignore_empty = wx.CheckBox(self,label="Ignore (Filled Containers)", style=3)
        self._ignore_empty.Bind(wx.EVT_CHECKBOX, self._check_ignore_empties)
        self._sizer.Add(self._ignore_empty, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 3)


        #run button
        self._run_button = wx.Button(self, label="Run Operation")
        self._run_button.Bind(wx.EVT_BUTTON, self._run_operation)
        self._sizer.Add(self._run_button, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, -1)

        #hide the radiobox by default.
        self._radio1.Hide()
        self.loot_textbox.Hide()
        self._label_txt4.Hide()
        self.spin_ctrl.Show()
        self._label_txt5.Show()
        self.Layout()
        self.Thaw()

    @property #handles the wx add option size (height, width) default is (0, 0) 
    #interesting to note that ommiting the 0 on the second index of the tuple works?
    def wx_add_options(self) -> Tuple[int, ...]:
        return (0,)

    #event for when text is edited to change the textbox to blank and change text color to black,
    #change the text back to orginal val when its blank.
    def _changed_text(self, evt):
        if self.loot_textbox.GetValue() == "loot_tables/folder_name/table_name.json":
            self.loot_textbox.SetStyle(0, 1000, wx.TextAttr((169, 169, 169, 255), (255, 255, 255, 128)))
        else:
            self.loot_textbox.SetStyle(0, 32767, wx.TextAttr((0, 0, 0, 255), (255, 255, 255, 128)))

    def _changed_text_focus(self, evt):
        print (str("focus")+self.loot_textbox.GetValue())
        if self.loot_textbox.GetValue() == "loot_tables/folder_name/table_name.json":
            self.loot_textbox.SetStyle(0, 1000, wx.TextAttr((169, 169, 169, 255), (255, 255, 255, 128)))
        else:
            self.loot_textbox.SetStyle(0, 32767, wx.TextAttr((0, 0, 0, 255), (255, 255, 255, 128)))

    def _changed_text_unfocus(self, evt):
        print (str("unfocus")+self.loot_textbox.GetValue())
        if len(self.loot_textbox.GetValue()) == 0:
            self.loot_textbox.SetStyle(0, 1000, wx.TextAttr((169, 169, 169, 255), (255, 255, 255, 128)))
            self.loot_textbox.SetValue("loot_tables/folder_name/table_name.json")

    #sorta clears the screen there is no clear and cut dry way of doing this sadly.
    def _cls(self):
        print("\033c\033[3J", end='')

    def _check_ignore_empties(self, evt):
        print (self._ignore_empty)

    def _on_seed_enter(self, evt):
        self.spin_ctrl.SetValue("0")

    def _on_seed_set_focus(self, evt):
        self.spin_ctrl.SetValue("0")

    def _on_seed_change(self, evt):
        self.spin_ctrl.SetValue("0")

    def _on_seed_kill_focus(self, evt):
        self.spin_ctrl.SetValue("0")

    def _on_seed_leave(self, evt):
        self.spin_ctrl.SetValue("0")

    def _on_seed_join(self, evt):
        self.spin_ctrl.SetValue("0")

    def _on_text_enter(self, evt):
        print ()

    def _click_skipper(self, evt):
        chk_selection = self.checklist.GetSelection()
        self.checklist.Deselect(chk_selection)
        if self.checklist.IsChecked(chk_selection) == True and chk_selection != 0:
            self.checklist.Check(chk_selection, check=False)
            return
        if self.checklist.IsChecked(chk_selection) == False and chk_selection != 0:
            self.checklist.Check(chk_selection, check=True)
            return
        if self.checklist.IsChecked(chk_selection) == True and chk_selection == 0:
            self.checklist.Check(0, check=False)
            self.checklist.Check(1, check=False)
            self.checklist.Check(2, check=True)
            self.checklist.Check(3, check=False)
            self.checklist.Check(4, check=False)
            self.checklist.Check(5, check=False)
            self.checklist.Check(6, check=False)
            self.check_var = False
            return
        if self.checklist.IsChecked(chk_selection) == False and chk_selection == 0:
            self.checklist.Check(0, check=True)
            self.checklist.Check(1, check=True)
            self.checklist.Check(2, check=True)
            self.checklist.Check(3, check=True)
            self.checklist.Check(4, check=True)
            self.checklist.Check(5, check=True)
            self.checklist.Check(6, check=True)
            self.check_var = True
            return 

    def _check_list_args(self, evt): 
        checked = list(self.checklist.GetCheckedItems())
        if 0 in checked and self.check_var == False:
            self.checklist.Check(1, check=True)
            self.checklist.Check(2, check=True)
            self.checklist.Check(3, check=True)
            self.checklist.Check(4, check=True)
            self.checklist.Check(5, check=True)
            self.checklist.Check(6, check=True)
            self.check_var = True
        if 0 not in checked and self.check_var == True:
            self.checklist.Check(1, check=False)
            self.checklist.Check(2, check=True)
            self.checklist.Check(3, check=False)
            self.checklist.Check(4, check=False)
            self.checklist.Check(5, check=False)
            self.checklist.Check(6, check=False)
            self.check_var = False
        return

    #handles choice box event.
    def _on_mode_change(self, evt):
        evt.GetEventObject()
        (platform, world_version) = plat
        #hides some UI elements when switching states.
        if self._mode.GetString(self._mode.GetSelection()) == "Randomize":
            self.spin_ctrl.Show()
            self._label_txt5.Show()
            self._sel_loot.Hide()
            self._label_txt3.Hide()
            self._radio1.Show()
            self.loot_textbox.Hide()
            self._label_txt4.Hide()
            self.Layout()
            self.Fit()

        elif self._mode.GetString(self._mode.GetSelection()) == "Custom":
            self._sel_loot.Hide()
            self._label_txt3.Hide()
            self._radio1.Hide()
            self.loot_textbox.Show()
            self._label_txt4.Show()
            self._label_txt5.Show()
            self.spin_ctrl.Show()
            self.Layout()
            self.Fit()

        elif self._mode.GetString(self._mode.GetSelection()) == "Vanilla":
            #loops over the loot tables and regenerates the platform and version.
            loot_table_src = {}
            self._sel_loot.Clear()
            for tbls in self._loot_table_strs((platform, world_version)):
                loot_table_src[os.path.basename(tbls)] = tbls
                self._sel_loot.Append(os.path.basename(tbls))

            #sets selection of the loot table to 0 index.
            self._sel_loot.SetSelection(0)
            self._sel_loot.Show()
            self._label_txt3.Show()
            self._radio1.Hide()
            self.loot_textbox.Hide()
            self._label_txt4.Hide()
            self.spin_ctrl.Show()
            self._label_txt5.Show()
            self.Layout()
            self.Fit()

        else:
            print ("(ERROR!) Invlaid mode selected! = "+str(self._mode.GetString(self._mode.GetSelection())))

        self._mode_description.SetLabel(
            operation_modes[self._mode.GetString(self._mode.GetSelection())]
        )
        
        self.Fit()
        self.Layout()
        evt.Skip()

    #handles radio box event
    def _on_radio_box(self, evt):
        (platform, world_version) = plat
        evt.GetEventObject()
        self._sel_loot.Clear()

        #gets selected radio box.
        radiobox_sel = self._radio1.GetString(self._radio1.GetSelection())

        #higher quality loot this is 100% what vanilla uses its too OP...
        if radiobox_sel == quality_names[0]:

            #loops over the loot tables and regenerates the list with the OP tables.
            loot_table_src = {}
            for tbls in self._loot_table_strs((platform, world_version)):
                loot_table_src[os.path.basename(tbls)] = tbls
                self._sel_loot.Append(os.path.basename(tbls))

        #lower quality loot thsi removes some tables that are too OP.
        elif radiobox_sel == quality_names[1]:

            #loops over the loot tables and regenerates the list without the OP tables.
            loot_table_src = {}
            for tbls in self._loot_table_strs((platform, world_version)):
                if tbls not in hardcoded_ops:
                    loot_table_src[os.path.basename(tbls)] = tbls
                    self._sel_loot.Append(os.path.basename(tbls))

        #sets selection of the loot table to 0 index.
        self._sel_loot.SetSelection(0)

    #Not sure where this is from may be left over junk code? from something. #Leaving to be safe.
    def _on_pick_block_button(self, evt):
        """Set up listening for the block click"""
        self._show_pointer = True

    #extracts the keys from the checkbox list then gets the assoiated block entity name ids as a list.
    def _get_block_entity_types_from_keys(self):
        sel_block_entities = []
        for checkbox_name in list(self.checklist.GetCheckedStrings()):
            sel_block_entities.append(chkdict[checkbox_name])

        return [indexitem for listitem in sel_block_entities for indexitem in listitem]

    #runs the main preform operation
    def _run_operation(self, _):
        self.canvas.run_operation(lambda: self._set_loot_tables())

    #updates a chunk so changes show visually.
    def _refresh_chunk(self, dimension, world, x, z):
       cx, cz = block_coords_to_chunk_coords(x, z)
       chunk = world.get_chunk(cx, cz, dimension)
       chunk.changed = True

    #checks the internet connection.
    def _connect(self, url_adress):
        try:
            urllib.request.urlopen(url_adress)
            return True
        except:
            return False

    #gets universal loot_tables in the case where all other methods failed and this
    #takes the hardcoded copy and minimizes it to work for as many platforms & versions as possible.
    def _get_universal_tables(self, loot_tables, mc_v):
        (mc_platform, mc_version) = mc_v

        #gets a string version of the the world format version.
        version_data = self._get_mcstr_version(mc_version)

        #filters out loot_tables that bedrock doesn't support.
        universal_tables = []

        #handles the loot table conversion from the src loot table.
        for loot_table in loot_tables:
            loot_table = self._parse_loot_str(loot_table)

            #handles the case where some loot tables from java may need to be renamed for bedrock or removed.
            if loot_table in universal_remove_tables:
                universal_tables.append(universal_remove_tables[loot_table])

            else:
                universal_tables.append(loot_table)

        #removes none values for cleanup.
        universal_tables = [x for x in universal_tables if x is not None]
        return universal_tables

    #gets minecraft bedrock loot_tables in the case where some loot tables may not exist in ealier versions causing the issue of empty chest.
    def _get_bedrock_tables(self, loot_tables, mc_v):
        (mc_platform, mc_version) = mc_v

        #mc_version returns a tuple on Minecraft Bedrock worlds when mc_platform == bedrock.
        #gets a string version of the the world format version from a tuple version.
        version_data = self._get_mcstr_version(mc_version)

        #filters out loot_tables that bedrock doesn't support.
        bedrock_tables = []

        #handles the loot table conversion from the src loot table.
        for loot_table in loot_tables:
            loot_table = self._parse_loot_str(loot_table)

            #handles the case if some loot tables didn't exist ('bedrock','1.16.0') #nether update
            if StrictVersion(version_data) < StrictVersion('1.16.0') and loot_table in bedrock_remove_tables['pre_1.16.0']:
                bedrock_tables.append(bedrock_remove_tables['pre_1.16.0'][loot_table])

            #handles the case if some loot tables didn't exist ('bedrock','1.10.0') #busy bees update
            if StrictVersion(version_data) < StrictVersion('1.10.0') and loot_table in bedrock_remove_tables['pre_1.10.0']:
                bedrock_tables.append(bedrock_remove_tables['pre_1.10.0'][loot_table])

            #handles the case if some loot tables didn't exist ('bedrock','1.4.0') #ocean aquatic update
            if StrictVersion(version_data) < StrictVersion('1.4.0') and loot_table in bedrock_remove_tables['pre_1.4.0']:
                bedrock_tables.append(bedrock_remove_tables['pre_1.4.0'][loot_table])

            #handles fast list replacement for case where loot table existed or didn't exist in all versions or was renamed.
            if loot_table in bedrock_remove_tables['*'] and loot_table in bedrock_tables:
                bedrock_tables = np.array(bedrock_tables)
                bedrock_tables = np.where(bedrock_tables == loot_table, bedrock_remove_tables['*'][loot_table], bedrock_tables)
                bedrock_tables = bedrock_tables.tolist()

            else:
                #handles the case where the loot table existed in all versions and platforms.
                bedrock_tables.append(loot_table)

        #removes none values for cleanup.
        bedrock_tables = [x for x in bedrock_tables if x is not None]
        return bedrock_tables

    #gets minecraft java loot_tables from a list of bedrock loot tables.
    def _get_java_tables(self, loot_tables, mc_v):
        (mc_platform, mc_version) = mc_v

        #quick note you will notice no hardcoded copy of java's loot tables are provided in this method.
        #this is because java is data driven from Minecraft Bedrocks loot tables using my conversion method.
        #_get_java_tables(self, loot_tables_list, (mc_platform, mc_version)) 
        #takes a bedrock loot table list or a universal loot table list and converts it to java.

        #filters out loot_tables that java doesn't support.
        java_tables = []

        #mc_version returns an interger on Minecraft Java worlds.

        #handles the conversion.
        for loot_table in loot_tables:
            loot_table = self._parse_loot_str(loot_table)

            #handles the case if some loot tables didn't exist ('java',2566) #nether update
            if mc_version < 2566 and loot_table in java_remove_tables['pre_2566']:
                java_tables.append(java_remove_tables['pre_2566'][loot_table])

            #handles the case if some loot tables didn't exist ('java',2225) #busy bees update
            if mc_version < 2225 and loot_table in java_remove_tables['pre_2225']:
                java_tables.append(java_remove_tables['pre_2225'][loot_table])

            #handles the case if some loot tables didn't exist ('java',1952) #village & pillage update
            if mc_version < 1952 and loot_table in java_remove_tables['pre_1952']:
                java_tables.append(java_remove_tables['pre_1952'][loot_table])

            #handles the case if some loot tables didn't exist ('java',1519) #ocean aquatic update
            if mc_version < 1519 and loot_table in java_remove_tables['pre_1519']:
                java_tables.append(java_remove_tables['pre_1519'][loot_table])

            #handles fast list replacement for case where loot table existed or didn't exist in all versions or was renamed.
            if loot_table in java_remove_tables['*'] and loot_table in java_tables:
                java_tables = np.array(java_tables)
                java_tables = np.where(java_tables == loot_table, java_remove_tables['*'][loot_table], java_tables)
                java_tables = java_tables.tolist()

            #handles the case where the loot table existed in all versions and platforms.
            else:
                java_tables.append(loot_table)

        #removes None values for clean up.
        java_tables = [x for x in java_tables if x is not None]
        return java_tables

    #gets a string version of MC in 1.16.2 format from a tuple (1, 16, 2) also supports int format 1297 as input.
    def _get_mcstr_version(self, tuple_version):
        try:
            str_vr = str(tuple_version[0])+"."+str(tuple_version[1])+"."+str(tuple_version[2])
            return str_vr
        except:
            str_vr = str(tuple_version)
            return str_vr

    #parses the loot table strings and cleans them.
    def _parse_loot_str(self, txtstr):
        try:
            fixed_str = txtstr.replace("\\","/")
        except:
            fixed_str = None
        try:
            loot_table = "loot_tables/"+str(str(fixed_str.split("/loot_tables/")[1].split(".json/")[0])+".json")
            return loot_table
        except:
            if txtstr is None:
                return None
            else:
                return txtstr

    #downloads the current behavior pack zip from the stable version of MCBE if the temp folder doesn't exist.
    def _get_loot_download(self):
        tdir = "/temp"
        if path.exists(str(os.getcwd()).replace("\\","/")+tdir):
            return self._get_vanilla_template(
                'https://www.aka.ms/behaviorpacktemplate',
                '/plugins'+str(tdir),
                'temp.zip'
            )[0]
        else:
            return self._get_loots_from_zip(
                'plugins'+str(tdir)+'/loot_tables/chests'
            )

    #gets the vanilla loot tables if installed on any of your drives.
    def get_all_loot_paths(self):
        #gets a list of drives on the device.
        dtypes = self._get_drives()

        loot_drives = []
        loot_names = []
        found_drives = []
        not_found_drives = []

        #searches over all the drives on this device if its supported for loot tables,
        for drive_type in dtypes:
            try:
                vanilla_loot_path = str(drive_type)+":/Program Files/WindowsApps/Microsoft.Minecraft*/data/behavior_packs/**/loot_tables/chests/*.*"
                vanilla_loot_path_village = str(drive_type)+":/Program Files/WindowsApps/Microsoft.Minecraft*/data/behavior_packs/**/loot_tables/chests/village/*.*"
                loot_paths = glob.glob(vanilla_loot_path)+glob.glob(vanilla_loot_path_village)

                for lootp in loot_paths:
                    lootpath = os.path.basename(lootp)

                    if lootpath not in loot_names:
                        loot_names.append(lootpath)

                for crd, curloot in enumerate(loot_names):
                    if curloot not in loot_drives:
                        loot_table = str(loot_paths[crd].split("/loot_")[0]+"/loot_"+curloot)
                        loot_drives.append(loot_table)

                found_drives.append(drive_type)

            except:
                not_found_drives.append(drive_type)

        return loot_drives

    #extract a loot table list using current version and platform of minecraft 'bedrock' or 'java' or other misc platforms.
    def _loot_table_strs(self, mc_v):
        #extracts the platform and version from the inputn tuple.
        (mc_platform, mc_version) = mc_v

        #creates a temp folder for extracting loot tables from a link if local install fails
        #note this temp ,folder is removed when the operation is complete.
        self._get_temp_folder("temp")

        #gets any local loot_tables installed.
        loots_local = self.get_all_loot_paths()
        loot_paths = None

        #get the loot table for the correct platform, java, bedrock, or unknown.
        if mc_platform == platform_names[0]:
            if bool(loots_local):
                print ("Defaulting to local tables...")
                #takes bedrock tables converts them to java tables.
                loot_paths = self._get_java_tables(loots_local, (mc_platform, mc_version))

            #checks internet if local loot_tables can't be found to see if it can download the latest from the internet.
            elif self._connect(test_url) == True:
                print ("Defaulting to online tables...")
                link_tables = self._get_loot_download()
                loot_paths = self._get_java_tables(link_tables, (mc_platform, mc_version))

            else:
                print ("Defaulting to hardcoded tables for java.")
                #takes hardcoded bedrock tables converts them to java tables because all other methods failed.
                loot_paths = self._get_java_tables(loots_hardcoded, (mc_platform, mc_version))

        elif mc_platform == platform_names[1]:
            if bool(loots_local):
                print ("Defaulting to local tables...")
                loot_paths = self._get_bedrock_tables(loots_local, (mc_platform, mc_version))

            #checks internet if local loot_tables can't be found to see if it can download the latest from the internet.
            elif self._connect(test_url) == True:
                print ("Defaulting to online tables...")
                link_tables = self._get_loot_download()
                loot_paths = self._get_bedrock_tables(link_tables, (mc_platform, mc_version))

            else:
                #uses hardcoded bedrock tables because all other methods failed.
                print ("Defaulting to hardcoded tables for bedrock.")
                loot_paths = self._get_bedrock_tables(loots_hardcoded, (mc_platform, mc_version))

        else:
            #sets the loot_paths to use a hardcoded universal list - this is if the platform isn't 'java' or 'bedrock', 
            #it will only use loot tables that exist on both platforms to be safe.
            #this also parses them to make sure they work in all versions and platforms 
            #though this does limit options and remove many loot tables :(
            loot_paths = loots_universal_table

        #empty list for cleaned tables.
        clean_tables = []

        #loops over loot_paths and parses the strings.
        for loot_path in loot_paths: 
            clean_tables.append(self._parse_loot_str(loot_path))

        return clean_tables

    #barrowed from the amulet api. #thanks gentlegiant
    def _get_vanilla_block(self, dim, world, x, y, z, trans):
        cx, cz = block_coords_to_chunk_coords(x, z)
        offset_x, offset_z = x - 16 * cx, z - 16 * cz

        chunk = world.get_chunk(cx, cz, dim)
        runtime_id = chunk.blocks[offset_x, y, offset_z]

        universal_bk = chunk.block_palette[runtime_id]
        universal_be = chunk.block_entities.get((x, y, z), None)
        return trans.block.from_universal(universal_bk, universal_be)

    #gets a list of drive letters to for grabbing Minecraft Bedrocks data folder path later on.
    def _get_drives(self):
        drives = [ 
            chr(x) for x in range(65,91) 
            if os.path.exists(chr(x) + ":") 
        ]
        return drives

    #creates a temp folder if it doesn't already exist.
    def _get_temp_folder(self, bk_type):
        try:
            os.makedirs('plugins/temp')
        except:
            return None

    #gets parsed list of loot tables from a list
    def _get_loots_from_zip(self, loots_path):
        loot_paths = glob.glob(str(loots_path)+"/*.*")
        loot_paths_village = glob.glob(str(loots_path)+"/village/*.*")
        loot_paths_combined = loot_paths+loot_paths_village

        loot_table_paths = []
        for loot_file in loot_paths_combined:
            loot_table_paths.append(loot_file.split("temp/")[1].replace("\\","/"))

        return loot_table_paths

    def _get_be_id(self, te):
        if "minecraft:" not in te.namespaced_name:
            return str(te.namespaced_name).split(":")[1]
        return te.namespaced_name

    #extracts loot tables paths from a zipurl, 
    def _get_vanilla_template(self,zipurl,tdir,tname):
        
        zip_files = []
        loot_files = []

        with urlopen(zipurl) as zipresp:
            with ZipFile(BytesIO(zipresp.read())) as zfile:
                zfile.extractall(str(os.getcwd()).replace("\\","/")+tdir)
                for zname in zfile.namelist():
                    zip_files.append(zname)

        loot_path_list = _get_loots_from_zip(self, "plugins/temp/loot_tables/chests")
        return loot_path_list

    #prints a message about the bad chunk.
    def _bad_chunk(self, x, y, z):
        print ("Chunk does not exist or can't be read at [X, Y, Z]: "+str([x, y, z]))

    #removes float values
    def trun(self, x, ds = 0):
        mm = 10 ** ds
        return int(x * mm) / mm

    def _parse_custom_loot_tables(self, table_object):
        if isinstance(table_object, str ):
            if len(table_object) > 0:

                #check if base loot_table string exist.
                if "loot_tables/" in table_object and '.json' in table_object:

                    #for comma seperated list.
                    if table_object.count(",") > 0:
                        if ", " in table_object:
                            return self._parse_custom_loot_tables(table_object.split(", "))
                        elif "," in table_object:
                            return self._parse_custom_loot_tables(table_object.split(","))
                        else:
                            wx.MessageBox("(ERROR!) Custom loot table string is invalid!/nPlease try again...")

                    return table_str

        elif isinstance(table_object, list ):
            parsed_tables = []

            for loot_table in table_object:
                if "%" in loot_table:
                    weight = loot_table.split("%")[0]
                    loot_table_str = loot_table.split("%")[1]
                    parsed_tables.append([weight, loot_table_str])

                else:
                    parsed_tables.append([None, loot_table.lstrip()])

            weights = []
            good_weights = []
            tables = []
            for parser_table in parsed_tables:
                weight_var, table_var = parser_table
                weights.append(weight_var)

                if table_var is not None:
                    tables.append(table_var)

                if weight_var is not None:
                    good_weights.append(weight_var)

            good_weight = len(good_weights)
            rweights = list(map(float, good_weights))

            print (rweights)

            #create a formula to calculate the remaigning chance out of the missing weights 
            calculate_missing_weights = sum(rweights) / 100.0

            #gets the remaigner value from the above formula.
            missing_weight = 1.0 - calculate_missing_weights
            balanced_weight = round(missing_weight / weights.count(None),2)
            combined_weight = float(f"{missing_weight:.2f}")
            print ("missing weight: "+str(combined_weight))
            print ("balanced_weight: "+str(balanced_weight))

            if sum(rweights) > 100.0:
                wx.MessageBox("(ERROR!) random weight is greater then allowed: "+str(int(sum(rweights)))+" > 100%")

            elif balanced_weight <= 0.0 and missing_weight <= 0.0:
                wx.MessageBox("(ERROR!) cant devide by 0, decrease a weighted value by at least 1%")

            else:
                final_loot_tables = []
                for parsed_table in parsed_tables:
                    if parsed_table[0] == None:
                        final_loot_tables.append([combined_weight, parsed_table[1]])
                    else:
                        final_loot_tables.append([float(parsed_table[0]), parsed_table[1]])

                print (*final_loot_tables, sep='\n')
                return final_loot_tables
        else:
            wx.MessageBox("(ERROR!) custom loot table string is invalid!/nPlease try again...")

    #main preform method.
    def _set_loot_tables(self):
        #gets the operation_mode for what operation to run.
        op_mode = self._mode.GetString(self._mode.GetSelection())

        #boolean value for empty chest only selections.
        empty_mode = self._ignore_empty.GetValue()

        #parses custom loot_table string.
        selected_custom_table = self._parse_custom_loot_tables(self.loot_textbox.GetRange(0, 32767))

        #gets the selected loot_table string from the vanilla list.
        selected_table = "loot_tables/chests/"+str(self._sel_loot.GetString(self._sel_loot.GetSelection()))

        #gets the world instance and platform and version.
        world = self.world
        platform = world.level_wrapper.platform
        world_version = world.level_wrapper.version

        #gets the selection boxes
        sel = self.canvas.selection.selection_group

        #gets the dimension
        dim = self.canvas.dimension

        #gets an instance of the translation_manager using the current platform & world version.
        trans = world.translation_manager.get_version(platform, world_version)
        mc_version = (platform, world_version)

        #debug_tracking.
        containers_count = 0
        containers_found = []

        #grabs a list of block_entity entity ids from a hardcoded dictionary for now.
        #currently there no way to data drive the list of block entities.
        sel_block_entities = self._get_block_entity_types_from_keys()

        #gets a list of all block entity ids.
        all_block_entities = []
        for abe in chkdict:
            all_block_entities.append(chkdict[abe])

        #formats the list of all block entity ids.
        all_block_entities = [indexitem for listitem in all_block_entities for indexitem in listitem]

        #mode 0 = Set Random, mode 1 = Set Vanilla, mode 2 = Set Custom Path.
        op_modes = list(operation_modes.keys())

        #the randomized loot tables operation is handled here.
        if op_mode == op_modes[0]:
            #start message.
            print ("Selected mode: 'Randomize'")
            print ()
            print ("Started editing containers...")

            #handles the wildcard case where a user selects "All Containers" this will find all block entities with an "Items" tag and add loot tables.
            if "*" in sel_block_entities:
                print ("Wildcard: True")
                #loops over the selection boxes.
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
                            if "Items" in block_entity.nbt:
                                block_entity.nbt["Items"] = TAG_List([])
                                block_entity.nbt["LootTable"] = TAG_String(random.choice(list(loot_table_src.values())))
                                block_entity.nbt["LootTableSeed"] = TAG_Long(loot_table_seed)

                                #sets the block_entity block with updated NBT.
                                world.set_version_block(x, y, z, dim, mc_version, block, block_entity)

                                #counts + 1 for every block_entity it finds.
                                containers_count+=1

                                #adds the block_entity_id to a list.
                                block_entity_id = self._get_be_id(block_entity)
                                if block_entity_id not in containers_found:
                                    containers_found.append(block_entity_id)

                                #updates the chunk.
                                self._refresh_chunk(dim, world, x, z)

            elif len(sel_block_entities) > 0:
                print ("Wildcard: False")
                #loops over the selection boxes.
                for box in sel.merge_boxes().selection_boxes:
                    #loops over the current selection box's x, y, z coordinates.
                    for (x, y, z) in box:
                        #handles the case where a chunk may not be able to be read.
                        try:
                            #gets info about the block (the_block, nbt_data, water_logged_blocks.)
                            (block, block_entity, extras) = self._get_vanilla_block(dim, world, x, y, z, trans)
                            if block_entity is not None:

                                #checks if the block_entity.id is in the list of selected block_entities,
                                #modifies and creates new nbt in the block_entity.
                                block_entity_id = self._get_be_id(block_entity)

                                if block_entity_id in sel_block_entities:
                                    block_entity.nbt["Items"] = TAG_List([])
                                    block_entity.nbt["LootTable"] = TAG_String(random.choice(list(loot_table_src.values())))
                                    block_entity.nbt["LootTableSeed"] = TAG_Long(loot_table_seed)

                                    #sets the tile_entity block with updated NBT.
                                    world.set_version_block(x, y, z, dim, mc_version, block, block_entity)
                                    
                                    #counts + 1 for every block_entity it finds.
                                    containers_count+=1

                                    #adds the block_entity_id to a list.
                                    if block_entity_id not in containers_found:
                                        containers_found.append(block_entity_id)

                                    #updates the chunk.
                                    self._refresh_chunk(dim, world, x, z)
                        except:
                            #prints an error message about the chunk.
                            self._bad_chunk(x, y, z)

            else:
                wx.MessageBox("(ERROR!) There were no containers selected!/nPlease try again...")

        #the set vanilla loot table operation is handled here.
        elif op_mode == op_modes[1]:
            #start message.
            print ("Selected mode: 'Vanilla'")
            print ()
            print ("Started editing containers...")

            #handles the wildcard case where a user selects "All Containers" this will find all block entities with an "Items" tag and add loot tables.
            if "*" in sel_block_entities:
                print ("Wildcard mode: True")
                for box in sel.merge_boxes().selection_boxes:
                    for (x, y, z) in box:
                        #gets info about the block (the_block, nbt_data, water_logged_blocks.)
                        (block, block_entity, extras) = self._get_vanilla_block(dim, world, x, y, z, trans)
                        if block_entity is not None:

                            block_entity_id = self._get_be_id(block_entity)

                            #checks if the "Items" tag is in the block_entity,
                            #modifies and creates new nbt in the block_entity.
                            if "Items" in block_entity.nbt:
                                block_entity.nbt["Items"] = TAG_List([])
                                block_entity.nbt["LootTable"] = TAG_String(selected_table)
                                block_entity.nbt["LootTableSeed"] = TAG_Long(loot_table_seed)

                                #sets the tile_entity block with updated NBT.
                                world.set_version_block(x, y, z, dim, mc_version, block, block_entity)

                                #counts + 1 for every block_entity it finds.
                                containers_count+=1

                                #adds the block_entity_id to a list.
                                if block_entity_id not in containers_found:
                                    containers_found.append(block_entity_id)

                                #updates the chunk.
                                self._refresh_chunk(dim, world, x, z)

            elif len(sel_block_entities) > 0:
                print ("Wildcard mode: False")
                for box in sel.merge_boxes().selection_boxes:
                    for (x, y, z) in box:
                        #gets info about the block (the_block, nbt_data, water_logged_blocks.)
                        (block, block_entity, extras) = self._get_vanilla_block(dim, world, x, y, z, trans)
                        if block_entity is not None:

                            #checks if the block_entity.id is in the list of selected block_entities,
                            #modifies and creates new nbt in the block_entity.
                            block_entity_id = self._get_be_id(block_entity)

                            if block_entity_id in sel_block_entities:
                                block_entity.nbt["Items"] = TAG_List([])
                                block_entity.nbt["LootTable"] = TAG_String(selected_table)
                                block_entity.nbt["LootTableSeed"] = TAG_Long(loot_table_seed)

                                #sets the tile_entity block with updated NBT.
                                world.set_version_block(x, y, z, dim, mc_version, block, block_entity)

                                #counts + 1 for every block_entity it finds.
                                containers_count+=1

                                #adds the block_entity_id to a list.
                                if block_entity_id not in containers_found:
                                    containers_found.append(block_entity_id)

                                #updates the chunk.
                                self._refresh_chunk(dim, world, x, z)

            else:
                wx.MessageBox("(ERROR!) There were no containers selected!/nPlease try again...")

        #the set custom loot table operation is handled here.
        elif op_mode == op_modes[2]:
            #start message.
            print ("Selected mode: 'Custom'")

            #handles the wildcard case where a user selects "All Containers" this will find all block entities with an "Items" tag and add loot tables.
            if "*" in sel_block_entities:
                print ("Wildcard mode: True")
                for box in sel.merge_boxes().selection_boxes:
                    for (x, y, z) in box:
                        #gets info about the block (the_block, nbt_data, water_logged_blocks.)
                        (block, block_entity, extras) = self._get_vanilla_block(dim, world, x, y, z, trans)
                        if block_entity is not None:

                            block_entity_id = self._get_be_id(block_entity)

                            #checks if the "Items" tag is in the block_entity,
                            #modifies and creates new nbt in the block_entity.
                            if "Items" in block_entity.nbt:
                                block_entity.nbt["Items"] = TAG_List([])
                                block_entity.nbt["LootTable"] = TAG_String(selected_custom_table)
                                block_entity.nbt["LootTableSeed"] = TAG_Long(loot_table_seed)

                                #sets the tile_entity block with updated NBT.
                                world.set_version_block(x, y, z, dim, mc_version, block, block_entity)

                                #counts + 1 for every block_entity it finds.
                                containers_count+=1

                                #adds the block_entity_id to a list.
                                if block_entity_id not in containers_found:
                                    containers_found.append(block_entity_id)

                                #updates the chunk.
                                self._refresh_chunk(dim, world, x, z)

            elif len(sel_block_entities) > 0:
                print ("Wildcard mode: False")

                for box in sel.merge_boxes().selection_boxes:
                    for (x, y, z) in box:
                        #gets info about the block (the_block, nbt_data, water_logged_blocks.)
                        (block, block_entity, extras) = self._get_vanilla_block(dim, world, x, y, z, trans)
                        if block_entity is not None:

                            #checks if the block_entity.id is in the list of selected block_entities,
                            #modifies and creates new nbt in the block_entity.
                            block_entity_id = self._get_be_id(block_entity)

                            #checks if this is one of the selected tiles.
                            if block_entity_id in sel_block_entities:
                                if empty_mode == True:
                                    if len(list(block_entity.nbt["Items"].value)) < 1:
                                        block_entity.nbt["LootTable"] = TAG_String(selected_custom_table)
                                        block_entity.nbt["LootTableSeed"] = TAG_Long(loot_table_seed)
                                        block_entity.nbt["Items"] = TAG_List([])

                                        #sets the tile_entity block with updated NBT.
                                        world.set_version_block(x, y, z, dim, mc_version, block, block_entity)

                                        #counts + 1 for every block_entity it finds.
                                        containers_count+=1

                                        #adds the block_entity_id to a list.
                                        if block_entity_id not in containers_found:
                                            containers_found.append(block_entity_id)

                                        #updates the chunk.
                                        self._refresh_chunk(dim, world, x, z)
                                else:
                                    block_entity.nbt["LootTable"] = TAG_String(selected_custom_table)
                                    block_entity.nbt["LootTableSeed"] = TAG_Long(loot_table_seed)
                                    block_entity.nbt["Items"] = TAG_List([])

                                    #sets the tile_entity block with updated NBT.
                                    world.set_version_block(x, y, z, dim, mc_version, block, block_entity)

            else:
                wx.MessageBox("(ERROR!) There were no containers selected!/nPlease try again...")

        #the set custom loot table operation is handled here.
        elif op_mode == op_modes[3]:
            #start message.
            print ("Selected mode: 'Remove'")

            #handles the wildcard case where a user selects "All Containers" this will find all block entities with an "Items" tag and add loot tables.
            if "*" in sel_block_entities:
                print ("Wildcard mode: True")
                for box in sel.merge_boxes().selection_boxes:
                    for (x, y, z) in box:
                        #gets info about the block (the_block, nbt_data, water_logged_blocks.)
                        (block, block_entity, extras) = self._get_vanilla_block(dim, world, x, y, z, trans)
                        if block_entity is not None:

                            block_entity_id = self._get_be_id(block_entity)

                            #checks if the "LootTable & " tag is in the block_entity,
                            #modifies and creates new nbt in the block_entity.
                            if "LootTable" in block_entity.nbt:
                                del block_entity.nbt["LootTable"]
                                del block_entity.nbt["LootTableSeed"]

                                #sets the tile_entity block with updated NBT.
                                world.set_version_block(x, y, z, dim, mc_version, block, block_entity)

                                #counts + 1 for every block_entity it finds.
                                containers_count+=1

                                #adds the block_entity_id to a list.
                                if block_entity_id not in containers_found:
                                    containers_found.append(block_entity_id)

                                #updates the chunk.
                                self._refresh_chunk(dim, world, x, z)

            elif len(sel_block_entities) > 0:
                print ("Wildcard mode: False")

                for box in sel.merge_boxes().selection_boxes:
                    for (x, y, z) in box:
                        #gets info about the block (the_block, nbt_data, water_logged_blocks.)
                        (block, block_entity, extras) = self._get_vanilla_block(dim, world, x, y, z, trans)
                        if block_entity is not None:

                            #checks if the block_entity.id is in the list of selected block_entities,
                            #modifies and creates new nbt in the block_entity.
                            block_entity_id = self._get_be_id(block_entity)

                            #checks if this is one of the selected tiles.
                            if block_entity_id in sel_block_entities:
                                if empty_mode == True:
                                    if len(list(block_entity.nbt["Items"].value)) < 1:
                                        if "LootTable" in block_entity.nbt:
                                            del block_entity.nbt["LootTable"]
                                            del block_entity.nbt["LootTableSeed"]

                                            #sets the tile_entity block with updated NBT.
                                            world.set_version_block(x, y, z, dim, mc_version, block, block_entity)

                                            #counts + 1 for every block_entity it finds.
                                            containers_count+=1

                                            #adds the block_entity_id to a list.
                                            if block_entity_id not in containers_found:
                                                containers_found.append(block_entity_id)

                                            #updates the chunk.
                                            self._refresh_chunk(dim, world, x, z)
                                else:
                                    block_entity.nbt["LootTable"] = TAG_String(selected_custom_table)
                                    block_entity.nbt["LootTableSeed"] = TAG_Long(loot_table_seed)
                                    block_entity.nbt["Items"] = TAG_List([])

                                    #sets the tile_entity block with updated NBT.
                                    world.set_version_block(x, y, z, dim, mc_version, block, block_entity)

            else:
                wx.MessageBox("(ERROR!) There were no containers selected!/nPlease try again...")


        if len(sel_block_entities) > 0:
            #completion message and block_entity meta.
            print ("Finished processing!")
            print ()
            print ("MC Platform: "+str(platform))
            print ("MC Version: "+str(world_version))
            print ()
            print ("Total containers found: "+str(containers_count))

            #Checks if there were more than 0 containers.
            if containers_count > 0:
                print ()
                print ("Types of containers found: ")
                print ('\n'.join(map(str, list(containers_found)))) 
            else:
                wx.MessageBox("(ERROR!) there are no valid containers found!/nPlease try again...")

            #remove temp folder when complete.
            temp_path = str(os.getcwd())+'\\plugins\\temp\\'
            try:
                shutil.rmtree(temp_path)
            except:
                try:
                    os.rmdir(temp_path)
                except:
                    wx.MessageBox("(ERROR!) with removing: "+str(temp_path))
                pass

#simple export options.
export = {
    "name": "Set LootTables",
    "operation": SetLootTables,
}