'''
Description:

	get_selection:
		takes message and a list and/or dict
		requests, validates, and returns a user input
'''
from unidecode import unidecode
import unicodedata
import os


def clear_screen():
	# CLEAR SCREEN
	if os.name == 'posix':  # For UNIX or Linux or MacOS
		os.system('clear')
	elif os.name == 'nt':  # For Windows
		os.system('cls')

def visible_len(s):
	''' Returns the visible length of unicode characters for correct columns justification 
	'''
	return len([c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'])


def fancy(message):
	# return message with an underline of '='s for menus
	return message + '\n' + '=' * min(len(message),30)

def get_selection(options, message=""):
	'''	Take a dictionary of <options (1, 2, a, b, etc.)>:<options descriptions>
		Validates user input and returns choice
	'''
	invalid = False
	while True:
		clear_screen() 
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
	'''	print many options in columns
	'''
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

def print_bigger_columns(options):
	'''	hope to add paging functionality when columns don't fit in window
	'''
	pass