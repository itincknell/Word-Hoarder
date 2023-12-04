'''
This is the main module for interacting with sorted language dictionaries.
Allows user to look up words, edit and add them to user dictionaries.
'''

import pickle
import os
from unidecode import unidecode
from copy import deepcopy
import unicodedata
import inspect
from pyfiglet import figlet_format

from create_word import create_word
import word_methods
from word_print_edit import get_entry_string, edit_entries, word_combo
from get_selection import get_selection, clear_screen
import edit_dictionary
from load_dict import change_path, SORTED_LANGUAGE_FILES, USER_CREATED_DICTIONARIES
import tables


# character used to put box around search display
theme = "|"

def current_line_number():
    return inspect.currentframe().f_back.f_lineno

# ADD WORDS OPTIONS
# # # # # # # # # # #
def add_word_options(current_dict):
	'''	user options for interacting with sorted language file and
		adding words to customized user dictionary.
	'''
	# TODO: definition tags is a set() in some places and a list in others
	tags = set()

	while True:
		clear_screen()

		# create user options
		options = {'1':"\nWord Search Options:\n==================================\n>'1' word search\n",
			'2':">'2' to set tags\n",
			'3':">'3' to display current gloss\n",
			'4':">'4' to create word\n",
			't':">'T' for tables\n",
			'0':">'0' to exit ('00' to quit)\n"}

		# indicate current tags or none; these will be added to each word
		# that is saved (including updates of previously saved words)
		# Avoids user having to remember to tag each word. The assumption
		# is that the user will want to apply some common tags to all words
		# in a given session.
		if not tags:
			options['0'] += "** No tags selected **\n"
		else:
			options['0'] += f"* {', '.join(tags)} *\n"

		# ensure user makes a valid selection
		user_input = get_selection(options)

		# options to exit or quit program completely
		if user_input == '0':
			return current_dict, False
		if user_input == '00':
			return current_dict, True

		# option to interact with sorted language file
		if user_input == '1':
			current_dict = word_search(current_dict,tags)
			continue

		# option to set session tags
		elif user_input.lower() == '2':
			master_list = word_methods.get_master_list(current_dict)
			tags = word_methods.getTags(tags,'',master_list)
			continue

		# option to pretty print all words in current dictionary that match
		# current session tags.
		elif user_input.lower() == '3':
			tag_mode = '1' if tags == set() else '2'
			count = edit_dictionary.filter_gloss(current_dict,tags,output_file=None,tag_mode=tag_mode)
			print(f"\n\t{count} items with current tags\n")
			continue

		# option to create a new word (if word was not found in sorted language file)
		if user_input == '4':
			current_dict = create_word(current_dict,tags)
			continue

		# option for 'morphology table' functionality
		# See readme and tables.py
		elif user_input == 't':
			tables.table_options(current_dict['language'])
# END ADD WORD OPTIONS


# WORD OPTIONS
# # # # # # # # # # # # # 
def word_options(new_word,current_dict,backup,existing_word,t):
	''' User options for iteracting with a word retreived from 
		sorted language files.
	'''

	# for brevity
	heading = new_word['heading']

	while True:
		# get formatted string; may change between loop iterations
		entry_string = get_entry_string(new_word['entries'])

		# create user options

		
		if existing_word:
			# display different message if word already exists in current dictionary
			options = {'0':f"\n===================================================\n"\
			+ f"{heading} already exists in '{current_dict['file']}'\n",
			'1':f"Do you want to save, edit or discard '{heading}'?\n"}
		else:
			# standard message for new words
			options = {
			'1':f"\n===================================================\n"\
			+ f"Do you want to save, edit or discard '{heading}'?\n"}
			options.update({'2':">>>(1=save, 2=edit, 0=discard)"})

		# option to create a morphology flashcard template file
		# and indicate that the table exists for future reference.
		# currently disabled to avoid cluttering user options.
		'''
		if 'template' not in new_word:
			options.update({'t':" 'T' to add templates\n"})
		else:
			options.update({'t':"\n"})
		'''

		# option to revert to unmodified definition from the sorted 
		# language file for existing words
		if existing_word:
			options.update({'3':"'3' to see original wiktionary\n"})
		else:
			options.update({'0':''})

		# validate user selection
		user_input = get_selection(options,entry_string)

		# option to go back
		if user_input == '0':
			return current_dict

		# disabled option to create morphology flaschard template
		elif user_input.lower() == 't':
			tables.auto_template(current_dict,new_word)
			if 'template' in new_word:
				save_word(new_word,current_dict)

		# saved the word to current dictionary
		elif user_input == '1':
			save_word(new_word,current_dict)
			return current_dict

		# edit the definition
		elif user_input == '2':
			clear_screen()
			new_word, finish_and_save = edit_entries(new_word,current_dict,t)
			if finish_and_save:
				save_word(new_word,current_dict)
				return current_dict

		# option to revert to original umodified definition
		elif user_input == '3':
			# should preserve 'template' tag after reverting
			template = True if 'template' in new_word else False
			new_word['entries'] = backup['entries']
			if template:
				new_word['template'] = True
		clear_screen()
