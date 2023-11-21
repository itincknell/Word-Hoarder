import json, pickle
import glob
import os
from load_dict import change_path
from get_selection import get_selection
from unidecode import unidecode
from copy import deepcopy
import requests
import re
import tables_greek_ext

DEBUG = True
import inspect

def debug_print(message):
	line_number = inspect.currentframe().f_back.f_lineno
	if DEBUG:
		print(f"[Line {line_number}] - {message}")

def get_tables(language):
	change_path('tables')
	myFiles = glob.glob('*.txt')
	table_file = language.replace(" ","") + "-tables.txt"
	if table_file not in myFiles:
		return []
	else:
		with open(table_file,'r') as f:
			tables_list = json.load(f)
		tables_list = sort_tables(tables_list,language)
		return tables_list

def get_forms(language):
	change_path('tables')
	myFiles = glob.glob('*.txt')
	form_file = language.replace(" ","") + "-forms.txt"
	if form_file not in myFiles:
		return []
	else:
		with open(form_file,'r') as f:
			forms_list = json.load(f)
		forms_list = sort_tables(forms_list,language)
		return forms_list

def sort_tables(tables_list,language):
	if language == 'Ancient Greek':
		tables_list.sort(key=lambda item: greek_sort_name(item.get('title')))
	else:
		tables_list.sort(key=lambda item: find_sort_name(item.get('title')))
	return tables_list

def greek_sort_name(word):
	if ": " in word:
		word = word[word.find(": ")+2]
	return replace_greek(word.lower())

def find_sort_name(word):
	if ": " in word:
		word = word[word.find(": ")+2]
	return unidecode(word.lower())

