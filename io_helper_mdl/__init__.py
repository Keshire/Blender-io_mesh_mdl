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
from io_helper_mdl.lzo_spec import (Lzo_Codec)

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

def import_bin(file, context, self):
	#Create the Scene Root
	scn = bpy.context.collection
	for o in scn.objects: o.select_set(state=False)
	name = read_string(file)
	isSkeletal = struct.unpack('<?', file.read(1))[0]
	matrix = helper_model_origin(file)
	HPNT_Count = struct.unpack('<H', file.read(2))[0]
	HDMY_Count = struct.unpack('<H', file.read(2))[0]
	
	HLPR_Size = struct.unpack('<I', file.read(4))[0]
	Pad = file.read(2)
	
	if HPNT_Count > 0:
		HPNT = {}
		size = struct.unpack('<H', file.read(2))[0]
		print('HPNT size:'+str(size))
		if size > 0:
			src = file.read(size)
			dst = bytearray((4*4)*HPNT_Count)
			result = Lzo_Codec.Lzo1x_Decompress(src, 0, size+5, dst, 0)
			print(result)
			print(dst)
		
		for i in range(HPNT_Count):
			HPNT[i] = helper_point_origin(file)
				
	if HDMY_Count > 0:
		HDMY = {}
		size = struct.unpack('<H', file.read(2))[0]
		print('HDMY size:'+str(size))
		if size > 0:
			src = file.read(size+3)
			dst = bytearray((13*4)*HDMY_Count)
			result = Lzo_Codec.Lzo1x_Decompress(src, 0, size+3, dst, 0)
			print(str(result)+','+str(len(dst)))
			print(dst)

		for i in range(HDMY_Count):
			HDMY[i] = helper_dummy_origin(file)

def helper_point_origin(file):
	fmt = '<5i'
	_s = file.read(struct.calcsize(fmt))
	point = struct.unpack(fmt, _s)
	return point

def helper_dummy_origin(file):
	fmt = '<13i'
	_s = file.read(struct.calcsize(fmt))
	dummy = struct.unpack(fmt, _s)
	return dummy
	
def helper_model_origin(file):
	fmt = '<10f'
	_s = file.read(struct.calcsize(fmt))
	matrix = struct.unpack(fmt, _s)
	return matrix
	
def adjust_in_out(src):
	soffset = (src[1] << 8) + src[0];
	print(soffset)
	return soffset