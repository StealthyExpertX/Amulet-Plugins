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
Commercial use of this plugin is permitted free of charge. All I ask is you asking for permission first.
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

import os
import wx
import time
import traceback
import logging
from datetime import datetime
from typing import List

import amulet
from amulet_nbt import load as load_nbt, utf8_escape_decoder, CompoundTag
from amulet.api.data_types import Dimension
from amulet.api.selection import SelectionGroup, SelectionBox
from amulet_map_editor.programs.edit.api.operations import (
    SimpleOperationPanel,
    OperationError as EditorOperationError,
)
from amulet.level.formats.mcstructure import MCStructureFormatWrapper

logger = logging.getLogger("SchemToMCBEStructure")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)-5s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    logger.addHandler(ch)
logger.propagate = False

def format_duration(seconds: float) -> str:
    if seconds >= 60:
        m = int(seconds // 60); s = seconds % 60
        return f"{m}m{s:04.2f}s"
    return f"{seconds:.2f}s"

class SchemToMCBEStructure(SimpleOperationPanel):
    def __init__(self, parent, canvas, world, options_path: str):
        super().__init__(parent, canvas, world, options_path)
        opts = self._load_options({"bulk_edit": False})

        desc = (
            "Convert Sponge .schem files into Bedrock .mcstructure files.\n\n"
            "• Bulk Conversion (checked): browse for a folder; every .schem inside will be converted.\n"
            "• File Conversion (unchecked): pick one or more .schem files manually to convert."
        )
        self._sizer.Add(wx.StaticText(self, label=desc), 0, wx.ALL | wx.EXPAND, 8)

        self._bulk = wx.CheckBox(self, label="Bulk Conversion")
        self._bulk.SetValue(opts["bulk_edit"])
        self._bulk.Bind(wx.EVT_CHECKBOX, self._on_toggle)
        self._sizer.Add(self._bulk, 0, wx.ALL, 5)

        hz = wx.BoxSizer(wx.HORIZONTAL)
        self._input_txt = wx.TextCtrl(self, style=wx.TE_READONLY)
        self._browse_input = wx.Button(self, label="Browse…")
        self._browse_input.Bind(wx.EVT_BUTTON, self._on_browse_input)
        hz.Add(self._input_txt, 1, wx.EXPAND|wx.ALL, 2)
        hz.Add(self._browse_input, 0, wx.ALL, 2)
        self._sizer.Add(wx.StaticText(self, label="Input:"), 0, wx.LEFT, 8)
        self._sizer.Add(hz, 0, wx.EXPAND, 0)

        self._out_picker = wx.DirPickerCtrl(
            self,
            message="Select output folder",
            style=wx.DIRP_USE_TEXTCTRL | wx.DIRP_DIR_MUST_EXIST
        )
        self._sizer.Add(wx.StaticText(self, label="Output:"), 0, wx.LEFT, 8)
        self._sizer.Add(self._out_picker, 0, wx.EXPAND|wx.ALL, 5)

        self._add_run_button("Convert")
        self.Layout()

        self._input_paths: List[str] = []
        self._on_toggle(None)

    def _on_toggle(self, event):
        self._input_txt.SetValue("")
        self._input_paths = []
        if self._bulk.IsChecked():
            self._browse_input.SetLabel("Browse folder…")
        else:
            self._browse_input.SetLabel("Browse files…")

    def _on_browse_input(self, event):
        if self._bulk.IsChecked():
            dlg = wx.DirDialog(self, "Select input folder", style=wx.DD_DIR_MUST_EXIST)
            if dlg.ShowModal() == wx.ID_OK:
                fld = dlg.GetPath()
                dlg.Destroy()
                files = []
                for root, _, names in os.walk(fld):
                    for name in names:
                        if name.lower().endswith(".schem"):
                            files.append(os.path.join(root, name))
                if not files:
                    wx.MessageBox("No .schem files found in that folder.", "No Files", wx.ICON_WARNING)
                    return
                self._input_paths = files
                self._input_txt.SetValue(fld)
            else:
                dlg.Destroy()
        else:
            dlg = wx.FileDialog(
                self, "Select .schem files",
                wildcard="*.schem",
                style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_FILE_MUST_EXIST
            )
            if dlg.ShowModal() == wx.ID_OK:
                paths = dlg.GetPaths()
                dlg.Destroy()
                if not paths:
                    wx.MessageBox("No .schem files selected.", "No Files", wx.ICON_WARNING)
                    return
                self._input_paths = paths
                brief = "; ".join(os.path.basename(p) for p in paths)
                self._input_txt.SetValue(brief)
            else:
                dlg.Destroy()

    def disable(self):
        self._save_options({"bulk_edit": self._bulk.IsChecked()})

    def _operation(self, world, dimension: Dimension, selection):
        if not self._input_paths:
            wx.MessageBox("Please select input files or folder first.", "Missing Input", wx.ICON_ERROR)
            return False

        output_folder = self._out_picker.GetPath()
        if not output_folder or not os.path.isdir(output_folder):
            wx.MessageBox("Please select a valid output folder.", "Missing Output", wx.ICON_ERROR)
            return False

        from datetime import datetime
        logger.info("Conversion started at %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        total = len(self._input_paths)
        logger.info("Processing %d file(s)...", total)

        start_all = time.time()
        successes = 0

        for schem in self._input_paths:
            t0 = time.time()
            base = os.path.basename(schem)
            name = os.path.splitext(base)[0]
            out_path = os.path.join(output_folder, f"{name}.mcstructure")

            try:
                struct = amulet.load_level(schem)

                sel = getattr(struct, "selection", None)
                if not sel or not getattr(sel, "selection_boxes", None):
                    with open(schem, "rb") as f:
                        root = load_nbt(f, little_endian=False, string_decoder=utf8_escape_decoder).compound
                    if isinstance(root.get("Schematic"), CompoundTag):
                        root = root["Schematic"]
                    off = root.get("Offset")
                    dims = [root.get(tag) for tag in ("Width", "Height", "Length")]
                    if not (off and all(dims)):
                        raise EditorOperationError("Corrupted schematic")
                    mins = [int(x) for x in off]
                    sz = [d.py_int for d in dims]
                    struct.selection = SelectionGroup(
                        SelectionBox(mins, [mins[i] + sz[i] for i in range(3)])
                    )

                wrapper = MCStructureFormatWrapper(out_path)
                wrapper.create_and_open("bedrock", world.level_wrapper.version, struct.selection, True)
                wrapper.translation_manager = struct.translation_manager
                struct.save(wrapper=wrapper)
                wrapper.close()
                struct.close()

                dur = time.time() - t0
                logger.info("%s → %s (converted in %s)", base, os.path.basename(out_path), format_duration(dur))
                successes += 1

            except Exception:
                dur = time.time() - t0
                logger.error("%s → %s (failed in %s)", base, os.path.basename(out_path), format_duration(dur))
                traceback.print_exc()

        total_dur = time.time() - start_all
        logger.info("Conversion completed: %d/%d succeeded in %s", successes, total, format_duration(total_dur))
        return True

export = {
    "name": "Schem to Bedrock MCStructure v1.0.0 Plugin",
    "operation": SchemToMCBEStructure,
    "description": "Convert Sponge .schem files into Bedrock .mcstructure files, in bulk.",
}
