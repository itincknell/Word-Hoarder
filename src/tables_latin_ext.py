
from bs4 import BeautifulSoup

import tables
from load_dict import change_path, FORMATTED_FLASHCARD_FILES, FLASHCARD_TEMPLATE_FILES, SUPPLEMENTARY_LANGUAGE_FILES
from get_selection import get_selection
from copy import deepcopy
from unidecode import unidecode
import flashcard_html_utilities
import random
import sys
import json
import glob


def new_template(heading="",handle="",definition="",POS=""):
	template = {}
	while True:
		x = 'POS'
		if POS != "verb" and POS != "noun" and POS != "adjective":
			print("Enter choose template {x} ('0' to go back)")
			print("'1'> noun/adj.")
			print("'2'> verb")
			print("type description for other (e.g. 'particle', 'not comparable', 'indeclinable')")
			user_input = input(": ")
			if user_input == '0':
				break
			elif user_input == '00':
				return
			elif user_input == '1':
				template[x] = 'noun/adj.'
			elif user_input == '2':
				template[x] = 'verb' 
			else:
				template[x] = user_input
		elif POS == "noun" or POS == "adjective":
			template[x] = 'noun/adj.'
		elif POS == "verb":
			template[x] = 'verb'

		if template[x] == 'noun/adj.':
			x = 'gender'
			options = {'0':f"Enter choose template {x} ('0' to go back)\n",
					'1':"'1'> (m)\n",
					'2':"'2'> (f)\n",
					'3':"'3'> (m or f)\n",
					'4':"'4'> (n)\n",
					'5':"'5'> (m,f,n)\n",
					'6':"'6'> (m/f,n)\n",
					'7':"'7'> (m/f/n)\n",
					'00':"'00' to quit\n"}
			user_input = get_selection(options)
			if user_input == '0':
				break
			elif user_input == '00':
				return
			else:
				template[x] = options[user_input][options[user_input].find("("):].strip("\n")
				print("Proper noun? ('Y' for yes, any other key for no)")
				user_input = input(": ")
				template['proper'] = True if user_input.upper() == 'Y' else False
		while True:
			x = 'title'
			if heading == "":
				print(f"Enter template {x} ('0' to go back)")
				user_input = input(": ")
				if user_input == '0':
					break
				elif user_input == '00':
					return
				else:
					template[x] = user_input
			else:
				template[x] = heading
			x = 'search word'
			if template['POS'] != 'noun/adj.' and template['POS'] != 'verb':
				template['search word'] = None
			elif handle == "":
				template[x] = unidecode(user_input)
			else:
				template[x] = handle
			while True:
				if template['POS'] != 'noun/adj.' and template['POS'] != 'verb':
					template['defno'] = None
				else:
					print("Enter definition number ('0' if unspecified)")
					try:
						template['defno'] = int(input(": "))
					except:
						print("Invalid entry")
						continue

				template = get_forms(template)
				print(template['principal'])
				print_parts(template['parts'])
				x = 'definition'
				if definition == "":
					print(f"Enter template {x} ('0' to go back '00' to quit)")
					user_input = input(": ")
					if user_input == '0':
						continue
					elif user_input == '00':
						return
					else:
						template[x] = user_input
				else:
					template[x] = definition
				return template	

def edit_template(template):
	while True:
		options = {'1':f"Template \"{template['title']}\" options:\n'1' change definition\n",
					'2':"'2' to display forms\n",
					'3':"'3' to re-do forms\n",
					'4':"'4' to delete\n",
					'0':"'0' to go back\n"}
		user_input = get_selection(options)

		if user_input == '1':
			print(f"Current definition: {template['definition']}")
			user_input = input("Enter new definition ('0' to cancel): ")
			if user_input == '0':
				continue
			else:
				template['definition'] == user_input
		elif user_input == '2':
			print(template['principal'])
			print_parts(template['parts'])
			input("\n\nPress Enter to continue\n")
		elif user_input == '3':
			template = get_forms(template)
		elif user_input == '4':
			del template
			return
		elif user_input == '0':
			return



def print_parts(chunk,string='',outer_key=''):
	if string != '' or outer_key != '':
		string += " " + outer_key
	if type(chunk) == dict:
		for inner_key in chunk:
			print_parts(chunk[inner_key],string,inner_key)
	else:
		if chunk != '---' and chunk != "–":
			final_str = f"{string.lstrip():_<70}" + chunk
			print(final_str)

