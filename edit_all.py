'''
This module is a grab bag of functions for editing an entire user dictionary

'''
import get_selection
import word_methods

import glob
import os
import sys
import pickle, json
from iteration_utilities import unique_everseen
from copy import deepcopy
from unidecode import unidecode
import load_dict
import word_print_edit
import edit_entry
import edit_dictionary
from tables_greek_ext import auto_parts


# EDIT ALL
# # # # # # # # # # # # 
def edit_all(current_dict):

	while True:

		options = {'1':"Edit All Options:\n==================================\n>'1' to replace a tag\n",
		'q':">'q' other_unknown\n",
		'2':">'2' special option\n",
		'a':">'a' change file name\n",
		'b':">'b' special option II\n",
		'c':">'c' convert to gloss/tags defs\n",
		'd':">'d' match dictionaries\n",
		'3':">'3' to edit a subset by tag\n",
		'4':">'4' to remove punctuation\n",
		'5':">'5' to fix participles\n",
		'p':">'p' to fix pronuncitations\n",
		'6':">'6' deduplicate\n",
		'7':">'7' to fix verbs\n",
		'8':">'8' remove periods\n",
		'9':">'9' fix sort handles\n",
		'10':">'10' special greek option\n",
		#'q':">'q' to cut parens\n",
		'0':">'0' to go back\n",
		'r':">'r' to reset template indicators\n",
		't':">'t' to tag splits\n",
		's':">'s' remove spaces\n",
		'x':">'x' to convert to set\n"}
		user_input = get_selection.get_selection(options)

		if user_input == '0':
			return current_dict
		elif user_input == 'r':
			for i in current_dict['definitions']:
				if 'template' in i:
					del i['template']
		elif user_input == '1':
			current_dict = replace_tag(current_dict)
		elif user_input == 'a':
			current_dict = change_file_name(current_dict)
		elif user_input == 't':
			for i in current_dict['definitions']:
				if i['entries'][0]['partOfSpeech'] == 'verb':
					i['entries'][0]['simpleParts'] = auto_parts(i['entries'][0]['simpleParts'],True)					

			load_dict.change_path('dictionaries')
			openFile = open(current_dict['file'],mode = 'wb')
			pickle.dump(current_dict, openFile)
			openFile.close()	

		elif user_input == '2':
			current = special(current_dict)
		elif user_input == 'c':
			current_dict = replace_defs(current_dict)
		elif user_input == 'd':
			match_dictionaries(current_dict)
		elif user_input == 'p':
			current_dict = fix_pronunciations(current_dict)
		#elif user_input == 'q':
		#	cut_parens_access(current_dict['language'])
		elif user_input == '3':
			current_dict = edit_subset(current_dict)
		elif user_input == '4':
			current_dict == remove_all_punct(current_dict)
		elif user_input == 'b':
			find_paren(current_dict)
		elif user_input == '5':
			current_dict = fix_participles(current_dict)
		elif user_input == '6':
			current_dict = deduplicate(current_dict)
		elif user_input == '7':
			current_dict = fix_verbs(current_dict)
		elif user_input == '8':
			current_dict = remove_periods(current_dict)
		elif user_input == '9':
			current_dict = fix_sort_handles(current_dict)
		elif user_input == '10':
			current_dict = fix_etymology(current_dict)
		#elif user_input == '10':
		#	special_greek(current_dict)
		elif user_input == 's':
			current_dict = remove_spaces(current_dict)
		elif user_input == 'x':
			convert_to_set(current_dict)
		elif user_input == 'q':
			other_unknown(current_dict)

# END EDIT ALL

import tables, tables_greek_ext

def other_unknown(current_dict):
	print('re-doing all verbs')
	load_dict.change_path('templates')
	myFiles = glob.glob('*.txt')
	template_file = "AncientGreek_templates.txt"
	if template_file not in myFiles:
		print("No '_templates.txt' files found in directory")
		templates = []
	else:
		with open(template_file,'r') as f:
			templates = json.load(f)
	in_out_list = []	
	for t in templates:
		if t['POS'] == 'verb':
			user_input = input(f"{t['title']} = contracted (y/n)?: ")
			if user_input.lower() == 'y':
				in_out_list.append(True)
			else:
				in_out_list.append(False)
	print(f"in_out_list = : {in_out_list}")
	for i, t in enumerate(templates):
		if t['POS'] == 'verb':
			if in_out_list[i]:
				t = tables_greek_ext.get_forms(t)
				print(t['principal'])
	user_input = input("Save new verb data (y/n)?")
	if user_input.lower() == 'y':

		load_dict.change_path('templates')
		sort_tables(templates,language)
		with open(template_file,'w') as f:
			json.dump(templates,f)

		print('re-doing all verbs succesful')
	else:
		print('re-doing all verbs aborted succesfully')
	return
