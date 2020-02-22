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
import mathutils
from bpy_extras.io_utils import unpack_list, unpack_face_list
from bpy_extras.image_utils import load_image

##################
## Struct setup ##
##################

class material:
	def __init__(self, file):
		print(file.read(4)) #Don't know what this is doing
		self.material = bpy.data.materials.new(name=read_string(file)) #Material Name
		print(file.read(4)) #Don't know what this is doing

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
		print('Material Type: '+str(Type))
		
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
		struct.unpack('<I', file.read(4))[0]
		file.read(1)	#pad
		
		self.nTris = struct.unpack('<I', file.read(4))[0] # passed outside class
		
		pStart = struct.unpack('<I', file.read(4))[0] #offset pointer
		
		Origin = struct.unpack('<6f', file.read(24))[0]
		if animated:
			struct.unpack('<I', file.read(4))[0]
					
class triangle:
	def __init__(self, file):
		self.v1 = struct.unpack('<h', file.read(2))[0]
		self.v2 = struct.unpack('<h', file.read(2))[0]
		self.v3 = struct.unpack('<h', file.read(2))[0]
		
class BuildSkeleton:

		fName = []
		fBone = []
		Name = []
		Parent = []
		Matrix = []
		Transform = []

		def __init__(self, file):
			self.nFlags = struct.unpack( 'B', file.read(1))[0]
			for i in range(self.nFlags):
				self.fName.append([struct.unpack('<I', file.read(4))[0]])
				self.fBone.append([struct.unpack('<i', file.read(4))[0]])
				print('Bone:', self.fName[i], 'BoneID', self.fBone[i])
				
			self.nBones1 = struct.unpack('<I', file.read(4))[0]
			for i in range(self.nBones1):
				self.Name.append([struct.unpack('<I', file.read(4))[0]])
				self.Parent.extend([struct.unpack('<i', file.read(4))[0]])
				print('Bone:', i, self.Name[i], 'Parent', self.Parent[i])
	
			self.nBones2 = struct.unpack('<I', file.read(4))[0]
			self.TransformTest = []
			for i in range(self.nBones2):
				self.Matrix.append([struct.unpack('<f', file.read(4))[0],
									struct.unpack('<f', file.read(4))[0],
									struct.unpack('<f', file.read(4))[0],
									struct.unpack('<f', file.read(4))[0],
									struct.unpack('<f', file.read(4))[0], #X
									struct.unpack('<f', file.read(4))[0], #Y
									struct.unpack('<f', file.read(4))[0], #Z
									struct.unpack('<f', file.read(4))[0],
									struct.unpack('<f', file.read(4))[0],
									struct.unpack('<f', file.read(4))[0],
									struct.unpack('<f', file.read(4))[0]])
									
				self.bTransform = mathutils.Quaternion((self.Matrix[i][3],self.Matrix[i][0],self.Matrix[i][1],self.Matrix[i][2]))
				self.Transform.extend([self.bTransform])

			#Debug#
			for i in range(self.nBones2): 
				print('Bone',i,': Unknown[',self.Matrix[i][0],self.Matrix[i][1],self.Matrix[i][2],self.Matrix[i][3],'] XYZ[',
						self.Matrix[i][4],self.Matrix[i][5],self.Matrix[i][6],'] Unknown[',
						self.Matrix[i][7],self.Matrix[i][8],self.Matrix[i][9],self.Matrix[i][10],']')
						
						
			self.armdata = bpy.data.armatures.new('SkelNewTest')
			self.armature = bpy.data.objects.new('SkelTest', self.armdata)
			bpy.context.collection.objects.link(self.armature)
			
			for i in bpy.context.collection.objects: i.select_set(False) #deselect all objects
			self.armature.select_set(True)
			bpy.context.view_layer.objects.active = self.armature
			
			for i in range(self.nBones2):
				bpy.ops.object.mode_set(mode='EDIT')
				self.newbone = self.armature.data.edit_bones.new(str(self.Name[i]))
				self.parentbone = None
				
				self.pos_x = self.Matrix[i][4]
				self.pos_y = self.Matrix[i][5]
				self.pos_z = self.Matrix[i][6]
				
				
				if self.Parent[i] != -1:
					self.parentbone = self.armature.data.edit_bones[self.Parent[i]]
					self.newbone.parent = self.parentbone
					
					self.rotmatrix = self.Transform[i].to_matrix().to_4x4().to_3x3()
					self.newbone.transform(self.Transform[i].to_matrix().to_4x4(),True,True)
					
					self.newbone.head.x = self.parentbone.head.x + self.pos_x
					self.newbone.head.y = self.parentbone.head.y + self.pos_y
					self.newbone.head.z = self.parentbone.head.z + self.pos_z

					self.newbone.tail.x = self.parentbone.head.x + (self.pos_x * self.rotmatrix[1][0])
					self.newbone.tail.y = self.parentbone.head.y + (self.pos_y * self.rotmatrix[1][1])
					self.newbone.tail.z = self.parentbone.head.z + (self.pos_z * self.rotmatrix[1][2])
					
					
				else: #No parent
				
					self.rotmatrix = self.Transform[i].to_matrix().to_3x3()
					
					self.newbone.head.x = self.pos_x
					self.newbone.head.y = self.pos_y
					self.newbone.head.z = self.pos_z

					self.newbone.tail.x = self.pos_x * self.rotmatrix[1][0]
					self.newbone.tail.y = self.pos_y * self.rotmatrix[1][1]
					self.newbone.tail.z = self.pos_z * self.rotmatrix[1][2]

			bpy.context.view_layer.update()

