import sys
from conversion.abc2audio import abc2wav_writing

print(abc2wav_writing(sys.argv[1], "a.midi", "a.wav").reason)