from .hls_helper import read_file_hls_timestamp, get_start_end_seq_hls, write_body_record, write_end_record, \
    write_head_record


def cut_hls_in_local(path_name, from_time, to_time):
    timestamps, names, sums = read_file_hls_timestamp(path_name)
    start_seq, end_seq = get_start_end_seq_hls(sums, from_time, to_time)
    file_name_cut = u'{original_path}_{from_time}_{to_time}.m3u8'.format(
        original_path=path_name[:-5],
        from_time=from_time,
        to_time=to_time
    )
    f = open(file_name_cut, 'w')
    write_head_record(f)
    write_body_record(f, start_seq, end_seq, names, timestamps)
    write_end_record(f)
    return file_name_cut
