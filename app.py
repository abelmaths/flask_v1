"""
25th Jan - fix 'wrong answer' section (DONE), add 'answer limit' section (DONE), add basic image functionality (DONE), finish basic teacher/pupil views (DONE)
1st Feb - add password protection to login (DONE), get basic version on the web (DONE)
8th Feb - 'create homework' page flow for teachers (DONE) and 'create class' page flow for teachers (DONE), correct the date formats (TODO) 
15th Feb - add 'create account' / 'signup' / 'demo login' (TBC) functionality, woody level uploader?, refactor code including async DB setting
7th March - make it look pretty, look into dynatable, add loads of validation checks in JS (are all fields filled, are usernames valid, do dates make sense)
Afterwards - consider multiple choice, how to generate images, etc.

Immediate to do list
================================
--Dynatable
--Create classroom and set homework page
--Create homework flash message
--Any tweaks to login/signup functionality. Add a 'home' logo
--Make top bar nicer
--Create 'join class' page for logged in pupil
--Formatting in exercise - make fonts right size, highlight question being asked etc.
Do a check to set max limit on questions if exercise is short
Upload questions
SEND TO WOODY
Refactor code to make all consistent and DRY
Put progress bars and statuses in appropriate tables to make visually better


Views to complete:
===============================
Filter pupils by class when seeing 'pupil view' from class view
Filter exercises by class when seeing 'exercise view' from class view
Select correct class when clicking 'set exercise' in class view
Settings for teacher
Settings for pupil
Existing pupil join a classroom
Design nice enough looking homepage

Other things todo:
================================
* Change classroom name in DB to not include teacher's name
* check I have Fixed login section on all pages where it shows (refactor code to appear in its own template with associated JS)
* Deal with dates displayed in datatables, and datepicker
* _pupil_join_classroom_confirm and _create_pupil_via_school have repetitive code
* Allow teacher to see pupil's attempt at an exercise
* Allow teacher to preview exercise
* Once datepicker sorted, make default value for hwk set = Now (or have it blank and do it in Python)

Things to alter once in testing
================================
Redo pupil's view into cards(?) to make nicer
Explore bootstrap themes for visual niceness
Count wrong attempts for people trying to join a classroom
Make classroom codes longer/harder but still simple to type. Make sure there are no duplicates when code is generated.
Add expiration date to classroom code?
Add settings for a teacher to remove pupil, delete a homework, edit date due for homework, reset pupil passwords
Make login use a form rather than jquery? Hash password? See: http://stackoverflow.com/questions/17248888/how-to-redirect-with-flask-and-jquery
Create homework - advanced options (include/exclude pupils, date set)

"""

from flask import Flask, url_for, render_template, request, session, redirect, flash
#from flask.ext.script import Manager
import json
import mongo
import os
from functools import wraps
reload(mongo)
from mongo_setup import *
from bson.objectid import ObjectId
from id_masker import id_mask
from werkzeug.security import generate_password_hash
#from flask.ext.wtf import Form
#from wtforms import StringField, SubmitField
#from wtforms.validators import Required

app = Flask(__name__)
app.secret_key = os.environ['APP_SECRET_KEY']
#manager = Manager(app)


#################################### GENERAL FUNCTIONS ####################################
def debug(argument):
    if True:
        print argument

@app.before_request
def before_request():
    # If we have a user in session variable, create user object
    global USER
    # User object with populated or empty dict depending if any logged in
    USER = mongo.User(session.get('user', {}))
    USER.print_to_console()

def login_required(function_to_protect):
    @wraps(function_to_protect)
    def wrapper(*args, **kwargs):
        if USER.exists():  # i.e. an actual user is loaded within session cookie courtesy of before_request()
            return function_to_protect(*args, **kwargs)
        else:   # no user loaded, go to some non-logged in page
            flash('You must be logged in to view this page')
            return redirect(url_for('entry'))
    return wrapper

def must_be_teacher(function_to_protect):
    @wraps(function_to_protect)
    def wrapper(*args, **kwargs):
        if not USER.is_teacher():
            flash('Only teachers can view this page')
            return redirect(url_for('pupil_all_exercises'))
        else:
            return function_to_protect(*args, **kwargs)
    return wrapper

def must_be_pupil(function_to_protect):
    @wraps(function_to_protect)
    def wrapper(*args, **kwargs):
        if USER.is_teacher():
            return redirect(url_for('teacher_all_exercises'))
        else:
            return function_to_protect(*args, **kwargs)
    return wrapper

