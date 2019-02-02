import mechanicalsoup
import json
import re
import art
import sys
import getpass




class KLOGIC:
    def __init__(self, apiMode=False):
        self.browser = mechanicalsoup.StatefulBrowser()
        self.result_all = dict()
        self.user_info = dict()
        self.grade_info = list()
        self.term_info = dict()
        self.student_bio = dict()
        self.username = ''
        self.status = False
        self.apiMode = apiMode
        if not self.apiMode:
            self.welcome()

    def welcome(self):
        art.tprint("KLOGIC")
        print("*----- Welcome to KLOGIC GPA Reporter -----*")


    def current_page(self):
        print("Page:", self.browser.get_url())

    def remove_xa(self, text):
        return text.replace("\xa0", "")

    def authentication(self, userName=None, passWord=None):
        self.klogic_site()
        if userName and passWord:
            username = userName
            password = passWord
        else:
            username = input("Username: ")
            password = getpass.getpass('Password: ')
        # password = input("Password: ")

        self.browser.select_form('form[action="/kris/index.jsp"]')

        self.browser["username"] = username
        self.browser["password"] = password

        # print(browser.get_current_form().print_summary())

        self.browser.submit_selected()

        page = self.browser.get_current_page()
        td_all = page.find_all("td", align="center", colspan="2")
        td_all_filter = [texts.text.strip() for texts in td_all]
        # print(td_all_filter)
        if ('รหัสผ่านไม่ถูกต้อง' in td_all_filter):
            return False

        self.username = username
        self.status = True
        return True

    def get_user_information(self, tables):

        user_td = tables[0].find_all("td")
        # print(user_td)
        self.user_info["ผู้ใช้งาน"] = re.search(r"(?<!\d)\d{13}(?!\d)", user_td[0].text).group(0)
        self.user_info["เวลา"] = user_td[1].text.replace("\xa0", "")
        self.user_info["ภาค/ปีการศึกษาปัจจุบัน"] = re.search(r"(?<!\d)\d{1,2}/\d{4}(?!\d)", user_td[2].text).group(0)
        self.user_info["ภาค/ปีการศึกษาที่ทำงานอยู่"] = re.search(r"(?<!\d)\d{1,2}/\d{4}(?!\d)", user_td[3].text).group(0)
        # print(user_info)

        tables = tables[1:]

        user_td2 = tables[0].find_all("td")
        # print(user_td2)
        self.user_info["เลขประจำตัว"] = re.search(r"(?<!\d)\d{13}(?!\d)", user_td2[0].text).group(0)
        self.user_info["ชื่อ"] = user_td2[1].text.replace("\xa0", "").replace("ชื่อ", "").replace("\r\n", "")

        user_td3 = tables[1].find_all("td")
        # print(user_td3)

        self.user_info["สาขา"] = user_td3[0].text.replace("สาขา", "").replace("\xa0", "")
        self.user_info["ภาควิชา"] = user_td3[1].text.replace("ภาควิชา", "").replace("\xa0", "")
        self.user_info["คณะ"] = user_td3[2].text.replace("คณะ", "").replace("\xa0", "")
        
        if not self.apiMode:
            print("*----- Get User information SUCCEED -----*")

    def get_grade_information(self, tables):
        # print("Grade Tables:", tables)
        for tb in tables:
            # print(tb)
            # break
            first_term = tb
            # print(first_term)
            ft_tr = first_term.find_all("tr")
            # print(ft_tr[2])
            # print(ft_tr[1:])
            ft = ft_tr[0].text.replace("\xa0", "")
            term_info = dict()
            term_info[ft] = {"รายวิชา": []}
            self.term_info[ft] = {"รายวิชา": []}
            # term_info = [{ft: {"รายวิชา": []}}]

            for tr in ft_tr[2:]:
                try:
                    ft_tr2_td = tr.find_all("td")
                    # print(ft_tr2_td)
                    course_info = {}
                    course_id = re.search(r"(?<!\d)\d{9}(?!\d)", ft_tr2_td[0].text).group(0)
                    course_info["รหัสวิชา"] = course_id
                    course_info["ชื่อวิชา"] = ft_tr2_td[0].text.replace(course_id, "").replace("\xa0", "").strip()
                    course_info["หน่วยกิต"] = ft_tr2_td[1].text.strip()
                    course_info["ตอนเรียน"] = ft_tr2_td[2].text.strip()
                    course_info["เกรด"] = ft_tr2_td[3].text.strip()
                    # print(course_info)
                    term_info[ft]["รายวิชา"].append(course_info)
                    self.term_info[ft]["รายวิชา"].append(course_info)
                    # print(term_info)
                except:
                    # print(tr.find_all("td"))
                    result = tr.find_all("td")
                    # print(result)
                    result_first_row = result[0].find_all("td")
                    # print(result_first_row[6:])
                    result_first_row = result_first_row[6:]
                    term_info[ft]["ประจำภาค"] = {"คะแนนฉลี่ย": self.remove_xa(result_first_row[0].text),
                                                 "หน่วยกิตที่ลง": self.remove_xa(result_first_row[1].text),
                                                 "หน่วยกิตที่ได้": self.remove_xa(result_first_row[2].text),
                                                 "แต้มระดับคะแนน": self.remove_xa(result_first_row[3].text)}
                    self.term_info[ft]["ประจำภาค"] = {"คะแนนฉลี่ย": self.remove_xa(result_first_row[0].text),
                                                 "หน่วยกิตที่ลง": self.remove_xa(result_first_row[1].text),
                                                 "หน่วยกิตที่ได้": self.remove_xa(result_first_row[2].text),
                                                 "แต้มระดับคะแนน": self.remove_xa(result_first_row[3].text)}
                    result_first_row = result_first_row[5:]
                    # print(result_first_row)
                    term_info[ft]["สะสม"] = {"คะแนนฉลี่ย": self.remove_xa(result_first_row[0].text),
                                             "หน่วยกิตที่ลง": self.remove_xa(result_first_row[1].text),
                                             "หน่วยกิตที่ได้": self.remove_xa(result_first_row[2].text),
                                             "แต้มระดับคะแนน": self.remove_xa(result_first_row[3].text)}
                    self.term_info[ft]["สะสม"] = {"คะแนนฉลี่ย": self.remove_xa(result_first_row[0].text),
                                             "หน่วยกิตที่ลง": self.remove_xa(result_first_row[1].text),
                                             "หน่วยกิตที่ได้": self.remove_xa(result_first_row[2].text),
                                             "แต้มระดับคะแนน": self.remove_xa(result_first_row[3].text)}
                    term_info[ft]["สถานภาพ"] = result[-1].text.strip()
                    self.term_info[ft]["สถานภาพ"] = result[-1].text.strip()
                    break
            # print(term_info)
            if not self.apiMode:
                print("*------Get info for TERM:", ft, "SUCCEED ------*")
            self.grade_info.append(term_info)


    def get_information(self):
        if self.status:
            self.klogic_site()
            self.browser.follow_link("grade.jsp")
        else:
            if not self.apiMode:
                print("*----- Unauthorized: Please log in -----*")
            while self.authentication():
                pass
            self.browser.follow_link("grade.jsp")
        # current_page()
        page = self.browser.get_current_page()
        # print(page)

        tables = page.find_all("table")
        tables = tables[7:]

        self.get_user_information(tables)

        # print(user_info)

        # for td in tables[0]:
        #     print(td)
        # print(td.find("td"))
        # user_info[]

        tables = tables[3:]
        tables = tables[::2]

        self.get_grade_information(tables)
        # print(tables[::2])
        self.result_all["รายละเอียดผู้ใช้งาน"] = self.user_info
        # self.result_all["ผลการเรียน"] = self.grade_info
        self.result_all["ผลการเรียน"] = self.term_info

    def get_bio(self):
        if self.status:
            self.klogic_site()
            self.browser.follow_link("student_bio.jsp")
        else:
            if not self.apiMode:
                print("*----- Unauthorized: Please log in -----*")
            while self.authentication():
                pass
            self.browser.follow_link("student_bio.jsp")

        page = self.browser.get_current_page()
        tables = page.find_all("table", align="center", width="100%")
        first_table = tables[0]
        first_table_tr = first_table.find_all("tr")
        for row in first_table_tr[1:]:
            row_td = row.find_all("td")
            self.student_bio[row_td[0].text.strip()] = row_td[1].text.strip()
            # print("{}: {}".format(row_td[0].text.strip(), row_td[1].text.strip()))

        second_table = tables[1]
        second_table_tr = second_table.find_all("tr")
        for row in second_table_tr:
            row_td = row.find_all("td")
            self.student_bio[row_td[0].text.strip()] = row_td[1].text.strip()
            # print("{}: {}".format(row_td[0].text.strip(), row_td[1].text.strip()))

        third_table = tables[2]
        third_table_tr = third_table.find_all("tr")
        for row in third_table_tr[1:]:
            row_td = row.find_all("td")
            self.student_bio[row_td[0].text.strip()] = row_td[1].text.strip()
            # print("{}: {}".format(row_td[0].text.strip(), row_td[1].text.strip()))

        forth_table = tables[3]
        forth_table_tr = forth_table.find_all("tr")
        # print(forth_table_tr)
        for row in forth_table_tr[1:]:

            row_td = row.find_all("td")
            # print(row_td)
            # if(row_td[0].text == ""):
            #     self.student_bio["ที่อยู่(ต่อ)"] = row_td[1].text.strip()
            # else:
            # print("Length:", len(row_td))
            if len(row_td) == 6:
                self.student_bio[row_td[0].text.strip()] = row_td[1].text.strip()
                self.student_bio[row_td[2].text.strip()] = row_td[3].text.strip()
                self.student_bio[row_td[4].text.strip()] = row_td[5].text.strip()
            else:
                if(row_td[0].text == ""):
                    self.student_bio["ที่อยู่(ต่อ)"] = row_td[1].text.strip()
                else:
                    self.student_bio[row_td[0].text.strip()] = row_td[1].text.strip()


        fifth_table = tables[4]
        fifth_table_tr = fifth_table.find_all("tr")
        for row in fifth_table_tr:
            row_td = row.find_all("td")

            self.student_bio[row_td[0].text.strip()] = row_td[1].text.strip()


        sixth_table = tables[5]
        sixth_table_tr = sixth_table.find_all("tr")
        # print(sixth_table_tr[0])

            # print("ROW:",row)
        row_td = sixth_table_tr[0].find_all("td")
        # print(row_td)
        self.student_bio[row_td[0].text.strip()] = row_td[1].text.strip()
            # print("{}: {}".format(row_td[0].text.strip(), row_td[1].text.strip()))
        del self.student_bio[""]
        self.result_all["ประวัตินักศึกษา"] = self.student_bio

        if not self.apiMode:
            print("*-------- Get Student Bio SUCCEED -------*")

    def gradedb(self):
        if self.term_info:
            import pandas as pd
            db = pd.DataFrame(columns=['Course Id', 'Course Name', 'Year', 'Semester', 'Credit', 'Section',
                                       'Grade', 'Grade(Score)'])
            grade_table = {
                'A': 4,
                'B+': 3.5,
                'B': 3,
                'C+': 2.5,
                'C': 2,
                'D+': 1.5,
                'D': 1,
                'F': 0
            }
            for term in self.term_info:
                year_split = term.split(" ")  # Extract the selected term
                year = year_split[1]  # Get the year
                semester = year_split[3]  # Get the semester
                for row in self.term_info[term]["รายวิชา"]:
                    db = db.append({'Course Id': row['รหัสวิชา'], 'Course Name': row['ชื่อวิชา'], 'Year': year,
                               'Semester': semester, 'Credit': row['หน่วยกิต'], 'Section': row['ตอนเรียน'],
                               'Grade': row['เกรด'], 'Grade(Score)': grade_table[row['เกรด']]}, ignore_index=True)

            return db
        else:
            if not self.apiMode:
                print("No term information!")
                print("Getting information...")
            self.get_information()
            return self.gradedb()

    def klogic_site(self):
        self.browser.open("http://klogic2.kmutnb.ac.th:8080/kris/index.jsp")

    def icit_site(self):
        self.browser.open("http://grade-report.icit.kmutnb.ac.th/auth/signin")

    def generate_json(self):

        with open('report_{}.json'.format(self.username), 'w+', encoding='utf8') as outfile:
            json.dump(self.result_all, outfile, indent=4, ensure_ascii=False)

        if not self.apiMode:
            print("*----- Generate JSON report for user => {} COMPLETE -----*".format(self.username))
    
    def json(self):
        return json.dumps(self.result_all, ensure_ascii=False).encode("utf8")

# if __name__ == "__main__":
#     klogic = KLOGIC()
#     if klogic.authentication():
#         klogic.get_bio()
#         klogic.get_information()
        # klogic.gradedb()
        # klogic.generate_json()
