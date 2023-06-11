
class WebVTTConverter:
    def __init__(self, ssm, output_dir):
        self.ssm = ssm
        self.output_dir = output_dir
        
        self._output_list = []

    def run(self):
        self.convert()
        return self.output_dir
    
    def convert(self):
        for sentence in self.ssm:
            self._write_line(sentence)

    def _write_line(self, sentence: dict):
        """
        Takes a sentence and converts it to a line of WebVTT format.
        """

        start_time = sentence['start_time']
        start_time = self._seconds_to_time(start_time)
        end_time = sentence['end_time']
        end_time = self._seconds_to_time(end_time)
        speaker = sentence['speaker']
        text = sentence['text']

        self._output_list.append(f'{start_time} --> {end_time}')
        self._output_list.append(f'<v {speaker}>{text}')
        self._output_list.append('')

    def _seconds_to_time(self, input_seconds: float)->str:
        """
        Converts seconds to WebVTT time format.
        """

        minutes = int(input_seconds // 60)
        seconds = int(input_seconds % 60)
        milliseconds = int((input_seconds % 1) * 1000)

        return f'{minutes:02d}:{seconds:02d}.{milliseconds:03d}'