@app.route("/redirect_with_flash/<redirect_url_for>/<flash_message>", methods=["GET", "POST"])
def redirect_with_flash(redirect_url_for, flash_message):
    debug_text = "Redirecting to {}, flash message = {}".format(redirect_url_for, flash_message)
    debug(debug_text)
    flash(flash_message)
    return redirect(url_for(redirect_url_for))

@app.route('/')
def home():
    if not USER.exists():
        return redirect(url_for('entry'))
    if USER.is_teacher():
        return redirect(url_for('teacher_all_exercises'))
    if not USER.is_teacher():
        return redirect(url_for('pupil_all_exercises'))
    else:
        debug('Unknown USER state within home()')

@app.route('/level_test_uploader', methods=['GET', 'POST'])
def level_test_uploader():
    if request.method == 'POST':
        variables = request.files['variables']
        skeleton = request.files['skeleton']
        exercise_title_visible = request.form['exercise_title_visible']
        exercise_description = request.form['exercise_description']
        from level_test_uploader import test_uploader
        test_uploader(variables, skeleton, exercise_title_visible, exercise_description)
        flash('Attempted to create exercise. Set exercise for pupil to see if successful.')
        return redirect(url_for('home'))

    return render_template('level_test_uploader.html')

def display_pct(number):
    """
    Convert fraction into rounded percentage
    If string (i.e. blank, no attempt) return '-'
    """
    if isinstance(number, str):
        return number
    return '{0:.0f}%'.format(number*100)

        

#################################### GENERAL VIEWS ####################################
@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

#################################### TEACHER CREATING THINGS ####################################
@app.route('/instructor/create_classroom')
@login_required
@must_be_teacher
def create_classroom():
    """
    Page for a logged in teacher to create a classroom
    Given the entry code when done
    create_classroom(
        teacher_object, subject_name, yeargroup_name
    )
    """
    return render_template('instructor_create_classroom.html')

@app.route('/instructor/set_exercise')
@login_required
@must_be_teacher
def set_exercise():
    """
    Page for a logged in teacher to create an exercise/homework
    Select their class and the subject
    create_homework(exercise_object, classroom_object, teacher_object, date_due='2015-12-12')
    """
    # Load classes that they own
    classroom_array = USER.get_my_classes_teacher()

    # Load list of all exercises
    exercise_array = mongo.get_all_exercises()

    return render_template('instructor_set_exercise.html',
        classroom_array = classroom_array,
        exercise_array = exercise_array
        )

@app.route('/_create_classroom_submit', methods=['GET', 'POST'])
def create_classroom_submit():
    """
    AJAX endpoint for teacher creating a classroom
    Given subject and classname, will create a classroom and return classroom code
    """
    class_name = request.json['class_name']
    subject = request.json['subject']

    _id, classroom_code = mongo.create_classroom(USER, subject, class_name)
    
    # Debug
    debug_text = "id = {}, classroom_code = {}".format(_id, classroom_code)
    debug(debug_text)

    return_data = {'classroom_code':classroom_code}
    return json.dumps({'status':1, 'data':return_data})


@app.route('/_create_homework_submit', methods=['GET', 'POST'])
def create_homework_submit():
    """
    Create a homework object and save to database
    (this will create submission for each pupil)
    """
    classroom_id = request.json['classroom_id']
    exercise_id = request.json['exercise_id']
    date_set = request.json['date_set']
    date_due = request.json['date_due']
    attempts_required = request.json['attempts_required']
    pupil_list = request.json['pupil_list']
    exclude_include = request.json['exclude_include']

    exercise_object = mongo.load_by_id(ObjectId(exercise_id), 'exercises')
    classroom_object = mongo.load_by_id(ObjectId(classroom_id), 'classrooms')

    # Debug
    debug_text = "Loaded this exercise --> {}".format(exercise_object.D)
    debug(debug_text)
    debug_text = "Loaded this classroom --> {}".format(classroom_object.D)
    debug(debug_text)

    mongo.create_homework(
        exercise_object = exercise_object,
        classroom_object = classroom_object,
        teacher_object = USER,
        date_set=date_set,
        date_due=date_due)

    debug("Created homework.")

    return_data = {}
    return json.dumps({'status':1, 'data':return_data})

#################################### CREATE ACCOUNT ####################################
@app.route('/entry')
def entry():
    """
    Signup or login
    """
    return render_template('entry.html')

