"""Build the illustrative dialogue with sherpa-onnx 1.12.26 and English Kokoro v0.19."""
from argparse import ArgumentParser
from pathlib import Path
import subprocess
import sys
import tempfile
import wave

import numpy as np
import sherpa_onnx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from content import STORIES

def main():
    parser = ArgumentParser()
    parser.add_argument('model', type=Path, help='Directory containing the English Kokoro int8 model and voices')
    parser.add_argument('--story', choices=STORIES, help='Build dialogue for one example only')
    args = parser.parse_args()
    path = args.model
    kokoro = sherpa_onnx.OfflineTtsKokoroModelConfig(
        model=str(path/'model.int8.onnx'), voices=str(path/'voices.bin'),
        tokens=str(path/'tokens.txt'), data_dir=str(path/'espeak-ng-data'),
    )
    engine = sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(
        model=sherpa_onnx.OfflineTtsModelConfig(kokoro=kokoro, num_threads=3),
        max_num_sentences=1, silence_scale=.30,
    ))
    rate = engine.sample_rate
    def speak(text, speaker):
        samples = np.asarray(engine.generate(text, sid=speaker, speed=.99).samples, dtype=np.float32)
        if not len(samples):
            raise RuntimeError('The model did not return audio for '+text)
        active = np.flatnonzero(np.abs(samples) > .006)
        if len(active):
            samples = samples[max(0,active[0]-int(.075*rate)):min(len(samples),active[-1]+int(.14*rate))]
        fade = np.linspace(0,1,min(int(.018*rate),len(samples)//2))
        samples[:len(fade)] *= fade
        samples[-len(fade):] *= fade[::-1]
        return samples / max(.45, float(np.max(np.abs(samples)))) * .62
    def export(samples, path):
        with tempfile.TemporaryDirectory() as tmp:
            wav=Path(tmp)/'mix.wav'
            with wave.open(str(wav),'wb') as output:
                output.setparams((1,2,rate,0,'NONE','not compressed'))
                output.writeframes((samples.clip(-1,1)*32767).astype('<i2').tobytes())
            subprocess.run(['ffmpeg','-v','error','-y','-i',str(wav),'-af',
                            'highpass=f=65,lowpass=f=8000,loudnorm=I=-20:TP=-2.5:LRA=7',
                            '-ar','44100','-codec:a','libmp3lame','-b:a','80k',str(path)],check=True)
    speakers = {'service':(3,6),'property':(9,0),'business':(0,6),'clinic':(1,7)}
    numbers = {'94103':'nine four one zero three', 'ZIP':'zip', 'AC':'A C', '10 AM':'ten a.m.'}
    for key,story in STORIES.items():
        if args.story and args.story!=key:
            continue
        for scene,step in enumerate(story['steps'][:2]):
            lines=[]
            for line,voice in zip((step[4],step[6]),speakers[key]):
                for original,spoken in numbers.items():
                    line=line.replace(original,spoken)
                lines.append(speak(line,voice))
            mix=np.concatenate((np.zeros(round(.10*rate)),lines[0],np.zeros(round(.28*rate)),lines[1],np.zeros(round(.08*rate))))
            export(mix,ROOT/'dist/media'/f'sample-{key}-{scene}.mp3')
    if args.story:
        return
    film=np.zeros(rate*18,dtype=np.float32)
    for time,voice,line in [(.78,3,'My A C stopped cooling. Can I get a visit tomorrow?'),
                            (5.92,6,'What’s your zip code? And does tomorrow morning work?')]:
        data=speak(line,voice)
        start=round(time*rate)
        film[start:start+len(data)]=data
    export(film,ROOT/'art'/'film-dialogue.mp3')

if __name__=='__main__':
    main()