class mesh:
	def __init__(self, file, animated):
	
		if animated:
			self.Name = "AnimatedObject"
		else:
			self.Name = read_string(file)
			
		file.read(1)	#pad

		iMesh 		= struct.unpack('<I', file.read(4))[0]
		self.iMaterial 	= struct.unpack('<I', file.read(4))[0]
		nTris 		= struct.unpack('<I', file.read(4))[0]
		
		struct.unpack('<I', file.read(4))[0] #unknown
		
		nVerts 	= struct.unpack('<I', file.read(4))[0]
		
		if not animated:
			Origin2 = matrix(file)
		
		nMeshSplit = struct.unpack('<I', file.read(4))[0]
		MeshSplit = []
		nTotalTris = 0
		for i in range(nMeshSplit):
			if animated:
				MeshSplit.extend([mesh_split(file, animated)])
			else:
				MeshSplit.extend([mesh_split(file, animated)])
			nTotalTris = nTotalTris + MeshSplit[i].nTris
		
		
		#An Array of bones
		if animated:
			BoneID = []
			nCount = struct.unpack('<I', file.read(4))[0]
			for j in range(nCount):
				nCount2 = struct.unpack('<I', file.read(4))[0]
				for i in range(nCount2):
					BoneID = [struct.unpack('<I', file.read(4))[0]]

		
		#XYZ, Unk, UV
		vert_1 = []
		vert_indice = []
		for i in range(nVerts):
			if animated:
				vert_1.extend([avect16_1(file)]) #An Array
			else:
				vert_1.extend([vect16_1(file)])
			
			vert_indice.append([vert_1[i].v[0], vert_1[i].v[1], vert_1[i].v[2]]) #An Index of xyz

			
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
			
			
		print('---Dynamic Cloth Stuff---')
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
				print('Debug 1:', vDebug[i])				
			vDebug = []
			for i in range(nCVerts):
				vDebug.append([struct.unpack('<f', file.read(4))[0], 
									struct.unpack('<f', file.read(4))[0], 
									struct.unpack('<f', file.read(4))[0], 
									struct.unpack('<f', file.read(4))[0]])
				print('Debug 2:', vDebug[i])				
			for i in range(nCVerts):
				vDebug = struct.unpack('<f', file.read(4))[0]
				print('Debug 3:', vDebug)				
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
		print('--End of Dynamic Cloth Stuff--')
		
		#Build the Mesh from lists
		if animated:
			self.mesh = bpy.data.meshes.new("AnimatedMesh")
			self.mesh.from_pydata(vert_indice, [], face_indice)
			self.mesh.vertices.foreach_set('normal', vert_2_table)
			uv_layer = self.mesh.uv_layers.new(name="AnimatedMesh")
		else:
			self.mesh = bpy.data.meshes.new(self.Name)
			self.mesh.from_pydata(vert_indice, [], face_indice)
			self.mesh.vertices.foreach_set('normal', vert_2_table)
			uv_layer = self.mesh.uv_layers.new(name=self.Name)

		for loop in self.mesh.loops:
			uv_layer.data[loop.index].uv = (vert_1[loop.vertex_index].v[4],-vert_1[loop.vertex_index].v[5]) #Flip uv on y axis. Maps correctly but now it's not normalized?

		
##################
## Read in File ##
##################