@app.route('/entry/<entry_code>')
def signup_pupil_into_classroom(entry_code):
    """
    Page for pupil to signup to a classroom using username and password
    i.e. school account
    If already logged in, allow logged in pupil to add class to their roster
    But count wrong attempts (for logged in or anon user) and block if too many
    """

    debug("Trying to enter class with entry code:{}".format(entry_code))

    classroom = mongo.load_by_arbitrary({'entry_code':entry_code}, 'classrooms')
    if not classroom.exists():
        flash('Sorry, this classroom does not exist')
        return redirect(url_for('home'))

    if USER.exists():
        # Check if already a member of this class
        if classroom.check_if_pupil_in_class(USER.get_id()):
            flash('You are already a member of this class')
            return redirect(url_for('pupil_all_exercises'))
        else:
            # Show confirmation page for pupil to confirm entry to class
            return render_template('pupil_join_classroom_confirm.html',
                entry_code=entry_code,
                teacher_name=classroom.get_teacher_name(),
                classroom_name=classroom.get_classroom_name()
                )
    else:    
        # If not logged in, allow account creation        
        return render_template('signup_pupil_via_school.html', entry_code=entry_code)

@app.route('/entry/independent')
def signup_pupil_independent():
    """
    Page for pupil to signup for independent account
    """
    return render_template('signup_pupil_independent.html')

@app.route('/_pupil_join_classroom_confirm', methods=['GET', 'POST'])
def pupil_join_classroom_confirm():
    """
    Pupil joins classroom (already logged in, entry code for classroom)
    """
    entry_code = request.json['entry_code']
    
    # Add to class
    USER_db = mongo.load_by_id(ObjectId(USER.get_id()), 'users') # Load proper pupil from DB
    classroom = mongo.load_by_arbitrary({'entry_code':entry_code}, 'classrooms')
    mongo.pupil_joins_classroom(USER_db, classroom)

    # Create submission objects (should refactor all of this code a bit)
    pupil_id = USER.get_id()
    pupil_name = USER.get_display_name()
    for homework_id in classroom.get_homework_ids():
        homework_object = mongo.load_by_arbitrary({'_id':homework_id}, 'homeworks')
        mongo.create_submission(pupil_id, pupil_name, homework_object)

    return_data = {}
    return json.dumps({'status':1, 'data':return_data})

@app.route('/complete_personal_info')
def complete_personal_info():
    """
    Require user to fill in personal info now that they are signed up
    """
    return render_template('complete_personal_info.html')

@app.route('/_submit_personal_info', methods=['GET', 'POST'])
def submit_personal_info():
    firstname = request.json['firstname']
    surname = request.json['surname']

    # Load full USER object from DB to make edits to it
    U = mongo.load_by_username(USER.get_username())

    U.set_surname(surname)
    U.set_firstname(firstname)

    if U.is_teacher():
        U = request.json['display_name']
        USER.set_display_name(display_name)
    else:
        U.set_display_name(None)  # Will just amalgamate firstname and surname for pupils

    # Save all of this to the database and put latest in session
    mongo.save_object(U, 'users')
    session['user'] = U.save_to_session()

    return_data = {}
    return json.dumps({'status':1, 'data':return_data})

@app.route('/_create_teacher_attempt', methods=['GET', 'POST'])
def create_teacher_attempt():
    email = request.json['email']
    password = request.json['password']
    firstname = request.json['firstname']
    surname = request.json['surname']
    display_name = request.json['display_name']

    # Check email does not exist in database
    if mongo.load_by_arbitrary({'email':email}, 'users').exists():
        return_data = {'message':'This email address is already registered.'}
        return json.dumps({'status':0, 'data':return_data})

    # Create user
    mongo.create_user(
        username=email,
        firstname=firstname,
        surname=surname,
        display_name=display_name,
        password=password,
        is_teacher=True,
        email=email,
        confirmed=False)

    USER = mongo.load_by_username(email)
    session['user'] = USER.save_to_session()

    return_data = {}
    return json.dumps({'status':1, 'data':return_data})

