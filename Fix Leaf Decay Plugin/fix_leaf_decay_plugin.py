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

#standard library imports
import time
import traceback
from typing import Tuple, Any 

#third-party imports
import numpy as np
import PyMCTranslate

#local amulet imports
from amulet.api.block import Block
from amulet.api.data_types import Dimension
from amulet.api.level import BaseLevel
from amulet.api.selection import SelectionGroup
from amulet.utils.world_utils import block_coords_to_chunk_coords
from amulet_nbt import ByteTag, StringTag

#dictionary mapping each operation option to its UI representation and default state.
operation_options = {
	"Prevents leaf blocks in your world from decaying.\nChoose the types of leaves you want to keep,\nrun the plugin, and they'll be set to stay persistent!": ["label"],
	"TREE TYPES": ["label"],
	"Oak": ["bool", True],
	"Spruce": ["bool", True],
	"Birch": ["bool", True],
	"Jungle": ["bool", True],
	"Acacia": ["bool", True],
	"Dark Oak": ["bool", True],
	"Azalea": ["bool", True],
	"Azalea Flowered": ["bool", True],
	"Mangrove": ["bool", True],
	"Cherry": ["bool", True]
}

#mapping for converting leaf block state properties between Minecraft Java and Bedrock editions.
leaves_universal_mapping = {
	"java": {
		"1.20.0": {
			"Oak": ["minecraft:oak_leaves", {"distance": "7", "persistent": "false", "waterlogged": "false", "old_leaf_type": None, "new_leaf_type": None, "persistent_bit": None, "update_bit": None}],
			"Spruce": ["minecraft:spruce_leaves", {"distance": "7", "persistent": "false", "waterlogged": "false", "old_leaf_type": None, "new_leaf_type": None, "persistent_bit": None, "update_bit": None}],
			"Birch": ["minecraft:birch_leaves", {"distance": "7", "persistent": "false", "waterlogged": "false", "old_leaf_type": None, "new_leaf_type": None, "persistent_bit": None, "update_bit": None}],
			"Jungle": ["minecraft:jungle_leaves", {"distance": "7", "persistent": "false", "waterlogged": "false", "old_leaf_type": None, "new_leaf_type": None, "persistent_bit": None, "update_bit": None}],
			"Acacia": ["minecraft:acacia_leaves", {"distance": "7", "persistent": "false", "waterlogged": "false", "old_leaf_type": None, "new_leaf_type": None, "persistent_bit": None, "update_bit": None}],
			"Dark Oak": ["minecraft:dark_oak_leaves", {"distance": "7", "persistent": "false", "waterlogged": "false", "old_leaf_type": None, "new_leaf_type": None, "persistent_bit": None, "update_bit": None}],
			"Azalea": ["minecraft:azalea_leaves", {"distance": "7", "persistent": "false", "waterlogged": "false", "old_leaf_type": None, "new_leaf_type": None, "persistent_bit": None, "update_bit": None}],
			"Azalea Flowered": ["minecraft:flowering_azalea_leaves", {"distance": "7", "persistent": "false", "waterlogged": "false", "old_leaf_type": None, "new_leaf_type": None, "persistent_bit": None, "update_bit": None}],
			"Mangrove": ["minecraft:mangrove_leaves", {"distance": "7", "persistent": "false", "waterlogged": "false", "old_leaf_type": None, "new_leaf_type": None, "persistent_bit": None, "update_bit": None}],
			"Cherry": ["minecraft:cherry_leaves", {"distance": "7", "persistent": "false", "waterlogged": "false", "old_leaf_type": None, "new_leaf_type": None, "persistent_bit": None, "update_bit": None}]
		},
		"1.19.0": {
			"Oak": ["minecraft:oak_leaves", {"distance": "7", "persistent": "false", "waterlogged": "false", "old_leaf_type": None, "new_leaf_type": None, "persistent_bit": None, "update_bit": None}],
			"Spruce": ["minecraft:spruce_leaves", {"distance": "7", "persistent": "false", "waterlogged": "false", "old_leaf_type": None, "new_leaf_type": None, "persistent_bit": None, "update_bit": None}],
			"Birch": ["minecraft:birch_leaves", {"distance": "7", "persistent": "false", "waterlogged": "false", "old_leaf_type": None, "new_leaf_type": None, "persistent_bit": None, "update_bit": None}],
			"Jungle": ["minecraft:jungle_leaves", {"distance": "7", "persistent": "false", "waterlogged": "false", "old_leaf_type": None, "new_leaf_type": None, "persistent_bit": None, "update_bit": None}],
			"Acacia": ["minecraft:acacia_leaves", {"distance": "7", "persistent": "false", "waterlogged": "false", "old_leaf_type": None, "new_leaf_type": None, "persistent_bit": None, "update_bit": None}],
			"Dark Oak": ["minecraft:dark_oak_leaves", {"distance": "7", "persistent": "false", "waterlogged": "false", "old_leaf_type": None, "new_leaf_type": None, "persistent_bit": None, "update_bit": None}],
			"Azalea": ["minecraft:azalea_leaves", {"distance": "7", "persistent": "false", "waterlogged": "false", "old_leaf_type": None, "new_leaf_type": None, "persistent_bit": None, "update_bit": None}],
			"Azalea Flowered": ["minecraft:flowering_azalea_leaves", {"distance": "7", "persistent": "false", "waterlogged": "false", "old_leaf_type": None, "new_leaf_type": None, "persistent_bit": None, "update_bit": None}],
			"Mangrove": ["minecraft:mangrove_leaves", {"distance": "7", "persistent": "false", "waterlogged": "false", "old_leaf_type": None, "new_leaf_type": None, "persistent_bit": None, "update_bit": None}]
		},
		"1.18.0": {
			"Oak": ["minecraft:oak_leaves", {"distance": "7", "persistent": "false", "waterlogged": "false", "old_leaf_type": None, "new_leaf_type": None, "persistent_bit": None, "update_bit": None}],
			"Spruce": ["minecraft:spruce_leaves", {"distance": "7", "persistent": "false", "waterlogged": "false", "old_leaf_type": None, "new_leaf_type": None, "persistent_bit": None, "update_bit": None}],
			"Birch": ["minecraft:birch_leaves", {"distance": "7", "persistent": "false", "waterlogged": "false", "old_leaf_type": None, "new_leaf_type": None, "persistent_bit": None, "update_bit": None}],
			"Jungle": ["minecraft:jungle_leaves", {"distance": "7", "persistent": "false", "waterlogged": "false", "old_leaf_type": None, "new_leaf_type": None, "persistent_bit": None, "update_bit": None}],
			"Acacia": ["minecraft:acacia_leaves", {"distance": "7", "persistent": "false", "waterlogged": "false", "old_leaf_type": None, "new_leaf_type": None, "persistent_bit": None, "update_bit": None}],
			"Dark Oak": ["minecraft:dark_oak_leaves", {"distance": "7", "persistent": "false", "waterlogged": "false", "old_leaf_type": None, "new_leaf_type": None, "persistent_bit": None, "update_bit": None}],
		},
		"1.17.0": {
			"Oak": ["minecraft:oak_leaves", {"distance": "7", "persistent": "false", "waterlogged": "false", "old_leaf_type": None, "new_leaf_type": None, "persistent_bit": None, "update_bit": None}],
			"Spruce": ["minecraft:spruce_leaves", {"distance": "7", "persistent": "false", "waterlogged": "false", "old_leaf_type": None, "new_leaf_type": None, "persistent_bit": None, "update_bit": None}],
			"Birch": ["minecraft:birch_leaves", {"distance": "7", "persistent": "false", "waterlogged": "false", "old_leaf_type": None, "new_leaf_type": None, "persistent_bit": None, "update_bit": None}],
			"Jungle": ["minecraft:jungle_leaves", {"distance": "7", "persistent": "false", "waterlogged": "false", "old_leaf_type": None, "new_leaf_type": None, "persistent_bit": None, "update_bit": None}],
			"Acacia": ["minecraft:acacia_leaves", {"distance": "7", "persistent": "false", "waterlogged": "false", "old_leaf_type": None, "new_leaf_type": None, "persistent_bit": None, "update_bit": None}],
			"Dark Oak": ["minecraft:dark_oak_leaves", {"distance": "7", "persistent": "false", "waterlogged": "false", "old_leaf_type": None, "new_leaf_type": None, "persistent_bit": None, "update_bit": None}],
		}
	},
	"bedrock": {
		"1.20.0": {
			"Oak": ["minecraft:leaves", {"old_leaf_type": "oak", "persistent_bit": "false", "update_bit": "false", "distance": None, "persistent": None, "waterlogged": None, "new_leaf_type": None}],
			"Spruce": ["minecraft:leaves", {"old_leaf_type": "spruce", "persistent_bit": "false", "update_bit": "false", "distance": None, "persistent": None, "waterlogged": None, "new_leaf_type": None}],
			"Birch": ["minecraft:leaves", {"old_leaf_type": "birch", "persistent_bit": "false", "update_bit": "false", "distance": None, "persistent": None, "waterlogged": None, "new_leaf_type": None}],
			"Jungle": ["minecraft:leaves", {"old_leaf_type": "jungle", "persistent_bit": "false", "update_bit": "false", "distance": None, "persistent": None, "waterlogged": None, "new_leaf_type": None}],
			"Acacia": ["minecraft:leaves2", {"new_leaf_type": "acacia", "persistent_bit": "false", "update_bit": "false", "distance": None, "persistent": None, "waterlogged": None, "old_leaf_type": None}],
			"Dark Oak": ["minecraft:leaves2", {"new_leaf_type": "dark_oak", "persistent_bit": "false", "update_bit": "false", "distance": None, "persistent": None, "waterlogged": None, "old_leaf_type": None}],
			"Azalea": ["minecraft:azalea_leaves", {"persistent_bit": "false", "update_bit": "false", "distance": None, "persistent": None, "waterlogged": None, "old_leaf_type": None, "new_leaf_type": None}],
			"Azalea Flowered": ["minecraft:azalea_leaves_flowered", {"persistent_bit": "false", "update_bit": "false", "distance": None, "persistent": None, "waterlogged": None, "old_leaf_type": None, "new_leaf_type": None}],
			"Mangrove": ["minecraft:mangrove_leaves", {"persistent_bit": "false", "update_bit": "false", "distance": None, "persistent": None, "waterlogged": None, "old_leaf_type": None, "new_leaf_type": None}],
			"Cherry": ["minecraft:cherry_leaves", {"persistent_bit": "false", "update_bit": "false", "distance": None, "persistent": None, "waterlogged": None, "old_leaf_type": None, "new_leaf_type": None}]
		},
		"1.19.0": {
			"Oak": ["minecraft:leaves", {"old_leaf_type": "oak", "persistent_bit": "false", "update_bit": "false", "distance": None, "persistent": None, "waterlogged": None, "new_leaf_type": None}],
			"Spruce": ["minecraft:leaves", {"old_leaf_type": "spruce", "persistent_bit": "false", "update_bit": "false", "distance": None, "persistent": None, "waterlogged": None, "new_leaf_type": None}],
			"Birch": ["minecraft:leaves", {"old_leaf_type": "birch", "persistent_bit": "false", "update_bit": "false", "distance": None, "persistent": None, "waterlogged": None, "new_leaf_type": None}],
			"Jungle": ["minecraft:leaves", {"old_leaf_type": "jungle", "persistent_bit": "false", "update_bit": "false", "distance": None, "persistent": None, "waterlogged": None, "new_leaf_type": None}],
			"Acacia": ["minecraft:leaves2", {"new_leaf_type": "acacia", "persistent_bit": "false", "update_bit": "false", "distance": None, "persistent": None, "waterlogged": None, "old_leaf_type": None}],
			"Dark Oak": ["minecraft:leaves2", {"new_leaf_type": "dark_oak", "persistent_bit": "false", "update_bit": "false", "distance": None, "persistent": None, "waterlogged": None, "old_leaf_type": None}],
			"Azalea": ["minecraft:azalea_leaves", {"persistent_bit": "false", "update_bit": "false", "distance": None, "persistent": None, "waterlogged": None, "old_leaf_type": None, "new_leaf_type": None}],
			"Azalea Flowered": ["minecraft:azalea_leaves_flowered", {"persistent_bit": "false", "update_bit": "false", "distance": None, "persistent": None, "waterlogged": None, "old_leaf_type": None, "new_leaf_type": None}],
			"Mangrove": ["minecraft:mangrove_leaves", {"persistent_bit": "false", "update_bit": "false", "distance": None, "persistent": None, "waterlogged": None, "old_leaf_type": None, "new_leaf_type": None}]
		},
		"1.18.0": {
			"Oak": ["minecraft:leaves", {"old_leaf_type": "oak", "persistent_bit": "false", "update_bit": "false", "distance": None, "persistent": None, "waterlogged": None, "new_leaf_type": None}],
			"Spruce": ["minecraft:leaves", {"old_leaf_type": "spruce", "persistent_bit": "false", "update_bit": "false", "distance": None, "persistent": None, "waterlogged": None, "new_leaf_type": None}],
			"Birch": ["minecraft:leaves", {"old_leaf_type": "birch", "persistent_bit": "false", "update_bit": "false", "distance": None, "persistent": None, "waterlogged": None, "new_leaf_type": None}],
			"Jungle": ["minecraft:leaves", {"old_leaf_type": "jungle", "persistent_bit": "false", "update_bit": "false", "distance": None, "persistent": None, "waterlogged": None, "new_leaf_type": None}],
			"Acacia": ["minecraft:leaves2", {"new_leaf_type": "acacia", "persistent_bit": "false", "update_bit": "false", "distance": None, "persistent": None, "waterlogged": None, "old_leaf_type": None}],
			"Dark Oak": ["minecraft:leaves2", {"new_leaf_type": "dark_oak", "persistent_bit": "false", "update_bit": "false", "distance": None, "persistent": None, "waterlogged": None, "old_leaf_type": None}],
			"Azalea": ["minecraft:azalea_leaves", {"persistent_bit": "false", "update_bit": "false", "distance": None, "persistent": None, "waterlogged": None, "old_leaf_type": None, "new_leaf_type": None}],
			"Azalea Flowered": ["minecraft:azalea_leaves_flowered", {"persistent_bit": "false", "update_bit": "false", "distance": None, "persistent": None, "waterlogged": None, "old_leaf_type": None, "new_leaf_type": None}],
		},
		"1.17.0": {
			"Oak": ["minecraft:leaves", {"old_leaf_type": "oak", "persistent_bit": "false", "update_bit": "false", "distance": None, "persistent": None, "waterlogged": None, "new_leaf_type": None}],
			"Spruce": ["minecraft:leaves", {"old_leaf_type": "spruce", "persistent_bit": "false", "update_bit": "false", "distance": None, "persistent": None, "waterlogged": None, "new_leaf_type": None}],
			"Birch": ["minecraft:leaves", {"old_leaf_type": "birch", "persistent_bit": "false", "update_bit": "false", "distance": None, "persistent": None, "waterlogged": None, "new_leaf_type": None}],
			"Jungle": ["minecraft:leaves", {"old_leaf_type": "jungle", "persistent_bit": "false", "update_bit": "false", "distance": None, "persistent": None, "waterlogged": None, "new_leaf_type": None}],
			"Acacia": ["minecraft:leaves2", {"new_leaf_type": "acacia", "persistent_bit": "false", "update_bit": "false", "distance": None, "persistent": None, "waterlogged": None, "old_leaf_type": None}],
			"Dark Oak": ["minecraft:leaves2", {"new_leaf_type": "dark_oak", "persistent_bit": "false", "update_bit": "false", "distance": None, "persistent": None, "waterlogged": None, "old_leaf_type": None}],
		}
	}
}

