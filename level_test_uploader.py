ALLOWED_EXTENSIONS = set(['txt', 'csv'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def test_uploader(variables, skeleton, exercise_title_visible, exercise_description):
    if skeleton and allowed_file(skeleton.filename):
        data = skeleton.stream.readlines()[0]
        lines =  data.split('\r')
        output = {}
        for line in lines:
            # Get into correct format
            cells = line.split(',')
            Key = cells[0]
            Value = ','.join(cells[1:]).strip('"')
            # From other script
            if Key in output:
                output[Key].append(Value)
            else:
                output[Key] = [Value]
    level_dict = output
    if variables and allowed_file(variables.filename):
        data = variables.stream.readlines()[0]
        lines = data.split('\r')
        list_of_dicts = []
        counter = 0
        for line in lines:
            # Get into correct format
            row = line.split(',')
            if counter==0:
                heading = row
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
    level_dict['variables'] = list_of_dicts
    import create_all_exercises as Q
    level_hash = Q.generate_hash(level_dict)
    exercise_dict = {
        'exercise_name_unique':'Test exercise unique',
        'exercise_title_visible':exercise_title_visible,
        'exercise_description_visible':exercise_description,
        'question_attempts_required':'5',
        'level_ids':[]
    }
    exercise_dict['level_ids'].append(level_hash)
    Q.save_hash_and_dict_to_database(_dict = level_dict, _hash = level_hash, db_name='levels')
    exercise_hash = Q.generate_hash(exercise_dict)
    Q.save_hash_and_dict_to_database(_dict = exercise_dict, _hash = exercise_hash, db_name='exercises')