'''
Description:

	get_simple:
		takes principle parts line from a wiktionary entry and
		chops out all extraneous word

	i_stem_test:
		look up the i-stem version of the gen plural of a 
		third declension noun to check if the noun is
		i-stem or not; returns true or false
'''

from unidecode import unidecode
import load_dict
import pickle


def load_dump():
	try:
		print("Loading previous Latin trie...")
		load_dict.change_path("dumps_sorted")
		with open("Latin" + '-trie.txt','rb') as openFile:
			t = pickle.load(openFile)
		return t['definitions']
	except FileNotFoundError:
		print("'Latin-trie.txt' not found in 'dumps_sorted' directory")
		return None


def load_i_stem_trie():
	load_dict.change_path("dumps_sorted")
	try:
		with open("Latin-i_stem_nouns-trie.txt",'rb') as openFile:
			t = pickle.load(openFile)
		return t['definitions']
	except FileNotFoundError:
		print("'Latin-i_stem_nouns-trie.txt' not found in 'dumps_sorted' directory")
		input("Enter to continue")
		return load_dump()

quickmode = True
i_stem_mode = False

if quickmode:
	t = load_i_stem_trie()
else:
	t = load_dump()

# CHOP PARTS
# # # # # # # # # # 
def chop_parts(parts):
	''' Chop parts down to simple list '''
	# cut off tail after closing paratheses
	if ';' in parts:
		parts = parts[:parts.find(';')]

	# separate into list
	parts = parts.split(' ')

	# remove punctuation
	for index in range(len(parts)):
		parts[index] = parts[index].strip(" ,()")

	return parts
# END CHOP PARTS


# REMOVE WORDS
# # #
def remove_words(parts,remove_words):
	""" Loop to remove extra words not part of principal parts """
	# need to reverse for special case of Latin word 'neuter'
	parts.reverse()

	# remove extraneous word
	for word in remove_words:
		if word in parts:
			parts.remove(word)

	# reverse back
	parts.reverse()
	return parts

# END REMOVE WORDS


# COMBINE DEPONENT
# # # # # # # # # # # # # # # 
def combine_deponent(parts):
	''' Loop for perfect active form of deponent verbs '''
	offset = 0
	for number in range(1,len(parts)):

		# when items combined index shrinks
		# very unlikely that this is needed twice
		index = number - offset

		# combine parts with '__ sum'
		if parts[index] == 'sum':
			popped = parts.pop(index)
			parts[index - 1] += f" {popped}"
			offset += 1
			
		index = number - offset

		# combine parts with '__ est'
		if parts[index] == 'est':
			popped = parts.pop(index)
			parts[index - 1] += f" {popped}"
			offset += 1

	return parts
# END COMBINE DEPONENT


# COMBINE 'OR'
# # # # # # # # # # # # # # # 
def combine_or(parts):
	""" Loop to combine part with __ or __ """
	offset = 0
	for number in range(len(parts)):

		# when items combined index shrinks
		index = number - offset

		# combine parts with __ or __
		if parts[index] == 'or':
			popped = parts.pop(index)
			parts[index - 1] += f" {popped}"
			popped = parts.pop(index)
			parts[index - 1] += f" {popped}"
			offset += 2

	return parts
# END COMBINE 'OR'


# DOUBLE NOUN
# # # # # # # # # # # 
def double_noun(parts):
	#print("\n\n\t\tACTIVE IF DOUBLE NOUN >>>>>>>>>>>")
	#print(parts)
	''' catches the special case of a two word noun'''
	if len(parts) == 1:
		parts[0] = parts[0].strip('\xa0')
		return parts
	if '\xa0' in parts[1]:
		parts[0] += ' ' + parts.pop(1)
		if len(parts) > 2:
			parts[1] += ' ' + parts.pop(2)
	#parts = parts[:2]
	return parts
# END DOUBLE NOUN


# MOVE GENDER
# # # # # # # # # # # # # # # 
def move_gender(parts,partOfSpeech):
	for index in range(len(parts)):
		# wiktionary entries contain special character 
		# between nominative and gender of nouns
		if '\xa0' in parts[index]:
			#print("\n\n\t\tACTIVE IF \xa0 >>>>>>>>>>>")
			# split nom into two or three parts
			word_plus_gdr = parts[index].split('\xa0')

			# reassign nom w/o gdr to 0 in parts
			parts[index] = word_plus_gdr[0]

			# and gender to the end of parts; don't do this for pronouns
			if partOfSpeech == 'noun':
				# add gender to end of parts
				parts.append(word_plus_gdr[1])

				# if two-part gender, 
				# add second part to gender already appended at end of parts
				if len(word_plus_gdr) == 3:
					parts[-1] += ' '
					parts[-1] += word_plus_gdr[-1]
		elif partOfSpeech == 'noun':
			#print("\n\n\t\tACTIVE ELIF >>>>>>>>>>>")
			#print(parts)
			offset = 0
			for i in range(len(parts)):
				i = i - offset
				letters = ['n','f','m','sg','pl','m or f']
				if parts[i] in letters:
					parts.append(parts.pop(i))
					offset += 1
			#print(parts)
	return parts
