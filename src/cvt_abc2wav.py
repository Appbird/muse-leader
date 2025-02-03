from pathlib import Path
import sys

from conversion.abc2audio import abc2wav_writing
from conversion.validate_abc import validate_abc

print(abc2wav_writing(sys.argv[1], "a.midi", "a.wav").reason)