
'''
Description:

	edit entries:
		options within word to create, delete, move and modify entries

	select entries:
		allows user to choose an entry based on letter indices
		returns selection as the number index of selected entry in entries list

	print entries:
		print all entries of a word including part of speech
		option to include capital letter next to part of speech begining each entry
'''
import pickle
from unidecode import unidecode
from copy import deepcopy
import word_methods
import edit_entry
import create_word
from get_selection import get_selection, clear_screen
import parser_shell
import load_dict 
from pyfiglet import figlet_format

# EDIT ENTRIES
# # # # # # # # # # # # 
def edit_entries(new_word,current_dict,t):
	language = current_dict['language']
	# save confirm choice string used in multiple places
	confirm_str = "'1' to confirm, any other key to cancel: "
	entry_string = ''
	# rest of function contained in loop
	while True:

		# flag if only one entry exists
		if len(new_word['entries']) <= 1:
			single_entry = True
		else:
			single_entry = False

		entry_string = get_entry_string(new_word['entries'])

		# get user selection
		options = {
		'1':f"\n===================================================\n'{new_word['heading']}' Options:\n>'1' Edit Entry\n",
		'2':">'2' Create New Entry\n"}
		if not single_entry:
			options.update({
				'3':">'3' Move Entry\n",
				'4':">'4' Delete Entry\n"})
				#'5':">'5' Merge Entries\n"})
		if 'template' in new_word:
			options.update({'reset':">'reset' to reset template tag\n"})
		options.update({
			'tags':">'tags' to modify tags\n",
			'add':">'add' to add another word\n",
			'head':"'head' to change heading\n",
			#'split':"'split' to create sub-cards\n",
			'0':">'0' to finish edit\n",'00':">'00' to finish and save\n",'verb':''})
		clear_screen()
		user_input = get_selection(options,entry_string)
		

		# Option to exit, only way to end loop
		if user_input == '0':
			return new_word, False

		if user_input == '00':
			return new_word, True

		# edit tags option
		if user_input.lower() == 'tags':
			master_list = word_methods.get_master_list(current_dict)
			new_word['tags'] = word_methods.getTags(new_word['tags'],'',master_list)

		if user_input.lower() == 'reset':
			del new_word['template']

		# Options to modify entry, then repeat loop
		elif user_input == '1':
			# selection needed only for multiple entries
			if single_entry:
				new_word['entries'][0], finish_and_save = edit_entry.edit_entry(new_word['entries'][0],new_word)
				if finish_and_save:
					return new_word, True
			else:
				# request user selection with appropriate message
				message = '===================================================\nEnter the letter of the entry you want to modify.'
				selection = select_entry(new_word['entries'],message)

				# unless modify is aborted, call edit_entry, repeat loop when done
				if selection != None:
					clear_screen()
					new_word['entries'][selection], finish_and_save = edit_entry.edit_entry(new_word['entries'][selection],new_word)
					if finish_and_save:
						return new_word, True

		# Option to create new entry, then repeat loop
		elif user_input == '2':
			new_word, result = create_word.create_entry(new_word)

		# Option to move entry
		elif user_input == '3' and not single_entry:
			if len(new_word['entries']) == 2:
				new_word['entries'] = edit_entry.move_entries(new_word['entries'],1,0)
			else:
				exit_inner_loop = False
				while not exit_inner_loop:
					# request user selection with appropriate message
					message = "\n===================================================\nEnter the letter of the entry you want to move."
					selection = select_entry(new_word['entries'],message)

					# unless move is aborted, proceed to STEP TWO
					if selection != None:
						# request user selection with appropriate message
						message = f"\n===================================================\nMove {chr(selection + 65)} to what position?"
						new_position = select_entry(new_word['entries'],message)

						# unless move is aborted, confirm requested change
						if new_position != None:
							new_word['entries'] = edit_entry.move_entries(new_word['entries'],selection,new_position)
					else:
						exit_inner_loop = True

		elif user_input.lower() == 'add':
			print("'1' to look up word, '2' to create new entry")
			user_input = input(": ")
			if user_input == '1':
				new_word = word_combo(new_word,t,current_dict['language'])
			else:
				new_entry, result = create_word.create_entry(new_word)

		# Option to delete
		elif user_input == '4' and not single_entry:
			exit_inner_loop = False
			while not exit_inner_loop:
				# request user selection with appropriate message
				message = '===================================================\nEnter the letter of the entry you want to delete.'
				selection = select_entry(new_word['entries'],message)

				# if delete not aborted, confirm requested deletion
				if selection != None:
					# Confirm deletion
					print(f"\nDelete entry {chr(selection+65)}?")
					user_input = input(confirm_str)

					# if confirmed, delete entry / either way, repeat loop when done
					if user_input == '1':
						del new_word['entries'][selection]
				else:
					exit_inner_loop = True
				if len(new_word['entries']) == 1:
					exit_inner_loop = single_entry = True

		elif user_input == '5' and not single_entry:
			exit_inner_loop = False
			while not exit_inner_loop:
				# request user selection
				# request user selection with appropriate message
				message = '===================================================\nEnter the letter of the entry you want to merge to.'
				s1 = select_entry(new_word['entries'],message)

				if s1 != None:
					# request user selection with appropriate message
					message = f'===================================================\nEnter the letter of the entry you want to merge with entry {chr(s1 + 65)}.'
					s2 = select_entry(new_word['entries'],message)

					if s2 != None:
						new_word['entries'][s1]['defs'].extend(new_word['entries'][s2]['defs'])

						print(f"\nChange principle parts \nfrom: {new_word['entries'][s1]['simpleParts']}")
						print(f"to:   {new_word['entries'][s2]['simpleParts']}\n")
						user_input = input("'1' to confirm, any other key for no: ")

						if user_input == '1':
							new_word['entries'][s1]['simpleParts'] = new_word['entries'][s2]['simpleParts']

						del new_word['entries'][s2]
						exit_inner_loop = True
				else:
					exit_inner_loop = True

			# Test if heading should be changed
			if new_word['heading'] != new_word['entries'][0]['simpleParts'][:len(new_word['heading'])]:
				print(f"Change heading from {new_word['heading']} to {new_word['entries'][0]['simpleParts'][:len(new_word['heading'])]}?")
				user_input = input("'1' to confirm, any other key for no: ")

				if user_input == '1':
					new_word['heading'] = new_word['entries'][0]['simpleParts'][:len(new_word['heading'])]
					new_word['handle'] = unidecode(new_word['heading'])

		elif user_input == 'head':
			print("\nEnter your new heading ('0' to go back) (ā, ē, ī, ō, ū)")
			new_definition = input(': ')

			if new_definition != '0':
				new_word['heading'] = new_definition
				new_word['handle'] = unidecode(new_word['heading'])

		elif user_input == 'split':
			split_word(new_word,current_dict)

		elif user_input == 'verb':
			for i in new_word['entries']:
				i['partOfSpeech'] = 'verb'


