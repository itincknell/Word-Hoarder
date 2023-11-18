

import parser_shell
from load_dict import change_path
from copy import deepcopy
import edit_all
import pickle
import beta_code
from language_splitter import split_language
from dict_utilities import printpr

debug_print = False
progress_print = True

interval = 1000
level = 0
start = (interval * level)
stop = (interval) * (level + 1)

def cut_text(text,start,stop):
	p = text.find(start) + len(start)
	text = text[p:]
	text = text[:text.find(stop)]
	return text

def translate_greek(text,bold):
	text = list(text)
	text = [x for x in text if not x.isnumeric()]
	text = "".join(text)
	if bold:
		return "<b>" + beta_code.beta_code_to_greek(text) + "</b>"
	else:
		return beta_code.beta_code_to_greek(text)


def smart_join(text):
	if debug_print:
		print(text)
	s = ""
	for i in range(len(text)):
		if i == 0:
			s = text[i]
		else:
			if s[-1] != " " and s[-1] not in ['('] and text[i][0] != " " and text[i][0] not in [',','.',';',')','?']:
				s += " " + text[i]
			else:
				s += text[i]
	return s.replace(" .",".").replace(" ,",",").replace(" :",":")

def configure_parts(defs):
	count = 0
	for i in defs[0]['gloss']:
		if i == "(":
			count += 1
		if i == ")" and count != 0:
			count -= 1
		
		if count < 0:
			# Unbalance parens
			if debug_print:
				# need db printing function for line and function info
				print(defs[0]['gloss'])
				print(defs[1]['gloss'])
			break

	if count != 0:
		if debug_print:
			# need db printing function
			print(defs[0]['gloss'])
			print(defs[1]['gloss'])

		parens = 0
		for i in range(len(defs[1]['gloss'])):
			if defs[1]['gloss'][i] == ")":
				parens += 1
			if defs[1]['gloss'][i] == "(":
				parens -= 1
			if parens == count:
				break
		if i < len(defs[1]['gloss']) - 1:
			defs[0]['gloss'] = smart_join([defs[0]['gloss'],defs[1]['gloss'][: i + 1]])
			defs[1]['gloss'] = defs[1]['gloss'][i + 1 :]
			for i in range(len(defs[1]['gloss'])):
				if defs[1]['gloss'][i].isalpha() or defs[1]['gloss'][i] == "=":
					break
			defs[1]['gloss'] = defs[1]['gloss'][i:]
		else:
			defs[0]['gloss'] += ")"

		if debug_print:	
			# These statements are all useless
			print(defs[0]['gloss'])
			print(defs[1]['gloss'])
	return defs


def process_entry(text):
	definition = {'heading':'',
				'handle':'',
				'tags':set("Middle Liddell"),
				'entries':[]}

	entry = {'defs':[],
			'partOfSpeech':'',
			'principleParts':'',
			'simpleParts':'',
			'etymology':''}

	handle = cut_text(text,"key=\"","\"")
	if debug_print:
		print(handle)

	definition['heading'] = definition['handle'] = translate_greek(handle,False)

	if debug_print:
		print("@"*5000 + f"\nheading \"{definition['heading']}\"")

	while text != "":
		text, defs = get_def(text)

		for x in defs:
			if debug_print:
				print(f"definition: {x['gloss']}")
			entry['defs'].append(deepcopy(x))
		
	if len(entry['defs']) > 1:
		entry['defs'] = configure_parts(entry['defs'])
		entry['simpleParts'] = entry["principleParts"] = entry['defs'][0]['gloss']
		entry['defs'].pop(0)
	else:
		entry['simpleParts'] = entry["principleParts"] = definition['heading']
	definition['entries'].append(deepcopy(entry))
	definition['tags'].add("Middle Liddell")

	if debug_print:
		print(definition)
	return definition

def get_def(text):
	m = 0
	gloss = []
	defs = []
	greek = quote = author = False
	candidate_tag = ''
	while True:
		pull = text[:text.find("<")]
		brac = text[text.find("<"):text.find(">")+1]
		text = text[text.find(">") + 1:]

		if greek and pull != "":
			pull = translate_greek(pull,True)
			greek = False

		if 'lang=\"greek\"' in brac:
			greek = True

		if "<sense" in brac:
			gloss = smart_join(gloss).strip(",. ")
			if gloss != "":
				defs.append({'gloss':gloss,'tags':[]})
			gloss = []

		if pull != "":
			gloss.append(deepcopy(pull))

		if brac == "</sense>" or text == "":
			gloss = smart_join(gloss).strip(",. ")
			if gloss != "":
				defs.append({'gloss':gloss,'tags':[]})
			break

	return text, defs

def extract_dictionary(perseus, dictionary):
	line_list = []
	ignition = False
	for i in range(len(perseus)):

		if "<entry" in perseus[i]:
			ignition = True
		if ignition:
			line_list.append(perseus[i].strip(" \n\t"))
		if "</entry" in perseus[i] and ignition:
			line_list.append(perseus[i].strip())
			line_list = "".join(line_list)
			dictionary['definitions'].append(process_entry(line_list))
			ignition = False
			line_list = []
	return dictionary

def middle_liddell(new_dictionary):

	change_path('texts')

	dictionary = {'file':'','definitions':[],"language":''}

	with open('Perseus_text_1999.04.0058.txt','r') as f:
		if progress_print:
			print(f"Parsing 'Perseus_text_1999.04.0058.txt': ",flush=True,end='')

		line_list = []
		ignition = False
		counter = 0
		for line in f.readlines():

			if "<entry" in line:
				ignition = True
			if ignition:
				line_list.append(line.strip(" \n\t"))
			if "</entry" in line and ignition:
				line_list.append(line.strip())
				line_list = "".join(line_list)
				dictionary['definitions'].append(process_entry(line_list))
				ignition = False
				line_list = []
			counter += 1
			if progress_print:
				printpr(counter)
			

		print(f' {counter:,} lines parsed',flush=True)

	new_dictionary['definitions'].extend(dictionary['definitions'])
	
	return new_dictionary




