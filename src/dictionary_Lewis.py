

import parser_shell
from load_dict import change_path
from copy import deepcopy
import edit_all
import pickle
import beta_code
from language_splitter import split_language
from unidecode import unidecode 

import inspect

def current_line_number():
    return inspect.currentframe().f_back.f_lineno

def extract_dictionary(lewis, dictionary,debug_print=False):
	keys = set()
	values = set()
	for i in lewis:
		for key,value in i.items():
			if key not in {'entry_type', 'title_orthography', 'main_notes', 'alternative_genative', 'key', 'greek_word', 'part_of_speech', 'gender', 'alternative_orthography', 'senses', 'declension', 'title_genitive'}:
				if debug_print:
					print("\n\n\n\t\t\t" + "*"*1000 + f"\n\nLINE: {current_line_number()}")  
					print(f"\n  KEY:\n{key}\n\nVALUE:\n{value}")
					print(f"KEY NOT IN LIST!!!")
					exit()
			keys.add(key)
		print('\n\n')

	print(keys)

	

	def get_entry(i,debug_print):
		counter = 0
		counter_princ_parts = -10000000
		counter_grk = -10000000
		counter_senses = -10000000
		entry = {}
		if i['entry_type'] in {'main','hapax','greek','foreign'}:
			entry['partOfSpeech'] = i['part_of_speech']
			if not isinstance(i['main_notes'],str):
				for item in i['main_notes']:
					entry['defs'].append({'gloss':item,'tags':[]})
				if debug_print:
					print("\n\n\n\t\t\t" + "*"*1000 + f"\n\nLINE: {current_line_number()}") 
					print(f"entry['defs'] = {entry['defs']}")
					exit()
			else:
				entry['defs'] = [{'gloss':i['main_notes'],'tags':[]}]

			if 'alternative_orthography' in i:
				entry['principleParts'] = i['alternative_orthography']
				for x in range(6):
					if debug_print:
						print("\n\n\n\t\t\t" + "*"*1000 + f"\n\nLINE: {current_line_number()}") 
					if isinstance(i['alternative_orthography'],list):
						i['alternative_orthography'] = i['alternative_orthography'][0]
				if debug_print:
					print("\n\n\n\t\t\t" + "*"*1000 + f"\n\nLINE: {current_line_number()}")  
					print(f"['alternative_orthography'] == {i['alternative_orthography']}")
					print(entry)
				if 'alternative_genative' in i:
					if debug_print:
						print("\n\n\n\t\t\t" + "*"*1000 + f"\n\nLINE: {current_line_number()}")  
						print(f"i = {i}")
					if isinstance(i['alternative_genative'],list):
						i['alternative_genative'] = i['alternative_genative'][0]


					entry['principleParts'] = i['alternative_orthography'] + " (" + i['alternative_genative'] + ")"
					
					if debug_print:
						print("\n\n\n\t\t\t" + "*"*1000 + f"\n\nLINE: {current_line_number()}")  
						print(f"i['alternative_genative'] == {i['alternative_genative']}")
						print(entry)
			if 'title_orthography' in i and i['title_orthography']:
				if debug_print:
					print("\n\n\n\t\t\t" + "*"*1000 + f"\n\nLINE: {current_line_number()}")  
					print(f"['title_orthography'] == {i['title_orthography']}")
					print(entry)
				entry['principleParts'] = i['title_orthography']
				if 'title_genitive' in i and i['title_genitive']:
					if debug_print:
						print("\n\n\n\t\t\t" + "*"*1000 + f"\n\nLINE: {current_line_number()}")  
						print(f"['title_genitive'] == {i['title_genitive']}")
						print(entry)
					entry['principleParts'] = i['title_orthography'] + " (" + i['title_genitive'] + ")"
					

			if 'senses' in i:
				for sense in i['senses']:
					def get_senses(entry,sense):
						counter = 0
						if isinstance(sense,list):
							for item in sense:
								get_senses(entry,item)
						else:
							entry['defs'].append({'gloss':sense,'tags':[]})
					get_senses(entry,sense)

					if debug_print:
						print("\n\n\n\t\t\t" + "*"*1000 + f"\n\nLINE: {current_line_number()}")  
						print(f"entry with senses = ")
						for x, item in enumerate(entry['defs']):
							print(f"{x+1} tags: {item['tags']} gloss: {item['gloss']}")
						print(f"senses limit reached ")
						if counter_senses > 5:
							exit()
						else:
							counter_senses += 1

			if 'greek_word' in i:
				
				if debug_print:
					print("\n\n\n\t\t\t" + "*"*1000 + f"\n\nLINE: {current_line_number()}")  
					print(f"['greek_word'] == {i['greek_word']}")
					
					entry['defs'].append({'gloss':i['greek_word'],'tags':['greek_word']})
					print(f"entry == {entry}")
					if counter_grk > 1:
						print(f"Greek Word Break")
						exit()
					else:
						counter_grk += 1
		else:
			if i['entry_type'] in {'spur','gloss'}:
				return None
			if debug_print:
				print("\n\n\n\t\t\t" + "*"*1000 + f"\n\nLINE: {current_line_number()}")  
				print(f"i['entry_type'] == 'main' == {i['entry_type'] == 'main'}")
				print(f"i['entry_type'] == {i['entry_type']}")
				print(i)

				#exit()
		if 'principleParts' not in entry:
			
			defs = entry['defs'][0]['gloss']
			defs = defs.split()
			gloss = ''
			tag = ''
			flag = False
			for x, q in enumerate(defs):
				if debug_print:
					print("\n\n\n\t\t\t" + "*"*1000 + f"\n\nLINE: {current_line_number()}") 
					print(f"defs = {defs}")
					print(f"q = {q}")
					print(f"q[-1] = {q[-1]}")
				if (x and q[0].isupper()) or q[0] == '(' or q[0].isnumeric():
					break
				if ((q[-1] == ',' and not flag) or (x == len(defs)-1 and not flag)  or x == 0) and not (q[-1] == '.'):
					gloss += q.strip(":") + ' '
				else:
					tag += q + ' '
				if q[-1] == ':':
					if debug_print:
						print("\n\n\n\t\t\t" + "*"*1000 + f"\n\nLINE: {current_line_number()}") 
						print(f"End in colon is True = {q[-1]}")
					break
				if q[-1] != ',':
					flag = True
					continue
				

			if tag.strip():
				entry['principleParts'] = gloss.strip(", ") + " (" + tag.strip() + ")"
			else:
				entry['principleParts'] = gloss.strip(", ")
				if debug_print:
					print("\n\n\n\t\t\t" + "*"*1000 + f"\n\nLINE: {current_line_number()}")  
					if counter_princ_parts > 4: 
						print("'principleParts' not in entry")
						print(i['entry_type'])
						print(f"entry = {entry}")
						print(f"final {entry['principleParts']}",flush=True)
						exit()
					else:
						for x in entry['defs']:
							if isinstance(x['gloss'],list):
								print(f"Gloss = List {x['gloss']}",flush=True)
								print(f"i = {i}")
								exit()
						print("'principleParts' not in entry")
						print(f"increment {entry['principleParts']}")
						counter_princ_parts += 1
		return entry
	for i in lewis:
		entry = get_entry(i,debug_print)
		if entry:
			dictionary['definitions'].append({'entries':[entry],'heading':i['key'],'handle':unidecode(i['key']),'tags':set()})
			
import json

def Lewis(new_dictionary={'definitions':[]}):



	change_path('texts')
	change_path('lewis-short-json-master')

	dictionary = {'file':'','definitions':[],"language":''}

	for i in range(0,1):
		json_file = 'ls_' + chr(i+65) + '.json'
		with open(json_file,'r') as f:
			print(f"Successfully opened '{'ls_' + chr(i+65) + '.json'}'",flush=True)
			lewis = json.load(f)
		extract_dictionary(lewis,dictionary)

	new_dictionary['definitions'].extend(dictionary['definitions'])
	
	return new_dictionary
print(Lewis())


