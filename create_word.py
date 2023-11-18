'''
Description:

	create word:
		create a new word based on user input
		intended to be used if valid latin word cannot be retrieved by wiktionary parser

	create entry:
		create a new entry within a word
		used by create_word and by word_print_edit.edit_entries
'''

from unidecode import unidecode
import pickle

import parser_shell
import word_print_edit
import edit_entry
import load_dict
# CREATE WORD
# # # # # # # # # # # 
def create_word(current_dict,tags):

	# Create new word, first tag is file name - .txt
	new_word = {'tags':tags}

	# begin user input loop
	exit_loop = False
	while not exit_loop:
		print("\nEnter new word heading ('0' to exit) (ā, ē, ī, ō, ū)")
		user_input = input(': ')

		# option to go back, return to calling function
		if user_input == '0':
			return current_dict
		
		# assign input to heading; un-macroned version to handle
		new_word['heading'] = user_input
		new_word['handle']  = unidecode(user_input)

		# create empty entries list
		new_word['entries'] = []

		# call create entry, returns False if creation not completed
		new_word, exit_loop = create_entry(new_word)

	# End while Loop only if complete word is created
	# Send new word to edit entry to add additional definitons etc.
	new_word['entries'][0], dummy = edit_entry.edit_entry(new_word['entries'][0],new_word)

	# call word options, from here return
	load_dict.change_path('dumps sorted')
	if current_dict['language'] == 'Latin' or current_dict['language'] == "Ancient Greek":
		wiki_dump = parser_shell.load_big_language(new_word['heading'][0],current_dict['language'])
	else:
		wiki_dump = parser_shell.load_dump(current_dict['language'])
	parser_shell.save_word(new_word,wiki_dump,2)
	current_dict = parser_shell.save_word(new_word,current_dict)
	return current_dict
# END CREATE WORD


# CREATE ENTRY
# # # # # # # # # # # 
def create_entry(new_word):

		# copy heading to shorter name
		heading = new_word['heading']
		# create empty entry to be added to
		entry = {}

		# Start series of ascending loops
		# # # # # # # # # # # # # # # # # 

		# Begin Loop LEVEL ONE: part of speech
		while True:

			print(f"\nEnter part of speech for '{heading}'")
			print("'0' to go back")
			user_input = input(': ')

			# go back, word cancelled
			if user_input == '0':
				return new_word, False 

			# add to entry, proceed to next inner loop
			entry['partOfSpeech'] = user_input

			# Begin Loop LEVEL TWO: etymology
			while True:

				print(f"\nEnter etymology for '{heading}'")
				print("'0' to go back\n'1' to go back\n'2' to skip")
				user_input = input(': ')

				# go back, word cancelled
				if user_input == '0':
					return new_word, False 

				elif user_input == '1':
					break

				# add to entry, proceed to next inner loop
				elif user_input != '2':
					entry['etymology'] = user_input
				else:
					entry['etymology'] = ''

				# begin loop LEVEL THREE: principal parts
				while True:

					print(f"\nEnter principle parts for '{heading}' (ā, ē, ī, ō, ū)")
					print("'0' to exit")
					print("'1' to go back")
					user_input = input(': ')

					# exit, word cancelled
					if user_input == '0':
						return new_word, False
					# go back to previous level
					elif user_input == '1':
						break

					# simple/principal the same for created word
					entry['principleParts'] = user_input
					entry['simpleParts'] = user_input

					# Begin Loop LEVEL FOUR: 1st definition
					while True:

						print(f"\nEnter '{heading}' definition")
						print("'0' to exit")
						print("'1' to go back")
						user_input = {'gloss':input(': ')}

						# exit, word cancelled
						if user_input == '0':
							return new_word, False
						# go back to previous level
						elif user_input == '1':
							break

						user_input['tags'] = []
						while True:
							print("Enter definition tags ('0' to finish)")
							new_tag = input(": ")
							if new_tag == '0':
								break
							else:
								user_input['tags'].append(new_tag)
						# assign to entry defintions list
						entry['defs'] = [user_input]

						# append new entry to new word, return True
						new_word['entries'].append(entry)
						return new_word, True
# END CREATE ENTRY
