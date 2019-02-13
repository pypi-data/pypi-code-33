from .exception import FileException


def write_head_record(f, target_duration=10, start_seq=0, play_list_type='EVENT'):
    f.write('#EXTM3U\n')
    f.write('#EXT-X-VERSION:3\n')
    f.write('#EXT-X-MEDIA-SEQUENCE:{start_seq}\n'.format(start_seq=start_seq))
    f.write('#EXT-X-TARGETDURATION:{target_duration}\n'.format(target_duration=target_duration))
    f.write('#EXT-X-PLAYLIST-TYPE: {play_list_type}\n'.format(play_list_type=play_list_type))
    f.write('#EXT-X-DISCONTINUITY\n')


def write_body_record(f, start_seq, end_seq, names, timestamps):
    for i in range(start_seq, end_seq + 1, 1):
        f.write('#EXTINF:{timestamp},\n'.format(timestamp=timestamps[i]))
        f.write(u'{name}'.format(name=names[i]))


def write_end_record(f):
    f.write('#EXT-X-ENDLIST\n')


def get_start_end_seq_hls(timestamps_sum, from_time, to_time):
    start_seq = None
    end_seq = None
    i = -1
    for e in timestamps_sum:
        i += 1
        if e > from_time and start_seq is None:
            start_seq = i
        if e > to_time and end_seq is None:
            end_seq = i
    if start_seq is None:
        raise FileException('Can not cut file with none start')
    if end_seq is None:
        end_seq = len(timestamps_sum) - 1
    return start_seq, end_seq


def read_file_hls_timestamp(path_name):
    timestamps = []
    names = []
    sums = []
    target_duration = 0
    f = open(path_name)
    i = 0
    for line in f.readlines():
        line = line.strip()
        if '#EXTINF' in line:
            i += 1
            timestamp = float(line[8:-1])
            timestamps.append(timestamp)
            if i == 1:
                sums.append(timestamp)
            else:
                sums.append(sums[i - 2] + timestamp)
        elif '.ts' in line:
            names.append(line)
        elif '#EXT-X-TARGETDURATION' in line:
            target_duration = float(line[22:])
    return timestamps, names, sums, target_duration
