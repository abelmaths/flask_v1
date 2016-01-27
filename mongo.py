"""
Todo:

* Create functions to do the following (will often need to update multiple fields):
	- create a new pupil [DONE]
	- assign an exercise to a class [DONE]
	- create a new classroom [DONE]
	- add pupil to a classroom [DONE]
	- pupil submit an answer to a question [DONE]
	- view all homeworks for a pupil with appropraite details
	- view all homeworks for a class with appropraite details
	- view all homeworks for a teacher with appropraite details
* Make the demo script realistic:
	--create 10 pupils
	--create 2 teachers
	--make teachers create 2 classes 
	--pupils add themselves to classes
	--teachers create exercises
	--pupils submit answers to questions
* Make variable names consistent

Let the exercise/level/question class take care of writing to DB what the level score is at the end of each level
When you come back to the homework after a break, it should be able to load the last state from the DB

"""

# Load the general setup gump
from mongo_setup import *
#from mongo_general import *
run_demo = False


#################### CLASSES ####################

class User:
	def __init__(self, D):
		self.D = D

	def __str__(self):
		return """
		\nName: {} \nClasses: {} \nHomeworks: {}
		""".format(self.D.get('display_name'), str(self.D.get('classrooms')), str(self.D.get('homeworks')))

	def get_id(self, to_string=True):
		if to_string:
			return str(self.D.get('_id'))
		else:
			return ObjectId(self.D.get('_id'))

	def exists(self):
		"""
		Returns true if any data exists within this user
		"""
		if self.D:
			return True
		else:
			return False

	def set_surname(self, new_name):	
		"""
		Change the surname. Note this doesn't affect display name.
		"""	
		self.D['surname'] = new_name

	def set_display_name(self, new_name):
		"""
		Teacher can choose their display name
		"""
		if self.D.get('is_teacher'):
			self.D['display_name'] = new_name
		else:
			self.D['display_name'] = '{} {}'.format(self.D.get('first_name'), self.D.get('surname'))

	def get_display_name(self):
		"""
		Return the display name (full name for pupils, Title Surname for teachers)
		"""
		return self.D.get('display_name')

	def check_password(self, password_attempt):
		"""
		Return true if attempt matches known password
		"""
		from werkzeug.security import check_password_hash
		from werkzeug.security import generate_password_hash
		known_password_hash = self.D.get('password_hash')
		return check_password_hash(str(known_password_hash), str(password_attempt))

	def is_teacher(self):
		"""
		Returns if user is a teacher
		"""
		return self.D.get('is_teacher')

	def add_classroom(self, classroom):
		"""
		Given a classroom object, add basic info to classrooms array
		"""
		self.D['classrooms'].append(classroom.get_basic_info())

	def add_homework(self, homework):
		"""
		Given a homework object, add basic info to the homework array
		We actually need this to be nested in another dict in this case, so tranform done here
		"""
		#if not self.D.get('is_teacher'):
		if not self.is_teacher():
			H = homework.get_basic_info()

			# We now have a dict, but we want to pull the ID outside of it
			_id = str(H['_id'])
			self.D['homeworks'][_id] = H  # now we have inserted the dictionary

			# Add a few more fields
			self.D['homeworks'][_id]['started'] = False
			self.D['homeworks'][_id]['completed'] = False
			self.D['homeworks'][_id]['correct_count'] = 0
			self.D['homeworks'][_id]['incorrect_count'] = 0	
			self.D['homeworks'][_id]['answer_log'] = []	
			self.D['homeworks'][_id]['level_scores'] = {}
			for level_hash in homework.get_level_hashes():
				self.D['homeworks'][_id]['level_scores'][level_hash] = {'correct_count':0, 'incorrect_count':0, 'completed':False}		

	def start_homework(self, homework):
		"""
		User starts the homework
		"""
		homework_id = homework.get_id()
		self.D['homeworks'][homework_id]['started'] = True

	def complete_homework(self, homework):
		"""
		User completes homework
		"""
		homework_id = homework.get_id()
		self.D['homeworks'][homework_id]['completed'] = True

	def increment_homework(self, homework, answer_data):
		"""
		User submits an answer
		answer_data = {
			'exercise_complete':False,
			'exercise_correct_count':2,
			'exercise_incorrect_count':0,
			'level_complete':True,
			'level_correct_count':2,
			'level_incorrect_count':0,
			'level':'01',
			'question':'02',
			'display_format':'question',			
			'answers_recorded':{'ans1':21},
			'is_correct':True,	
			'hint':False,
		}
		"""
		homework_id = homework.get_id()
		self.D['homeworks'][homework_id]['started'] = True
		self.D['homeworks'][homework_id]['completed'] = answer_data['exercise_complete']		
		self.D['homeworks'][homework_id]['correct_count'] = answer_data['exercise_correct_count']
		self.D['homeworks'][homework_id]['incorrect_count'] = answer_data['exercise_incorrect_count']
		self.D['homeworks'][homework_id]['answer_log'].append(
				{
					'time':time.time(),
					'level':answer_data['level'],
					'question':answer_data['question'],
					'display_format':answer_data['display_format'],
					'is_correct':answer_data['is_correct'],
					'answers_recorded':answer_data['answers_recorded'],
					'hint':answer_data['hint']
				}
			)
		self.D['homeworks'][homework_id]['level_scores'][answer_data['level']]['correct_count'] = answer_data['level_correct_count']
		self.D['homeworks'][homework_id]['level_scores'][answer_data['level']]['incorrect_count'] = answer_data['level_incorrect_count']
		self.D['homeworks'][homework_id]['level_scores'][answer_data['level']]['completed'] = answer_data['level_complete']

	def save_to_session(self):
		"""
		Returns all info that is to be saved on the session cookie
		"""
		try:
			keys = ['display_name', '_id', 'is_teacher', 'first_name', 'surname', 'username']
			# Need to make the _id a string
			return {k : self.D[k] if k!='_id' else str(self.D[k]) for k in keys}		
		except:
			print "NO USER EXISTS"
			return {}

	def get_basic_info(self):
		"""
		Return basic info from object as a dict (to save within other collections)
		"""
		keys = ['display_name', '_id']
		return {k : self.D[k] for k in keys if k in self.D}		

	def get_all_info(self):
		"""
		Return all info from object as a dict (in order to save back to mongodb)
		"""
		return self.D

	def print_to_console(self):
		print "USER:"
		for k in self.D:
			print '  {} ==> {}'.format(k, self.D[k])


