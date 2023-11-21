

import pickle
import os
from unidecode import unidecode
from copy import deepcopy

from create_word import create_word
import word_methods
from word_print_edit import get_entry_string, edit_entries, word_combo
from get_selection import get_selection, clear_screen
import edit_dictionary
import load_dict
import tables
import unicodedata
import inspect
from pyfiglet import figlet_format

theme = '\u2624'
theme = "|"

def current_line_number():
    return inspect.currentframe().f_back.f_lineno

# ADD WORDS OPTIONS
# # # # # # # # # # #
def add_word_options(current_dict):
	tags = set()
	while(True):
		clear_screen()
		options = {'1':"\nWord Search Options:\n==================================\n>'1' word search\n",
			'2':">'2' to set tags\n",
			'3':">'3' to display current gloss\n",
			'4':">'4' to create word\n",
			't':">'T' for tables\n",
			'0':">'0' to exit ('00' to quit)\n"}
		if not tags:
			options['0'] += "** No tags selected **\n"
		else:
			options['0'] += f"* {', '.join(tags)} *\n"
		user_input = get_selection(options)
		if user_input == '0':
			return current_dict, False
		if user_input == '00':
			return current_dict, True
		if user_input == '1':
			current_dict = word_search(current_dict,tags)
			continue
		elif user_input.lower() == '2':
			master_list = word_methods.get_master_list(current_dict)
			tags = word_methods.getTags(tags,'',master_list)
			continue
		elif user_input.lower() == '3':
			tag_mode = '1' if tags == set() else '2'
			count = edit_dictionary.filter_gloss(current_dict,tags,output_file=None,tag_mode=tag_mode)
			print(f"\n\t{count} items with current tags\n")
			continue
		if user_input == '4':
			current_dict = create_word(current_dict,tags)
			continue
		elif user_input == 't':
			tables.table_options(current_dict['language'])
		else:
			current_dict = look_up_word(user_input,current_dict,tags)
# END ADD WORD OPTIONS


# WORD OPTIONS
# # # # # # # # # # # # # 
def word_options(new_word,current_dict,backup,existing_word,t):
	language = current_dict['language']
	handle = new_word['handle']
	heading = new_word['heading']
	entry_string = ''
	while True:
		entry_string = get_entry_string(new_word['entries'])
		if existing_word == True:

			options = {'0':f"\n===================================================\n{heading} already exists in '{current_dict['file']}'\n",
			'1':f"Do you want to save, edit or discard '{heading}'?\n",
			'2':">>>(1=save, 2=edit, 0=discard)"}
			#if 'template' not in new_word:
			#	options.update({'t':"'T' to add templates\n"})
			#else:
			#	options.update({'t':"\n"})
			options.update({'3':"'3' to see original wiktionary\n"})
		else:
			options = {
			'1':f"\n===================================================\nDo you want to save, edit or discard '{heading}'?\n",
			'2':">>>(1=save, 2=edit, 0=discard)"}
			#if 'template' not in new_word:
			#	options.update({'t':" 'T' to add templates\n"})
			#else:
			#	options.update({'t':"\n"})
			options.update({'0':''})
		user_input = get_selection(options,entry_string)

		if user_input == '0':
			return current_dict

		elif user_input.lower() == 't':
			tables.auto_template(current_dict,new_word)
			if 'template' in new_word:
				save_word(new_word,current_dict)
				
		elif user_input == '1':
			save_word(new_word,current_dict)
			return current_dict

		elif user_input == '2':
			clear_screen()
			new_word, finish_and_save = edit_entries(new_word,current_dict,t)
			if finish_and_save:
				save_word(new_word,current_dict)
				return current_dict

		elif user_input == '3':
			template = True if 'template' in new_word else False
			new_word['entries'] = backup['entries']
			if template:
				new_word['template'] = True
		clear_screen()
# END WORD OPTIONS

# SAVE WORD
# # # # # # # # # # # 
def save_word(new_word,current_dict,mode=1):
	if mode == 2:
		load_dict.change_path('dumps_sorted')
	else:
		load_dict.change_path('dictionaries')
	for i in range(len(current_dict['definitions'])):
		if current_dict['definitions'][i]['handle'] == new_word['handle']:
			current_dict['definitions'][i] = deepcopy(new_word)
			with open(current_dict['file'],mode = 'wb') as openFile:
				pickle.dump(current_dict, openFile)
			input(f"\n\"{new_word['heading']}\" was updated; press enter to continue")
			return current_dict	
	current_dict['definitions'].append(deepcopy(new_word))
	current_dict['definitions'].sort(key=lambda item: tables.replace_greek(item.get('handle').lower()))
	with open(current_dict['file'],mode = 'wb') as openFile:
		pickle.dump(current_dict, openFile)

	input(f"\n\"{new_word['heading']}\" was saved; press enter to continue")
	return current_dict
# END SAVE WORD


def load_dump(language):
	print(f"Loading {language}...")

	load_dict.change_path("dumps_sorted")
	with open(language.replace(" ","") + '-trie.txt','rb') as openFile:
		t = pickle.load(openFile)
	return t['definitions']


def word_search(current_dict,tags):

	t = load_dump(current_dict['language'])

	while True:
		""" Retrieve use selection from dictionary """ 
		result = choose_from_trie(t,current_dict['language'])
		clear_screen()

		""" 'end' will be returned is user choose to end querying """
		if result == None:
			return current_dict

		else:
			""" Test if selected word already exists in saved dictionary """
			existing_word = False
			backup = deepcopy(result)
			for i in range(len(current_dict['definitions'])):
				if current_dict['definitions'][i]['handle'] == result['handle']:
					existing_word = True
					result = deepcopy(current_dict['definitions'][i])
			result['tags'] = result['tags'] | tags
			current_dict = word_options(result,current_dict,backup,existing_word,t)

