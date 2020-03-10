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


#includes
import os
import os.path
import bpy
import struct
import math
import mathutils
from bpy_extras.io_utils import unpack_list, unpack_face_list, axis_conversion,orientation_helper
from bpy_extras.image_utils import load_image

##################
## Struct setup ##
##################

class material:
	def __init__(self, file):
		file.read(4) #Don't know what this is doing
		self.material = bpy.data.materials.new(name=read_string(file)) #Material Name
		file.read(4) #Don't know what this is doing

		self.material.use_nodes = True
		
		nodes = self.material.node_tree.nodes
		
		for node in nodes:
			nodes.remove(node)
		
		#Texture Nodes
		diffuse_texture = nodes.new(type='ShaderNodeTexImage')
		normal_texture = nodes.new(type='ShaderNodeTexImage')
		specular_texture = nodes.new(type='ShaderNodeTexImage')
		emission_texture = nodes.new(type='ShaderNodeTexImage')
		environment_texture = nodes.new(type='ShaderNodeTexImage')
		
		#Shader Nodes
		diffuse = nodes.new(type='ShaderNodeBsdfDiffuse')
		normal = nodes.new(type='ShaderNodeNormalMap')
		specular = nodes.new(type='ShaderNodeRGBCurve')
		emission = nodes.new(type='ShaderNodeEmission')
		mix = nodes.new(type='ShaderNodeMixShader')
		add = nodes.new(type='ShaderNodeAddShader')
		output = nodes.new(type='ShaderNodeOutputMaterial')
		
		refraction = nodes.new(type='ShaderNodeBsdfRefraction') # not sure if needed
		glossy = nodes.new(type='ShaderNodeBsdfGlossy')

		links = self.material.node_tree.links
		
		#Texture Links
		links.new(diffuse_texture.outputs[0],diffuse.inputs[0])
		links.new(normal_texture.outputs[0],normal.inputs[1])
		links.new(specular_texture.outputs[0],specular.inputs[1])
		links.new(emission_texture.outputs[0],emission.inputs[1])
		links.new(environment_texture.outputs[0],glossy.inputs[0])
		
		#Shader Links
		links.new(diffuse.outputs[0], mix.inputs[1])
		links.new(glossy.outputs[0], mix.inputs[2])
		links.new(specular.outputs[0], mix.inputs[0])
		
		links.new(normal.outputs[0], diffuse.inputs[2])
		links.new(normal.outputs[0], glossy.inputs[2])
		
		links.new(mix.outputs[0], add.inputs[0])
		links.new(emission.outputs[0], add.inputs[1])
		
		links.new(add.outputs[0], output.inputs[0])
		
		Type = struct.unpack('<I', file.read(4))[0]
		#print('Material Type: '+str(Type))
		
		#Honestly, no idea what this data is??
		if Type == 1:
			file.read(4) #Hash?
		elif Type == 2:
			file.read(4) #Hash?
		elif Type == 7:
			file.read(4) #Hash?
			struct.unpack('<I', file.read(4))[0]
			struct.unpack('<f', file.read(4))[0]
			struct.unpack('<f', file.read(4))[0]
			struct.unpack('<f', file.read(4))[0]
			struct.unpack('<f', file.read(4))[0]
			
			file.read(4) #Hash?
			
		elif Type == 11:
			file.read(4) #Hash?
			struct.unpack('<I', file.read(4))[0]
			struct.unpack('<f', file.read(4))[0]
			
			file.read(4) #Hash?
			struct.unpack('<I', file.read(4))[0]
			struct.unpack('<f', file.read(4))[0]
			struct.unpack('<f', file.read(4))[0]
			struct.unpack('<f', file.read(4))[0]
			struct.unpack('<f', file.read(4))[0]
			
			file.read(4) #Hash?
			
		sTextures = struct.unpack('<I', file.read(4))[0] #size of texture block in bytes
		
		texture = []
		for i in range(6):
			texture_name = read_string(file)
			print(texture_name)
			if texture_name != "":
				texture_path = os.path.basename(texture_name)
				texture.append(bpy.data.textures.new(name=texture_path + '.dds', type='IMAGE'))

				
		#Honestly, no idea what this data is??		
		struct.unpack('<f', file.read(4))[0]
		struct.unpack('<f', file.read(4))[0]

		#Honestly, no idea what this data is??
		if Type == 2:
			file.read(4) #Hash?
			struct.unpack('<I', file.read(4))[0]
			struct.unpack('<f', file.read(4))[0]
			
		elif Type == 7:
			file.read(4) #Hash?
			struct.unpack('<I', file.read(4))[0]
			struct.unpack('<f', file.read(4))[0]
			
			file.read(4) #Hash?
			struct.unpack('<I', file.read(4))[0]
			struct.unpack('<f', file.read(4))[0]
			
			file.read(4) #Hash?
			struct.unpack('<I', file.read(4))[0]
			struct.unpack('<f', file.read(4))[0]
			struct.unpack('<f', file.read(4))[0]
			struct.unpack('<f', file.read(4))[0]
			struct.unpack('<f', file.read(4))[0]
			
			file.read(4) #Hash?
			struct.unpack('<I', file.read(4))[0]
			struct.unpack('<f', file.read(4))[0]
			struct.unpack('<f', file.read(4))[0]
			struct.unpack('<f', file.read(4))[0]
			struct.unpack('<f', file.read(4))[0]

			file.read(4) #Hash?
			struct.unpack('<I', file.read(4))[0]
			struct.unpack('<f', file.read(4))[0]
			
		elif Type == 11:
			file.read(4) #Hash?
			struct.unpack('<I', file.read(4))[0]
			struct.unpack('<f', file.read(4))[0]
			struct.unpack('<f', file.read(4))[0]
			struct.unpack('<f', file.read(4))[0]
			struct.unpack('<f', file.read(4))[0]
			
			file.read(4) #Hash?
			struct.unpack('<I', file.read(4))[0]
			struct.unpack('<f', file.read(4))[0]
			
			file.read(4) #Hash?
			struct.unpack('<I', file.read(4))[0]
			struct.unpack('<f', file.read(4))[0]
			
			file.read(4) #Hash?
			struct.unpack('<I', file.read(4))[0]
			struct.unpack('<f', file.read(4))[0]
			
			file.read(4) #Hash?
			struct.unpack('<I', file.read(4))[0]
			struct.unpack('<f', file.read(4))[0]
			
			file.read(4) #Hash?
			struct.unpack('<I', file.read(4))[0]
			struct.unpack('<f', file.read(4))[0]
			struct.unpack('<f', file.read(4))[0]
			struct.unpack('<f', file.read(4))[0]
			struct.unpack('<f', file.read(4))[0]
			
			file.read(4) #Hash?
			struct.unpack('<I', file.read(4))[0]
			struct.unpack('<f', file.read(4))[0]
			struct.unpack('<f', file.read(4))[0]
			struct.unpack('<f', file.read(4))[0]
			struct.unpack('<f', file.read(4))[0]

			file.read(4) #Hash?
			struct.unpack('<I', file.read(4))[0]
			struct.unpack('<f', file.read(4))[0]
			