class Homework:
	def __init__(self, D):
		self.D = D

	def get_id(self, to_string=True):
		if to_string:
			return str(self.D.get('_id'))
		else:
			return ObjectId(self.D.get('_id'))

	def get_pupils(self):
		"""
		Return all of the pupils along with their progress etc.
		"""
		return self.D.get('pupils')

	def get_level_hashes(self):
		return self.D.get('level_hash_list')

	def add_pupils(self, pupil_list, level_hashes):
		"""
		Given a list of pupil-dicts each with name and ID
		Make into a dict of dicts with ID as key
		"""		
		for P in pupil_list:
			pupil_id = str(P['_id'])
			self.D['pupils'][pupil_id] = {
				'display_name':P['display_name'],
				'started':False,
				'completed':False,
				'correct_count':0,
				'incorrect_count':0,
				'level_scores':{x:{'correct_count':0, 'incorrect_count':0, 'completed':False} for x in level_hashes}
			}
		self.D['pupils_set_count'] = len(pupil_list)

	def set_date_due(self, date_due):
		"""
		Change the due date
		"""
		self.D['date_due'] = date_due

	def increment_homework(self, pupil_object, answer_data):
		"""
		Increment homework as a pupil answers a question
		answer_data = {
			'exercise_complete':False,
			'exercise_correct_count':2,
			'exercise_incorrect_count':0,
			'level_complete':True,
			'level_correct_count':2,
			'level_incorrect_count':0,
			'level':'01',
			'question':'02',
			'display_format':'question',			
			'answers_recorded':{'ans1':21},
			'is_correct':True,	
			'hint':False,
		}
		"""
		pupil_id = pupil_object.get_id()
		self.D['pupils'][pupil_id]['started'] = True
		self.D['pupils'][pupil_id]['completed'] = answer_data['exercise_complete']
		self.D['pupils'][pupil_id]['correct_count'] = answer_data['exercise_correct_count']
		self.D['pupils'][pupil_id]['incorrect_count'] = answer_data['exercise_incorrect_count']
		self.D['pupils'][pupil_id]['level_scores'][answer_data['level']]['correct_count'] = answer_data['level_correct_count']
		self.D['pupils'][pupil_id]['level_scores'][answer_data['level']]['incorrect_count'] = answer_data['level_incorrect_count']
		self.D['pupils'][pupil_id]['level_scores'][answer_data['level']]['completed'] = answer_data['level_complete']

		# Finally, update the counts of pupils having started the homework and completed it
		self.D['pupils_started_count'] = sum([self.D['pupils'][_id]['started'] for _id in self.D['pupils']])
		self.D['pupils_completed_count'] = sum([self.D['pupils'][_id]['completed'] for _id in self.D['pupils']])

	def get_exercise_name_unique(self):
		return self.D.get('exercise_name_unique')

	def get_exercise_description_visible(self):
		return self.D.get('exercise_description_visible')

	def get_exercise_title_visible(self):
		return self.D.get('exercise_title_visible')

	def get_date_due(self):
		return self.D.get('date_due')

	def get_date_set(self):
		return self.D.get('date_set')

	def get_classroom_name(self):
		return self.D.get('classroom_name')

	def get_question_attempts_required(self):
		return self.D.get('question_attempts_required')	

	def get_status_count(self):
		"""
		Get count of each status
		"""
		status_counts = {
			'complete':0,
			'in_progress':0,
			'not_started':0
		}
		# Get a list of all statuses
		# [{u'status': u'not_started'},
		#  {u'status': u'completed'},
		#  {u'status': u'not_started'},
		#  {u'status': u'not_started'},
		#  {u'status': u'in_progress'}]
		cursor = db['submissions'].find(
			{'homework_id':self.get_id(to_string=True)},
			{ '_id':0, 'status':1}  # returns only 'status'
			)
		status_list = [x for x in cursor]
		for d in status_list:
			status = d['status']
			status_counts[status] += 1
		return status_counts

	def get_basic_info(self):
		"""
		Return basic info from object as a dict (to save within other collections)
		"""
		keys = ['exercise_name', 'exercise_hash', 'teacher_name', 'classroom_name', '_id']
		return {k : self.D[k] for k in keys if k in self.D}			

	def get_all_info(self):
		"""
		Return all info from object as a dict (in order to save back to mongodb)
		"""
		return self.D


