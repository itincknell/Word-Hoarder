
from bs4 import BeautifulSoup
import tables
import flashcard_html_utilities
from load_dict import change_path
from get_selection import get_selection
from copy import deepcopy
import random
import sys

def add_tables():

	tables_list = tables.get_tables('Old English')
	table_info = {'title':'','type':''}
	table_file = "OldEnglishtables.txt"
	
	while True:	
		print("Use table template? ('1' for yes, '0' to go back, any other key for no)")
		user_input =  input(": ")
		if user_input == '1':
			template = tables.get_template('Old English')
			if template == None:
				continue
			table_info['title'] = template['title']
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
			options = {'1':"'1'> noun\n",'2':"'2'> verb conjugation\n"}
			options.update({'0':"'0'> to go back"})
			user_input = get_selection(options)
			if user_input == '0':
				exit_second_loop = True
				continue
			elif user_input == '1':
				table_info['type'] = 'noun'
			elif user_input == '2':
				table_info['type'] = 'conj'

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
							tables_list = tables.save_table(tables_list,table_info,'Old English')
							tables.pop_template(template,'Old English')
						exit_loop_four = exit_third_loop = exit_second_loop = True
						continue
					elif user_input == '0':
						exit_loop_four = exit_third_loop = exit_second_loop = True
						continue
					elif user_input == '00':
						return

def empty(item):
	if type(item) != dict:
		return True if item == '---' or item == '—' else False
	for key in item:
		if not empty(item[key]):
			return False
	return True

def auto_retreive_verb(table_info,template):
	moods = retreive_verb_forms(template)
	if moods == None:
		return None
	table_info['parts'] = moods
	return True

def auto_retreive_noun(table_info,template):
	cases = retreive_noun_forms(template)
	if cases == None:
		return None
	case_keys = ["Nominative",'Genitive','Dative','Accusative']
	number_keys = ['Singular',"Plural"]
	parts = {}
	for case in case_keys:
		parts[case] = {}
		for number in number_keys:
			parts[case][number] = cases[case.lower()][number]
	table_info['parts'] = parts
	if template:
		table_info['title'] = f"{template['title']}"
	return True

def retreive_verb_forms(template):
	if 'specified' in template:
		specified = template['specified']
	else:
		specified = 0
	html_doc = tables.get_html(template)
	if html_doc == None:
		return
	soup = BeautifulSoup(html_doc, 'html.parser')
	page_list = soup.prettify().split('\n')
	page_list = clean_page_list(page_list)

	tenses = {"present tense":'','past tense':''}
	tenses_2 = {"present":'','past':''}
	moods = {"infinitive":[],'indicative':[],'subjunctive':[],'imperative':[],"participle":[]}
	mood_list = ["infinitive",'indicative mood','subjunctive','imperative',"participle"]
	persons_1 = {'1p sing.':'---','2p sing.':'---','3p sing.':'---','plural':'---'}
	person_list = {'first person singular':'1p sing.','second person singular':'2p sing.','third person singular':'3p sing.','plural':'plural'}
	persons_2 = {'singular':'---','plural':'---'}

	moods['infinitive'] = []
	moods['indicative'] = deepcopy(persons_1)
	for key in persons_1:
		moods['indicative'][key] = deepcopy(tenses)
	moods['subjunctive'] = deepcopy(persons_2)
	for key in persons_2:
		moods['subjunctive'][key] = deepcopy(tenses)
	moods['imperative'] = deepcopy(persons_2)
	moods['participle'] = deepcopy(tenses_2)

	mood = False
	for i in range(len(page_list)):
		if page_list[i].strip(" ") in mood_list:
			mood = page_list[i].strip(" ")
			if mood == 'indicative mood':
				mood = 'indicative'
			person = tense = False
			index = 0
		elif mood == 'infinitive':
			moods[mood].append(page_list[i].strip(" "))
		elif mood == 'indicative':
			if page_list[i].strip(" ") in person_list:
				person = person_list[page_list[i].strip(" ")]
				t_list = list(tenses.keys())
				index = 0
			elif index < 2 and person:
				moods[mood][person][t_list[index]] = page_list[i].strip(" ")
				index += 1
			elif index > 1:
				mood = person = False
		elif mood == 'subjunctive':
			if page_list[i].strip(" ") in persons_2:
				person = page_list[i].strip(" ")
				t_list = list(tenses.keys())
				index = 0
			elif index < 2 and person:
				moods[mood][person][t_list[index]] = page_list[i].strip(" ")
				index += 1
			elif index > 1:
				mood = person = False
		elif mood == 'imperative':
			if page_list[i].strip(" ") in persons_2:
				person = page_list[i].strip(" ")
				index = 0
			elif index < 2 and person:
				moods[mood][person] = page_list[i].strip(" ")
				index += 1
			elif index > 1:
				mood = person = False
		elif mood == 'participle':
			t_list = list(tenses_2.keys())
			if page_list[i].strip(" ") in tenses_2:
				pass
			elif index < 2:
				moods[mood][t_list[index]] = page_list[i].strip(" ")
				index += 1
			elif index > 1:
				mood = tense = False
	return moods

