"""
Classes for Empatica E4-formatted Physio import
"""
from __future__ import division  # In case of Py2k fix float division
# from Atheneum import models
import datetime
# from django.db import connection
import gzip
import json
import logging
import os
import pandas as pd
import pytz
from shutil import rmtree
import tempfile
import zipfile

logger = logging.getLogger(__name__)

try:
    import tables
    hdf_available = True
except ImportError:
    hdf_available = False


class Session(object):
    """A full E4 physio session archive / zip containing several stream csv's.

    Arguments
    -----------
    source_path : file handle or path string
        Source of the physio session; a path to a directory or archive zip file
        containing E4 csv streams.

    Attributes
    ----------
    streams : dict
        A dictionary with stream names as keys and
        :class:`~empatican.physio.e4.Stream` objects as values

    start_datetime : datetime
        A "common" start time for most streams in the session.

    duration : float
        Length of stream recording in seconds


    Examples
    ---------
    >>> session1 = Session('Sub01')
    >>> session1.streams['acc']
    < physio.AccStream at ... >


    >>> session2 = Session('Sub01.zip')
    >>> session2.streams['eda']
    < physio.EdaStream at ... >

    Raises
    ------
    IOError : If the filename doesn't exist
    """

    def __init__(self, source_path):
        if 'db_pk' in dir(self):
            # Already loaded from Database
            pass
        elif ('endswith' in dir(source_path) and source_path.endswith('.h5') or
              'name' in dir(source_path) and source_path.name.endswith('.h5')):
            if hdf_available:
                self.load_hdf(source_path)
            else:
                logger.info('Please install `tables` for HDF5 support '
                            'if needed.')
        else:
            self.load_csvs(source_path)

        start_datetime = datetime.datetime.fromtimestamp(
            self.streams['acc'].start_timestamp, tz=pytz.utc)
        self.start_datetime = start_datetime

        duration = self.streams['acc'].duration
        self.duration = duration

        assert ('e4_meta' in dir(self))

    def load_csvs(self, source_path, on_error="WARN"):
        self.source_path = source_path
        self.streams = self.read_streams()

        metadata_path = os.path.join(self._temp_source_path, 'metadata.json')
        e4_meta = self._load_meta(metadata_path)
        self.e4_meta = e4_meta

    @property
    def source_path(self):
        return self._source_path

    @source_path.setter
    def source_path(self, source_path):
        try:
            dirlike = os.path.isdir(source_path)
        except TypeError:
            dirlike = False

        if dirlike or self.hdf5like(source_path):
            self._temp_source_path = source_path
        elif zipfile.is_zipfile(source_path):
            with zipfile.ZipFile(source_path) as zf:
                tmpdir = tempfile.mkdtemp()
                zf.extractall(tmpdir)
            self._temp_source_path = tmpdir
        else:
            self._source_path, self._temp_source_path = None, None
            source_msg = ("Check path: File %s must be an existing directory, "
                          "hdf5 or zip file." % source_path)
            raise IOError(source_msg)
        self._source_path = source_path

    @source_path.deleter
    def source_path(self):
        if '_temp_source_path' in dir(self):
            if self._temp_source_path != self._source_path and os.path.isdir(
                    self._temp_source_path):
                logger.debug("Removing temporary extracted archive dir %s" %
                             self._temp_source_path)
                rmtree(self._temp_source_path)

    def read_streams(self):
        """Read all streams in an archive and expose them in a dict

        Returns
        -------

        streams : dict
            Dictionary of streams with stream names as keys and physio.Stream
            objects as values.
        """
        streams = dict()

        # Loop through each stream and instantiate it from the appropriate csv
        for stream_name, (stream_class, stream_path) in STREAM_SOURCE.items():
            temp_path = os.path.join(self._temp_source_path, stream_path)
            streams[stream_name] = stream_class(temp_path)

        return streams

    def __del__(self):
        # Ensure that temporary extracted files are removed
        # (does NOT delete the zip on disk!)
        del (self.source_path)

    def to_hdf(self, out_file=None, base_key='/dt/', **args):
        """Save a stream out to a single hdf5 file.
        """
        if not out_file:
            out_file = self.default_fname(ext='.h5')

        # Default compression level - extreme compression but slower
        compression_args = dict(complevel=9, complib='blosc:zstd')
        compression_args.update(args)

        with pd.HDFStore(out_file, **compression_args) as store:
            for name, stream in self.streams.items():
                key = base_key + name
                store.put(key, stream.data)
                attrs = store.get_storer(key).attrs
                stream_metadata = dict(
                    start_timestamp=stream.start_timestamp,
                    frequency=stream.frequency,
                    filepath=stream.filepath,
                    duration=stream.duration)
                attrs.metadata = stream_metadata

            attrs = store.get_node(base_key)._v_attrs
            for key, val in self.e4_meta.items():
                attrs[key] = val
        return out_file

    def load_hdf(self, source_path, base_key='/dt/'):
        """Load a session from a saved h5 file"""
        streams = dict()
        with pd.HDFStore(source_path) as store:
            attrs = store.get_node(base_key)._v_attrs
            self.e4_meta = attrs.__dict__

            for stream_name, (stream_class,
                              stream_path) in STREAM_SOURCE.items():
                stream_key = base_key + stream_name

                # Load Dataset and H5 Stored Metadata
                stream_df = store.get(stream_key)
                stream_meta = store.get_storer(stream_key).attrs['metadata']

                # Create a thin stream (just the dataset)
                stream = stream_class(stream_df)

                # Then, update H5 Stored Metadata (FIXME - TOO FRAGILE)
                stream.start_timestamp = stream_meta['start_timestamp']
                stream.frequency = stream_meta['frequency']
                stream.filepath = stream_meta['filepath']
                stream.duration = stream_meta['duration']
                streams[stream_name] = stream

        self.streams = streams
        self._source_path, self._temp_source_path = None, None

    def to_archive(self, out_path=None):
        """Save a session to archive csv directory

        Parameters
        -----------
        out_path : str
            Path to use for saving the directory. Optionally end the file with
            ".zip" to create a zipped archive file, otherwise creates a
            directory structure.

        Returns
        -------
        out_path : str
            Returns the newly written archive path (in case default metadata
            was used to create the archive).
        """
        if not out_path:
            out_path = self.default_fname()
        if os.path.exists(out_path):
            raise IOError('Archive dir {} already exists - not overwriting'.
                          format(out_path))
        else:
            if out_path.endswith('.zip'):
                out_dir = out_path[:-4]
            else:
                out_dir = out_path
            os.makedirs(out_dir)

        for stream_name, (stream_class, stream_path) in STREAM_SOURCE.items():
            stream = self.streams[stream_name]
            temp_path = os.path.join(out_dir, stream_path)
            stream.to_csv(temp_path)

        with open(os.path.join(out_dir, 'metadata.json'), 'w') as f:
            f.write(
                json.dumps(
                    self.e4_meta, indent=4, sort_keys=True, default=str))

        if out_path.endswith('.zip'):
            with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                self._make_zip(out_dir, zipf)
            rmtree(out_dir)

        return out_path

    def _make_zip(self, path, ziph, include_root=False):
        path = os.path.abspath(path)
        # ziph is zipfile handle
        for root, dirs, files in os.walk(path):
            if include_root:
                base = os.path.dirname(path)
            else:
                base = path
            dest_dir = root.replace(base, '', 1)
            for fname in files:
                ziph.write(
                    os.path.join(root, fname),
                    arcname=os.path.join(dest_dir, fname))

    def _load_meta(self, path):
        """Load vendor info from metadata.json if present.

        Be sure to call after header and data have been read so that they
        are available for consistency checks."""
        if os.path.exists(path):
            with open(path, 'r') as f:
                e4_info = json.load(f)

            duration = self.streams['acc'].duration
            if int(e4_info['duration']) != int(duration):
                err_pat = ('Duration from metadata ({}) does not '
                           'match duration from data ({})')
                err_args = e4_info['duration'], duration
                logger.warning(err_pat.format(*err_args))

            start_timestamp = self.streams['acc'].start_timestamp
            if e4_info['start_time'] != start_timestamp:
                err_pat = ('Starting timestamp from metadata ({}) '
                           'does not match start read from data ({})')
                err_args = e4_info['start_time'], start_timestamp
                logger.warning(err_pat.format(*err_args))

        else:
            e4_info = {}
        return e4_info

    def hdf5like(self, source_path):
        try:
            pd.read_hdf(source_path)
            is_hdf = True
        except (NotImplementedError, OSError):
            is_hdf = False
        except ImportError:
            self.has_hdf = False
            is_hdf = False
            logger.info('Please install `tables` for HDF5 support if needed.')
        return is_hdf

    def default_fname(self, ext='.zip'):
        fname = "%d" % self.start_datetime.timestamp()
        if 'device_name' in self.e4_meta.keys():
            fname += '_' + self.e4_meta['device_name']
        elif 'device_id' in self.e4_meta.keys() and self.e4_meta['device_id']:
            fname += '_' + self.e4_meta['device_id']
        fname += ext
        return fname


