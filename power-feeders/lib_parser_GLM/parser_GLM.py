# script to create a tree based on the GLM file

import os
import sys
import copy
import pdb
import random
import numpy as np



module_template = {'name': ''}
object_template = {'type': '', 'class': '', 'ID_child': [], 'ID_parent': '', 'list_attributes': []}




recorder_empty = '''
object recorder {
	file file_name**;
	//flags DELTAMODE;
	interval interval**;
	property properties**;
};
'''

switch = '''
object switch{
	status CLOSED;
	phases ABCN;
	name name**;
	to to**;
	from from**;
};
'''




# Determine if the string opens or closes the definition of an object/module
def beginning_object(line):
	if type(line) != list:
		l = line.split('//')[0].split()
	else:
		l = line

	if len(l) > 0:
		if l[-1][-1] == '{':
			return True
	return False

def end_object(l):
	if len(l) > 0:
		if l[0][0] == '}':
			return True
	return False


# Read the content between the beginning and end of an object/module
def read_obj(line_raw, glm_file):
	# we add the first line to the object_raw
	line = line_raw.split('//')[0]
	object_raw = [line]
	l = line.split()
	if beginning_object(l):
		obj_count = 1

		while obj_count > 0:
			line = next(glm_file)
			object_raw.append( line )
			l = line.split()
			if beginning_object(l):	
				obj_count += 1
			elif end_object(l):
				obj_count -= 1
	return object_raw