# END WORD OPTIONS

# SAVE WORD
# # # # # # # # # # # 
def save_word(new_word,current_dict,mode=1):
	'''	Add new_word to current_dict and saves updated current_dict
		object to a file using pickle.dump method
	'''

	# not sure why this option is here
	# SORTED_LANGUAGE_FILES should not be modified
	if mode == 2:
		change_path(SORTED_LANGUAGE_FILES)
	else:
		change_path(USER_CREATED_DICTIONARIES)
	
	# update the existing entry for the word by matching the handle
	for i in range(len(current_dict['definitions'])):
		if current_dict['definitions'][i]['handle'] == new_word['handle']:

			# once the correct entry if found, overwrite the entry
			current_dict['definitions'][i] = deepcopy(new_word)

			# pickle.dump current_dict to file
			with open(current_dict['file'],mode = 'wb') as openFile:
				pickle.dump(current_dict, openFile)

			# announce success and return
			input(f"\n\"{new_word['heading']}\" was updated; press enter to continue")
			return current_dict	

	# existing entry not found: append and sort
	current_dict['definitions'].append(deepcopy(new_word))
	current_dict['definitions'].sort(key=lambda item: tables.replace_greek(item.get('handle').lower()))

	# pickle.dump current_dict to file
	with open(current_dict['file'],mode = 'wb') as openFile:
		pickle.dump(current_dict, openFile)

	# announce success and return
	input(f"\n\"{new_word['heading']}\" was saved; press enter to continue")
	return current_dict
# END SAVE WORD


def load_sorted_language(language):
	'''	load datrie object from SORTED_LANGUAGE_FILES
	'''

	# loading may take several seconds for Latin
	print(f"Loading {language}...")

	change_path(SORTED_LANGUAGE_FILES)
	with open(language.replace(" ","") + '-trie.txt','rb') as openFile:
		t = pickle.load(openFile)
	return t['definitions']


def word_search(current_dict,tags):
	'''	Call and handle returns from choose_from_trie function
	'''

	# load datrie containing sorted language
	t = load_sorted_language(current_dict['language'])

	while True:
		# Retrieve use selection from dictionary 
		result = choose_from_trie(t,current_dict['language'])
		clear_screen()

		# 'end' will be returned is user choose to end querying
		if result == None:
			return current_dict

		else:
			# Test if selected word already exists in saved dictionary
			existing_word = False

			# save a back up of unmodified definition from sorted language file
			backup = deepcopy(result)

			# find a matching entry in current_dict if one exists
			for i in range(len(current_dict['definitions'])):
				if current_dict['definitions'][i]['handle'] == result['handle']:
					existing_word = True
					result = deepcopy(current_dict['definitions'][i])

			# add current session tags to result
			result['tags'] = result['tags'] | tags

			# go to options for selected word
			current_dict = word_options(result,current_dict,backup,existing_word,t)

