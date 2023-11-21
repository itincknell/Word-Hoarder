

from load_dict import change_path
from unidecode import unidecode
import pickle
import datrie

def split_language(new_dictionary):

	alpha = 'abcdefghijklmnopqrstuvwxyz-'

	t = datrie.Trie(alpha)
	#counter = 0
	for i in range(len(new_dictionary['definitions'])):
		if any(entry['simpleParts'] != False for entry in new_dictionary['definitions'][i]['entries']):
			#counter += 1
			try:
				key = unidecode(new_dictionary['definitions'][i]['heading']).lower()
				if key not in t:
					t[key] = new_dictionary['definitions'][i]
				else:
					if isinstance(t[key],list):
						t[key].append(new_dictionary['definitions'][i])
					else:
						t[key] = [t[key],new_dictionary['definitions'][i]]

			except KeyError:
				print(f"{new_dictionary['definitions'][i]} could not be added")
	#print(counter)
	#if counter == 0:
	#	return
	new_dictionary['file'] = new_dictionary['language'].replace(' ','') + "-trie.txt"
	new_dictionary['definitions'] = t
	change_path("dumps_sorted")
	with open(new_dictionary['file'],mode = 'wb') as openFile:
		pickle.dump(new_dictionary, openFile,protocol=pickle.HIGHEST_PROTOCOL)

	return