@app.route('/_create_pupil_via_school', methods=['GET', 'POST'])
def create_pupil_via_school():
    """
    Create pupil account given a valid entry code
    Add pupil to the class whilst creating their account
    """
    username = request.json['username']
    password = request.json['password']
    entry_code = request.json['entry_code']
    firstname = request.json['firstname']
    surname = request.json['surname']
    
    # Check username and password etc.
    USER = mongo.load_by_username(username)
    if USER.exists():
        USER = {}
        return_data = {'message':'Username already taken'}
        return json.dumps({'status':0, 'data':return_data})
    
    # Create user
    mongo.create_user(
        username=username,
        firstname=firstname,
        surname=surname,
        password=password,
        display_name=None,
        is_teacher=False,
        email=None,
        confirmed=False)
    USER = mongo.load_by_username(username)
    session['user'] = USER.save_to_session()

    # Add to class
    classroom = mongo.load_by_arbitrary({'entry_code':entry_code}, 'classrooms')
    mongo.pupil_joins_classroom(USER, classroom)

    # Create submission objects (should refactor all of this code a bit)
    pupil_id = USER.get_id()
    pupil_name = USER.get_display_name()
    for homework_id in classroom.get_homework_ids():
        homework_object = mongo.load_by_arbitrary({'_id':homework_id}, 'homeworks')
        mongo.create_submission(pupil_id, pupil_name, homework_object)

    return_data = {}
    return json.dumps({'status':1, 'data':return_data})

@app.route('/_create_pupil_independent', methods=['GET', 'POST'])
def create_pupil_independent():
    """
    Create pupil account not connected to a class
    """
    email = request.json['email']
    password = request.json['password']
    firstname = request.json['firstname']
    surname = request.json['surname']
    
    # Check username and password etc.
    USER = mongo.load_by_arbitrary({'email':email}, 'users')
    if USER.exists():
        USER = {}
        return_data = {'message':'Username already taken'}
        return json.dumps({'status':0, 'data':return_data})
    
    else:
        # Create user
        mongo.create_user(
            username=email,
            firstname=firstname,
            surname=surname,
            password=password,
            display_name=None,
            is_teacher=False,
            email=email,
            confirmed=False)

        USER = mongo.load_by_arbitrary({'email':email}, 'users')
        session['user'] = USER.save_to_session()

        return_data = {}
        return json.dumps({'status':1, 'data':return_data})
#################################### LOGGING IN ####################################
@app.route('/logout')
def logout():
    """
    Page to logout
    """
    session.clear()
    return render_template('entry.html')

@app.route('/_login_attempt', methods=['GET', 'POST'])
def login_attempt():
    username = request.json['username']
    password = request.json['password']
    
    # Check username and password etc.
    USER = mongo.load_by_username(username)
    if USER.exists():
        password_check_ok = USER.check_password(password)
        if password_check_ok:
            session['user'] = USER.save_to_session()
            return json.dumps({'status':1, 'data':None})
        else:
            USER = {}
            session.clear()
            return_data = {'message':'Incorrect password'}
            return json.dumps({'status':0, 'data':return_data})
    else:
        return_data = {'message':'Username does not exist'}
        return json.dumps({'status':0, 'data':return_data})    


#################################### TEACHER SPECIFIC VIEWS ####################################
@app.route('/instructor/my_exercises')
@login_required
@must_be_teacher
def teacher_all_exercises():
    """
    Show grid of all exercises (old and new and due)
    Filterable
    """
    # Load all submission objects for the pupil
    homeworks = mongo.load_by_arbitrary({'teacher_id':USER.get_id()}, 'homeworks', multiple=True)

    # Send along as json to be used within datatable (javascript)
    homework_data = []
    for H in homeworks:
        record = {
            'exercise_title_visible':H.get_exercise_title_visible(),
            'exercise_description_visible':H.get_exercise_description_visible(),
            'classroom_name':H.get_classroom_name(),
            'date_set':H.get_date_set(),
            'date_due':H.get_date_due(),
            'status_count':H.get_status_count(),
            'see_pupil_progress':{'text':'See pupil progress', 'url':url_for('teacher_exercise_progress', homework_id = H.get_id())},
            'see_exercises':{'text':'Preview exercise', 'url':'/'}
        }
        homework_data.append(record)
        debug(homework_data)

    return render_template('instructor_exercises.html', homework_data = homework_data) #, USER=USER)

@app.route('/instructor/my_pupils')
@login_required
@must_be_teacher
def teacher_all_pupils():
    """
    Show grid of all students
    Should be filterable by class
    """
    # Load pupils (ID, display_name, classrooms)
    pupil_dict = USER.get_my_students_teacher()
    debug("Pupil dict --> {}".format(pupil_dict))

    # Send along as json to be used within datatable (javascript)
    pupil_data = []
    for pupil_id in pupil_dict:
        pupil_name = pupil_dict[pupil_id]['display_name']
        classrooms = pupil_dict[pupil_id]['classrooms']
        record = {
            'name': pupil_name,
            'classrooms': classrooms,
            'see_progress':{'text':"See {}'s progress".format(pupil_name), 'url':url_for('teacher_pupil_progress', pupil_id = pupil_id)},
        }
        pupil_data.append(record)

    return render_template('instructor_pupils.html', pupil_data = pupil_data)