def retreive_noun_forms(template):
	html_doc = tables.get_html(template)
	if html_doc == None:
		return
	soup = BeautifulSoup(html_doc, 'html.parser')
	page_list = soup.prettify().split('\n')
	page_list = clean_page_list(page_list)

	cases = {"nominative":'','genitive':'','dative':'','accusative':''}
	numbers = {'Singular':'---',"Plural":'---'}
	for case in cases:
		cases[case] = deepcopy(numbers)

	start = 0
	case = False
	for i in range(len(page_list)):
		if page_list[i].strip() == "Case":
			start = 1
		if page_list[i].strip() == "Singular" and start == 1:
			start = 2
		if page_list[i].strip() == "Plural" and start == 2:
			start = 3
		if page_list[i].strip() in cases and start == 3:
			case = page_list[i].strip()
			index = 0
		elif case:
			if index == 0:
				number = 'Singular'
			elif index == 1:
				number = 'Plural'
			elif index > 1:
				index = 0
				case = False
				continue
			if cases[case][number] == "---": 
				cases[case][number] = page_list[i].strip()
			index += 1	
	return cases

def clean_page_list(page_list):
	offset = 0
	for i in range(1,len(page_list)):
		i = i - offset
		if ' ' in page_list[i]:
			page_list[i] = page_list[i].replace(' ',' ')
		if page_list[i].strip()[0] == "<":
			del page_list[i]
			offset += 1

	offset = 0
	for i in range(1,len(page_list)):
		i = i - offset
		if page_list[i].strip(' ') == ',':
			page_list[i - 1] = page_list[i - 1].strip(' ') + ", " + page_list[i + 1].strip(' ')
			del page_list[i + 1]
			del page_list[i]
			offset += 2
		elif page_list[i].strip(' ') == '/':
			page_list[i - 1] = page_list[i - 1].strip(' ') + "/" + page_list[i + 1].strip(' ')
			del page_list[i + 1]
			del page_list[i]
			offset += 2
		elif page_list[i - 1].strip(' ') == ')' and len(page_list[i - 2].strip(' ')) < 4 and page_list[i - 3].strip(' ') == '(':
			page_list[i] = "(" + page_list[i - 2].strip(' ') + ")" + page_list[i].strip(' ')
			for x in range(3):
				del page_list[i - 3]
			offset += 3
		elif page_list[i].strip()[0] == "<" or (len(page_list[i].strip()) == 1 and page_list[i].strip().isnumeric()):
			del page_list[i]
			offset += 1
		else:
			previous = ''
	return page_list

def print_tables(tables_list):
	out_file = 'OldEnglishflashcardtables.txt'
	original_stdout = sys.stdout 
	change_path('flashcards')
	sys.stdout = open(out_file,'w')
	random_list = list(range(len(tables_list)))
	random.shuffle(random_list)
	for i in random_list:

		print('<P align="left">Forms: ' + tables_list[i]['title'] + '</P>|',end='')
		
		if tables_list[i]['definition']:
			body_string = '<P align="left">' + tables_list[i]['definition'] + '</P>'
		else:
			body_string = ''

		body_string = html_x.set_styles(body_string)

		if tables_list[i]['type'] == 'noun':
			body_string = html_x.create_table(body_string,tables_list[i]['parts'],'noun',2)
		elif tables_list[i]['type'] == 'conj':
			body_string += '<P align="left">infinitive:</P>'
			body_string = html_x.create_box(body_string,tables_list[i]["parts"]["infinitive"][0],tables_list[i]["parts"]["infinitive"][1])
			body_string += '<P align="left">indicative:</P>'
			indicative = tables_list[i]['parts']['indicative']
			body_string = html_x.create_table(body_string,indicative,'',2)
			body_string += '<P align="left">subjunctive:</P>'
			subjunctive = tables_list[i]['parts']['subjunctive']
			body_string = html_x.create_table(body_string,subjunctive,'',2)
			body_string += '<P align="left">imperative:</P>'
			imperative = tables_list[i]['parts']['imperative']
			body_string = html_x.create_style(body_string,1)
			body_string = html_x.create_body(body_string,imperative,'')
			body_string += '<P align="left">participle:</P>'
			participle = tables_list[i]['parts']['participle']
			body_string = html_x.create_style(body_string,1)
			body_string = html_x.create_body(body_string,participle,'')

		print(body_string + '|"table"')

	sys.stdout = original_stdout