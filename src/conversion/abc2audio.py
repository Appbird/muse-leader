import subprocess
import sys
from pathlib import Path
from utility.Result import ResultConversion, ProcessState, ResultOK
from utility.important_path import get_same_name_file

def write_midi_from_abc_with_abc2midi(abc_file_path:str, midi_file_path:str) -> ResultConversion:
    sbp = subprocess.Popen(["abc2midi", abc_file_path, '-o', midi_file_path],
        stdout=subprocess.PIPE,
        cwd=Path.cwd()
    )
    out, _ = sbp.communicate()
    try:
        stdout_content = out.decode('utf-8')
    except UnicodeDecodeError:
        stdout_content = "Failed to decode stdout; UnicodeDecodeError."
    if any([line.startswith("Error") for line in stdout_content.splitlines()]): return ResultConversion(ProcessState.FAILED_ABC2MIDI, stdout_content)
    if any([line.startswith("Warning") for line in stdout_content.splitlines()]): return ResultConversion(ProcessState.OK, stdout_content)
    return ResultOK()



def write_midi_from_abc_with_abcjs(abc_file_path:str, midi_file_path:str) -> ResultConversion:
    sbp = subprocess.Popen(["npm", "run", "app", abc_file_path, midi_file_path],
        stdout=subprocess.PIPE,
        cwd=Path.cwd()
    )
    out, _ = sbp.communicate()
    try:
        stdout_content = out.decode('utf-8')
    except UnicodeDecodeError:
        stdout_content = "Failed to decode stdout; UnicodeDecodeError."
    if any([line.startswith("Error") for line in stdout_content.splitlines()]): return ResultConversion(ProcessState.FAILED_ABC2MIDI, stdout_content)
    if any([line.startswith("Warning") for line in stdout_content.splitlines()]): return ResultConversion(ProcessState.OK, stdout_content)
    return ResultOK()

def write_wav_from_midi(midi_file_path:str, wav_file_path:str, gain:float) -> ResultConversion:
    sound_font_path = str(Path.cwd()/"sf2/GeneralUser_GS_1.471/GeneralUser_GS_v1.471.sf2")
    sbp = subprocess.Popen([
            "fluidsynth",
            # Render MIDI file to raw audio data and store in [file]
            "-F", wav_file_path,
            # Set the master gain [0 < gain < 10, default = 0.2]
            "-g", str(gain),
            # Do not print welcome message or other informational output
            "-q",
            sound_font_path,
            midi_file_path,
        ],
        stderr=subprocess.PIPE,
        cwd=Path.cwd()
    )
    _, err = sbp.communicate()
    return ResultOK() if sbp.returncode == 0 else ResultConversion(ProcessState.FAILED_MIDI2WAV, err.decode('utf-8'))


def abc2wav_writing(input_abc_path:str, midi_file:str, wav_file:str) -> ResultConversion:
    result1 = write_midi_from_abc_with_abc2midi(input_abc_path, midi_file)
    if not result1.is_ok() : return result1
    
    result2 = write_wav_from_midi(midi_file, wav_file, 1)
    if not result2.is_ok() : return result2

    return result2 if len(result1.reason) == 0 else ResultConversion(ProcessState.OK, result1.reason + result2.reason)


if __name__ == "__main__":

    print(abc2wav_writing(
        sys.argv[1],
        get_same_name_file(Path(sys.argv[1]), "midi").name,
        get_same_name_file(Path(sys.argv[1]), "wav").name
    ).reason)