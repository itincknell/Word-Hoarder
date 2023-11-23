
import json
import sys
import copy
import pickle
import os
import glob
from math import ceil
from unidecode import unidecode
import difflib

import parser_shell
from load_dict import change_path, pick_language
import edit_all
from get_selection import get_selection
from language_splitter import split_language
from tables import replace_greek, replace_greek_ii


progress_print = True
Test = False

def debug_print(Test, *args):
	"""Print messages if Test is True."""
	if Test:
		print(*args)

def similar_enough(item, tag):
	"""Compare two strings and return a boolean indicating if they are similar enough."""
	s = difflib.SequenceMatcher(None, item, tag)
	ratio = s.quick_ratio()
	return ratio >= .5

def filter_tags(gloss_parts, existing_tags, Test):
	"""Filter existing tags by comparing them to the gloss_parts."""
	new_tags = existing_tags.copy()
	for tag in existing_tags:
		gloss_parts = [part for part in gloss_parts if not similar_enough(part, tag)]
		if any(similar_enough(part, tag) for part in gloss_parts):
			new_tags.remove(tag)
	return new_tags, gloss_parts

def paren_cut(gloss, tags):

	if gloss[0] != "(":
		return gloss, tags

	gloss_parts = gloss[1:gloss.find(")")].split(", ")
	remaining_gloss = gloss[gloss.find(")") + 2:]

	debug_print(Test, f"g = {gloss_parts}", f"gloss = {remaining_gloss}", f"split g = {gloss_parts}", f"tags = {tags}")

	new_tags, gloss_parts = filter_tags(gloss_parts, tags, Test)

	if len(gloss_parts) == 0:
		return remaining_gloss, new_tags
	else:
		return "(" + ", ".join(gloss_parts) + ") " + remaining_gloss, new_tags



def add_def(senses,new_gloss,gloss_tags):
	if ")" in new_gloss:
		for d in senses:
			if new_gloss[new_gloss.find(")") + 2:] == d['gloss']:
				d['gloss'] = new_gloss
				for tag in gloss_tags:
					if tag not in d['tags']:
						d['tags'].append(tag)
				d['gloss'], d['tags'] = paren_cut(d['gloss'],d['tags'])
			return

	if ":" in new_gloss:
		for d in senses:
			if ":" in d['gloss'] and new_gloss[:new_gloss.find(':')] == d['gloss'][:d['gloss'].find(':')]:
				if new_gloss[new_gloss.find(':') + 2:].isspace() or not new_gloss[new_gloss.find(':') + 2:]:
					return
				elif new_gloss[new_gloss.find(':') + 2:] == d['gloss'][d['gloss'].find(':') + 2:]:
					return
	if new_gloss:
		senses.append({'gloss':new_gloss,'tags':copy.deepcopy(gloss_tags)})

def create_senses(line_senses, tag_list):
	senses = []
	dupe_list = []

	def process_glosses(glosses, gloss_tags):
		for gloss in glosses:
			new_gloss = gloss.strip(". ")
			split_gloss = new_gloss.split('\n##') if '\n##' in new_gloss else [new_gloss]
			
			# Apply the loop only if we have split the gloss
			if len(split_gloss) > 1:
				for i in range(1, len(split_gloss)):
					new_gloss, gloss_tags = paren_cut(split_gloss[0] + split_gloss[i], gloss_tags)
					if new_gloss not in dupe_list:
						add_def(senses, new_gloss, gloss_tags)
						dupe_list.append(new_gloss)
			else:
				new_gloss, gloss_tags = paren_cut(new_gloss, gloss_tags)
				if new_gloss not in dupe_list:
					add_def(senses, new_gloss, gloss_tags)
					dupe_list.append(new_gloss)
					
		return gloss_tags

	for sense in line_senses:
		gloss_tags = []
		if 'form_of' in sense:
			gloss_tags.append('form of ' + sense['form_of'][0]['word'])

		if 'tags' in sense:
			gloss_tags.extend([tag for tag in sense['tags'] if tag not in tag_list])

		if 'english' in sense and sense['english'] not in tag_list:
			gloss_tags.append(sense['english'])

		if 'qualifier' in sense and sense['qualifier'] not in tag_list:
			gloss_tags.append(sense['qualifier'])

		if 'glosses' in sense:
			gloss_tags = process_glosses([sense['glosses'][0].strip(". ")], gloss_tags)

		if 'raw_glosses' in sense:
			gloss_tags = process_glosses(sense['raw_glosses'], gloss_tags)

		if Test:
			print(f"dupe_list = {dupe_list}")

	if Test:
		print(f"senses: {senses}")
	return senses

