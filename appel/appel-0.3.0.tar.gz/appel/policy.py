GRADE_SPLITTER = " ----------------------------------- "

def getPercentScore(attendance, absence_limit, absence_penalty_past_limit):
    score = 100

    absences = sum(1 for x in attendance.values() if x is None)
    more_than_allowed = absences - absence_limit

    if more_than_allowed > 0:
        score -= more_than_allowed * absence_penalty_past_limit

    return max(score, 0)

def getComments(attendance):
    comments = []

    for date in sorted(attendance.keys()):
        entry = attendance[date]
        if entry is None:
            comments.append("%s: ABSENT" % date)
        else:
            comments.append("%s: PRESENT - %s - Notes: %s" % (date, entry.location, entry.notes))

    return GRADE_SPLITTER.join(comments)