# END EDIT ENTRIES

def flatten(word):
	for i in word['entries']:
		for z in i['defs']:
			z['gloss'] = z['gloss'].lower()

def split_word(word,current_dict):
	count = 1
	splits = []
	while True:
		new_split = {}
		print(word['heading'])
		print(word['entries'][0]['simpleParts'])
		print(f"Enter Split {count} heading ('0' to stop)")
		user_input = input(": ")
		if user_input == '0':
			return
		new_split['heading'] = new_split['handle'] = '<!--Split-->' + user_input
		new_split['tags'] = []
		new_split['entries'] = [{'simpleParts':user_input,'principleParts':user_input,'partOfSpeech':'split','defs':[]}]
		for entry in word['entries']:
			while True:
				print(f"Split {count}:")
				if new_split['entries'][0]['defs']:
					edit_entry.print_entry(new_split['entries'][0])
				else:
					print("\nENTRY:")
					print("******\n")
					print(f"{new_split['entries'][0]['partOfSpeech']}\n")
					print(new_split['entries'][0]['simpleParts'])
				selection = edit_entry.select_definition(entry,f"Choose definition to add to split {count} ('0' for next):")
				if selection == None:
					break
				if type(selection) == list:
					for i in range(selection[0],selection[1]+1):
						new_split['entries'][0]['defs'].append(entry['defs'][i])
				else:
					new_split['entries'][0]['defs'].append(entry['defs'][selection])
		edit_entry.print_entry(new_split['entries'][0])
		while True:
			print(f"Save split {count}? ('1' save, '0' to discard)")
			user_input = input(": ")
			if user_input == '0':
				break
			elif user_input == '1':
				splits.append(deepcopy(new_split))
				break
			else:
				print("Invalid entry")
		while True:
			print("Creat another split? ('1' to continue, '0' to finish)")
			user_input = input(": ")
			if user_input == '0' or user_input == '1':
				break
			else:
				print("Invalid entry")
		if user_input == '1':
			count += 1
			continue
		elif user_input == '0':
			break
	if splits:
		for split in splits:
			parser_shell.save_word(split,current_dict)
	return




