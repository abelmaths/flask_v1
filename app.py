"""
25th Jan - fix 'wrong answer' section (DONE), add 'answer limit' section (DONE), add basic image functionality (DONE), finish basic teacher/pupil views
1st Feb - add password protection to login (DONE), look into date formats, get basic version on the web (DONE)
8th Feb - 'create homework' page flow for teachers and 'create class' page flow for teachers
15th Feb - add 'create account' / 'signup' / 'demo login' (TBC) functionality
7th March - make it look pretty
Afterwards - consider multiple choice, how to generate images, etc.



"""

from flask import Flask, url_for, render_template, request, session, redirect
#from flask.ext.script import Manager
import json
import mongo
import os
from functools import wraps
reload(mongo)
from mongo_setup import *
from bson.objectid import ObjectId
from id_masker import id_mask
#from flask.ext.wtf import Form
#from wtforms import StringField, SubmitField
#from wtforms.validators import Required

app = Flask(__name__)
app.secret_key = os.environ['APP_SECRET_KEY']
#manager = Manager(app)

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
            return redirect(url_for('login'))
    return wrapper

@app.route('/')
def home():
    if not USER.exists():
        return redirect(url_for('login'))
    if USER.is_teacher():
        return redirect(url_for('teacher_all_exercises'))
    if not USER.is_teacher():
        return redirect(url_for('pupil_all_exercises'))
    else:
        print "WHAT?!!"


@app.route('/instructor/signup')
def create_teacher():
    name = None
    # form = NameForm()
    # if form.validate_on_submit():
    #     name = form.name.data
    #     form.name.data = ''
    #     return render_template('index.html', form=form, name=name)
    return """
    Page to create a teacher via a form
    \nNeed a special school code to prevent kids creating teacher accounts
    \ncreate_user(username, first_name, surname, display_name, is_teacher)
    """


@app.route('/instructor/create_classroom')
@login_required
def create_classroom():
    return """
    Page for a logged in teacher to create a classroom
    \nGiven the entry code when done
    \ncreate_classroom(
        teacher_object, subject_name, yeargroup_name
    )
    """

@app.route('/instructor/set_exercise')
@login_required
def set_exercise():
    return """
    Page for a logged in teacher to create an exercise/homework
    \nSelect their class and the subject
    \ncreate_homework(exercise_object, classroom_object, teacher_object, date_due='2015-12-12')
    """

@app.route('/signup')
def create_pupil():
    return """
    Page to create a pupil via a form
    \ncreate_user(username, first_name, surname, display_name, is_teacher)
    \nNeed to join a classroom in same step so that teacher can connect account
    """

@app.route('/login')
def login():
    # USER = mongo.User({})
    # session['user']=USER.save_to_session()
    session.clear()
    return render_template('login.html')

@app.route('/logout')
def logout():
    """
    Page to logout
    """
    # USER = mongo.User({})
    # session['user']=USER.save_to_session()
    session.clear()
    return render_template('login.html')

@app.route('/join_classroom')
@login_required
def join_classroom():
    return """
    Page for a pupil to join additional classrooms
    \nType in code to join classroom
    """

@app.route('/instructor/my_exercises')
@login_required
def teacher_all_exercises():
    """
    Show grid of all exercises (old and new and due)
    Filterable
    """
    # Redirect pupils to their own page
    if not USER.is_teacher():
        return redirect(url_for('pupil_all_exercises'))

    # Load all submission objects for the pupil
    homeworks = mongo.load_by_arbitrary({'teacher_id':USER.get_id()}, 'homeworks', multiple=True)
    return render_template('instructor_exercises.html', homework_array = homeworks, USER=USER)


@app.route('/instructor/my_students')
@login_required
def teacher_all_pupils():
    """
    Show grid of all students
    \nFilterable (by class)
    """
    # Redirect pupils
    if not USER.is_teacher():
        return redirect(url_for('pupil_all_exercises'))

    pupil_dict = USER.get_my_students_teacher()
    print pupil_dict
    return render_template('instructor_pupils.html', pupil_dict = pupil_dict)

@app.route('/instructor/my_classes')
@login_required
def teacher_all_classes():
    """
    Show grid of all classes
    """
    # Redirect pupils to their own page
    if not USER.is_teacher():
        return redirect(url_for('pupil_all_exercises'))

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
    return render_template('instructor_submissions.html', submission_array = submissions)

@app.route('/instructor/submissions/student/<pupil_id>')
@login_required
def teacher_pupil_progress(pupil_id):
    """
    Show all exercise submissions for the pupil
    """
    submissions = mongo.load_by_arbitrary({'teacher_id':USER.get_id(), 'user_id':pupil_id}, 'submissions', multiple=True)
    return render_template('instructor_submissions.html', submission_array = submissions)

@app.route('/instructor/exercise_preview/<id>')
@login_required
def teacher_exercise_preview():
    return """
    Preview of 1 question per level on the exercise
    """

@app.route('/instructor/student/<username>')
@login_required
def teacher_pupil_summary():
    return """
    (Lower priority)
    \nShow a single pupil's history
    \nAnd stats over time
    \nIf they link to the pupil via a class
    \nGood for parents eve
    """

@app.route('/my_exercises')
@login_required
def pupil_all_exercises():
    """
    Table (or nicer format) if all exercises done and to do
    \nTo do: can click (green) 'do exercise'
    \nDone: can click different button (blue) saying 'revisit'
    """
    # Redirect teachers to their own page
    if USER.is_teacher():
        return redirect(url_for('teacher_all_exercises'))

    # Load all submission objects for the pupil
    submissions = mongo.load_by_arbitrary({'user_id':USER.get_id()}, 'submissions', multiple=True)
    return render_template('my_exercises.html', submission_array = submissions)

@app.route('/my_progress')
@login_required
def pupil_progress():
    return """
    My progress - topline stats, questions attempted/answered, a chart, medals
    """

@app.route('/exercise_tester')
@login_required
def exercise_tester():
    return render_template('level_tester_full_exercise.html')

@app.route('/exercise/<homework_id>')
@login_required
def exercise(homework_id):
    """
    Load the exercise (by homework id)
    Retrieve level list from homework id and send to javascript via jinja
    The html will then run the level page from there (by loading each level one by one)
    """
    # Load submission entry to find status of submission (not started, in progress, complete (i.e. practice))
    print "Loading exercise page"
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

@app.route('/password_reset')
@login_required
def password_reset():
    return """
    Teacher can reset a student's password
    """

@app.route('/password_change')
@login_required
def password_change():
    return """
    Teacher or pupil can change their own password
    """

@app.route('/hello')
def hello(name=None):
    return render_template('hello.html', name=name)

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
            return json.dumps({'status':0, 'data':'Password does not match'})
    else:
        return json.dumps({'status':0, 'data':'Username does not exist'})

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
        return json.dumps({'status':0, 'data':'Query did not return a level_dict'})

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
    return json.dumps({'status':1, 'data':'Saved data successfully.'})


if __name__ == '__main__':
    app.run(debug=True)