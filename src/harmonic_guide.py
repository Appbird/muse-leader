from datetime import datetime
from io import TextIOWrapper
from os import makedirs
from pathlib import Path
import re

from LLM.OpenAI import GPT, Model
from sequence.add_chord_comments import insert_midi_chords
from utility.load_prompts import load_prompt
from conversion.answer2abc import extract_abc_score
from conversion.abc2audio import abc2wav_writing
from utility.important_path import get_same_name_file, RESULT
from utility.time_measurement import Stopwatch
from sequence.param2prompt import form_table, input_table

MODEL = Model.gpt_4o_2024_08_06
EXE_DATETIME = datetime.now()
leader_prompt_textfile = "leader.txt"
melody_prompt_textfile = "melody_agent.txt"
chord_prompt_textfile = "chord_agent.txt"
simple_prompt_textfile = "simple.txt"
instrument_prompt_textfile = "instrument_agent.txt"


def write_condition_section(log:TextIOWrapper):
    date = EXE_DATETIME.strftime("%Y-%m-%d %H:%M:%S")
    log.write(
        f"# Experimental Conditions\n"
        f"|Params|value|\n" +
        f"|---|---|\n" +
        f"|date|\t{ date }|\n" +
        f"|all model|\t{MODEL.value}|\n" + 
        f"|leader prompt|\t{MODEL.value}|\n" +
        f"|composer_textfile|\t{MODEL.value}|\n" +
        "\n" +
        "\n"
    )

def write_new_message(log:TextIOWrapper, who:str, message:str):
    log.write(f"# {who}  \n{message}\n\n")

def emmbedding_param_into_prompt(base_prompt:str, params:dict[str, str]) -> str:
    for (param_name, value) in params.items():
        base_prompt = base_prompt.replace("${"+ param_name +"}", value)
    return base_prompt

def error_correction(score:str):
    in_chord_name = False
    before_soundname = False
    score_list = list(score)
    for i in range(len(score_list)):
        if score[i] == '"': in_chord_name = not in_chord_name
        if not in_chord_name:
            if before_soundname:
                if score[i] == '#' :
                    score_list[i] = '^'
                    score_list[i-1], score_list[i] = score_list[i], score_list[i-1] 
                if score[i] == 'b' :
                    score_list[i] = '_'
                    score_list[i-1], score_list[i] = score_list[i], score_list[i-1] 
                before_soundname = False
                continue
            before_soundname = score[i].isalpha()
    return "".join(score_list)



def experiment(dst:Path, param_axis:str, values:list[list[float]]):
    actual_dst = dst.parent/f"{dst.stem}"
    makedirs(actual_dst, exist_ok=True)
    base_score="""
以下の曲をベースとして、編集を行なってください。
```
X: 1
T: Classical Balance
M: 4/4
L: 1/4
Q: 1/4=120
K: C
V:1
%%MIDI gchord b2b2
%%MIDI program 1 % ピアノ
%%MIDI chordprog 48 % 弦楽四重奏
%%MIDI bassprog 45 % ピチカート・ストリングス (ベース)
| "C" E2 G2 | "F" F3 A | "G" G2 E2 | "C" C4 | % measure 1-4
%%MIDI program 1
%%MIDI chordprog 48
%%MIDI bassprog 45
| "Dm" D2 E2 | "G" G3 F | "C" E2 D2 | "C" C4 | % measure 5-8
%%MIDI program 1
%%MIDI chordprog 79
%%MIDI bassprog 45
| "Am" A,2 C2 | "Dm" D3 F | "G" G2 E2 | "C" C4 | % measure 9-12
%%MIDI program 1
%%MIDI chordprog 48
%%MIDI bassprog 45
| "C" E2 G2 | "G" G3 D | "Dm" F2 D2 | "C" C4 | % measure 13-16
```
"""
    leader = GPT(MODEL, load_prompt(leader_prompt_textfile))
    melody_agent = GPT(MODEL, load_prompt(melody_prompt_textfile))
    chord_agent = GPT(MODEL, load_prompt(chord_prompt_textfile))
    instrument_agent = GPT(MODEL, load_prompt(instrument_prompt_textfile))
    count = 0
    leader.tell(base_score)
    with open(actual_dst/"experiments.log.md", "w") as log:
        write_condition_section(log)
        for param_list in values:
            sw = Stopwatch()
            sw.start()
            param_table = form_table(param_axis, param_list)
            if param_table == None: break
            write_new_message(log, "user", param_table)
            print("INFO > start composing!")
            
            leader.tell(param_table)
            leader_message = leader.ask(True)
            write_new_message(log, "leader", leader_message)
            print("INFO > leader answered.")

            chord_agent.tell(leader_message)
            chord_msg = chord_agent.ask(True)
            write_new_message(log, "chord", chord_msg)
            print("INFO > chord answered.")
            
            melody_agent.tell(leader_message)
            melody_agent.tell(chord_msg)
            melody_msg = melody_agent.ask(True)
            write_new_message(log, "melody", melody_msg)
            print("INFO > melody answered.")

            instrument_agent.tell(leader_message)
            instrument_agent.tell(melody_msg)
            instrument_msg = instrument_agent.ask(True)
            write_new_message(log, "instrument", instrument_msg)
            print("INFO > instrument answered.")
            
            
            (result, score) = extract_abc_score(instrument_msg)
            if not result.is_ok():
                print(result.reason)
                return
            # print(score)
            score = insert_midi_chords(score)
            # print("# after error correction")
            # print(score)
            abc_path = actual_dst/f"composition-{count}.abc"
            with open(abc_path, "w") as f: f.write(score)
            result = abc2wav_writing(
                str(get_same_name_file(abc_path, "abc")),
                str(get_same_name_file(abc_path, "midi")),
                str(get_same_name_file(abc_path, "wav"))
            )
            write_new_message(log, "compiler", result.reason)
            print(result.reason)
            log.write(f"TIME: {sw.measure():.2f}\n\n")
            count += 1
        return 0


if __name__ == "__main__":
    FOLDER_NAME = "ifip-icec2025"
    axis_list = [
        "厳かな", "明るさ", "春", "気まぐれな", "クラシック感", "ジャズ感"
    ]
    params = [
        [0.5, 0.5, 0.75, 0.4]
    ]
    for axis_name in axis_list:
        target_path = RESULT(FOLDER_NAME, EXE_DATETIME, axis_name)
        experiment(target_path, axis_name, params)