# WORD COMBO
# # # # # # # # # # # # # # #
def word_combo(new_word,t,lang,search_word=None):
	letters = []
	""" Retrieve use selection from dictionary """ 
	combo_word = parser_shell.choose_from_trie(t,lang)

	if combo_word == None:
		return new_word
	else:
		if 'roots' in combo_word:
			new_word['roots'] = combo_word['roots']
		for index in range(len(combo_word['entries'])):
			new_word['entries'].append(combo_word['entries'][index])

			if new_word['heading'] != combo_word['heading']:
				print(f"Change heading from {new_word['heading']} to {combo_word['heading']}?")
				user_input = input("'1' to confirm, any other key for no: ")

				if user_input == '1':
					new_word['heading'] = combo_word['heading']
					new_word['handle'] = combo_word['handle']

		print("NEW COMBINED WORD:\n")
		print_entries(new_word['entries'])
		return new_word

# END WORD COMBO


# SELECT ENTRY
# # # # # # # # # # # # # # # 
def select_entry(entries,message):
	# whole function contained in loop
	invalid = False
	while True:
		# Display entries in 'options mode'
		print_entries(entries,mode='choice')

		# Print message supplied in function call
		print(message)
		print("'0' to go back")
		if invalid:
			print('\ninvalid selection\n\n')
			invalid = False
		user_input = input(': ')

		# Options to go back, None indicates no selection made
		if user_input == '0':
			return None

		# validate user input, should be a single letter

		# Avoid empty string error
		if len(user_input) == 1:

			# convert to index 'A'=0,'B'=1...
			user_input = ord(unidecode(user_input.upper())[0])-65
			# verify input in range
			if user_input in range(len(entries)):
				# return valid selection
				return user_input

		# invalid, repeat loop
		invalid = True
# END SELECT ENTRY

def get_entry_string(entries, mode=''):
	string = ""
	if mode == 'choice':
		string += figlet_format("ENTRY OPTIONS:",font='cybermedium',width=150)
		string += "**************\n\n"
	else:
		string += figlet_format("CURRENT WORD:",font='cybermedium',width=150)
		string += "*************************\n\n"

	# Loop to print entries
	for index in range(len(entries)):

		# mode '1' print capital letters new to part of speech for each entry
		if mode == 'choice':
			c = chr(index + 65)
			string += f"\n({c}). "

		# assign definitions to shorter name
		if mode == 'choice':
			string += edit_entry.get_entry(entries[index],'choice',trunc=True)	
		else:
			string += edit_entry.get_entry(entries[index],'plain',trunc=True)
		string += '\n'
	# print new line when finished
	string = string.strip("\n")
	return string


# PRINT ENTRIES
# # # # # # # # # # # # # # #
def print_entries(entries,mode=''):
	# mode 1 is options mode
	clear_screen()
	print(get_entry_string(entries,mode))
# END PRINT ENTRIES