class mesh_split:
	def __init__(self, file, animated):
		unknown = file.read(4)
		print('Submesh Unknown: '+str(unknown))
		
		file.read(1)	#pad
		
		self.nTris = struct.unpack('<I', file.read(4))[0] # passed outside class
		
		pStart = struct.unpack('<I', file.read(4))[0] #offset pointer
		Origin = struct.unpack('<6f', file.read(24))[0]
		if animated:
			unknown = file.read(4)
			print('Animated Submesh Unknown: '+str(unknown))
					
class triangle:
	def __init__(self, file):
		self.v1 = struct.unpack('<h', file.read(2))[0]
		self.v2 = struct.unpack('<h', file.read(2))[0]
		self.v3 = struct.unpack('<h', file.read(2))[0]
		
class mesh:
	def __init__(self, file, animated):
	
		if animated:
			self.Name = "AnimatedObject"
		else:
			self.Name = read_string(file)
			
		file.read(1)	#pad

		iMesh 			= struct.unpack('<I', file.read(4))[0]
		self.iMaterial 	= struct.unpack('<I', file.read(4))[0]
		nTris 			= struct.unpack('<I', file.read(4))[0]
		
		unknown = struct.unpack('<I', file.read(4))[0] #unknown
		print(unknown)
		
		nVerts 	= struct.unpack('<I', file.read(4))[0]
		
		if not animated:
			origin = float10(file)
		
		nMeshSplit = struct.unpack('<I', file.read(4))[0]
		nTotalTris = 0
		
		MeshSplit = {}
		for i in range(nMeshSplit):
			MeshSplit[i] = mesh_split(file, animated)
			nTotalTris = nTotalTris + MeshSplit[i].nTris
		
		
		#An Array of bones used in this mesh
		if animated:
			self.BoneID = {}
			nCount = struct.unpack('<I', file.read(4))[0]
			print(nCount)
			for j in range(nCount):
				nCount2 = struct.unpack('<I', file.read(4))[0]
				print(nCount2)
				for i in range(nCount2):
					self.BoneID[i] = struct.unpack('<I', file.read(4))[0]
					print(self.BoneID[i])

		
		#XYZ, Unk, UV
		self.vert_1 = []
		vert_indice = []
		for i in range(nVerts):
			if animated:
				self.vert_1.extend([avect16_1(file)]) #An Array
			else:
				self.vert_1.extend([vect16_1(file)])
			
			vert_indice.append([self.vert_1[i].v[0], self.vert_1[i].v[1], self.vert_1[i].v[2]]) #An Index of xyz

			
		vert_2 = []
		vert_2_table = []
		for i in range(nVerts):
			vert_2.extend([vect16_2(file)]) #An Array
			vert_2_table.extend([vert_2[i].v[0], vert_2[i].v[1], vert_2[i].v[2]]) #an Index of v0,1,2
			#v[3] is always 0.0
			#v[4|5|6|7] is unknown, and I'm not even sure these are floats...
		
		
		#Morphing stuff??
		if animated:
			nArray = struct.unpack('<?', file.read(1))[0]
			if nArray == True:
				for i in range(nVerts):
					file.read(8)

		face = []
		face_indice = []
		for i in range(nTotalTris):
			face.extend([triangle(file)])
			face_indice.append([face[i].v1, face[i].v2, face[i].v3])
			
			
		#print('---Dynamic Cloth Stuff---')
		#Dynamic Clothing Meshes go here. And are not supported at the moment...
		nCloth = struct.unpack('<I', file.read(4))[0]
		for i in range(nCloth):
			#This is going to look reallll ugly for now.
			nCloth1 = struct.unpack('<I', file.read(4))[0]
			nCloth2 = struct.unpack('<I', file.read(4))[0]
			nCVerts = struct.unpack('<I', file.read(4))[0]
			nCloth4 = struct.unpack('<I', file.read(4))[0]
			nCloth5 = struct.unpack('<I', file.read(4))[0]
			nCTris  = struct.unpack('<I', file.read(4))[0]
			nCloth7 = struct.unpack('<I', file.read(4))[0]
			nCloth8 = struct.unpack('<I', file.read(4))[0]
			nCloth9 = struct.unpack('<I', file.read(4))[0]
			
			if animated:
				for i in range(nCVerts):
					struct.unpack('<I', file.read(4))[0]
				for i in range(nCVerts):
					struct.unpack('<4I', file.read(4*4))[0]
				
			nCloth12 = struct.unpack('<I', file.read(4))[0]
			nCloth13 = struct.unpack('<I', file.read(4))[0]
			nCloth14 = struct.unpack('<I', file.read(4))[0]
			nCloth15 = struct.unpack('<I', file.read(4))[0]
			nCloth16 = struct.unpack('<I', file.read(4))[0]
			
			struct.unpack('<6f', file.read(4*6))[0]
			
			#Couple booleans
			nCloth17 = struct.unpack('<?', file.read(1))[0]
			nCloth18 = struct.unpack('<?', file.read(1))[0]
			
			vCloth = [] #list
			for i in range(nCVerts):
				#Mesh Vertices
				vCloth.append([struct.unpack('<f', file.read(4))[0], 
									struct.unpack('<f', file.read(4))[0], 
									struct.unpack('<f', file.read(4))[0]])
			print('---Debug Per Vertex Float sets---')
			vDebug = []	
			for i in range(nCVerts):
				vDebug.append([struct.unpack('<f', file.read(4))[0], 
									struct.unpack('<f', file.read(4))[0], 
									struct.unpack('<f', file.read(4))[0], 
									struct.unpack('<f', file.read(4))[0]])
				#print('Debug 1:', vDebug[i])				
			vDebug = []
			for i in range(nCVerts):
				vDebug.append([struct.unpack('<f', file.read(4))[0], 
									struct.unpack('<f', file.read(4))[0], 
									struct.unpack('<f', file.read(4))[0], 
									struct.unpack('<f', file.read(4))[0]])
				#print('Debug 2:', vDebug[i])				
			for i in range(nCVerts):
				vDebug = struct.unpack('<f', file.read(4))[0]
				#print('Debug 3:', vDebug)				
			fCloth = []
			for i in range(nCTris):
				#Mesh Faces
				fCloth.append([struct.unpack('<h', file.read(2))[0], 
									struct.unpack('<h', file.read(2))[0], 
									struct.unpack('<h', file.read(2))[0]])									
			for i in range(nCloth7):
				file.read(2*2)
			for i in range(nCloth7):
				struct.unpack('<4f', file.read(4*4))[0]
			
			if animated:
				for i in range(nCloth8):
					file.read(1)
			else:
				for i in range(nCVerts):
					file.read(1)
					
			for i in range(nCloth12):
				file.read(4*8)
			for i in range(nCloth14):
				file.read(4*14)
				
			if animated:	
				for i in range(nCloth8 - nCloth5):
					file.read(4*2)
			else:
				for i in range(nCVerts - nCloth5):
					file.read(4*2)
		#print('--End of Dynamic Cloth Stuff--')
		
		#Build the Mesh from lists
		self.mesh = bpy.data.meshes.new(self.Name)
		self.mesh.from_pydata(vert_indice, [], face_indice)
		self.mesh.vertices.foreach_set('normal', vert_2_table)
		uv_layer = self.mesh.uv_layers.new(name=self.Name)

		#Build UV Map
		#This needs coordinate conversion done on it.
		for loop in self.mesh.loops:
			uv_layer.data[loop.index].uv = (self.vert_1[loop.vertex_index].v[4],-self.vert_1[loop.vertex_index].v[5]) #Flip uv on y axis. Maps correctly but now it's not normalized?

