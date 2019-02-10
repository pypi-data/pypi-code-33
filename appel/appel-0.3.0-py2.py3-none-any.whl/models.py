from collections import namedtuple

User = namedtuple("User", "name, login, gtID, canvasID")
Attendance = namedtuple("Attendance", "location, date, notes, timestamp")