@app.route('/instructor/my_classes')
@login_required
@must_be_teacher
def teacher_all_classes():
    """
    Show grid of all classes
    """
    # Load all classrooms for teacher
    classrooms = mongo.load_by_arbitrary({'teacher_id':USER.get_id()}, 'classrooms', multiple=True)

    # Send along as json to be used within datatable (javascript)
    classroom_data = []
    for C in classrooms:
        record = {
            'name':C.get_classroom_name(),
            'pupil_count':C.get_number_of_pupils(),
            'latest_set':C.get_latest_set_and_next_due_homeworks(),
            'next_due':C.get_latest_set_and_next_due_homeworks(),
            'entry_code':C.get_entry_code(),
            'see_pupils':{'text':'Pupils', 'url':'/'},
            'see_exercises':{'text':'Exercises', 'url':'/'},
            'set_exercise':{'text':'Set exercise', 'url':'/'},
        }
        classroom_data.append(record)

    return render_template('instructor_classrooms.html', classroom_data=classroom_data)

@app.route('/instructor/submissions/exercise/<homework_id>')
@login_required
def teacher_exercise_progress(homework_id):
    """
    Show all pupils and their progress on the exercise
    """
    submissions = mongo.load_by_arbitrary({'teacher_id':USER.get_id(), 'homework_id':homework_id}, 'submissions', multiple=True)

    # Send along as json to be used within datatable (javascript)
    submission_data = []
    for S in submissions:
        record = {
            'pupil_name':S.get_pupil_name(),
            'exercise_title_visible':S.get_exercise_title_visible(),
            'progress':S.get_level_scores(),
            'status':S.get_status_display(),
            'total_score':display_pct(S.get_total_score()),
            'percentage_attempted':display_pct(S.get_percentage_attempted()),
            'see_attempt':{'text':'See attempt (TODO)', 'url':'/'},
        }
        submission_data.append(record)

    return render_template('instructor_submissions.html', submission_data = submission_data, format='pupils')

@app.route('/instructor/submissions/pupil/<pupil_id>')
@login_required
def teacher_pupil_progress(pupil_id):
    """
    Show all exercise submissions for the pupil
    Note: only include classes for which the current user is a teacher
    """
    submissions = mongo.load_by_arbitrary({'teacher_id':USER.get_id(), 'user_id':pupil_id}, 'submissions', multiple=True)

    # Send along as json to be used within datatable (javascript)
    submission_data = []
    for S in submissions:
        record = {
            'pupil_name':S.get_pupil_name(),
            'exercise_title_visible':S.get_exercise_title_visible(),
            'progress':S.get_level_scores(),
            'status':S.get_status_display(),
            'total_score':display_pct(S.get_total_score()),
            'percentage_attempted':display_pct(S.get_percentage_attempted()),
            'see_attempt':{'text':'See attempt (TODO)', 'url':'/'},
        }
        submission_data.append(record)

    return render_template('instructor_submissions.html', submission_data = submission_data, format='exercises')

@app.route('/instructor/exercise_preview/<exercise_id>')
@login_required
def teacher_exercise_preview():
    return """
    Preview of 1 question per level on the exercise
    Should we make it subscription only, or offer previews to non subscription?
    """

@app.route('/instructor/pupil/<username>')
@login_required
def teacher_pupil_summary():
    return """
    (Lower priority)
    \nShow a single pupil's history
    \nAnd stats over time
    \nIf they link to the pupil via a class
    \nGood for parents eve
    """


#################################### PUPIL SPECIFIC VIEWS ####################################
@app.route('/my_exercises')
@login_required
@must_be_pupil
def pupil_all_exercises():
    """
    Table (or nicer format) if all exercises done and to do
    \nTo do: can click (green) 'do exercise'
    \nDone: can click different button (blue) saying 'revisit'
    """
    # Load all submission objects for the pupil
    submissions = mongo.load_by_arbitrary({'user_id':USER.get_id()}, 'submissions', multiple=True)

    # Send along as json to be used within datatable (javascript)
    submission_data = []
    for S in submissions:
        record = {
            'exercise_name':{'text':S.get_exercise_title_visible(), 'url':S.get_href()},
            'exercise_description_visible':S.get_exercise_description_visible(),
            'status':S.get_status_display(),
            'total_score':display_pct(S.get_total_score()),
            'percentage_attempted':display_pct(S.get_percentage_attempted()),
            'date_set':S.get_date_set(),
            'date_due':S.get_date_due(),
        }
        submission_data.append(record)

    return render_template('my_exercises.html', submission_data = submission_data)

