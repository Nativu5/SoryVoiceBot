from . import snowboydecoder

def get_detector(model, sensitivity=0.5):
    return snowboydecoder.HotwordDetector(decoder_model=model, sensitivity=sensitivity)
