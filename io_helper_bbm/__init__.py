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
    "name": "Lionhead Fable:A Helpers",
    "author": "Jonathan Mattison (Keshire)",
    "version": (0, 0, 1),
    "blender": (2, 82, 0),
    "location": "File > Import-Export > Lionhead Fable:A Helpers",
    "description": "Import-Export Lionhead Fable:A Helpers",
    "category": "Import-Export"}
	
#includes
import os
import bpy
import struct
import mathutils
import zlib
from bpy_extras.io_utils import (ImportHelper,ExportHelper)
from bpy.props import (
    StringProperty,
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    FloatProperty,
)

class ImportBBM(bpy.types.Operator, ImportHelper):
	'''load empty helper data'''
	bl_idname = "import_helpers.bbm"
	bl_label = "Import BBM"
	filename_ext = ".bbm"
	filter_glob = StringProperty(default="*.bbm", options={'HIDDEN'})
	files = CollectionProperty(name="File Path", description="File Path", type=bpy.types.OperatorFileListElement)
	directory = StringProperty(subtype='DIR_PATH')

	def execute(self, context):
		with open(self.filepath, 'rb') as file:
			import_bbm(file, context, self)
		return {'FINISHED'}	

class ExportBBM(bpy.types.Operator, ExportHelper):
	'''Write empty helper data'''
	bl_idname = "export_helpers.bbm"
	bl_label = "Export BBM"
	filename_ext = ".bbm"
	filter_glob = StringProperty(default="*.bbm", options={'HIDDEN'})
	files = CollectionProperty(name="File Path", description="File Path", type=bpy.types.OperatorFileListElement)
	directory = StringProperty(subtype='DIR_PATH')

	def execute(self, context):
		with open(self.filepath, 'wb') as file:
			export_bbm(file, context, self)
		return {'FINISHED'}	


#Plugin loading functions#
def menu_import(self, context):
    self.layout.operator(ImportBBM.bl_idname, text="Fable:A BBM (.bbm)").filepath = "*.bbm"

def menu_export(self, context):
    self.layout.operator(ExportBBM.bl_idname, text="Fable:A BBM (.bbm)").filepath = "*.bbm"

def register():
	bpy.utils.register_class(ImportBBM)
	bpy.utils.register_class(ExportBBM)
	bpy.types.TOPBAR_MT_file_import.append(menu_import)
	bpy.types.TOPBAR_MT_file_export.append(menu_export)
	
def unregister():
	bpy.utils.unregister_class(ImportBBM)
	bpy.utils.unregister_class(ExportBBM)
	bpy.types.TOPBAR_MT_file_import.remove(menu_import)
	bpy.types.TOPBAR_MT_file_export.remove(menu_export)
	
if __name__ == "__main__":
    register()