def get_forms(template):
	if template['POS'] != 'noun/adj.' and template['POS'] != 'verb':
		template['forms'] = [{'form':template['title']}]
		template['principal'] = template['title'] + " (" + template['POS'] + ")"
		template['parts'] = {'single form':template['title']}
		return template
	if template['POS'] == 'noun/adj.':
		template['parts'] = retreive_noun_forms(template)
		if template['gender'] == '(m,f,n)':
			template['parts'] = fix_two_ending(template['parts'])
			parts = template['parts']['Nominative']['Singular']
			template['principal'] = ", ".join([x for x in parts.values()])
			template['forms'] = inside_out_multi_noun(template['parts'])
		elif template['gender'] == '(m/f,n)':
			#print(template['parts']['Nominative']['Singular'])
			template['parts'] = fix_two_ending(template['parts'])
			parts = template['parts']['Nominative']['Singular']
			template['principal'] = ", ".join([y for x,y in parts.items() if x != 'Feminine'])
			template['forms'] = inside_out_multi_noun(template['parts'])
		elif template['gender'] == '(m/f/n)':
			template['parts'] = fix_two_ending(template['parts'])
			part = template['parts']['Nominative']['Singular']["Masculine"]
			nom = part
			part = template['parts']['Genitive']['Singular']["Masculine"]
			gen = part
			template['principal'] = nom + ", " + gen
			template['forms'] = inside_out_noun(template['parts'])
		else:
			part = template['parts']['Nominative']['Singular']
			nom = part
			part = template['parts']['Genitive']['Singular']
			gen = part
			template['principal'] = nom + ", " + gen + template['gender']
			template['forms'] = inside_out_noun(template['parts'])
	elif template['POS'] == 'verb':
		template['parts'] = retreive_verb_forms(template)
		result = assign_principle_parts({},template['parts'])
		result = [y['Principal Part'] for y in result['parts'].values()]
		template['principal'] = ", ".join(result)
		print("GETTING FORMS")
		template['forms'] = inside_out_verb(template['parts'])
	return template

def redo(templates):
	for template in templates:
		template = get_forms(template)
	return templates

def fix_two_ending(parts):
	for case in parts:
		for number in parts[case]:
			if parts[case][number]["Feminine"] == "---":
				parts[case][number]["Feminine"] = deepcopy(parts[case][number]["Masculine"])
			if parts[case][number]["Neuter"] == "---":
				parts[case][number]["Neuter"] = deepcopy(parts[case][number]["Masculine"])
	return parts


def remove_emdash(forms):
	for form in forms:
		if form['form'] == '—':
			del form


def inside_out_multi_noun(parts):
	forms = []
	print(parts)
	for case in parts:
		for number in parts[case]:
			for gender in parts[case][number]:
				if parts[case][number][gender] != "—":
					if "," in parts[case][number][gender]:
						for x in parts[case][number][gender].split(","):
							form = {'form':x.strip()}
							form['case'] = case
							form['number'] = number
							form['gender'] = gender
							forms.append(deepcopy(form))
					elif "/" in parts[case][number][gender]:
						for x in parts[case][number][gender].split("/"):
							form = {'form':x.strip()}
							form['case'] = case
							form['number'] = number
							form['gender'] = gender
							forms.append(deepcopy(form))
					else:
						print(f"{case} {number} {gender} = {parts[case][number][gender]}")
						form = {'form':parts[case][number][gender]}
						form['case'] = case
						form['number'] = number
						form['gender'] = gender
						forms.append(deepcopy(form))
	remove_emdash(forms)
	return forms

def inside_out_noun(parts):
	forms = []
	for case in parts:
		for number in parts[case]:
			if parts[case][number] != "—":
				if "," in parts[case][number]:
					for x in parts[case][number].split(","):
						form = {'form':x.strip()}
						form['case'] = case
						form['number'] = number
						forms.append(deepcopy(form))
				elif "/" in parts[case][number]:
					for x in parts[case][number].split("/"):
						form = {'form':x.strip()}
						form['case'] = case
						form['number'] = number
						forms.append(deepcopy(form))
				else:
					form = {'form':parts[case][number]}
					form['case'] = case
					form['number'] = number
					forms.append(deepcopy(form))
	remove_emdash(forms)
	return forms