class Stream(object):
    """A single E4 stream (e.g. ACC, IBI, ...).

    General methods to handle oddities of the E4 data format and normalize
    across modalities.

    Parameters
    ---------
    filepath_or_buffer : file handle or path string
        Source E4 data, as either the path to a [possibly gzipped] file name
        or file handle (possibly existing only in memory).

    header_names : list
        Names of each columns measurements are required; see subclasses for
        more information.

    timestamp_present : bool, default True
        True if line 1 contains a timestamp for this stream format

    freq_present : bool, default True
        True if line 2 contains a frequency for this stream format


    Attributes
    ----------

    filepath : str or handle
        Source filepath used to generate the string.

    data : pd.DataFrame
        dataframe with time-stampped index and named columns.

    start_timestamp : int
        The initial timestamp from the csv (line 1) in UTC.

    frequency : int or None
        The initial frequency from the csv (ussually line 2, absent for IBI).

    duration : float
        Duration of stream recording (in seconds)
    """

    def __init__(self,
                 filepath_or_buffer,
                 header_names,
                 timestamp_present=True,
                 freq_present=True):
        if isinstance(filepath_or_buffer, pd.DataFrame):
            # If a dataframe is provided, set it directly w/o ts and frequency
            data = filepath_or_buffer

            if data.shape[0]:  # Not an empty Dataframe
                start_timestamp = int(data.index[0].timestamp())

                # Check to see if all time deltas are the same
                # ... (sampled with regular frequency)
                timesteps = (data.iloc[1:].index - data.iloc[:-1].index)
                if timesteps.unique().size == 1:
                    timestep = data.index[1] - data.index[0]
                    frequency = int(round(1 / timestep.total_seconds()))
                else:
                    frequency = None
            else:
                start_timestamp = None
                frequency = None

        else:
            if os.path.exists(filepath_or_buffer):
                self.filepath = filepath_or_buffer
            else:
                # If an in-memory buffer was passed don't set filepath.
                self.filepath = None

            data, start_timestamp, frequency = self.parse_raw_data(
                filepath_or_buffer, header_names, timestamp_present,
                freq_present)

        self.data = data
        self.start_timestamp = start_timestamp
        self.frequency = frequency
        self.timestamp_present = timestamp_present
        self.freq_present = freq_present

        # Calculate duration directly from Datetime index of `data`
        if self.data.shape[0]:
            self.duration = (data.index[-1] - data.index[0]).total_seconds()
        else:  # Except empty DataFrame
            self.duration = 0

    def parse_raw_data(self,
                       filepath_or_buffer,
                       header_names,
                       timestamp_present=True,
                       freq_present=True,
                       on_error='warn'):
        """Read a single E4-formatted stream of data.

        Parameters
        ----------
        filepath_or_buffer : file handle or str
            Path or buffer to load stream data from

        header_names : list of strings
            Column names of a stream's specific attributes. Hard-coded
            when sub-classing Stream as in AccStream (['x', 'y', 'z']),
            TemperatureStream (['temperature']) etc.

        timestamp_present : boolean, default True
            Indicator for whether or not line 1 is a timestamp (true except for
            phone press [tag] stream)

        freq_present : boolean, default True
            Indicator for whether or not line 2 is a frequency (true except for
            streams where the values themselves are timestamps, currently only
            IBI).

        on_error : str, 'warn' or 'raise'
            Behavior for short streams where an appropriate timestamp index
            can not be built.


        Returns
        -------
        stream_df : pd.DataFrame
            Pandas dataframe with proper timestampped index and frequency.

        timestamp : int
            Unix timestamp (UTC) of stream start (row 1 when timestamp present).

        frequency : int
            Frequency in Hz of stream (row 2 when freq present).
        """
        timestamp, frequency, n_samples = self.read_header(
            filepath_or_buffer,
            timestamp_present=timestamp_present,
            freq_present=freq_present)

        if timestamp_present:
            if freq_present:
                skiprows = 2
            else:
                skiprows = 1
        else:
            skiprows = 0

        stream_df = pd.read_csv(
            filepath_or_buffer, skiprows=skiprows, names=header_names)

        # Almost always, there will be a frequency for the stream so
        # timestamps can be inferred. For the case of processed heartbeat data
        # (IBI) that's not the case so the index will be a standard
        # auto-incrementing int.
        if frequency:
            timestamp_index = self.build_freq_index(timestamp, frequency,
                                                    n_samples)
            if timestamp_index.size == 0:
                timestamp_msg = ("Couldn't build a valid "
                                 "timestamp index with (%s, %s, %s)")
                if on_error == 'raise':
                    raise ValueError(
                        timestamp_msg % (timestamp, frequency, n_samples))
                else:  # if on_error == 'warn':
                    logger.debug(
                        timestamp_msg % (timestamp, frequency, n_samples))
        else:
            if timestamp:  # IBI
                timestamp_index = self.build_timedelta_index(
                    timestamp, stream_df)
            else:  # tags / presses
                # Use only the first column (currently df is always 1-d anyway)
                timestamp_index = self.build_timestamp_index(
                    stream_df.iloc[:, 0])
        stream_df.index = timestamp_index
        return stream_df, timestamp, frequency

    def read_header(self,
                    filepath_or_buffer,
                    timestamp_present=True,
                    freq_present=True):
        """Go through the stream once to read some metadata

        This is the first of two passes simply to get metadata and sample
        count, so as an algorithm it could certainly be improved, but we don't
        need to optimize right now.

        Read E4-formatted header, where line 1 is the unix timestamp and line 2
        is ussually the frequency (when freq_present is True).

        nb E4 always appears to have a correct unix timestamp (a base unit of
        seconds), but the embrace file looks to have timestamps as a base unit
        of milliseconds.

        Parameters
        ----------
        filepath_or_buffer : file handle or str
            Path or buffer to load stream data from

        timestamp_present : boolean, default True
            Indicator for wehther or not line 1 is a timestamp (true except for
            phone press [tag] stream)

        freq_present : boolean, default True
            Indicator for whether or not line 2 is a frequency (true except for
            streams where the values themselves are timestamps, currenctly only
            IBI).

        Returns
        -------
        timestamp : int or None
            Initial unix timestamp (from line 1) in UTC or None if not present
            (press stream [tags.csv] )

        freq : int or None
            Frequency in Hz (from line 2) or None if not present (IBI).

        n_samples : int
            Count of remaining lines to build timestamp
        """
        if filepath_or_buffer.endswith('.gz'):
            openfunc = gzip.open
            delim = b','
        else:
            openfunc = open
            delim = ','

        with openfunc(filepath_or_buffer, 'r') as f:
            # Round-trip through float for pythonic reading of the number
            if timestamp_present:
                ts_val = f.readline().strip().split(delim)[0]
                try:
                    timestamp = int(float(ts_val))
                except ValueError:
                    timestamp = None
            else:
                timestamp = None

            if freq_present:
                ts_val = f.readline().strip().split(delim)[0]
                try:
                    freq = int(float(ts_val))
                except ValueError:
                    freq = None
            else:
                freq = None
            n_samples = 0
            while f.readline():
                n_samples += 1

        return timestamp, freq, n_samples

    def build_freq_index(self, timestamp, freq, n_samples):
        """Build a datetime index from initial timestamp, frequency, and number
        of samples."""
        start = datetime.datetime.fromtimestamp(timestamp, tz=pytz.utc)

        # Convert from int herz frequency to a pandas datetime offset string
        freq_string = "%fL" % (1 / freq * 1000)

        # Build the DatetimeIndex
        timestamp_index = pd.date_range(
            start=start, freq=freq_string, periods=n_samples)

        return timestamp_index

    def build_timedelta_index(self, timestamp, df):
        """Build a datetime index from an initial time and a df of time
        deltas."""

        # Insert 0 (to account for timestamp in the header)
        df.loc[0] = 0

        # Calculate the additive time (in seconds) from the df index
        sec_delta = df.index.sort_values().to_series()

        # Create timestamps by adding the initial time
        timestamps = timestamp + sec_delta.values

        # Create a pd.Series where index is the delta and value is timestamp
        ts_series = pd.to_datetime(timestamps, unit='s', utc=True)

        return ts_series

    def build_timestamp_index(self, series):
        """Build a datetime index from a df of timestamps.

        At present can only handle a series (vector)"""
        ts_series = pd.to_datetime(series, unit='s', utc=True)
        return ts_series

    @property
    def num_samples(self):
        return self.data.shape[0]

    def to_csv(self, fname=None):
        frames = []
        if self.timestamp_present:
            ts_df = pd.DataFrame([], columns=self.data.columns)
            ts_df.loc[0] = self.start_timestamp
            frames.append(ts_df)

        if self.freq_present:
            freq_df = pd.DataFrame([], columns=self.data.columns)
            freq_df.loc[0] = self.frequency
            frames.append(freq_df)

        frames.append(self.data)

        out_df = pd.concat(frames)

        out_df.to_csv(fname, header=False, index=False)


