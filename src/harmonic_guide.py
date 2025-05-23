from collections import deque
from datetime import datetime
from io import TextIOWrapper
import json
from os import makedirs
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import random

from LLM.Anthropic import Claude
from LLM.OpenAI import GPT, Model
from sequence.add_chord_comments import insert_midi_chords
from utility.error_corrections import error_correction
from utility.logger import write_new_message
from utility.load_prompts import load_prompt
from conversion.answer2abc import extract_abc_score
from conversion.abc2audio import abc2wav_writing
from utility.important_path import CONCUR_RESULT, get_same_name_file
from utility.time_measurement import Stopwatch
from sequence.param2prompt import form_table

MODEL = Model.gpt_4_1_2025_04_14
EXE_DATETIME = datetime.now()
naive_prompt_textfile = "naive.txt"
leader_prompt_textfile = "leader.txt"
melody_prompt_textfile = "melody_agent.txt"
chord_prompt_textfile = "chord_agent.txt"
simple_prompt_textfile = "simple.txt"
instrument_prompt_textfile = "instrument_agent.txt"

FOLDER_NAME = "gpt4-1"
TRIAL_COUNT = 3
axis_list = [
	# based on MusicCaps top 10 Genre
	"Electronic",
	"Classical", "Rock", "Country",
	"Blues", "Music for children", "New-age music", "Jazz",
	"Latin America", "Hip hop"
]

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
def experiment_naive(dst:Path, param_axis:str, values:list[list[float]]):
	actual_dst = dst.parent/f"{dst.stem}"
	makedirs(actual_dst, exist_ok=True)
	composer = GPT(MODEL, load_prompt(naive_prompt_textfile))
	count = 0
	abc_scores:list[dict] = []
	with open(actual_dst/"experiments.log.md", "w") as log:
		write_condition_section(log)
		for param_list in values:
			sw = Stopwatch()
			sw.start()
			param_table = form_table(param_axis, param_list)
			if param_table == None: break
			write_new_message(log, "user", param_table)
			print("INFO > start composing!")
			
			composer.tell(param_table)
			composer_msg = composer.ask(True)
			write_new_message(log, "composer", composer_msg)
			print("INFO > naive answered.")

			(result, original_score) = extract_abc_score(composer_msg)
			if not result.is_ok():
				print(result.reason)
				return abc_scores
			score = error_correction(original_score)
			score = insert_midi_chords(score)

			abc_path = actual_dst/f"composition-{count}.abc"
			with open(abc_path, "w") as f: f.write(score)
			result = abc2wav_writing(
				str(get_same_name_file(abc_path, "abc")),
				str(get_same_name_file(abc_path, "midi")),
				str(get_same_name_file(abc_path, "wav"))
			)
			write_new_message(log, "compiler", result.reason)
			print(result.reason)
			abc_scores.append({
				"score": score,
				"original_score": original_score,
				"compiler": result.reason,
				"param": param_list
			})
			log.write(f"TIME: {sw.measure():.2f}\n\n")
			count += 1
		return abc_scores

def experiment(dst:Path, param_axis:str, values:list[list[float]]):
	actual_dst = dst.parent/f"{dst.stem}"
	makedirs(actual_dst, exist_ok=True)
	leader = GPT(MODEL, load_prompt(leader_prompt_textfile))
	melody_agent = GPT(MODEL, load_prompt(melody_prompt_textfile))
	chord_agent = GPT(MODEL, load_prompt(chord_prompt_textfile))
	instrument_agent = GPT(MODEL, load_prompt(instrument_prompt_textfile))
	count = 0
	abc_scores:list[dict] = []
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
			
			
			(result, original_score) = extract_abc_score(instrument_msg)
			if not result.is_ok():
				print(result.reason)
				return abc_scores
			score = error_correction(original_score)
			score = insert_midi_chords(score)

			abc_path = actual_dst/f"composition-{count}.abc"
			with open(abc_path, "w") as f: f.write(score)
			result = abc2wav_writing(
				str(get_same_name_file(abc_path, "abc")),
				str(get_same_name_file(abc_path, "midi")),
				str(get_same_name_file(abc_path, "wav"))
			)
			write_new_message(log, "compiler", result.reason)
			print(result.reason)
			abc_scores.append({
				"score": score,
				"original_score": original_score,
				"compiler": result.reason,
				"param": param_list
			})
			log.write(f"TIME: {sw.measure():.2f}\n\n")
			count += 1
		return abc_scores

def make_params(change_prob=0.5):
	# param[0]: 元のパラメータ
	choices1 = [1.0, 0.5, 0.0]
	p0 = [random.choice(choices1) for _ in range(4)]
	
	# param[1]: p0 をベースにランダム変更。ただし値域は choices2
	p1 = p0.copy()
	while p0 == p1:
		choices2 = [0.0, 0.5, 1.0]
		p1 = [
			random.choice(choices2) if random.random() < change_prob else v
			for v in p0
		]
	return [p0, p1]

def run_trial(i):
	"""i 番目の試行分だけ実行し、結果リストを返す"""
	trial_results = []
	for axis_name in axis_list:
		try:
			params = make_params()
			target_path = CONCUR_RESULT(FOLDER_NAME, str(i), axis_name)
			r = experiment(target_path, axis_name, params)
			trial_results.append({
				"date": str(datetime.now()),
				"result": r,
				"axis_param": axis_name
			})
		except Exception as e:
			# 例外情報を文字列化して返す
			print(str(e))
			trial_results.append({
                "error": str(e),
                "params": params,
                "axis_param": axis_name
            })
	return trial_results

def main():
	# プロセス数を TRIAL_COUNT に合わせる
	with ProcessPoolExecutor(max_workers=TRIAL_COUNT) as executor:
		# map の返り値は i=0,1,2 の順で trial_results を返す
		result = list(executor.map(run_trial, range(TRIAL_COUNT)))
	# JSON に書き出し
	makedirs("result" / Path(FOLDER_NAME), exist_ok=True)
	out_path = "result" / Path(FOLDER_NAME) / "result.json"
	out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
	main()