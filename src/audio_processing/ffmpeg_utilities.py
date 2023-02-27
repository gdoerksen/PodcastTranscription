from subprocess import run
from pathlib import Path

def ffmpeg_to_16k(input_file: Path, output_directory: Path)->tuple[Path, str]:
    output_file = output_directory / (input_file.stem + "_16k.wav")
    command_line = f"ffmpeg -i {input_file} -vn -acodec pcm_s16le -ac 1 -ar 16000 -f wav {output_file}\n"
    command = command_line.split()
    log = run(command, capture_output=True)
    return output_file, log