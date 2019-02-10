import requests
from .models import User

course_url = "https://gatech.instructure.com/api/v1/courses/%s/"
assignment_url = "assignments/%s/"

user_search = "search_users"
assignment_users = "gradeable_students"
update_grades = "submissions/update_grades"
update_grade = "submissions/%s"

def getPaginatedItems(url, req_args):
    results = []

    nextUrl = requests.get(url, **req_args).url

    while nextUrl is not None:
        # Get the data
        r = requests.get(nextUrl, **req_args)

        data = r.json()

        for item in data:
            results.append(item)

        # Next page
        if "next" in r.links:
            nextUrl = r.links["next"]["url"]
        else:
            nextUrl = None

    return results

def getUsersInCourse(token, course):
    users = []

    url = (course_url % str(course)) + user_search
    payload = {"per_page": 1000}
    headers = {'Authorization': 'Bearer %s' % token}

    data = getPaginatedItems(url, {"params": payload, "headers": headers})

    for user in data:
        print(user)
        users.append(User(user["name"], user["login_id"], user["sis_user_id"], user["id"]))

    return users

def getUsersForAssignment(users, token, assignment, course):
    url = (course_url % str(course)) + (assignment_url % assignment) + assignment_users
    payload = {"per_page": 1000}
    headers = {'Authorization': 'Bearer %s' % token}

    data = getPaginatedItems(url, {"params": payload, "headers": headers})

    ids = {x['id'] for x in data}

    return [x for x in users if x.canvasID in ids]


def setUserAssignmentScoresWithComments(token, course, assignment, grades):
    #url = (course_url % str(course)) + (assignment_url % assignment) + update_grades
    #headers = {'Authorization': 'Bearer %s' % token}
    #data = {}

    #for user, score, comments in grades:
    #    data["grade_data[%s][posted_grade]" % user.canvasID] = "%d%%" % score
    #    data["grade_data[%s][text_comment]" % user.canvasID] = comments

    #r = requests.post(url, headers=headers, data=data)
    #return r.status_code

    url = (course_url % str(course)) + (assignment_url % assignment) + update_grade
    headers = {'Authorization': 'Bearer %s' % token}

    success = 0
    failure = 0
    for user, score, comments in grades:
        user_url = url % user.canvasID
        data = {"submission[posted_grade]": "%d%%" % score, "comment[text_comment]": comments}

        r = requests.put(user_url, headers=headers, data=data)

        success += 1 if r.status_code == 200 else 0
        failure += 0 if r.status_code == 200 else 1
        #print("User %s, score %d%% submitted with status code %d" % (user.name, score, r.status_code))

    return success, failure
