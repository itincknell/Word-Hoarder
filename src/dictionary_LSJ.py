
from load_dict import change_path, SUPPLEMENTARY_LANGUAGE_FILES
from perseus_xml_utilities import printpr, cut_text, translate_greek, smart_join, configure_parts, process_entry, get_def

progress_print = True


def LSJ(new_dictionary):
	''' function for parsing the Liddell-Scott-Jones files. 
		See readme for info on files.
	'''
	change_path(SUPPLEMENTARY_LANGUAGE_FILES)
	dictionary = {'file':'','definitions':[],"language":''}

	# 27 files total
	for i in range(1,28):

		try:
			with open('grc.lsj.perseus-eng' + str(i) + '.txt','r') as f:

				if progress_print:
					print(f"Parsing '{'grc.lsj.perseus-eng' + str(i) + '.txt:' + chr(39):<28}",end='',flush=True)

				# line list collects the lines the make up an entry for a single word
				# in this file words can be spread over multiple lines
				line_list = []

				# flag indicates when the start of a word may have been found
				ignition = False

				# used to print progress bar
				counter = 0

				for line in f.readlines():

					# indicates start of a definition
					if "<entryFree" in line:
						ignition = True

					# collect lines until end of definition
					if ignition:
						line_list.append(line.strip(" \n\t"))

					# close of entry, join lines and pass to process_entry
					if "</entryFree" in line and ignition:
						line_list.append(line.strip())
						line_list = "".join(line_list)
						dictionary['definitions'].append(process_entry(line_list,tag="LSJ"))
						ignition = False
						line_list = []

					counter += 1
					if progress_print:
						printpr(counter)

				print(f' {counter:,} lines parsed',flush=True)

		except FileNotFoundError:
			print(f"'{'grc.lsj.perseus-eng' + str(i) + '.txt'} not found in 'texts' directory")

	new_dictionary['definitions'].extend(dictionary['definitions'])
	return new_dictionary