def inside_out_verb(parts):
	change_path(SUPPLEMENTARY_LANGUAGE_FILES)
	with open('sum_forms.txt','r') as f:
		sum_forms = json.load(f)
	if parts['Present']['Active']['Indicative']['FPS'] == "sum":
		exception = True
	else:
		exception = False
	forms = []
	for tense in parts:
		for voice in parts[tense]:
			for mood in parts[tense][voice]:
				if mood == 'Infinitive':
					if parts[tense][voice][mood] != "---":
						if "," in parts[tense][voice][mood]:
							split = parts[tense][voice][mood].split(",")
							for x in split:
								if x.strip() in sum_forms and not exception:
									x = split[0][:split[0].find(" ")+1] + x.strip()
									print(x)
								form = {'form':x.strip()}
								form['tense'] = tense
								form['voice'] = voice
								form['mood'] = mood
								forms.append(deepcopy(form))
						elif "/" in parts[tense][voice][mood]:
							for x in parts[tense][voice][mood].split("/"):
								form = {'form':x.strip()}
								form['tense'] = tense
								form['voice'] = voice
								form['mood'] = mood
								forms.append(deepcopy(form))
						else:
							form = {'form':parts[tense][voice][mood]}
							form['tense'] = tense
							form['voice'] = voice
							form['mood'] = mood
							forms.append(deepcopy(form))
				elif mood == 'Participle':
					if parts[tense][voice][mood] != "---":
						if "," in parts[tense][voice][mood]:
							split = parts[tense][voice][mood].split(",")
							for x in split:
								if x.strip() in sum_forms and not exception:
									x = split[0][:split[0].find(" ")+1] + x.strip()
									print(x)
								form = {'form':x.strip()}
								form['tense'] = tense
								form['voice'] = voice
								form['mood'] = mood
								forms.append(deepcopy(form))
						elif "/" in parts[tense][voice][mood]:
							for x in parts[tense][voice][mood].split("/"):
								form = {'form':x.strip()}
								form['tense'] = tense
								form['voice'] = voice
								form['mood'] = mood
								forms.append(deepcopy(form))
						else:
							form = {'form':parts[tense][voice][mood]}
							form['tense'] = tense
							form['voice'] = voice
							form['mood'] = mood
							forms.append(deepcopy(form))
				else:
					for person in parts[tense][voice][mood]:
						if parts[tense][voice][mood][person] != "---":
							if "," in parts[tense][voice][mood][person]:
								split = parts[tense][voice][mood][person].split(",")
								for x in split:
									if x.strip() in sum_forms and not exception:
										x = split[0][:split[0].find(" ")+1] + x.strip()
										print(x)
									form = {'form':x.strip()}
									form['tense'] = tense
									form['voice'] = voice
									form['mood'] = mood
									form['person'] = person
									forms.append(deepcopy(form))
							elif "/" in parts[tense][voice][mood][person]:
								for x in parts[tense][voice][mood][person].split("/"):
									form = {'form':x.strip()}
									form['tense'] = tense
									form['voice'] = voice
									form['mood'] = mood
									form['person'] = person
									forms.append(deepcopy(form))
							else:
								form = {'form':parts[tense][voice][mood][person]}
								form['tense'] = tense
								form['voice'] = voice
								form['mood'] = mood
								form['person'] = person
								forms.append(deepcopy(form))
	remove_emdash(forms)
	return forms

def auto_parts(parts):
	print("Enter look up word")
	user_input = input(": ")
	result = retreive_verb_forms({'search word':user_input,'title':''})
	result = assign_principle_parts(result,result)
	result = [y['Principal Part'] for y in result['parts'].values()]
	result = ", ".join(result)
	print("Does this look right ('1' to except '0' to discard)?")
	print(result)
	user_input = input(": ")
	if user_input == '1':
		return result
	else:
		return parts

def assign_principle_parts(table_info,tenses,template=None):
	table_info['parts'] = {
		'Present':{'Principal Part':tenses['Present']['Active']['Indicative']['FPS']},\
		'Infinitive':{'Principal Part':tenses['Present']['Active']['Infinitive']},\
		'Perfect Act.':{'Principal Part':tenses['Perfect']['Active']['Indicative']['FPS']},\
		'Perfect Pas.':{'Principal Part':tenses['Perfect']['Passive']['Participle']}}
	if template:
		table_info['title'] = f"Principal Parts: {template['title']}"
	return table_info

