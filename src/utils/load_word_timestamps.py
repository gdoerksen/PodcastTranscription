import json
from pathlib import Path

def load_word_timestamps( word_ts_file_path: Path )-> list[ dict ]:
    """
    Load a word timestamp file and return a list of dictionaries of the form: {'start': start_time, 'end': end_time, 'text': word}
    """
    word_ts = []
    with word_ts_file_path.open('r') as f:
        for line in f:
            line_temp = json.loads(line)
            word_ts.append(line_temp)
    return word_ts