#retrieves nested values from a dictionary using a list of keys.
def get_from_dict(data_dict, map_list):
	for k in map_list:
		data_dict = data_dict.get(k, {})
	return data_dict

#determines whether a bedrock block requires an old or new leaf type.
def get_leaf_info(platform, key_version, leaf):
	leaf_info = get_from_dict(leaves_universal_mapping, [platform, key_version, leaf])
	blockstate, properties = leaf_info if leaf_info else [None, {}]

	for key in ['old_leaf_type', 'new_leaf_type']:
		if key in properties:
			return [key, properties[key]]

	return None

#formats nanoseconds into a human-readable string.
def pretty_time_delta_ns(nanoseconds):
	sign_string = '-' if nanoseconds < 0 else ''
	nanoseconds = abs(int(nanoseconds))
	days, nanoseconds = divmod(nanoseconds, 86400*(10**9))
	hours, nanoseconds = divmod(nanoseconds, 3600*(10**9))
	minutes, nanoseconds = divmod(nanoseconds, 60*(10**9))
	seconds, nanoseconds = divmod(nanoseconds, 10**9)
	milliseconds, nanoseconds = divmod(nanoseconds, 10**6)

	if days > 0:
		return f"{sign_string}{days}d {hours}h {minutes}m {seconds}s"
	elif hours > 0:
		return f"{sign_string}{hours}h {minutes}m {seconds}s"
	elif minutes > 0:
		return f"{sign_string}{minutes}m {seconds}s"
	elif seconds > 0:
		return f"{sign_string}{seconds}s"
	elif milliseconds > 0:
		return f"{sign_string}{milliseconds}ms"
	else:
		return f"{sign_string}{nanoseconds}ns"

