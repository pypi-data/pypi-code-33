from collections import defaultdict

import bs4 as BeautifulSoup

from yalesnotes.src.utils.iterators import grouper


def parse_student_marks(content):
    html_tree = BeautifulSoup.BeautifulSoup(content, "html.parser")
    lines = html_tree.find_all("td", attrs={"class": "Ligne"})
    lines_text = [l.text for l in lines]
    groups = grouper(lines_text, 3)

    user_marks = defaultdict(dict)
    for matiere, examen, mark in groups:
        user_marks[matiere][examen] = mark

    lectures_name = dict()
    all_lectures = \
        html_tree.find("table", attrs={"class": "Table"}).find_all("tr")[1:]

    for lecture in all_lectures:
        td = lecture.find_all("td")
        lectures_name[td[1].text.strip() + "-" + td[2].text.strip()] = \
            td[3].text[1:-1]

    return user_marks, lectures_name


if __name__ == '__main__':
    pass