def BuildSkeleton(file):

		DummyName = {}
		DummyID = {}
		Name = {}
		Parent = {}
		local_matrices = {}
		
		#Create the armature
		armdata = bpy.data.armatures.new('Skeleton')
		armature = bpy.data.objects.new('Armature', armdata)
		bpy.context.collection.objects.link(armature)
		
		#Make sure only armature is selected and in edit mode
		for i in bpy.context.collection.objects: i.select_set(False) #deselect all objects
		armature.select_set(True)
		bpy.context.view_layer.objects.active = armature
		bpy.ops.object.mode_set(mode='EDIT')

		dummies = struct.unpack('B', file.read(1))[0]
		for i in range(dummies):
			DummyName[i] = struct.unpack('<I', file.read(4))[0]
			DummyID[i] = struct.unpack('<i', file.read(4))[0]
			
		hierarchy = struct.unpack('<I', file.read(4))[0]
		for i in range(hierarchy):
			Name[i] = struct.unpack('<I', file.read(4))[0]
			Parent[i] = struct.unpack('<i', file.read(4))[0]
		
		
		Bones = struct.unpack('<I', file.read(4))[0]
		for i in range(Bones):
			bone = armature.data.edit_bones.new(str(Name[i]))
			bone.length = 0.05
			
			#parent bone
			if Parent[i] != -1:
				bone.parent = armature.data.edit_bones[Parent[i]]
			
			#Pull data from file
			Matrix = [	struct.unpack('<f', file.read(4))[0],  #Matrix[0] X?
						struct.unpack('<f', file.read(4))[0],  #Matrix[1] Y?
						struct.unpack('<f', file.read(4))[0],  #Matrix[2] Z?
						struct.unpack('<f', file.read(4))[0],  #Matrix[3] scale? Maybe W?
						struct.unpack('<f', file.read(4))[0],  #Matrix[4] X?
						struct.unpack('<f', file.read(4))[0],  #Matrix[5] Y?
						struct.unpack('<f', file.read(4))[0],  #Matrix[6] Z?
						struct.unpack('<f', file.read(4))[0],  #Matrix[7] scale? Maybe W?
						struct.unpack('<f', file.read(4))[0],  #Matrix[8]
						struct.unpack('<f', file.read(4))[0],  #Matrix[9]
						struct.unpack('<f', file.read(4))[0]]  #Matrix[10]
			
			#helpers
			pos = mathutils.Vector((Matrix[4],Matrix[5],Matrix[6]))
			rot = mathutils.Quaternion((Matrix[3],Matrix[0],Matrix[1],Matrix[2]))
			scale = mathutils.Vector((Matrix[7],Matrix[8],Matrix[9]))
			
			#Keep the matrices, but don't apply them. We need to change the axis first.
			local_matrices[bone.name] = calculate_armature_matrices(pos,rot,scale)

		#assumes only one root bone
		if Bones > 0:
			root_bone = armature.data.edit_bones[0]
			global_matrix = mathutils.Matrix() #axis_conversion(from_forward='Y', from_up='Z', to_forward='-X', to_up='Z').to_4x4()
			root_bone.matrix = local_matrices[root_bone.name] @ global_matrix
			apply_armature_matrices(root_bone,local_matrices,global_matrix)
			bpy.ops.object.mode_set(mode='OBJECT')
			bpy.context.view_layer.update()
		return armature
		