#Main Import function#	
def import_bbm(file, context, self):

	scn_root = bpy.context.collection
	#de-select all objects
	for o in scn_root.objects: o.select_set(state=False)
	#create a new collection for helpers
	scn = bpy.data.collections.new('HLPR')
	scn_root.children.link(scn)
	
	name,crc = read_string(file)
	scn['export_name'] = name
	scn['export_crc'] = crc #probably won't need this.
	
	isSkeletal = struct.unpack('<?', file.read(1))[0]
	scn['export_isSkeletal'] = isSkeletal
	origin = read_helper_origin(file)
	scn['export_origin'] = origin
	
	HPNT_Count = struct.unpack('<H', file.read(2))[0]
	HDMY_Count = struct.unpack('<H', file.read(2))[0]
	HLPR_Size = struct.unpack('<I', file.read(4))[0]
	file.read(2) # Padding
	
	#Well, shit. points and dummies, sorted by crc. Strings are sorted alphabetically. Don't match...3270660459
	if HPNT_Count > 0:
		compressed_size = struct.unpack('<H', file.read(2))[0] #file should be unpacked
		HPNT = {}
		for i in range(HPNT_Count):
			p = read_helper_point_origin(file)
			HPNT[p.index] = p
				
	if HDMY_Count > 0:
		compressed_size = struct.unpack('<H', file.read(2))[0] #file should be unpacked	
		HDMY = {}
		for i in range(HDMY_Count):
			d = read_helper_dummy_origin(file)
			HDMY[d.index] = d
	
	if HLPR_Size > 0:
		compressed_size = struct.unpack('<H', file.read(2))[0] #file should be unpacked
		
		point_block = struct.unpack('<H', file.read(2))[0]
		points = {}
		for i in range(HPNT_Count):
			name,index = read_string(file)
			HPNT[index].name = name
			points[i] = HPNT[index]
			
			p = bpy.data.objects.new('HPNT_'+points[i].name,None)
			p.location = (points[i].x,points[i].y,points[i].z)
			p.empty_display_size = 0.1
			p.empty_display_type = 'PLAIN_AXES'
			scn.objects.link(p)
		
		file.read(1) # end of block
		
		dummy_block = HLPR_Size - point_block
		dummies = {}
		for i in range(HDMY_Count):
			name,index = read_string(file)
			HDMY[index].name = name
			dummies[i] = HDMY[index]
			p = bpy.data.objects.new('HDMY_'+dummies[i].name,None)
			p.matrix_local = dummies[i].matrix
			p.empty_display_size = 10
			p.empty_display_type = 'ARROWS'
			scn.objects.link(p)
		
		file.read(1) # end of block
	
	#All this can be empty, may not even be read by the game.
	file.read(4) #material
	file.read(4) #submesh
	file.read(4) #bone
	file.read(4) #boneindex
	file.read(1) #pad
	file.read(2) #unk
	file.read(2) #unk
	scn['export_matrix'] = mathutils.Matrix(read_helper_matrix(file))

#Main Export function#	
def export_bbm(file, context, self):
	#Get the Collection Meta Data
	col = bpy.data.collections.get("HLPR")
	
	name = col['export_name']
	isSkeletal = col['export_isSkeletal']
	origin = col['export_origin']
	matrix = col['export_matrix']
	
	file.write(write_string(name))
	file.write(struct.pack('<?',isSkeletal))
	file.write(write_helper_origin(origin))
	
	HPNT = [obj for obj in bpy.context.scene.objects if obj.name.startswith("HPNT_")]
	HPNT_Count = len(HPNT)
	HDMY = [obj for obj in bpy.context.scene.objects if obj.name.startswith("HDMY_")]
	HDMY_Count = len(HDMY)
	
	file.write(struct.pack('<H', HPNT_Count))
	file.write(struct.pack('<H', HDMY_Count))
	
	#Strings are sorted alphabetically
	HPNT = sorted(HPNT, key=lambda point: point.name[5:])
	HDMY = sorted(HDMY, key=lambda dummy: dummy.name[5:])
	HLPR = b''
	#build helper block to get size
	for i in range(HPNT_Count):
		HLPR += write_string(HPNT[i].name[5:])
	HLPR += b'\x00' #padding
	
	point_block = len(HLPR)+2 #needs to take into account itself.
	HLPR = struct.pack('<H',point_block)+HLPR #self and point block

	for i in range(HDMY_Count):
		HLPR += write_string(HDMY[i].name[5:])
	HLPR += b'\x00' #padding
	
	HLPR_Size = len(HLPR) #Total size
	file.write(struct.pack('<I', HLPR_Size))
	file.write(b'\x00\x00')#Pad
	
	compressed_size = b'\x00\x00' #Unpacked 0000
	file.write(compressed_size)
	#HPNTs sorted by crc
	HPNT = sorted(HPNT, key=lambda point: (0xffffffff - zlib.crc32(point.name[5:].encode('utf-8'),0xffffffff)))
	for i in range(HPNT_Count):
		file.write(write_helper_point_origin(HPNT[i]))

	file.write(compressed_size)
	#HDMYs sorted by crc
	HDMY = sorted(HDMY, key=lambda dummy: (0xffffffff - zlib.crc32(dummy.name[5:].encode('utf-8'),0xffffffff)))
	for i in range(HDMY_Count):
		file.write(write_helper_dummy_origin(HDMY[i]))
	
	file.write(compressed_size)
	#HLPR index sorted alphabetically
	file.write(HLPR)
	
	#All this can be empty, may not even be read by the game.
	file.write(b'\x00\x00\x00\x00') #material
	file.write(b'\x00\x00\x00\x00') #submesh
	file.write(b'\x00\x00\x00\x00') #bone
	file.write(b'\x00\x00\x00\x00')#boneindex
	file.write(b'\x00') #pad
	file.write(b'\x00\x00') #unk
	file.write(b'\x00\x00') #unk

	file.write(write_helper_matrix(matrix))
	
	
