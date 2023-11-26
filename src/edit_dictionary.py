'''
Description:

	edit_dictionary:
		options to route control to different functions within this file

	word_look_up:
		the function searches for a word input within the current dictionary
		if found, send the word and current dictionary to existing_entry_options

	word list:
		print a list of all entries (or filtered by tags) 
		user selection is sent to existing_enntry_options

	print_dict:
		print the dictionary or a subset of tags to a file
'''
import glob
import os
import sys
import pickle
from unidecode import unidecode
import re

import word_print_edit
import parser_shell
import word_methods
import get_selection
import edit_all
from load_dict import change_path, USER_CREATED_DICTIONARIES, FORMATTED_FLASHCARD_FILES
from edit_entry import pretty_print_tags

# EDIT DICTIONARY
# # # # # # # # # # # # 
def edit_dictionary(current_dict):
	'''	This is a user menu for editing either inidividual definitions or
		the entire current user dictionary (using the edit_all module)	
	'''
	while True:

		# dictionary options
		options = {
		'1':"\nEdit Dictionary Options:\n==================================\n>'1' to look up words by name\n",
		'2':">'2' to select from all entries\n",
		'3':">'3' for edit all options\n",
		'tags':">'tags' to select from a subset by tag\n",
		'0':">'0' to go back\n"
		}
		user_input = get_selection.get_selection(options)

		# options to go back
		if user_input == '0':
			return current_dict

		elif user_input == '1':
			current_dict = word_look_up(current_dict)


		# Option to set tags
		elif user_input.lower() == 'tags':
			master_list = word_methods.get_master_list(current_dict)
			tags = word_methods.getTags([],'filter',master_list)
			user_input = '2'
		else:
			tags = []

			# Proceed to next step
		if user_input == '2':
			current_dict = word_list(current_dict, tags)

		if user_input == '3':
			current_dict = edit_all.edit_all(current_dict)
# END EDIT DICTIONARY


# WORD LOOK UP
# # # # # # # # # # # # # # # # # # # 
def word_look_up(current_dict,look_up_word=None):
	'''	Functionality to look-up a word by searching
	'''
	while True:
		# set/reset flag
		word_found = False
		if not look_up_word:
			# prompt user to input word
			print("Enter the word you want to look up ('0' to go back)")
			user_input = input(": ")
		else:
			user_input = look_up_word

		# option to go back
		if user_input == '0':
			return current_dict
		else:
			# compare with handles in current dictionary
			for word in current_dict['definitions']:
				if user_input == word['handle']:
					word_found = True
					print(f"\nEntry for '{user_input}' found in {current_dict['file']}")
					word_print_edit.print_entries(word['entries'])
					current_dict = existing_word_options(current_dict,word)	
		if look_up_word:
			invalid_selection = not word_found
			return current_dict, invalid_selection			
		if not word_found:
			print(f"\n\t'{user_input}' not found in {current_dict['file']}\n")

# END WORD LOOK UP

def subset_test(tags,word_tags):
	'''	Utility function to test if tags argument is a subset of word_tags argument
	'''
	result = True
	for i in tags:
		if i not in word_tags:
			result = False
	return result