##################
## Read in File ##
##################

def read(file, context, op):
	
	global_matrix = axis_conversion(from_forward='-Z',from_up='Y').to_4x4()
	#Create the Scene Root
	scn_root = bpy.context.collection
	scn = bpy.data.collections.new('Fable3_MESH')
	scn_root.children.link(scn)
	
	for o in scn_root.objects:
		o.select_set(state=False)
		o.matrix_world = global_matrix

	##HEADER##
	FNVHash = struct.unpack('<I', file.read(4))[0]
	file.read(8) 	#padding
	
	armature = BuildSkeleton(file) #Read in the skeleton
	
	origin = float10(file) #Same as in header
	
	#Counts of different mesh types
	nMaterials 			= struct.unpack('<I', file.read(4))[0]
	nStatic 			= struct.unpack('<I', file.read(4))[0]
	nSkeletal		 	= struct.unpack('<I', file.read(4))[0]
	nPlanes 			= struct.unpack('<I', file.read(4))[0]
	nUnknownMeshType 	= struct.unpack('<I', file.read(4))[0] #Haven't seen this used yet, but I assume it's some mesh type
	nUnknownMeshType 	= struct.unpack('<I', file.read(4))[0] #Mostly buildings use this. Probably collision
	
	if nSkeletal > 0:
		Animated = True
	else:
		Animated = False
	
	file.read(1)	#pad
	node(file) #I'm not sure what these are for. They don't look like dummies or points.
	
	##MATERIAL##
	Material = {}
	for i in range(nMaterials):
		Material[i] = material(file)
	
	##MESH##
	for i in range(nStatic+nSkeletal):
		submesh = mesh(file, Animated)
		submesh.mesh.update()
		submesh.mesh.validate()

		submesh.mesh.materials.append(Material[submesh.iMaterial].material)
		nobj = bpy.data.objects.new(submesh.Name, submesh.mesh)
		
		if Animated:
			nobj.modifiers.new(type='ARMATURE', name="Armature").object = armature
			for i in submesh.BoneID:
				name = armature.data.bones[submesh.BoneID[i]].name
				nobj.vertex_groups.new(name=name)

			for v in submesh.mesh.vertices:
				for i in range(len(submesh.vert_1[v.index].bones)):
					vbone = submesh.vert_1[v.index].bones[i]
					vweight = submesh.vert_1[v.index].weights[i]
					name = armature.data.bones[submesh.BoneID[vbone]].name
					if vweight > 0:
						nobj.vertex_groups[name].add([v.index], vweight/255, "REPLACE")
				
		scn.objects.link(nobj)
		bpy.context.view_layer.update()
		