class parser_GLM:
	def __init__(self):
		self.number_objects = 0
		self.list_modules = []
		self.list_objects = []
		self.list_directives = []
		#self.list_classes = []

		#create_list_elements(self, glm_file)
	def create_list_elements(self, glm_file):
		# introduce some libraries, modules, and class definitions
		with open(glm_file) as original_glm:
			for raw_line in original_glm:
				line = raw_line.strip()

				# identify the type of element
				# directive
				if len(line) == 0:
					pass

		
				elif line[0] == '#':
					self.list_directives.append( line )
				# modules
				elif line.startswith('module'): 
					module_raw = read_obj(raw_line, original_glm)
					self.add_module(module_raw)

				# object
				elif beginning_object(line):#line.startswith('object'): 
					obj_raw = read_obj(raw_line, original_glm)
					self.add_object(obj_raw)
				

		return

	
	def add_module(self, text_raw):
		module = copy.deepcopy(module_template)
		i = 0
		l = text_raw[i].split()
		mult_attributes = beginning_object(l)

		# multiple attributes in the module
		if mult_attributes:
			name = l[1].replace('{', '')

			obj_count = 1
			#k = 0
			while obj_count > 0: # or k==0:
				i += 1
				line = text_raw[i]
				l = line.split()
			
				if len(l) == 0:
					pass
				elif l[0].startswith('//'):
					pass
				elif beginning_object(l):	
					obj_count += 1
				elif end_object(l):
					obj_count -= 1
				else:
					attribute = l[0]
					value = line.replace(attribute, '').replace(';', '').strip()
					module[attribute] = value

		# module with ah single attribute
		else:
			name = l[1].replace(';', '')
		module['name'] = name
		self.list_modules.append( module )
		return 
	

	def add_object(self, raw_text, i=0, id_parent=''):
		#global list_objects
		#global number_objects

		if type(raw_text) == str:
			raw_text = raw_text.strip().split('\n')

		# assign id to the object
		object_id = self.number_objects
		object_ = copy.deepcopy(object_template)

		self.list_objects.append( None )
		self.number_objects += 1

		l = raw_text[i].split('{')[0].split()

		type_ = l[0]
		class_ = ' '.join(l[1:])


		obj_count = 1
		while obj_count > 0:
			i += 1
			line = raw_text[i]
			l = line.split()
		
			if len(l) == 0:
				pass

			elif beginning_object(l):	
				sub_object_id, i = self.add_object(raw_text, i, object_id)
				object_['ID_child'].append( sub_object_id )

			elif end_object(l):
				obj_count -= 1

			else:
				attribute = l[0]
				value = line.split(';')[0].replace(attribute, '', 1).strip()
				if attribute in object_.keys():
					object_[attribute].append(value)
				else:
					object_[attribute] = [value]
					object_['list_attributes'].append( attribute )
				

		object_['type'] = [type_]
		object_['class'] = [class_]
		object_['ID_parent'] = id_parent


		self.list_objects[ object_id ] = object_
		return object_id, i


	
	def save_directives(self, new_glm):
		directives = '\n'.join(self.list_directives)
		new_glm.write( directives + '\n' )
		return


	def save_modules(self, new_glm):
		for i in range(len(self.list_modules)):
			module = self.list_modules[i]
			raw_module = '\nmodule ' + module['name']
			if len(module) == 1:
				raw_module += ';\n'
			else:
				raw_module += '{\n'
				for attr in module.keys():
					if attr != 'name':
						raw_module += '\t' + attr + ' ' + module[attr] + ';\n' 
				raw_module += '};\n'
			#print(raw_module)
			new_glm.write( raw_module )
		return 
	

	def save_objects(self, new_glm):
		n = len(self.list_objects)
		set_objects = set( range( n ) )
	
		for object_id in range (n ):
			if object_id not in set_objects:
				pass
			else:
				raw_object, set_objects = self.read_object( object_id, set_objects )
				new_glm.write( raw_object )
		return 



	def read_object(self, id, set_objects):

		if len(set_objects) <= 0 or id not in set_objects:
			return '', set_objects

		object_i = self.list_objects[id]
		set_objects -= {id}	

		if object_i == '':
			return '', set_objects
		#pdb.set_trace()
		raw_object = '\n' +  ' '.join(object_i['type']) + ' ' + ' '.join(object_i['class'])
		raw_object += '{\n'
		#for attr in object_i.keys():
		for attr in object_i['list_attributes']:
			if attr not in ['type', 'class', 'ID_parent', 'ID_child', 'list_attributes']:
				for val in object_i[attr]:
					try:
						raw_object += '\t' + attr + ' ' + val + ';\n' 
					except:
						pdb.set_trace()

		if object_i['ID_child'] != []:
			for id_child in object_i['ID_child']:
				try:
					sub_object, set_objects = self.read_object( id_child, set_objects )
					raw_object += sub_object.replace('\n', '\n\t')
				except:
					#pdb.set_trace()
					pass


		raw_object += '\n};\n'
		return raw_object, set_objects







	def remove_objects(self, elements, recursive=True):
		for id in elements:
			if recursive:
				try:
					self.remove_objects( self.list_objects[id]['ID_child'] )
				except:
					pass
			try:
				self.list_objects[id] = ''
			except:
				pass
		return



	def add_recorder(self, ids, file_name, period, attributes):
		if type(ids) == list:
			if ids == []:
				return None
			list_ids = ids
		else:
			list_ids = [ids]

		for id in list_ids:
			recorder = copy.deepcopy(recorder_empty)
			recorder = recorder.replace('file_name**', file_name)
			recorder = recorder.replace('interval**', str(period))
			recorder = recorder.replace('properties**', ','.join(attributes))

			rec_id, pos = self.add_object(recorder)	
			self.list_objects[id]['ID_child'].append(rec_id)

		return rec_id



	def find_objects_set(self, attr, val, set_search):

		objects_match = []
		for i in set_search:
			try:
				if attr in self.list_objects[i].keys():
					if type(val) == str:
						values = [val]
					else:
						values = val

					for v in values:
						if v in self.list_objects[i][attr]:
							objects_match.append(i)
			except:
				pass
		return objects_match



	def find_and_remove(self, attributes):
		black_list = self.find_objects(attributes)
		#print(black_list)
		self.remove_objects(black_list)
		return



	# find objects with some properties
	def find_objects(self, list_attr):
		list_candidates = range( len(self.list_objects) )

		n = len(list_attr)
		for k in range(n):
			attr_k, val_k = list_attr[k]
			#print('attr: '+str(attr_k))
			#print('val: '+str(val_k))
			#print('')
			list_candidates = self.find_objects_set(attr_k, val_k, list_candidates)
		
			if len(list_candidates) == 0:
				return []
		return list_candidates




			

	def modify_attr(self, id, attr, val, add_attribute=False):

		if add_attribute:
			if attr not in self.list_objects[id]['list_attributes']:
				self.list_objects[id]['list_attributes'].append(attr)

			if type(val)  == list:
				self.list_objects[id][attr] = val
			else:
				self.list_objects[id][attr] = [val]
		else:
			if attr not in self.list_objects[id]['list_attributes']:
				return 

			if type(val)  == list:
				self.list_objects[id][attr] = val
			else:
				self.list_objects[id][attr] = [val]


		return 


	def read_attr(self, id, attr):
		if attr not in self.list_objects[id].keys():
			return None
		else:
			return self.list_objects[id][attr]	



	def remove_link(self, ids):

		for id in ids:
			switch_replace = copy.deepcopy(switch)
			switch_id, pos = self.add_object(switch_replace)

			# configure the switch	
			attributes = ['name', 'to', 'from']
			for attr in attributes:
				val = self.list_objects[id][attr]
				self.modify_attr( switch_id, attr, val)
			# remove the object
		self.remove_objects(ids)

		return

	# find the meter neighbor to the network node
	def find_neighbor(self, id, attr, val):
		obj_name = self.list_objects[id]['name']
		neighbors_a = self.find_objects([['parent', obj_name]])
		neighbors_b = self.find_objects([['from', obj_name]])

		#pdb.set_trace()

		if neighbors_a != []:
			for id_n in neighbors_a:
				try:
					if val in self.list_objects[id_n][attr]:
						return id_n
				except:
					pass
				id_match = self.find_neighbor(id_n, attr, val)
				if id_match != None:
					return id_match

		elif neighbors_b != []:
			for id_n in neighbors_b:
				name_next = self.list_objects[id_n]['to']
				id_next = self.find_objects([['name', name_next]])
				try:
					if val in self.list_objects[id_next[0]][attr]:
						return id_next[0]
				except:
					pass
				id_match = self.find_neighbor(id_next[0], attr, val)
				if id_match != None:
					return id_match

		return None