# WORD LIST
# # # # # # # # # # # # # # 
def word_list(current_dict,tags):
	'''	Functionality to selected a definition from a (possibly very long) 
		number list of the user's current dictionary
	'''

	invalid_selection = False
	while True:

		counter = 0
		sublist = []

		# Print heading for dictionary entries display
		print(f"\n{current_dict['file']}\n")
		labels = ["     Headings:","Parts:","Definitions:"]
		print(f"{labels[0]:<25}{labels[1]:<55}{labels[2]}\n")

		# Loop to create sub-list to select from
		for index in range(len(current_dict['definitions'])):

			# assign word to shorten name
			word = current_dict['definitions'][index]

			# test if tags match; always 'yes' for empty tags

			if subset_test(tags,word['tags']):

				# Create and print formatted string
				entry_string = f"{counter + 1:>3}. {word['heading']}:"
				# print with desired alignment
				print(f"{entry_string:<25}",end='')

				# check if part exceeds desired length
				entry_len = len(word['entries'][0]['simpleParts'])
				entry_string = f"{word['entries'][0]['simpleParts'][:50]}"

				# if over length attach elipses
				if entry_len > 50:
					entry_string = entry_string[:-3]
					entry_string += "..."
				# print with desired alignment
				print(f"{entry_string:<55}", end='')

				# check if definition exceeds desired length
				entry_len = len(word['entries'][0]['senses'][0]['gloss'])
				entry_string = f"{word['entries'][0]['senses'][0]['gloss'][:50]}"

				# if over length attach elipses
				if entry_len > 50:
					entry_string = entry_string[:-3]
					entry_string += "..."
				print(f"{entry_string}")
				
				# save word as a dictionary entry with index values
				sublist.append({'word':word})
				sublist[counter]['index'] = index
				counter += 1

		# if sublist is empty
		if counter == 0:
			print("\nno definitions found with these tags")
			return current_dict

		if invalid_selection:
			print("\ninvalid selection\n")
		invalid_selection = False

		# prompt selection
		print("Select definition ('0' to go back)")
		user_input = input(": ")

		# Option to go back to edit dictionary
		if user_input == '0':
			return current_dict
		# validate selection is numeric
		if not user_input.isnumeric():
			current_dict, invalid_selection = word_look_up(current_dict,user_input)
		else:
			# validate selection is in range
			if int(user_input) - 1 not in range(len(sublist)):
				invalid_selection = True
			else:
				# assign saved index from sublist
				i = sublist[int(user_input) - 1]['index']
				word = current_dict['definitions'][i]
				current_dict = existing_word_options(current_dict,word)
# END WORD LIST


# EXISTING WORD OPTIONS
# # # # # # # # # # # # # # # # # # # 
def existing_word_options(current_dict,word):
	'''	Options once a word has been selected are
		Delete, Edit, re-look-up the word, or split 
		the word entries between multiple definitions
	'''
	# Set directory 
	change_path(USER_CREATED_DICTIONARIES)

	# whole function contained in loop
	while True:

		# retreive heading from sublist
		heading = word['heading']
		# display options
		options = {
		'α':"Options:\n",
		'1':f">'1' to Edit '{heading}'\n",
		'2':f">'2' to Delete '{heading}'\n",
		'3':f">'3' look-up '{heading}'\n",
		'4':f">'4' split word\n",
		'0':">'0' to go back\n"
		}
		user_input = get_selection.get_selection(options)

		# Option to go back
		if user_input == '0':
			return current_dict

		# Option to edit
		elif user_input == '1':
			# call edit word
			language = current_dict['language']
			word, result = word_print_edit.edit_entries(word,current_dict)
			parser_shell.save_word(word,current_dict)

			# back to calling function
			return current_dict

		# Option to delete word
		elif user_input == '2':
			# confirm deletion request
			print(f"Delete {heading}?\n'1' to confirm, any other key to cancel")
			user_input = input(": ")

			if user_input == '1':
				# retrieve correct index from sublist
				for i in range(len(current_dict['definitions'])):
					if heading == current_dict['definitions'][i]['heading']:
						del current_dict['definitions'][i]
						break

				# Open file an save dictionary after deleting
				openFile = open(current_dict['file'],mode = 'wb')
				pickle.dump(current_dict, openFile)
				openFile.close()				

				# announce word was deleted
				print(f"\n'{heading}' deleted from {current_dict['file']}\n")
				# back calling function
				return current_dict
		elif user_input == '3':
			parser_shell.look_up_word(heading,current_dict,word['tags'],skip_check=True)
			return current_dict

		elif user_input == '4':
			word_print_edit.split_word(word,current_dict)
			return current_dict
# END EXISTING WORD OPTIONS

def pos_test_latin_definitions(definition,pos):
	'''	Utility function for dividing flashcard sets by partOfSpeech
		Returns false if no entry has the correct partOfSpeech
	'''
	for entry in definition['entries']:
		if pos_test_latin_entries(entry['partOfSpeech'],pos):
			return True
	return False

def pos_test_latin_entries(entry_pos,pos):
	'''	Utility function for dividing flashcard sets by partOfSpeech
		Returns True only if the entry argument has the correct 
		partOfSpeech
	'''
	if pos == 'adjective':
		if entry_pos == 'adjective' or entry_pos == 'participle':
			return True
		else:
			return False
	elif pos == 'noun': 
		if entry_pos == 'noun' or entry_pos == 'name' or entry_pos.lower() == 'proper noun' :
			return True
		else:
			return False
	elif pos == 'verb':
		if entry_pos == 'verb':
			return True
		else:
			return False
	elif pos == 'other':
		if entry_pos == 'adjective' or entry_pos == 'participle' or entry_pos == 'noun' or entry_pos == 'verb':
			return False
		else:
			return True