def center_text(text, total_width):
	'''	Display text with equal amount of filler character 'theme' on both sides
	'''
	padding_each_side = (total_width - len(text.split('\n')[0])) // 2
	lines = text.split('\n')
	centered_lines = [f"{theme} " * ((padding_each_side - 2)//2) \
		+ line + f" {theme}" * ( (padding_each_side + 2)//2)\
		+ f" {theme}" for line in lines if line != '']

	return '\n'.join(centered_lines)

def choose_from_trie(t,lang,debug_print=True):
	''' Displays search window. Retreives words matching user search string
		from datrie and prompts user selection from matching words.
	'''
	# user search string
	prefix = ''

	# collector for matching words
	items = []

	# flag when search turns up no results
	empty = False

	while True:
		clear_screen()

		# print heading
		message = f"{theme} " * (75) + "\n"
		asci_art = lang.upper() + " WORD SEARCH"
		asci_art = figlet_format(asci_art,font='digital',width=150)
		asci_art = center_text(asci_art,150)
		message += asci_art + "\n"
		message += f"{theme} " * (75) 
		message += "\n" + " "*148 + theme
		message += "\n" + " "*148 + theme
		print(message)

		# display matching items, if any
		if items:
			print_word_list(items)

		# display current search string
		if prefix:
			print(" " * 148 + theme)
			message = f"Current filter: {prefix}-"
			print("{:<148}".format(message) + theme)

		# notify user the search string did not have any matches
		if empty:
			print(" " * 148 + theme)
			print("{:<148}".format("! No items found with this combination") + theme)
			print(" " * 148 + theme)
			empty = False

		# Display options menu
		print("{:<148}".format("Options:") + theme)

		# If options are visible, prompt user to choose a definition
		if prefix:
			print("{:<148}".format("Enter a number to select definition") + theme)

		# prompt user to enter a search string, 
		# instructions for how to limit the length of matching
		print("{:<148}".format("Enter a search word or partial word (add one or more trailing '*'s to limit characters)") + theme)

		# options to clear search string or quit
		message = "Enter '0' to go back, '00' to "
		if prefix:
			message += "clear, '000' to "
		message += "end"

		# display message and wait for user input
		print("{:<148}".format(message) + theme)
		user_input = input(": ")

		# validate user has input some value
		if user_input == '':
			continue

		# 'go back' means remove last letter from search string
		if user_input == '0':
			prefix = prefix[:-1]

		# option to clear search string
		elif user_input == '00' and prefix:
			prefix = ''
			items = []
			continue

		# option to quit
		elif user_input == '00' or user_input == '000':
			return None

		# invisible option: entry with a leading 0 will overwrite previous search string
		elif user_input[0] == '0':
			prefix = user_input[1:]

		# if nummeric value, user wants to select a word from search results
		elif user_input.isnumeric():
			# more data validation inside get_word
			result = get_word(items,int(user_input))

			# a valid selection was made
			if result:
				return result
			else:
				continue

		# if none of the above apply, add user input to search string
		else:
			prefix += user_input

		# if user is using a greek keyboard, the input must be converted to 
		# asci before querying the trie
		prefix = unidecode(prefix).lower()

		# find the longest search string the matches a key in the trie
		while not t.keys(prefix.replace('*','')):
			prefix = prefix.replace('*','')[:-1]

		# indicates no matches
		if not prefix:
			items = []
			empty = True
			continue

		# get matching definition nodes as list
		items = t.values(prefix.replace('*',''))

		# find nodes containing multiple distinct definitions 
		# and split them into multiple list items so that items 
		# is a homogenous list of definition objects
		items = flatten_sublists(items)

		# if trailing '*'s user want to limit the length of words returned
		if '*' in prefix:
			# one '*' indicates exact match of length, multiple indicate within 1, 2 etc.
			max_length = len(prefix) - 1

			# eliminate overlength items from list
			items = [item for item in items if len(item['heading']) <= max_length]

			# if no items fit the maximum length
			if not items:
				empty = True


def flatten_sublists(lst):
	'''	Remove sublists in items
	'''
	i = 0
	# could use for loop here
	while i < len(lst):
		# If list encountered, stay on item until list is empty
		while isinstance(lst[i], list):
			# pop empty list
			if not lst[i]:
				lst.pop(i)
				i -= 1
				break
			# Extend the main list with the elements of the sublist
			else:
				lst[i:i + 1] = lst[i]
		i += 1
	return lst

def get_word(items,user_input):
	'''	valide user selection and return selected word
	'''
	i = user_input - 1
	if i in range(len(items)):
		return items[i]
	else:
		print("\n\t" + theme*3 + " Selection out of range " + theme*3 + "\n")
		return None

def visible_len(s):
    return len([c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'])

def print_word_list(items):
	'''	Print search results in number list with consisted padding
	'''
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

			# print single entry words with just a number
			if j == 0:
				entry_string = f"{i + 1:>6}.  {word['heading']}:"

			# print multiple entry words with number-letter indices
			else:
				entry_string = f"{i + 1:>6}{chr(j + 97)}. {word['heading']}:"

			# add padding to entry string
			message += f"{entry_string:<30}"		

			# add preview of top word senses
			text = word['entries'][j]['senses']

			# word contains a single sense
			if len(text) == 1:
				entry_len = len(text[0]['gloss'])
				entry_string = text[0]['gloss']

			# if word contains multiple senses
			else:
				entry_len = sum([len(f"0) " + text[i]['gloss'] + "  ") for i in range(len(text))])
				entry_string = ''
				for line in [f"{i + 1}) " + text[i]['gloss'] + "  " for i in range(len(text))]:
					entry_string += line

			# limit to 100 chars
			entry_string = entry_string[:100]

			# if over length attach elipses
			if entry_len > 100:
				entry_string = entry_string[:-3]
				entry_string += "..."

			message += f"{entry_string}"

			# ensure correct padding for all alphabets
			while visible_len(message) < 148:
				message += " "

			# print and reset message
			print(message + theme)
			message = ''

		
