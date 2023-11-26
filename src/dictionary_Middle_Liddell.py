
from load_dict import change_path, SUPPLEMENTARY_LANGUAGE_FILES
from language_splitter import split_language
from perseus_xml_utilities import printpr, cut_text, translate_greek, smart_join, configure_parts, process_entry, get_def

progress_print = True


def middle_liddell(new_dictionary):
	'''	Function for parsing the Middle Liddell xml file.
		See readme for more information about the file.
	'''

	change_path(SUPPLEMENTARY_LANGUAGE_FILES)

	dictionary = {'file':'','definitions':[],"language":''}

	try:
		with open('Perseus_text_1999.04.0058.txt','r') as f:
			if progress_print:
				print(f"Parsing 'Perseus_text_1999.04.0058.txt': ",flush=True,end='')

			# line list collects the lines the make up an entry for a single word
			# in this file words can be spread over multiple lines
			line_list = []

			# flag indicates when the start of a word may have been found
			ignition = False

			# used to print progress bar
			counter = 0


			for line in f.readlines():

				# indicates start of a definition
				if "<entry" in line:
					ignition = True

				# collect lines until end of definition
				if ignition:
					line_list.append(line.strip(" \n\t"))

				# close of entry, join lines and pass to process_entry
				if "</entry" in line and ignition:
					line_list.append(line.strip())
					line_list = "".join(line_list)
					dictionary['definitions'].append(process_entry(line_list,tag="Middle Liddell"))
					ignition = False
					line_list = []

				counter += 1
				if progress_print:
					printpr(counter)

			print(f' {counter:,} lines parsed',flush=True)
		
	except FileNotFoundError:
		print("'Perseus_text_1999.04.0058.txt' not found in 'texts' directory")
		input("Enter to continue")

	new_dictionary['definitions'].extend(dictionary['definitions'])
	return new_dictionary




