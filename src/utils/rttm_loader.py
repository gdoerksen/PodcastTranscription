from pathlib import Path

def load_rttm_file( rttm_file_path: Path )-> list[ list[int] ]:
    """
    Load a speaker timetsamp .rttm file and return a list of lists of the form: [start_time, end_time, speaker_id]
    """
    speaker_ts = []
    with rttm_file_path.open('r') as f:
        lines = f.readlines()
        for line in lines:
            line_list = line.split(' ')
            start = int(float(line_list[3]) * 1000)
            end = start + int(float(line_list[4]) * 1000)
            speaker_id = int(line_list[7].split('_')[-1])
            speaker_ts.append([start, end, speaker_id])

    return speaker_ts