#Utility import functions#
class read_helper_point_origin:
	def __init__(self,file):
		self.name = "None"
		self.index = struct.unpack('<I', file.read(4))[0]
		self.x = struct.unpack('<f', file.read(4))[0]/100
		self.y = struct.unpack('<f', file.read(4))[0]/100
		self.z = struct.unpack('<f', file.read(4))[0]/100
		self.hierarchy = struct.unpack('<I', file.read(4))[0]

class read_helper_dummy_origin:
	def __init__(self,file):
		self.name = "None"
		self.index = struct.unpack('<I', file.read(4))[0]
		self.matrix = read_helper_matrix(file)
		self.hierarchy = struct.unpack('<I', file.read(4))[0]

def read_helper_matrix(file):
	fmt = '<12f' #3x4, scale = (1,1,1) to make it 4x4 I beleive
	_s = file.read(struct.calcsize(fmt))
	f = struct.unpack(fmt, _s)
	matrix = (	(f[0]/100,f[ 1]/100,f[ 2]/100,1),
				(f[3]/100,f[ 4]/100,f[ 5]/100,1),
				(f[6]/100,f[ 7]/100,f[ 8]/100,1),
				(f[9]/100,f[10]/100,f[11]/100,1)) 
	return matrix

def read_helper_origin(file):
	fmt = '<10f' #3x3, scale = 1
	_s = file.read(struct.calcsize(fmt))
	matrix = struct.unpack(fmt, _s)
	return matrix

def read_string(file):
	#read in the characters till we get a null character
	s = b''
	while True:
		c = struct.unpack('<c', file.read(1))[0]
		if c == b'\x00':
			break
		s += c
	crc = (0xffffffff - zlib.crc32(s,0xffffffff))
	#remove the null character from the string
	return str(s, "utf-8", "replace"), crc

def write_helper_point_origin(point):
	point_out = struct.pack('<I',(0xffffffff - zlib.crc32(point.name[5:].encode('utf-8'),0xffffffff)))
	point_out += struct.pack('<f',point.location.x*100)
	point_out += struct.pack('<f',point.location.y*100)
	point_out += struct.pack('<f',point.location.z*100)
	point_out += (b'\xFF\xFF\xFF\xFF')
	return point_out

def write_helper_dummy_origin(dummy):
	dummy_out = struct.pack('<I',(0xffffffff - zlib.crc32(dummy.name[5:].encode('utf-8'),0xffffffff)))
	dummy_out += write_helper_matrix(dummy.matrix_local)
	dummy_out += (b'\xFF\xFF\xFF\xFF')
	return dummy_out

def write_helper_matrix(m):
	fmt = '<12f' #3x4, scale = (1,1,1) to make it 4x4 I beleive
	return struct.pack(fmt,m[0][0]*100,m[1][0]*100,m[2][0]*100,
						   m[0][1]*100,m[1][1]*100,m[2][1]*100,
						   m[0][2]*100,m[1][2]*100,m[2][2]*100,
						   m[0][3]*100,m[1][3]*100,m[2][3]*100)

def write_helper_origin(o):
	fmt = '<10f' #3x3, scale = 1
	return struct.pack(fmt,o[0],o[1],o[2],o[3],o[4],o[5],o[6],o[7],o[8],o[9])

def write_string(string):
	encoded_text = string.encode('utf-8')
	return encoded_text + b'\x00'