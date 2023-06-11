import os
import json
from pathlib import Path

from omegaconf import OmegaConf
import wget 
from nemo.collections.asr.models.msdd_models import ClusteringDiarizer

def prep_NeMo(audio_in: Path, output_dir: Path):

    manifest = 'manifest.json'
    manifest_path = output_dir / manifest

    diarize_manifest = {
        'audio_filepath': str(audio_in),
        'offset': 0,
        'duration':  None,
        'label': "infer",
        'text': "-",            
        'num_speakers': None,           #TODO should be set if we know it
        'rttm_filepath': None,          # Is this actually required?
        'uniq_id': "",
    }   

    # if not manifest_path.exists():
    with manifest_path.open('w') as f:
        f.write(json.dumps(diarize_manifest))

    model_config = output_dir / 'diar_infer_meeting.yaml'
    if not model_config.exists():
      config_url = "https://raw.githubusercontent.com/NVIDIA/NeMo/main/examples/speaker_tasks/diarization/conf/inference/diar_infer_meeting.yaml"
      model_config = wget.download(config_url, str(output_dir))

    #TODO save model config to output_dir and load it from there

    config = OmegaConf.load(model_config)
    #TODO could load this with yaml

    config.num_workers = 4
    config.batch_size = 32

    config.diarizer.manifest_filepath = str(manifest_path)
    config.diarizer.out_dir = str(output_dir / 'diarized')
    config.diarizer.speaker_embeddings.model_path = 'titanet_large'
    config.diarizer.speaker_embeddings.parameters.window_length_in_sec = [1.5, 1.0, 0.5]
    config.diarizer.speaker_embeddings.parameters.shift_length_in_sec = [0.75, 0.5, 0.25]
    config.diarizer.speaker_embeddings.parameters.multiscale_weights = [0.33, 0.33, 0.33]
    config.diarizer.speaker_embeddings.parameters.save_embeddings = False

    config.diarizer.ignore_overlap = False
    config.diarizer.oracle_vad = False
    config.diarizer.collar = 0.25


    config.diarizer.vad.model_path = 'vad_multilingual_marblenet'
    config.diarizer.oracle_vad = False # TODO: Not using oracle VAD, but should we? 

    return config 

def run_NeMo(config, audio_in:Path)->Path:
    """
    Runs the NeMo diarization model. Output is saved based on prep_NeMo() config.
    """
    
    model = ClusteringDiarizer(cfg=config)
    model.diarize()
    rttm_file = Path(config.diarizer.out_dir) / 'pred_rttms' / (audio_in.stem + '.rttm')

    #TODO move to temp dir to prevent overwriting on next 
    # rttm_file.replace(audio_in.parent / (audio_in.stem + '.rttm'))

    return rttm_file

    # diarizer = SpeakerDiarizer(cfg=config.diarizer)
    # diarizer.diarize()