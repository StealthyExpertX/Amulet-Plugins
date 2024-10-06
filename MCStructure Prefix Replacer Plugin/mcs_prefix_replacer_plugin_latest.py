"""
------------------------------------------
Plugin License: 
Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)
------------------------------------------
Author: Karl D. | StealthyX
Aliases: StealthyExpertX, stealthyx, StealthyExpert
------------------------------------------
Contact:
New Discord: stealthyx
Old Discord: StealthyX#8940
Twitter/X: @RedstonerLabs
------------------------------------------
Usage:
Commercial use of this plugin is permitted free of charge. All I ask is you asking me for permission first.
------------------------------------------
Licensing:
As the author, I reserve the right to change the licensing terms as required.
------------------------------------------
Liability:
By using this plugin, you're assuming all responsibility for any potential issues. Please note, I won't be liable for any problems or damages that may occur. Use it wisely!
------------------------------------------
Feedback & Updates:
Your feedback is invaluable! I'm open to updating this plugin based on popular demand. Don't hesitate to reach out!
------------------------------------------
"""

#plugin supports v1.17.0 to 1.21.30, (Minecraft Bedrock Only!)

#standard library imports
import os
import wx
import time

#amulet library imports
from amulet_nbt import StringTag
from amulet.api.errors import ObjectWriteError
from amulet.api.data_types import Dimension
from amulet.api.selection import SelectionGroup
from amulet_nbt import load as load_nbt, utf8_escape_decoder, utf8_escape_encoder
from amulet_map_editor.programs.edit.api.operations import SimpleOperationPanel, OperationError