# END MOVE GENDER


# BUILD STRING
# # # # # # # # # # # # # # # # # 
def build_string(num_parts,comma_stop,parts,partOfSpeech,i_stem=False):
	''' Loop to build simple parts string '''
	simpleParts = ''
	for index in range(min(num_parts,len(parts))):
		# Last part of nouns should be gender in ()
		if partOfSpeech == 'noun' and index == num_parts-1:
			simpleParts += f"({parts[index]})"
		else:
			# append part to string
			simpleParts += parts[index]

		# rule for when to insert comma
		if index < num_parts - comma_stop:
			simpleParts += ', '
		else:
			# insert i-stem label if flagged
			if i_stem == True and index == num_parts - 2:
				simpleParts += ' -ium'
			# insert space w/o comma
			simpleParts += ' '

	return simpleParts

# END BUILD STRING


# GET SIMPLE LA 'LATIN'
# # # # # # # # # # # # # # # 
def get_simple(partOfSpeech,parts,heading):

	# Only works on noun, verb, adjective, pronoun, determiner
	# adverbs, conjunctions, interjections, etc. remain the same

	# in case proper noun or other subset of noun
	if partOfSpeech.lower() == 'proper noun':
		partOfSpeech = 'noun'

	# not a, b, or c then return
	if partOfSpeech not in ['noun','verb','adjective','participle','adverb','pronoun','determiner','numeral']:
		return parts

	# set some flags ['thid_decl', 'adjective_parts', 'deponent', 'defective', 'verb_label']
	flags = set_flags_la(parts,partOfSpeech)

	# if not comparable for adverb return parts
	if 'not comparable' in parts and partOfSpeech == 'adverb':
		return parts

	# Chop parts down to simple list
	parts = chop_parts(parts)

	# abort here len(part) == 1, (not a main entry)
	if len(parts) == 1 or partOfSpeech == 'adverb':
		return parts[0]

	# List of words to remove
	remove_words_la = ['present','infinitive','perfect','active',
	'future','participle','supine','genitive','feminine','neuter','irregular',
	'no','indeclinable','variously','declined','comparative','superlative'
	]

	# remove extra words not part of principal parts
	parts = remove_words(parts,remove_words_la)

	# Loop for perfect active form of deponent verbs
	parts = combine_deponent(parts)

	# Loop to combine part with __ or __
	parts = combine_or(parts)

	# for noun list should only contain nominative & genitive
	if partOfSpeech == 'noun':
		parts = double_noun(parts)

	# Loop to find gender, separate from nominative
	parts = move_gender(parts,partOfSpeech)

	# test for i-stem
	i_stem = i_stem_test(parts,heading,flags)

	# wrap up, create simpleParts string

	# add blanks for verbs without four principle parts
	if (partOfSpeech == 'verb' and not flags['deponent']) and len(parts) < 4 and flags['no_perfect']:
		parts.insert(2,"____")

	while (partOfSpeech == 'verb' and not flags['deponent']) and len(parts) < 4:
		parts.append("____")

	# Verbs and nouns all parts are used
	# adjectives are cutoff at 2 or 3
	if partOfSpeech in ['adjective','participle','numeral'] and not flags['indeclinable']:
		num_parts = flags['adjective_parts']
	else:
		num_parts = len(parts)

	# No comma between parts and gender for nouns
	if partOfSpeech == 'noun':
		comma_stop = 2
	else:
	# Comma between each part until last for non-noun
		comma_stop = 1

	simpleParts = build_string(num_parts,comma_stop,parts,partOfSpeech,i_stem)

	# add verb label label if any
	if flags['verb_label'] and partOfSpeech == 'verb':
		simpleParts += flags['verb_label']

	if flags['indeclinable']:
		simpleParts += '(indeclinable)'

	if flags['indeclinable portion']:
		simpleParts += '(indeclinable portion)'

	# return string
	
	'''	this 'i_stem_mode' return option was part of creating 
		the 'Latin-i_stem_nouns-trie.txt' file.
		Could probably be removed now.
	'''
	if i_stem_mode:
		if i_stem and partOfSpeech == 'noun':
			return simpleParts
		else:
			return False
	else:
		return simpleParts