def special_greek(current_dict):
	letters = {
	'Ἀ':'Α',
	'ά':'α', 'ἀ':'α', 'ἄ':'α', 'ἅ':'α', 'ἆ':'α', 'ᾰ':'α', 'ᾱ':'α', 'ᾴ':'α',
	'έ':'ε', 'ἐ':'ε', 'ἑ':'ε', 'ἔ':'ε', 'ἕ':'ε', 
	'ή':'η','ἡ':'η', 'ἤ':'η', 'ἥ':'η', 'ῆ':'η',
	'ί':'ι','ἰ':'ι', 'ἱ':'ι', 'ἴ':'ι', 'ἵ':'ι', 'ἶ':'ι', 'ῐ':'ι', 'ῑ':'ι', 'ῖ':'ι',
	'ό':'ο','ὀ':'ο', 'ὁ':'ο', 'ὄ':'ο', 'ὅ':'ο',
	'ῥ':'ρ',
	'ύ':'υ','ὐ':'υ', 'ὑ':'υ', 'ὔ':'υ', 'ὕ':'υ', 'ὖ':'υ', 'ὗ':'υ','ῠ':'υ', 'ῡ':'υ', 'ῦ':'υ', 
	'ώ':'ω', 'ὧ':'ω','ῶ':'ω', 'ῷ':'ω'
	}
	letters = list(letters.keys())
	for x in current_dict['definitions']:
		for y in x['heading']:
			if y not in letters:
				letters.append(y)
	letters.sort()
	print("&" * 100)
	print(letters)

def remove_spaces(current_dict):
	for i in range(len(current_dict['definitions'])):
		for j in range(len(current_dict['definitions'][i]['entries'])):
			for k in range(len(current_dict['definitions'][i]['entries'][j]['defs'])):
					text = current_dict['definitions'][i]['entries'][j]['defs'][k]
					text['gloss'] = text['gloss'].replace(" .",".").replace(" ,",",").replace(" :",":")
					current_dict['definitions'][i]['entries'][j]['defs'][k] = text		
	with open(current_dict['file'],mode = 'wb') as openFile:
		pickle.dump(current_dict, openFile)
	return current_dict	

def fix_etymology(current_dict):
	for i in range(len(current_dict['definitions'])):
		for x in range(len(current_dict['definitions'][i]['entries'])):
			current_dict['definitions'][i]['entries'][x]['etymology'] = current_dict['definitions'][i]['entries'][x]['etymology'].strip('\n')
			current_dict['definitions'][i]['entries'][x]['etymology'] = current_dict['definitions'][i]['entries'][x]['etymology'].replace("\n"," ")
	openFile = open(current_dict['file'],mode = 'wb')
	pickle.dump(current_dict, openFile)
	openFile.close()			
	return current_dict

def fix_sort_handles(current_dict):
	for i in range(len(current_dict['definitions'])):
		if 'sort_handle' in current_dict['definitions'][i]:
			current_dict['definitions'][i]['handle'] = current_dict['definitions'][i]['heading']
			del current_dict['definitions'][i]['sort_handle']
	openFile = open(current_dict['file'],mode = 'wb')
	pickle.dump(current_dict, openFile)
	openFile.close()			
	return current_dict

def fix_pronunciations(current_dict):
	for i in range(len(current_dict['definitions'])):
		if 'Pronunciation' in current_dict['definitions'][i]['tags']:
			current_dict['definitions'][i]['heading'] = "<!--Pronunciation-->Pronunciation: " + current_dict['definitions'][i]['heading']
			current_dict['definitions'][i]['handle'] = current_dict['definitions'][i]['heading']
	openFile = open(current_dict['file'],mode = 'wb')
	pickle.dump(current_dict, openFile)
	openFile.close()			
	return current_dict

