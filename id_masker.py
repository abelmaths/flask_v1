def id_mask(input_string, method='encrypt'):
	"""
	Add 1 to all numbers
	"""
	encoder = {
		'0':'2',
		'1':'4',
		'2':'6',
		'3':'8',
		'4':'0',
		'5':'1',
		'6':'3',
		'7':'5',
		'8':'7',
		'9':'9'
	}
	decoder = {
		'2':'0',
		'4':'1',
		'6':'2',
		'8':'3',
		'0':'4',
		'1':'5',
		'3':'6',
		'5':'7',
		'7':'8',
		'9':'9'
	}
	output_string = ''
	for char in input_string:
		if char.isdigit():
			if method == 'encrypt':
				output_string += encoder[char]
			else:
				output_string += decoder[char]
		else:
			output_string += char
	return output_string