def pos_test_greek_definitions(definition,pos):
	'''	Utility function for dividing flashcard sets by partOfSpeech
		Returns false if no entry has the correct partOfSpeech
	'''
	for entry in definition['entries']:
		if pos_test_greek_entries(entry['partOfSpeech'],pos):
			return True
	return False

def pos_test_greek_entries(entry_pos,pos):
	'''	Utility function for dividing flashcard sets by partOfSpeech
		Returns True only if the entry argument has the correct 
		partOfSpeech
	'''
	if pos == 'verb':
		if entry_pos == 'verb':
			return True
		else:
			return False
	elif pos == 'other':
		if entry_pos == 'verb':
			return False
		else:
			return True


# PRINT DICT
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
def print_dict(current_dict):
	'''	Function prints a loaded dictionary as text to a file with special 
		separator character and html tags for formatting. 
		Currently focused on supporting Anki flashcard import tool.

		TODO: Add functionality to print a flashcard deck based on user 
		selected tags. This is already implemented in 'filter_gloss' function
		that pretty print a page of definitions (See below).
	'''

	# change file path to 'prints' folder
	change_path(FORMATTED_FLASHCARD_FILES)
	myFiles = glob.glob('*.txt')

	# option to split flashcard decks by part of speech
	print("Split flashcard sets by part of part of speech?")
	user_input = input("Enter 'y' to split, otherwise press enter: ")

	# different setting for Greek and Latin. 
	# TODO: Allow user to customize these options
	if current_dict['language'] == "Latin" and user_input.lower() == 'y':
		split = True
		pos_list = ['noun','verb','adjective','other']
		pos_test_definitions, pos_test_entries = pos_test_latin_definitions, pos_test_latin_entries
	elif current_dict['language'] == "Ancient Greek" and user_input.lower() == 'y':
		split = True
		pos_list = ['verb','other']
		pos_test_definitions, pos_test_entries = pos_test_greek_definitions, pos_test_greek_entries
	else:
		split = False
		pos_list = ['other']
		pos_test_definitions = pos_test_entries = lambda x,y:True

	# Special separator character
	c = '|'

	while True:

		# Save a reference to the original standard output
		original_stdout = sys.stdout 

		# create a different file for each pos in pos_list
		for pos in pos_list:
			if split:
				file_name = current_dict['language'].replace(' ','') + "-" + pos.upper() + '-Flashcards.txt'
			else:
				file_name = current_dict['language'].replace(' ','') + '-Flashcards.txt'

			# assign user selected file to output
			sys.stdout = open(file_name, 'w')

			# Loop through words in current_dict
			for i in range(len(current_dict['definitions'])):

				# if pos test returns False and split == True, skip this entire definition
				if pos_test_definitions(current_dict['definitions'][i],pos) == False and split == True:
					continue

				# start new string to by printed as next line in flashcard file
				word_string = '<P align="left"><!--' + pos + f"-->{current_dict['definitions'][i]['heading'].strip()}</P>{c}"

				# loop through the entries in the definition and print only those matching 'pos'
				for j in range(len(current_dict['definitions'][i]['entries'])):
					entry = current_dict['definitions'][i]['entries'][j]
					partOfSpeech = entry['partOfSpeech']

					# if pos test returns False and split == True, skip this particular entry
					if pos_test_entries(partOfSpeech,pos) == False and split == True:
						continue

					# include etymology string is less than 126 characters
					if 'etymology' in entry:
						if len(entry['etymology']) <= 125:
							word_string +=  f'<P align="left">{entry["etymology"]}</P>'

					# returns the rest of the entry with proper formatting 
					word_string += get_entry_string(entry,current_dict['language'])

				# add separator character between end of back of card - beginning of tags
				word_string += c

				# add tags as a comma separated list in double quotes
				for tag in current_dict['definitions'][i]['tags']:
					word_string += '"' + tag + '"; '
				word_string.strip('; ')

				# print formatted flashcard string to file
				print(word_string)


		# re-assign orinigal output
		sys.stdout = original_stdout

		print("\n**********************\n\nPrint to file complete\n\n**********************\n")
		return