#fetches a block and its extras at given coordinates from a world and translates them from universal format.
def get_block(dimension, world, x, y, z, world_versions) -> Tuple[Any, Any, Any]:
	world_trans = world.translation_manager.get_version(*world_versions)

	chunk_coords = block_coords_to_chunk_coords(x, z)
	cx = x - 16 * chunk_coords[0]
	cz = z - 16 * chunk_coords[1]

	chunk = world.get_chunk(chunk_coords[0], chunk_coords[1], dimension)
	runtime_id = chunk.blocks[cx, y, cz]
	uni_block = chunk.block_palette[runtime_id]
	(block_object, _, block_extras) = world_trans.block.from_universal(uni_block, None)
	return (block_object, block_extras)

#determines the nearest applicable version for a given key from a mapping, considering world's platform and version.
def get_closest_version(world,leaves_universal_mapping, world_platform, world_version, key):
	version_number = world.translation_manager.get_version(world_platform, world_version).version_number

	platform_dict = leaves_universal_mapping.get(world_platform, {})

	versions = sorted([tuple(map(int, v.split('.'))) for v in platform_dict.keys()], reverse=True)

	for v in versions:
		if v <= version_number:
			closest_version = '.'.join(map(str, v))
			break
	else:
		closest_version = '.'.join(map(str, versions[-1]))

	key_dict = platform_dict.get(closest_version, {}).get(key, {})
	return [key,key_dict,closest_version]

