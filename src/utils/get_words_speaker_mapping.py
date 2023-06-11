def get_word_ts_anchor(start, end, option='start'):
    """
    Get the anchor point for a word timestamp
    """
    if option == 'end':
        return end
    elif option == 'mid':
        return (start + end) / 2
    return start

def get_words_speaker_mapping(wrd_ts, spk_ts, word_anchor_option='start')-> list[ dict ]:
    """
    Map words to speakers based on the word timestamps and speaker timestamps
    """

    start, end, speaker = spk_ts[0]
    wrd_pos, turn_idx = 0, 0
    wrd_spk_mapping = []
    for wrd_dict in wrd_ts:
        word_start_s = int(wrd_dict['start'] * 1000)
        word_end_s = int(wrd_dict['end'] * 1000)
        word = wrd_dict['text']
        wrd_pos = get_word_ts_anchor(word_start_s, word_end_s, word_anchor_option)
        while wrd_pos > float(end):
            turn_idx += 1
            turn_idx = min(turn_idx, len(spk_ts) - 1)
            start, end, speaker = spk_ts[turn_idx]
        wrd_spk_mapping.append({'word': word, 'start_time': word_start_s, 'end_time': word_end_s, 'speaker': speaker})
    return wrd_spk_mapping