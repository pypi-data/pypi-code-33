import json, pprint
from collections import defaultdict
from IPython.display import display

import pandas as pd
import pyarrow as pa

from .chart import ChartBuilder

from .datamode_app import DatamodeApp
from .arrow import serialize_to_arrow
from .reactdata import unpack_filterset

from datamode.utils.utils import get_hexhash_from_int, log_exception_with_context
from datamode.utils.usageutils import is_anonymous_tracking_allowed
from datamode.utils.data import is_col_vector
from datamode.utils.timer import CustomTimer
from datamode.settings import AUID


from datamode.utils.utils import get_logger
log = get_logger(__name__)


class ReactBridge():
  def __init__(self, reactdata, timer, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.reactdata = reactdata
    self.timer = timer
    self.cb = ChartBuilder(reactdata)

  # Todo: not threadsafe!
  def handle_comm_msg(self, comm, msg):
    comm_data = None

    try:
      msg_data = msg['content']['data']
      msgtype = msg_data['msgtype']

      # We should log all calls except get_rows, which has a lot of calls.
      logit = msgtype != 'get_rows'
      timermsg = f'\n-------------- Message {msgtype} received ---------------------------\n'
      self.timer = CustomTimer(log, msgtype, msg=timermsg, logit=logit)

      buffers = None

      if msgtype == 'transform_frame':
        comm_data, buffers = self.handle_transform_frame(msg_data)
      elif msgtype == 'get_rows':
        comm_data, buffers = self.handle_get_rows(msg_data)
      elif msgtype == 'chart':
        comm_data, buffers = self.cb.build_chart(msg_data)


      _td_elapsed, td_total = self.timer.report()
      comm_data['elapsed'] = td_total.total_seconds()

      comm.send(comm_data, buffers=buffers)
      self.timer.end('Sent comm_data')


    except Exception as e:
      comm_str = pprint.pformat(comm)
      msg_str = pprint.pformat(msg)
      comm_data_str = 'not pprinted'
      # comm_data_str = pprint.pformat(comm_data)

      # Change print_locals to True to see details here
      log_exception_with_context(log, e, f'Exception {e.__class__.__name__} caught in handle_comm_msg:\n\ncomm:\n{comm_str}\n\nmsg:\n{msg_str}\n\ncomm_data:\n{comm_data_str}\n', print_locals=False)
      # self.timer.report('Logged exception')
      raise e


  def handle_transform_frame(self, msg_data):
    transform_id, facets, sort = unpack_filterset(msg_data['filterset'])
    columnar_viz = msg_data.get('columnar_viz')  # Can be None

    # Actually filter the data
    df = self.reactdata.get_filtered_df(transform_id, facets, sort=sort)
    table = self.reactdata.get_df_dest_at_transform_id(transform_id)

    # Send it back over the wire
    self.timer.report(f'About to marshal data for transform_id={transform_id}, table={table}')
    comm_data = self.marshal_metadata(df, transform_id, table, facets, columnar_viz)
    comm_data['msgtype'] = 'transform_frame_response'
    comm_data['record_count'] = df.shape[0]
    comm_data['snapshot_hash'] = self.create_snapshot_hash(df)

    return comm_data, None


  def handle_get_rows(self, msg_data):
    transform_id, facets, sort = unpack_filterset(msg_data['filterset'])
    rowset = msg_data['rowset']

    # Actually filter the data
    df = self.reactdata.get_filtered_df(transform_id, facets, sort=sort, rowset=rowset)
    table = self.reactdata.get_df_dest_at_transform_id(transform_id)

    # Send it back over the wire
    # self.timer.report(f'About to marshal data for transform_id={transform_id}, table={table}, index_start={index_start}, index_end={index_end}')
    comm_data = {
      'msgtype': 'get_rows_response',
      'rowset': rowset,
    }

    for colname in df.columns:
      col = df[colname]
      if is_col_vector(col):
        col.apply(lambda x: str(x.shape))
        df[colname] = col


    comm_data['compress'] = True
    buffer = serialize_to_arrow(df, compress=True)
    buffers = [buffer]

    return comm_data, buffers


  def marshal_metadata(self, df, transform_id, table, facets={}, columnar_viz=None):
    colinfos = self.reactdata.get_colinfos(transform_id, df, columnar_viz)
    self.timer.report(f'Finished getting colinfos. table={table}, transform_id={transform_id}, facets={facets}')

    metadata = {
      'transform_id': transform_id,
      'table': table,
      'columnar_viz': columnar_viz,
      'facets': facets,
      'columns': colinfos,
    }

    return metadata


  # taglist_by_colname is a dict where key=colname, value=taglist.
  # taglist is a set of string tags that apply to the cell.
  def build_taglist_by_colname(self, record):
    taglist_by_colname = defaultdict(list)

    for colname, value in record.items():
      # Set null values
      if value is None:
        taglist_by_colname[colname].append('null')
      if value == 'home_page':
        taglist_by_colname[colname].append('invalid')

    return dict(taglist_by_colname)


  def display(self, timer=None):
    # Initial transform_id - the last transform
    transform_id = self.reactdata.tcon.ds.tstate_count - 1

    # Package everything for React
    tstates = self.reactdata.tcon.ds.tstates

    transform_entries = []
    for index, tstate in enumerate(tstates):
      entry = {
        'transform': str(tstate.transform),
        'index': index,
        'elapsed': tstate.elapsed.total_seconds()
      }

      transform_entries.append(entry)

    send_anon_usage = is_anonymous_tracking_allowed()

    props = {
      'transform_entries': transform_entries,
      'initialTransformId': transform_id,
      'anonymousUserId': AUID if send_anon_usage else None,
    }


    # Enable debugging comm data from display
    # facets = {'summary': "" }
    # self.simulate_comm_request(transform_id, facets={}, columnar_viz={ 'vizType': 'kde', 'targetVariable': 'Pclass' })


    # Create the component and actually display it in the notebook
    react_datamode_app = DatamodeApp(handler=self.handle_comm_msg, props=props)
    display(react_datamode_app)
    self.timer.report('Completed Jupyter display')


  # https://stackoverflow.com/questions/31567401/get-the-same-hash-value-for-a-pandas-dataframe-each-time
  # We only need to hash the dataframe itself.
  def create_snapshot_hash(self, df):
    hashval = hash(df.values.tobytes())
    self.timer.report('Completed dataframe hash')
    hexhash = get_hexhash_from_int('md5', hashval)
    return hexhash


  def simulate_comm_request(self, transform_id, facets, columnar_viz=None):
    # breakpoint()
    df = self.reactdata.get_filtered_df(transform_id, facets)
    self.reactdata.get_colinfos(transform_id, df, columnar_viz=columnar_viz)
    comm_data = self.marshal_metadata(df, transform_id, 'dummy_table', facets, columnar_viz=columnar_viz)
    serialize_to_arrow(df)