# END PRINT DICT

def split_tags(tags,next_index,previous_tags):
	'''	This function attempts to group tags together when multiple
		senses have a set of common tags. If a sense differs from a 
		group by a single tag the spoiler is inserted into the line
		for the sense to preserve the grouping.
	'''
	current_index = next_index - 1

	# If previous (current) tags and current tags both exist 
	if previous_tags != [] and tags[current_index] != []:
		match = True
		# previous tags longer than current tags
		if len(previous_tags) > len(tags[current_index]):
			match = False
		else:
			# check if first n tags match between previous and current tag sets
			for i in range(len(previous_tags)):
				if previous_tags[i] != tags[current_index][i]:
					match = False
		# If all previous (common) tags match with first n current tags 
		if match:
			# Seperate current into common and distinct tags 
			return tags[current_index][:i+1], tags[current_index][i+1:]

	# Current did not match previous common tags, inspect next tags 
	if len(tags) > next_index:
		if tags[next_index] != []:
			# Next tags exist and are not empty '''
			if tags[next_index] == tags[next_index - 1]:
				# Tags are exactly the same, all current tags will be common tags 
				return tags[current_index], []

			# Find the smaller of the two lists 
			if len(tags[current_index]) <= len(tags[next_index]):
				shorter = tags[current_index]
				longer = tags[next_index]
			else:
				shorter = tags[next_index]
				longer = tags[current_index]
			for i in range(len(shorter)):
				if shorter[i] != longer[i]:
					# Once lists are no longer the same we have common and distict tags 
					if i == 0:
						# If no matches, all tags are common 
						return tags[current_index], []
					# Else use index to seperate common and distinct 
					return tags[current_index][:i], tags[current_index][i:]

	# If next tags don't exist or are empty, all tags are common tags '''
	return tags[current_index], []


def get_entry_string(entry,language):
	'''	Functionality to format a definition with html tags so the
		card with have left alignment, bolded heading and two level ordered lists
		when diplayed in Anki flashcard manager.
	'''

	# start with bolded simpleParts for entry heading
	entry_string = f'<P align="left"><b>' + f"{entry['simpleParts'].strip()}</b><br>"

	# change senses from list of dictionary to two lists
	sense_glosses = [definition['gloss'] for definition in entry['senses']]
	sense_tags = [definition['tags'] for definition in entry['senses']]

	# short_senses attempts to trim down overly long senses for more readable flashcards
	if language == "Latin":
		sense_glosses = short_senses(sense_glosses)

	# open first order list
	entry_string += f'<ol align="left">'

	# start with tags belonging to the first sense
	line_tags = sense_tags[0]
	# no previous tags
	previous_tags = []

	# determines of current sense should continue to be grouped under same
	# tags as previous and whether current grouping should be closed
	common_tags, distinct_tags = split_tags(sense_tags,1,previous_tags)

	# determine if a sublist should be started for the first sense
	open_sublist = False
	if line_tags:
		open_sublist = True
		entry_string += pretty_print_tags(common_tags,-1)

	# next index is an arugment for split_tags
	next_index = 1

	# iterate through tuples of sense glosses and tags
	for gloss, tags in zip(sense_glosses,sense_tags):

		# determine if senses are compatible for grouping under common tags
		common_tags, distinct_tags = split_tags(sense_tags,next_index,previous_tags)
		previous_tags = common_tags

		# indicates the current grouping must be closed
		if common_tags != line_tags:
			line_tags = common_tags

			# close previous sublist (grouped senses)
			if open_sublist:
				entry_string += "</ol></li>"

			# if next/current sense has tags, start a new sublist
			if common_tags != []:
				open_sublist = True
				entry_string += pretty_print_tags(common_tags,-1)
			# othter senses will print to list level one
			else:
				open_sublist = False

		# 'spoiler' tags are added into the line for the sense
		if distinct_tags:
			entry_string += '<li>' + "(" + ",".join(distinct_tags) + ") " + gloss.strip(";,. ").strip("†∆*^") + '</li>'
		else:
			entry_string += '<li>' + gloss.strip(";,. ").strip("†∆*^") + '</li>'

		next_index += 1

	# close both list levels, add breaks to give space before next entry starts on multi-entry cards
	if open_sublist:
		entry_string += "</ol></li>"
	entry_string += '</ol></P><br><br>'

	# return formated string to flashcard printing function
	return entry_string


