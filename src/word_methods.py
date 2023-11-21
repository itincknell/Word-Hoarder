
'''
Description:
	
	copy word:
		takes a fetch and new_word
		returns a new_word
		take a result from the wiktionary parser and
		copies a simpler version into a new_word taken as an argument

	getTags:
		takes a list of tags and allows user to add or delete tags
'''

#from get_simple import get_simple
from edit_dictionary import chop_parens
import re
from unidecode import unidecode
import get_selection
import copy


# REMOVE OR
# # # # # # # # # # 
def remove_or(text):
	text = text.split()
	offset = 0
	for i in range(len(text)):
		i = i - offset
		if text[i] == 'or':
			text[i-1] += ","
			del text[i]
			offset += 1
	new_text = ''
	for i in range(len(text)):
		new_text += text[i] + " "
	return new_text
# END REMOVE OR

# VERB EDIT
# # # # # # # # # 
def verb_edit(text):
	# slip definitions into individual words
	text = text.split(" ")

	offset = 0
	# delete 'I's replace 'am's with 'be'
	for num in range(len(text)):
		num = num - offset
		if text[num] == "I":
			del text[num]
			offset += 1
		elif text[num].strip(";,") == "myself":
			text[num] = text[num].replace("myself","oneself")
		elif text[num] == "am":
			text[num] = "be"
		elif text[num] == "my":
			text[num] = "one's"

	# recombine word
	new_text = ''
	for num in range(len(text)):
		if num < len(text) - 1:
			new_text += text[num] + " "
		else:
			new_text += text[num]
	return new_text
# VERB EDIT


# PARTICIPLE EDIT
# # # # # # # # # # 
def participle_edit(text,first):
	text = list(text)
	new_text = ''
	for num in range(len(text)):
		if text[num] == chr(160):
			text[num] = chr(32)
		new_text += text[num]
	text = new_text
	text = re.split(",|;|:",text)

	offset = 0
	string_bank = ['having been','having']
	for i in range(len(text)):
		i = i - offset
		for string in string_bank:
			if string in text[i]:
				cut = text[i][text[i].find(string + " ") + len(string) + 1:].strip('. ')
				if cut in text or " " + cut in text:
					del text[i]
					offset += 1
					break

	for num in range(len(text)):
		if 'which is to be' in text[num] and not first:
			#print(text[num])
			cut = text[num].find('to be ') + 6
			text[num] = text[num][cut:]
			#print(text[num])
			text[num] = remove_or(text[num])
		elif 'which is to be' in text[num]:
			first = False
			text[num] = remove_or(text[num])


	new_text = ''
	for num in range(len(text)):
		if num < len(text) - 1:
			new_text += text[num].strip() + ", "
		else:
			new_text += text[num].strip()
	return new_text, first
# END PARTICPLE EDIT

# COPY WORD
# # # # # # # # # # # # # 
def copy_word(fetch_word,new_word,language):

	# Declare components of new_word
	new_word['heading'] = None
	entries = []
	entry = {}
	partOfSpeech = []
	principleParts = []
	simpleParts = []
	senses = []
	roots_list = []

	# for Loop LEVEL ONE, may contain empty 'definitions'
	for outer in range(len(fetch_word)):

		if fetch_word[outer]['etymology'] != '':
			etymology = fetch_word[outer]['etymology']
		else:
			etymology = ''

		# If not empty...
		if fetch_word[outer]['definitions'] == []:
			principleParts = simpleParts = partOfSpeech = '*blank definition*'
			# Create new entry
			entry['partOfSpeech'] = partOfSpeech
			entry['principleParts'] = principleParts
			entry['simpleParts'] = simpleParts
			entry['senses'] = []
			entry['etymology'] = etymology

			# append entry to entries
			entries.append(entry)

			# reset entry to blank dict
			entry = {}
		else:
			# for Loop LEVEL TWO, copy info into new word components
			for middle in range(len(fetch_word[outer]['definitions'])):

				# copy definitions text list into new list with shorter name
				text = fetch_word[outer]['definitions'][middle]['text']

				# capture heading (only one needed per word)
				if new_word['heading'] == None:
					# heading should have same number of characters as handle
					# compare de-macroned version of text[0] with handle
					# if text[0] starts with something else; heading will just be handle
					if unidecode(text[0][:len(new_word['handle'])]) != new_word['handle']:
						new_word['heading'] = new_word['handle']
					else:
						# should be the same number of character as handle
						new_word['heading'] = text[middle][:len(new_word['handle'])]

				# capture part of speech
				partOfSpeech = fetch_word[outer]['definitions'][middle]['partOfSpeech']

				# How many lines in the definition (including principal parts)
				num_entries = len(text)

				# for Loop LEVEL THREE, loop through text[:] to copy definitions
				first = True
				for inner in range(num_entries):

					# Copy definition
					text = fetch_word[outer]['definitions'][middle]['text'][inner]

					# Capture principal parts (first entry in ^ 'text')
					if inner == 0:
						principleParts = text
						# call get_simple to simplify principle parts, remove extraneous words
						simpleParts = principleParts #get_simple(partOfSpeech,principleParts,new_word['heading'],language)

					# Appends definitions to definitions componant
					else:
						if partOfSpeech == 'verb':
							text = verb_edit(text)
						
						if partOfSpeech == 'participle':
							text, first = participle_edit(text,first)


						senses.append(text.strip(".").replace(":",";"))
				
				# check if entry is a form of another main entry
				roots_list = find_root(roots_list,senses,etymology)

				# Create new entry
				entry['partOfSpeech'] = partOfSpeech
				entry['principleParts'] = principleParts
				entry['simpleParts'] = simpleParts
				entry['senses'] = senses
				entry['etymology'] = etymology

				# reset senses to empty list
				senses = []

				# append entry to entries
				entries.append(entry)

				# reset entry to blank dict
				entry = {}

		# Back to Loop LEVEL ONE

	# When Loop LEVEL ONE has finished all iterations

	# assign entries to new_word
	new_word['entries'] = entries

	if roots_list:
		new_word['roots'] = roots_list

	return new_word
