import os
import time
import requests
from . import util
from . conf import Config


config = Config()


class DataReader(Config):

    def _get(self, subject_name, year_start, year_end):

        subject = util.db_retrieve(db_engine=self.db_engine, query=util.GetSubject, query_param=subject_name)
        paths = util.db_retrieve(db_engine=self.db_engine, query=util.GetPath, query_param=subject)
        header = util.db_retrieve(db_engine=self.db_engine, query=util.GetHeaderPath, query_param=subject)

        paths = [p for p in paths if year_start <= p.Path.year <= year_end]

        save_dir = os.path.join(self.data_dir, subject.directory_name)
        util.check_dir(save_dir)

        for p in paths:
            url = p.Url.domain_name + p.Path.path
            util.print_to_shell("Getting data file from {}".format(url))
            req = requests.get(url)
            util.save_zip(req.content, save_dir)

            if subject_name == "candidate master":
                # janky fix to all candidate master files being named 'cn.txt' LOL
                fix = url.replace('.zip', '')
                filename = 'cn' + str(p.Path.year) + '.txt'
                os.rename(os.path.join(save_dir, 'cn.txt'), os.path.join(save_dir, filename))
            elif subject_name == "contributions to candidates":
                # janky fix to all contribution to candidate files being named 'itpas2.txt' LOL
                fix = url.replace('.zip', '')
                filename = 'itpas' + str(p.Path.year) + '.txt'
                os.rename(os.path.join(save_dir, 'itpas2.txt'), os.path.join(save_dir, filename))

            time.sleep(5)

        url = header.Url.domain_name + header.Path.path
        util.print_to_shell("Getting header file from {}".format(url))
        util.get_header(url, save_dir, 'header.txt')

        util.print_to_shell("{} data retrieval complete.".format(subject_name))

    def get_pac_summary(self, start, end):
        self._get(subject_name="pac summary", year_start=start, year_end=end)

    def get_candidate_master(self, start, end):
        self._get(subject_name="candidate master", year_start=start, year_end=end)

    def get_contributions_to_candidates(self, start, end):
        self._get(subject_name="contributions to candidates", year_start=start, year_end=end)
