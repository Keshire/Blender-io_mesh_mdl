# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Lionhead Fable Anniversary Binary Helpers",
    "author": "Jonathan Mattison (Keshire)",
    "version": (0, 0, 1),
    "blender": (2, 82, 0),
    "location": "File > Import-Export > Lionhead Binary Helpers",
    "description": "Import-Export Lionhead Binary Helpers",
    "category": "Import-Export"}
	
#includes
import os
import bpy
import lzma
import struct

from bpy.props import (
    StringProperty,
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    FloatProperty,
)
from bpy_extras.io_utils import (
    ImportHelper,
    ExportHelper,
)

class ImportBIN(bpy.types.Operator, ImportHelper):
	'''Load MDL mesh data'''
	bl_idname = "import_helpers.bin"
	bl_label = "Import BIN"
	filename_ext = ".bin"
	filter_glob = StringProperty(default="*.bin", options={'HIDDEN'})
	files = CollectionProperty(name="File Path", description="File path used for importing the BIN file", type=bpy.types.OperatorFileListElement)
	directory = StringProperty(subtype='DIR_PATH')

	def execute(self, context):
		with open(self.filepath, 'rb') as file:
			import_bin(file, context, self)
		return {'FINISHED'}	
		
def menu_import(self, context):
    self.layout.operator(ImportBIN.bl_idname, text="Lionhead BIN (.bin)").filepath = "*.bin"

def register():
	bpy.utils.register_class(ImportBIN)
	bpy.types.TOPBAR_MT_file_import.append(menu_import)
	
def unregister():
	bpy.utils.unregister_class(ImportBIN)
	bpy.types.TOPBAR_MT_file_import.remove(menu_import)
	
if __name__ == "__main__":
    register()
	
def read_string(file):
	#read in the characters till we get a null character
	s = b''
	while True:
		c = struct.unpack('<c', file.read(1))[0]
		if c == b'\x00':
			break
		s += c

	#remove the null character from the string
	return str(s, "utf-8", "replace")

def float10(file):
	fmt = 'f' * 10
	_s = file.read(struct.calcsize(fmt))
	float10 = struct.unpack(fmt, _s)
	return float10

def import_bin(file, context, self):
	#Create the Scene Root
	scn = bpy.context.collection
	for o in scn.objects: o.select_set(state=False)
	sName = read_string(file)
	print(sName)
	bSkeleton = struct.unpack('<?', file.read(1))[0]
	aOrigin = float10(file)
	HPNT_Count = struct.unpack('<H', file.read(2))[0]
	HDMY_Count = struct.unpack('<H', file.read(2))[0]
	
	HLPR_Uncompressed = struct.unpack('<I', file.read(4))[0]
	Pad = file.read(4)
	
	HPNT_CompressedSize = struct.unpack('<H', file.read(2))[0]
	print(HPNT_CompressedSize)
	HPNT_Chunk = file.read(HPNT_CompressedSize)
	HPNT = lzma.decompress(HPNT_Chunk)
	print(HPNT)
	'''
	HPNT_Origin = {}
	HPNT = {}
	for i in range(HPNT_Count):
		HPNT_Origin[i] = helper_point_origin(file)
		HPNT[i] = struct.unpack('<I', file.read(4))[0]
		print(str(HPNT_Origin[i])+str(HPNT[i]))
	'''
		
	#HDMY_CompressedSize = struct.unpack('<H', file.read(2))[0]
	#print(HDMY_CompressedSize)
	#HDMY_Chunk = file.read(HDMY_CompressedSize)
	'''
	HDMY_Origin = {}
	HDMY = {}
	for i in range(HDMY_Count):
		HDMY_Origin[i] = helper_dummy_origin(file)
		HDMY[i] = struct.unpack('<I', file.read(4))[0]
		print(str(HDMY_Origin[i])+str(HDMY[i]))
	'''
	
	#HLPR_Compressed = struct.unpack('<H', file.read(2))[0]
	#print(HLPR_Compressed)
	
	'''
	HPNT_IndexSize = struct.unpack('<H', file.read(2))[0]
	
	HPNT_Index = {}
	for i in range(HPNT_IndexSize):
		HPNT_Index[i] = struct.unpack('<c', file.read(1))[0]
	print(HPNT_Index)
	
	HDMY_Index = {}
	for i in range(HLPR_Uncompressed-HPNT_IndexSize):
		HDMY_Index[i] = struct.unpack('<c', file.read(1))[0]
	print(HDMY_Index)
	'''
	
def helper_point_origin(file):
	fmt = 'f' * 4
	_s = file.read(struct.calcsize(fmt))
	floats = struct.unpack(fmt, _s)
	return floats

def helper_dummy_origin(file):
	fmt = 'f' * 13
	_s = file.read(struct.calcsize(fmt))
	floats = struct.unpack(fmt, _s)
	return floats