class Exercise:
	def __init__(self, D):
		self.D = D

	def get_id(self, to_string=True):
		if to_string:
			return str(self.D.get('_id'))
		else:
			return ObjectId(self.D.get('_id'))

	def get_exercise_hash(self):
		return self.D.get('hash')

	def get_exercise_name_unique(self):
		return self.D['dict'].get('exercise_name_unique')

	def get_exercise_title_visible(self):
		return self.D['dict'].get('exercise_title_visible')		

	def get_exercise_description_visible(self):
		return self.D['dict'].get('exercise_description_visible')

	def get_question_attempts_required(self):
		return self.D['dict'].get('question_attempts_required')

	def get_level_hashes(self):
		"""
		Return a list of string hashes for levels
		"""
		# Might need to convert to 01, 02 etc.?
		return self.D['dict'].get('level_ids')

	# def become_latest_exercise(self, exercise_name):
	# 	"""
	# 	Load up the latest modified version of an exercise for a given name
	# 	"""
	# 	# Create exercise object. Find latest hashed version of the exercise.
	# 	self.D = db.exercises.find(
	# 			{'exercise_name':exercise_name}
	# 		).sort(
	# 			[('date_modified', -1)] 
	# 		).limit(1)[0]					

	def get_all_info(self):
		"""
		Return all info from object as a dict (in order to save back to mongodb)
		"""
		return self.D



