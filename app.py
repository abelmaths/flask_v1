"""
25th Jan - fix 'wrong answer' section (DONE), add 'answer limit' section (DONE), add basic image functionality (DONE), finish basic teacher/pupil views (DONE)
1st Feb - add password protection to login (DONE), get basic version on the web (DONE)
8th Feb - 'create homework' page flow for teachers (TODO) and 'create class' page flow for teachers (DONE), correct the date formats (TODO) 
15th Feb - add 'create account' / 'signup' / 'demo login' (TBC) functionality, woody level uploader?, refactor code including async DB setting
7th March - make it look pretty, look into dynatable, add loads of validation checks in JS (are all fields filled, are usernames valid, do dates make sense)
Afterwards - consider multiple choice, how to generate images, etc.

Mini things todo:
Fix login section on all pages where it shows (refactor code to appear in its own template with associated JS)
_pupil_join_classroom_confirm and _create_pupil_via_school have repettive code
Generate tables using dynatable - deal with dates in this part
Once datepicker sorted, make default value for hwk set = Now (or have it blank and do it in Python)
Count wrong attempts for people trying to join a classroom
Make classroom codes longer/harder but still simple to type
Add expiration date to classroom
Add settings for a teacher to remove pupil, delete a homework, edit date due for homework, reset pupil passwords
Change classroom name in DB to not include teacher's name
Make login use a form rather than jquery? Hash password? See: http://stackoverflow.com/questions/17248888/how-to-redirect-with-flask-and-jquery
Add flash message to hide_body_and_redirect in base.js (i.e. when something has happened, want to give flash message as feedback on redirect)

Views to complete:
Filter pupils by class when seeing 'pupil view' from class view
Filter exercises by class when seeing 'exercise view' from class view
Select correct class when clicking 'set exercise' in class view
Settings for teacher
Settings for pupil
Existing pupil join a classroom
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
    print "Redirecting to {}, flash message = {}".format(redirect_url_for, flash_message)
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
        print "WHAT?!!"

@app.route('/exercise_tester')
@login_required
def exercise_tester():
    return render_template('level_tester_full_exercise.html')


#################################### CREATION OF THINGS ####################################
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

    return render_template('instructor_set_exercise.html', classroom_array = classroom_array, exercise_array = exercise_array)


#################################### LOGGING IN ####################################

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

    classroom = mongo.load_by_arbitrary({'entry_code':entry_code}, 'classrooms')
    if not classroom.exists():
        flash('Sorry, this classroom does not exist')
        return redirect(url_for('pupil_all_exercises'))

    # TODO: if logged in, take to 'add a class' page within their logged in user
    if USER.exists():
        # Check if already a member of this class
        if classroom.check_if_pupil_in_class(USER.get_id()):
            flash('You are already a member of this class')
            return redirect(url_for('pupil_all_exercises'))
        else:
            return render_template('pupil_join_classroom.html', entry_code=entry_code, teacher_name=classroom.get_teacher_name(), classroom_name=classroom.get_classroom_name())
    else:    
        # If not logged in, allow account creation        
        return render_template('signup_pupil_via_school.html', entry_code=entry_code)

@app.route('/entry/independent')
def signup_pupil_independent():
    """
    Page for pupil to signup for independent account
    """
    return render_template('signup_pupil_independent.html')

@app.route('/logout')
def logout():
    """
    Page to logout
    """
    session.clear()
    return render_template('entry.html')

@app.route('/complete_personal_info')
def complete_personal_info():
    """
    Require user to fill in personal info now that they are signed up
    """
    return render_template('complete_personal_info.html')


#################################### GENERAL VIEWS ####################################
@app.route('/settings')
@login_required
def settings():
    return """
    Change settings
    """


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
    return render_template('instructor_exercises.html', homework_array = homeworks, USER=USER)

@app.route('/instructor/my_pupils')
@login_required
@must_be_teacher
def teacher_all_pupils():
    """
    Show grid of all students
    \nFilterable (by class)
    """
    pupil_dict = USER.get_my_students_teacher()
    print pupil_dict
    return render_template('instructor_pupils.html', pupil_dict = pupil_dict)

@app.route('/instructor/my_classes')
@login_required
@must_be_teacher
def teacher_all_classes():
    """
    Show grid of all classes
    """
    # Load all classrooms for teacher
    classrooms = mongo.load_by_arbitrary({'teacher_id':USER.get_id()}, 'classrooms', multiple=True)
    return render_template('instructor_classrooms.html', classroom_array = classrooms)

@app.route('/instructor/submissions/exercise/<homework_id>')
@login_required
def teacher_exercise_progress(homework_id):
    """
    Show all pupils and their progress on the exercise
    """
    submissions = mongo.load_by_arbitrary({'teacher_id':USER.get_id(), 'homework_id':homework_id}, 'submissions', multiple=True)
    return render_template('instructor_submissions.html', submission_array = submissions, format='pupils')

@app.route('/instructor/submissions/pupil/<pupil_id>')
@login_required
def teacher_pupil_progress(pupil_id):
    """
    Show all exercise submissions for the pupil
    """
    submissions = mongo.load_by_arbitrary({'teacher_id':USER.get_id(), 'user_id':pupil_id}, 'submissions', multiple=True)
    return render_template('instructor_submissions.html', submission_array = submissions, format='exercises')

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
    return render_template('my_exercises.html', submission_array = submissions)

@app.route('/my_progress')
@login_required
def pupil_progress():
    return """
    My progress - topline stats, questions attempted/answered, a chart, medals
    """

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

#################################### AJAX ####################################
@app.route('/_create_classroom_submit', methods=['GET', 'POST'])
def create_classroom_submit():
    class_name = request.json['class_name']
    subject = request.json['subject']

    _id, classroom_code = mongo.create_classroom(USER, subject, class_name)
    print _id, classroom_code

    return_data = {'classroom_code':classroom_code}
    return json.dumps({'status':1, 'data':return_data})

@app.route('/_create_homework_submit', methods=['GET', 'POST'])
def create_homework_submit():
    classroom_id = request.json['classroom_id']
    exercise_id = request.json['exercise_id']
    date_set = request.json['date_set']
    date_due = request.json['date_due']
    attempts_required = request.json['attempts_required']
    pupil_list = request.json['pupil_list']
    exclude_include = request.json['exclude_include']

    print exercise_id
    exercise_object = mongo.load_by_id(ObjectId(exercise_id), 'exercises')
    print exercise_object.D
    classroom_object = mongo.load_by_id(ObjectId(classroom_id), 'classrooms')
    print classroom_object.D
    teacher_object = USER
    mongo.create_homework(exercise_object, classroom_object, teacher_object, date_set=date_set, date_due=date_due)

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




if __name__ == '__main__':
    app.run(debug=True)