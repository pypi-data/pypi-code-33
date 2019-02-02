import mechanicalsoup
import json
import re
import art
import sys
import getpass




class ICIT:
    def __init__(self, apiMode=False):
        self.browser = mechanicalsoup.StatefulBrowser()
        self.result_all = {}
        self.user_info = {}
        self.grade_list = []
        self.username = ''
        self.status = False
        self.apiMode = apiMode
        if not self.apiMode:
            self.welcome()

    def welcome(self):
        art.tprint("ICIT")
        print("*----- Welcome to ICIT Grade Reporter -----*")


    def current_page(self):
        print("Page:", self.browser.get_url())

    def remove_xa(self, text):
        return text.replace("\xa0", "")

    def check_page(self, page):
        if (page == "LOGIN"):
            if (self.current_page() == "http://grade-report.icit.kmutnb.ac.th/auth/signin"):
                return False
            return True

    def authentication(self, userName=None, passWord=None):
        self.icit_site()
        if userName and passWord:
            username = userName
            password = passWord
        else:
            username = input("Username: ")
            password = getpass.getpass('Password: ')

        self.browser.select_form('form[action="http://grade-report.icit.kmutnb.ac.th/auth/signin"]')

        self.browser["username"] = username
        self.browser["password"] = password

        # print(browser.get_current_form().print_summary())

        self.browser.submit_selected()

        self.status = self.check_page("LOGIN")
        if self.status:
            self.username = username
        return self.status

    def get_grade_information(self):
        page = self.browser.get_current_page()
        # print(page)

        li = page.find_all("li", class_="navbar-brand")
        # print(li)
        std_number = re.search(r"(?<!\d)\d{13}(?!\d)", li[1].text).group(0)

        self.user_info["ชื่อ-นามสกุล"] = li[1].text.replace("ชื่อ", "").replace("รหัสนักศึกษา", "").replace(std_number, "").strip()
        self.user_info["เลขประจำตัว"] = std_number
        tr = page.find_all("tr")

        # grade_list = []

        for r in tr[1:-1]:
            ro = r.find_all("td")
            # print(ro)
            grade_dict = {}
            grade_dict["รหัสวิชา"] = ro[0].text
            grade_dict["ตอนเรียน"] = ro[1].text
            grade_dict["ชื่อวิชา"] = ro[2].text
            grade_dict["หน่วยกิต"] = ro[3].text
            grade_dict["เกรด"] = ro[4].text
            self.grade_list.append(grade_dict)
            print("*------Get info for subject:", ro[2].text, "SUCCEED ------*")

        self.grade_list.append({"เกรดเฉลี่ย (เฉพาะเกรดที่แสดงไว้)": tr[-1].find_all("td")[-1].text})

        # print(grade_list)


    def get_current_grade(self):
        if self.status:
            self.icit_site(logged_in=True)
            # self.browser.follow_link("grade.jsp")
        else:
            if not self.apiMode:
                print("*----- Unauthorized: Please log in -----*")
            while self.authentication():
                pass
            self.icit_site(logged_in=True)


        self.get_grade_information()
        # print(tables[::2])
        self.result_all["รายละเอียดผู้ใช้งาน"] = self.user_info
        self.result_all["ผลการเรียน"] = self.grade_list


    def icit_site(self, logged_in=False):
        if not logged_in:
            self.browser.open("http://grade-report.icit.kmutnb.ac.th/auth/signin")
        else:
            self.browser.open("http://grade-report.icit.kmutnb.ac.th/auth/data")



    def generate_json(self):

        with open('grade_icit_{}.json'.format(self.username), 'w+', encoding='utf8') as outfile:
            json.dump(self.result_all, outfile, indent=4, ensure_ascii=False)

        if not self.apiMode:
            print("*----- Generate JSON report complete for user => {} -----*".format(self.username))

    def json(self):
        return json.dumps(self.result_all, ensure_ascii=False).encode("utf8")


if __name__ == "__main__":
    icit = ICIT()
    if icit.authentication():
        icit.get_current_grade()
        icit.generate_json()