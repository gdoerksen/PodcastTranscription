from pathlib import Path
import math

import pandas as pd


class SegmentCombiner: 
    def __init__(
        self, 
        rttm_file_path_1 : Path, # pure path to the first segment file
        rttm_file_path_2 : Path, # pure path to the second segment file
        output_dir : Path, # pure path to the output directory
        duration_no_overlap_s: float = 3600.0, 
        duration_overlap_s: float = 300.0,
        signal_quality_s: float = 0.1
        ):
        # injected
        self.rttm_file_path_1 = rttm_file_path_1
        self.rttm_file_path_2 = rttm_file_path_2
        self.output_dir = output_dir
        self.duration_no_overlap_s = duration_no_overlap_s
        self.duration_overlap_s = duration_overlap_s
        self.signal_quality_s = signal_quality_s

        # derived
        self.first_overlap_cutoff_s = duration_no_overlap_s - duration_overlap_s # seconds
        self.second_overlap_cutoff_s = duration_overlap_s # seconds

    def load_rttm(self, file_path: Path):
        columnn_names = ['type', 'file', 'channel', 'start_s', 'duration_s', 'NA1', 'NA2', 'speaker', 'NA3', 'NA4']
        sep = '\s+'
        
        # Read in the .rttm file
        df = pd.read_csv(file_path, 
                    sep=sep, 
                    header=None, 
                    names=columnn_names,
                    index_col=False
                    )
        return df

    def preprocess_rttm(self, df: pd.DataFrame, is_first_segment: bool):
        df = df.copy()
        # df = df.drop(columns=['type', 'channel', 'NA1', 'NA2', 'NA3', 'NA4'])
        df = df.assign(end_s=df['start_s'] + df['duration_s'])

        if is_first_segment:
            df = df[df['start_s'] > self.first_overlap_cutoff_s]
        else:
            df = df[df['start_s'] < self.second_overlap_cutoff_s]

        return df

    def to_signal(self, df: pd.DataFrame) -> pd.DataFrame:
        '''
        This function converts a .rttm pandas df to signals bounded 
        between 0 and 1. 
        '''
        signal_length_s = self.duration_overlap_s
        signal_index_length = int(signal_length_s / self.signal_quality_s) # 3000
        signal_multiplier = int(1/self.signal_quality_s) # 10
        rounding_precision = int(-1*math.log10(self.signal_quality_s)) # 1

        # get the number of speakers 
        num_speakers = df['speaker'].nunique()
        columns = ['speaker_' + str(i) for i in range(num_speakers)]

        signal_df = pd.DataFrame(index=range(signal_index_length), columns=columns, data=0)

        # Loop through each speaker
        for i in range(num_speakers):
            speaker_str = 'speaker_' + str(i)
            slice = df[df['speaker'] == speaker_str ]

            # Get the start and end times of the speaker
            start = slice['start_s'].round(rounding_precision).mul(signal_multiplier).astype(int)
            end = slice['end_s'].round(rounding_precision).mul(signal_multiplier).astype(int)

            temp_df = pd.DataFrame([start, end]).T
            if temp_df.max().max() > (signal_index_length*2): 
                #TODO I'm sure this magic *2 will come back to bite me, could cause float to int comparison issues
                #TODO dum hack lol
                temp_df = temp_df.sub( int((self.duration_no_overlap_s-signal_length_s)/self.signal_quality_s) )

            for row in temp_df.itertuples(index=False):
                signal_df[speaker_str][row[0]:row[1]] = 1
                #TODO this is slow, but unsure how to vectorize it
        
        return signal_df       

    def signal_correlation(self, signal_1: pd.DataFrame, signal_2: pd.DataFrame) -> pd.DataFrame:
        """
        Computes the correlation between two sets of speaker signals and returns a dataframe of the results
        """

        s1s = signal_1.shape[1]
        s2s = signal_2.shape[1]
        matrix = pd.DataFrame(index=range(s1s), columns=range(s2s), data=0)

        # for each speaker, get the correlation between the two signals
        for i in range(s1s):
            for j in range(s2s):
                # We can optimize via pyramid
                result = signal_1['speaker_' + str(i)].mul(signal_2['speaker_' + str(j)]).sum()
                # place result in matrix
                matrix.iloc[i, j] = result # TODO order? 
        
        '''
        Observation: 
        If not all the expected speakers are in the overlapping signal then we are probably boned 

        '''
        return matrix

    def assign_speakers(self, correlation_matrix: pd.DataFrame) -> dict:
        # get the max correlation for each speaker
        speaker_assignments = {}
        result = correlation_matrix.idxmax(axis=1) 
        if not result.is_unique:
            raise Exception('Multiple max correlations for a speaker')
        for i in range(len(result)):
            speaker_assignments['speaker_' + str(result[i])] = 'speaker_' + str(i)
        return speaker_assignments

    def run(self)->Path:
        rttm_1_df = self.load_rttm(self.rttm_file_path_1) #TODO str on path? 
        rttm_2_df = self.load_rttm(self.rttm_file_path_2) #TODO str on path? 

        overlap_1_df = self.preprocess_rttm(rttm_1_df, is_first_segment=True)
        overlap_2_df = self.preprocess_rttm(rttm_2_df, is_first_segment=False)

        signal_1 = self.to_signal(overlap_1_df)
        signal_2 = self.to_signal(overlap_2_df)

        correlation_matrix = self.signal_correlation(signal_1, signal_2)
        speaker_assignments = self.assign_speakers(correlation_matrix)

        # replace the speaker names in the second segment with the assigned names
        # rttm_2_df['new_speaker'] = rttm_2_df['speaker'].map(speaker_assignments) #TODO for multi combine
        rttm_2_df['speaker'] = rttm_2_df['speaker'].map(speaker_assignments)

        # combine the two segments

        ## need to remove the overlap from the second segment
        index = rttm_2_df[rttm_2_df['start_s'] > self.second_overlap_cutoff_s].index[0]
        index -= 1 
        temp = self.duration_overlap_s - rttm_2_df.iloc[index]['start_s']
        new_line_duration_s = rttm_2_df.iloc[index]['duration_s'] - temp

        rttm_2_df.at[index, 'start_s'] = self.duration_overlap_s
        rttm_2_df.at[index, 'duration_s'] = new_line_duration_s

        rttm_2_df['start_s'] = rttm_2_df['start_s'].add(self.first_overlap_cutoff_s)

        combined = pd.concat([rttm_1_df, rttm_2_df.iloc[index:]  ], ignore_index=True)

        output_file_path = self.output_dir / (self.rttm_file_path_1.stem + '_combined.rttm')

        # write the combined segment to a file
        combined.to_csv(
            output_file_path, 
            sep=' ', 
            header=False, 
            index=False, 
            float_format='%.3f',
            na_rep='<NA>')

        return output_file_path