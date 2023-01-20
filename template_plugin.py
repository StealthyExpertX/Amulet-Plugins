from amulet.api.selection import SelectionGroup
from amulet.api.level import BaseLevel
from amulet.api.data_types import Dimension

operation_options = {
	"Text Label": ["label"],
	"Bool input default": [
		"bool"
	],
	"Bool input False": [
		"bool",
		False,
	],
	"Bool input True": ["bool", True],
	"Int input default": ["int"],
	"Int input 10": [
		"int",
		10,
	],
	"Int input 10 bounded": [
		"int",
		10,
		0,
		20,
	],
	"Float input default": [
		"float"
	],
	"Float input 10": [
		"float",
		10,
	],
	"Float input 10 bounded": [
		"float",
		10,
		0,
		20,
	],
	"String input empty": [
		"str"
	],
	"String input empty2": ["str", ""],
	"String input hello": ["str", "hello"],
	"Text choice": ["str_choice", "choice 1", "choice 2", "choice 3"],

	"File Open picker": ["file_open"],
	"File Save picker": ["file_save"],
	"Folder picker": ["directory"],
}

def operation(
	world: BaseLevel, dimension: Dimension, selection: SelectionGroup, options: dict
):
	sel_group = self.canvas.selection.selection_group
	chunk_coordinates = sel_group.chunk_locations()

	for chunk in chunk_coordinates:
		block_entities = chunk.block_entities
		be_keys = block_entities.keys()
		for be_coordinates in be_keys:
			if be_coordinates in sel_group: 
				print (be_coordinates)
		print (block_entities.keys())
		print (dimension)
		print (options)

export = {
	"name": "Test Plugin",
	"operation": operation,
	"options": operation_options,
}