class Classroom:
	def __init__(self, D):
		self.D = D

	def get_id(self, to_string=True):
		if to_string:
			return str(self.D.get('_id'))
		else:
			return ObjectId(self.D.get('_id'))

	def set_entry_code(self, size=5, chars=string.ascii_uppercase):
		entry_code = ''.join(random.choice(chars) for _ in range(size))
		self.D['entry_code'] = entry_code

	def get_entry_code(self):
		return self.D.get('entry_code')

	def add_pupils(self, pupil_list):
		"""
		Given a list of pupil objects
		Adds them to the list
		"""
		for pupil in pupil_list:
			self.add_pupil(pupil)

	def add_pupil(self, pupil):
		"""
		Given a pupil object, adds basic info to the pupil list
		Name, full name, id... (see User.get_basic_info)
		"""
		self.D['pupils'].append(pupil.get_basic_info())

	def get_pupils(self):
		"""
		Return a list of all pupils in the classroom
		"""
		return self.D['pupils']

	def add_homework(self, homework):
		"""
		Given a homework object, adds basic info to the homework list
		"""
		self.D['homeworks'].append(homework.get_basic_info())

	def set_yeargroup_name(self, new_name):
		"""
		Set the yeargroup name to something new
		"""
		self.D['yeargroup_name'] = new_name
		self.update_classroom_name()

	def set_teacher_name(self, new_name):
		"""
		Set the teacher name to something new
		"""
		self.D['teacher_name'] = new_name
		self.update_classroom_name()

	def set_teacher_id(self, new_id):
		self.D['teacher_id'] = new_id

	def set_subject_name(self, new_name):
		"""
		Set the subject name to something new
		"""
		self.D['subject_name'] = new_name
		self.update_classroom_name()

	def update_classroom_name(self):
		"""
		If a class changes year or teacher changes name, regenerate the classroom's name
		"""
		classroom_name = '{yeargroup_name} - {subject_name} - {teacher_name}'.format(
			yeargroup_name = self.D.get('yeargroup_name'), # Might be class name or year name
			subject_name = self.D.get('subject_name'),
			teacher_name = self.D.get('teacher_name')
		)
		self.D['classroom_name'] = classroom_name

	def get_classroom_name(self):
		"""
		Return classroom name
		"""
		return self.D.get('classroom_name')

	def get_latest_set_and_next_due_homeworks(self):
		"""
		Query homeworks to find the next due and latest set
		"""
		# cursor = db['homeworks'].find({
		# 	{'classroom_id':self.get_id(to_string=True)},
		# 	{ '_id':0, 'date_set':1, 'date_due':1, 'exercise_name':1}  # returns only 'date due' and 'exercise name'
		# 	})
		# homeworks = [x for x in cursor]
		#TODO pull out the latest homework set and the next homework due, and return these
		return "TODO"

	def get_number_of_pupils(self):
		"""
		Return the number of pupils in the class
		"""
		return len(self.D.get('pupils'))

	def get_basic_info(self):
		"""
		Return basic info from object as a dict (to save within other collections)
		"""
		keys = ['classroom_name', 'teacher_name', '_id']
		return {k : self.D[k] for k in keys if k in self.D}				

	def get_all_info(self):
		"""
		Return all info from object as a dict (in order to save back to mongodb)
		"""
		return self.D



#################### GENERIC FUNCTIONS ####################

def load_by_id(_id, collection_name):
	"""
	Given an object ID and a collection to load from
	Gets the object as a dict from mongo then converts to object
	Only works for a single object
	"""
	# Mapping collection name to appropriate class
	collection_to_class_map = Object_Type = {
			'classrooms':Classroom,
			'users':User,
			'homeworks':Homework,
			'exercises':Exercise,
			'submissions':Submission,
		}
	# Which collection to load from?
	collection = db[collection_name]
	# Load the object
	obj = collection.find_one({"_id": _id})
	Object_Class = collection_to_class_map[collection_name]
	return Object_Class(obj)

def load_by_username(username):
	"""
	Given a userid, gets the object as a dict from mongo then converts to object
	"""
	# Load the object
	obj = db['users'].find_one({"username": username})
	return User(obj)

def load_by_arbitrary(query_map, collection_name, multiple=False):
	"""
	Given arbitrary selection of keys and values to search
	And given a collection
	Gets the object as a dict from mongo then converts to object
	Only works for a single object
	"""
	# Mapping collection name to appropriate class
	collection_to_class_map = {
				'classrooms':Classroom,
				'users':User,
				'homeworks':Homework,
				'exercises':Exercise,
				'submissions':Submission,
			}
	if not multiple:
		# Which collection to load from?
		collection = db[collection_name]
		# Load the object
		obj = collection.find_one(query_map)
		Object_Class = collection_to_class_map[collection_name]
		return Object_Class(obj)
	if multiple:
		collection = db[collection_name]
		# Load the object
		cursor = collection.find(query_map)
		Object_Class = collection_to_class_map[collection_name]
		return [Object_Class(obj) for obj in cursor]


def save_object(the_object, collection_name):
	#TODO - alter so that we can save new ones or update old ones
	# Which collection to save to?
	collection = db[collection_name]
	_id = the_object.get_id(to_string=False)
	D = the_object.get_all_info()
	exists_already = collection.find({'_id':_id}).limit(1).count() # Should be 1 or 0
	assert exists_already == 1 or exists_already == 0, "Unexpected # records found"
	if exists_already:
		# Already exists, update
		_id = collection.update({'_id':_id}, D)	
		assert _id['ok'] == 1, "Update failed"
		print "Updated object in {} collection".format(collection_name)
	else:
		# Doesn't exist, create new
		_id = collection.insert_one(D)
		print "Added object into {} collection".format(collection_name)
	return _id

