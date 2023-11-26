'''
DESCRIPTION:

	edit_entry:
		allows user to edit an entry: change parts, change definitions,
		move definitions, delete definitions or replace all

	move_entries:
		take a list and two positionn as arguments and move
		item from position one to position two

	print_entry:
		prints parts and definition of a single entry

	select_definition:
		validates the selection of a definition
'''

from unidecode import unidecode
from get_selection import get_selection, clear_screen,visible_len
import edit_dictionary
from copy import deepcopy
from tables_greek_ext import auto_parts
from pyfiglet import figlet_format


# string used multiple times
confirm_str = "'1' to confirm, any other key to cancel: "

# EDIT ENRTY
# # # # # # # # 
entry_string = ''
def edit_entry(entry,new_word):
	''' Menu for user options to edit an entry of a definition.
		TODO: each option should be moved to a separate function.
	'''
	while True:
		
		# flag if only one definition exists
		singleton = True if len(entry['senses']) == 1 else False

		# display entry
		entry_string = get_entry(entry)

		# define user options
		options = {
		'1':"\n==================================\nEntry Options:\n>'1' to add definition\n",
		'2':">'2' to change definition\n"}
		if singleton:
			options.update({
				'3':">'3' to replace definition\n"})

		# only display these options if more than one definition
		if not singleton:
			options.update({
				'3':">'3' to replace all\n",
				'4':">'4' to move definitions\n",
				'5':">'5' to delete definitions\n"})

		# more options
		options.update({
			'tag':">'tag' to tag defintions",
			'untag_all':'',
			'untag':">'untag' to remove tags\n",
			'parts':">'parts' to change principal parts\n",
			'etym':">'etym' to change etymology\n",
			'ps':">'ps' to change part of speech\n",
			'0':">'0' to go back ",'00':">'00' to finish and save\n"})

		user_input = get_selection(options,entry_string)

		# Option to finish/go back
		if user_input == '0':
			return entry, False

		elif user_input == '00':
			return entry, True

		# Option to add new
		elif user_input == '1':
			add_new(entry)

		# apply a new tag to some of the senses within the definition
		elif user_input.lower() == 'tag':
			add_new_tag(entry)

		# remove all tags, currently an invisible option
		elif user_input.lower() == "untag_all":
			for i in entry['senses']:
				i['tags'] = []

		# remove a tag from some of the senses within the definition
		elif user_input.lower() == 'untag':
			remove_tag(entry)

		# Option to change definition
		elif user_input == '2':
			change_definition(entry,singleton)

		# Option to move definition
		elif user_input == '4' and not singleton:
			move_definition(entry)

		# Option to delete definition		
		elif user_input == '5' and not singleton:
			delete_definition(entry)

		# Options to replace all definitions		
		elif user_input == '3':
			replace_all(entry)

		# Option to rewrite principle parts			
		elif user_input.lower() == 'parts':
			change_principle_parts(entry)

		# Option to rewrite etymology			
		elif user_input.lower() == 'etym':
			change_etymology(entry)

		# option to change the partOfSpeech for a definition
		elif user_input.lower() == 'ps':
			change_pos(entry)

# END EDIT ENTRY