# PRINT GLOSS SETUP
# # # # # # # # # # # # 
def print_gloss_setup(current_dict):
	'''	Functionality to pretty print a list of word definitions so that is will fit well
		into a standard page. The idea to allow the user to create study sheets for a 
		particular set of tags such a textbook chapter or a section of a Latin text.
	'''

	# change file path to 'prints' folder
	change_path('glosses')
	myFiles = glob.glob('*.txt')

	while True:
		# give user option to select from all tags found in the current dictionary
		master_list = word_methods.get_master_list(current_dict)
		tags = word_methods.getTags([],'filter',master_list)

		options= {'1':"Choose tag option: '1' for strict match",'2':", '2' for loose match\n"}
		tag_mode = get_selection.get_selection(options)


		# User input Loop
		exit_inner_loop = False
		while not exit_inner_loop:
			
			# Input name of print file
			print("What to you want to name your print file?")
			user_input = input("Enter name (0 to go back): ")

			# return control
			if user_input == '0':
				exit_inner_loop = True
				continue

			file_name = user_input + '.txt'

			# Check with user before overwriting existing file
			if file_name in myFiles:
				print(f"\n{file_name} already exists, ok to overwrite?")
				print("'1' to proceed, any other key to go back")
				user_input = input(': ')

				if user_input != '1':
					continue
			
			filter_gloss(current_dict,tags,file_name,tag_mode)
			
			print("\n**********************\n\nPrint to file complete\n\n**********************\n")
			return
# END PRINT GLOSS SETUP



# FILTER GLOSS
# # # # # # # # # # # # # # 
def filter_gloss(current_dict,tags,output_file=None,tag_mode='1'):
	count = 0

	if output_file:
		# Save a reference to the original standard output
		original_stdout = sys.stdout 

		# assign user selected file to output
		sys.stdout = open(output_file, 'w')		

	if tags:
		print(f"\n\t{str(tags)}\n")

	parts_list = ["noun", 
		"proper noun","verb","adjective","participle", "adverb", "determiner",
		"article", "preposition", "conjunction","pronoun","letter", "character", 
		"phrase", "proverb", "idiom","symbol", "syllable", "numeral", "initialism",
		"interjection","definitions"]
	for part in parts_list:
		count += print_gloss(current_dict,tags,part,tag_mode)

	if output_file:
		# re-assign orinigal output
		sys.stdout = original_stdout
	return count
# END FILTER GLOSS