##################
## Import Stuff ##
##################

class MDLImporter(bpy.types.Operator):
	'''Import from MDL file format (.mdl)'''
	bl_idname = "import_mesh.mdl"
	bl_label = "Import MDL"

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.


	def execute(self, context):
		with open(self.properties.filepath, 'rb') as file:
			print('Importing file', self.properties.filepath)
			read(file, context, self)
		return {'FINISHED'}

	def invoke(self, context, event):
		wm = context.window_manager
		wm.add_fileselect(self)
		return {'RUNNING_MODAL'}
		
###########
## UTILS ##
###########

def node(file):
	nNodes = struct.unpack('<I', file.read(4))[0]
	Strings = {}
	for i in range(nNodes):
		Strings[i] = read_string(file)
	return Strings

def HalfToFloat(h):
    s = int((h >> 15) & 0x00000001)    # sign
    e = int((h >> 10) & 0x0000001f)    # exponent
    f = int(h & 0x000003ff)            # fraction

    if e == 0:
       if f == 0:
          return int(s << 31)
       else:
          while not (f & 0x00000400):
             f <<= 1
             e -= 1
          e += 1
          f &= ~0x00000400
    elif e == 31:
       if f == 0:
          return int((s << 31) | 0x7f800000)
       else:
          return int((s << 31) | 0x7f800000 | (f << 13))

    e = e + (127 -15)
    f = f << 13

    return int((s << 31) | (e << 23) | f)
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
	