# REMOVE WORDS
# # # # # # # # # # # 
def remove_words(text):
	'''	This function allows the user to delete a substring from a definition
		by specifying the start and end point to 'snip'. The function displays
		the definition on a grid showing the user how to specify the start and 
		end point. 
		The word is divided into rows of 26 characters where each character in
		the row is under a column heading with the 26 letters of the alphabet.
	'''
	text = list(text)		
	invalid = False
	while True:
		clear_screen()

		# compute number of rows 
		rows = 1+len(text)//26

		# print top of box that surrounds grid
		print('*' * 35 + " |")

		for i in range(rows):

			# print letters for row indices
			print(f"Row ({chr(i + 65)}): ",end='')

			# print letters for columns indices
			for j in range(len(text[ 26 * i : 26 * (i + 1) ])):
				print(chr(j+65),end='')

			# print '|'s to box in grid
			pad = 26 - len(text[ 26 * i : 26 * (i + 1) ]) 
			print(' ' * pad + " |")
			print(' ' * 9,end='')

			# print portion of sense that belong in this row
			for j in range(26 * i,(26 * i) + len(text[ 26 * i : 26 * (i + 1) ])):
				print(text[j],end='')

			# print '-'s and '|'s to box in grid
			pad = 26 - len(text[ 26 * i : 26 * (i + 1) ]) 
			print(' ' * pad + " |")		
			print('-' * 35 + " |")

		# print '*'s and '|' to complete box
		print('*' * 35 + " |")

		# print message with UI instructions
		print("To cut enter 'Start Row, Start Col, Stop Row, Stop Col':'RC,RC' ('0' to stop): ")

		# if previous entry was invalid
		if invalid:
			print("\nInvalid entry\n\n")
			invalid = False

		user_input = input(": ")

		# choice to exit
		if user_input == '0':

			# construct return string
			return_text = ''
			for i in range(len(text)):
				return_text += text[i]
			return return_text

		# try to decode user input and cut substring
		else:
			try:
				user_input = user_input.split(',')
				row1 = user_input[0][0].upper()
				col1 = user_input[0][1].upper()
				row2 = user_input[1][0].upper()
				col2 = user_input[1][1].upper()
				start = ( ( ord(row1) - 65 ) * 26 ) + ( ord(col1) - 65 )
				stop = ( ( ord(row2) - 65 ) * 26 ) + ( ord(col2) - 65 ) + 1
				text = text[:start] + text[stop:]
			except:
				invalid = True
# END remove_words


def add_new(entry):
	''' Add a new sense to the entry
	'''
	while True:
		print("\nChoose postion of new definition (1-n)")
		try:
			place = int(input(": "))-1
		except:
			print("Invalid")
			continue
		break
	if place < 0:
		return
	print("\nEnter your new definition ('0' to go back) (ā, ē, ī, ō, ū)")
	new_definition = {'gloss':input(': ')}

	if new_definition['gloss'] != '0':
		new_definition['tags'] = []
		print("Enter definition tags ('0' to finish)")
		new_tag = input(": ")
		if new_tag != '0':
			new_definition['tags'].append(new_tag)
		entry['senses'].insert(place,new_definition)

def add_new_tag(entry):
	''' Add a new tag, apply tag to multiple senses until finished
	'''
	exit_loop = False
	while not exit_loop:		
		print("Enter the tag you want to apply ('0' to go back)")
		new_tag = input(": ")
		if new_tag == '0':
			exit_loop = True
		else:
			exit_inner_loop = False
			while exit_inner_loop == False:
				message = "\n==================================\nChoose the definition you want to tag\n'0' to go back"
				selection = select_definition(entry,message)
				if selection == None:
					exit_inner_loop = True
				else:
					entry['senses'][selection]['tags'].append(new_tag)

def remove_tag(entry):
	'''	User selects a sense and tags to remove
	'''
	exit_loop = False
	while not exit_loop:		
		message = "\n==================================\nChoose the definition you want to untag\n'0' to go back"
		selection = select_definition(entry,message)
		if selection == None:
			exit_loop = True
		elif entry['senses'][selection]['tags']:
			exit_inner_loop = False
			while exit_inner_loop == False:
				for i in range(len(entry['senses'][selection]['tags'])):
					print(f"{i+1}. {entry['senses'][selection]['tags'][i]}")
				print("Select the tag you want to remove ('0' to go back)")
				tag_no = input(": ")
				if tag_no == '0':	
					exit_inner_loop = True
				elif int(tag_no) - 1 in range(len(entry['senses'][selection]['tags'])):
					del entry['senses'][selection]['tags'][int(tag_no) - 1]
					if entry['senses'][selection]['tags'] == []:
						print("\ndefinitions has no more tags")
						exit_inner_loop = True
				else:
					print("\ninvalid selection")
		else:
			print('\ndefinition has no tags')