#retrieves the types of trees for a specific game version.
def get_trees_in_version(world,leaves_universal_mapping, world_platform, world_version):
	version_number = world.translation_manager.get_version(world_platform, world_version).version_number

	platform_dict = leaves_universal_mapping.get(world_platform, {})

	versions = sorted([tuple(map(int, v.split('.'))) for v in platform_dict.keys()], reverse=True)

	for v in versions:
		if v <= version_number:
			closest_version = '.'.join(map(str, v))
			break
	else:
		closest_version = '.'.join(map(str, versions[-1]))

	tree_keys = platform_dict.get(closest_version, {}).keys()
	return tree_keys

#places a leaf block at given coordinates with provided properties and extra blocks.
def set_leaf_block(world, x, y, z, dimension, world_versions, block_namespace, block_name, block_prop, block_extras):
	leaves_block = Block(
		block_namespace,
		block_name,
		block_prop,
		extra_blocks=block_extras
	)
	world.set_version_block(x, y, z, dimension, world_versions, leaves_block)

#fixes leaf decay issues in Minecraft world based on user's selection and world's version/platform.
def fix_leaf_decay(world: BaseLevel, dimension: Dimension, selection: SelectionGroup, options: dict):
	try:
		#starts the operation timer and prints a starting message
		start_time = time.perf_counter_ns()
		print("\n" * 2 + "Starting the operation...")

		#copies the selected options into a new variable
		tree_bool = options.copy()

		#extracts platform and version information from the world
		world_platform = world.level_wrapper.platform
		world_version = world.level_wrapper.version
		world_versions = (world_platform, world_version)
		
		#maps appropriate leaf properties keys based on the world platform
		persistent_key = {"java":"persistent","bedrock":"persistent_bit"}.get(world_platform)
		bedrock_update_bit_key = "update_bit"

		#predefines NBT tags for future use
		byte_tag_true = ByteTag(1)
		byte_tag_false = ByteTag(0)
		string_tag_true = StringTag("true")

		#retrieves tree types for the current world version and platform
		tree_types = get_trees_in_version(world,leaves_universal_mapping, world_platform, world_version)

		#maps selected tree types to the closest available version in the world instance
		trees = []
		found_version = False
		for treebool in tree_bool.keys():
			if treebool in tree_types and tree_bool[treebool]:
				treekey, key_dict, key_version = get_closest_version(world, leaves_universal_mapping, world_platform, world_version, treebool)
				trees.append([treekey, key_dict,key_version])
				if found_version == False:
					print("Loaded leaves mapping from version: "+str(key_version))
					found_version = True

		#throws error if no tree types were selected
		if not trees:
			raise ValueError("You need to select atleast one checkbox!")

		#iterates over each block in the selection
		for box in selection.merge_boxes().selection_boxes:
			for x, y, z in box:
				#retrieves block and associated data at given coordinates
				(block_object, block_extras) = get_block(dimension, world, x, y, z, world_versions)

				#extracts block name details
				block_name = block_object.base_name
				block_namespace = block_object.namespace
				block_namespaced = block_object.namespaced_name

				#skips non-leaf or non-vanilla blocks
				if "leave" not in block_name or block_namespace != "minecraft":
					continue

				#iterates over selected tree types
				for valid_tree in trees:
					key_dicts = valid_tree[1]

					#checks if current block matches with the selected tree type
					if key_dicts[0] == block_namespaced:
						treekey = valid_tree[0]
						key_version = valid_tree[2]
						block_prop = block_object.properties

						#retrieves leaf type information for the current version
						leaves_type = get_leaf_info(world_platform, key_version, treekey)

						#handles specific properties for Bedrock edition leaf blocks
						if world_platform == "bedrock":

							#updates block properties to prevent decay
							should_break = False

							if leaves_type is not None:
								leaf_type_value, leaf_type_key = leaves_type
								leaf_block = block_prop.get(leaf_type_value, None)

								if leaf_block is not None and leaf_block == leaf_type_key:
									should_break = True

							block_prop[persistent_key] = byte_tag_true
							block_prop[bedrock_update_bit_key] = byte_tag_false
							set_leaf_block(world, x, y, z, dimension, world_versions, block_namespace, block_name, block_prop, block_extras)

							if should_break:
								break

						#handles Java Edition leaf blocks; updates the block properties to prevent decay
						elif world_platform == "java":
							block_prop[persistent_key] = string_tag_true
							set_leaf_block(world, x, y, z, dimension, world_versions, block_namespace, block_name, block_prop, block_extras)
							break

	#handles exceptions and prints out detailed error information for debugging
	except Exception as e:
		print()
		print("ERROR MESSAGE:")
		print(str(e))
		print()
		print("TRACEBACK:")
		print(traceback.format_exc())

	else:
		#calculates and prints the elapsed time once the operation is successfully completed
		elapsed_time = time.perf_counter_ns() - start_time
		print(f"Operation completion time: {pretty_time_delta_ns(elapsed_time)}")

#exports the operation and its options for use in the program
export = {
	"name": "Fix Leaf Decay",
	"operation": fix_leaf_decay,
	"options": operation_options,
}