import logging
import argparse
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import torch

from utils import (
    configure_logging,
    load_rttm_file,
    load_word_timestamps,
    get_words_speaker_mapping
)
from metadata import TinyTagAudioMetadata
from audio_processing import FFmpegSplitter, ffmpeg_to_16k
from transcriber import WhisperTranscriber
from diarizer import prep_NeMo, run_NeMo
from rttm_combiner import SegmentCombiner
from punctuation_realignment import (
    get_realigned_ws_mapping_with_punctuation,
    get_sentences_speaker_mapping,
    save_diarized_transcript,
)

"""
* The user should decide:
    * whether to split the audio file or not.
    * if the audio file is split, how long each split should be.
    * if the audio file is split, how much overlap there should be between each split.

* provide json config file for user to set these parameters
"""

if __name__ == "__main__":

    APP_NAME = "Speaker Diarization"
    LOG_NAME = "Main"
    OUTPUT_DIR = "output"

    parser = argparse.ArgumentParser(
        prog=APP_NAME,
        description="Speaker Diarization using Whisper and NeMo",
        )

    #pylint: disable=line-too-long
    parser.add_argument("-i", "--input", type=str, default="input.wav", help="Path to audio file, default input.wav")
    parser.add_argument("-o", "--output", type=str, default=None, help="Path to output directory, no default")
    parser.add_argument("-m", "--model", type=str, default="medium", help="Whisper model to use, default medium")
    parser.add_argument("-l", "--language", type=str, default="en", help="Language to use, default english (en)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--split-length", type=int, default=3600, help="audio split length in seconds")
    parser.add_argument("--split-overlap", type=int, default=300, help="audio split overlap in seconds")
    #pylint: enable=line-too-long

    args = parser.parse_args()

    cwd = Path.cwd()

    # add date to log file
    now = datetime.now(timezone.utc)
    log_file = "log_" + now.strftime("%Y%m%d_%H%M%S") + ".log"

    configure_logging(
        filename=log_file,
        log_to_file=True, 
        verbose=args.verbose
        )
    logger = logging.getLogger(LOG_NAME)
    logger.info("%s: starting", APP_NAME)
    
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info("Using device: %s", DEVICE)

    MODEL_SIZE = args.model
    logger.info("Using model: %s", MODEL_SIZE)

    LANGUAGE = args.language
    logger.info("Using language: %s", LANGUAGE)
    #TODO: problem, this defaults to english, not None

    AUDIO_IN = args.input
    # check if file exists
    if not Path(AUDIO_IN).is_file():
        message = "Input file not found: %s", AUDIO_IN
        logger.error(message)
        raise FileNotFoundError(message)

    logger.info("Using file: %s", AUDIO_IN)
    audio_in = Path(AUDIO_IN)

    #TODO check that OUTPUT_DIR is actually a directory and that it exists
    OUTPUT_DIR = args.output
    if OUTPUT_DIR is None:
        raise ValueError("Output directory not specified")
    elif not Path(OUTPUT_DIR).is_dir():
        raise FileNotFoundError("Output directory not found")
    output_dir = Path(OUTPUT_DIR)
    logger.info("Using output directory: %s", output_dir)
    temp_uuid = uuid4()
    output_temp_dir = output_dir / str(temp_uuid)
    output_temp_dir.mkdir()
    logger.debug("Using temp directory: %s", output_temp_dir)

    #TODO: instead of a uuid, use the input file name so we can use checkpoints to resume

    # TODO verify or parse these variables into correct format
    split_length_s = args.split_length
    logger.info("Using split length (seconds): %s", split_length_s)
    split_overlap_s = args.split_overlap
    logger.info("Using split overlap (seconds): %s", split_overlap_s)

    # Above this is config and setup

    # ------- METADATA -------

    metadata = TinyTagAudioMetadata("Metadata", audio_in)
    #TODO debug log metadata

    # ------- 16K CONVERSION -------

    audio_16k, log = ffmpeg_to_16k(audio_in, output_temp_dir)
    logger.info("Converted audio to 16k: %s", audio_16k)
    logger.debug("FFmpeg log: %s", log)

    # ------- SPLIT -------

    if metadata.duration_s > split_length_s:
        audio_splitter = FFmpegSplitter(
            "FFmpegSplitter",
            audio_16k,
            output_temp_dir,
            metadata.duration_s,
            split_length_s,
            split_overlap_s,
        )
        input_splits = audio_splitter.split()
    else:
        input_splits = [audio_16k]
    
    # ------- WHISPER -------

    transcriber = WhisperTranscriber(
        # "WhisperTranscriber",
        audio_in=audio_16k,
        model_size=MODEL_SIZE,
        device=DEVICE,
        language=LANGUAGE,
        )

    timestamped_words = transcriber.transcribe()
    timestamped_words_filepath = transcriber.save_transcript(timestamped_words, output_dir)

    # ------- NEMO -------
    rttm_splits = []
    for split in input_splits:
        nemo_config = prep_NeMo(split, output_temp_dir)
        rttm_file = run_NeMo(nemo_config, split)
        rttm_splits.append(rttm_file)

    # ------- SEGMENT COMBINE RTTM -------

    rttm_output_file_path = rttm_splits[0]
    for i in range(1, len(rttm_splits)):
        rttm_file_path_2 = rttm_splits[i+1]
        
        SIGNAL_QUALITY_S = 0.1

        segcom = SegmentCombiner(
        rttm_output_file_path,
        rttm_file_path_2,
        output_temp_dir,
        split_length_s,
        split_overlap_s,
        SIGNAL_QUALITY_S
        )
        rttm_output_file_path = segcom.run()

    rttm_output_file_path = rttm_output_file_path.rename(output_dir / "combined_output.rttm")

    # ------- COMBINE WORDS AND RTTM -------

    # timestamped_words_filepath = Path("/home/gdoerksen/repos/PodcastTranscription/output/C1E2_IntoTheMuck_16k.txt")

    #TODO already have timestamped_words
    words = load_word_timestamps(timestamped_words_filepath)
    speakers = load_rttm_file(rttm_output_file_path)

    combined_words_and_speakers = get_words_speaker_mapping(words, speakers, 'start')   


    # ------- REALIGNMENT VIA PUNCTUATION -------`  

    wsm = get_realigned_ws_mapping_with_punctuation(combined_words_and_speakers)
    ssm = get_sentences_speaker_mapping(wsm, speakers)
    save_diarized_transcript(ssm)


    pass

    """
    ssm {'speaker': f'Speaker {spk}', 'start_time': start, 'end_time': end, 'text': ''}
    """

    #TODO: output WebVTT file 