def get_file_selection(Test, test_file, test_language):
	change_path('dumps_unsorted')
	if Test:
		return test_file, test_language
	else:
		myFiles = glob.glob('*.json')
		if myFiles == []:
			print("\nSorry no saved dictionaries")
			return None, None
		else:
			options = {'0':f"\nChoose from the following files: (0 to go back)\n"}
			for index in range(len(myFiles)):
				options[f"{str(index + 1)}"] = f"{index + 1}. {myFiles[index]}\n"
			user_input = get_selection(options)

			if user_input == '0':
				return None, None
			else:
				file = myFiles[int(user_input)-1]
			language = pick_language()
		return file, language

def print_debug_info(line, counter):
	print('\n')
	print(f"\tline: {counter}, word: {line['word']}")
	print("WORD ITEMS >>>>>>>>>>>>>>")
	for item in line.items():
		print(item)
	print("SENSES ITEMS >>>>>>>>>>>>")
	for item in line['senses'][0].items():
		print(item)

def handle_pos(line):
	pos_mapping = {
		'adv': 'adverb',
		'adj': 'adjective',
		'prep': 'preposition',
		'intj': 'interjection'
	}

	pos = line['pos']
	line['pos'] = pos_mapping.get(pos, pos)
	return line['pos']

def handle_senses(line,tag_list):
	if 'tags' in line['senses'][0]:
		tag = line['senses'][0]['tags']
		if 'no-senses' in tag or 'no-gloss' in tag or 'empty-gloss' in tag:
			if isinstance(tag,list):
				return [{'gloss': ", ".join(tag), 'tags': []}]
			else:
				return [{'gloss': tag, 'tags': []}]
		else:
			return create_senses(line['senses'], tag_list)
	else:
		return create_senses(line['senses'], tag_list)

def handle_etymology(line):
	if 'etymology_text' in line:
		return line['etymology_text']
	else:
		return ''

def handle_parts(line,get_simple=None):
	if get_simple:
		return get_simple(line['pos'], line['head_templates'][0]['expansion'], line['word']) if 'head_templates' in line else line['word']
	else:
		return line['head_templates'][0]['expansion'] if 'head_templates' in line else line['word']


def handle_word_entry(line,tag_list,get_simple=None):
	return {
		'partOfSpeech': handle_pos(line),
		'principleParts': line['head_templates'][0]['expansion'] if 'head_templates' in line else line['word'],
		'simpleParts': handle_parts(line,get_simple),
		'senses': handle_senses(line, tag_list),
		'etymology': handle_etymology(line)
	}



def handle_word(line,tag_list,language,get_simple=None):
	return {
		'heading': line['word'],
		'handle': unidecode(line['word']) if language in ["Latin", "Italian"] else line['word'],
		'entries': [handle_word_entry(line, tag_list,get_simple)],
		'tags': set(),
		'roots': [line['senses'][0][root_type][0]['word'] for root_type in ['alt_of', 'form_of'] if root_type in line['senses'][0]]
	}

def ui_template(new_dictionary,dict_str,shrt_str,cite,cite_2='',dict_f=""):
	user_input = input(f"\nAdd definitiions from: \"{dict_str}\"?"\
		+ "\nType 'y' to add definitions, Press 'Enter' to continue: " )
		
	if user_input.lower() == 'y':
		user_input = '0'
		new_dictionary = dict_f(new_dictionary)

		new_dictionary = edit_all.deduplicate(new_dictionary)
		n = len(new_dictionary['definitions'])
		thank(dict_str,shrt_str,n,cite)

def thank(dict_str,shrt_str,length,cite,cite_2='',dict_f=""):
	print(f"\nYour dictionary now contains ( {length:,} ) unique definitions after adding {shrt_str}.")
	print(f"Data files courtesy of {cite}.",end='')
	if cite_2:
		i = input(f"\nType 'i' for more info, Press 'Enter' to continue: ")
		if i.lower() == 'i':
			print(f"\n{cite_2}")
			input(f"Press 'Enter' to continue ")
	else:
		input(f"\n(Press 'Enter' to continue)")

