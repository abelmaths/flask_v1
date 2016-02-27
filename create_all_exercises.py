"""
Summary
---------
Code collection to take collection of csvs and upload to database

Detail
---------
For each exercise:
	Load all levels from csvs
	For each level, create a hash
	See if already exists in database, upload as new entry if not
	Create exercise as a list of levels
	If exercise is different from everything in DB currently, upload exercise
	Note we may have multiple versions of same exercise
	When a homework is set, it links to a particular version of an exercise
"""

################################ IMPORTS ###########################################
from pprint import pformat
from hashlib import sha1
import csv, os, datetime, re, collections, json
import mongo as mong


################################ FUNCTIONS ###########################################
def write_structure_to_file(filename, variable_name, dictionary):
	"""
	Write python dict to a file (used in level tester implementation, not to save to DB)
	"""
	f = open(filename, 'w')
	f.write('{} = {}'.format(variable_name, str(dictionary)))
	f.close()

def create_skeleton_fields(filename):
	"""
	Fill skeleton fields of a dictionary with a csv
	"""
	output = {}
	with open(filename, 'rU') as csvfile:
	    R = csv.reader(csvfile)
	    for row in R:
	    	Key = row[0]
	    	Value = row[1]
	    	# Make sure every value is part of a list, even if one item
	    	if Key in output:
	    		output[Key].append(Value)
	    	else:
	    		output[Key] = [Value]
	return output

def create_variable_list(filename):
	"""
	Create a list of dicts, each with variables and answers in
	This is ultimately one part of the generator dictionary (one value)
	"""
	list_of_dicts = []
	with open(filename, 'rU') as csvfile:
	    R = csv.reader(csvfile)
	    counter = 0
	    # Each row is a question (except first row)
	    for row in R:
	    	# First row is headings
	    	if counter==0:
	    		heading = row
	    	# Non first row is actual answers
	    	else:
	    		# Put together a dict for this question
	    		dict_of_vars = {}
	    		i = 0
	    		for value in row:
	    			variable_name = heading[i]
	    			# If wrong answer field, we want to create a mini-dict for wrong answers
	    			if 'wrong' in variable_name:
	    				wrong_var_title = variable_name[0:-3]
	    				if wrong_var_title not in dict_of_vars:
	    					dict_of_vars[wrong_var_title] = {}
	    				dict_of_vars[wrong_var_title][value] = variable_name
	    			# Else we add the value to the dict of variables under the correct name
	    			else:
	    				dict_of_vars[variable_name] = value
	    			i += 1
	    		list_of_dicts.append(dict_of_vars)
	    	counter+=1
	return list_of_dicts

def create_level_dict(level_number):
	"""
	Return a dictionary for a level
	"""
	level_dict = create_skeleton_fields('skeletons_{}.csv'.format(level_number))
	level_dict['variables'] = create_variable_list('variables_{}.csv'.format(level_number))
	return level_dict

def create_list_of_levels(dir_path):
	"""
	Trawl a directory and collect list of level numbers, ordered
	Only return those that appear in a list and a skeleton
	"""
	filenames = os.listdir(dir_path)
	skeletons_found, variables_found = [], []
	for f in filenames:
		skeleton_match = re.match(r'skeletons_(\d+)\.csv', f)
		if skeleton_match:
			skeletons_found.append(skeleton_match.group(1))
		variables_match = re.match(r'variables_(\d+)\.csv', f)
		if variables_match:
			variables_found.append(variables_match.group(1))
	
	# Check if any skeletons or variables exist without their partner
	S_multiset = collections.Counter(skeletons_found)
	V_multiset = collections.Counter(variables_found)
	overlap = list((S_multiset & V_multiset).elements())
	S_remainder = list((S_multiset - V_multiset).elements())
	V_remainder = list((V_multiset - S_multiset).elements())
	if S_remainder:
		print "Warning: Missing the following variables: {}".format(S_remainder)
	if V_remainder:
		print "Warning: Missing the following skeletons: {}".format(V_remainder)

	# Return the overlapping level numbers
	return sorted(list(set(overlap)))

def generate_hash(structure):
	"""
	Generate a sha1 hash of a structure
	Note that pformat sorts the level
	"""
	return str(sha1(pformat(structure)).hexdigest())

def save_hash_and_dict_to_database(_dict, _hash, db_name):
	# Check if exists, upload if not
	collection = mong.db[db_name]
	already_exists = collection.find({"hash": _hash}).count()  # either 0 or 1
	if not already_exists:
		print "Dict appears to be new or modified, uploading new version"
		collection.insert({
			'hash':_hash,
			'dict':_dict,
			'upload_time':datetime.datetime.now()
			}, check_keys=False)
		# TODO: should use insert_one
		# but in this case can't do check_keys = False
		# Not allowed '.' in key, so 2.9 : ans_1_wrong not allowed for wrong answers
		# Need to convert to array of tuples and change logic on exercise html page when checking wrong answers
	else:
		print "Entry found with hash {} - not uploading new version".format(_hash)

def create_exercise(exercise_name):
	"""
	Saves exercise and levels to database,
	creating a new version if any different to existing
	"""
	# Shift directory
	os.chdir('exercises/{}'.format(exercise_name))

	# Create new exercise dictionary
	exercise_dict = {
		'exercise_name_unique':'Error - information missing',
		'exercise_title_visible':'Error - information missing',
		'exercise_description_visible':'Error - information missing',
		'question_attempts_required':'15',
		'level_ids':[]
	}

	# Open up metadata and fill in for the exercise
	with open('exercise_info.csv', 'rU') as csvfile:  # TODO, navigate to correct directory
	    R = csv.reader(csvfile)
	    for row in R:
	    	Key = row[0]
	    	Value = row[1]
	    	exercise_dict[Key] = Value
	
	# Generate the question numbers to loop through
	level_list = create_list_of_levels('.')
	
	# Create each level locally, hash it, save within the new exercise dictionary
	for level_number in level_list:
		level_dict = create_level_dict(level_number)
		level_hash = generate_hash(level_dict)
		exercise_dict['level_ids'].append(level_hash)
		save_hash_and_dict_to_database(_dict = level_dict, _hash = level_hash, db_name='levels')

	# Create exercise hash, upload it if hash doesn't exist
	exercise_hash = generate_hash(exercise_dict)
	save_hash_and_dict_to_database(_dict = exercise_dict, _hash = exercise_hash, db_name='exercises')

	# Shift directory back again
	os.chdir('..')
	os.chdir('..')

def create_all_exercises():
	"""
	Loop through folder structure and create an exercise for everything
	"""
	exercise_folders = os.listdir('exercises')
	for name in exercise_folders:
		if name[0] != '.':  #hidden files:
			print "Creating exercise '{}'".format(name)
			create_exercise(name)

def delete_all_exercises():
	y = raw_input("Are you sure you wish to delete all exercises? Type 'y' to continue: ")
	if y != 'y':
		print "Cancelling - not deleting anything."
		return 0
	mong.db['exercises'].remove()
	print "Deleted!"

def delete_all_levels():
	y = raw_input("Are you sure you wish to delete all levels? Type 'y' to continue: ")
	if y != 'y':
		print "Cancelling - not deleting anything."
		return 0
	mong.db['levels'].remove()
	print "Deleted!"

################################ CREATE ALL EXERCISES ###########################################

if __name__ == '__main__':
	if True:
		delete_all_exercises()
		delete_all_levels()
	create_all_exercises()
	
	
	