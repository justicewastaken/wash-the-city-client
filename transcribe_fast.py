#!/usr/bin/env python3
import sys
from faster_whisper import WhisperModel

def transcribe(audio_path, model_size="tiny", device="cpu", compute_type="int8"):
    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    segments, info = model.transcribe(audio_path, beam_size=5)
    text = ""
    for segment in segments:
        text += segment.text + " "
    return text.strip()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: transcribe_fast.py <audio_file> [model_size]")
        sys.exit(1)
    audio_path = sys.argv[1]
    model_size = sys.argv[2] if len(sys.argv) > 2 else "tiny"
    result = transcribe(audio_path, model_size=model_size)
    print(result)
