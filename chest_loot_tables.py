#You may use this plugin for only non commercial purposes aka non Minecraft Marketplace content.

#This loot table plugin supports java, bedrock and possibly other platforms!
#I gave it my best shot so let me know if it works on mac-os or linux?

#Currently it updates the UI based on the platform and version of the world,
#This plugin was designed to make adding loot tables to containers easier 
#and to work on as many platforms and versions of Minecraft as possible.

#Twitter: @RedstonerLabs
#Discord: StealthyExpert#8940



#VERSION DOCS this is for tracking loot tables btw versions.

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
# BEDROCK: (1,11,0)

# Update Aquatic #ADDED THE ocean treasure loot tables.
# JAVA: 1519
# BEDROCK: (1,5,0)


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
    "Randomize LootTables": "Set containers with randomized vanilla loot tables.",
    "Set Vanilla LootTables": "Set containers with a selected vanilla loot table name.",
    "Set Custom LootTables": "Set containers with a custom inputed loot table path.",
}

#bedrock op loot tables.
#these loot tables contain items that are considered too op and have high enchants & loot, etc.
#updated bedrock_1.17.0 & java_1.17
hardcoded_ops = [
    "loot_tables/chests/bastion_treasure.json",
    "loot_tables/chests/shipwrecksupply.json",
    "loot_tables/chests/buriedtreasure.json",
    "loot_tables/chests/end_city_treasure.json",
    "loot_tables/chests/spawn_bonus_chest.json",
    "loot_tables/chests/shipwrecktreasure.json"
]

#loot table settings for randomizing.
lblList = ['Epic Quality', "Normal Quality"] 