def view(collection):
	c = collection.find()
	for _ in c:
		pp.pprint(_)
		print

#################### SUBMISSIONS ####################

"""
A submission entry is created for every pupil when a homework is set
Unique by user and homework combination

Submission format:
{
	'_id':.......
	'user_id':...
	'homework_id':...
	'level_hash_list':[...,...,...]
	'status': (not_started | in_progress | complete)
	'progress_snapshot':[2, 4, 3, 5, 1, 0, [7,2,6,1,5,4,3,8]]
	--> current_level, current_question, correct_total, incorrect_total, correct_level, incorrect_level, question_order
	'1':[{'df':'question', 'hint':'hint', 'qu':1, 'score':0}, {{'df':'scaffold', 'hint':'no_hint', 'qu':2, 'score':0.5}]
	--> level answers (note - only filled out during first homework attempt, not during retries)
}
"""
class Submission:
	def __init__(self, D):
		self.D = D

	def __str__(self):
		return """
		\nuser: {} \nhomework: {} \nstatus: {}
		""".format(self.D.get('user_id'), str(self.D.get('homework_id')), str(self.D.get('status')))

	def create_empty_level_slots(self):
		"""
		Add a key for each level (just its index, not a hash)
		Blank list, but will eventually be filled with answers
		i.e. '1':[{'df':'question', 'hint':'hint', 'qu':1, 'score':0}, {{'df':'scaffold', 'hint':'no_hint', 'qu':2, 'score':0.5}]
		"""
		level_hash_list = self.get_level_hash_list()
		for i in range(len(level_hash_list)):
			self.D[str(i)] = []

	def get_id(self, to_string=True):
		if to_string:
			return str(self.D.get('_id'))
		else:
			return ObjectId(self.D.get('_id'))

	def get_status(self):
		return self.D.get('status')

	def get_status_display(self):
		"""
		Return display friendly version of the current status
		"""
		return {
			'not_started':'Not started',
			'in_progress':'In progress',
			'complete':'Completed'
		}[self.get_status()]

	def get_progress_snapshot(self):
		"""
		'progress_snapshot': [    0,
	                              3,
	                              u'question',
	                              2,
	                              0,
	                              2,
	                              0,
	                              2,
	                              [3, 5, 0, 6, 1, 7, 2, 4]],
	    FROM JS:
	    level_number = progress_snapshot[0]
		question_index = progress_snapshot[1]
		display_format = progress_snapshot[2]
		questions_correct_total_count = progress_snapshot[3]
		questions_incorrect_total_count = progress_snapshot[4]
		questions_correct_level_count = progress_snapshot[5]
		questions_incorrect_level_count = progress_snapshot[6]
		questions_attempted_count = progress_snapshot[7]
		question_order_array = progress_snapshot[8]
		"""
		return self.D.get('progress_snapshot')

	def get_level_hash_list(self):
		return self.D.get('level_hash_list')

	def get_homework_id(self):
		return self.D.get('homework_id')

	def get_href(self):
		return 'exercise/{}'.format(self.get_homework_id())

	def get_exercise_name_unique(self):
		return self.D.get('exercise_name_unique')

	def get_exercise_title_visible(self):
		return self.D.get('exercise_title_visible')

	def get_exercise_description_visible(self):
		return self.D.get('exercise_description_visible')

	def get_date_set(self):
		return self.D.get('date_set')

	def get_date_due(self):
		return self.D.get('date_due')

	def get_pupil_name(self):
		return self.D.get('pupil_name')

	def get_question_attempts_required(self):
		return self.D.get('question_attempts_required')

	def get_level_scores(self):
		"""
		Return a summary of how well the pupil has done on each level
		correct, incorrect, hints, etc...
		Question log looks like so:
		[   {   u'ans': [u'3'],
                  u'df': u'question',
                  u'hint': u'no_hint',
                  u'qu': 0,
                  u'score': 1},
              {   u'ans': [u'sing'],
                  u'df': u'question',
                  u'hint': u'no_hint',
                  u'qu': 1,
                  u'score': 0} ]

        Output looks like this:
        {0: {'correct_count': 3, 'correct_pct': 1.0, 'incorrect_count': 0},
 		 1: {'correct_count': 3, 'correct_pct': 1.0, 'incorrect_count': 0}}

 		We can display this by looping through levels
 		Any level with C+I = 0 is blank (no questions answered), otherwise colour according to correct_pct
		"""
		output_list = {}
		for level_number in range(len(self.get_level_hash_list())):
			correct_count = 0
			incorrect_count = 0
			answer_log = self.D[str(level_number)]
			for d in answer_log:
				if d['df'] in ['scaffold', 'question']:
					correct_count += d['score']
					incorrect_count += 1-d['score']
			output_list[level_number] = {
				'correct_count':correct_count,
				'incorrect_count':incorrect_count,
				'correct_pct':correct_count*1.0 / (correct_count + incorrect_count) if correct_count + incorrect_count > 0 else 0
			}
		return output_list

	def get_total_score(self):
		"""
		Returns the current score as a decimal, 1 = 100%, 0.5 = 50%, and so on
		Level scores look like this
		{0: {'correct_count': 3, 'correct_pct': 1.0, 'incorrect_count': 0},
 		 1: {'correct_count': 3, 'correct_pct': 1.0, 'incorrect_count': 0}}
		"""
		level_scores = self.get_level_scores()
		correct_count, incorrect_count = 0, 0
		for L in level_scores:
			correct_count += level_scores[L]['correct_count']
			incorrect_count += level_scores[L]['incorrect_count']
		return correct_count*1.0 / (correct_count + incorrect_count) if correct_count + incorrect_count > 0 else 0

	def get_percentage_attempted(self):
		"""
		Return proportion of exercise completed if in progress, as a decimal
		"""
		question_attempts_required = int(self.get_question_attempts_required())
		level_scores = self.get_level_scores()
		questions_attempted = 0
		for L in level_scores:
			questions_attempted += (level_scores[L]['correct_count']+level_scores[L]['incorrect_count'])
		return questions_attempted*1.0 / (question_attempts_required)


	def set_progress_snapshot(self, progress_snapshot):
		self.D['progress_snapshot'] = progress_snapshot

	def update_answer_logs(self, answer_log):
		level_key = answer_log['level']
		answer_log.pop("level", None)
		self.D[str(level_key)].append(answer_log)		

	def set_status(self, status):
		"""
		Update status
		"""
		self.D['status'] = status
		print "Changed status to {}".format(status)

	def update_status(self):
		"""
		Set the status according to variables
		If current status is 'not_started' and there is a progress snapshot, must be 'in_progress'
		If current status is 'not_started' and there is no progress snapshot, must still be 'not_started'
		If current status is 'in_progress' and there is a progress snapshot, must still be 'in_progress'
		If current status is 'in_progress' and there no progress snapshot, must be 'complete' (because we send '0' in this case)
		If current status is 'complete' we don't change it
		"""
		current_status = self.get_status()
		progress_snapshot = self.get_progress_snapshot()
		print "Status {} and progress {}".format(current_status, progress_snapshot)
		if current_status == 'not_started' and progress_snapshot:
			self.set_status('in_progress')
		elif current_status == 'in_progress' and progress_snapshot in (0, '0'):
			self.set_status('complete')

	def get_all_info(self):
		"""
		Return all info from object as a dict (in order to save back to mongodb)
		"""
		return self.D