def change_definition(entry,singleton):
	''' User is given the option to remove text from any part of the sense
		or add text to the beginning or ending of the sense. 
	'''
	while True:

		# get user selection for sense to modify
		if singleton:
			selection = 0
		else:
			message = "\n==================================\nChoose the definition you want to change\n'0' to go back"
			selection = select_definition(entry,message)
			if selection == None:
				return

		
		while selection != None:

			# display gloss, tags and user options
			definition_string = f"Definition: {entry['senses'][selection]['gloss']}\nTags: {', '.join(entry['senses'][selection]['tags'])}\n"
			options = {'0':f"Change Definition Options:\n>'0' to go back",'00':">'00' to finish\n",'1':">'1' to remove words\n",
			'2':">'2' to add text to the end\n",
			'3':">'3' to add text to the beginning\n",
			'4':">'4' to write new definition\n"}
			user_input = get_selection(options,definition_string)

			# option to go back (exit if singleton)
			if user_input == '0':
				selection = None
				if singleton:
					return
			# option to exit back to edit entry menu
			elif user_input == '00':
				return

			# option to remove text from any part of sense
			elif user_input == '1':
				entry['senses'][selection]['gloss'] = remove_words(entry['senses'][selection]['gloss'])

			# option to add to end of sense
			elif user_input == '2':
				print("\nEnter text to add to definition ('0' to go back) (ā, ē, ī, ō, ū)")
				new_text = input(': ')
				if new_text != '0':
					entry['senses'][selection]['gloss'] += new_text	

			# option to add to beginning of sense
			elif user_input == '3':
				print("\nEnter text to add to definition ('0' to go back) (ā, ē, ī, ō, ū)")
				new_text = input(': ')
				if new_text != '0':
					entry['senses'][selection]['gloss'] = new_text + entry['senses'][selection]['gloss']

			# option to overwrite definition		
			elif user_input == '4':
				print("\nEnter your new definition ('0' to go back) (ā, ē, ī, ō, ū)")
				new_definition = input(': ')
				if new_definition != '0':
					entry['senses'][selection]['gloss'] = new_definition
					entry['senses'][selection]['tags'] = []
					while True:
						print("Enter definition tags ('0' to finish)")
						new_tag = input(": ")
						if new_tag == '0':
							break
						else:
							entry['senses'][selection]['tags'].append(new_tag)

def change_principle_parts(entry):
	'''	principle parts set to requested user input
	'''
	print("'1' to auto retreieve verb parts (Greek only), any other key to proceed")
	user_input = input(": ")
	if user_input == '1':
		entry['simpleParts'] = auto_parts(entry['simpleParts'],True)
	else:
		print("\nEnter your new principal parts ('0' to go back) (ā, ē, ī, ō, ū)")
		new_definition = input(': ')

		if new_definition != '0':
			entry['simpleParts'] = new_definition

def change_etymology(entry):
	'''	etymology set to requested user input
	'''
	print("\nEnter your new etymology ('0' to go back) (ā, ē, ī, ō, ū) ('X' to delete)")
	user_input = input(': ')
	if user_input.upper() == "X":
		entry['etymology'] = ''
	elif user_input != '0':
		entry['etymology'] = user_input

def change_pos(entry):
	'''	pos set to requested user input
	'''
	print("\nEnter your new part of speech ('0' to go back)")
	user_input = input(': ')
	if user_input != '0':
		entry['partOfSpeech'] = user_input

def move_definition(entry):
	'''	validate user input for move entries function
	'''
	if len(entry['senses']) == 2:
		entry['senses'] = move_entries(entry['senses'],1,0)
	else:
		exit_inner_loop = False
		while not exit_inner_loop:
			message = "\n==================================\nChoose the definition you want to move\n'0' to go back"
			take = select_definition(entry,message)

			if take != None:
				message = "\nMove to what position?\n'0' to go back"
				put = select_definition(entry,message)

				if put != None:
					entry['senses'] = move_entries(entry['senses'],take,put)

			else:
				exit_inner_loop = True

def delete_definition(entry):
	'''	validate user input to delete a sense
	'''
	exit_inner_loop = False
	while not exit_inner_loop:
		message = "\n==================================\nChoose the definition you want to delete\n'0' to go back"
		selection = select_definition(entry,message)

		if selection != None:
			print(f"\nAre you sure to want to delete {selection+1}?")
			user_input = input(confirm_str)

			if user_input == '1':
				del entry['senses'][selection]

		else:
			exit_inner_loop = True
		if len(entry['senses']) == 1:
			exit_inner_loop = singleton = True	

def replace_all(entry):
	'''	senses replaced with a single sense from user input
	'''
	print("\nEnter your new definition ('0' to go back) (ā, ē, ī, ō, ū)")
	new_definition = {'gloss':input(': ')}

	if new_definition != '0':
		new_definition['tags'] = []

		print("Enter definition tags ('0' to finish)")
		new_tag = input(": ")
		if new_tag != '0':
			new_definition['tags'].append(new_tag)
		entry['senses'] = [new_definition]	

