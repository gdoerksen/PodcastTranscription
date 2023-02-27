from pathlib import Path
import json

import whisper
import whisperx

class WhisperTranscriber:

    def __init__(
        self,
        audio_in: Path, 
        model_size: str,
        device: str,
        language : str = None,
        beam_size: int = None,

        ):
        self.audio_in = audio_in
        self.model_size = model_size
        self.device = device
        self.language = language
        self.beam_size = beam_size
        

    def transcribe(self):
        """Transcribe audio file using Whisper model and align the results using WhisperX"""

        audio_in_str = str(self.audio_in)

        options = {
            "language": self.language,
            "beam_size": self.beam_size,
        }

        model = whisper.load_model(self.model_size, device=self.device )
        results = model.transcribe(audio_in_str, **options) 

        if self.language is None:
            self.language = results["language"]

        alignment_model, metadata = whisperx.load_align_model(language_code=self.language, device=self.device)
        result_aligned = whisperx.align(results["segments"], alignment_model, metadata, audio_in_str, self.device)

        return result_aligned
    
    def save_transcript(self, transcription, output_dir: Path):
        """Save transcript to file"""

        filename = output_dir / f'{self.audio_in.stem}.txt'
        
        with open(filename, 'w+') as f:
            for line in transcription['word_segments']:
                line_temp = line.copy()
                line_temp['text'] = line_temp['text'].strip()
                f.write(f'{json.dumps(line_temp)}\n')

    def load_transcript(self, output_dir: Path):
        """Load transcript from file"""

        filename = output_dir / f'{self.audio_in.stem}.txt'
        
        with open(filename, 'r') as f:
            lines = f.readlines()
            lines = [json.loads(line) for line in lines]

        return lines