def read(file, context, op):

	#Create the Scene Root
	scn = bpy.context.collection
	
	for o in scn.objects:
		o.select_set(state=False)

	##HEADER##
	FNVHash = struct.unpack('<I', file.read(4))[0]
	print('\nFNVHash:', FNVHash)
	file.read(8) 	#padding
	
	Skeleton = BuildSkeleton(file)
	
	Origin = matrix(file) #Same as in header
	
	nMaterials = struct.unpack('<I', file.read(4))[0]
	nMeshes = struct.unpack('<I', file.read(4))[0]
	nAnimatedMeshes = struct.unpack('<I', file.read(4))[0]
	
	if nAnimatedMeshes > 0:
		Animated = True
	else:
		Animated = False
	
	nPlanes = struct.unpack('<I', file.read(4))[0]
	unk1 = struct.unpack('<I', file.read(4))[0] #Haven't seen this used yet
	nWTF = struct.unpack('<I', file.read(4))[0] #Mostly buildings use this. Probably collision
		
	file.read(1)	#pad
	
	#I'm not sure what these are for. They don't look like dummies or points.
	node(file)
	
	##MATERIAL##
	print('--Texture Stuff--')
	Material = []
	for i in range(nMaterials):
		Material.extend([material(file)])

	##MESH##
	print('--Mesh Stuff--')
	Mesh = []
	for i in range(nMeshes+nAnimatedMeshes):
		#print('Mesh:', i)
		Mesh.extend([mesh(file, Animated)])
		Mesh[i].mesh.update()
		Mesh[i].mesh.validate()
		
		print('Material:', Mesh[i].iMaterial)
		Mesh[i].mesh.materials.append(Material[Mesh[i].iMaterial].material)
		
		nobj = bpy.data.objects.new(Mesh[i].Name, Mesh[i].mesh)
		scn.objects.link(nobj)

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
	Strings = []
	for i in range(nNodes):
		Strings.extend([read_string(file)])
		print(Strings[i])

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

def matrix(file):
	fmt = 'f' * 10
	_s = file.read(struct.calcsize(fmt))
	matrix = struct.unpack(fmt, _s)	
def vect(file):
	fmt = '7f'
	_s = file.read(struct.calcsize(fmt))
	v = struct.unpack(fmt, _s)
	
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
	#xyz
	#?
	#Bones
	#Weights
	#uv
	
	def __init__(self, file):
		_s = file.read(struct.calcsize(self.fmt))
		self.v16 = struct.unpack(self.fmt, _s)
		
		#Convert 16bit floats
		self.vu = [HalfToFloat(self.v16[0]),
					HalfToFloat(self.v16[1]),
					HalfToFloat(self.v16[2]),
					HalfToFloat(self.v16[3]),
					HalfToFloat(self.v16[12]),
					HalfToFloat(self.v16[13])]
		
		self.vp = struct.pack('6I', self.vu[0], 
									self.vu[1], 
									self.vu[2], 
									self.vu[3], 
									self.vu[4], 
									self.vu[5])
									
		self.v = struct.unpack('6f', self.vp)
		self.bones = [self.v16[4], self.v16[5], self.v16[6], self.v16[7]]
		self.weights = [self.v16[8], self.v16[9], self.v16[10], self.v16[11]]
class vect16_2:
	fmt = '8h'
	
	def __init__(self, file):
		_s = file.read(struct.calcsize(self.fmt))
		self.v16 = struct.unpack(self.fmt, _s)
		
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

#not used anywhere yet...		
class matrix_complex:
	fmt = '6hf6h4f'
	
	def __init__(self, file):
		_s = file.read(struct.calcsize(self.fmt))
		self.temp = struct.unpack(self.fmt, _s)
		
		self.v16Temp = [HalfToFloat(self.temp[0]), 
					HalfToFloat(self.temp[1]),
					HalfToFloat(self.temp[2]),
					HalfToFloat(self.temp[3]),
					HalfToFloat(self.temp[4]),
					HalfToFloat(self.temp[5]),
					HalfToFloat(self.temp[7]),
					HalfToFloat(self.temp[8]),
					HalfToFloat(self.temp[9]),
					HalfToFloat(self.temp[10]),
					HalfToFloat(self.temp[11]),
					HalfToFloat(self.temp[12])]
					
		self.v16Temp2 = struct.pack('12I',self.v16Temp[0], 
									self.v16Temp[1], 
									self.v16Temp[2], 
									self.v16Temp[3],
									self.v16Temp[4], 
									self.v16Temp[5], 
									self.v16Temp[6], 
									self.v16Temp[7],
									self.v16Temp[8], 
									self.v16Temp[9], 
									self.v16Temp[10], 
									self.v16Temp[11])
									
		self.v16 = struct.unpack('12f', self.v16Temp2)
		self.f1 = self.temp[6]
		self.f2 = self.temp[13]
		self.v = [self.temp[14], self.temp[15], self.temp[16]]