def parse_lines(input_file,tag_list,language,get_simple=None):
	definitions_dict = {}
	counter = 0
	for line in input_file:

		# sort line into Word-Hoarder definition structure
		line = json.loads(line)
		new_definition = handle_word(line, tag_list,language,get_simple)

		# combine synomyns
		if new_definition['heading'] in definitions_dict:
			definitions_dict[new_definition['heading']]['entries'].extend(new_definition['entries'])
		else:
			definitions_dict[new_definition['heading']] = new_definition

		# show progress bar
		counter += 1
		if progress_print or Test:
			if counter % 1000 == 0:
				print(".",end='',flush=True)
			if counter % 100000 == 0:
				print(f' {counter:,} lines parsed',flush=True)
		if Test:
			print_debug_info(line,counter)

	input_file.close()

	print(f' {counter:,} lines parsed',flush=True)
	print("De-duplicating definitions...")

	# convert dict values to list
	definitions = list(definitions_dict.values())

	dict_str = f"{language} Wiktionary"
	shrt_str = f"{language} Wiktionary"
	cite = "Tatu Ylonen, see kaikki.org for more information"
	cite_2 = "Tatu Ylonen: Wiktextract: Wiktionary as Machine-Readable Structured Data, Proceedings of the 13th Conference on Language Resources and Evaluation (LREC), pp. 1317-1325, Marseille, 20-25 June 2022."
	n = len(definitions)
	thank(dict_str,shrt_str,n,cite,cite_2)
	return definitions

# duplicate of a function found in tables.py
'''
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
'''

def sort_dump():

	print_mode = Test
	save_mode = not Test
	test_language = 'Ancient Greek'
	test_file = "kaikki.org-dictionary-AncientGreek.json"

	# Load list of tags that are not descriptive/overly general
	try:
		change_path('texts')
		with open('ignore_tags.txt','r') as f:
			tag_list = json.load(f)
	except FileNotFoundError:
		print("'ignore_tags.txt' not found in 'texts' directory.")
		input("Enter to continue")
		tag_list = []

	# choose language option, create kaikki.org file string
	language = pick_language()
	file = "kaikki.org-dictionary-" + language.replace(' ','') + ".json"

	# this module loads a '-trie.txt' file which can take a few seconds, should be avoided if lanugage != Latin
	if language == "Latin":
		from get_simple import get_simple
		simple = get_simple
	else:
		simple = None

	sorted_file = language.replace(" ", '') + "Dump.txt"
	new_dictionary = {'definitions':[], 'file': sorted_file, 'language':language}

	print(f"Parsing {file}")
	
	# attempt to parse kaikki.org json file
	change_path('dumps_unsorted')
	try:
		with open(file, 'r') as input_file:
			new_dictionary['definitions'] = parse_lines(input_file, tag_list,language,simple)

		# save a list of all tags that were encountered
		change_path('texts')
		with open(language + '_new_tag_list.txt', mode='w') as f:
			json.dump(tag_list, f)
	except FileNotFoundError:
		print(f"'{file}' not found in 'dumps_unsorted' directory")
		input("Enter to continue")
		return

	# Latin fixes
	if new_dictionary['language'] == 'Latin':
		if progress_print:
			print(f"Fixing participles...")
		new_dictionary = edit_all.fix_participles(new_dictionary)
		if progress_print:
			print(f"Fixing verbs...")
		new_dictionary = edit_all.fix_verbs(new_dictionary)
	if progress_print:
		print(f"Fixing etymologies...")
	new_dictionary = edit_all.fix_etymology(new_dictionary)
	
	# Greek Supplement
	if new_dictionary['language'] == "Ancient Greek":
	
		dict_str = ["Liddell & Scott, An Intermediate Greek-English Lexicon","Liddell & Scott, A Greek-English Lexicon (LSJ)"]
		shrt_str = ["\"Middle\" Liddell",'\"LSJ\"']
		cite = "Tufts University Perseus Digital Library"
		cite_2=''
		from dictionary_Middle_Liddell import middle_liddell
		from dictionary_LSJ import LSJ
		dict_f = [middle_liddell,LSJ]

		for i in range(2):
			ui_template(new_dictionary,dict_str[i],shrt_str[i],cite,cite_2,dict_f[i])

	# Old English Supplement
	if new_dictionary['language'] == "Old English":
		dict_str = "Mary Lynch Johnson, A Modern English - Old English Dictionary"
		shrt_str = "M.L. Johnson OE Dictionary"
		cite = "Richard Zimmermann, https://old-engli.sh/dictionary.php"
		cite_2=''
		from dictionary_MLJohnson import Johnson_OED
		ui_template(new_dictionary,dict_str,shrt_str,cite,cite_2,Johnson_OED)	

	# Last few sections may leave CWD == 'texts', change to 'dumps_sorted'
	change_path('dumps_sorted')

	# sort by handle string
	new_dictionary['definitions'].sort(key=lambda item: item.get('handle').lower())

	# sort definitions list into trie
	print("Converting dictionary to trie")
	split_language(new_dictionary)
	input("Extraction successful, press enter to continue")
	return


if Test:
	sort_dump()