# MOVE ENTRIES
# # # # # # # # # # # # # # # # # 
def move_entries(entries,selection,new_position):
	''' Rearrange object in list from selection to new_position
	'''
	if selection == new_position:
		return
	else:
		popped = entries.pop(selection)
		# avoid going out of bounds
		if new_position == len(entries):
			entries.append(popped)
		else:
			entries.insert(int(new_position),popped)
	return entries
# END MOVE ENTRIES

def pretty_print_tags(tags,mode=[]):
	''' Utility function for printing senses in two level list
		based on tag groupings
	'''

	''' -1 is mode for html printing '''
	''' else mode corresponds to counter '''
	if mode != -1:
		string = f'{mode}. ('
	else:
		''' begin html list '''
		string = '<li>('

	string += ", ".join(tags)

	''' if -1 start sub list in hierarchy, edit_dictionary.print_entry_string takes care of capping ordered list '''
	if mode == -1:
		string += ')<ol style="list-style-type: lower-roman; padding-bottom: 0; margin-left:1em">'

		''' else simply cap tags with ")", print_entry takes care of sublist '''
	else:
		string += ")\n"
	return string


def split_tags(senses,next_index,previous_tags):
	''' This function tries to group a common tags between senses
		so that the entry displays more cleanly. If most of the
		tags match, the senses will be grouped in a sublist.
		Any individual tags the would break up a logical grouping
		may be added to the individual lines.
	'''
	current_index = next_index - 1

	''' If previous (current) tags and current tags both exist '''
	if previous_tags != [] and senses[current_index]['tags'] != []:
		match = True
		if len(previous_tags) > len(senses[current_index]['tags']):
			match = False
		else:
			for i in range(len(previous_tags)):
				if previous_tags[i] != senses[current_index]['tags'][i]:
					match = False
		''' If all previous (common) tags match with first n current tags '''
		if match:
			''' Seperate current into common and distinct tags '''
			return senses[current_index]['tags'][:i+1], senses[current_index]['tags'][i+1:]

	''' Current did not match previous common tags, inspect next tags '''
	if len(senses) > next_index:
		if senses[next_index]['tags'] != []:
			''' Next tags exist and are not empty '''
			if senses[next_index]['tags'] == senses[next_index - 1]['tags']:
				''' Tags are exactly the same, all current tags will be common tags '''
				return senses[current_index]['tags'], []

			''' Find the smaller of the two lists '''
			if len(senses[current_index]['tags']) <= len(senses[next_index]['tags']):
				shorter = senses[current_index]['tags']
				longer = senses[next_index]['tags']
			else:
				shorter = senses[next_index]['tags']
				longer = senses[current_index]['tags']
			for i in range(len(shorter)):
				if shorter[i] != longer[i]:
					''' Once lists are no longer the same we have common and distict tags '''
					if i == 0:
						''' If no matches, all tags are common '''
						return senses[current_index]['tags'], []
					''' Else use index to seperate common and distinct '''
					return senses[current_index]['tags'][:i], senses[current_index]['tags'][i:]

	''' If next tags don't exist or are empty, all tags are common tags '''
	return senses[current_index]['tags'], []



