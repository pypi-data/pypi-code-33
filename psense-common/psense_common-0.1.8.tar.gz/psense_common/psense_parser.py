import re
import pandas as pd
import numpy as np
import os
import pytz
from datetime import datetime
import json


def is_float(val):
    try:
        # if this isn't a numeric value, we'll cause a valueerror exception
        float(val)
        # don't allow NaN values, either.
        if pd.isnull(val):
            return False
        return True
    except:
        return False


''' classes '''


class PSenseParser:
    def __init__(self, filename='', exp_config=None, debugmode=False):
        self.debugmode = debugmode
        self.valid_types = ['BWII', 'PSHIELD', 'PSENSE', 'VFP', 'EXPLAIN',
                            'WEBAPP', 'WEB1CHAN', 'EMSTAT_EXPORT', 'EMSTAT_PSESSION']
        self.header_text = {
            'BWII': 'DATETIME, RECORDNUM,',
            'PSHIELD': 'Potentiostat Shield',
            'PSENSE': 'BWIIData',
            'VFP': 'VFP600',
            'EXPLAIN': 'EXPLAIN',
            'WEBAPP': 'timestamp,isig,fisig',
            'WEB1CHAN': 'timestamp,signal1,vout1,c_signal1',
            'EMSTAT_EXPORT': 'Date and time:,',
            'EMSTAT_PSESSION': 'PalmSens.DataFiles.SessionFile'
        }
        self.delimiter = {
            'BWII': ',',
            'PSHIELD': ',',
            'PSENSE': ',',
            'VFP': '\t',
            'EXPLAIN': '\t',
            'WEBAPP': ',',
            'WEB1CHAN': ',',
            'EMSTAT_EXPORT': ',',
            'EMSTAT_PSESSION': 'JSON'
        }
        self.loc_timestamp = {
            'BWII': 0,
            'PSHIELD': 1,
            'PSENSE': 0,
            'VFP': None,
            'EXPLAIN': 0,
            'WEBAPP': 0,
            'WEB1CHAN': 0,
            'EMSTAT_EXPORT': 0,
            'EMSTAT_PSESSION': None
        }
        self.loc_vout = {
            'BWII': [3, 4, 8, 9],
            'PSHIELD': None,
            'PSENSE': [1, 3],
            'VFP': 0,
            'EXPLAIN': 1,
            'WEBAPP': None,
            'WEB1CHAN': 2,
            'EMSTAT_EXPORT': None,
            'EMSTAT_PSESSION': None
        }
        self.loc_isig = {
            'BWII': [2, 7],
            'PSHIELD': 2,
            'PSENSE': [2, 4],
            'VFP': 1,
            'EXPLAIN': 2,
            'WEBAPP': 1,
            'WEB1CHAN': 1,
            'EMSTAT_EXPORT': None,
            'EMSTAT_PSESSION': None
        }
        self.num_channels = {
            'BWII': 2,
            'PSHIELD': 1,
            'PSENSE': 2,
            'VFP': 1,
            'EXPLAIN': 1,
            'WEBAPP': 1,
            'WEB1CHAN': 1,
            'EMSTAT_EXPORT': 1,
            'EMSTAT_PSESSION': 1
        }

        # what's the current offset between local and UTC?
        # assumes things are collected in PST/PDT
        self.local = pytz.timezone("America/Los_Angeles")
        self.time_offset = datetime.now(self.local).utcoffset()

        self.source = None
        self.data = None
        self.name = filename
        self.config = exp_config
        self.vout = None
        self.we_count = 1

    def force_source(self, source):
        if source in self.valid_types:
            self.source = source
            self.we_count = self.num_channels[source]
        else:
            raise IOError('Invalid source ({}). Must be in list: {}'.format(
                source, self.valid_types))

    def identify_file_source(self, fpath=''):
        for cur in self.valid_types:
            if self.find_header_text(fpath, self.header_text[cur]):
                self.source = cur
                self.we_count = self.num_channels[cur]
                return cur

        self.source = None
        return None

    def parse_record(self, row):
        row = row.split(self.delimiter[self.source])
        if self.loc_timestamp[self.source] is not None:
            timestamp = row[self.loc_timestamp[self.source]]
        else:
            timestamp = datetime.now(self.local)

        if self.loc_vout[self.source] is not None:
            vout = [float(row[x]) for x in self.loc_vout[self.source]]
        else:
            vout = None

        isig = [float(row[x]) for x in self.loc_isig[self.source]]

        if self.we_count == 1:
            isig = isig[0]
            vout = vout[0]

        # custom modifications for specific source types
        if self.source == 'VFP':
            isig = isig * 1e9

        elif self.source == 'BWII':
            # KLUDGE:  BWII hardware v12011 uses an arbitrary timestamp. For real-time purposes, just use the current time.
            timestamp = datetime.now().isoformat('T')
            # convert Vout = Vw - Vr, converted to volts.
            vout = [(vout[0] - vout[1]) / 1000, (vout[2] - vout[3]) / 1000]

        elif self.source == 'PSHIELD':
            timestamp = pd.to_pydatetime(
                timestamp, unit='s') - self.time_offset

        elif self.source == 'WEBAPP':
            timestamp = timestamp.replace(' ', 'T')

        if vout is None and self.vout is not None:
            vout = self.vout

        if self.debugmode:
            print('[PSenseParser][parse_record] data: {}'.format(
                [timestamp, vout, isig]))
        return [timestamp, vout, isig]

    def load_rawfile(self, fname, origin_timestamp, origin_is_end):
        self.data = None

        if self.debugmode:
            print('[PSenseParser][load_rawfile] {}'.format(
                [fname, origin_timestamp, origin_is_end]))

        if self.source == 'PSHIELD':
            data, header = self.read_variable_header_file(
                fname,
                "Sample Count",
                sep=",",
                skiprows=[1],
                usecols=lambda x: x.upper().strip() in ['ELAPSED SECONDS', 'CURRENT(NA)'])

            # skip any corrupted rows (or pshield restarts)
            mask = data.applymap(is_float).all(1)
            data = data[mask]
            # rearrange and add columns
            data.columns = ['ts', 'isig']

            # add in vout from the file
            v_out = float(
                re.search(r'Output Voltage:([\W\.0-9]+)', header).group()[15:])
            data['vout'] = np.ones(len(data.index)) * v_out
            self.vout = v_out

            # adjust from UTC to PST
            data['ts'] = pd.to_pydatetime(
                data['ts'], unit='s') + self.time_offset
            self.data = data[['ts', 'vout', 'isig']]
            self.period = data['ts'].diff().median()
            return True

        elif self.source == 'BWII':

            assert origin_timestamp is not None, '\terror: this file type requires a timestamp to be specified'

            data, header = self.read_variable_header_file(
                fname,
                'DATETIME,',
                sep=',',
                usecols=lambda x: x.upper().strip() in ['RECORDNUM', 'I1', 'VW1', 'VR1', 'I2', 'VW2', 'VR2'])

            mask = data.applymap(is_float).all(1)
            data = data[mask]
            data.columns = ['ts', 'isig1', 'vw1', 'vr1', 'isig2', 'vw2', 'vr2']

            data['ts'] = data['ts'].map(lambda x: int(x))
            try:
                period = 1 / float(
                    re.search(r'sampling interval:  ([0-9-\.E]+)', header).group()[20:]) or 30
            except:
                period = 30

            origin_timestamp = pd.Timestamp(origin_timestamp).to_pydatetime()

            data['ts'] = pd.to_datetime(
                (np.asarray(data['ts']) - float(data['ts'][0])) * period,
                unit='s',
                origin=origin_timestamp
            )

            self.data = data
            self.period = period
            return True

        elif self.source == 'PSENSE':
            data, header = self.read_variable_header_file(
                fname,
                'Timestamp,Vout1,Signal1,Vout2,Signal2',
                sep=',',
                usecols=lambda x: x.upper().strip() in ['TIMESTAMP', 'VOUT1', 'SIGNAL1', 'VOUT2', 'SIGNAL2'])

            data.columns = ['ts', 'vout1', 'isig1', 'vout2', 'isig2']
            # convert units
            data['ts'] = pd.to_datetime(data['ts'])
            data['vout1'] = data['vout1'] / 1000
            data['vout2'] = data['vout2'] / 1000
            # sampling and data
            self.period = data['ts'].diff().median()
            self.data = data

            return True

        elif self.source == 'VFP':
            assert origin_timestamp is not None, '\terror: this file type requires a timestamp to be specified'

            data, header = self.read_variable_header_file(
                fname,
                "Voltage\tCurrent",
                sep="\t",
                skiprows=[1],
                usecols=lambda x: x.upper() in ['VOLTAGE', 'CURRENT'])

            period = 1 / float(
                re.search(r'FREQ\tQUANT\t([0-9-\.E]+)', header).group()[11:])

            origin_timestamp = pd.Timestamp(origin_timestamp).to_pydatetime()
            if origin_is_end:  # make sure origin reflects the timestamp of the first record.
                origin_timestamp -= pd.Timedelta(
                    seconds=(len(data.index) - 1) * period)

            mask = data.applymap(is_float).all(1)
            data = data[mask]

            data['ts'] = pd.to_datetime(
                np.asarray(data.index) * period,
                unit='s',
                origin=origin_timestamp
            )

            data.columns = ['vout', 'isig', 'ts']
            data = data[['ts', 'vout', 'isig']]
            # convert from scientific notation string to floats
            data['isig'] = data['isig'].astype(np.float64) * 1e9

            self.data = data
            self.vout = data['vout'].median()
            self.period = period
            return True

        elif self.source == 'EXPLAIN':
            data, header = self.read_variable_header_file(
                fname,
                "\tPt\tT\tVf",
                sep="\t",
                skiprows=[1],
                usecols=lambda x: x.upper() in ['T', 'VF', 'IM'])

            # extract starting time
            date_start = re.search(
                r'DATE\tLABEL\t([\-\./0-9]+)', header).group()[11:]
            time_start = re.search(
                r'TIME\tLABEL\t([\.0-9:]+)', header).group()[11:]
            origin_timestamp = datetime.strptime(
                date_start + 'T' + time_start, '%m/%d/%YT%H:%M:%S')

            # remove corrupted data
            mask = data.applymap(is_float).all(1)
            data = data[mask]

            # rearrange and add columns
            data.columns = ['ts', 'vout', 'isig']

            # adjust from seconds elapsed to PST
            data['ts'] = pd.to_datetime(
                round(data['ts']),
                unit='s',
                origin=origin_timestamp)

            # convert from A to nA
            data['isig'] = data['isig'].astype(np.float64) * 1e9

            # save
            self.data = data
            self.vout = data['vout'].median()
            self.period = data['ts'].diff().median()
            return True

        elif self.source == 'WEBAPP':
            data, header = self.read_variable_header_file(
                fname,
                "timestamp,isig,fisig",
                sep=",",
                usecols=lambda x: x.upper() in ['TIMESTAMP', 'ISIG'])

            # rearrange and add columns
            data.columns = ['ts', 'isig']
            data['ts'] = pd.to_datetime(data['ts'])
            self.period = data['ts'].diff().median()
            self.data = data
            return True

        elif self.source == 'WEB1CHAN':
            data, header = self.read_variable_header_file(
                fname,
                "timestamp,signal1,vout1,c_signal1",
                sep=",",
                usecols=lambda x: x.upper() in ['TIMESTAMP', 'SIGNAL1', 'VOUT1'])

            # rearrange and add columns
            data.columns = ['ts', 'isig', 'vout']

            data['ts'] = pd.to_datetime(data['ts'])
            self.data = data[['ts', 'vout', 'isig']]
            self.vout = data['vout'].median()
            self.period = data['ts'].diff().median()
            return True

        elif self.source == 'EMSTAT_EXPORT':
            if origin_timestamp is None:
                print('\terror: this file type requires a timestamp to be specified')
                return False

            # custom read function. DirectSens uses UTF-16 fileenc
            data, origin_timestamp = self.read_emstat_file(
                fname,
                "s,µA",
                sep=",")

            if origin_is_end:
                origin_timestamp -= pd.Timedelta(
                    seconds=(len(data.index) - 1) * period)

            # ignore last row due to encoding
            data.drop(data.tail(1).index, inplace=True)

            # rearrange and add columns
            data.columns = ['ts', 'isig']
            data['isig'] = data['isig'] * 1e3  # convert from uA to nA

            data['ts'] = pd.to_datetime(
                np.asarray(data['ts'].astype(float)),
                unit='s',
                origin=origin_timestamp
            )

            # convert from string to floats
            data['isig'] = data['isig'].astype(np.float64)
            self.period = data['ts'].diff().median()
            self.data = data
            return True

        elif self.source == "EMSTAT_PSESSION":
            self.read_pssession_file(fname)
            return False

        else:
            raise ValueError(
                'Input file {name} not recognized.'.format(name=fname))

    def find_header_text(self, fname, search_string):
        with open(fname, 'r', encoding="utf8", errors='ignore') as f:
            pos = 0
            cur_line = f.readline()
            while not cur_line.startswith(search_string):
                if f.tell() == pos:
                    return False
                pos = f.tell()
                cur_line = f.readline()

        f.close()
        if pos < os.path.getsize(fname):
            return True

        return False

    def read_variable_header_file(self, fname, line, **kwargs):
        header_text = ''
        with open(fname, 'r', encoding="utf8", errors='ignore') as f:
            pos = 0
            cur_line = f.readline()
            while not cur_line.startswith(line):
                if f.tell() == pos:
                    break
                pos = f.tell()
                cur_line = f.readline()
                header_text += cur_line

            f.seek(pos)
            if pos == os.path.getsize(fname):
                return None, None

            return pd.read_csv(f, **kwargs), header_text

    def read_emstat_file(self, fname, line, **kwargs):
        header_text = ''
        with open(fname, 'r', encoding="utf-16le", errors='ignore') as f:
            pos = 0
            cur_line = f.readline()
            header_text = cur_line
            while not cur_line.startswith(line):
                if f.tell() == pos:
                    break
                pos = f.tell()
                cur_line = f.readline()
                header_text += cur_line

            f.seek(pos)
            if pos == os.path.getsize(fname):
                return None, None

            idx_start = header_text.find('Date and time:') + 7
            header_text = header_text[idx_start:]
            idx_stop = header_text.find('\n')
            origin_timestamp = pd.Timestamp(
                header_text[idx_start:idx_stop]).to_pydatetime()

            # origin_timestamp = pd.Timestamp(header_text[idx_start:idx_stop])
            return pd.read_csv(f, **kwargs), origin_timestamp

    def read_pssession_file(self, fname):
        import codecs
        # encoded_text = open('dbo.chrRaces.Table.sql', 'rb').read()
        encoded_text = open(fname, 'rb').read()
        bom = codecs.BOM_UTF16_LE  # print dir(codecs) for other encodings
        # make sure the encoding is what you expect, otherwise you'll get wrong data
        assert encoded_text.startswith(bom)
        encoded_text = encoded_text[len(bom):]  # strip away the BOM
        decoded_text = encoded_text.decode('utf-16le')
        data = json.loads(decoded_text[:-1])

        print(data['measurements'][0]['dataset']['values'][0]['description'])
        print(data['measurements'][0]['dataset']['values'][1]['description'])
        print(data['measurements'][0]['dataset']['values'][2]['description'])
        print(data['measurements'][0]['dataset']['values'][2]['unit'])
        print(np.asarray(data['measurements'][0]
                         ['dataset']['values'][2]['datavalues']))
        assert(False)