#This is a HACK..
class vect16_1:
	fmt = '6h'
	
	def __init__(self, file):
		_s = file.read(struct.calcsize(self.fmt))
		self.v16 = struct.unpack(self.fmt, _s)
		
		self.vu = [HalfToFloat(self.v16[0]), 
					HalfToFloat(self.v16[1]),
					HalfToFloat(self.v16[2]),
					HalfToFloat(self.v16[3]),
					HalfToFloat(self.v16[4]),
					HalfToFloat(self.v16[5])]
		self.vp = struct.pack('6I', self.vu[0], 
									self.vu[1], 
									self.vu[2], 
									self.vu[3], 
									self.vu[4], 
									self.vu[5])
									
		self.v = struct.unpack('6f', self.vp)	
class avect16_1:
	fmt = '4h8B2h'
	
	def __init__(self, file):
		_s = file.read(struct.calcsize(self.fmt))
		v16 = struct.unpack(self.fmt, _s)
		#print(v16)
		#v16[0] X
		#v16[1] Y
		#v16[2] Z
		#v16[3] ??
		#v16[4] Bone?
		#v16[5] Bone?
		#v16[6] Bone?
		#v16[7] Bone?
		#v16[8] Weight?
		#v16[9] Weight?
		#v16[10] Weight?
		#v16[11] Weight?
		#v16[12] U
		#v16[13] V
		
		#Convert 16bit floats
		vu = [HalfToFloat(v16[0]),HalfToFloat(v16[1]),HalfToFloat(v16[2]),HalfToFloat(v16[3]),HalfToFloat(v16[12]),HalfToFloat(v16[13])]
		vp = struct.pack('6I', vu[0],vu[1],vu[2],vu[3],vu[4],vu[5])
									
		self.v = struct.unpack('6f', vp)
		self.bones = [v16[4], v16[5], v16[6], v16[7]]
		self.weights = [v16[8],v16[9],v16[10],v16[11]]
class vect16_2:
	fmt = '8h'
	
	def __init__(self, file):
		_s = file.read(struct.calcsize(self.fmt))
		self.v16 = struct.unpack(self.fmt, _s)
		#print(self.v16)
		
		self.vu = [HalfToFloat(self.v16[0]), 
					HalfToFloat(self.v16[1]),
					HalfToFloat(self.v16[2]),
					HalfToFloat(self.v16[3]),
					HalfToFloat(self.v16[4]),
					HalfToFloat(self.v16[5]),
					HalfToFloat(self.v16[6]),
					HalfToFloat(self.v16[7])]
		self.vp = struct.pack('4I', self.vu[0], 
									self.vu[1], 
									self.vu[2], 
									self.vu[3])
		self.v = struct.unpack('4f', self.vp)
	
def calculate_armature_matrices(translation,quaternion,scale):
	return mathutils.Matrix.Translation(translation) @ quaternion.to_matrix().to_4x4() @ mathutils.Matrix.Scale(scale[0],4,(1,0,0)) @ mathutils.Matrix.Scale(scale[1],4,(0,1,0)) @ mathutils.Matrix.Scale(scale[2],4,(0,0,1))
   
def apply_armature_matrices(parent_bone,local_matrices,global_conversion=None):
	# process children
	for child in parent_bone.children:
		child.matrix = parent_bone.matrix @ global_conversion.inverted() @ local_matrices[child.name] @ global_conversion
		apply_armature_matrices(child,local_matrices,global_conversion)

	#for child in parent_bone.children:
		#apply_armature_matrices(child,local_matrices,global_conversion)