def load_submission(user_id, homework_id):
	"""
	Load submission object given a user_id and homework_id
	"""
	return None

def create_submission(pupil_id, pupil_name, homework_object, level_hash_list):
	"""
	Given a pupil and homework id, create a submission object
	Add the level slots to keep track of answers
	"""
	submission = Submission (
		{
			'user_id':str(pupil_id),
			'pupil_name':pupil_name,
			'homework_id':homework_object.get_id(),
			'exercise_name_unique':homework_object.get_exercise_name_unique(),
			'exercise_title_visible':homework_object.get_exercise_title_visible(),
			'exercise_description_visible':homework_object.get_exercise_description_visible(),
			'level_hash_list':level_hash_list,
			'status': 'not_started', #(not_started | in_progress | complete)
			'progress_snapshot':0, # [2, 4, 3, 5, 1, 0, [7,2,6,1,5,4,3,8]] --> current_level, current_question, correct_total, incorrect_total, correct_level, incorrect_level, question_order
			'date_set':homework_object.get_date_set(),
			'date_due':homework_object.get_date_due(),
			'question_attempts_required':homework_object.get_question_attempts_required()
		}
	)
	submission.create_empty_level_slots()
	save_object(submission, collection_name='submissions')



#################### SPECIALIZED FUNCTIONS ####################

def get_level_by_hash(level_hash):
	"""
	Return a level blob given its hash
	"""
	levels = db['levels']
	print "Getting the level blob bruv... {}".format(level_hash)
	level_all = levels.find_one({'hash':level_hash})
	return level_all['dict']