@app.route('/my_progress')
@login_required
def pupil_progress():
    return """
    My progress - topline stats, questions attempted/answered, a chart, medals
    """

@app.route('/my_classes')
@login_required
def pupil_classes():
    return """
    My progress - topline stats, questions attempted/answered, a chart, medals
    """

@app.route('/join_class')
@login_required
def pupil_join_class_interface():
    """
    Interface for pupil to add classroom code when logged in already
    in order to join a classroom
    """
    return render_template('pupil_join_classroom_interface.html')

#################################### EXERCISE ####################################
@app.route('/exercise/<homework_id>')
@login_required
def exercise(homework_id):
    """
    Load the exercise (by homework id)
    Retrieve level list from homework id and send to javascript via jinja
    The html will then run the level page from there (by loading each level one by one)
    """
    # Load submission entry to find status of submission (not started, in progress, complete (i.e. practice))
    submission = mongo.load_by_arbitrary(
        {'user_id':USER.get_id(), 'homework_id':homework_id},
        'submissions')
    status = submission.get_status()
    progress_snapshot = submission.get_progress_snapshot()
    level_hash_list = submission.get_level_hash_list()
    exercise_title_visible = submission.get_exercise_title_visible()
    exercise_description_visible = submission.get_exercise_description_visible()
    question_attempts_required = submission.get_question_attempts_required()

    # If hasn't started, load page as homework submission with no progress
    if status=='not_started':
        exercise_status = 'submission'

    # If in progress, load page as homework submission passing latest progress
    elif status=='in_progress':
        exercise_status = 'submission'

    # If revision, load page as practice, passing latest progress
    elif status=='complete':
        exercise_status = 'revision'

    else:
        print "Unrecognised status!"
    
    return render_template('level_tester_full_exercise.html',
        level_hash_list = level_hash_list,
        exercise_status = exercise_status,
        progress_snapshot = progress_snapshot,
        homework_id = id_mask(homework_id, method='encrypt'),
        exercise_title_visible = exercise_title_visible,
        exercise_description_visible = exercise_description_visible,
        question_attempts_required = question_attempts_required,
        USER=USER)

@app.route('/_get_level_blob', methods=['GET', 'POST'])
def get_level_blob():
    """
    Saves progress to database for this user
    Returns the level dict given a hash of that level
    """
    # Get the next level
    next_level_hash = request.json['next_level_hash']
    debug("Getting level blob {}".format(next_level_hash))
    next_level_dict = mongo.get_level_by_hash(next_level_hash)
    if next_level_dict:
        return json.dumps({'status':1, 'data':next_level_dict})
    else:
        return_data = {'message':'Query did not return a level_dict'}
        return json.dumps({'status':0, 'data':return_data})

@app.route('/_save_progress', methods=['GET', 'POST'])
def save_progress():
    """
    Save progress snapshot (for loading purposes),
    update the answer log, set the status of the submission
    """
    # Load submission entry
    progress_snapshot = request.json['progress_snapshot']
    answer_log = request.json['answer_log']
    homework_id = id_mask(request.json['homework_id'], method='decrypt')
    question_time_taken = request.json['question_time_taken']
    
    debug("We got this progress snapshot:")
    debug(progress_snapshot)

    submission = mongo.load_by_arbitrary(
        {'user_id':USER.get_id(), 'homework_id':homework_id},
        'submissions')

    # Set the progress snapshot to show latest progress (for when we next want to load)
    submission.set_progress_snapshot(progress_snapshot)
    
    # If this is the actual homework, add answer to the log
    if submission.get_status() != 'complete':
        submission.update_answer_logs(answer_log)
        # Update the status to 'in_progress' or 'complete'
        submission.update_status()    

        if submission.get_status() == 'complete':
            print "Homework is now complete, do stuff here that needs to be done (e.g. updating other records)"

    # Save to database
    mongo.save_object(submission, 'submissions')
    return_data = {'message':'Saved data successfully.'}
    return json.dumps({'status':1, 'data':return_data})

if __name__ == '__main__':
    app.run(debug=True)