def change_file_name(current_dict):
	print(f"Enter new name for {current_dict['file']} ('0' to go back)")
	user_input = input(": ")
	if user_input == '0':
		return current_dict
	else:
		load_dict.change_path('dictionaries')
		current_dict['file'] = user_input + '.txt'
		openFile = open(current_dict['file'],mode = 'wb')
		pickle.dump(current_dict, openFile)
		openFile.close()			
		return current_dict

def replace_defs(current_dict):
	for i in range(len(current_dict['definitions'])):
		for j in range(len(current_dict['definitions'][i]['entries'])):
			for k in range(len(current_dict['definitions'][i]['entries'][j]['defs'])):
				current_dict['definitions'][i]['entries'][j]['defs'][k] = {'gloss':current_dict['definitions'][i]['entries'][j]['defs'][k],'tags':[]}
	openFile = open(current_dict['file'],mode = 'wb')
	pickle.dump(current_dict, openFile)
	openFile.close()	
	return current_dict

def load_latin(index_letter):
	if index_letter.lower() not in 'abcdefghijklmnopqrstuvwxyz':
		index_letter = 'misc'
	load_dict.change_path("dumps sorted")
	with open('Latin-' + index_letter.lower() + '.txt','rb') as openFile:
		wiki_dump = pickle.load(openFile)
	return wiki_dump


def match_dictionaries(current_dict):
	load_dict.change_path("dumps sorted")
	trie_file = current_dict['language'].replace(" ","") + '-trie.txt'

	print(f"Loading {trie_file}")
	with open(trie_file, 'rb') as openFile:
		current_trie = pickle.load(openFile)['definitions']

	for word_data in current_dict['definitions']:
		heading = unidecode(word_data['heading'].lower())
		if heading in current_trie:
			if isinstance(current_trie[heading],list):
				for i in range(len(current_trie[heading])):
					if current_trie[heading][i]['heading'] == word_data['heading']:
						print(f"{word_data['heading']} updated")
						current_trie[heading][i]['tags'].update(word_data['tags'])
			else:
				print(f"{word_data['heading']} updated")
				current_trie[heading]['tags'].update(word_data['tags'])
		else:
			print(f"\t{word_data['heading']} added")
			current_trie[heading] = deepcopy(word_data)

	with open(current_dict['language'].replace(" ","") + '-trie.txt', mode = 'wb') as openFile:
		pickle.dump({'file': trie_file, 'language': current_dict['language'], 'definitions': current_trie}, openFile, protocol=pickle.HIGHEST_PROTOCOL)


def remove_all_punct(current_dict):
	for i in range(len(current_dict['definitions'])):
		for j in range(len(current_dict['definitions'][i]['entries'])):
			for k in range(len(current_dict['definitions'][i]['entries'][j]['defs'])):
				if '\n' in current_dict['definitions'][i]['entries'][j]['defs'][k]:
					text = current_dict['definitions'][i]['entries'][j]['defs'][k]
					text = text[:text.find('\n')]
					current_dict['definitions'][i]['entries'][j]['defs'][k] = text		
	with open(current_dict['file'],mode = 'wb') as openFile:
		pickle.dump(current_dict, openFile)

def remove_periods(current_dict):
	for i in range(len(current_dict['definitions'])):
		for j in range(len(current_dict['definitions'][i]['entries'])):
			for k in range(len(current_dict['definitions'][i]['entries'][j]['defs'])):
					text = current_dict['definitions'][i]['entries'][j]['defs'][k]
					text['gloss'] = text['gloss'].strip(",.; ")
					current_dict['definitions'][i]['entries'][j]['defs'][k] = text		
	with open(current_dict['file'],mode = 'wb') as openFile:
		pickle.dump(current_dict, openFile)
	return current_dict


def prune(entry):
	while True:
		edit_entry.print_entry(entry)
		user_input = int(input("Prune definitions starting from ('0' to finish): "))
		if user_input == 0:
			return entry
		else:
			entry['defs'] = entry['defs'][:user_input]