def convert_message(message,string):
	''' this function joins a new string to the message being built
		by the get_entry function. Keeps the strings to < 129 
		characters before separating into a new line.
	'''
	modulus = 129
	if len(message) < modulus:
		string += message + "\n"
		return string
		
	last = 0
	for i in range((len(message)//modulus)+1):
		first = last
		if len(message) > (i+1) * modulus:
			last = message[0: (i+1) * modulus].rstrip(" ").rfind(" ")
			if last == -1:  # No space found, force break
				last = len(message)
			string += message[first:last].replace("\n","") + '\n'
		else:
			string += message[first:].replace("\n","") + '\n'
	return string

def get_entry(entry,mode='',trunc=False):
	'''	Get a formatted string representing an entire word entry.
		Prints the entry etymology, partOfSpeech and simpleParts,
		followed by the senses for the entry.
		The sense are printed in two list levels.
		Level 1: arabic numerals, any untagged senses or a list of tags.
		Level 2: lower-case roman numerals, one or more sense under a
		common set of tags
	'''
	string = ''
	iv = ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x', 'xi', 'xii', 'xiii', 'xiv', 'xv', 'xvi', 'xvii', 'xviii', 'xix', 'xx', 'xxi', 'xxii', 'xxiii', 'xxiv', 'xxv', 'xxvi', 'xxvii', 'xxviii', 'xxix', 'xxx', 'xxxi', 'xxxii', 'xxxiii', 'xxxiv', 'xxxv', 'xxxvi', 'xxxvii', 'xxxviii', 'xxxix', 'xl', 'xli', 'xlii', 'xliii', 'xliv', 'xlv', 'xlvi', 'xlvii', 'xlviii', 'xlix', 'l']

	''' Print Heading '''
	if mode == '':
		string += figlet_format("ENTRY:",font='cybermedium',width=150)
		string += "**************\n\n"

	''' Print Etymology if Applicable '''
	if 'etymology' in entry and entry['etymology'] != '' and mode != 'choice':
		string = convert_message(f"\n{entry['etymology']}\n\n",string)
	if entry['partOfSpeech'] != "":
		string += f"{entry['partOfSpeech']}\n\n"
	
	string = convert_message(entry['simpleParts'],string)

	previous_tags = []
	char_count = 0
	etym = len(string)
	counter = 1
	offset = 0

	''' Loop through senses '''
	for index in range(len(entry['senses'])):
		if( (index > 3 or char_count > 400) and trunc):
			string += f"{index + 1}. ...\n"
			break

		''' "choice" mode involves simpler formatting '''
		if mode != "choice":

			''' compare current, previous and next tags for next common tags '''
			common_tags, distinct_tags = split_tags(entry['senses'],index + 1,previous_tags)

			''' If a new set of tags '''
			if common_tags != previous_tags:
				previous_tags = common_tags
				if common_tags != []:
					''' Create a new numerical list item '''
					string += pretty_print_tags(common_tags,counter)
					offset = index
					counter += 1
			''' If no tags, simply print senses as numerical list item '''
			last = 0
			if common_tags == []:
				string = convert_message(f"{counter}. {entry['senses'][index]['gloss']}",string)
				counter += 1
				''' Skip the bottom block for printing senses with roman numerals '''
				char_count = len(string) - etym
				continue
		
		''' Choice mode uses a simple list w/o hierarchy '''
		last = 0
		if mode == 'choice':
			string = convert_message(f"{index + 1}. {entry['senses'][index]['gloss']}",string)
			''' Print definitions with roman numeral in the event there are tags '''
		else:
			if distinct_tags:
				string = convert_message(f"{iv[index - offset]:>4}. ({', '.join(distinct_tags)}) {entry['senses'][index]['gloss']}",string)
				string.strip('\n')
			else:
				string = convert_message(f"{iv[index - offset]:>4}. {entry['senses'][index]['gloss']}",string)
				string.strip('\n')
		char_count = len(string) - etym
	x = 800
	if mode != '' and char_count - etym > x:
		string = string[:x-1] +"...\n"
	return string



# PRINT ENTRY
# # # # # # # # # 
def print_entry(entry,mode=''):
	print(get_entry(entry,mode,False))
# END PRINT ENTRY


# SELECT DEFINITIONS
# # # # # # # # # # # # # # 
def select_definition(entry,message):
	''' user input function for a selecting a definition
		for modification, deletion, etc.
	'''
	invalid = False
	while True:
		clear_screen()
		print_entry(entry,'choice')
		print(message)

		if invalid:
			print('\ninvalid selection')
			invalid = False

		user_input = input(': ')

		# Option to go back
		if user_input == '0':
			return None

		# confirm input is numeric
		elif "-" in user_input:
			user_input = user_input.split("-")
			if user_input[0].isnumeric() and user_input[1].isnumeric():
				user_input[0] = int(user_input[0])-1
				user_input[1] = int(user_input[1])-1
				if user_input[0] in range(len(entry['senses'])) and user_input[1] in range(len(entry['senses'])):
					return user_input
		elif user_input.isnumeric():
			# convert to string
			user_input = int(user_input)-1
			#confirm in range
			if user_input in range(len(entry['senses'])):
				return user_input
		# repeat loop after invalid selection
		invalid = True
# END SELECT DEFINITIONS