def replace_greek(word):
	alt_letters = {
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
	for x in word:
		if x in alt_letters:
			word = word.replace(x,alt_letters[x])
	return word

def replace_greek_ii(word):
	alt_letters = {
	'Ᾰ̓':'Ἀ', 

	'Ᾰ̔':'Ἁ', 
	'ᾰ̀':'ὰ', 
	'ᾰ́':'ά', 
	'ᾰ̓':'ἀ', 
	'ᾰ̔':'ἁ', 
	'ἀ̆':'ἀ', 
	'ἄ̆':'ἄ', 
	'ά̆':'ά', 
	'Ῐ̓':'Ἰ', 
	'Ῐ̔':'Ἱ', 
	'ῐ̈':'ι', 
	'ϊ':'ι',
	'ῐ̓':'ἰ', 
	'ῐ̔':'ἱ',
	'ί̆':'ί', 
	'Ῠ̔':'Υ',
	'ύ̆':'ύ', 
	'ῠ́':'ύ', 
	'ῠ̈':'υ', 
	'ῠ̔':'ὑ',

	# added for kukao
	'ῠ':'υ',

	# removed for εὐνοϊκός
	# 'ϊ̄́':'ί', 


	'ί':'ί', 
	'ύ':'ύ', 
	
	'ἄ':'ἄ', 
	'ἴ':'ἴ', 

	'ᾰ̔':'ἁ', 
	'ᾰ́':'ά', 
	'ᾰ':'α', 



	'Ᾱ̓́':'Ἄ', 
	'Ᾱ̓':'Ἀ', 
	'Ᾱ̔':'Ἁ', 
	'Ᾱ':'Α', 
	'ᾱ̔́':'ἅ', 
	'ᾱ̓́':'ἄ', 
	'ᾱ̀':'ὰ', 
	'ᾱ́':'ά', 
	'ᾱ̆':'ᾶ', 
	'ᾱ̔':'ἁ', 
	'ᾱ̓':'ἀ', 
	'ᾱ':'α', 
	'Ῑ̓́':'Ἴ', 
	'Ῑ̓':'Ἰ', 
	'Ῑ̔':'Ἱ', 
	'Ῑ':'Ι', 
	'ῑ́̔':'ἵ', 
	'ῑ̈́':'ί', 
	'ῑ̓́':'ἴ', 
	'ῑ̔́':'ἵ', 
	'ῑ̔':'ἱ', 
	'ῑ́':'ί', 
	'ῑ̆':'ῖ', 
	'ῐ':"ι",
	'ῑ̈':'ι', 
	'ῐ́':'ί',
	'ῑ̓':'ἰ', 
	'ῑ':'ι', 
	'ῡ̈́':'ύ',
	'ῡ̔́':'ὕ', 
	'ῡ́':'ύ', 
	'ῡ̈':'υ', 
	'ῡ̔':'ὑ', 
	'ῡ':'υ', 
	'Ῡ̔':'Υ'
	}

	for x in alt_letters:
		if x in word:
			word = word.replace(x,alt_letters[x])
	return word


def save_tables(tables_list,file):
	change_path('tables')
	with open(file,'w') as f:
		json.dump(tables_list,f)

def add_table(tables_list,table_info):
	found = False
	for i in range(len(tables_list)):
		if tables_list[i]['title'] == table_info['title']:
			debug_print(f"Match found {table_info['title']} == {tables_list[i]['title']}")
			tables_list[i] = deepcopy(table_info)
			debug_print(f"{table_info['title']} updated")
			found = True
			break
	if not found:
		debug_print(f"No Match Found: New entry made for {table_info['title']}")
		tables_list.append(deepcopy(table_info))
		debug_print(f"{table_info['title']} added successfully")
	return tables_list

def table_options(language):
	while True:

		options = {'1':"\nTable Options:\n==================================\n>'1' to add a table\n",
			'2':">'2' to edit tables\n",
			'3':">'3' to print table flashcards\n",
			'4':">'4' for template options\n",
			'0':">'0' to go back\n"}
		user_input = get_selection(options)
		if user_input == '1':
			add_tables(language)
		elif user_input == '2':
			edit_tables(language)
		elif user_input == '3':
			tables_list = get_tables(language)
			print_tables(tables_list,language)
		elif user_input == '4':
			template_options(language)
		elif user_input == '0':
			return
'''
def template_options(language):
	print('re-doing all templates')
	change_path('templates')
	myFiles = glob.glob('*.txt')
	template_file = language.replace(" ","") + "_templates.txt"
	if template_file not in myFiles:
		templates = []
	else:
		with open(template_file,'r') as f:
			templates = json.load(f)
	for t in templates:
		if t['POS'] == 'verb':
			t = tables_greek_ext.get_forms(t)

	change_path('templates')
	sort_tables(templates,language)
	with open(template_file,'w') as f:
		json.dump(templates,f)

	print('re-doing all templates succesful')
	return
'''
def template_options(language):
	while True:
		change_path('templates')
		myFiles = glob.glob('*.txt')
		template_file = language.replace(" ","") + "_templates.txt"
		if template_file not in myFiles:
			templates = []
		else:
			with open(template_file,'r') as f:
				templates = json.load(f)

		while True:
			if templates == []:
				user_input = "00"
			else:

				options, keys = get_template_options(templates)
				user_input = get_selection(options,"\nSelect template:\n==================================\n")
			if user_input == '0':
				break
			if user_input == '00':
				template = new_template(language)
				if template:
					templates.append(template)
			#if user_input == "x":
			#	templates = redo_templates(templates,language)
			else:
				for i in range(len(templates)):
					if templates[i]['title'] == keys[user_input]['title']:
						edit_template(templates[i],language)
						break

		change_path('templates')
		sort_tables(templates,language)
		with open(template_file,'w') as f:
			json.dump(templates,f)
		return

def edit_template(template,language):
	if language == 'Ancient Greek':
		return tables_greek_ext.edit_template(template)	
	elif language == "Latin":
		return tables_latin_ext.edit_template(template)	

def new_template(language,heading='',handle='',definition='',partOfSpeech=''):
	if language == 'Ancient Greek':
		return tables_greek_ext.new_template(heading,handle,definition,partOfSpeech)
	elif language == 'Latin':
		return tables_latin_ext.new_template(heading,handle,definition,partOfSpeech)
	elif language == 'Old English':
		return tables_oe_ext.new_template(heading,handle,definition,partOfSpeech)

def redo_templates(templates,language):
	if language == 'Ancient Greek':
		return tables_greek_ext.redo(templates)

def get_template_options(templates):
	counter = 1
	options = {}
	keys = {}
	for t in templates:
		fill_char = '#'
		options[str(counter)] = f"{counter:>4}. {t['title']}"
		keys[str(counter)] = t
		counter += 1
	options.update({'00':" '00' to create new\n"})
	options.update({'0':"'0' to go back"})
	#options.update({"x":"'x' to re-do existing templates"})
	return options, keys

def auto_template(dictionary,word):
	change_path('templates')
	myFiles = glob.glob('*.txt')
	language = dictionary['language']
	template_file = language.replace(" ","") + "_templates.txt"
	if template_file not in myFiles:
		templates = []
	else:
		with open(template_file,'r') as f:
			templates = json.load(f)

	for i in range(len(word['entries'])):
		entry = word['entries'][i]
		def_string = [x['gloss'] for x in entry['senses']]
		def_string = "; ".join(chop_line(def_string[:5]))
		print(f"\n{word['heading']} entry #{i+1} info:")
		print("{:<18}".format("Principle Parts:") + entry['simpleParts'])
		print("{:<18}".format("Part of Speech:") + entry['partOfSpeech'])
		print("{:<18}".format("Definition:") + def_string)
		if 'etymology' in entry:
			if len(entry['etymology']) <= 125:
				print("{:<18}".format("Etymology:") + entry['etymology'])
		print(f"Create template ('1' for yes, '0' to finish, any other key to skip)")
		user_input = input(": ")
		if user_input == '0':
			break
		elif user_input == '1':	
			word['template'] = True
			template = new_template(language,word['heading'],word['handle'],def_string,word['entries'][i]['partOfSpeech'])
			if template:
				templates.append(template)

	change_path('templates')
	sort_tables(templates,language)
	with open(template_file,'w') as f:
		json.dump(templates,f)
	return

def chop_line(text):
	bank = ["*","^","†","∆"]
	for x in bank:
		for i in range(len(text)):
			text[i] = text[i].replace(x,"")
	
	if len(text) < 3:
		limit = 5
	elif len(text) == 3:
		limit = 4
	elif len(text) == 4:
		limit = 3
	elif len(text) == 5:
		limit = 2

	size = sum([len(line) for line in text])
	if size > 100:
		for i in range(len(text)):
			text[i] = short_line(text[i],limit)
	return text


# SHORT LINE
# # # # # # # # # # 
def short_line(line,limit):

	#print(f"PRINT SHORT LINE WHILE TOP PRE SPLIT:\n{line}")
	line = re.split(",|;",line)
	stop = orstop = parstop = limit
	for i in range(len(line)):
		orlist = [x for x in line[i:] if " or " in x]
		if orlist != []:
			orstop = i + 1
			continue
		else:
			#stop = max(i,limit)
			break
	for i in range(len(line)):
		parlist = [x for x in line[i:] if ")" in x or "(" in x]
		if parlist != []:
			parstop = i + 1
			continue
		else:
			#stop = max(i,limit)
			break
	stop = max(orstop,parstop,limit)
	line = line[:stop]
	new_text = ''
	for i in range(len(line)):
		new_text += line[i].strip() + ', '
	line = new_text.strip(", ")

	return line

def get_template(language):
	change_path('templates')
	myFiles = glob.glob('*.txt')
	template_file = language.replace(" ","") + "_templates.txt"
	if template_file not in myFiles:
		return None
	else:
		with open(template_file,'r') as f:
			templates = json.load(f)	
		while True:
			print("Choose template ('0' to go back)")
			for i in range(len(templates)):
				print(f"{i + 1}. {templates[i]['title']}")
			user_input = input(": ")
			if user_input == '0':
				return None
			elif user_input == '':
				print("Invalid selection")
			elif user_input[0] == '-':
				if user_input[1:].isnumeric():
					if int(user_input[1:]) - 1 in range(len(templates)):
						del templates[int(user_input[1:]) - 1]
			elif int(user_input) - 1 in range(len(templates)):
				return templates[int(user_input) - 1 ]
			else:
				print("Invalid selection")

def get_table_types(tables_list):
	counter = 1
	options = {}
	types = {}
	for t in tables_list:
		if t['type'] not in types.values():
			options[str(counter)] = f"{counter:>3}. {t['type']}\n"
			types[str(counter)] = t['type']
			counter += 1
	options.update({'0':"'0' to go back"})
	return options, types

def get_table_family(tables_list,table_type):
	counter = 1
	families = {}
	options = {}
	for t in tables_list:
		if t['type'] == table_type:
			word = t['title'][t['title'].find(": ")+2:]
			if word not in families.values():
				options[str(counter)] = f"{counter:>3}. {t['title'][t['title'].find(': ')+2:]}"
				families[str(counter)] = t['title'][t['title'].find(': ')+2:]
				counter += 1
	options.update({'0':"'0' to go back"})
	return options, families

def get_table_options(tables_list,table_type,family=None):
	counter = 1
	positions = {}
	options = {}
	for i in range(len(tables_list)):
		t = tables_list[i]
		if t['type'] == table_type:
			word = t['title'][t['title'].find(": ")+2:]
			if family == None or family == word:
				positions[str(counter)] = i
				options[str(counter)] = f"{counter:>3}. {t['title']}"
				counter += 1
	options.update({'0':"'0' to go back"})
	return options, positions


def edit_tables(language):
	tables_list = get_tables(language)
	while True:
		
		options, types = get_table_types(tables_list)
		options['1'] = "\nSelect table group:\n==================================\n" + options['1'] 
		user_input = get_selection(options)
		if user_input == '0':
			return
		table_type = types[user_input]
		family = None
		if table_type == 'conj':
			
			options, families = get_table_family(tables_list,'conj')
			options['1'] = "\nSelect table family:\n==================================\n" + options['1'] 
			user_input = get_selection(options)
			if user_input == '0':
				continue
			family = families[user_input]
		exit_loop = False
		while not exit_loop:
			options, positions = get_table_options(tables_list,table_type,family)
			options['1'] = "\nSelect table:\n==================================\n" + options['1'] 
			user_input = get_selection(options)
			if user_input == '0':
				exit_loop = True
				continue
			elif user_input in positions:
				index = positions[user_input]
				if index in range(len(tables_list)):
					print("'X' to delete, any other key to edit")
					user_input = input(': ')
					if user_input == 'X':
						del tables_list[index]
					else:
						tables_list[index] = edit_table(tables_list[index])
					save_tables(tables_list,language)
					continue
			else:
				print("Invalid entry")

def get_person(x,y):
	if x == '1st Person':
		return '1st Sg.' if y == 'Singular' else '1st Pl.'
	elif x == '2nd Person':
		return '2nd Sg.' if y == 'Singular' else '2nd Pl.'
	elif x == '3rd Person':
		return '3rd Sg.' if y == 'Singular' else '3rd Pl.'

def edit_table(table):
	while True:
		table_list = [['definition','',table['definition']]]
		table_list.append(['title','',table['title']])
		for part in table['parts']:
			if type(table['parts'][part]) != dict:
				table_list.append([part,'',table['parts'][part]])
			else:
				for x in table['parts'][part]:
					if type(table['parts'][part][x]) != dict:
						table_list.append([part,x,table['parts'][part][x]])
					else:
						for y in table['parts'][part][x]:
							person = get_person(x,y)
							table_list.append([part,person,table['parts'][part][x][y]])
		for i in range(len(table_list)):
			if table['type'] != 'parts':
				print(f"{i + 1:>2}. {table_list[i][0]:>11} {table_list[i][1]:>8}: {table_list[i][2]}")
			else:
				print(f"{i + 1:>2}. {table_list[i][0]:>15}: {table_list[i][2]}")
		user_input = input("('0' to go back): ")
		if user_input == '0':
			return table
		elif user_input.isnumeric():
			if int(user_input) - 1 in range(len(table_list)):
				if table_list[int(user_input) - 1][0] == 'definition':
					print("Enter replacement definition ('0' to cancel)")
					user_input = input(": ")
					if user_input != '0':
						table['definition'] = user_input
				elif table_list[int(user_input) - 1][0] == 'title':
					print("Enter replacement title ('0' to cancel)")
					user_input = input(": ")
					if user_input != '0':
						table['title'] = user_input					
				else:
					part = table_list[int(user_input)-1][0]
					number = table_list[int(user_input)-1][1]
					print(f"Enter replacement for {table['parts'][part][number]} ('0' to cancel) (ᾱ)")
					user_input = input(": ")
					if user_input != '0':
						table['parts'][part][number] = user_input
		else:
			print("Invalid entry")

import tables_latin_ext, tables_greek_ext, tables_oe_ext

def add_tables(language):
	if language == 'Ancient Greek':
		tables_greek_ext.add_tables()
	elif language == 'Latin':
		tables_latin_ext.add_tables()
	elif language == 'Old English':
		tables_oe_ext.add_tables()

def get_html(word):
	try:
		search_string = "https://en.wiktionary.org/wiki/" + word
		page_obj = requests.get(search_string)
		html_doc = page_obj.content
	except:
		print("\tERROR: Search String Not Found ")
		return
	print(f"{word} retreived successfully")
	return html_doc

def create_style(body_string,columns):
		if columns == 2:
			body_string += '</style>' + f'<table class="tg" style="undefined;table-layout: fixed; width: 600px">\
		<colgroup>\
		<col style="width: 100px">\
		<col style="width: 250px">\
		<col style="width: 250px">'
		elif columns == 1:
			body_string += '</style>' + f'<table class="tg" style="undefined;table-layout: fixed; width: 600px">\
		<colgroup>\
		<col style="width: 300px">\
		<col style="width: 300px">'
		body_string += '</colgroup>'
		return body_string

def create_table(body_string,parts,t_type,columns,header=''):
	body_string = create_style(body_string,columns)
	body_string += f'<thead><tr><th class="tg-0lax">{header}</th>'
	columns = parts[list(parts.keys())[0]]
	for col in columns:
		body_string += f'<th class="tg-0lax">{col}</th>'
	body_string += "</tr></thead><tbody>"
	for row in parts:
		body_string += '<tr>'
		if t_type == 'noun':
			body_string += f'<td class="tg-0lax">{row[:3]}.</td>'
		elif t_type == 'conj':
			body_string += f'<td class="tg-0lax">{row[:3]}</td>'
		else:
			body_string += f'<td class="tg-0lax">{row}</td>'
		for col in parts[row]:
			body_string += f'<td class="tg-0lax">{parts[row][col]}</td>'
		body_string += '</tr>'
	body_string += '</tbody></table>'
	return body_string

def print_tables(tables_list,language):
	if language == 'Ancient Greek':
		tables_greek_ext.print_tables(tables_list)
	elif language == 'Latin':
		tables_latin_ext.print_tables(tables_list)
	elif language == 'Old English':
		tables_oe_ext.print_tables(tables_list)
	print("\n**************************\n\nFlashcards printed to file\n\n**************************\n")
'''

#import parser_shell, word_print_edit, edit_dictionary, edit_entry
def add_definition(language):

	while True:
		change_path('dumps sorted')
		wiki_dump = parser_shell.load_dump(language)
		combo_word = parser_shell.choose_from_alpha(wiki_dump,[],language)
		if combo_word == 'end' or combo_word == 'return to top' or combo_word == 'back':
			return None
		else:
			if len(combo_word['entries']) > 1:
				selection = word_print_edit.select_entry(combo_word['entries'],"Choose the definition you want to use:")
			else:
				selection = 0
			number = edit_entry.select_definition(combo_word['entries'][selection],"Choose the line you want to use:")
			definition = combo_word['entries'][selection]['senses'][number]['gloss']
			if selection == None:
				return None
			else:
				return definition
'''