def create_homework(exercise_object, classroom_object, teacher_object, date_due):
	"""
	Create a new homework, when it is set by the teacher
	Create submissions for each pupil
	"""
	homework = Homework(
			{
				'exercise_hash':exercise_object.get_exercise_hash(),
				'exercise_name_unique':exercise_object.get_exercise_name_unique(),
				'exercise_title_visible':exercise_object.get_exercise_title_visible(),
				'exercise_description_visible':exercise_object.get_exercise_description_visible(),
				'exercise_id':exercise_object.get_id(),
				'question_attempts_required':exercise_object.get_question_attempts_required(),
				'level_hash_list':exercise_object.get_level_hashes(),
				'teacher_name':teacher_object.get_display_name(),
				'classroom_name':classroom_object.get_classroom_name(),
				'classroom_id':classroom_object.get_id(),
				'teacher_id':teacher_object.get_id(),
				'pupils':{},
				'pupils_set_count':0,
				'pupils_started_count':0,
				'pupils_completed_count':0,
				'date_set':time.time(),
				'date_due':''
			}
		)
	homework.set_date_due(date_due)
	
	# Get all pupils in the class and add to homework
	# pupil_list = classroom_object.get_pupils()  # Each is a mini dict with name and ID	
	# homework.add_pupils(pupil_list, exercise_object.get_level_hashes())
	homework_id = save_object(homework, collection_name='homeworks')

	# # Add the homework to each pupil's record
	# object_ids = [P.get('_id') for P in pupil_list] # Get a list of object IDs for the pupils
	# cursor = db.users.find({ "_id": { "$in": object_ids } }) # Get all pupils from the pupil collection: https://docs.mongodb.org/manual/reference/operator/#AdvancedQueries-%24in, http://stackoverflow.com/questions/29560961/query-mongodb-for-multiple-objectids-in-array
	# for D in cursor:
	# 	pupil = User(D)
	# 	pupil.add_homework(homework)
	# 	save_object(pupil, collection_name = 'users')

	# Add the exercise to the class's record
	classroom_object.add_homework(homework)
	save_object(classroom_object, collection_name = 'classrooms')

	# Create a submission object for each pupil
	pupil_list = classroom_object.get_pupils()
	level_hash_list = exercise_object.get_level_hashes()
	homework_id = homework_id.inserted_id
	homework_object = load_by_id(homework_id, 'homeworks')
	for pupil_dict in pupil_list:
		pupil_id = pupil_dict['_id']
		pupil_name = pupil_dict['display_name']
		create_submission(pupil_id, pupil_name, homework_object, level_hash_list)

def create_classroom(teacher_object, subject_name, yeargroup_name):
	"""
	Given a teacher object and a yeargroup and subject name, create classroom
	Return classroom ID as well as entry code
	"""
	classroom = Classroom(
			{
				'yeargroup_name':'',
				'subject_name':'',
				'teacher_name':'',
				'teacher_id':'',
				'classroom_name':'',
				'entry_code':'',
				'homeworks':[],
				'pupils':[]
			}
		)
	classroom.set_yeargroup_name(yeargroup_name)
	classroom.set_subject_name(subject_name)
	classroom.set_teacher_name(teacher_object.get_display_name())	
	classroom.set_teacher_id(teacher_object.get_id(to_string=True))	
	classroom.set_entry_code()	
	_ = save_object(classroom, collection_name = 'classrooms')
	return _.inserted_id, classroom.get_entry_code()

def create_user(username, first_name, surname, display_name, password_hash, is_teacher):
	"""
	Create a new user object
	"""
	user = User(
		{
			'username':username,
			'display_name':'',  # Pupils can't change, teachers can
			'first_name':first_name,
			'surname':surname,
			'password_hash':password_hash,
			'classrooms':[],
			'homeworks':{},
			'is_teacher':is_teacher
		}
	)
	user.set_display_name(display_name)
	_ = save_object(user, collection_name = 'users')
	return _.inserted_id

def pupil_joins_classroom(pupil_object, classroom_object):
	"""
	When a pupil joins a classroom:
		- Add classroom to pupil's object
		- Add pupil to classroom object
	"""
	classroom_object.add_pupil(pupil_object)
	pupil_object.add_classroom(classroom_object)
	save_object(classroom_object, collection_name = 'classrooms')
	save_object(pupil_object, collection_name = 'users')


