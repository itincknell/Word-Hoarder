
import pickle
from load_dict import change_path

change_path('dictionaries')
with open('new_dictionary_unjoined.txt','rb') as file:
	dictionary = pickle.load(file)

alpha = {}
for i in range(0,26):
	alpha[chr(i+97)] = 0
for i in range(len(dictionary['definitions'])):
	if dictionary['definitions'][i]['handle'][0].lower() in alpha:
		alpha[dictionary['definitions'][i]['handle'][0].lower()] = i

'''
prev = 0
counter = 0
for key in alpha:
	print(f"processing {key}s")
	for i in range(prev,alpha[key]):
		if dictionary['definitions'][i] in dictionary['definitions'][i + 1:i + 10]:
			dictionary['definitions'][i]['tags'].append('DUPE')
	prev = alpha[key]
	print(f"{key}s completed")

offset = 0
for i in range(len(dictionary['definitions'])):
	if "DUPE" in dictionary['definitions'][i - offset]['tags']:
		print(f"deleting {dictionary['definitions'][i - offset]['handle']}")
		del dictionary['definitions'][i - offset]
		offset += 1
'''	
prev = 0
counter = 0
comp = ''
for key in alpha:
	handles = []
	print(f"processing {key}s")
	for i in range(prev,alpha[key]):
		if comp == dictionary['definitions'][i]:
			continue
		else:
			comp = dictionary['definitions'][i]
		for j in range(1,len(dictionary['definitions'][i + 1:i+20])):
			if dictionary['definitions'][i + j]['handle'] == dictionary['definitions'][i]['handle']:
				print(f"i={i},j={j}; adding {dictionary['definitions'][i]['handle']} to {dictionary['definitions'][i + j]['handle']}")
				dictionary['definitions'][i]['entries'].extend(dictionary['definitions'][i + j]['entries'])
				dictionary['definitions'][i]['roots'].extend(dictionary['definitions'][i + j]['roots'])
				dictionary['definitions'][i + j]['tags'].append('DUPE')
	prev = alpha[key]
	print(f"{key}s completed")

offset = 0
for i in range(len(dictionary['definitions'])):
	if "DUPE" in dictionary['definitions'][i - offset]['tags']:
		print(f"deleting {dictionary['definitions'][i - offset]['handle']}")
		del dictionary['definitions'][i - offset]
		offset += 1


with open(dictionary['file'],mode = 'wb') as openFile:
	pickle.dump(dictionary, openFile)
