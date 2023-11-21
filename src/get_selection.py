'''
Description:

	get_selection:
		takes message and a list and/or dict
		requests, validates, and returns a user input
'''
from unidecode import unidecode
import unicodedata
import os

# CLEAR SCREEN
def clear_screen():
	if os.name == 'posix':  # For UNIX or Linux or MacOS
		os.system('clear')
	elif os.name == 'nt':  # For Windows
		os.system('cls')

def visible_len(s):
    return len([c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'])

def get_selection(options, message=""):
	invalid = False
	while True:
		clear_screen()  # Uncomment this if you have a clear_screen function
		if message:
			print(message)

		if len(options) > 30:
			print_columns(options)
		else:
			for key, value in options.items():
				if value != '':
					print(value.rstrip('\n'))

		if invalid:
			print("\nInvalid selection\n\n")
			invalid = False

		user_input = unidecode(input(": ")).lower()

		if user_input in options:
			return user_input
		else:
			invalid = True

def print_columns(options,field=25):
	limit = 40
	keys = list(options.keys())
	special_keys = ['0', '00']

	# Separate special keys from the rest
	regular_keys = [k for k in keys if k not in special_keys]

	# Calculate the number of columns needed
	num_columns = len(regular_keys) // limit + 1
	row_string = ''
	for i in range(limit):
		for col in range(num_columns):
			idx = i + limit * col
			if idx >= len(regular_keys):
				continue

			option_str = options[regular_keys[idx]].rstrip('\n')
			while visible_len(option_str) < field:
				option_str += " "
			if visible_len(option_str) > field and field != 40:
				clear_screen()
				print_columns(options,40)
				return
			row_string += f"{option_str}"

		print(row_string)
		row_string = ''

	# Print special keys at the end
	for key in special_keys:
		if key in options:
			print(options[key], end='')


'''
# GET SELECTION
# # # # # # # # # # # # # # 
def get_selection(options,message=""):
	# whole function contained in loop
	invalid = False
	while True:
		clear_screen()
		if message:
			print(message)

		if len(list(options.keys())) > 30:
			print_columns(options)
		else:
			for key in options:
				print(f"{options[key]}",end='')
		if invalid:
			print("\ninvalid selection\n\n")
			invalid = False
		user_input = unidecode(input(": "))

		# check if input matches and keys in options
		if user_input.lower() in options:
			return user_input
		else:
			invalid = True
			

# END GET SELECTION

def print_columns(options):
	limit = 50
	keys = list(options.keys())
	if '0' in keys:
		end = ['0']
		keys.remove('0')
	if '00' in keys:
		end.append('00')
		keys.remove('00')
	L = len(keys)
	if L > 1000:
		print_bigger_columns()
	else:
		step = L // limit + 1
		for i in range(0,limit):
			for x in range(step):
				q = i + limit * x
				if q >= L:
					continue
				else:
					fill_char = ' '
					# using .format()
					print_str = "{message:{fill}<30}".format(message=options[keys[q]], fill=fill_char)
					def multi_replace(string):
						replacements = [ ('θ','t'), ('ψ','s'), ('φ','f'), ('̓',''), ]
						for old, new in replacements:
							string = string.replace(old, new)
						return string
					len_str = multi_replace(print_str)
					while len(len_str) < 25:
						len_str += "#"
						print_str += "#"
					while len(print_str) > 25:
						len_str = len_str[:-1]
						print_str = print_str[:-1]
					print(print_str, end='')
					
			print()
		for key in end:
			print(options[key],end="")
			
'''	




def print_bigger_columns(options):
	pass