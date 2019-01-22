import flatast
import urllib3
from bs4 import BeautifulSoup
import os
import re
from datetime import datetime
from flatast.issue_tracker import IssueTracker
from flatast.patch import Patch
import sys
import sqlite3

def main():
    conn = sqlite3.connect('gitlog.db')
    c = conn.cursor()

    # Create table
    c.execute('''CREATE TABLE IF NOT EXISTS issues (id integer primary key, summary text, description text, type text, priority text, status text, owner text, creator text, is_private integer, create_date datetime, update_date datetime)''')

    # Insert a row of data
    c.execute("create table IF NOT EXISTS patches(id integer primary key, issue_id integer, time datetime, touched_files text, content text)")

    # Save (commit) the changes
    conn.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()

    date_format = '%Y-%m-%dT%H:%M:%S'
    http = urllib3.PoolManager()
    urllib3.disable_warnings()

    #project = 'LUCENE'
    #issue_id = 8575
    #root_url = 'https://issues.apache.org/jira/browse/'
    #issue_url = os.path.join(root_url, '{}-{}'.format(project,issue_id))

    issue_url = sys.argv[1]
    a = issue_url.split("/")
    project = a[5]
    f=1
    t=10000
    b = project.split("-")
    if len(b) > 0:
        project = b[0]
        if len(b) > 1:
           f = int(b[1])
           if len(b) > 2:
              t = int(b[2])
    issue_url = a[0] + "/" + a[1] + "/" + a[2] + "/" + a[3] + "/" + a[4] + "/" + project

    for issue_id in range(f, t):
        print("%04d" % issue_id)
        tracker = IssueTracker()
        tracker.id = issue_id
        if tracker.issue_exists_in_database():
            continue
        #print("%s-%d" % (issue_url, issue_id))

        response = http.request('GET', "%s-%d" % (issue_url, issue_id))
        web_data = BeautifulSoup(response.data,features="lxml")
        desc = web_data.find(id="description-val")

        if desc is None:
            continue

        summary_raw = web_data.title.string
        summary = summary_raw.replace("- ASF JIRA","").replace("[{}-{}]".format(project,issue_id),"").strip()
        # print('the summary of the issue is: {}'.format(summary))
        tracker.summary = summary

        description = web_data.find(id="description-val").get_text().strip()
        # print('the description of the issue is: {}'.format(description))
        tracker.description = description

        if web_data.find(id = "issuedetails") is None:
            continue
        for one_node in web_data.find(id = "issuedetails").find_all('div'):
                key_value_pair = one_node.get_text().split(':')
                if not len(key_value_pair) == 2:
                        break
                key = key_value_pair[0].strip()
                value = key_value_pair[1].strip()
                if hasattr(tracker,key.lower()):
                        setattr(tracker,key.lower(),value.lower())

        create_time_str = web_data.find(id='datesmodule').find(id='created-val').time['datetime']

        tracker.create_date = datetime.strptime(create_time_str[:-5], date_format)

        update_time_str = web_data.find(id='datesmodule').find(id='updated-val').time['datetime']

        tracker.update_date = datetime.strptime(update_time_str[:-5], date_format)

        if web_data.find(id = "file_attachments") is None:
            continue
        for node in web_data.find(id = 'file_attachments').find_all('div'):
                patch = Patch()
                patch.id = int(node.parent['data-attachment-id'])
                if patch.patch_exists_in_database():
                    continue
                patch.url = 'https://issues.apache.org'+node.a['href']
                patch.time = datetime.strptime(node.parent.time['datetime'][:-5],date_format)
                patch_response = http.request('GET', patch.url)
                patch_data = BeautifulSoup(patch_response.data,features="lxml")
                patch.content = patch_data.get_text()
                matched_lines = [line for line in patch.content.split('\n') if "diff" in line]
                for line in matched_lines:
                        strs = line.split(' ')
                        file_name = strs[-1][1:]
                        patch.touched_files.append(file_name)
                tracker.patch_list.append(patch)

        tracker.save_to_database()

if __name__ == "__main__":
    main()
