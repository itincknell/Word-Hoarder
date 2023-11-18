


from load_dict import change_path
from copy import deepcopy
import edit_all
import pickle

from dict_utilities import printpr

interval = 30
level = 1
start = interval * level
stop = (interval) * (level + 1)

debug_print = False
progress_print = True

# From here on this is the most contrived code ever written

tenses = ['pres','past','ptp']
genders = ['m','f','n','pl','?']
numbers = [f'{i + 1}.' for i in range(30)]
other_pos = {'adj':'adjective',
			'noun':'noun',
			'pronoun':'pronoun',
			'prep':'preposition',
			'conj':'conjuction',
			'interrog. adv':'interrogative',
			'interrog':'interrogative',
			'adv':'adverb',
			'prefix':'prefix',
			'interj':'interjection',
			'pron':'pronoun',
			'suffix':'suffix',
			'num':'number',
			'article':'article',
			'infl':'inlfection',
			'indecl':'indecllinable noun'}

def Johnson_OED(new_dictionary):

	def pos_test(line,line_0 = ''):
		if debug_print:
			print(f"TEST LINE: {line}")

		index = None
		if 'ptp' in line:
			full_verb = True
			for n in numbers:
				if n in line:
					if line.index(n) < line.index('ptp'):
						full_verb = False
		else:
			full_verb = False

		if full_verb:
			entry = {'partOfSpeech':'verb','etymology':''}
			index = line.index('ptp')+2
			parts = line_0 + ' '.join(line[:index]).strip(',.;')
			entry['simpleParts'] = entry['principleParts'] = parts

			if debug_print:
				print('\n>>>>> FULL VERB')
			return entry, index

		else:
			if debug_print:
				print('NOT FV',end='\t')

			see = False
			for word in line:
				if word == 'see':
					see = True
					break
				if word.strip('.,') in other_pos \
					or word in numbers \
					or word.strip(',.') in genders:
					break

			if see:
				index = line.index('see')
				entry = {'partOfSpeech':'form','etymology':''}
				entry['simpleParts'] = entry['principleParts'] = line_0 + ' '.join(line[:index]).strip(',.;')
				entry['defs'] = [{'gloss':'alternative form of ' + ' '.join(line[index+1:]).strip(',.;'),'tags':[]}]
				new_word['entries'] = entry

				if debug_print:
					print('\n>>>>> FORM OF')
				return entry, index

			if debug_print:
				print('NOT FORM',end='\t')

			noun = flag = stop = False
			for i in range(len(line)):
				if line[i].strip(".,") in genders and not stop:
					noun = flag = True
					index = i + 1
					continue
				elif noun and not flag:
					stop = True
				if flag:
					if '(' in line[i]:
						if ')' in line[i]:
							index = i + 1
							flag = False
						else:
							continue
					else:
						flag = False
					if ')' in line[i]:
						index = i + 1
						flag = False
				if line[i] in numbers:
					break

			if noun:
				entry = {'partOfSpeech':'noun','etymology':''}
				parts = line_0 + ' '.join(line[:index]).strip(',.;')
				entry['simpleParts'] = entry['principleParts'] = parts
				if debug_print:
					print('\n>>>>> NOUN')
				return entry,index

			if debug_print:
				print('NOT NOUN',end='\t')

			found_pos = False
			for i in range(len(line)):
				if line[i].strip('.,') in other_pos:
					index = i
					pos = other_pos[line[i].strip('.,')]
					found_pos = True
					break
				if line[i] in numbers:
					break

			if found_pos:
				entry = {'partOfSpeech':pos,'etymology':''}
				if pos == 'noun' or pos == 'pronoun':
					if debug_print:
						print('%'*1000)
					if debug_print:
						print(line)
					flag = suspicious =  False
					og_index = index
					for i in range(index,len(line)):
						if line[i].strip('(,.') in genders:
							if '(' in line[i]:
								flag = True
							else:
								index = i + 1
						if flag:
							if ')' in line[i]:
								flag = False
								index = i + 1	
						if line[i].strip(',.') in ['suffix','prefix']:
							entry['partOfSpeech'] = line[i].strip(',.')	
						if line[i].strip(',.') in other_pos:
							suspicious = True
						if line[i].strip(',.') == 'or' and suspicious:
							entry['partOfSpeech'] = ''
							index = 1

					if entry['partOfSpeech'] == 'noun' and index > og_index:
						parts = ' '.join(line[:index])
						entry['simpleParts'] = entry['principleParts'] = parts

				if entry['partOfSpeech'] == 'suffix' or entry['partOfSpeech'] == 'prefix' :
					entry['simpleParts'] = entry['principleParts'] = line[0]
					index = 1

				else:
					parts = line_0 + ' '.join(line[:index]).strip(',.;')
					entry['simpleParts'] = entry['principleParts'] = parts
					index += 1
				if debug_print:
					print('\n>>>>> OTHER POS')
				return entry, index
			if debug_print:
				print('POS NOT FOUND',end='\t')

			form = False
			for i in range(len(line)):
				if line[i] == 'of':
					form = True
				if line[i].strip('.,') in other_pos \
					or line[i] in numbers \
					or line[i].strip(',.') in genders:
					form = False
					break
			if form:
				entry = {'partOfSpeech':'form','etymology':''}
				entry['simpleParts'] = entry['principleParts'] = line_0
				index = 0
				return entry, index
				prin("")
		return None, None

	def return_defs(line,index):
		sub_nums = []
		for i in range(len(numbers)):
			if numbers[i] in line[index:]:
				sub_nums.append(numbers[i])
		defs = []
		if debug_print:
			print(line)
		for i in range(len(sub_nums)):
			start = line.index(sub_nums[i]) + 1
			if sub_nums[i] == sub_nums[-1]:
				stop = None
			else:
				stop = line.index(sub_nums[i+1])
			if stop:
				defs.append({'gloss':' '.join(line[start:stop]).strip(',.;'),'tags':[]})
			else:
				defs.append({'gloss':' '.join(line[start:]).strip(',.;'),'tags':[]})
		return defs

	def return_multi_entry(line):
		
		sub_nums = []
		for i in range(len(numbers)):
			if numbers[i] in line:
				sub_nums.append(numbers[i])
				
		entries	= []
		if debug_print:
			print(sub_nums)
		for i in range(len(sub_nums)):
			if debug_print:
				print(sub_nums[i])
			start = line.index(sub_nums[i]) + 1
			if sub_nums[i] == sub_nums[-1]:
				stop = None
			else:
				stop = line.index(sub_nums[i+1])
			if debug_print:
				print(line[start:stop])
			if stop:
				entry, index = pos_test(line[start:stop],line[0] + ' ')
			else:
				entry, index = pos_test(line[start:],line[0] + ' ')
			if entry == None or index == None:
				if debug_print:
					print("\t\tAAAAAAAA")
				entry = {'partOfSpeech':'','etymology':''}
				parts = ' '.join(line[:line.index('1.')]).strip(',.;')
				entry['simpleParts'] = entry['principleParts'] = parts
				if stop:
					entry['defs'] = [{'gloss':' '.join(line[start:stop]).strip(',.;'),'tags':[]}]
				else:
					entry['defs'] = [{'gloss':' '.join(line[start:]).strip(',.;'),'tags':[]}]
			else:
				if debug_print:
					print("\t\tBBBBBBBB")
				if stop:
					if 'defs' not in entry:
						entry['defs'] = [{'gloss':' '.join(line[start+index:stop]).strip(',.;'),'tags':[]}]
				else:
					if 'defs' not in entry:
						entry['defs'] = [{'gloss':' '.join(line[start+index:]).strip(',.;'),'tags':[]}]
			entries.append(deepcopy(entry))		
		return entries

	# Start of actual MLJohnson code
	# # # # # # # # # # # # # # # # 

	change_path('texts')

	definitions = []
	counter = 0
	line_counter = 0

	with open('MLJohnson_OEDictionary.txt','r') as f:
		if progress_print:
			print(f"Parsing 'MLJohnson_OEDictionary.txt': ",flush=True,end='')
	
		for line in f.readlines():
			line = line.split()

			if '[]' in line:
				line.remove('[]')

			offset = 0
			for i in range(len(line)):
				i = i - offset
				if len(line[i]) > 2:
					line[i] = line[i].rstrip('1234')
				if len(line[i]) > 1:
					line[i] = line[i].strip('?')
				if line[i].rstrip('1234') == '':
					del line[i]
					offset += 1
					i -= 1

				if line[i].strip('.') in other_pos and line[i-1].strip('.') == 'interrog':
					line[i-1] = 'interrog. adv.'
					del line[i]
					offset += 1

			if line:
				new_word = {}
				new_word['heading'] = new_word['handle'] = line[0]

				# PART OF SPEECH TESTS
				entry, index = pos_test(line)
				if debug_print:
					print(f'\nPOS TEST: {entry} {index}')

				if entry:
					if entry['partOfSpeech'] == 'suffix' or entry['partOfSpeech'] == 'prefix':
						for i in range(len(line)):
							if entry['partOfSpeech'] in line[i]:
								line[i] = line[i].strip(",.;") + ":"


				one_entry = True
				for n in numbers:
					if n in line:
						one_entry = False
					else:
						break
				if debug_print:
					print(f"ONE ENTRY = {one_entry}")

				if index == None and not one_entry:
					new_word['entries'] = return_multi_entry(line)
						
				elif index and not one_entry:
					entry['defs'] = return_defs(line,index)
					new_word['entries'] = [entry]

				elif index == None and one_entry:
					verb = False
					for i in range(len(line)):
						if '/' in line[i] or line[i] == 'verb':
							index = i + 1
							verb = True
					if verb:
						entry = {'partOfSpeech':'verb','etymology':''}
						parts = ' '.join(line[:index]).strip(',.;')
						entry['simpleParts'] = entry['principleParts'] = parts	


					elif 'of' in line:
						entry = {'partOfSpeech':'form','etymology':''}
						entry['simpleParts'] = entry['principleParts'] = line[0]
						index = 1
					elif index == None:
						entry = {'partOfSpeech':'','etymology':''}
						entry['simpleParts'] = entry['principleParts'] = line[0]
						index = 1
						counter += 1		
					entry['defs'] = [{'gloss':' '.join(line[index:]).strip(',.;'),'tags':[]}]
					new_word['entries'] = [entry]	
				else:
					if 'defs' not in entry:
						entry['defs'] = [{'gloss':' '.join(line[index:]).strip(',.;'),'tags':[]}]
					new_word['entries'] = [entry]
				new_word['tags'] = set('MLJ')
				if debug_print:
					print(f"\n\tFINAL WORD: {new_word}\n")
				if counter > 2:
					if debug_print:
						print("COUNTER EXCEEDED")
					break
				definitions.append(new_word)
			
			line_counter += 1
			if progress_print:
				printpr(line_counter)

		print(f' {line_counter:,} lines parsed',flush=True)


		new_dictionary['definitions'].extend(definitions)
		return new_dictionary