def center_text(text, total_width):
    padding_each_side = (total_width - len(text.split('\n')[0])) // 2
    lines = text.split('\n')
    centered_lines = [f"{theme} " * ((padding_each_side - 2)//2) + line + f" {theme}" * ( (padding_each_side + 2)//2) + f" {theme}" for line in lines if line != '']

    return '\n'.join(centered_lines)

def choose_from_trie(t,lang,debug_print=True):
	prefix = ''
	items = []
	empty = False
	while True:
		clear_screen()


		# print heading
		message = f"{theme} " * (75) + "\n"
		asci_art = lang.upper() + " WORD SEARCH"
		#if len(asci_art)%2 != 0:
		#	asci_art += "!"
		asci_art = figlet_format(asci_art,font='digital',width=150)
		asci_art = center_text(asci_art,150)
		message += asci_art + "\n"
		message += f"{theme} " * (75) 
		message += "\n" + " "*148 + theme
		message += "\n" + " "*148 + theme
		print(message)


		if items:
			print_word_list(items)

		if prefix:
			print(" " * 148 + theme)
			message = f"Current filter: {prefix}-"
			print("{:<148}".format(message) + theme)

		if empty:
			print(" " * 148 + theme)
			print("{:<148}".format("! No items found with this combination") + theme)
			print(" " * 148 + theme)
			empty = False


		print("{:<148}".format("Options:") + theme)

		if prefix:
			print("{:<148}".format("Enter a number to select definition") + theme)

		print("{:<148}".format("Enter a search word or partial word (add one or more trailing '*'s to limit characters)") + theme)
		message = "Enter '0' to go back, '00' to "
		if prefix:
			message += "clear, '000' to "
		message += "end"
		print("{:<148}".format(message) + theme)
		user_input = input(": ")

		if user_input == '':
			continue

		if user_input == '0':
			prefix = prefix[:-1]

		elif user_input == '00' and prefix:
			prefix = ''
			items = []
			if debug_print:
				print("\n" + theme * 15 + f"\n\nLINE: {current_line_number()}")
				print(f"Prefix == {prefix}")
				if prefix:
					print(f"Prefix != ''")
					exit()
			continue

		elif user_input == '00' or user_input == '000':
			return None

		elif user_input[0] == '0':
			prefix = user_input[1:]

		elif user_input.isnumeric():
			result = get_word(items,int(user_input))
			if result:
				return result
			else:
				continue
		else:
			prefix += user_input

		prefix = unidecode(prefix).lower()

		while not t.keys(prefix.replace('*','')):
			prefix = prefix.replace('*','')[:-1]

		if not prefix:
			items = []
			empty = True
			continue

		items = t.values(prefix.replace('*',''))
		items = flatten_sublists(items)

		if '*' in prefix:
			max_length = len(prefix) - 1
			items = [item for item in items if len(item['heading']) <= max_length]


			if not items:
				empty = True
				


def flatten_sublists(lst):
	i = 0
	while i < len(lst):
		while isinstance(lst[i], list):
			if not lst[i]:
				lst.pop(i)
				i -= 1
				break
			else:
				lst[i:i + 1] = lst[i]
		i += 1
	return lst

def get_word(items,user_input):
	i = user_input - 1
	if i in range(len(items)):
		return items[i]
	else:
		print("\n\t" + theme*3 + " Selection out of range " + theme*3 + "\n")
		return None

def visible_len(s):
    return len([c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'])

def print_word_list(items):
	clear_screen()

	# print heading
	print(f"{theme} " * 75)
	print(f"{theme} " * 33 + "SEARCH RESULTS " + f" {theme}" * 34)
	print(" " * 148 + theme)
	print(" " * 148 + theme)
	labels = ["      Headings:","Definitions:"]
	message = f"{labels[0]:<30}{labels[1]}"
	print("{:<148}".format(message) + theme)
	print(" " * 148 + theme)

	# Loop to create sub-list to select from
	for i in range(len(items)):

		if i >= 100:
			message = f"{theme} " * 29 + "Limit reached " + f"{theme} " * 29
			print("{:<148}".format(message) + theme)
			break

		# assign word to shorten name
		word = items[i]

		# Create and print formatted string
		message = ''
		for j in range(len(word['entries'])):
			if j == 0:
				entry_string = f"{i + 1:>6}.  {word['heading']}:"
				# print with desired alignment
				#print(f"{entry_string:<30}",end='')
			else:
				entry_string = f"{i + 1:>6}{chr(j + 97)}. {word['heading']}:"
			message += f"{entry_string:<30}"
				# print with desired alignment
				#print(f"{entry_string:<30}",end='')				

			text = word['entries'][j]['senses']
			if len(text) == 1:
				entry_len = len(text[0]['gloss'])
				entry_string = text[0]['gloss']
			else:
				entry_len = sum([len(f"0) " + text[i]['gloss'] + "  ") for i in range(len(text))])
				entry_string = ''
				for line in [f"{i + 1}) " + text[i]['gloss'] + "  " for i in range(len(text))]:
					entry_string += line
			entry_string = entry_string[:100]

			# if over length attach elipses
			if entry_len > 100:
				entry_string = entry_string[:-3]
				entry_string += "..."
			message += f"{entry_string}"
			while visible_len(message) < 148:
				message += " "
			print(message + theme)
			message = ''

		