# PRINT GLOSS
# # # # # # # # # # # # # # 
def print_gloss(current_dict,tags,partOfSpeech=None,tag_mode='1'):
	strings = {}
	first_run = True

	counter = 0

	# Loop to create sub-list to select from
	for index in range(len(current_dict['definitions'])):

		# assign word to shorten name
		word = current_dict['definitions'][index]

		for x in range(len(word['entries'])):
			# test if tags match; always 'yes' for empty tags
			if tag_mode == '1':
				print_flag = set(tags).issubset(set(word['tags']))
			elif tag_mode == '2':
				print_flag = False
				for tag in tags:
					if tag in word['tags']:
						print_flag = True
			# test if part of speech match if using part of speech mode
			if print_flag and partOfSpeech:
				print_flag = word['entries'][x]['partOfSpeech'].lower() == partOfSpeech.lower()

			# print word in desired subset
			if print_flag:
				
				if partOfSpeech and first_run:
					print(f"\n{partOfSpeech.upper()}S:\n")
					first_run = False
				
				# increment counter
				counter += 1

				# print with desired alignment
				if current_dict['language'] == 'Latin':
					simpleParts = word['entries'][x]['simpleParts']
					if partOfSpeech == 'verb':
						if len(simpleParts) > 50:
							simpleParts = simpleParts[:49] + "-"
						entry_string = f"{simpleParts:.<50} | "
					else:
						if len(simpleParts) > 30:
							simpleParts = simpleParts[:29] + "-"
						entry_string = f"{simpleParts:.<30} | "
					# check if definition exceeds desired length
					text = [d['gloss'] for d in word['entries'][x]['senses']]
					dtags = [d['tags'] for d in word['entries'][x]['senses']]

					if len(text) == 1: 
						entry_string += f"~) " + text[0].strip('*^†∆') + ";  "
					else:
						for i in range(len(text)):
							entry_string += f"{i+1}) " + text[i].strip('*^†∆') + ";  "
					entry_string = entry_string.strip("; ")

					if len(entry_string) > 130:
						print(entry_string[:entry_string[:130].rfind(' ')])
						if partOfSpeech == 'verb':
							second_line = entry_string[entry_string[:130].rfind(' '):]
							if len(second_line) > 80:
								second_line = second_line[:77] + "..."
							print(f"{'.':.<50} |   {second_line}")
						else:
							second_line = entry_string[entry_string[:150].rfind(' '):]
							if len(second_line) > 100:
								second_line = second_line[:97] + "..."
							print(f"{'.':.<30} |   {second_line}")
					else:
						print(f"{entry_string}")
				elif current_dict['language'] == "Ancient Greek":
						
					entry_string = word['entries'][x]['simpleParts'][:word['entries'][x]['simpleParts'].find(')')+1].strip()

					# TODO: this should be replaced with the get_visible_length function from the get_selection module
					length_string = entry_string.lower().replace("θ",'t')
					length_string = length_string.replace("χ",'k') 
					length_string = length_string.replace('φ','f')
					length_string = length_string.replace('ψ','c')
					entry_string += ' ' * (30 - len(unidecode(length_string))) + " | "
					# check if definition exceeds desired length
					text = [line['gloss'] for line in word['entries'][x]['senses']]
					text = short_senses(text)
					if len(text) == 1:
						entry_string += text[0]
					else:
						for i in range(len(text)):
							entry_string += f"{i+1}) " + text[i].strip('*^†∆') + ";  "
					entry_string = entry_string.strip("; ")

					if len(entry_string) > 130:
						print(entry_string[:entry_string[:130].rfind(' ')])
						print(f"{' ':<30} |   {entry_string[entry_string[:130].rfind(' '):entry_string[:225].rfind(',')]}")
					else:
						print(f"{entry_string}")

	return counter
# END PRINT GLOSS

''' The rest of these functions attempt to shorten senses that are overly long
	to make more useful flashcards.
'''

# CHOP LINE
# # # # # # # # # # # # # 
def chop_line(senses):
	'''	Determines how much each sense should be shortened based on
		the total number of senses and the total characters
	'''
	size = sum([len(sense) for sense in senses])

	if len(senses) < 3:
		limit = 5
	elif len(senses) == 3:
		limit = 4
	elif len(senses) > 3:
		limit = 3

	if size > 150:
		for i in range(len(senses)):
			senses[i] = short_line(senses[i],limit)
	return senses


# SHORT LINE
# # # # # # # # # # 
def short_line(line,limit):
	'''	Attempts to shorten line, aborts under certain conditions such as
		parens at the end (usually contain something important)
	'''

	line = re.split(",|;",line)
	stop = orstop = parstop = limit

	# if line contains and 'or' avoid cutting before the or
	for i in range(len(line)):
		orlist = [x for x in line[i:] if " or " in x]
		if orlist != []:
			orstop = i + 1
			continue
		else:
			break
	# if line contains parens, avoid cutting before the last closing paren
	for i in range(len(line)):
		parlist = [x for x in line[i:] if ")" in x or "(" in x]
		if parlist != []:
			parstop = i + 1
			continue
		else:
			break

	# determine the least safe cutting point
	stop = max(orstop,parstop,limit)
	line = line[:stop]

	# reconstruct string 
	new_text = ", ".join(word.strip() for word in line)

	return line

# SHORT senses
# # # # # # # # # # 
def short_senses(text):
	'''	removes empty strings before and after calling chop_line
	'''
	while '' in text:
		text.remove('')

	text = chop_line(text)

	while '' in text:
		text.remove('')

	for i in range(len(text)):
		text[i] = text[i].strip(',;')
	return text
# END SHORT senses

# CHOP PARENS
# # # # # # # # # # # # 
def chop_parens(text):
	for i in range(len(text)):
		if text[i].strip()[:1] == "(":
			text[i] = text[i][text[i].find(')')+1:].strip(';, ')
		if text[i][-1:] == ")":
			text[i] = text[i][:text[i].rfind('(')].strip(':, ')
	return text
