# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURm_posE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

## [LZO:1X]: Lempel-Ziv-Oberhumer lossless data compression algorithm
## http://www.oberhumer.com/opensource/lzo/
## this python implementation based on the java implementation from:
## http://www.oberhumer.com/opensource/lzo/download/LZO-v1/java-lzo-1.00.tar.gz

import os
import bpy

class Lzo_Codec:
	
	print('Begin Decompression')
	LZO_E_OK                  =  0
	LZO_E_ERROR               = -1
	LZO_E_INPUT_OVERRUN       = -4
	LZO_E_LOOKBEHIND_OVERRUN  = -6
	LZO_E_INPUT_NOT_CONSUMED  = -8

	def Lzo1x_Decompress(src, src_off, src_len, dst, dst_off):
		"""
		src = bytes
		dst = bytearray

		returns: error, result_index
		"""
		ip = src_off
		op = dst_off
		t = 0
		m_pos = 0
		error = Lzo_Codec.LZO_E_OK
		result_index = op
		
		print('Begin Decompression')
		
		t = U(src[ip])
		ip += 1
		print(t)
		if t > 17:
			t -= 17
			while True: ## do while t > 0
				dst[op] = src[ip]
				op += 1
				ip += 1
				t -= 1
				print('t:'+str(t)+', op:'+str(op)+', ip'+str(ip))
				if t <= 0:
					break ## do while t > 0

			#t = U(src[ip++]);
			t = U(src[ip])
			ip += 1
			if t < 16: return Lzo_Codec.LZO_E_ERROR, result_index

		## loop:
		loop = False
		#ip -= 1 ## first loop for (;;t = src[ip++])
		while not loop: #for (;;t = src[ip++])
			t = U(src[ip]) #for (;;t = src[ip++])
			
			if t < 16:
				if t == 0:
					while src[ip] == 0:
						t += 255
						ip += 1
					t += 15 + U(src[ip])
					ip += 1
				t += 3
				while True: ## do while t > 0
					dst[op] = src[ip]
					print(str(src[ip])+'-->'+str(dst[op]))
					op += 1
					ip += 1
					t -= 1
					if t <= 0:
						break ## do while t > 0
				t = U(src[ip])
				ip += 1
				if t < 16:
					m_pos = op - 0x801 - (t >> 2) - (U(src[ip]) << 2)
					ip += 1
					if m_pos < dst_off:
						error = Lzo_Codec.LZO_E_LOOKBEHIND_OVERRUN
						loop = True
						break ## loop
					t = 3
					while True: ## do while t > 0
						dst[op] = dst[m_pos]
						op += 1
						m_pos += 1
						t -= 1
						if t <= 0:
							break ## do while t > 0
					t = src[ip-2] & 3
					if t == 0:
						continue ## 1 for (;;t = src[ip++])
					while True: ## do while t > 0
						dst[op] = src[ip]
						op += 1
						ip += 1
						t -= 1
						if t <= 0:
							break ## do while t > 0
					t = U(src[ip])
					ip += 1

			#ip -= 1 ## second loop for (;;t = src[ip++])
			while not loop: #for (;;t = src[ip++])
				t = U(src[ip]) ## 2 for (;;t = src[ip++])
				
				if t >= 64:
					m_pos = op - 1 - ((t >> 2) & 7) - (U(src[ip]) << 3)
					ip += 1
					t = (t >> 5) - 1
				elif t >= 32:
					t &= 31
					if t == 0:
						while src[ip] == 0:
							t += 255
							ip += 1
						t += 31 + U(src[ip])
						ip += 1
					m_pos = op - 1 - (U(src[ip]) >> 2)
					ip += 1
					m_pos -= (U(src[ip]) << 6)
					ip += 1
				elif t >= 16:
					m_pos = op - ((t & 8) << 11)
					t &= 7
					if t == 0:
						while src[ip] == 0:
							t += 255
							ip += 1
						t += 7 + U(src[ip])
						ip += 1
					m_pos -= (U(src[ip]) >> 2)
					ip += 1
					m_pos -= (U(src[ip]) << 6)
					ip += 1
					if m_pos == op:
						loop = True
						break ## loop
					m_pos -= 0x4000
				else:
					m_pos = op - 1 - (t >> 2) - (src[ip] << 2)
					ip += 1
					t = 0
				if m_pos < dst_off:
					error = Lzo_Codec.LZO_E_LOOKBEHIND_OVERRUN
					loop = True
					break ## loop
				t += 2
				while True: ## do while t > 0
					dst[op] = dst[m_pos]
					op += 1
					m_pos += 1
					t -= 1
					if t <= 0:
						break ## do while t > 0
				t = src[ip - 2] & 3
				if t == 0:
					break
				while True: ## do while t > 0
					dst[op] = src[ip]
					op += 1
					ip += 1
					t -= 1
					if t <= 0:
						break ## do while t > 0
		
				#increment for loop
				ip += 1 ## 2 for (;;t = src[ip++])
			
			#increment for loop
			ip += 1 ## 1 for (;;t = src[ip++])
		

		ip -= src_off
		op -= dst_off
		result_index = op
		if error < Lzo_Codec.LZO_E_OK:
			return error, result_index
		if ip < src_len:
			error = Lzo_Codec.LZO_E_INPUT_NOT_CONSUMED
			return error, result_index
		if ip > src_len:
			error = Lzo_Codec.LZO_E_INPUT_OVERRUN
			return error, result_index
		if t != 1:
			error = Lzo_Codec.LZO_E_ERROR
			return error, result_index
		return error, result_index
		
def U(b):
	return b & 0xff