# END GET SIMPLE 'LATIN'


# SET FLAGS 'LATIN'
# # # # # # # # # # # # # # # # # 
def set_flags_la(parts,partOfSpeech):

	flags = {}

	# flag one/two vs. three termination adjective
	if 'one-termination' in parts or 'two-termination' in parts or 'third declension' in parts:
		flags['adjective_parts'] = 2
	else:
		flags['adjective_parts'] = 3

	if 'comparative' in parts and 'superlative' in parts:
		flags['adjective_parts'] += 2

	# flag third declension noun for i-stem test
	if 'third declension' in parts and partOfSpeech == 'noun':
		flags['third_decl'] = True
	else:
		flags['third_decl'] = False

	# flag defective verb
	if 'highly defective' in parts and partOfSpeech == 'verb':
		flags['defective'] = 'highly defective'
	elif 'defective' in parts and partOfSpeech == 'verb':
		flags['defective'] = 'defective'
	elif 'perfect forms have present meaning' in parts and partOfSpeech == 'verb':
		flags['defective'] = 'perfect forms have present meaning'
	else: flags['defective'] = False

	if 'no perfect stem' in parts:
		flags['no_perfect'] = True
	else:
		flags['no_perfect'] = False

	# flag deponent verb
	if 'semi-deponent' in parts and partOfSpeech == 'verb':
		flags['deponent'] = 'semi-deponent'
	elif 'optionally deponent' in parts and partOfSpeech == 'verb':
		flags['deponent'] = 'optionally deponent'
	elif 'deponent' in parts and partOfSpeech == 'verb':
		flags['deponent'] = 'deponent'
	else:
		flags['deponent'] = False

	deponent = flags['deponent']
	defective = flags['defective']

	# combine labels into one
	if defective and deponent and deponent != 'deponent':
		flags['verb_label'] = f"({deponent}, {defective})"
	elif defective:
		flags['verb_label'] = f"({defective})"
	elif deponent and deponent != 'deponent':
		flags['verb_label'] = f"({deponent})"
	else:
		flags['verb_label'] = False

	if 'indeclinable portion' in parts:
		flags['indeclinable portion'] = True
	else:
		flags['indeclinable portion'] = False

	if 'indeclinable' in parts and not flags['indeclinable portion']:
		flags['indeclinable'] = True
	else:
		flags['indeclinable'] = False

	return flags
# END SET FLAGS 'LATIN'


# I-STEM TEST
# # # # # # # # # # # # # 
def i_stem_test(parts,heading,flags):
	''' this test requires the 'Latin-i_stem_nouns-trie.txt' starter file 
		or a previously parsed 'Latin-trie.txt' file in order to work
	'''
	if t is None: # key file missing
		return False

	if quickmode:
		if parts[0] in t and flags['third_decl']:
			return True
		else:
			return False
	else:
		''' test to determine if i'stem label is needed'''
		if flags['third_decl']:

			# chop 's' off genitive to get stem
			istem = parts[1][:-1]
			# add 'um' for gen plur (of i-stem)
			istem += 'um'
			# remove macrons
			istem = unidecode(istem)		
		else:
			return False

		# remove macrons for comparison
		handle = unidecode(heading)


		if istem in t:
			value = t[istem]
			if isinstance(value,list):
				entries_list = []
				for e in value:
					entries_list.extend(e['entries'])
			else:
				entries_list = value['entries']
			for entry in entries_list:
				for d in entry['senses']:
					compare = unidecode(d['gloss'])
					if 'genitive' in compare and handle in compare:
						#print(f"{parts[0]},{parts[1]} is i_stem")
						return True
		return False
# END I-STEM TEST

# Combine adjective parts
# # # # # # # # # # # # # # # # 
def combine_adjective_parts(parts):
	''' combine masculine and feminine for spanish adjectives '''
	offset = 0
	for number in range(1,len(parts)):
		index = number - offset
		if parts[index][-1] == 'a' and parts[index - 1][-1] == 'o':
			if parts[index][:-1] == parts[index - 1][:-1]:
				parts[index - 1] += "/-a"
				del parts[index]
				offset += 1
		elif parts[index][-2:] == 'as' and parts[index - 1][-2:] == 'os':
			if parts[index][:-2] == parts[index - 1][:-2]:
				parts[index - 1] += "/-as"
				del parts[index]
				offset += 1				
	return parts
# END COMBINE ADJECTIVE PARTS