def pupil_starts_homework(pupil_object, homework_object):
	"""
	Pupil starts homework
	Create an 'attempt' dict
	"""
	None


def pupil_submits_answer(pupil_object, homework_object, answer_data):
	"""
	Pupil submits answer. Known already if right or wrong
	answer_data = {
			'homework_complete':False,
			'correct_count':6,
			'incorrect_count':4,
			'level':3,
			'question':4,
			'display_format':'question',			
			'answers_recorded':{'ans1':4, 'ans2':5},
			'is_correct':True,	
			'hint':True,
		}
	"""
	# TODO
	# actually we don't know what the correct/incorrect counts are from the ajax
	# we just know the level/user/homework/question
	# so we should query the homework, which will tell us complete/incomplete for pupil
	# and how many corrects required (per level)
	# and therefore can fill in the remainder of the answer_data, saying is_complete etc.
	# Then we can fill in the two things below...

	# TODO
	# Actually maybe it's not a great idea having all pupil's progress within HWK DB
	# Since if many pupils submitting at once, we may have concurrency issues
	# where a pupil's progress isn't updated as it is overwritten by another one loading/writing

	# Update the pupil's database entry with progress
	pupil_object.increment_homework(homework_object, answer_data)
	save_object(pupil_object, 'users')

	# Update the homework's database entry with progress
	homework_object.increment_homework(pupil_object, answer_data)
	save_object(homework_object, 'homeworks')

	

################# DEMO / TEST #################

if __name__ == "__main__":

	if run_demo:
		# Remove users
		db['users'].remove()
		db['classrooms'].remove()
		db['homeworks'].remove()
		db['submissions'].remove()

		# Create some pupils
		from werkzeug.security import generate_password_hash
		password_hash = generate_password_hash('123')
		create_user('davidabelman', 'David', 'Abelman', password_hash=password_hash, display_name = None, is_teacher=False)
		create_user('tonyblair', 'Tony', 'Blair', password_hash=password_hash, display_name = None, is_teacher=False)
		create_user('adamguy', 'Adam', 'Guy', password_hash=password_hash, display_name = None, is_teacher=False)
		create_user('woodylewenstein', 'Woody', 'Lewenstein', password_hash=password_hash, display_name = None, is_teacher=False)
		create_user('annieabelman', 'Annie', 'Abelman', password_hash=password_hash, display_name = None, is_teacher=False)
		create_user('anniehughes', 'Annie', 'Hughes', password_hash=password_hash, display_name = None, is_teacher=False)
		create_user('benabelman', 'Ben', 'Abelman', password_hash=password_hash, display_name = None, is_teacher=False)

		# Create some teachers
		create_user('dennehy1234', 'A', 'Dennehy', password_hash=password_hash, display_name = 'Miss Dennehy', is_teacher=True)
		create_user('asher999', 'Tony', 'Asher', password_hash=password_hash, display_name = 'Sir Asher', is_teacher=True)

		# Make teacher create a class each
		_id_class1, entry_code_1 = create_classroom(
			teacher_object = load_by_username('asher999'),
			subject_name = 'Mechanics',
			yeargroup_name = 'Year 11'
			)
		_id_class2, entry_code_2 = create_classroom(
			teacher_object = load_by_username('dennehy1234'),
			subject_name = 'Pure',
			yeargroup_name = 'Year 11'
			)

		# Pupils add themselves to classes
		classroom_1 = load_by_id(_id_class1, 'classrooms')
		for u in ['adamguy', 'davidabelman', 'woodylewenstein', 'annieabelman', 'benabelman']:
			pupil = load_by_username(u)
			if pupil.D:
				pupil_joins_classroom(pupil, classroom_1)
		classroom_2 = load_by_id(_id_class2, 'classrooms')
		for u in ['tonyblair', 'davidabelman', 'arong', 'annieabelman', 'adamguy']:
			pupil = load_by_username(u)
			if pupil.D:
				pupil_joins_classroom(pupil, classroom_2)

		# Teacher sets a homework
		exercise_object = load_by_id(
			db['exercises'].find_one({'dict.exercise_name_unique':'angles180'})['_id'],
			'exercises')
		classroom_object = load_by_id(_id_class1, 'classrooms')
		teacher_object = load_by_username('asher999')
		create_homework(exercise_object, classroom_object, teacher_object, date_due='2015-12-12')

	# Take a look at the databases!
	for collection_name in ['users', 'classrooms', 'homeworks', 'exercises', 'submissions']:
		print collection_name
		print "================="
		view(db[collection_name])
		print "\n\n"