def retreive_verb_forms(template):
	if 'specified' in template:
		specified = template['specified']
	else:
		specified = 0
	if template['search word'] == 'sum':
		exception = True
	else:
		exception = False

	html_doc = tables.get_html(template['search word'])
	if html_doc == None:
		return
	soup = BeautifulSoup(html_doc, 'html.parser')
	page_list = soup.prettify().split('\n')
	page_list = clean_page_list(page_list,exception)

	tenses = {"Present":'','Imperfect':'','Future':'','Future Perfect':'','Perfect':'','Pluperfect':''}
	voices = {"Active":'','Passive':''}
	moods = {'Indicative':[],'Subjunctive':[],'Imperative':[],"Infinitive":[],"Participle":[]}
	mood_list = ['Indicative','Subjunctive','Imperative']
	persons = {'FPS':'---','SPS':'---','TPS':'---','FPP':'---','SPP':'---','TPP':'---'}

	for tense in tenses:
		tenses[tense] = deepcopy(voices)
		for voice in tenses[tense]:
			tenses[tense][voice] = deepcopy(moods)
			for mood in tenses[tense][voice]:
				if mood in mood_list:
					tenses[tense][voice][mood] = deepcopy(persons)
				elif mood == 'Participle' or mood == 'Infinitive':
					tenses[tense][voice][mood] = '---'

	tense = False
	mood = False
	voice = False
	count = 0
	specified = 0
	for i in range(len(page_list)):
		if count < specified:
			if page_list[i].strip() == 'Conjugation of':
				count += 1
		elif page_list[i].strip() == "verbal nouns":
			break
		elif page_list[i].strip(": ").title() in mood_list:
			mood = page_list[i].strip(": ").title()
			voice = False
			tense = False
		elif page_list[i].strip(": ")[:-1].title() in ['Infinitive','Participle']:
			mood = page_list[i].strip(": ")[:-1].title()
			columns = ['Active','Passive']
			rows = ['Present','Perfect','Future','Present','Perfect','Future']
			index = 0
			continue
		elif mood in mood_list:
			if page_list[i].strip().title() in voices:
				voice = page_list[i].strip().title()
				index = 0
			elif voice:
				if page_list[i].strip().title() in tenses:
					tense = page_list[i].strip().title()
					index = 0
				elif tense:
					if index not in range(6):
						tense = False
					else:
						if tenses[tense][voice][mood][list(persons.keys())[index]] == '---':
							tenses[tense][voice][mood][list(persons.keys())[index]] = page_list[i].strip()
						index += 1
		elif mood in ['Infinitive','Participle']:
			if index == 6:
				mood = False
			else:
				tenses[rows[index]][columns[index//3]][mood] = page_list[i].strip()
				index += 1
	return tenses

def count_indent(a):
	return len(a) - len(a.lstrip())

def manual_sort(cases,case,holder,multi=True):
	print(f"\nSorting needed for {case} case")
	genders = {"M":"Masculine","F":"Feminine","N":"Neuter"}
	numbers = {"S":"Singular","P":"Plural"}
	while True:
		for word in holder:
			user_input = ""
			if multi:
				while True:
					print(f"Select gender for {word} ({case}) ('M', 'F', 'N') ('X' to discard)")
					user_input = input(": ")
					if user_input.upper() == "X":
						break
					if len(user_input) == 2:
						user_input = list(user_input)
						if user_input[0].upper() not in genders and user_input[1].upper() not in numbers:
							print("Invalid entry")
							continue
						else:
							gender = genders[user_input[0].upper()]
							number = numbers[user_input[1].upper()]
							break
					if user_input.upper() not in genders:
						print("Invalid entry")
						continue
					else:
						gender = genders[user_input.upper()]
						break
			if user_input == "X":
				break
			while True:
				if len(user_input) == 2:
					break
				print(f"Select number for {word} ({case}) ('S', 'P')")
				user_input = input(": ")
				if user_input.upper() not in numbers:
					print("Invalid entry")
					continue
				else:
					number = numbers[user_input.upper()]
					break
			if multi:
				if cases[case][number][gender] != "---":
					cases[case][number][gender] += ", " + word
				else:
					cases[case][number][gender] = word
			else:
				if cases[case][number] != "---":
					cases[case][number] += ", " + word
				else:
					cases[case][number] = word
		print("Like this? ('1' to accept, '2' to manually edit, any other key to try again)")
		print_parts(cases[case])
		user_input = input(": ")
		if user_input == '1':
			break
		elif user_input == '2':
			return manual_edit(cases,case)
		else:
			reset(cases[case])
	return cases

def reset(case):
	for key in case:
		if type(case[key]) == dict:
			reset(case[key])
		else:
			case[key] = "---"

def manual_edit(parts,case):
	while True:
		print("Select term to edit ('0' to finish)")
		index = 1
		key_holder = {}
		for number in parts[case]:
			if type(parts[case][number]) == dict:
				for gender in parts[case][number]:
					print(f"{index}. {case} {number} {gender} {parts[case][number][gender]}")
					key_holder[str(index)] = {'number':number,'gender':gender}
					index += 1
			else:
				print(f"{index}. {case} {number} {parts[case][number]}")
				key_holder[str(index)] = {'number':number}
				index += 1
		user_input = input(": ")
		if user_input == '0':
			return parts
		elif user_input in key_holder:
			keys = key_holder[user_input]
			print(f"Enter correct form for {case} {' '.join([x for x in key_holder[user_input].values()])} ('0' to go back)")
			user_input = input(": ")
			if user_input == '0':
				continue
			if 'gender' in keys:
				parts[case][keys['number']][keys['gender']] = user_input
			else:
				parts[case][keys['number']] = user_input


def retreive_noun_forms(template):
	html_doc = tables.get_html(template['search word'])
	if html_doc == None:
		return
	soup = BeautifulSoup(html_doc, 'html.parser')
	page_list = soup.prettify().split('\n')
	page_list = clean_page_list(page_list)

	multi = True if template['gender'] in ["(m,f,n)","(m/f,n)","(m/f/n)"] else False
	one_ending = True if template['gender'] == "(m/f/n)" else False
	two_ending = True if template['gender'] == "(m/f,n)" else False
	three_endiing = True if template['gender'] == "(m,f,n)" else False


	cases = {"Nominative":'','Genitive':'','Dative':'','Accusative':'','Ablative':'','Vocative':''}
	genders = {'Masculine':'---','Feminine':'---','Neuter':'---'}
	numbers = {'Singular':'---',"Plural":'---'}
	if multi:
		for n in numbers:
			numbers[n] = deepcopy(genders)
	for case in cases:
		cases[case] = deepcopy(numbers)

	case = False
	start = 0
	last = False
	holder = []
	indent = 0
	count = 0
	specified = template['defno'] - 1
	stop = False
	for i in range(len(page_list)):
		if count_indent(page_list[i]) < indent - 2:
			stop = True
		if page_list[i].strip().title() == "Case" or page_list[i].strip().title() == "Number":
			start = 1
		if page_list[i].strip().title() == "Singular" and start == 1:
			start = 2
		if (page_list[i].strip().title() == "Plural" or page_list[i].strip().title() == "Case / Gender") and start == 2:
			start = 3
			if count < specified:
				count += 1
				start = 0
		if page_list[i].strip().title() in cases and start == 3 or stop:
			if not indent:
				indent = count_indent(page_list[i])
			if case or stop:
				if multi:
					if len(holder) > 6:
						cases = manual_sort(cases,case,holder)
					elif len(holder) == 6:
						if three_endiing:
							cases[case]['Singular']['Masculine'] = holder[0]
							cases[case]['Singular']["Feminine"] = holder[1]
							cases[case]['Singular']['Neuter'] = holder[2]
							cases[case]['Plural']['Masculine'] = holder[3]
							cases[case]['Plural']["Feminine"] = holder[4]
							cases[case]['Plural']['Neuter'] = holder[5]
						else:
							cases = manual_sort(cases,case,holder)
					elif len(holder) == 5:
						cases = manual_sort(cases,case,holder)
					elif len(holder) == 4:
						if two_ending:
							cases[case]['Singular']['Masculine'] = holder[0]
							cases[case]['Singular']['Neuter'] = holder[1]
							cases[case]['Plural']['Masculine'] = holder[2]
							cases[case]['Plural']['Neuter'] = holder[3]
						else:
							cases = manual_sort(cases,case,holder)
					elif len(holder) == 3:
						cases = manual_sort(cases,case,holder)
					elif len(holder) == 2:
						cases[case]['Singular']['Masculine'] = holder[0]
						cases[case]['Plural']['Masculine'] = holder[1]
				else:
					if len(holder) > 2:
						cases = manual_sort(cases,case,holder,False)
					else:
						cases[case]['Singular'] = holder[0]
						cases[case]['Plural'] = holder[1]
				if stop:
					indent = 0
					stop = False
					break
			holder = []
			case = page_list[i].strip()
		elif case:
			holder.append(page_list[i].strip())

	return cases

def add_sum_forms(page_list,i,alt=''):
	change_path(SUPPLEMENTARY_LANGUAGE_FILES)
	with open('sum_parts.txt','r') as f:
		sum_forms = json.load(f)
	if 'Imperfect' in page_list[i - 1].title():
		tense = 'Imperfect'
	elif 'Future' in page_list[i - 1].title():
		tense = 'Future'
	elif 'Present' in page_list[i - 1].title():
		tense = 'Present'
	if 'Indicative' in page_list[i - 1].title():
		mood = 'indicative'
	elif 'Subjunctive' in page_list[i - 1].title():
		mood = 'subjunctive'
	voice = 'active'
	keys = ['tpp','spp','fpp','tps','sps','fps']
	for key in keys:
		if alt:
			page_list.insert(i + 1,alt + "/" + page_list[i - 2].strip() + " " + sum_forms[tense][voice][mood][key])
		else:
			page_list.insert(i + 1,page_list[i - 2] + " " + sum_forms[tense][voice][mood][key])
	return page_list


def add_tables():

	tables_list = tables.get_tables('Latin')
	table_info = {'title':'','type':''}
	table_file = "Latin-tables.txt"
	
	while True:	
		print("Use table template? ('1' for yes, '0' to go back, any other key for no) 'AUTO' to auto-add all forms")
		user_input =  input(": ")
		if user_input == '1':
			template = tables.get_template('Latin')
			if template == None:
				continue
			table_info['title'] = template['title']
		elif user_input.upper() == 'AUTO':
			auto_add(tables_list,table_info,table_file)
			return
		elif user_input == '0':
			return
		else:
			template = None
			print(f"Enter table title ('0' to go back)")
			table_info['title'] = input(': ')
			if table_info['title'] == '0':
				continue

		exit_second_loop = False
		while not exit_second_loop:
			complete = False
			print("Select table type")
			options = {'1':"'1'> noun\n",'2':"'2'> verb principal parts\n",'3':"'3'> verb conjugation\n",'4':"'4'> complete verb system\n",'5':"'5'> complete forms\n"}

			options.update({'4':"'4'> complete verb system\n"})
			options.update({'0':"'0'> to go back"})
			user_input = get_selection(options)
			if user_input == '0':
				exit_second_loop = True
				continue
			elif user_input == '1':
				table_info['type'] = 'noun'
			elif user_input == '2':
				table_info['type'] = 'parts'
			elif user_input == '3':
				table_info['type'] = 'conj'
			elif user_input == '4':
				table_info['type'] = 'conj'
				complete = True
			elif user_input == '5':
				table_info['type'] = 'form'
				complete = True

			exit_third_loop = False
			while not exit_third_loop:
				if template:
					table_info['definition'] = template['definition']
				else:
					definition = input("Enter definition ('0' to go back): ")
					if definition == '0':
						exit_third_loop = True
						continue
					table_info['definition'] = definition
					while True:
						print("Enter definition number (1-n) ('0' to go back)")
						try:
							user_input = int(input(": "))
						except:
							print("Invalid entry")
							continue
						if user_input == 0:
							break
						else:
							table_info['specified'] = user_input

				if complete:
					if table_info['type'] == 'conj':
						add_complete_verb_system(template,table_info,tables_list,table_file)
					elif table_info['type'] == 'form':
						add_complete_forms(template)
					exit_second_loop = exit_third_loop = True
					prtin("tables added succesfully")
					continue

				exit_loop_four = False
				while not exit_loop_four:
					print(f"Do you want to auto-retreive {table_info['title']}? ('1' for yes, '0' to go back, '00' to exit)")
					user_input = input(": ")
					if user_input == '1':
						if table_info['type'] in ['parts','conj']:
							result = auto_retreive_verb(table_info,template)
						else:
							result = auto_retreive_noun(table_info,template)
						if result:
							tables_list = tables.add_table(tables_list,table_info)
							tables.save_tables(tables_list,table_file)
						exit_loop_four = exit_third_loop = exit_second_loop = True
						continue
					elif user_input == '0':
						exit_loop_four = exit_third_loop = exit_second_loop = True
						continue
					elif user_input == '00':
						return

def auto_add(tables_list,table_info,table_file):
	change_path(FLASHCARD_TEMPLATE_FILES)
	myFiles = glob.glob('*.txt')
	template_file = "Latin_templates.txt"
	if template_file not in myFiles:
		return
	else:
		with open(template_file,'r') as f:
			templates = json.load(f)
	for template in templates:
		print(template['title'])
		i = template
		add_complete_forms(template)
		table_info['definition'] = template['definition']
		if template["POS"] == 'verb':
			table_info['type']= 'conj'
			add_complete_verb_system(template,table_info,tables_list,table_file)
		if template["POS"] == 'noun/adj.':
			table_info['type']= 'noun'
			if template['gender'] == "(m,f,n)" or template['gender'] == "(m/f,n)" or template['gender'] == '(m/f/n)':
				continue
			table_info = auto_retreive_noun(table_info,template)
			tables_list = tables.add_table(tables_list,table_info)
			tables.save_tables(tables_list,table_file)

def empty(item):
	if type(item) != dict:
		return True if item == '---' or item == '—' else False
	for key in item:
		if not empty(item[key]):
			return False
	return True

def add_complete_forms(template):
	return
	forms_list = tables.get_forms("Latin")
	for i in range(len(template['forms'])):
		found = False
		for x in range(len(forms_list)):
			if forms_list[x]['title'] == unidecode(template['forms'][i]['form']):
				found = True
				instance = {'form':template['forms'][i]['form']}
				instance['root'] = template['title']
				instance['features'] = {x:y for x,y in template['forms'][i].items() if x != 'form'}
				for y in forms_list[x]['instances']:
					same = True
					for key in y['features'].keys():
						if key not in instance['features']:
							same = False
							break
						else:
							if y['features'][key] != instance['features'][key]:
								#print(f"NOT SAME {y['features']} AND {instance['features']}")
								same = False
								break
					if same:
						break
				if same:
					print(f"rejected DUPLICATE")						
					break
				'''
				if 'tense' in instance['features']:
					if instance['features']['tense'] not in ["Present",'Imperfect','Future']:
						#print(f"rejected {instance['features']['tense']}")						
						break
				if 'mood' in instance['features']:
					if instance['features']['mood'] in ["Subjunctive",'Imperative']:
						#print(f"rejected {instance['features']['mood']}")						
						break
				'''
				instance['principal'] = template['principal']
				instance['definition'] = template['definition']
				print("ADDING TO EXISTING")
				print(instance)
				forms_list[x]['instances'].append(deepcopy(instance))
		if not found:
			form = {'title':unidecode(template['forms'][i]['form'])}
			instance = {'form':template['forms'][i]['form']}
			instance['root'] = template['title']
			instance['features'] = {x:y for x,y in template['forms'][i].items() if x != 'form'}
			'''
			if 'tense' in instance['features']:
				if instance['features']['tense'] not in ["Present",'Imperfect','Future']:
					#print(f"rejected {instance['features']['tense']}")					
					continue
			if 'mood' in instance['features']:
				if instance['features']['mood'] in ["Subjunctive",'Imperative']:
					#print(f"rejected {instance['features']['mood']}")					
					continue
			'''
			instance['principal'] = template['principal']
			instance['definition'] = template['definition']
			form['instances'] = [deepcopy(instance)]
			print("ADDING NEW")
			print(instance)
			forms_list.append(deepcopy(form))
	tables.save_tables(forms_list,'Latin_forms.txt')

def add_complete_verb_system(template,table_info,tables_list,table_file):
	table_info['principal'] = template['principal']
	tenses = template['parts']
	for tense in ["Present",'Imperfect','Future','Future Perfect','Perfect',"Pluperfect"]:
		for voice in ["Active",'Passive']:
			table_info = assign_table_info(table_info,template,tenses,tense,voice)
			if empty(table_info['parts']):
				#print(f"\t\t\t\t\t\t\t\t{table_info['title']} was blank")
				continue
			else:
				tables_list = tables.add_table(tables_list,table_info)
				tables.save_tables(tables_list,table_file)
				#print(f"\t\t\t\t\t\t\t\t{table_info['title']} saved")
	table_info['type'] = 'parts'
	table_info = assign_principle_parts(table_info,tenses,template)
	tables_list = tables.add_table(tables_list,table_info)
	tables.save_tables(tables_list,table_file)

def auto_retreive_verb(table_info,template):
	tenses = template['parts']
	if table_info['type'] == 'parts':
		table_info = assign_principle_parts(table_info,tenses,template)
		return table_info
	elif table_info['type'] == 'conj':
		options1 = {'1':"Present",'2':'Imperfect','3':'Future','4':'Perfect','5':'Pluperfect','6':'Future Perfect'}
		user_input = get_selection(options1,2)
		tense = options1[user_input]
		options2 = {'1':"Active",'2':'Passive'}
		user_input = get_selection(options2,2)
		voice = options2[user_input]
		options3 = {'1':'Indicative','2':'Subjunctive','3':'Imperative'}
		user_input =  get_selection(options3,2)
		mood = options3[user_input]
		table_info = assign_table_info(table_info,template,tenses,tense,voice,mood)
		return table_info



def assign_table_info(table_info,template,tenses,tense,voice):
	x = 'Indicative'
	table_info['parts'] = {'1st Person':{'Singular':tenses[tense][voice][x]['FPS'],'Plural':tenses[tense][voice][x]['FPP']},\
						'2nd Person':{'Singular':tenses[tense][voice][x]['SPS'],'Plural':tenses[tense][voice][x]['SPP']},\
						'3rd Person':{'Singular':tenses[tense][voice][x]['TPS'],'Plural':tenses[tense][voice][x]['TPP']}}
	table_info['parts'].update({'Infinitive':tenses[tense][voice]['Infinitive']})
	table_info['parts'].update({'Participle':tenses[tense][voice]['Participle']})
	x = 'Imperative'
	table_info['parts'].update({'Imperative':{'1st Person':{'Singular':tenses[tense][voice][x]['FPS'],'Plural':tenses[tense][voice][x]['FPP']},\
						'2nd Person':{'Singular':tenses[tense][voice][x]['SPS'],'Plural':tenses[tense][voice][x]['SPP']},\
						'3rd Person':{'Singular':tenses[tense][voice][x]['TPS'],'Plural':tenses[tense][voice][x]['TPP']}}})
	x = 'Subjunctive'
	table_info['parts'].update({'Subjunctive':{'1st Person':{'Singular':tenses[tense][voice][x]['FPS'],'Plural':tenses[tense][voice][x]['FPP']},\
						'2nd Person':{'Singular':tenses[tense][voice][x]['SPS'],'Plural':tenses[tense][voice][x]['SPP']},\
						'3rd Person':{'Singular':tenses[tense][voice][x]['TPS'],'Plural':tenses[tense][voice][x]['TPP']}}})
	if template:
		table_info['title'] = f"{tense.title()} {voice.title()}: {template['title']}"
	return table_info

def auto_retreive_noun(table_info,template):
	table_info['principal'] = template['principal']
	parts = template['parts']
	case_keys = ["Nominative",'Genitive','Dative','Accusative','Ablative','Vocative']
	number_keys = ['Singular',"Plural"]
	table_info['parts'] = {}
	for case in case_keys:
		table_info['parts'][case] = {}
		for number in number_keys:
			if 'Masculine' not in parts[case][number]:
				table_info['parts'][case][number] = parts[case][number]
			elif 'Masculine' in parts[case][number]:
				table_info['parts'][case][number] = ", ".join([parts[case][number]['Masculine'], parts[case][number]['Feminine'], parts[case][number]['Neuter']])
	if template:
		table_info['title'] = f"{template['title']}"
	return table_info





def clean_page_list(page_list,exception=False):
	offset = 0
	for i in range(1,len(page_list)):
		i = i - offset
		if ' ' in page_list[i]:
			page_list[i] = page_list[i].replace(' ',' ')
		if page_list[i].strip()[0] == "<":
			del page_list[i]
			offset += 1

	offset = 0
	sum_infinitive = ['īrī','esse']
	for i in range(1,len(page_list)):
		i = i - offset
		if page_list[i].strip(' ') == ',':
			page_list[i - 1] = page_list[i - 1].strip(' ') + ", " + page_list[i + 1].strip(' ')
			del page_list[i + 1]
			del page_list[i]
			offset += 2
		elif page_list[i].strip(' ') == 'sum' and page_list[i - 1].strip(' ')[0] == '+' and page_list[i - 1].strip(' ')[-2:] == 'of':
			if page_list[i - 3].strip() == 'or':
				page_list = add_sum_forms(page_list,i,page_list[i - 4].strip())
				for x in range(5):
					del page_list[i - 4]
				offset += 5
			else:
				page_list = add_sum_forms(page_list,i)
				for x in range(3):
					del page_list[i - 2]
				offset += 3
		elif page_list[i].strip(' ') == '/':
			page_list[i - 1] = page_list[i - 1].strip(' ') + "/" + page_list[i + 1].strip(' ')
			del page_list[i + 1]
			del page_list[i]
			offset += 2
		elif page_list[i].strip(' ') in sum_infinitive and previous not in sum_infinitive and not exception:
			page_list[i - 1] = page_list[i - 1].strip(' ') + ' ' + page_list[i].strip(' ')
			previous = page_list[i].strip(' ') 
			del page_list[i]
			offset += 1
		elif page_list[i].strip()[0] == "<" or (len(page_list[i].strip()) == 1 and page_list[i].strip().isnumeric()):
			del page_list[i]
			offset += 1
		else:
			previous = ''
	return page_list

def filter_cards(tables_list,random_list):
	filters = {
	'Pluperfect Passive':97,
	'Future Perfect Passive':97,
	'Pluperfect':75,
	'Future Perfect':75,
	'Perfect Passive':75,
	'Imperfect Passive':90,
	'Imperfect Active':65,
	'Present Passive':50,
	'Future Passive':65,
	'Future Active':25,
	}
	for i in range(len(tables_list)):
		r = random.randrange(0,100,1)
		for x in filters:
			if x in tables_list[i]['title']:
				if r < filters[x]:
					random_list.remove(i)
					break
	return random_list

def features_join(features):
	join = ""
	if 'gender' in features:
		join += " <b>" + features['gender'] + "</b>" 
	for x,y in features.items():
		if x == "mood" and (y != "Infinitive" and y != 'Participle'):
			join += " <em>" + y + "</em>"
		elif x == 'gender':
			pass
		else:
			join += " <b>" + y + "</b>"
	return join.strip()

def print_forms():
	out_file = 'Latin-FormCards.txt'
	original_stdout = sys.stdout 
	change_path(FORMATTED_FLASHCARD_FILES)
	sys.stdout = open(out_file,'w')
	forms_list = tables.get_forms("Latin")
	random_list = list(range(len(forms_list)))
	random.shuffle(random_list)
	for i in random_list:
		print('<P align="left"!--FORM-->· ' + unidecode(forms_list[i]['title']) + '</P>|',end='')
		for instance in forms_list[i]['instances']:
			features = features_join(instance['features'])
			if features:
				print('<P align="left" style="line-height:1.5">' + instance['form'] + '<br>',end='')
			else:
				print('<P align="left" style="line-height:1.5">',end='')
			print(features,end='')
			print(' form of: <b>' + instance['principal'] + '</b><br>',end='')
			print("Definition: " + instance['definition'] + '</P><br>',end='')
		print('|"forms"')
	sys.stdout = original_stdout

def print_tables(tables_list):
	print_forms()
	out_file = 'Latin-TableCards.txt'
	original_stdout = sys.stdout 
	change_path(FORMATTED_FLASHCARD_FILES)
	sys.stdout = open(out_file,'w')

	for i in range(len(tables_list)):
		

		if tables_list[i]['type'] != 'noun':
			print('<P align="left">' + tables_list[i]['title'] + '</P>|',end='')
		else:
			print('<P align="left">Forms: ' + tables_list[i]['title'] + '</P>|',end='')
		
		if tables_list[i]['definition']:
			body_string = '<P align="left">' + tables_list[i]['definition'] + '</P>'
		else:
			body_string = ''

		body_string = html_x.set_styles(body_string)

		if tables_list[i]['type'] == 'parts':
			body_string = html_x.create_table(body_string,tables_list[i]['parts'],'parts',1)
		elif tables_list[i]['type'] == 'noun':
			body_string = html_x.create_table(body_string,tables_list[i]['parts'],'noun',2)
		elif tables_list[i]['type'] == 'conj':
			parts = {k:v for k,v in tables_list[i]['parts'].items() if k != "Infinitive" and k != "Participle" and k != "Imperative" and k != "Subjunctive"}
			body_string = html_x.create_table(body_string,parts,'conj',2)
			body_string = html_x.create_box(body_string,'Infinitive',tables_list[i]["parts"]["Infinitive"])
			body_string = html_x.create_box(body_string,'Participle',tables_list[i]["parts"]["Participle"])
			if 'Subjunctive' in tables_list[i]['parts']:
				body_string += '<P align="left">Subjunctive:</P>'
				body_string = html_x.create_table(body_string,tables_list[i]['parts']['Subjunctive'],'conj',2)	
			if 'Imperative' in tables_list[i]['parts']:
				body_string += '<P align="left">Imperative:</P>'
				body_string = html_x.create_table(body_string,tables_list[i]['parts']['Imperative'],'conj',2)		


		print(body_string + '|"table"')

	sys.stdout = original_stdout