def remove_punct(entry):
	while True:
		edit_entry.print_entry(entry)
		user_input = input("Choose character to remove ('0' to finish): ")
		if user_input == '0':
			return entry
		else:
			for i in range(len(entry['defs'])):
				text = entry['defs'][i]
				text = list(text)
				while user_input in text:
					text.remove(user_input)
				new_text = ''
				for c in text:
					new_text += c
				entry['defs'][i] = new_text


# SPECIAL
# # # # # # # # # # # 
def special(current_dict,start=0):

	for i in range(start,len(current_dict['definitions'])):
		while True:
			edit_entry.print_entry(current_dict['definitions'][i]['entries'][0],'length')
			print(f"DEFINITION # {i}\n")
			options = {'0':">'0' to stop\n",
				'1':">'1' to prune definitions\n",
				'2':">'2' to remove punctuation\n",
				'3':">'3' to continue\n",
				'4':">'4' to skip forward\n",
				'5':">'5' to change order\n",
				'6':">'6' to change definition\n"}
			user_input = get_selection.get_selection(options)
			if user_input == '0':
				return current_dict
			elif user_input == '1':
				current_dict['definitions'][i]['entries'][0] = prune(current_dict['definitions'][i]['entries'][0])
				with open(current_dict['file'],mode = 'wb') as openFile:
					pickle.dump(current_dict, openFile)
			elif user_input == '2':
				current_dict['definitions'][i]['entries'][0] = remove_punct(current_dict['definitions'][i]['entries'][0])
				with open(current_dict['file'],mode = 'wb') as openFile:
					pickle.dump(current_dict, openFile)
			elif user_input == '3':
				break
			elif user_input == '4':
				user_input = int(input("Choose start position: "))
				if user_input != 0:
					special(current_dict,user_input)
					return current_dict
			elif user_input == '5':
				while True:
					user_input = input("Enter selection and new position seperated by commas ('0' to stop): ")
					if user_input == '0':
						break
					else:
						user_input = user_input.split(',')
						current_dict['definitions'][i]['entries'][0]['defs'] = edit_entry.move_entries(current_dict['definitions'][i]['entries'][0]['defs'],int(user_input[0]),int(user_input[1]))
				with open(current_dict['file'],mode = 'wb') as openFile:
					pickle.dump(current_dict, openFile)
			elif user_input == '6':
				message = "\nChoose the definition you want to change"
				selection = edit_entry.select_definition(current_dict['definitions'][i]['entries'][0],message)
				if selection != None:
					current_dict['definitions'][i]['entries'][0]['defs'][selection] = edit_entry.remove_words(current_dict['definitions'][i]['entries'][0]['defs'][selection])
					with open(current_dict['file'],mode = 'wb') as openFile:
						pickle.dump(current_dict, openFile)
	return current_dict
# END SPECIAL


# REPLACE TAG
# # # # # # # # # # # 
def replace_tag(current_dict):

	# Set directory
	load_dict.change_path('dictionaries')

	while True:
		tags = word_methods.get_master_list(current_dict)

		options = {'0':"Select the tag you want to replace ('0' to go back)\n"}

		for index in range(len(tags)):
			options[f"{index + 1}"] = f"{index + 1}. {tags[index]}\n"
		user_input = get_selection.get_selection(options)

		if user_input == '0':
			return current_dict

		else:
			tag_selection = tags[int(user_input) - 1]

			print(f"Enter the replacement tag for {tag_selection} ('0' to go back)")
			user_input = input(": ")

			if user_input == '0':
				continue
			else:
				for index in range(len(current_dict['definitions'])):
					offset = 0
					for inner in range(len(current_dict['definitions'][index]['tags'])):
						inner = inner - offset
						if current_dict['definitions'][index]['tags'][inner] == tag_selection:
							if user_input == '':
								del current_dict['definitions'][index]['tags'][inner]
								offset += 1
							else:
								current_dict['definitions'][index]['tags'][inner] = user_input

				# open file, pickle.dump definitions list to fine, close file
				openFile = open(current_dict['file'],mode = 'wb')
				pickle.dump(current_dict, openFile)
				openFile.close()

				print(f"All instances of {tag_selection} replaced with {user_input}\n")
# REPLACE TAG