# END COPY WORD


# FIND ROOT
# # # # # # # # # # # # # # # # # 
def find_root(roots_list,text,etymology):

	test = False


	trial_list = [copy.deepcopy(etymology)] + copy.deepcopy(text) if etymology else copy.deepcopy(text)
	trial_list = chop_parens(trial_list)

	if test:
		print(trial_list)


	word_bank = ['first-person','second-person','third-person','singular',
	'plural','indicative','imperative','infinitive','subjunctive','active','passive',
	'present','future','perfect','imperfect','pluperfect','participle',
	'masculine','feminine','neuter','common','nominative','comparative','degree',
	'genitive','dative','accusative','ablative','locative','vocative',
	'gerund','gerundive','inflection','supine','alternative','archaic','form','of','from'
	]
	for index in range(len(trial_list)):

		if 'participle of' in trial_list[index]:
			if test:
				print(trial_list[index])
			trial_list[index] = trial_list[index][trial_list[index].find('participle of'):]
			if test:
				print(trial_list[index])
			trial_list[index] = trial_list[index].split()
			trial_list[index].remove('participle')
			trial_list[index].remove('of')
			if test:
				print(trial_list[index])
			roots_list.append(trial_list[index][0].strip(".,; "))
			if test:
				print(trial_list[index][0])
			continue

		trial_list[index] = trial_list[index].strip(';, ')			
		if ',' in trial_list[index] or ';' in trial_list[index]:
			if test:
				print("Continue 1")
			continue





		string = trial_list[index]
		string = string.split(' ')
		if len(string) == 1:
			if test:
				print("Continue 2")
			continue

		offset = 0
		for index in range(len(string)):
			index = index - offset
			string[index] = string[index].strip("().")
			string[index] = string[index].lower()
			if '/' in string[index]:
				string.extend(string[index].split('/'))
				del string[index]
				offset += 1


		for word in word_bank:	
			if test:
				print(F"{word} {string}")
			if word in string:
				if test:
					print(f"{word} removed")
				string.remove(word)

		string[0] = string[0].strip(".,:;\n")

		if len(string) == 1 and string[0] not in roots_list:
			if test:
				print(f"{string[0]} being added to Roots")
			roots_list.append(string[0])
	if test:
		print("Roots test completed")
	return roots_list
# END FIND ROOT


# GET TAGS
# # # # # # # # 
def getTags(tags=set(),mode='',master_list=[]):

	# Whole function contained in loop
	while True:

		# flag if tags already in place
		if tags:

			# create list of tags
			tag_string = ", ".join(f"'{tag}'" for tag in tags)

			# Print list with appropriate commas
			if mode:
				print(f"\n{mode.title()} tags: {tag_string}")
			else:
				print(f"\nCurrent tags: {tag_string}")

		if mode:
			string = mode.title() + " "
		else:
			string = ''

		# Display options
		options = {
		'0':f"{string}Tag Options:\n>'0' to finish\n"}
		if mode == '':
			options.update({'1':">'1' to add a new tag\n"})
		options.update({'2':">'2' to choose from a list of all tags\n"})
		# only display if tags not empty
		if tags:
			options.update({'3':">'3' to Remove\n",
				'4':">'4' to clear all\n"})
		if master_list:
			options.update({})
		user_input = get_selection.get_selection(options)

		# Option to finish, return to calling function
		if user_input == '0':
			return tags

		# Option to add new tag
		elif user_input == '1':
			new_tag = input("Enter new tag: ")
			tags.add(new_tag)
		# Option to remove tag

		elif user_input == '3':
			options = {'0':"Select the tag you want to remove ('0' to go back)\n"}
			tags_list = list(tags)  # convert set to list
			for index in range(len(tags_list)):
				options[f"{index+1}"] = f"{index + 1}. {tags_list[index]}\n"
			user_input = get_selection.get_selection(options)

			if user_input != '0':
				del tags_list[int(user_input) - 1]
				tags = set(tags_list)  # convert list back to set


		# Option to clear all tags
		elif user_input.lower() == '4':
			tags = set()

		# option to choose from master list
		elif user_input.lower() == '2':
			exit_choose = False
			# delete all redundant entries
			offset = 0
			for index in range(len(master_list)):
				if master_list[index - offset] in tags:
					del master_list[index - offset]
					offset += 1

			# loop for user selections
			while not exit_choose:
				options = {}
				for index in range(len(master_list)):
					options[f"{index+1}"] = f"{index + 1}. {master_list[index]}\n"
				options.update({'0':"Select the tag you want to add to your current tags\n"})
				options.update({'00':"('0' to go back, '00' to finish)\n"})
				user_input = get_selection.get_selection(options)

				if user_input == '0':
					exit_choose = True
				elif user_input == '00':
					return tags
				else:
					tags.add(master_list[int(user_input) - 1])
					del master_list[int(user_input) - 1]
					tag_string = ", ".join(f"'{tag}'" for tag in tags)
					if mode == 'filter':
						print(f"Filter by tags: {tag_string}")
					else:
						print(f"Current tags: {tag_string}")
# END GET TAGS


# GET MASTER LIST
# # # # # # # # # # 
def get_master_list(current_dict):
	master_list = []
	# get list of all unique tags in current dictionary
	for word in current_dict['definitions']:
		for tag in word['tags']:
			if tag not in master_list:
				master_list.append(tag)
	return master_list
# END GET MASTER LIST
