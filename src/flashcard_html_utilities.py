'''
Fuctions used by tables.py to print flashcards with tables containing
verb conjugations and noun/adjective cases
'''


def set_styles(body_string):
	body_string += '<style type="text/css">\
	.tg  {border-collapse:collapse;border-spacing:0;}\
	.tg td{border-color:black;border-style:solid;border-width:1px;!important;font-size:xx-large;\
	  overflow:hidden;padding:10px 5px;word-break:normal;}\
	.tg th{border-color:black;border-style:solid;border-width:1px;!important;font-size:xx-large;\
	  font-weight:normal;overflow:hidden;padding:10px 5px;word-break:normal;}\
	.tg .tg-zp2n{!important;font-size:xx-large;text-align:left;vertical-align:top}</style>'
	return body_string

def create_style(body_string,width):
		if width == 2:
			body_string += f'<table class="tg" style="undefined;table-layout: fixed; width: 625px">\
			<colgroup><col style="width: 125px"><col style="width: 250px"><col style="width: 250px">'
		elif width == 1:
			body_string += f'<table class="tg" style="undefined;table-layout: fixed; width: 600px">\
			<colgroup><col style="width: 300px"><col style="width: 300px">'
		body_string += '</colgroup>'
		return body_string

def create_header(body_string,parts,header=''):
	body_string += f'<thead><tr><th class="tg-0lax">{header}</th>'
	column_labels = parts[list(parts.keys())[0]]
	for label in column_labels:
		body_string += f'<th class="tg-0lax">{label}</th>'
	body_string += "</tr></thead><tbody>"
	return body_string

def create_body(body_string,parts,t_type):
	for key in parts:
		body_string += '<tr>'
		if t_type == 'noun':
			body_string += f'<td class="tg-0lax">{key[:3]}.</td>'
		elif t_type == 'conj':
			body_string += f'<td class="tg-0lax">{key[:3]}</td>'
		else:
			body_string += f'<td class="tg-0lax">{key}</td>'
		if type(parts[key]) == dict:
			for row_item in parts[key]:
				body_string += f'<td class="tg-0lax">{parts[key][row_item]}</td>'
		else:
			body_string += f'<td class="tg-0lax">{parts[key]}</td>'
		body_string += '</tr>'
	body_string += '</tbody></table><br>'
	return body_string

def create_table(body_string,parts,t_type,width):
	body_string = create_style(body_string,width)
	body_string = create_header(body_string,parts)
	body_string = create_body(body_string,parts,t_type)

	return body_string

def create_box(body_string,label,content):
	body_string = create_style(body_string,1)
	body_string += f'<thead><tr><th class="tg-0lax">{label}</th>'
	body_string += f'<th class="tg-0lax">{content}</th>'
	body_string += '</tr></thead></table><br>'
	return body_string