def convert_to_set(current_dict):

	# Set directory
	load_dict.change_path('dictionaries')

	# Convert all tags from lists to sets
	for index in range(len(current_dict['definitions'])):
		current_dict['definitions'][index]['tags'] = set(current_dict['definitions'][index]['tags'])

	# open file, pickle.dump definitions list to fine, close file
	openFile = open(current_dict['file'],mode = 'wb')
	pickle.dump(current_dict, openFile)
	openFile.close()



# EDIT SUBSET
# # # # # # # # # # # # # 
def edit_subset(current_dict):

	# Set directory
	load_dict.change_path('dictionaries')
	while True:

		# option to set tags
		master_list = word_methods.get_master_list(current_dict)
		tags = word_methods.getTags([],'subset',master_list)

		options = {'0':"Subset options:\n>'0' to go back\n",
		'1':">'1' to add tags to subset\n",'2':">'2' to remove tags from subset\n"}
		user_input = get_selection.get_selection(options)

		if user_input == '0':
			return current_dict

		elif user_input == '1':
			mode = 'add'
			from_to = 'to'
		elif user_input == '2':
			mode = 'remove'
			from_to = 'from'

		options = {'1':">'1' for exact match\n",'2':">'2' for any word with selected tags\n"}
		user_input = get_selection.get_selection(options)

		if user_input == '1':
			exact = True
		elif user_input == '2':
			exact = False

		exit_loop = False
		while not exit_loop:
			print(f"Enter the tag your want to {mode} {from_to} your subset ('0' to go back)")
			user_input = input(": ")

			if user_input == '0':
				exit_loop = True

			# Loop to create sub-list to select from
			offset = 0
			for index in range(len(current_dict['definitions'])):
				index = index - offset

				# assign word to shorten name
				current_tags = current_dict['definitions'][index]['tags']
				# test if tags match; always 'yes' for empty tags
				if exact:
					tag_test = current_tags == tags
				else:
					tag_test = set(tags).issubset(set(current_tags))

				if tag_test:
					if mode == 'add':
						current_dict['definitions'][index]['tags'].append(user_input)
					elif mode == 'remove':
						if user_input in current_dict['definitions'][index]['tags']:
							current_dict['definitions'][index]['tags'].remove(user_input)
							offset += 1

			# open file, pickle.dump definitions list to fine, close file
			with  open(current_dict['file'],mode = 'wb') as openFile:
				pickle.dump(current_dict, openFile)

			print(f"\n{user_input} {mode[:5]}ed {from_to} subset\n")

			return current_dict
# END EDIT SUBSET

def fix_participles(current_dict):
	for i in range(len(current_dict['definitions'])):
		for j in range(len(current_dict['definitions'][i]['entries'])):
			if current_dict['definitions'][i]['entries'][j]['partOfSpeech'] == 'verb':
				simpleParts = current_dict['definitions'][i]['entries'][j]['simpleParts']
				simpleParts = simpleParts.split(',')
				if len(simpleParts) >= 3:
					if simpleParts[0][-2:] == 'us' and simpleParts[1][-1:] == 'a' and simpleParts[2][-2:] == 'um':
						current_dict['definitions'][i]['entries'][j]['partOfSpeech'] = 'participle'
						current_dict['definitions'][i]['entries'][j]['simpleParts'] = simpleParts[0].strip() + ", " + simpleParts[1].strip() + ", " + simpleParts[2].strip()
				if len(simpleParts) >= 2:
					if simpleParts[0][-2:] == 'ns' and simpleParts[1][-4:] == 'ntis':
						current_dict['definitions'][i]['entries'][j]['partOfSpeech'] = 'participle'
						current_dict['definitions'][i]['entries'][j]['simpleParts'] = simpleParts[0].strip() + ", " + simpleParts[1].strip()
				if current_dict['definitions'][i]['entries'][j]['partOfSpeech'] == 'participle':
					first = False
					for k in range(len(current_dict['definitions'][i]['entries'][j]['defs'])):
						text = current_dict['definitions'][i]['entries'][j]['defs'][k]['gloss']
						text, first = word_methods.participle_edit(text,first)
						current_dict['definitions'][i]['entries'][j]['defs'][k]['gloss'] = text
	openFile = open(current_dict['file'],mode = 'wb')
	pickle.dump(current_dict, openFile)
	openFile.close()	
	return current_dict