class AccStream(Stream):
    def __init__(self, *args, **kwargs):
        kwargs['header_names'] = ['x', 'y', 'z']
        super(AccStream, self).__init__(*args, **kwargs)


class BvpStream(Stream):
    def __init__(self, *args, **kwargs):
        kwargs['header_names'] = ['bvp']
        super(BvpStream, self).__init__(*args, **kwargs)


class EdaStream(Stream):
    def __init__(self, *args, **kwargs):
        kwargs['header_names'] = ['eda']
        super(EdaStream, self).__init__(*args, **kwargs)


class HrStream(Stream):
    def __init__(self, *args, **kwargs):
        kwargs['header_names'] = ['hr']
        super(HrStream, self).__init__(*args, **kwargs)


class IbiStream(Stream):
    def __init__(self, *args, **kwargs):
        kwargs['header_names'] = ['ibi']
        kwargs['freq_present'] = False
        super(IbiStream, self).__init__(*args, **kwargs)


class PressStream(Stream):
    def __init__(self, *args, **kwargs):
        kwargs['header_names'] = ['press']
        kwargs['freq_present'] = False
        kwargs['timestamp_present'] = False
        super(PressStream, self).__init__(*args, **kwargs)


class TemperatureStream(Stream):
    def __init__(self, *args, **kwargs):
        kwargs['header_names'] = ['temperature']
        super(TemperatureStream, self).__init__(*args, **kwargs)


STREAM_SOURCE = dict(
    acc=(AccStream, 'ACC.csv'),
    bvp=(BvpStream, 'BVP.csv'),
    eda=(EdaStream, 'EDA.csv'),
    hr=(HrStream, 'HR.csv'),
    ibi=(IbiStream, 'IBI.csv'),
    press=(PressStream, 'tags.csv'),
    temperature=(TemperatureStream, 'TEMP.csv'),
)
