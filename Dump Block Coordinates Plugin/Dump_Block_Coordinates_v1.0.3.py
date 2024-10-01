#This code is for non-commercial use only for the time being.
#https://creativecommons.org/licenses/by-nc/3.0/

#Please provide credit when possible, thanks :)
#Twitter: @RedstonerLabs
#Discord: StealthyExpert#8940

#Big thanks to gentlegiantJGC for information on the Amulet API.

#imports for required modules.
import numpy
from typing import TYPE_CHECKING, Tuple

import wx
import ast
import json
import os
import shutil
import platform

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

plugin_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODES = {
    "Coords to *.json": "Dumps [x, y, z] coordinates into multible json files.",
    "Coords to *.txt": "Dumps [x, y, z] coordinates into multible text files.",
    "Coords to *.*": "Dumps [x, y, z] coordinates into all supported file types.",
    "Counts to *.json": "Dumps [blocks counted] into multible json files.",
    "Counts to *.txt": "Dumps [blocks counted] into multible txt files.",
    "Counts to *.*": "Dumps [blocks counted] into all supported file types.",
}

#air_block default.
air_block = ["air", 0]

class DumpCoordinates(wx.Panel, DefaultOperationUI):
    def __init__(
        self,
        parent: wx.Window,
        canvas: "EditCanvas",
        world: "BaseLevel",
        options_path: str,
    ):

        #skip air setting.
        global skip_air

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
                value="This script will search the Amulet selection by finding unqiue block identifiers listing them out in the selected file type. Note, files get saved at plugins/<name>_coords\n",
                style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_BESTWRAP,
            )
            dialog.sizer.Add(text, 1, wx.EXPAND)
            dialog.ShowModal()
            evt.Skip()

        help_button.Bind(wx.EVT_BUTTON, on_button)

        self._skipair = wx.CheckBox(self, label="Skip Air", pos=(0,0))
        top_sizer.Add(self._skipair, 1, wx.EXPAND | wx.LEFT, 5)
        self._skipair.Bind(wx.EVT_CHECKBOX,self._onChecked) 

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

    def _onChecked(self, e): 
      cb = e.GetEventObject() 
      skip_air = cb.GetValue()

    def _on_pick_block_button(self, evt):
        """Set up listening for the block click"""
        self._show_pointer = True

    def _run_operation(self, _):
        self.canvas.run_operation(lambda: self._dump_coordinates())

    #gets a block at x, y, z and returns a given dict object.
    def _get_vanilla_block(self, dim, world, x, y, z, bk_arrays, skip_air):
        (platform, world_version, bk_array) = bk_arrays

        #translates the world from X platform and Z version.
        world_trans = world.translation_manager.get_version(platform, world_version)

        #barrowed from the amulet api. #thanks gentlegiant.
        cx, cz = block_coords_to_chunk_coords(x, z)
        offset_x, offset_z = x - 16 * cx, z - 16 * cz
        chunk = world.get_chunk(cx, cz, dim)
        runtime_id = chunk.blocks[offset_x, y, offset_z]
        uni_block = chunk.block_palette[runtime_id]
        uni_tile_entity = chunk.block_entities.get((x, y, z), None)
        (this_block, this_tile_entity, this_block_extras) = world_trans.block.from_universal(uni_block, uni_tile_entity)
        
        #gets base_name example: "stone" from the block_object.
        block_str = this_block.base_name

        #creates empty index if one wasn't present before hand.
        if block_str not in bk_array:
            bk_array[block_str] = []

        #creates the coordinates as list and adds them to bk_array dict.
        if skip_air == True:
            if block_str in air_block:
                return bk_array
            else:
                bk_array[block_str].append([x,y,z])
                return bk_array

        bk_array[block_str].append([x,y,z])
        return bk_array

    def _dump_message(self, bk_array, bk_count):
        blocks = []
        print ("")
        print ("blocks_types: "+str(len(bk_array)))
        print ("block_count: "+str(bk_count))
        print ("")
        blocks.append("blocks_types:"+str(len(bk_array)))
        blocks.append("block_count:"+str(bk_count))
        for bk in bk_array:
           print (str(bk)+": "+str(len(bk_array[bk])))
           blocks.append(str(bk)+":"+str(len(bk_array[bk])))
        return blocks

    #prints some info in the console.
    def _block_info(self, bk_array, bk_count, bk_type, ckey):
        print ("Finished dumping block coordinates!")
        print ("")
        if bk_type != "all":
            if bk_type == "counts":
                print ("(Dumped the following blocks to these paths)")
                print ("txt_counts/<name>.json")
                print ("json_counts/<name>.txt")
                return self._dump_message(bk_array, bk_count)
            else:
                print ("(Dumped the following blocks at "+str(bk_type)+str(ckey)+"/<name>."+str(bk_type)+")")
                return self._dump_message(bk_array, bk_count)
        else:
            print ("(Dumped the following blocks to these paths)")
            print ("plugins/txt_coords/<name>.json")
            print ("plugins/txt_counts/<name>.json")
            print ("plugins/json_coords/<name>.txt")
            print ("plugins/json_counts/<name>.txt")
            return self._dump_message(bk_array, bk_count)

    #create a folder in the plugins directory.
    def _get_folder(self, bk_type, bk_key):
        try:
            os.makedirs(os.path.join(plugin_folder, f"{str(bk_type)}{str(bk_key)}"), exist_ok=True)
        except:
            pass

    #preforms the main logic.
    def _dump_coordinates(self):

        #operation mode
        operation_mode = self._mode.GetString(self._mode.GetSelection())
        
        #removes folders on running the plugin.
        coords_path = [
            os.path.join(plugin_folder, 'plugins', 'txt_coords'),
            os.path.join(plugin_folder, 'plugins', 'json_coords'),
            os.path.join(plugin_folder, 'plugins', 'json_counts'),
            os.path.join(plugin_folder, 'plugins', 'txt_counts')
        ]
        for cpath in coords_path:
            try:
                shutil.rmtree(cpath)
            except:
                pass

        
        skip_air = self._skipair.GetValue()

        #gets the world instance.
        world = self.world

        #gets the world platform and version.
        platform = world.level_wrapper.platform
        world_version = world.level_wrapper.version

        #gets the block as a versioned object from platform and world version.
        block_version = world.translation_manager.get_version(platform, world_version)

        #gets selections and current dimnesion.
        selection = self.canvas.selection.selection_group
        dimension = self.canvas.dimension

        #unfinished code for dumping coordinates for specific blocks instead of all blocks in a selection. 
        #namespaces = block_version.block.namespaces(True)
        #base_names = block_version.block.base_names(namespaces[0], True)

        #static variables used for containers and counters.
        blocks_array = {}
        blocks_count = 0
        block_objs = ["blocks_types","block_count"]
        ckey = '_coords'
        tx = "txt" 
        jn = "json"
        cckey = '_counts'

        #scans for blocks and if it finds some it will dump them to the blocks_array.
        print ("Started dumping for block info...")
        for box in selection.merge_boxes().selection_boxes:
            for x, y, z in box:
                #catches if a chunk doesn't exist and skips it.
                try:
                    block_coords = self._get_vanilla_block(dimension, world, x, y, z, (platform, world_version, blocks_array), skip_air)
                    blocks_array.update(block_coords)
                    blocks_count+=1
                except:
                    pass

        #gets the selection mode of coords to *.json
        if operation_mode == "Coords to *."+str(jn):

            #create a folders in the plugins directory.
            self._get_folder(jn, ckey)

            #writes the json files at path plugins/json_coords
            for bk in blocks_array:
               with open(os.path.join(plugin_folder, f"{str(jn)}{str(ckey)}", f"{str(bk)}.{str(jn)}"),"w+") as jsonfile:
                    json.dump({bk:blocks_array[bk]}, jsonfile, indent=2)

            #prints some extra info in the console on the json files.
            self._block_info(blocks_array, blocks_count, jn, ckey)

        #gets the selection mode of coords to *.txt
        elif operation_mode == "Coords to *."+str(tx):

            #create a folders in the plugins directory.
            self._get_folder(tx, ckey)

            for bk in blocks_array:
                with open(os.path.join(plugin_folder, f"{str(tx)}_{str(ckey)}", f"{str(bk)}.{str(tx)}"),"w+") as textfile:

                    #writes the txt files at path plugins/txt_coords
                    for bks in blocks_array[bk]:
                        textfile.write(str(bk)+": "+str(bks).replace("[","").replace("]","").replace(",","")+"\n")

            #prints some extra info in the console on the txt files.
            self._block_info(blocks_array, blocks_count, tx, ckey)

        #gets the selection mode of coords to *.*
        elif operation_mode == "Coords to *.*":

            #create a folders in the plugins directory.
            self._get_folder(tx, ckey)

            #create a folders in the plugins directory.
            self._get_folder(jn, ckey)

            for bk in blocks_array:
                with open(os.path.join(plugin_folder, 'txt_coords', f"{str(bk)}.{str(tx)}"),"w+") as textfile:

                    #writes the txt files at path plugins/txt_coords
                    for bks in blocks_array[bk]:
                        edit_str = str(bks).replace("[","").replace("]","").replace(",","")
                        textfile.write(str(bk)+": "+edit_str+"\n")

                with open(os.path.join(plugin_folder, 'json_coords', f"{str(bk)}.{str(jn)}"),"w+") as jsonfile:
                    json.dump({bk:blocks_array[bk]}, jsonfile, indent=2)

            #prints some extra info in the console on the json files.
            self._block_info(blocks_array, blocks_count, "all", ckey)

        #gets the selection mode of block counts to *.json
        elif operation_mode == "Counts to *."+str(jn):

            #create a folders in the plugins directory.
            self._get_folder(jn, cckey)

            #writes the json files at path plugins/json_counts
            #prints some extra info in the console on the json files.
            counts = self._block_info(blocks_array, blocks_count, jn, ckey)
            with open(os.path.join(plugin_folder, str(jn), str(cckey), f"block_counts.{str(jn)}"),"w+") as jsonfile:
                countdict = {}
                countdict["info"] = {}
                countdict["blocks"] = {}
                for bkc in counts:
                    bname = bkc.split(":")[0]
                    bcount = bkc.split(":")[1]
                    if bname in block_objs:
                        countdict["info"][bname] = int(bcount)
                    else:
                        countdict["blocks"][bname] = int(bcount)
                json.dump(countdict, jsonfile, indent=2)

        #gets the selection mode of block counts to *.json
        elif operation_mode == "Counts to *."+str(tx):

            #create a folders in the plugins directory.
            self._get_folder(tx, cckey)

            #writes the json files at path plugins/json_counts
            #prints some extra info in the console on the json files.
            counts = self._block_info(blocks_array, blocks_count, tx, ckey)
            with open(os.path.join(plugin_folder, str(tx), str(cckey), f"block_counts.{str(tx)}"), "w+") as textfile:
                cck = 0
                cck2 = 0
                counts = self._block_info(blocks_array, blocks_count, tx, cckey)

                #writes the txt files at path plugins/txt_coords
                for bkc in counts:
                    bname = bkc.split(":")[0]
                    bcount = bkc.split(":")[1]
                    if bname in block_objs:
                        if cck2 == 0:
                            textfile.write("(INFO)\n")
                            cck2+=1
                        textfile.write(str(bname)+":"+str(bcount)+"\n")
                    else:
                        if cck == 0:
                            textfile.write("\n")
                            textfile.write("(BLOCKS)\n")
                            cck+=1
                        textfile.write(str(bname)+":"+str(bcount)+"\n")

        #gets the selection mode of block counts to *.json
        elif operation_mode == "Counts to *.*":

            #create a folders in the plugins directory.
            self._get_folder(tx, cckey)
            counts = self._block_info(blocks_array, blocks_count, "counts", cckey)
            #writes the json files at path plugins/json_counts
            with open(os.path.join(plugin_folder, str(tx), str(cckey), f"block_counts.{str(tx)}"), "w+") as textfile:
                cck = 0
                cck2 = 0

                #writes the txt files at path plugins/txt_coords
                for bkc in counts:
                    bname = bkc.split(":")[0]
                    bcount = bkc.split(":")[1]
                    if bname in block_objs:
                        if cck2 == 0:
                            textfile.write("(INFO)\n")
                            cck2+=1
                        textfile.write(str(bname)+":"+str(bcount)+"\n")
                    else:
                        if cck == 0:
                            textfile.write("\n")
                            textfile.write("(BLOCKS)\n")
                            cck+=1
                        textfile.write(str(bname)+":"+str(bcount)+"\n")

            #create a folders in the plugins directory.
            self._get_folder(jn, cckey)

            #writes the json files at path plugins/json_counts
            #prints some extra info in the console on the json files.
            with open(os.path.join(plugin_folder, str(jn), str(cckey), f"block_counts.{str(jn)}"), "w+") as jsonfile:
                countdict = {}
                countdict["info"] = {}
                countdict["blocks"] = {}
                for bkc in counts:
                    bname = bkc.split(":")[0]
                    bcount = bkc.split(":")[1]
                    if bname in block_objs:
                        countdict["info"][bname] = int(bcount)
                    else:
                        countdict["blocks"][bname] = int(bcount)
                json.dump(countdict, jsonfile, indent=2)

        #unknown option ignores creating files.
        else:
            print ("Unknown option selected, skipping instance.")
            pass

export = {
    "name": "Dump Coordinates",
    "operation": DumpCoordinates,
}