def fix_verbs(current_dict):
	for i in range(len(current_dict['definitions'])):
		for j in range(len(current_dict['definitions'][i]['entries'])):
			if current_dict['definitions'][i]['entries'][j]['partOfSpeech'] == 'verb':
				for k in range(len(current_dict['definitions'][i]['entries'][j]['defs'])):
					text = current_dict['definitions'][i]['entries'][j]['defs'][k]['gloss']
					text = word_methods.verb_edit(text)
					current_dict['definitions'][i]['entries'][j]['defs'][k]['gloss'] = text
	openFile = open(current_dict['file'],mode = 'wb')
	pickle.dump(current_dict, openFile)
	openFile.close()	
	return current_dict

import collections
from copy import deepcopy

def deduplicate(current_dict):
	entries = collections.defaultdict(list)
	language = current_dict['language']
	
	for item in current_dict['definitions']:
		if language == "Latin":
			key = unidecode(item['heading'])
		else:
			key = item['handle']
		entries[key].append(item)

	new_definitions = []
	for key, values in entries.items():
		main_item = deepcopy(values[0])
		if len(values) > 1:
			for value in values[1:]:
				main_item['entries'].extend(deepcopy(value['entries']))
		new_definitions.append(main_item)
		
	current_dict['definitions'] = new_definitions
	
	with open(current_dict['file'], mode='wb') as openFile:
		pickle.dump(current_dict, openFile)
	print("De-Duplicating Successful")

	return current_dict


def cut_parens_access(language):
	if language == "Latin":
		alpha = {'a':[],
		'b':[],
		'c':[],
		'd':[],
		'e':[],
		'f':[],
		'g':[],
		'h':[],
		'i':[],
		'j':[],
		'k':[],
		'l':[],
		'm':[],
		'n':[],
		'o':[],
		'p':[],
		'q':[],
		'r':[],
		's':[],
		't':[],
		'u':[],
		'v':[],
		'w':[],
		'x':[],
		'y':[],
		'z':[],
		'misc':[]}
		for key in alpha:
			alpha[key] = load_latin(key)
		for key in alpha:
			cut_parens(alpha[key])
	else:
		load_dict.change_path("dumps sorted")
		with open(language.replace(" ","") + 'Dump.txt','rb') as openFile:
			wiki_dump = pickle.load(openFile)
		cut_parens(wiki_dump)

def cut_parens(current_dict):
	for i in range(len(current_dict['definitions'])):
		for j in range(len(current_dict['definitions'][i]['entries'])):
			for k in range(len(current_dict['definitions'][i]['entries'][j]['defs'])):
				g = current_dict['definitions'][i]['entries'][j]['defs'][k]['gloss']
				if g[0] == "(":
					tags = ", ".join(current_dict['definitions'][i]['entries'][j]['defs'][k]['tags'])
					p = g[g.find("(") + 1:g.find(")")]
					if tags in p or tags.replace("-"," ") in p:
						current_dict['definitions'][i]['entries'][j]['defs'][k]['gloss'] = g[g.find(")") + 1:].strip(": ")
					else:
						for tag in current_dict['definitions'][i]['entries'][j]['defs'][k]['tags']:
							if tag in p or tag.replace("-"," ") in p:
								current_dict['definitions'][i]['entries'][j]['defs'][k]['gloss'] = g[g.find(")") + 1:].strip(": ")
	with open(current_dict['file'],mode = 'wb') as openFile:
		pickle.dump(current_dict, openFile)
	return current_dict

def find_paren(current_dict):
	original_stdout = sys.stdout
	sys.stdout = open("parenthesis.txt",'w')
	for definition in current_dict['definitions']:
		for defs in definition['entries'][0]['defs']:
			if ')' in defs:
				text = defs[defs.find("("):defs.find(")")+1]
				print(text)
	sys.stdout = original_stdout

'''
def fix_etymology(current_dict):
	for i in range(len(current_dict['definitions'])):
		for j in range(len(current_dict['definitions'][i]['entries'])):
			if 'etymology' in current_dict['definitions'][i]['entries'][j]:
				current_dict['definitions'][i]['entries'][j]['etymology'] = current_dict['definitions'][i]['entries'][j]['etymology'].replace('\n',' ')
	with open(current_dict['file'],mode = 'wb') as openFile:
		pickle.dump(current_dict, openFile)
	return current_dict
'''


