import json
import pyarrow as pa

from datamode.utils.data import is_obj_fancy_array


def serialize_to_arrow(df, compress=True, timer=None):
  timer.report('Started Arrow serialization') if timer else None

  df = fix_dicts(df)

  batch = pa.RecordBatch.from_pandas(df)
  timer.report(f'Converted df to RecordBatch. df: rows={df.shape[0]}. batch: rows={batch.num_rows}, cols={batch.num_columns}') if timer else None

  sink = pa.BufferOutputStream()
  writer = pa.RecordBatchFileWriter(sink, batch.schema)

  writer.write_batch(batch)
  writer.close()

  timer.report(f'Completed write. Bytes written: {sink.tell()}') if timer else None
  timer.report('Completed Arrow serialization.') if timer else None

  # In repr, use buffer.to_pybytes()[:1000]  to examine the memory, it prints ascii if it finds it.
  buffer = sink.getvalue()

  # For compression algorithm comparison:
  # https://gregoryszorc.com/blog/2017/03/07/better-compression-with-zstandard/
  #
  # and pyarrow docs:
  # https://arrow.apache.org/docs/python/generated/pyarrow.compress.html
  if compress:
    buffer = pa.compress(buffer, codec='gzip')

  return buffer


def make_arrow_friendly(value):
  if type(value) in (dict, list, set):
    return json.dumps(value)

  if is_obj_fancy_array(value):
    return str(value.shape)

  return value

# Although Pyarrow supports serializing arbitrary python objects, it doesn't appear to support doing that
# from a pandas dataframe. So, we'll just convert Python dicts to a string.
# We have to run it on all rows because the dataset could have objects in any row.
def fix_dicts(df):
  for colname in df.select_dtypes('object'):
    df[colname] = df[colname].apply(make_arrow_friendly)

  return df