#wasn't able to data drive the tile_entity list of ids for containers.
#will revist this at a later date.
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

        global plat
        global loot_table_src
        global sel_block_entities
        global all_block_entities

        plat = (platform, world_version)

        loot_table_src = {}
        for tbls in self._loot_table_strs((platform, world_version)):
            loot_table_src[os.path.basename(tbls)] = tbls

        wx.Panel.__init__(self, parent)
        DefaultOperationUI.__init__(self, parent, canvas, world, options_path)
        self.Freeze()

        self._sizer = wx.BoxSizer(wx.VERTICAL) #verticle shape top to bottom for main dialog.
        self.SetSizer(self._sizer)

        options = self._load_options({})
        top_sizer = wx.BoxSizer(wx.VERTICAL)
        self._sizer.Add(top_sizer, 1, wx.EXPAND | wx.ALL, 6)

        #text label for mode description
        self._label_txt1=wx.StaticText(self, 0, label=' Mode (Description)')
        self._sizer.Add(self._label_txt1, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 0)

        #text label for mode selection
        self._label_txt2=wx.StaticText(self, 0, label=' Choose (Mode)')
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

        #description text box.
        self._mode_description = wx.TextCtrl(
            self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_BESTWRAP
        )
        self._sizer.Add(self._mode_description, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 1)

        self._mode_description.SetLabel(
            operation_modes[self._mode.GetString(self._mode.GetSelection())]
        )

        self._mode_description.Fit()

        #chest checklistbox.
        self.checklist = wx.CheckListBox(self, 2, pos = (80,10), choices=list(chkdict.keys()), style=0)
        self._sizer.Add(self.checklist, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 0)

        #quality radio box
        #majorDimension = 1 == HORIZONTAL radios
        #majorDimension = 0 == VERTICAL radios
        self._radio1 = wx.RadioBox(self, label = 'Choose (Loot Option)', pos = (80,10), choices = lblList,majorDimension = 1, style = 0) 
        self._radio1.Bind(wx.EVT_RADIOBOX,self._on_radio_box)
        self._sizer.Add(self._radio1, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 0)

        #run button
        self._run_button = wx.Button(self, label="Run Operation")
        self._run_button.Bind(wx.EVT_BUTTON, self._run_operation)
        self._sizer.Add(self._run_button, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 1)

        #hide the radiobox by default.
        self._radio1.Hide()
        self.Layout()
        self.Thaw()

    @property #handles the wx add option size (height, width) default is (0, 0) 
    #interesting to note that ommiting the 0 on the second index of the tuple works?
    def wx_add_options(self) -> Tuple[int, ...]:
        return (0,)

    #sorta clears the screen there is no clear and cut dry way of doing this sadly.
    def _cls(self):
        print("\033c\033[3J", end='')

    #handles choice box event.
    def _on_mode_change(self, evt):
        evt.GetEventObject()
        (platform, world_version) = plat
        #hides some UI elements when switching states.
        if self._mode.GetString(self._mode.GetSelection()) == "Randomize LootTables":
            self._sel_loot.Hide()
            self._label_txt3.Hide()
            self._radio1.Show()
        else:
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

        self._mode_description.SetLabel(
            operation_modes[self._mode.GetString(self._mode.GetSelection())]
        )
        self._mode_description.Fit()
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
        if radiobox_sel == "Epic Quality":

            #loops over the loot tables and regenerates the list with the OP tables.
            loot_table_src = {}
            for tbls in self._loot_table_strs((platform, world_version)):
                loot_table_src[os.path.basename(tbls)] = tbls
                self._sel_loot.Append(os.path.basename(tbls))

        #lower quality loot thsi removes some tables that are too OP.
        elif radiobox_sel == "Normal Quality":

            #loops over the loot tables and regenerates the list without the OP tables.
            loot_table_src = {}
            for tbls in self._loot_table_strs((platform, world_version)):
                if tbls not in hardcoded_ops:
                    loot_table_src[os.path.basename(tbls)] = tbls
                    self._sel_loot.Append(os.path.basename(tbls))

        #sets selection of the loot table to 0 index.
        self._sel_loot.SetSelection(0)

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

    #old loot table download code from an ealier test.
    # def _loot_tables_from_link(self, zip_file_url):
        # resp = urlopen(zip_file_url)
        # zipfile = ZipFile(BytesIO(resp.read()))
        # r = requests.get(zip_file_url)
        # z = zipfile.ZipFile(io.BytesIO(r.content))
        # z.extractall("/plugins")
        # return zipfile.namelist()

    #gets universal loot_tables in the case where all other methods failed and this
    #takes the hardcoded copy and minimizes it to work for as many platforms & versions as possible.
    def _get_universal_tables(self, loot_tables, mc_v):
        (mc_platform, mc_version) = mc_v

        #tuple versions.
        #remove these loot strings durring universal loot table conversion.
        remove_tables = {
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
            "loot_tables/chests/village_blacksmith.json": None
        }

        #gets a string version of the the world format version.
        version_data = self._get_mcstr_version(mc_version)

        #filters out loot_tables that bedrock doesn't support.
        universal_tables = []

        #handles the loot table conversion from the src loot table.
        for loot_table in loot_tables:
            loot_table = self._parse_loot_str(loot_table)

            #handles the case where some loot tables from java may need to be renamed for bedrock.
            if loot_table in remove_tables:
                universal_tables.append(remove_tables[loot_table])

            else:
                universal_tables.append(loot_table)

        #removes none values for cleanup.
        universal_tables = [x for x in universal_tables if x is not None]
        return universal_tables

    #gets minecraft bedrock loot_tables in the case where some loot tables may not exist in ealier versions causing the issue of empty chest.
    def _get_bedrock_tables(self, loot_tables, mc_v):
        (mc_platform, mc_version) = mc_v

        #TABLES ADDED OR REMOVED: NONE
        # Cave & Cliffs
        # BEDROCK: (1,17,0)

        # Nether Update
        # BEDROCK: (1,16,0)

        # Buzzy Bees
        # BEDROCK: (1,14,0)

        # Village & Pillage
        # BEDROCK: (1,11,0)

        # Update Aquatic
        # BEDROCK: (1,5,0)

        #tables to convert file paths of loot tables from java to bedrock format.
        java_to_bedrock = {
            "loot_tables/chests/jungle_temple_dispenser.json": "loot_tables/chests/dispenser_trap.json",
            "loot_tables/chests/shipwreck_map.json": "loot_tables/chests/shipwreck.json",
            "loot_tables/chests/shipwreck_supply.json": "loot_tables/chests/shipwrecksupply.json",
            "loot_tables/chests/shipwreck_treasure.json": "loot_tables/chests/shipwrecktreasure.json"
        }

        #tuple versions.
        #remove these loot strings durring universal loot table conversion.
        remove_tables = {
            "pre_1.16.0":{
                "loot_tables/chests/bastion_bridge.json": None,
                "loot_tables/chests/bastion_hoglin_stable.json": None,
                "loot_tables/chests/bastion_other.json": None,
                "loot_tables/chests/bastion_treasure.json": None,
                "loot_tables/chests/ruined_portal.json": None
            }
        }

        #mc_version returns a tuple on Minecraft Bedrock worlds.

        #gets a string version of the the world format version from a tuple version.
        version_data = self._get_mcstr_version(mc_version)

        #filters out loot_tables that bedrock doesn't support.
        bedrock_tables = []

        #handles the loot table conversion from the src loot table.
        for loot_table in loot_tables:
            loot_table = self._parse_loot_str(loot_table)

            #handles the case if some loot tables didn't exist or needed to be renamed in ('bedrock','1.16.0') #nether update
            if StrictVersion(version_data) < StrictVersion('1.16.0') and loot_table in remove_tables['pre_1.16.0']:
                bedrock_tables.append(remove_tables['pre_1.16.0'][loot_table])

            #handles the case where some loot tables from java may need to be renamed for bedrock.
            elif loot_table in java_to_bedrock:
                bedrock_tables.append(java_to_bedrock[loot_table])

            else:
                bedrock_tables.append(loot_table)

        #removes none values for cleanup.
        bedrock_tables = [x for x in bedrock_tables if x is not None]
        return bedrock_tables

    #gets minecraft java loot_tables from a list of bedrock loot tables.
    def _get_java_tables(self, loot_tables, mc_v):
        (mc_platform, mc_version) = mc_v

        # # Cave & Cliffs
        # # JAVA: 2724

        # # Nether Update
        # # JAVA: 2566

        # # Buzzy Bees
        # # JAVA: 2225

        # # Village & Pillage
        # # JAVA: 1952

        # # Update Aquatic
        # # JAVA: 1519

        # #tables to convert file paths of loot tables from bedrock to java format.
        # bedrock_to_java = {
            # "loot_tables/chests/dispenser_trap.json": "loot_tables/chests/jungle_temple_dispenser.json",
            # "loot_tables/chests/shipwreck.json": "loot_tables/chests/shipwreck_map.json",
            # "loot_tables/chests/shipwrecksupply.json": "loot_tables/chests/shipwreck_supply.json",
            # "loot_tables/chests/shipwrecktreasure.json": "loot_tables/chests/shipwreck_treasure.json"
        # }

        # #tuple versions.
        # #remove these loot strings durring universal loot table conversion.
        # remove_tables = [
            # "loot_tables/chests/monster_room.json", #does not exist on java.
            # "loot_tables/chests/village_two_room_house.json", #does not exist on java.
            # "loot_tables/chests/village_blacksmith.json" #removed in 1.14
        # ]

        # #tuple versions.
        # #remove these loot strings durring universal loot table conversion.
        # remove_tables = {
            # 1952:{
                # "loot_tables/chests/village_blacksmith.json": None
            # },
            # 1519:{
            
            # }
        # }

        # #filters out loot_tables that java doesn't support.
        # java_tables = []

        # #mc_version returns an interger on Minecraft Java worlds.

        # #handles the conversion.
        # for loot_table in loot_tables:
            # loot_table = self._parse_loot_str(loot_table)

            # #Minecraft Java version 1952 = Village & Pillage.
            # #only instance of a loot_table being removed from java 1.14.0 #village_blacksmith.json
            # if (mc_version <= 1952 and loot_table == remove_tables[2]:
                # java_tables.append(None)

            # if (mc_version <= 1952 and loot_table == remove_tables[2]:
                # java_tables.append(None)

            # #haqndles removing some loot tables that don't exist on java.
            # elif loot_table in remove_tables and loot_table != remove_tables[2]:
                # java_tables.append(None)

            # #handles renaming loot tables.
            # elif loot_table in bedrock_to_java:
                # java_tables.append(bedrock_to_java[loot_table])

            # else:
                # java_tables.append(loot_table)

        # #removes None values for clean up.
        # java_tables = [x for x in java_tables if x is not None]
        # return java_tables

    #gets a string version of MC in 1.16.2 format from a tuple (1, 16, 2) also supports int format 1297 as input.
    def _get_mcstr_version(self, tuple_version):
        try:
            str_vr = str(tuple_version[0])+"."+str(tuple_version[1])+"."+str(tuple_version[2])
            return str_vr
        except:
            str_vr = str(tuple_version)
            return str_vr

    #parses the loot table strings and cleans them up.
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
        if path.exists(str(os.getcwd()).replace("\\","/")+tdir):
            return self._get_vanilla_template(
                'https://www.aka.ms/behaviorpacktemplate',
                '/plugins/temp',
                'temp.zip'
            )[0]
        else:
            return self._get_loots_from_zip(
                'plugins/temp/loot_tables/chests'
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

        #quick note you will notice no hardcoded copy of java's loot tables are provided in this method.
        #this is because java is data driven from Minecraft Bedrocks loot tables using my conversion method below.
        #_get_java_tables(self, loot_tables_list, (mc_platform, mc_version))

        #this table is hardcoded for bedrock, for the edge case that all other loot tables extractions fail for bedrock.
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
        #for the edge case that all other loot tables extraction methods fail?
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

        #gets any local loot_tables installed.
        loots_local = self.get_all_loot_paths()
        loot_paths = None

        #get the loot table for the correct platform, java, bedrock, or unknown.
        if mc_platform == 'java':
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

        elif mc_platform == 'bedrock':
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
            pass

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

    def _no_selected_error(self):
        print ("(ERROR!) There were no containers selected!")
        print ("Please try again...")

    #main preform method.
    def _set_loot_tables(self):
        print ("gathering loot_tables")
        op_mode = self._mode.GetString(self._mode.GetSelection())
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

        #the randomized loot tables operation is handled here.
        if op_mode == "Randomize LootTables":
            #start message.
            print ("Selected mode: 'Randomize LootTables'")
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
                        try:
                            #gets info about the block (the_block, nbt_data, water_logged_blocks)
                            (block, block_entity, extras) = self._get_vanilla_block(dim, world, x, y, z, trans)
                            
                            #checks if the block has a block entity or not.
                            if block_entity is not None:

                                #checks if the "Items" tag is in the block_entity,
                                #modifies and creates new nbt in the block_entity.
                                if "Items" in block_entity.nbt:
                                    block_entity.nbt["Items"] = TAG_List([])
                                    block_entity.nbt["LootTable"] = TAG_String(random.choice(list(loot_table_src.values())))
                                    block_entity.nbt["LootTableSeed"] = TAG_Long(0)

                                    #sets the block_entity block with updated NBT.
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
                                    block_entity.nbt["LootTableSeed"] = TAG_Long(0)

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
                self._no_selected_error()

        #the set vanilla loot table operation is handled here.
        elif op_mode == "Set Vanilla LootTables":
            #start message.
            print ("Selected mode: 'Set Vanilla LootTables'")
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
                                block_entity.nbt["LootTableSeed"] = TAG_Long(0)

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
                                block_entity.nbt["LootTableSeed"] = TAG_Long(0)

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
                self._no_selected_error()

        if len(sel_block_entities) > 0:
            #completion message and block_entity meta.
            print ("Finished editing all containers!")
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
                print ()
                print ("The loot table strings used: ")
                print ('\n'.join(map(str, loot_table_src.keys()))) 
            else:
                print ("(ERROR!) There are no valid containers found: ")
                print ("Please try again...")

            #remove temp folder when complete.
            temp_path = str(os.getcwd())+'\\plugins\\temp'
            try:
                print (temp_path)
                shutil.rmtree(temp_path)
            except:
                pass

#simple export options.
export = {
    "name": "Set LootTables",
    "operation": SetLootTables,
}