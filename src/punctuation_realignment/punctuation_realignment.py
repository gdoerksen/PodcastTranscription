from pathlib import Path


sentence_ending_punctuations = '.?!'

def get_first_word_idx_of_sentence(word_idx, word_list, speaker_list, max_words):
    is_word_sentence_end = lambda x: x >= 0 and word_list[x][-1] in sentence_ending_punctuations
    left_idx = word_idx
    while (left_idx > 0 and word_idx - left_idx < max_words and
            speaker_list[left_idx - 1] == speaker_list[left_idx] and
            not is_word_sentence_end(left_idx - 1)):
        left_idx -= 1
        
    return left_idx if left_idx == 0 or is_word_sentence_end(left_idx - 1) else -1

def get_last_word_idx_of_sentence(word_idx, word_list, max_words):
    is_word_sentence_end = lambda x: x >= 0 and word_list[x][-1] in sentence_ending_punctuations
    right_idx = word_idx
    while (right_idx < len(word_list) and right_idx - word_idx < max_words and
            not is_word_sentence_end(right_idx)):
        right_idx += 1
        
    return right_idx if right_idx == len(word_list) - 1 or is_word_sentence_end(right_idx) else -1

def get_realigned_ws_mapping_with_punctuation(word_speaker_mapping, max_words_in_sentence = 50):
    is_word_sentence_end = lambda x: x >= 0 and word_speaker_mapping[x]['word'][-1] in sentence_ending_punctuations
    wsp_len = len(word_speaker_mapping)
    
    words_list, speaker_list = [], []
    for k, line_dict in enumerate(word_speaker_mapping):
        word, speaker = line_dict['word'], line_dict['speaker']
        words_list.append(word)
        speaker_list.append(speaker)

    k = 0
    while k < len(word_speaker_mapping):
        line_dict = word_speaker_mapping[k]
        if k < wsp_len - 1 and speaker_list[k] != speaker_list[k + 1] and not is_word_sentence_end(k):
            left_idx = get_first_word_idx_of_sentence(k, words_list, speaker_list, max_words_in_sentence)
            right_idx = get_last_word_idx_of_sentence(k, words_list, max_words_in_sentence - k + left_idx - 1) if left_idx > -1 else -1
            if min(left_idx, right_idx) == -1:
                k += 1
                continue
            
            spk_labels = speaker_list[left_idx: right_idx + 1]
            mod_speaker = max(set(spk_labels), key=spk_labels.count)
            if spk_labels.count(mod_speaker) < len(spk_labels) // 2:
                k += 1
                continue
            
            speaker_list[left_idx: right_idx + 1] = [mod_speaker] * (right_idx - left_idx + 1)
            k = right_idx
        
        k += 1
  
    k, realigned_list = 0, []
    while k < len(word_speaker_mapping):
        line_dict = word_speaker_mapping[k].copy()
        line_dict['speaker'] = speaker_list[k]
        realigned_list.append(line_dict)
        k += 1
      
  
    return realigned_list

def get_sentences_speaker_mapping(word_speaker_mapping, spk_ts) -> list[dict[str, str]]:
    """
    Seperate the word speaker mapping into sentences based on the speaker change

    #TODO move this to a separate file
    """

    start, end, spk = spk_ts[0]
    prev_spk = spk

    sentences = []
    sentence = {'speaker': f'Speaker {spk}', 'start_time': start, 'end_time': end, 'text': ''}

    for wrd_dict in word_speaker_mapping:
        wrd, spk = wrd_dict['word'], wrd_dict['speaker']
        start, end = wrd_dict['start_time'], wrd_dict['end_time']
        if spk != prev_spk:
            sentences.append(sentence)
            sentence = {'speaker': f'Speaker {spk}', 'start_time': start, 'end_time': end, 'text': ''}
        else:
            sentence['end_time'] = end
        sentence['text'] += wrd + ' '
        prev_spk = spk

    sentences.append(sentence)
    return sentences

def save_diarized_transcript(sentences_speaker_mapping, output_dir_path: Path):
    """
    Output the diarized transcript to a file

    #TODO move this to a separate file
    """

    output_file = output_dir_path / 'diarization.txt'

    with output_file.open('w') as f:
        for sentence_dict in sentences_speaker_mapping:
            speaker = sentence_dict['speaker']
            text = sentence_dict['text']
            f.write(f'\n\n{speaker}: {text}')