'''
Utility function for parsing xml files of "Middle Liddell" and "LSJ" lexicons
Imported by dictionary_LSJ.py and dictionary_Middle_Liddel.py
'''
import beta_code
from copy import deepcopy

debug_print = False

# Print Progress
def printpr(counter, modulo=10000):
	if counter % modulo == 0:
		print(".",end='',flush=True)
	if counter % (modulo*100) == 0:
		print(f' {counter:,} lines parsed',flush=True)

def cut_text(text,start,stop):
	'''	cut string according to start and stop integer arguments
	'''
	p = text.find(start) + len(start)
	text = text[p:]
	text = text[:text.find(stop)]
	return text

def translate_greek(text,bold):
	''' convert beta code to unicode
	'''
	text = list(text)
	text = [x for x in text if not x.isnumeric()]
	text = "".join(text)
	if bold:
		return "<b>" + beta_code.beta_code_to_greek(text) + "</b>"
	else:
		return beta_code.beta_code_to_greek(text)

def smart_join(text):
	'''	Fixes recurring errors in spacing after punctuation from get_defs algorithm
	'''
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


def configure_parts(senses):
	'''	somehow compiles principle parts from top lines of senses.
		Need to review this code and comment in more detail.
	'''
	count = 0

	for i in senses[0]['gloss']:
		if i == "(":
			count += 1

		if i == ")" and count != 0:
			count -= 1

		if count < 0:
			# Error too many )s, unbalanced parens
			print(senses[0]['gloss'])
			print(senses[1]['gloss'])
			break

	if count != 0:
		parens = 0

		for i in range(len(senses[1]['gloss'])):
			if senses[1]['gloss'][i] == ")":
				parens += 1

			if senses[1]['gloss'][i] == "(":
				parens -= 1

			if parens == count:
				break

		if i < len(senses[1]['gloss']) - 1:
			senses[0]['gloss'] = smart_join([senses[0]['gloss'],senses[1]['gloss'][: i + 1]])
			senses[1]['gloss'] = senses[1]['gloss'][i + 1 :]

			for i in range(len(senses[1]['gloss'])):
				if senses[1]['gloss'][i].isalpha() or senses[1]['gloss'][i] == "=":
					break
			senses[1]['gloss'] = senses[1]['gloss'][i:]
		else:
			senses[0]['gloss'] += ")"

	return senses

def process_entry(text,tag):
	''' Process a definition from the persues file to find the
		pieces corresponding to the word-hoarder defintiion data structure
	'''

	'''	create the blank data structures
		definitions will have only one entry until they are deplicated and combined
	'''
	definition = {'heading':'',
				'handle':'',
				'tags':set(),
				'entries':[]}

	entry = {'senses':[],
			'partOfSpeech':'',
			'principleParts':'',
			'simpleParts':'',
			'etymology':''}

	# key contains the handle
	handle = cut_text(text,"key=\"","\"")
	definition['heading'] = definition['handle'] = translate_greek(handle,bold=False)
	
	'''	debug_print blasts out a massive amount of text showing what is being 
		assigned to what
	'''
	if debug_print:
		print("@"*5000 + f"\nheading \"{definition['heading']}\"")

	# get_def takes bites off remaining text until it is empty
	while text != "":
		text, senses = get_def(text)

		for x in senses:
			if debug_print:
				print(f"definition: {x['gloss']}")
			entry['senses'].append(deepcopy(x))

	'''	top line of definition contains the principles parts in some cases 
		and not in othes
	'''
	if len(entry['senses']) > 1:
		entry['senses'] = configure_parts(entry['senses'])
		entry['simpleParts'] = entry["principleParts"] = entry['senses'][0]['gloss']
		entry['senses'].pop(0)
	else:
		entry['simpleParts'] = entry["principleParts"] = definition['heading']

	definition['entries'].append(deepcopy(entry))
	definition['tags'].add(tag)
	return definition

def get_def(text):
	'''	Uses xml tags to recognize beginning and ending of senses
		Also spots greek beta code that needs to be translated
	'''
	m = 0
	gloss = []
	senses = []
	greek = False
	candidate_tag = ''
	while True:
		pull = text[:text.find("<")]
		brac = text[text.find("<"):text.find(">")+1]
		text = text[text.find(">") + 1:]

		if greek and pull != "":
			pull = translate_greek(pull,bold=True)
			greek = False

		if 'lang=\"greek\"' in brac:
			greek = True

		if "<sense" in brac:
			gloss = smart_join(gloss).strip(",. ")
			if gloss != "":
				senses.append({'gloss':gloss,'tags':[]})
			gloss = []

		if pull != "":
			gloss.append(deepcopy(pull))

		if brac == "</sense>" or text == "":
			gloss = smart_join(gloss).strip(",. ")
			if gloss != "":
				senses.append({'gloss':gloss,'tags':[]})
			break

	return text, senses



