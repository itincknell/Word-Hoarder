import parser_shell
from load_dict import *
import word_methods
import edit_dictionary
from get_selection import get_selection, clear_screen
import convert_file_utilities
import os
import tables
from pyfiglet import figlet_format

# Print welcome message
# # # # # # # # # # # # 
clear_screen()
message = ''
for i in range(5):
	if i%2 == 0:
		message += "\n" + "Ξ " * (75)
	else:
		message += "\n" + "Σ " * (75)

middle = '\n\n'
middle += figlet_format("        Word-Hoarder +",font='epic',width=150)
message += middle
for i in range(5):
	if i%2 == 0:
		message += "\n" + "Ξ " * (75)
	else:
		message += "\n" + "Σ " * (75)
print(message)
input("\n\n\n\t\t\tMake sure the display fits your screen\n\t\t\tPress \'Enter\' to continue\n")

# Whole program contained in loop
# # # # # # # # # # # # # # # # # 
exit_loop_1 = False
user_input = None
current_dict = None
while not exit_loop_1:

	# set/reset flag for second loop
	exit_loop_2 = False
	 
	options = {
	'1':"\nMain Menu:\n==================================\n>'1' Open saved dictionary\n",
	'2':">'2' Create new dictionary\n",
	'3':">'3' Data files\n",
	'0':">'0' to exit\n"
	}
	user_input = get_selection(options,message)
	message = ''
	# Terminate program
	if user_input == '0':
		exit_loop_1 = exit_loop_2 = True
		continue

	# function calls to load or create a dictionary
	# # # # # # # # # # # # # # # # # # # # # # # # 
	elif user_input == '1':
		current_dict = find_dict()
	elif user_input == '2':
		current_dict = create_dict()
	elif user_input == '3':
		convert_file_utilities.convert_files()

	# find/create will return {} if dict not loaded
	# must have a valid dictionary to proceed to new loop
	if current_dict == None:
		continue

	# inner Loop to get valid user input
	# # # # # # # # # # # # # # # # # # 
	
	while not exit_loop_2:
		# Print Options
		options = {
		'1':f"\n{current_dict['file']} options:\n==================================\n>'1' to look up words\n",
		'2':">'2' to save formatted flashcards\n",
		'3':">'3' to save gloss\n",
		'4':">'4' to edit dictionary\n",
		'5':">'5' to combine dictionaries\n",
		'6':">'6' add words from list\n",
		'0':">'0' to go back\n"
		}
		user_input = get_selection(options)

		# Return previous loop: dictionary selection
		if user_input == '0':
			exit_loop_2 = True
			current_dict = None

		# functions calls to add words to dictionary or print dictionary
		# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
		elif user_input == '1':
			current_dict, quit = parser_shell.add_word_options(current_dict)
			if quit:
				exit_loop_1 = exit_loop_2 = True
		elif user_input == '2':
			tables_list = tables.get_tables(current_dict['language'])
			tables.print_tables(tables_list,current_dict['language'])
			edit_dictionary.print_dict(current_dict)
			input("Press enter to Continue")
		elif user_input == '3':
			edit_dictionary.print_gloss_setup(current_dict)
		elif user_input == '4':
			current_dict = edit_dictionary.edit_dictionary(current_dict)
		elif user_input == '5':
			current_dict = combine_dict(current_dict)
		elif user_input == '6':
			extract_list(current_dict)

print("\n\nGood Bye")
# End Main