#define the main plugin class
class EditMCStructurePalette(SimpleOperationPanel):
    def __init__(self, parent: wx.Window, canvas: "EditCanvas", world: "BaseLevel", options_path: str):
        #call parent class constructor
        super().__init__(parent, canvas, world, options_path)
        
        #load user preferences
        options = self._load_options({"find_prefix": "", "replace_prefix": "", "bulk_edit": False})
        
        #add UI description
        description = wx.StaticText(self, label=(
            "This plugin edits Minecraft structures and replaces block ID prefixes and state ID prefixes with new ones.\n"
            "It's useful for updating structures in bulk when custom block prefixes have changed. (Supports bedrock edition only!)"
        ))
        self._sizer.Add(description, 0, wx.ALL | wx.EXPAND, 5)
        
        #add checkbox for bulk editing mode
        self._bulk_checkbox = wx.CheckBox(self, label="Bulk Edit (Folder)")
        self._bulk_checkbox.SetValue(options.get("bulk_edit", False))
        self._bulk_checkbox.Bind(wx.EVT_CHECKBOX, self._on_bulk_toggle)
        self._sizer.Add(self._bulk_checkbox, 0, wx.ALL | wx.CENTER, 5)

        #file picker for selecting individual .mcstructure files
        self._file_picker = wx.FilePickerCtrl(
            self, path=options.get("path", ""), wildcard="mcstructure file (*.mcstructure)|*.mcstructure", style=wx.FLP_USE_TEXTCTRL | wx.FLP_OPEN
        )

        #directory picker for selecting folder (hidden unless bulk edit is enabled)
        self._folder_picker = wx.DirPickerCtrl(self, path=options.get("path", ""), style=wx.DIRP_USE_TEXTCTRL)
        self._sizer.Add(self._file_picker, 0, wx.ALL | wx.CENTER, 5)
        self._folder_picker.Hide()
        self._sizer.Add(self._folder_picker, 0, wx.ALL | wx.CENTER, 5)

        #text fields for entering find and replace prefixes
        self._find_prefix = wx.TextCtrl(self, value=options.get("find_prefix", "arcedge_natu:"))
        self._sizer.Add(wx.StaticText(self, label="Find Prefix:"), 0, wx.ALL, 5)
        self._sizer.Add(self._find_prefix, 0, wx.EXPAND | wx.ALL, 5)
        
        self._replace_prefix = wx.TextCtrl(self, value=options.get("replace_prefix", "ae:"))
        self._sizer.Add(wx.StaticText(self, label="Replace With Prefix:"), 0, wx.ALL, 5)
        self._sizer.Add(self._replace_prefix, 0, wx.EXPAND | wx.ALL, 5)
        
        #add run button to execute palette edit operation
        self._add_run_button("Edit Palette")
        self.Layout()

    #toggle bulk edit mode
    def _on_bulk_toggle(self, event):
        if self._bulk_checkbox.IsChecked():
            self._file_picker.Hide() #hide file picker in bulk mode
            self._folder_picker.Show() #show folder picker
        else:
            self._folder_picker.Hide() #hide folder picker in non-bulk mode
            self._file_picker.Show() #show file picker
        self.Layout()

    #save user preferences
    def disable(self):
        self._save_options({
            "path": self._file_picker.GetPath() if not self._bulk_checkbox.IsChecked() else self._folder_picker.GetPath(),
            "find_prefix": self._find_prefix.GetValue(),
            "replace_prefix": self._replace_prefix.GetValue(),
            "bulk_edit": self._bulk_checkbox.IsChecked(),
        })

    #main operation for editing structure files
    def _operation(self, world: "BaseLevel", dimension: Dimension, selection: SelectionGroup):
        start_time = time.time() #track start time
        total_block_ids_edited = 0
        total_block_states_edited = 0
        structures_edited = 0
        
        #get find and replace prefixes
        find_prefix = self._find_prefix.GetValue()
        replace_prefix = self._replace_prefix.GetValue()
        
        if self._bulk_checkbox.IsChecked(): #bulk edit mode
            folder_path = self._folder_picker.GetPath()
            if not folder_path or not os.path.isdir(folder_path):
                raise OperationError("Please select a valid folder.") #error if folder is invalid
            mcstructure_files = []
            
            #search for .mcstructure files in selected folder
            for root, _, files in os.walk(folder_path):
                for file in files:
                    if file.endswith(".mcstructure"):
                        mcstructure_files.append(os.path.join(root, file))
            
            total_files = len(mcstructure_files)
            if total_files == 0:
                print(f"No .mcstructure files found in {folder_path}")
                return
            
            #process each .mcstructure file
            print(f"Processing {total_files} .mcstructure files in {folder_path}")
            for index, file_path in enumerate(mcstructure_files):
                print(f"\n[{index + 1}/{total_files}] Processing file: {file_path}")
                edited = self._process_file(file_path, find_prefix, replace_prefix)

                if edited:
                    structures_edited += 1
                    total_block_ids_edited += self.block_ids_edited
                    total_block_states_edited += self.block_states_edited

        else: #single file edit mode.
            file_path = self._file_picker.GetPath()
            if not file_path or not os.path.isfile(file_path):
                raise OperationError("Please select a valid mcstructure file.")

            print(f"Processing file: {file_path}")
            edited = self._process_file(file_path, find_prefix, replace_prefix)

            if edited:
                structures_edited += 1
                total_block_ids_edited += self.block_ids_edited
                total_block_states_edited += self.block_states_edited

        #calculate and print operation summary.
        end_time = time.time()
        elapsed_time = end_time - start_time

        print("\n--- Operation Completed ---")
        if structures_edited > 0:
            print(f"Total structures edited: {structures_edited}")
            print(f"Total block IDs edited: {total_block_ids_edited}")
            print(f"Total block states edited: {total_block_states_edited}")

        else:
            print("None of the mcstructures had prefixes to edit.")

        print(f"Total time taken: {elapsed_time:.2f} seconds")

    #process individual .mcstructure file.
    def _process_file(self, path, find_prefix, replace_prefix):
        try:
            #load structure NBT data for Minecraft Bedrock from a *.mcstructure file.
            with open(path, "rb") as file:
                structure_nbt = load_nbt(file, little_endian=True, string_decoder=utf8_escape_decoder).compound
            
            #setup edit counters.
            self.block_ids_edited = 0
            self.block_states_edited = 0
            
            #edit block palette.
            self._edit_palette(structure_nbt, find_prefix, replace_prefix)
            
            #save file if edits were made.
            if self.block_ids_edited > 0 or self.block_states_edited > 0:
                with open(path, "wb") as file:
                    structure_nbt.save_to(file, little_endian=True, compressed=False, string_encoder=utf8_escape_encoder)

                print(f"File {os.path.basename(path)} saved.")
                print(f"Block IDs edited: {self.block_ids_edited}")
                print(f"Block states edited: {self.block_states_edited}\n")
                return True
            
            print(f"No changes made to {os.path.basename(path)}.\n")
            return False

        except Exception as e:
            raise OperationError(f"An error occurred while processing {path}: {e}")

    #edit block prefixes in the palette and handle edge cases.
    def _edit_palette(self, structure_nbt, find_prefix, replace_prefix):
        palette = structure_nbt.get_compound("structure").get_compound("palette").get_compound("default")
        block_palette = palette.get_list("block_palette")

        for block in block_palette:
            block_name = block.get_string("name").py_str

            if block_name.startswith(find_prefix):
                new_block_name = block_name.replace(find_prefix, replace_prefix)
                block["name"] = StringTag(new_block_name)
                self.block_ids_edited += 1

            if "states" in block:
                block_states = block.get_compound("states")
                self._edit_states(block_states, find_prefix, replace_prefix)

    #edit state prefixes IDs in the palette.
    def _edit_states(self, states, find_prefix, replace_prefix):
        for state_key in list(states.keys()):
            if state_key.startswith(find_prefix):
                new_state_key = state_key.replace(find_prefix, replace_prefix)
                states[new_state_key] = states[state_key]
                del states[state_key]

                self.block_states_edited += 1

#export plugin details.
export = {
    "name": "MCStructure Prefix Replacer Plugin",
    "operation": EditMCStructurePalette,
    "description": "This plugin edits Minecraft structures by replacing (block ID and state ID prefixes) in bulk. It is great for updating structures when custom block prefixes have changed. Currently only supports bedrock!"
}