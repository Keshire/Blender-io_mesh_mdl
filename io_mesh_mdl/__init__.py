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

# <pep8-80 compliant>

bl_info = {
    "name": "Lionhead MDL format",
    "author": "Jonathan Mattison (Keshire)",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "File > Import-Export > Lionhead MDL",
    "description": "Import-Export Lionhead MDL files",
    "category": "Import-Export"}
	
if "bpy" in locals():
    import importlib
    if "import_mdl" in locals():
        importlib.reload(import_mdl)

#includes
import os
import bpy
from bpy.props import StringProperty, BoolProperty, CollectionProperty
from bpy_extras.io_utils import ExportHelper, ImportHelper


class ImportMDL(bpy.types.Operator, ImportHelper):
	'''Load MDL mesh data'''
	bl_idname = "import_mesh.mdl"
	bl_label = "Import MDL"

	filename_ext = ".mdl"

	filter_glob = StringProperty(	default="*.mdl", 
									options={'HIDDEN'})

	files = CollectionProperty(	name="File Path", 
								description="File path used for importing the MDL file", 
								type=bpy.types.OperatorFileListElement)

	directory = StringProperty(	subtype='DIR_PATH')

	def execute(self, context):
		from . import import_mdl
		print('Importing file', self.filepath)
		with open(self.filepath, 'rb') as file:
			import_mdl.read(file, context, self)
		return {'FINISHED'}

def menu_import(self, context):
    self.layout.operator(ImportMDL.bl_idname, text="Lionhead MDL (.mdl)").filepath = "*.mdl"

	
__classes__ = (
	ImportMDL
)

def register():
	bpy.utils.register_class(ImportMDL)
	bpy.types.TOPBAR_MT_file_import.append(menu_import)
	
def unregister():
	bpy.utils.unregister_class(ImportMDL)
	bpy.types.TOPBAR_MT_file_import.remove(menu_import)

if __name__ == "__main__":
    register()
