

from load_dict import change_path, SORTED_LANGUAGE_FILES
from unidecode import unidecode
import pickle
import datrie

def split_language(new_dictionary):
	'''	Take a list of definitions and converts it to a datrie.
		If multiple distinct definitions belong to the same node
		in the trie due to unidecoding to the same string, the 
		node will containt a list of definitions.
	'''

	# initialize trie
	alpha = 'abcdefghijklmnopqrstuvwxyz-'
	t = datrie.Trie(alpha)

	for i in range(len(new_dictionary['definitions'])):
		try:
			# key is the unidecode string of the entry heading
			key = unidecode(new_dictionary['definitions'][i]['heading']).lower()

			# if key is free to use
			if key not in t:
				t[key] = new_dictionary['definitions'][i]

			# if key is already used
			else:
				# if a list is already started
				if isinstance(t[key],list):
					t[key].append(new_dictionary['definitions'][i])

				# otherwise start a list with [previous item, new item]
				else:
					t[key] = [t[key],new_dictionary['definitions'][i]]

		except KeyError:
			print(f"{new_dictionary['definitions'][i]} could not be added")

	# rename new_dictionary file and replace list with trie
	new_dictionary['file'] = new_dictionary['language'].replace(' ','') + "-trie.txt"
	new_dictionary['definitions'] = t

	# save to sorted files directory
	change_path(SORTED_LANGUAGE_FILES)
	with open(new_dictionary['file'],mode = 'wb') as openFile:
		pickle.dump(new_dictionary, openFile,protocol=pickle.HIGHEST_PROTOCOL)

	return
