import io
import os
import pandas as pd
import pysftp


class SFTP:
    def __init__(self, host, username, private_key, private_key_pass):
        self.host = host
        self.username = username
        self.private_key = private_key
        self.private_key_pass = private_key_pass
        self.cnopts = pysftp.CnOpts()
        self.cnopts.hostkeys = None

    def put_file(self, local_path, remote_path):
        with pysftp.Connection(host=self.host, username=self.username, private_key=self.private_key,
                               private_key_pass=self.private_key_pass, cnopts=self.cnopts) as connection:
            connection.put(local_path, remote_path)

    def get_file(self, file_name):
        with pysftp.Connection(host=self.host, username=self.username, private_key=self.private_key,
                               private_key_pass=self.private_key_pass, cnopts=self.cnopts) as connection:
            with connection.cd(self.remote_base_path):
                connection.get(file_name, self.local_base_path)

    def make_dir(self, dir_name):
        with pysftp.Connection(host=self.host, username=self.username, private_key=self.private_key,
                               private_key_pass=self.private_key_pass, cnopts=self.cnopts) as connection:
            with connection.cd(self.remote_base_path):
                try:
                    connection.mkdir(dir_name)
                except OSError:
                    error_message = '%s already exists' % (self.remote_base_output + dir_name)
                    raise OSError(error_message)

    def list_dir(self, remote_path_from_base=''):
        with pysftp.Connection(host=self.host, username=self.username, private_key=self.private_key,
                               private_key_pass=self.private_key_pass, cnopts=self.cnopts) as connection:
            with connection.cd(self.remote_base_path + remote_path_from_base):
                return connection.listdir()

    def dataframe_to_local_csv(self, df, file_location='StringIO', file_prefix=None, give_header=False,
                               save_indices=False,
                               separator=','):  # (to be) acceptable input for file_location: StringIO, absolute path, if is directory: auto assign not existing file
        data_to_write = io.StringIO()
        number_of_rows = df.shape[0]
        take = 0
        skip = 50000
        while take < number_of_rows:
            pd.DataFrame(df[take:take + skip]).to_csv(data_to_write, sep=separator, header=give_header,
                                                      index=save_indices)
            take += skip
        data_to_write.seek(0)
        if file_location == 'StringIO':
            return data_to_write
        elif os.path.isabs(file_location) and os.path.isdir(file_location):
            if file_prefix is None:
                raise ValueError(
                    "MonetDB.dataframe_to_csv(): specified file_path is directory: set file_prefix for auto write")
            i = 0
            while '%s%s.csv' % (file_prefix, i) in os.listdir(file_location):
                i += 1
            else:
                file_name = file_location + '%s%s.csv' % (file_prefix, i)
                file = open(file_name, 'w')
                file.write(data_to_write.getvalue())
                file.close()
                return file_name
        elif os.path.isabs(file_location):
            file = open(file_location, 'w')
            file.write(data_to_write.getvalue())
            file.close()
        else:
            raise ValueError(
                "MonetDB.dataframe_to_csv(): expected file_path: 'StringIO' or absolute directory or file path")
