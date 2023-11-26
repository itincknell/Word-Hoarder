
from bs4 import BeautifulSoup
import tables
import flashcard_html_utilities
from load_dict import change_path, FORMATTED_FLASHCARD_FILES, FLASHCARD_TEMPLATE_FILES
from get_selection import get_selection
from copy import deepcopy, copy
import random
import sys
import glob, json

'''
{'title': capio
'search word':
'definition #':
'POS': verb
'definition': 'to take'
'principle' : capio, capere, capi ,captum
'parts':[mood][tense]etc..."capere"
'forms':[{'form':'capere','article':'','tense':'present',etc...}}
] }

'''

DEBUG = True
import inspect

def debug_print(message):
	line_number = inspect.currentframe().f_back.f_lineno
	if DEBUG:
		print(f"[Line {line_number}] - {message}")

def new_template(heading="",handle="",definition="",POS=""):
	template = {}
	while True:
		x = 'POS'
		options = {'0':f"\nEnter choose template {x} ('0' to go back)\n==================================\n",
					'1':"'1'> noun\n",'2':"'2'> verb\n",
					'00':"'00' to quit\n"}
		user_input = get_selection(options)
		if user_input == '0':
			break
		elif user_input == '00':
			return
		else:
			template[x] = 'noun' if user_input == '1' else 'verb'
		if template[x] == 'noun':
			x = 'gender'
			options = {'0':f"\nEnter choose template {x} ('0' to go back)\n==================================\n",
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
			while True:
				x = 'search word'
				if handle == "":
					print(f"Enter template {x} ('0' to go back '00' to quit)")
					user_input = input(": ")
					if user_input == '0':
						break
					elif user_input == '00':
						return
					else:
						template[x] = tables.replace_greek_ii(user_input)
				else:
					template[x] = handle
				while True:
					print("Enter definition number ('0' if unspecified)")
					try:
						template['defno'] = int(input(": "))
					except:
						print("Invalid entry")
						continue

					template = get_forms(template)
					x = 'definition'
					print(f"Enter template {x} ('0' to go back '00' to quit)")
					user_input = input(": ")
					if user_input == '0':
						continue
					elif user_input == '00':
						return
					else:
						template[x] = user_input
					print(template)
					return template	

def edit_template(template):
	while True:
		options = {'1':f"\nTemplate \"{template['title']}\" options:\n==================================\n'1' change definition\n",
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
		if chunk != '---':
			final_str = f"{string.lstrip():_<70}" + chunk
			print(final_str)

def get_forms(template):
	if template['POS'] == 'noun':
		if template['gender'] == '(multi)':
			while True:
				print(f"{template['title']} (m,f,n)>1 or (m/f,n)>2?")
				user_input = input(": ")
				if user_input == '1':
					template['gender'] = '(m,f,n)'
					break
				elif user_input == '2':
					template['gender'] = '(m/f,n)'
					break
				else:
					print("Invalid selection")
		template['parts'] = retreive_noun_forms(template)
		if template['gender'] == '(m,f,n)':
			parts = template['parts']['Nominative']['Singular']
			template['principal'] = ", ".join([x for x in parts.values()])
			template['forms'] = inside_out_multi_noun(template['parts'])
		elif template['gender'] == '(m/f,n)':
			print(template['parts']['Nominative']['Singular'])
			template['parts'] = fix_two_ending(template['parts'])
			parts = template['parts']['Nominative']['Singular']
			template['principal'] = ", ".join([y for x,y in parts.items() if x != 'Feminine'])
			template['forms'] = inside_out_multi_noun(template['parts'])
		else:
			parts = template['parts']['Nominative']['Singular']
			nom = parts['article'] + " " + parts['form']
			parts = template['parts']['Genitive']['Singular']
			gen = parts['article'] + " " + parts['form']
			template['principal'] = nom + ", " + gen
			template['forms'] = inside_out_noun(template['parts'])
	elif template['POS'] == 'verb':
		template['parts'] = retreive_verb_forms(template)
		result = assign_principle_parts({},template['parts'])
		result = [y['Principal Part'] for y in result['parts'].values()]
		template['principal'] = ", ".join(result)
		template['forms'] = inside_out_verb(template['parts'])
	return template

def redo(templates):
	for template in templates:
		template = get_forms(template)
	return templates

def fix_two_ending(parts):
	for case in parts:
		for number in parts[case]:
			print(f"{case} {number} Masculine = {parts[case][number]['Masculine']}")
			parts[case][number]["Feminine"] = parts[case][number]["Masculine"]
			print(f"{case} {number} Feminine now = {parts[case][number]['Feminine']}")
	print(parts)
	return parts


def nu_movable(x):
	wo_nu = x[:x.find("(")]
	letter = x[x.find("(")+1:-1]
	if len(letter) > 1:
		return [wo_nu]
	with_nu = wo_nu + letter
	return [wo_nu,with_nu]

def perfectMiddleSubjuctive(part):
	parts = part.split()
	if len(parts) == 2:
		parts[1] = parts[1].split("/")
		if len(parts[1]) == 2:
			new_parts = [parts[0] + " " + parts[1][0], parts[0] + " " + parts[1][1]]
			return new_parts
	return parts

def inside_out_multi_noun(parts):
	forms = []
	print(parts)
	for case in parts:
		for number in parts[case]:
			for gender in parts[case][number]:
				if parts[case][number][gender] != "—":
					if "," in parts[case][number][gender]:
						for x in parts[case][number][gender].split(","):
							if x.strip()[-1] == ')':
								for y in nu_movable(x):
									form = {'form':y.strip()}
									form['case'] = case
									form['number'] = number
									form['gender'] = gender
									forms.append(deepcopy(form))
							else:
								form = {'form':x.strip()}
								form['case'] = case
								form['number'] = number
								form['gender'] = gender
								forms.append(deepcopy(form))
					elif "/" in parts[case][number][gender]:
						for x in parts[case][number][gender].split("/"):
							if x.strip()[-1] == ')':
								for y in nu_movable(x):
									form = {'form':y.strip()}
									form['case'] = case
									form['number'] = number
									form['gender'] = gender
									forms.append(deepcopy(form))
							else:
								form = {'form':x.strip()}
								form['case'] = case
								form['number'] = number
								form['gender'] = gender
								forms.append(deepcopy(form))
					else:
						print(f"{case} {number} {gender} = {parts[case][number][gender]}")
						if parts[case][number][gender][-1] == ")":
							for x in nu_movable(parts[case][number][gender]):
								form = {'form':x.strip()}
								form['case'] = case
								form['number'] = number
								form['gender'] = gender
								forms.append(deepcopy(form))
						else:
							form = {'form':parts[case][number][gender]}
							form['case'] = case
							form['number'] = number
							form['gender'] = gender
							forms.append(deepcopy(form))
	return forms

def inside_out_noun(parts):
	forms = []
	for case in parts:
		for number in parts[case]:
			if parts[case][number]['form'] != "—":
				if "," in parts[case][number]['form']:
					for x in parts[case][number]['form'].split(","):
						if x.strip()[-1] == ")":
							for y in nu_movable(x):
								form = {'form':y.strip()}
								form['case'] = case
								form['number'] = number
								form['article'] = parts[case][number]['article']
								forms.append(deepcopy(form))
						else:
							form = {'form':x.strip()}
							form['case'] = case
							form['number'] = number
							form['article'] = parts[case][number]['article']
							forms.append(deepcopy(form))
				elif "/" in parts[case][number]['form']:
					for x in parts[case][number]['form'].split("/"):
						if x.strip()[-1] == ")":
							for y in nu_movable(x):
								form = {'form':y.strip()}
								form['case'] = case
								form['number'] = number
								form['article'] = parts[case][number]['article']
								forms.append(deepcopy(form))
						else:
							form = {'form':x.strip()}
							form['case'] = case
							form['number'] = number
							form['article'] = parts[case][number]['article']
							forms.append(deepcopy(form))
				else:
					if parts[case][number]['form'][-1] == ")":
						for x in nu_movable(parts[case][number]['form']):
							form = {'form':x.strip()}
							form['case'] = case
							form['number'] = number
							form['article'] = parts[case][number]['article']
							forms.append(deepcopy(form))
					form = {'form':parts[case][number]['form']}
					form['case'] = case
					form['number'] = number
					form['article'] = parts[case][number]['article']
					forms.append(deepcopy(form))
	return forms

def inside_out_verb(parts):
	forms = []
	for tense in parts:
		for voice in parts[tense]:
			for mood in parts[tense][voice]:
				if mood == 'Infinitive':
					if parts[tense][voice][mood] != "---":
						if "," in parts[tense][voice][mood]:
							for x in parts[tense][voice][mood].split(","):
								if x.strip()[-1] == ")":
									for y in nu_movable(x):
										form = {'form':y.strip()}
										form['tense'] = tense
										form['voice'] = voice
										form['mood'] = mood
										forms.append(deepcopy(form))
								else:
									form = {'form':x.strip()}
									form['tense'] = tense
									form['voice'] = voice
									form['mood'] = mood
									forms.append(deepcopy(form))
						elif "/" in parts[tense][voice][mood]:
							for x in parts[tense][voice][mood].split("/"):
								if x.strip()[-1] == ")":
									for y in nu_movable(x):
										form = {'form':y.strip()}
										form['tense'] = tense
										form['voice'] = voice
										form['mood'] = mood
										forms.append(deepcopy(form))
								else:
									form = {'form':x.strip()}
									form['tense'] = tense
									form['voice'] = voice
									form['mood'] = mood
									forms.append(deepcopy(form))
						else:
							if parts[tense][voice][mood][-1] == ")":
								for x in nu_movable(parts[tense][voice][mood]):
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
					for gender in parts[tense][voice][mood]:
						if parts[tense][voice][mood][gender] != "---":
							if "," in parts[tense][voice][mood][gender]:
								for x in parts[tense][voice][mood][gender].split(","):
									if x.strip()[-1] == ")":
										for y in nu_movable(x):
											form = {'form':y.strip()}
											form['gender'] = gender
											form['tense'] = tense
											form['voice'] = voice
											form['mood'] = mood
											forms.append(deepcopy(form))
									else:
										form = {'form':x.strip()}
										form['gender'] = gender
										form['tense'] = tense
										form['voice'] = voice
										form['mood'] = mood
										forms.append(deepcopy(form))
							elif "/" in parts[tense][voice][mood][gender]:
								for x in parts[tense][voice][mood][gender].split("/"):
									if x.strip()[-1] == ")":
										for y in nu_movable(x):
											form = {'form':y.strip()}
											form['gender'] = gender
											form['tense'] = tense
											form['voice'] = voice
											form['mood'] = mood
											forms.append(deepcopy(form))
									else:
										form = {'form':x.strip()}
										form['gender'] = gender
										form['tense'] = tense
										form['voice'] = voice
										form['mood'] = mood
										forms.append(deepcopy(form))
							else:
								if parts[tense][voice][mood][gender][-1] == ")":
									for x in nu_movable(parts[tense][voice][mood][gender]):
										form = {'form':x.strip()}
										form['gender'] = gender
										form['tense'] = tense
										form['voice'] = voice
										form['mood'] = mood
										forms.append(deepcopy(form))
								else:
									form = {'form':parts[tense][voice][mood][gender]}
									form['gender'] = gender
									form['tense'] = tense
									form['voice'] = voice
									form['mood'] = mood
									forms.append(deepcopy(form))
				else:
					for person in parts[tense][voice][mood]:
						if parts[tense][voice][mood][person] != "---":
							if "," in parts[tense][voice][mood][person]:
								for x in parts[tense][voice][mood][person].split(","):
									if x.strip()[-1] == ")":
										for y in nu_movable(x):
											form = {'form':y.strip()}
											form['tense'] = tense
											form['voice'] = voice
											form['mood'] = mood
											form['person'] = person
											forms.append(deepcopy(form))
									else:
										form = {'form':x.strip()}
										form['tense'] = tense
										form['voice'] = voice
										form['mood'] = mood
										form['person'] = person
										forms.append(deepcopy(form))
							elif "/" in parts[tense][voice][mood][person]:
								perfmidsubj_flag = False
								for x in parts[tense][voice][mood][person].split("/"):
									if x in ['ὦ','ᾖς','ᾖ','ἦτον','εἴην','εἴης','εἴη','εἴητον','εἶτον','εἰήτην','εἴτην','ὦμεν','ἦτε','ὦσῐ','ὦσῐ(ν)','εἴημεν','εἶμεν','εἴητε','εἶτε','εἴησᾰν','εἶεν']:
										perfmidsubj_flag = True
								if perfmidsubj_flag:
									for x in perfectMiddleSubjuctive(parts[tense][voice][mood][person]):
										form = {'form':x.strip()}
										form['tense'] = tense
										form['voice'] = voice
										form['mood'] = mood
										form['person'] = person
										forms.append(deepcopy(form))
								else:
									for x in parts[tense][voice][mood][person].split("/"):
										if x.strip()[-1] == ")":
											for y in nu_movable(x):
												form = {'form':y.strip()}
												form['tense'] = tense
												form['voice'] = voice
												form['mood'] = mood
												form['person'] = person
												forms.append(deepcopy(form))
										else:
											form = {'form':x.strip()}
											form['tense'] = tense
											form['voice'] = voice
											form['mood'] = mood
											form['person'] = person
											forms.append(deepcopy(form))
							else:
								if parts[tense][voice][mood][person][-1] == ")":
									for x in nu_movable(parts[tense][voice][mood][person]):
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
	return forms




def auto_parts(parts,rapid_fire=False):
	if not rapid_fire:
		print("Enter look up word")
		user_input = input(": ")
	else:
		if " " in parts:
			user_input = parts[:parts.find(" ")+1]
		else:
			user_input = parts
		user_input = tables.replace_greek_ii(user_input)
		print(user_input)
	#try:
	result = retreive_verb_forms({'search word':user_input,'title':''})#'defno':0})
	result = assign_principle_parts(result,result)
	result = [y['Principal Part'] for y in result['parts'].values()]
	result = ", ".join(result)
	while True:
		print("Does this look right ('1' to except '0' to discard)?")
		print(result)
		user_input = input(": ")
		if user_input == '1':
			return result
		elif user_input == '0':
			return parts
		else:
			print("Invalid entry")
	#except:
	#	print("Something went wrong")
		return parts

def assign_principle_parts(table_info,tenses,template=None):
	table_info['parts'] = {}
	# 1

	part = copy(tenses['Present']['Active']['Indicative']['1st Person Singular'])
	if part == "---":
		part = copy(tenses['Present']['Middle/Passive']['Indicative']['1st Person Singular'])
	if part == "---":
		part = copy(tenses['Present']['Middle']['Indicative']['1st Person Singular'])

	table_info['parts'].update({'Present':{'Principal Part':part}})

	# 2
	part = copy(tenses['Future']['Active']['Indicative']['1st Person Singular'])
	if part == "---":
		part = copy(tenses['Future']['Middle']['Indicative']['1st Person Singular'])

	table_info['parts'].update({'Future':{'Principal Part':part}})

	part = copy(tenses['Perfect']['Middle/Passive']['Indicative']['1st Person Singular'])
	if part == '---':
		part = copy(tenses['Perfect']['Middle']['Indicative']['1st Person Singular'])

	table_info['parts'].update(
		# 3
		{'Aorist Act.':{'Principal Part':tenses['Aorist']['Active']['Indicative']['1st Person Singular']},\
		# 4
		'Perfect Act.':{'Principal Part':tenses['Perfect']['Active']['Indicative']['1st Person Singular']},\
		# 5
		'Perf. M./P.':{'Principal Part':part},\
		# 6
		'Aorist Pas.':{'Principal Part':tenses['Aorist']['Passive']['Indicative']['1st Person Singular']}})
	if template:
		table_info['title'] = f"Principal Parts: {template['title']}"
	return table_info

def count_indent(a):
	return len(a) - len(a.lstrip())

def retreive_verb_forms(template):
	if 'defno' in template:
		defno = template['defno']
	else:
		defno = 0
	html_doc = tables.get_html(template['search word'])
	if html_doc == None:
		return
	soup = BeautifulSoup(html_doc, 'html.parser')
	page_list = soup.prettify().split('\n')
	if template['title'] == 'εἰμῐ́':
		print("exception detected")
		exception = True
	else:
		exception = False
	page_list = clean_page_list(page_list,exception)

	tenses = {"Present":'','Imperfect':'','Future':'','Aorist':'','Perfect':'','Pluperfect':''}
	voices = {"Active":'',"Middle/Passive":'',"Middle":'','Passive':''}
	moods = {'Indicative':[],'Subjunctive':[],'Optative':[],'Imperative':[],"Infinitive":[],"Participle":[]}
	mood_list = ['Indicative','Subjunctive','Optative','Imperative']
	persons = {'1st Person Singular':'---','2nd Person Singular':'---','3rd Person Singular':'---','2nd Person Dual':'---','3rd Person Dual':'---','1st Person Plural':'---','2nd Person Plural':'---','3rd Person Plural':'---'}
	genders = {'Masculine':'---','Feminine':'---','Neuter':'---'}
	codec = {'m':'Masculine','f':'Feminine','n':'Neuter'}

	for tense in tenses:
		tenses[tense] = deepcopy(voices)
		for voice in tenses[tense]:
			tenses[tense][voice] = deepcopy(moods)
			for mood in tenses[tense][voice]:
				if mood in mood_list:
					tenses[tense][voice][mood] = deepcopy(persons)
				elif mood == 'Participle':
					tenses[tense][voice][mood] = deepcopy(genders)
				elif mood == 'Infinitive':
					tenses[tense][voice][mood] = '---'
	tense = False
	mood = False
	voice = False

	indent = 0
	uncontracted = {}
	unc_flag = False
	counter = 0


	def build(uncontracted,tense,voice,mood):
		if tense not in uncontracted:
			uncontracted[tense] = {}
		if voice not in uncontracted[tense]:
			uncontracted[tense][voice] = {}
		if mood not in uncontracted[tense][voice]:
			uncontracted[tense][voice][mood] = {}
		if mood in mood_list:
			tenses[tense][voice][mood] = deepcopy(persons)
		elif mood == 'Participle':
			tenses[tense][voice][mood] = deepcopy(genders)
		elif mood == 'Infinitive':
			tenses[tense][voice][mood] = '---'



	for i in range(len(page_list)):
		if counter < defno:
			if page_list[i].strip(": ").title() in tenses:
				if not indent:
					indent = count_indent(page_list[i])
			if count_indent(page_list[i]) < indent - 2:
				indent = 0
				counter += 1
		else:
			if count_indent(page_list[i]) < indent - 2:
				if counter < defno:
					indent = 0
					tense = False
					mood = False
					voice = False
					counter += 1
				else:
					break
			if page_list[i].strip(": ").title() in tenses:
				if not indent:
					indent = count_indent(page_list[i])
				tense = page_list[i].strip(": ").title()
				voice = mood = gender = indent = unc_flag = False
				voices = []
			elif page_list[i].strip() == '(Uncontracted)':
				unc_flag = True
			elif tense:
				if page_list[i].strip().title() in tenses[tense]:
					voice = page_list[i].strip().title()
					voices.append(page_list[i].strip().title())
					index = 0
				elif voice:
					if page_list[i].strip().title() in moods:
						mood = page_list[i].strip().title()
						index = 0
					elif mood:
						if page_list[i].strip() == "Notes:":
							voice = mood = gender = False
						else:
							if mood in mood_list:
								if index not in range(len(list(persons.keys()))):
									mood = False
								else:
									if mood == 'Imperative' and (index == 0 or index == 5):
										index += 1
									if tenses[tense][voice][mood][list(persons.keys())[index]] == '---':
										if not unc_flag:
											tenses[tense][voice][mood][list(persons.keys())[index]] = page_list[i].strip()
										else:
											build(uncontracted,tense,voice,mood)
											uncontracted[tense][voice][mood][list(persons.keys())[index]] = page_list[i].strip()
									index += 1
							elif mood == 'Infinitive':
								if index >= len(voices):
									index %= len(voices)
								if tenses[tense][voices[index]][mood] == '---':
									if not unc_flag:
										tenses[tense][voices[index]][mood] = page_list[i].strip()
									else:
										build(uncontracted,tense,voice,mood)
										uncontracted[tense][voices[index]][mood] = page_list[i].strip()
									index += 1
							elif mood == 'Participle':
								if index >= len(voices):
									index %= len(voices)
								if page_list[i].strip() in codec:
									gender = codec[page_list[i].strip()]
									continue
								elif gender and tenses[tense][voices[index]][mood][gender] == '---':
									if unc_flag == False:
										tenses[tense][voices[index]][mood][gender] = page_list[i].strip()
									else:
										build(uncontracted,tense,voices[index],mood)
										uncontracted[tense][voices[index]][mood][gender] = page_list[i].strip()
								index += 1
	for tense in uncontracted.keys():
		tenses[f'{tense} (Uncontracted)'] = uncontracted[tense]
	return tenses

def retreive_noun_forms(template):
	html_doc = tables.get_html(template['search word'])
	print(f"template['gender'] = {template['gender']}")
	three_ending = True if template['gender'] == '(m,f,n)' else False
	two_ending = True if template['gender'] == '(m/f,n)' else False
	print(f" three_ending = {three_ending}, two_ending = {two_ending}")
	if 'proper' in template:
		proper = True if template['proper'] else False
	else:
		proper = False
	if html_doc == None:
		return
	soup = BeautifulSoup(html_doc, 'html.parser')
	page_list = soup.prettify().split('\n')
	page_list = clean_page_list(page_list)

	cases = {"Nominative":'','Genitive':'','Dative':'','Accusative':'','Vocative':''}
	numbers = {'Singular':'---','Dual':'---',"Plural":'---'}
	genders = {'Masculine':'---','Feminine':'---','Neuter':'---'}
	article = {'article':'','form':'---'}
	if three_ending or two_ending:
		for n in numbers:
			numbers[n] = deepcopy(genders)
	else:
		for n in numbers:
			numbers[n] = deepcopy(article)
	for case in cases:
		cases[case] = deepcopy(numbers)

	case = False
	indent = 0
	for i in range(len(page_list)):
		if count_indent(page_list[i]) < indent - 2:
			break
		if page_list[i].strip() in cases:
			if not indent:
				indent = count_indent(page_list[i])
			case = page_list[i].strip()
			index = 0
		if case:
			emdash = True if page_list[i].strip() == '—' else False
			if three_ending:
				if index % 2 != 0 or emdash:
					if index <= 6:
						number = 'Singular'
					elif index <= 12:
						number = 'Dual'
					elif index <= 18:
						number = 'Plural'
					else:
						if case == "Vocative":
							break
						case = False
						continue
					key_list = ['Masculine','Feminine','Neuter']
					cases[case][number][key_list[index//2%3]] = page_list[i].strip()
			if two_ending:
				if index % 2 != 0 or emdash:
					if index <= 4:
						number = 'Singular'
					elif index <= 8:
						number = 'Dual'
					elif index <= 12:
						number = 'Plural'
					else:
						if case == "Vocative":
							break
						case = False
						continue
					key_list = ['Masculine','Neuter']
					cases[case][number][key_list[index//2%2]] = page_list[i].strip()
			elif not two_ending and not three_ending:
				if index % 3 != 0 or emdash:
					if index <= 3:
						number = 'Singular'
					elif index <= 6:
						number = 'Dual'
					elif index <= 9:
						number = 'Plural'
					else:
						if case == "Vocative":
							break
						case = False
						continue
					if case == "Vocative":
						if "notes" in page_list[i].lower():
							break
						elif proper and number != 'Singular':
							break
						cases[case][number]['form'] = page_list[i].strip()	
						index += 1
					elif proper:
						cases[case][number]['form'] = page_list[i].strip()	
						index += 1
					else:
						key_list = ['article','form']
						cases[case][number][key_list[index%3-1]] = page_list[i].strip()					
			index += 2 if emdash else 1
	return cases

def add_tables():
	tables_list = tables.get_tables('Ancient Greek')

	table_info = {'title':'','type':''}
	table_file = "AncientGreek-tables.txt"
	
	while True:	
		print("Use table template? ('1' for yes, '0' to go back, any other key for no) 'AUTO' to auto-add all forms")
		user_input =  input(": ")
		if user_input == '1':
			template = tables.get_template('Ancient Greek')
			if template == None:
				continue
			table_info['title'] = template['title']
		elif user_input.upper() == 'AUTO':
			auto_add([],table_info,table_file)
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
			options = {'1':"'1'> noun\n",'2':"'2'> verb principal parts\n",'3':"'3'> verb conjugation\n",'4':"'4'> noun + dual\n",'5':"'5'> complete verb system\n",'6':"'6'> complete forms\n"}
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
				table_info['type'] = 'dual'
			elif user_input == '5':
				table_info['type'] = 'conj'
				complete = True
			elif user_input == '6':
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
							table_info['defno'] = user_input

				if complete:
					if table_info['type'] == 'conj':
						add_complete_verb_system(template,table_info,tables_list,table_file)
					elif table_info['type'] == 'form':
						add_complete_forms(template)
					exit_second_loop = exit_third_loop = True
					print("tables added succesfully")
					continue

				exit_loop_four = False
				while not exit_loop_four:
					print(f"Do you want to auto-retreive {table_info['title']}? ('1' for yes, '0' to go back, '00' to exit)")
					user_input = input(": ")
					if user_input == '1':
						if table_info['type'] in ['parts','conj']:
							table_info = auto_retreive_verb(table_info,template)
						else:
							table_info = auto_retreive_noun(table_info,template)
						if result:
							tables_list = tables.add_table(tables_list)
							tables.save_tables(tables_list,'AncientGreektables.txt')
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
	template_file = "AncientGreek_templates.txt"
	if template_file not in myFiles:
		print(f"file: {template_file} not found")
		return
	else:
		with open(template_file,'r') as f:
			templates = json.load(f)

	for template in templates:
		debug_print(f"Begin: {template['title']}")
		i = template
		#add_complete_forms(template)

		table_info['definition'] = template['definition']
		if template["POS"] == 'verb':
			
			table_info['type'] = 'conj'
			#for template in templates:
			
			debug_print(f"Running add_complete_verb_system")
			add_complete_verb_system(template,table_info,tables_list,table_file)
			debug_print(f"add_complete_verb_system successful")
		
		if template["POS"] == 'noun':
			
			table_info['type'] = 'noun'
			if template['gender'] == "(m,f,n)" or template['gender'] == "(m/f,n)":
				continue
			
			debug_print(f"Running auto_retreive_noun")
			table_info = auto_retreive_noun(table_info,template)
			debug_print(f"auto_retreive_noun successful")

		debug_print(f"Running add_table")
		tables_list = tables.add_table(tables_list,table_info)
		debug_print(f"add_table successful")
	tables.save_tables(tables_list,table_file)


def empty(item):
	if type(item) != dict:
		return True if item == '---' or item == '—' else False
	for key in item:
		if not empty(item[key]):
			return False
	return True

"""
[{'title':'capere','instances':[
{'root':template['title'],
'features':{x:y for x,y in template['forms'] if x != 'form'}
'principal:template['principal'],
'definition':template['definition'],
}
]}
]
"""

def add_complete_forms(template):
	forms_list = tables.get_forms("Ancient Greek")
	for i in range(len(template['forms'])):
		if not debug_print:
			print('*',end='',flush=True)
		found = False
		for x in range(len(forms_list)):
			if forms_list[x]['title'] == template['forms'][i]['form']:
				found = True
				instance = {'form':template['forms'][i]['form']}
				instance['root'] = template['title']
				instance['features'] = {x:y for x,y in template['forms'][i].items() if x != 'form'}

				same = True
				for y in forms_list[x]['instances']:
					for key in y['features'].keys():
						if key not in instance['features']:
							same = False
							break
						else:
							if y['features'][key] != instance['features'][key]:
								if debug_print:
									print(f"NOT SAME {y['features']} AND {instance['features']}")
								same = False
								break
					if not same:
						break
				if same:
					debug_print(f"rejected DUPLICATE")						
					break
				if 'tense' in instance['features']:
					if instance['features']['tense'] not in ["Present",'Imperfect','Future','Aorist']:
						debug_print(f"rejected {instance['features']['tense']}")						
						break
				if 'mood' in instance['features']:
					if instance['features']['mood'] in ["Subjunctive",'Imperative','Optative']:
						debug_print(f"rejected {instance['features']['mood']}")						
						break
				if 'number' in instance['features']:
					if instance['features']['number'] == 'Dual':
						debug_print(f"rejected {instance['features']['number']}")						
						break
				if 'person' in instance['features']:
					if instance['features']['person'] in ['2nd Person Dual','3rd Person Dual']:
						debug_print(f"rejected {instance['features']['person']}")						
						break
				instance['principal'] = template['principal']
				instance['definition'] = template['definition']
				
				
				debug_print("ADDING TO EXISTING")
				debug_print(instance)
				if not DEBUG:
					print('<',end='',flush=True)
				forms_list[x]['instances'].append(deepcopy(instance))


		if not found:
			form = {'title':template['forms'][i]['form']}
			instance = {'form':template['forms'][i]['form']}
			instance['root'] = template['title']
			instance['features'] = {x:y for x,y in template['forms'][i].items() if x != 'form'}
			if 'tense' in instance['features']:
				if instance['features']['tense'] not in ["Present",'Imperfect','Future','Aorist']:
					debug_print(f"rejected {instance['features']['tense']}")					
					continue
			if 'mood' in instance['features']:
				if instance['features']['mood'] in ["Subjunctive",'Imperative','Optative']:
					debug_print(f"rejected {instance['features']['mood']}")					
					continue
			if 'number' in instance['features']:
				if instance['features']['number'] == 'Dual':
					debug_print(f"rejected {instance['features']['number']}")					
					continue
			if 'person' in instance['features']:
				if instance['features']['person'] in ['2nd Person Dual','3rd Person Dual']:
					debug_print(f"rejected {instance['features']['person']}")					
					continue
			instance['principal'] = template['principal']
			instance['definition'] = template['definition']
			form['instances'] = [deepcopy(instance)]

			
			debug_print("ADDING NEW")
			debug_print(instance)
			if not debug_print:
				print('+',end='',flush=True)
			forms_list.append(deepcopy(form))

	file = 'AncientGreek_forms.txt'

	tables.add_tables(forms_list)



def add_complete_verb_system(template,table_info,tables_list,table_file):

	table_info['principal'] = template['principal']
	tenses = template['parts']
	for tense in ["Present",'Imperfect','Future','Aorist']:
		debug_print(f"Tense: {tense}")
		for voice in ["Active","Middle/Passive","Middle",'Passive']:
			debug_print(f"Voice: {voice}")

			debug_print("Running assign_table_info")
			table_info = assign_table_info(table_info,template,tenses,tense,voice,'Indicative')
			debug_print("assign_table_info run succesfully")

			if empty(table_info['parts']):
				debug_print(f"\t\t{table_info['title']} was blank")
				continue
			else:
				tables_list = tables.add_table(tables_list,table_info)
				debug_print(f"\t\t{table_info['title']} saved")
	table_info['type'] = 'parts'
	table_info = assign_principle_parts(table_info,tenses,template)
	tables_list = tables.add_table(tables_list,table_info)

def auto_retreive_verb(table_info,template):
	tenses = template['parts']
	if table_info['type'] == 'parts':
		table_info = assign_principle_parts(table_info,tenses,template)
		return table_info
	elif table_info['type'] == 'conj':
		options1 = {'1':"Present",'2':'Imperfect','3':'Future','4':'Aorist','5':'Perfect'}
		user_input = get_selection(options1,2)
		tense = options1[user_input]
		options2 = {'1':"Active",'2':"Middle/Passive",'3':"Middle",'4':'Passive'}
		user_input = get_selection(options2,2)
		voice = options2[user_input]
		options3 = {'1':'Indicative','2':'Subjunctive','3':'Optative','4':'Imperative'}
		user_input =  get_selection(options3,2)
		mood = options3[user_input]
		table_info = assign_table_info(table_info,template,tenses,tense,voice,mood)
		return table_info

def assign_table_info(table_info,template,tenses,tense,voice,mood):
	table_info['parts'] = {
		'1st Person':{
			'Singular':tenses[tense][voice][mood]['1st Person Singular'],\
			'Plural':tenses[tense][voice][mood]['1st Person Plural']},\
		'2nd Person':{
			'Singular':tenses[tense][voice][mood]['2nd Person Singular'],\
			'Plural':tenses[tense][voice][mood]['2nd Person Plural']},\
		'3rd Person':{
			'Singular':tenses[tense][voice][mood]['3rd Person Singular'],\
			'Plural':tenses[tense][voice][mood]['3rd Person Plural']}}
	table_info['parts'].update({'Infinitive':tenses[tense][voice]['Infinitive']})
	table_info['parts'].update({'Participle':{
		'Masculine':tenses[tense][voice]['Participle']['Masculine'],\
		'Feminine':tenses[tense][voice]['Participle']['Feminine'],\
		'Neuter':tenses[tense][voice]['Participle']['Neuter']}})
	if template:
		table_info['title'] = f"{tense.title()} {voice.title()} {mood.title()}: {template['title']}"
	return table_info

def auto_retreive_noun(table_info,template):
	table_info['principal'] = template['principal']
	parts = template['parts']
	case_keys = ["Nominative",'Genitive','Dative','Accusative','Vocative']
	number_keys = ['Singular','Dual',"Plural"]
	table_info['parts'] = {}
	for case in case_keys:
		table_info['parts'][case] = {}
		for number in number_keys:
			if number == 'Dual' and table_info['type'] != 'dual':
				continue
			if 'article' in parts[case][number]:
				if parts[case][number]['article'] != "":
					table_info['parts'][case][number] = parts[case][number]['article'] + " " + parts[case][number]['form']
				else:
					table_info['parts'][case][number] = parts[case][number]['form']
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
	perfmidsubj = ['ὦ','ᾖς','ᾖ','ἦτον','εἴην','εἴης','εἴη','εἴητον','εἶτον','εἰήτην','εἴτην','ὦμεν','ἦτε','ὦσῐ','ὦσῐ(ν)','εἴημεν','εἶμεν','εἴητε','εἶτε','εἴησᾰν','εἶεν']
	#articles = ["ὁ, ἡ"	,	"οἱ, αἱ"	,	"τοῦ, τῆς"	,	"τῷ, τῇ"	,	"τοῖς, ταῖς"	,	"τὸν, τὴν"	,	"τοὺς, τᾱ̀ς"]
	for i in range(1,len(page_list)):
		i = i - offset
		if page_list[i].strip(' ') == 'passive' and page_list[i - 1].strip(' ') == 'middle/':
			page_list[i] = 'middle/passive'
			del page_list[i - 1]
			offset += 1
		elif page_list[i].strip(' ') == ',':
			page_list[i - 1] = page_list[i - 1].rstrip(' ') + ", " + page_list[i + 1].strip(' ')
			del page_list[i + 1]
			del page_list[i]
			offset += 2
		elif page_list[i].strip(' ') == 'ν':
			if page_list[i - 1].strip(' ') == '(':
				page_list[i - 2] = page_list[i - 2].rstrip(' ') + '(ν)'
				del page_list[i + 1]
				del page_list[i]
				del page_list[i - 1]
				offset += 3
			else:
				page_list[i - 1] = page_list[i - 1].rstrip(' ') + '(ν)'
				del page_list[i + 1]
				del page_list[i]
				offset += 2
		elif page_list[i].strip(' ') == 'σ':
			if page_list[i - 1].strip(' ') == '(':
				page_list[i - 2] = page_list[i - 2].rstrip(' ') + '(σ)' + page_list[i + 2].strip(' ')
				del page_list[i + 2]
				del page_list[i + 1]
				del page_list[i]
				del page_list[i - 1]	
				offset += 4	
			else:
				page_list[i - 1] = page_list[i - 1].rstrip(' ') + '(σ)' + page_list[i + 2].strip(' ')
				del page_list[i + 2]
				del page_list[i + 1]
				del page_list[i]
				offset += 3
		elif page_list[i].strip(' ') == '/':
			page_list[i - 1] = page_list[i - 1].rstrip(' ') + "/" + page_list[i + 1].strip(' ')
			del page_list[i + 1]
			del page_list[i]
			offset += 2
		elif page_list[i].strip(' ')[:1] == ')' and page_list[i - 2].strip(' ')[-1] == '(':
			page_list[i - 2] = page_list[i - 2].rstrip(" ") + page_list[i - 1].strip(" ") + page_list[i].strip(' ')
			for x in range(2):
				del page_list[i - 1]
			offset += 2
		elif page_list[i].strip(' ') in perfmidsubj and previous not in perfmidsubj and not exception:
			page_list[i - 1] = page_list[i - 1].rstrip(' ') + ' ' + page_list[i].strip(' ')
			previous = page_list[i].strip(' ') 
			del page_list[i]
			offset += 1
		elif page_list[i].strip()[0] == "<" or (len(page_list[i].strip()) == 1 and page_list[i].strip().isnumeric()):
			del page_list[i]
			offset += 1
		else:
			previous = ''
	return page_list

"""
[{'title':'capere','instances':[
{'root':template['title'],
'features':{x:y for x,y in template['forms'] if x != 'form'}
'principal:template['principal'],
'definition':template['definition'],
}
]}
]
"""

def features_join(features):
	join = ""
	if 'gender' in features:
		join += " <b>" + features['gender'] + "</b>" 
	for x,y in features.items():
		if x != 'article':
			if x == "mood" and (y != "Infinitive" and y != 'Participle'):
				join += " <em>" + y + "</em>"
			elif x == 'gender':
				pass
			else:
				join += " <b>" + y + "</b>"
	return join.strip()

def print_forms():
	out_file = 'AncientGreek-FormCards.txt'
	original_stdout = sys.stdout 
	change_path(FORMATTED_FLASHCARD_FILES)
	sys.stdout = open(out_file,'w')
	forms_list = tables.get_forms("Ancient Greek")
	random_list = list(range(len(forms_list)))
	random.shuffle(random_list)
	for i in random_list:
		print('<P align="left"!--FORM-->· ' + forms_list[i]['title'] + '</P>|',end='')
		for instance in forms_list[i]['instances']:
			features = features_join(instance['features'])
			if 'article' in instance['features']:
				print('<P align="left" style="line-height:1.5">' + instance['features']['article'] + " " + instance['form'] + '<br>',end='')
			else:
				print('<P align="left" style="line-height:1.5">',end='')
			print(features,end='')
			print(' form of: <b>' + instance['principal'] + '</b><br>',end='')
			print("Definition: " + instance['definition'] + '</P><br>',end='')
		print('|"forms"')
	sys.stdout = original_stdout


def print_tables(tables_list):
	print_forms()
	out_file = 'AncientGreek-TableCards.txt'
	original_stdout = sys.stdout 
	change_path(FORMATTED_FLASHCARD_FILES)
	sys.stdout = open(out_file,'w')
	random_list = list(range(len(tables_list)))
	random.shuffle(random_list)
	for i in random_list:
		
		if tables_list[i]['type'] != 'noun':
			print('<P align="left">' + tables_list[i]['title'] + '</P>|',end='')
		else:
			print('<P align="left">Forms: ' + tables_list[i]['title'] + '</P>|',end='')
		
		if tables_list[i]['definition']:
			body_string = '<P align="left" style="line-height:1.5">' + tables_list[i]['definition'] + '<br>'
		else:
			body_string = ''
		if tables_list[i]['principal'] and tables_list[i]['type'] != 'parts':
			body_string +=  "Parts:<b> " + tables_list[i]['principal'] + '</b><br>'
		body_string += '</P>'

		body_string = html_x.set_styles(body_string)

		if tables_list[i]['type'] == 'parts':
			body_string = html_x.create_table(body_string,tables_list[i]['parts'],'parts',1)
		elif tables_list[i]['type'] == 'noun':
			body_string = html_x.create_table(body_string,tables_list[i]['parts'],'noun',2)
		elif tables_list[i]['type'] == 'conj':
			parts = {k:v for k,v in tables_list[i]['parts'].items() if k != "Infinitive" and k != "Participle"}
			body_string = html_x.create_table(body_string,parts,'conj',2)
			body_string = html_x.create_style(body_string,1)
			body_string = html_x.create_box(body_string,'Infinitive',tables_list[i]["parts"]["Infinitive"])
			parts = {k:v for k,v in tables_list[i]['parts'].items() if k == "Participle"}
			parts = {k:{'Participle':v} for k,v in parts['Participle'].items()}
			body_string = html_x.create_table(body_string,parts,'Participle',1)

		print(body_string + '|"table"')

	sys.stdout = original_stdout