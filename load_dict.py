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
#import parser_shell

# save cwd into global var
global CWD
CWD = os.path.dirname(os.getcwd()) 

# CHANGE PATH
# # # # # # # # # 
def change_path(folder=''):
	path = os.path.join(CWD,folder)
	if not os.path.isdir(path):
		os.mkdir(path)
	os.chdir(path)
# END CHANGE PATH




# FIND DICT
# # # # # # # 
def find_dict():
	change_path('dictionaries')
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
	change_path('dictionaries')
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
		change_path('dictionaries')
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
		'''
		for j in range(len(combo_dict['definitions'][i]['entries'])):
			def_tags = []
			for k in range(len(combo_dict['definitions'][i]['entries'][j]['defs'])):
				if combo_dict['definitions'][i]['entries'][j]['defs'][k][-1] in bank:
					def_tags.append(combo_dict['definitions'][i]['entries'][j]['defs'][k][-1])

			if def_tags:
				handle = combo_dict['definitions'][i]['handle']
				for x in range(len(current_dict['definitions'])):
					if current_dict['definitions'][x]['handle'] == handle:
						if j in range(len(current_dict['definitions'][x]['entries'])):
							if len(current_dict['definitions'][x]['entries'][j]['defs']) == len(combo_dict['definitions'][i]['entries'][j]['defs']):
								for tag in def_tags:
									current_dict['definitions'][x]['entries'][j]['defs'][0]['gloss'] += tag
		'''
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

# EXTRACT LIST
# # # # # # # # # # # # # # # 
def extract_list(current_dict,mode=0):

	change_path('lists')
	myFiles = glob.glob('*.txt')
	if myFiles == []:
		print("\nSorry no saved lists")
		return 
	else:
		options = {'0':f"\nChoose from the following files: (0 to go back)\n"}
		for index in range(len(myFiles)):
			options[f"{str(index + 1)}"] = f"{index + 1}. {myFiles[index]}\n"
		user_input = get_selection(options)
		if user_input == '0':
			return 
		else:
			with open(myFiles[int(user_input)-1],'r') as file:
				word_list = [unidecode(line).strip("\n\t, ") for line in file.readlines()]

		new_dictionary = {'definitions':[],'file':'','language':'Latin'}
	while True:
		if mode == 1:
			file_name = input("Enter name of new dictionary ('0' to go back): ")
			if file_name == '0':
				return
			else:
				user_input = pick_language()
				if user_input == None:
					continue
				else:
					new_dictionary['language'] = user_input
					new_dictionary['file'] = file_name + ".txt"
		else:
			new_dictionary['language'] = current_dict['language']
			new_dictionary['file'] =  myFiles[int(user_input)-1]

		#new_dictionary['file'] = file_name + ".txt"
		tag = ''
		user_input = input("Enter a tag to apply to dictionary entries (max=1,'0' to skip): ")
		if user_input != '0':
			tag = user_input



		if new_dictionary['language'] != 'Latin':
			#dump_dict = parser_shell.load_dump(new_dictionary['language'])
			for word in word_list:
				for i in range(len(dump_dict['definitions'])):
					if dump_dict['definitions'][i]['handle'] == word:
						dump_dict['definitions'][i]['tags'].append(tag)
						new_dictionary['definitions'].append(copy.deepcopy(dump_dict['definitions'][i]))
		else:
			alpha = {'a':[],
			'b':[],
			'c':[],
			'd':[],
			'e':[],
			'f':[],
			'g':[],
			'h':[],
			'i':[],
			'j':[],
			'k':[],
			'l':[],
			'm':[],
			'n':[],
			'o':[],
			'p':[],
			'q':[],
			'r':[],
			's':[],
			't':[],
			'u':[],
			'v':[],
			'w':[],
			'x':[],
			'y':[],
			'z':[],
			'misc':[]}
			for key in alpha:
				alpha[key] = parser_shell.load_big_language(key,current_dict['language']) 
			
			for word in word_list:
				if word[0].lower() not in 'abcdefghijklmnopqrstuvwxyz':
					key = 'misc'
				else:
					key = word[0].lower()
				for i in range(len(alpha[key]['definitions'])):
					if unidecode(alpha[key]['definitions'][i]['handle']) == unidecode(word):
						alpha[key]['definitions'][i]['tags'].append(tag)
						new_dictionary['definitions'].append(copy.deepcopy(alpha[key]['definitions'][i]))
		if mode == 1:
			change_path('dictionaries')
			with open(new_dictionary['file'],mode = 'wb') as openFile:
				pickle.dump(new_dictionary, openFile)
			print(f"{new_dictionary['file']} successfully saved")
		else:
			combine_dict(current_dict,new_dictionary)
		return







