import logging
import argparse
from datetime import datetime, timezone
from pathlib import Path

import torch
import whisper

from utils import configure_logging
from metadata import TinyTagAudioMetadata

if __name__ == "__main__":

    APP_NAME = "Speaker Diarization"
    LOG_NAME = "Main"
    OUTPUT_DIR = "output"

    parser = argparse.ArgumentParser(
        prog=APP_NAME,
        description="Speaker Diarization using Whisper and NeMo",
        )

    parser.add_argument("-i", "--input", type=str, default="input.wav", help="Path to audio file, default input.wav")
    parser.add_argument("-o", "--output", type=str, default=None, help="Path to output file, no default")
    parser.add_argument("-m", "--model", type=str, default="medium", help="Whisper model to use, default medium")
    parser.add_argument("-l", "--language", type=str, default="en", help="Language to use, default english (en)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

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

    AUDIO_IN = args.input
    logger.info("Using file: %s", AUDIO_IN)
    audio_in = Path(AUDIO_IN)


    metadata = TinyTagAudioMetadata("Metadata", audio_in)

    pass 







    # TODO convert to 16k wav so that NeMo works 
    # TODO convert to mono 
    # Consider 44100? 
    # ffmpeg -i .\C1E2_IntoTheMuck.mp3 -vn -acodec pcm_s16le -ac 1 -ar 16000 -f wav foo16.wav

    # model = whisper.load_model(MODEL_SIZE, device=DEVICE)

    # # RUN WHISPER
    # # TODO check if output file already exists

    # results = model.transcribe(FILE, beam_size=None)
    # """
    # Beam size if None by default (Greedy Decoding). You can also set the
    # beam_size to some number like 5. This will increase in better transcription
    # quality but it'll increase runtime considerabley.
    # """

    # if args.output is None:
    #     # create output file name
    #     input = Path(args.input)
    #     output = input.stem + ".txt"
    #     output_path = cwd / OUTPUT_DIR / output
    # else:
    #     output_path = cwd / OUTPUT_DIR / args.output
    # # save results object to file
    # with open(str(output_path), "w") as f:
    #     f.write(str(results))

    # output_path = cwd / OUTPUT_DIR / "output2.txt"
    # # save results text to file
    # with open(str(output_path), "w") as f:
    #     f.write(results["text"])


