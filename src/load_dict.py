'''
Description:

	find_dict:
		allow user to select a previously saved dictionary

	open_dict:
		open a saved dictionary, copy definitions into 
		dictionary object taken as argument, 

	create_dict:
		name a new dictionary to be created
'''
import glob
import os
import pickle
import copy
from unidecode import unidecode

from get_selection import get_selection


# save PARENT_DIR into global var
global PARENT_DIR
# save the parent directory of the current file into a global variable
PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# define names for important directories
KAIKKI_JSON_FILES = 'kaikki_json_files'
SORTED_LANGUAGE_FILES = 'sorted_language_files'
SUPPLEMENTARY_LANGUAGE_FILES = 'supplementary_language_files'
USER_CREATED_DICTIONARIES = 'user_created_dictionaries'
FLASHCARD_TEMPLATE_FILES = 'flash_card_templates'
FORMATTED_FLASHCARD_FILES = 'formatted_flashcard_files'

# CHANGE PATH
# # # # # # # # # 
def change_path(folder=''):
	path = os.path.join(PARENT_DIR,folder)
	if not os.path.isdir(path):
		os.mkdir(path)
	os.chdir(path)
# END CHANGE PATH

# FIND DICT
# # # # # # # 
def find_dict():
	change_path(USER_CREATED_DICTIONARIES)
	myFiles = glob.glob('*.txt')
	if myFiles == []:
		print("\nSorry no saved dictionaries")
		return create_dict()
	else:
		options = {'0':f"\nChoose from the following files: (0 to go back)\n==================================\n"}
		for index in range(len(myFiles)):
			options[f"{str(index + 1)}"] = f"{index + 1}. {myFiles[index]}\n"
		user_input = get_selection(options)
		if user_input == '0':
			return None
	current_dict = {'file':myFiles[int(user_input)-1]}
	with open(current_dict['file'],mode= 'rb') as openFile:
		current_dict = pickle.load(openFile)  
	return current_dict
# END FIND DICT

# CREATE DICT
# # # # # # # # 
def create_dict():
	change_path(USER_CREATED_DICTIONARIES)
	myFiles = glob.glob('*.txt')
	while True:
		print("What do you want to name new dictionary?: (0 to go back)\n==================================\n")
		user_input = input(': ')
		if user_input == '0':
			return
		user_input += '.txt'
		exit_loop = True
		while exit_loop:
			if user_input in myFiles:
				print(f'\n{user_input} already exists, do you want to add to {user_input}?')
				options = {'1':"(1=yes, ",'1':"0 to go back): "}
				choice = get_selection(options)
				if choice == '1':
					current_dict = {'file':user_input}
					openFile = open(current_dict['file'],mode= 'rb')
					current_dict = pickle.load(openFile)
					openFile.close()    
					return current_dict
				elif choice == '0':
					exit_loop = True
			else: 
				current_dict = {'file':user_input}
				user_input = pick_language()
				if user_input != None:
					current_dict['language'] = user_input
					current_dict['definitions'] = []
					return current_dict
				else:
					exit_loop = True
# END CREATE DICT

# COMBINE DICT
# # # # # # # # # # # # 
def combine_dict(current_dict,combo_dict=[]):
	if combo_dict == []:
		change_path(USER_CREATED_DICTIONARIES)
		myFiles = glob.glob('*.txt')
		if current_dict['file'] in myFiles:
			myFiles.remove(current_dict['file'])
		if myFiles == []:
			print("\nSorry no other saved dictionaries")
			return current_dict
		else:
			options = {'0':f"\nChoose from the following files: (0 to go back)\n==================================\n"}
			for index in range(len(myFiles)):
				options[f"{str(index + 1)}"] = f"{index + 1}. {myFiles[index]}\n"
			user_input = get_selection(options)
			if user_input == '0':
				return current_dict
			combine_file = myFiles[int(user_input) - 1]
			with open(combine_file,mode= 'rb') as openFile:
				combo_dict = pickle.load(openFile)

	# FIX DROPPED SOURCE TAGS
	bank = ["*","^","†","∆"]
	counter = 0
	for i in range(len(combo_dict['definitions'])):
		handle = combo_dict['definitions'][i]['handle']
		found = False
		for k in range(len(current_dict['definitions'])):
			if current_dict['definitions'][k]['handle'] == handle:
				found = True
				current_dict['definitions'][k]['tags'].extend(combo_dict['definitions'][i]['tags'])
				break
		if found == False:
			current_dict['definitions'].append(combo_dict['definitions'][i])
			counter += 1
		
	current_dict['definitions'].sort(key=lambda item: item.get('handle').lower())
	with open("test" + current_dict['file'] ,mode = 'wb') as openFile:
		pickle.dump(current_dict, openFile)
	print(f"\n{combo_dict['file']} successfully combined with {current_dict['file']}")
	print(f"{counter} new words added\n")
	return current_dict
# END COMBINE DICT


def pick_language():

	language_options = ["Latin","Ancient Greek","Old English"]

	options = {'0':"\nChoose the language for your new dictionary ('0' to go back)\n==================================\n"}
	for i in range(len(language_options)):
		options.update({f"{i+1}":f"{i+1}. {language_options[i]}\n"})
	user_input = get_selection(options)
	if user_input == '0':
		return None
	else:
		return language_options[int(user_input)-1]
