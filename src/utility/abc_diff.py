#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
import sys
from typing import List, Dict, Tuple

def parse_abc_file(abc_score: str) -> List[Dict]:
	"""
	与えられた ABC ファイルを読み込み、
	小節ごとの情報を辞書のリストで返す。
	"""
	lines = abc_score.split("\n")

	key = None
	bpm = None
	in_body = False

	# 現在の楽器設定
	current_program = None
	current_chordprog = None
	current_bassprog = None

	measures: List[Dict] = []

	# ヘッダー部でキーとテンポを取得し、V: 行で本体へ

	# 本体部を走査
	for line in lines:
		if line.startswith('K:'):
			key = line[2:].strip()
		elif line.startswith('Q:'):
			m = re.search(r'1/4\s*=\s*(\d+)', line)
			if m:
				bpm = int(m.group(1))
		if len(line) >= 2 and line[1] == ":":
			continue
		line = line.strip()
		# MIDI ディレクティブの更新
		if line.startswith('%%MIDI'):
			if 'program' in line:
				m = re.search(r'program\s+(\d+)', line)
				if m:
					current_program = int(m.group(1))
			elif 'chordprog' in line:
				m = re.search(r'chordprog\s+(\d+)', line)
				if m:
					current_chordprog = int(m.group(1))
			elif 'bassprog' in line:
				m = re.search(r'bassprog\s+(\d+)', line)
				if m:
					current_bassprog = int(m.group(1))
			continue

		# 小節区切り '|' を含む行を分割して各小節を処理
		if '|' in line:
			parts = line.split('|')
			for seg in parts:
				seg = seg.strip()
				# 中身なし or ディレクティブ行はスキップ
				if not seg or seg.startswith('%') or seg.startswith('V:'):
					continue

				# 1) コードと長さ
				chords: List[Tuple[str,int]] = []
				# chord タグで分割： tokens = [前, chord1, content1, chord2, content2, ...]
				tokens = re.split(r'"([^"]+)"', seg)	
				for j in range(1, len(tokens), 2):
					chord_name = tokens[j]
					content = tokens[j+1]
					# content 中の音符の duration を全て拾って合計
					durs = [int(d) for d in re.findall(r'[A-Ga-g][#^]*([0-9]+)', content)]
					total = sum(durs)
					chords.append((chord_name, total))

				# 2) メロディの音系列
				seg_without_chord = re.sub("\"[^\"]*\"", "", seg)
				melody = [(note, dur)
						  for note, dur in re.findall(r'([\^_]*[A-Ga-g][\'\,]*)([0-9]*\/?[0-9]*)', seg_without_chord)
				]

				measures.append({
					'key': key,
					'bpm': bpm,
					'program': current_program,
					'chordprog': current_chordprog,
					'bassprog': current_bassprog,
					'chords': chords,
					'melody': melody,
				})

	return measures
from typing import List, Dict, Tuple

def measure_equal(ma: Dict, mb: Dict) -> bool:
	return ma == mb


def compare_blocks(
	measures_a: List[Dict],
	measures_b: List[Dict],
	block_size: int = 4
) -> List[Tuple[int,int,int]] | None:
	"""
	measures_a, measures_b を block_size 小節ずつ区切って比較し、
	差分のあるブロックを (ブロック番号, 開始小節, 終了小節) のリストで返す。

	例: [(1,1,4), (3,9,12)] など
	"""
	n = len(measures_a)
	if len(measures_b) != n:	return None
	if n % block_size != 0:		return None

	diffs: List[Tuple[int,int,int]] = []
	for i in range(n // block_size):
		start = i * block_size
		end = start + block_size
		block_a = measures_a[start:end]
		block_b = measures_b[start:end]
		# いずれかの小節で等しくなければ差分あり
		if any(not measure_equal(a, b) for a, b in zip(block_a, block_b)):
			diffs.append((i, start+1, end))
	return diffs



def main():
	if len(sys.argv) != 2:
		print("Usage: python parse_abc.py <abc_filename>")
		sys.exit(1)

	filename = sys.argv[1]
	with open(filename) as f: txt = f.read()
	measures = parse_abc_file(txt)
	# 結果の表示
	for idx, m in enumerate(measures, start=1):
		print(f"--- Measure {idx} ---")
		print(f"Key: {m['key']}, BPM: {m['bpm']}")
		print(f"Program: {m['program']}, Chordprog: {m['chordprog']}, Bassprog: {m['bassprog']}")
		print("Chords and durations:")
		for chord, dur in m['chords']:
			print(f"  {chord}: {dur}")
		print("Melody sequence:")
		for note, dur in m['melody']:
			print(f"  {note}{dur}")
		print()

if __name__ == '__main__':
	main()
