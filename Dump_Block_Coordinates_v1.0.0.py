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
    "Coords to *.json": "Dumps [x, y, z] coordinates into multible json files.",
    "Coords to *.txt": "Dumps [x, y, z] coordinates into multible text files.",
}

class DumpCoordinates(wx.Panel, DefaultOperationUI):
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
                value="This script will search the amulet selection by finding unqiue block identifiers listing them out as txt or json files in the plugins/block_coords directory\n",
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
        self.canvas.run_operation(lambda: self._dump_coordinates())

    #gets a block at x, y, z and returns a given dict object.
    def get_vanilla_block(self, dim, world, x, y, z, bk_arrays):
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
        bk_array[block_str].append([x,y,z])
        return bk_array

    #prints some info in the console.
    def _block_info(self, bk_array, bk_count, bk_type):
        print ("Finished dumping block coordinates!")
        print ("")
        print ("(Dumped the following blocks at plugins/"+str(bk_type)+"_coords/<name>."+str(bk_type)+")")
        print ("")
        print ("blocks_types: "+str(len(bk_array)))
        print ("block_count: "+str(bk_count))
        print ("")
        for bk in bk_array:
           print (str(bk)+": "+str(len(bk_array[bk])))

    #create a folder in the plugins directory.
    def _get_coords_folder(self, bk_type):
        try:
            os.makedirs('plugins/'+str(bk_type)+'_coords')
        except:
            pass

    #preforms the main logic.
    def _dump_coordinates(self):

        #operation mode
        operation_mode = self._mode.GetString(self._mode.GetSelection())

        #removes folders on running the plugin.
        coords_path = [str(os.getcwd())+'\\plugins\\txt_coords',str(os.getcwd())+'\\plugins\\json_coords']
        for cpath in coords_path:
            try:
                print (cpath)
                shutil.rmtree(cpath)
            except:
                pass

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

        #scans for blocks and if it finds some it will dump them to the blocks_array.
        print ("Started dumping for block coordinates...")
        for box in selection.merge_boxes().selection_boxes:
            for x, y, z in box:
                #catches if a chunk doesn't exist and skips it.
                try:
                    block_coords = self.get_vanilla_block(dimension, world, x, y, z, (platform, world_version, blocks_array))
                    blocks_array.update(block_coords)
                    blocks_count+=1
                except:
                    pass

        #gets the selection mode of coords to *.json
        if operation_mode == "Coords to *.json":

            #create a folders in the plugins directory.
            self._get_coords_folder("json")

            #writes the json files at path plugins/json_coords
            for bk in blocks_array:
               with open("plugins/json_coords/"+str(bk)+".json","w+") as jsonfile:
                    json.dump({bk:blocks_array[bk]}, jsonfile, indent=2)

            #prints some extra info in the console on the json files.
            self._block_info(blocks_array, blocks_count, "json")

        #gets the selection mode of coords to *.txt
        elif operation_mode == "Coords to *.txt":

            #create a folders in the plugins directory.
            self._get_coords_folder("txt")

            for bk in blocks_array:
                with open("plugins/txt_coords/"+str(bk)+".txt","w+") as textfile:

                    #writes the txt files at path plugins/txt_coords
                    for bks in blocks_array[bk]:
                        textfile.write(str(bk)+": "+str(bks).replace("[","").replace("]","").replace(",","")+"\n")

            #prints some extra info in the console on the txt files.
            self._block_info(blocks_array, blocks_count, "txt")

        #unknown option ignores creating files.
        else:
            pass

export = {
    "name": "Dump Coordinates",
    "operation": DumpCoordinates,
}
