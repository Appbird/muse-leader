def emmbedding_param_into_prompt(base_prompt:str, params:dict[str, str]) -> str:
	for (param_name, value) in params.items():
		base_prompt = base_prompt.replace("${"+ param_name +"}", value)
	return base_prompt

def rotate_sublist_right(score_list: list[str], i: int, j: int) -> None:
    # score_list[i] … score_list[j] を右へ 1 要素だけ回転
    # 例: [A, B, C, D] → [D, A, B, C]
    score_list[i:j+1] = [score_list[j]] + score_list[i:j]

def error_correction(score:str):
	in_chord_name = False
	in_header = False
	in_comment = False
	after_soundname = False
	start_soundname = 0
	score_list = list(score)
	for i in range(len(score_list)):
		# 関係ない箇所を無視
		if score[i] == "|" : continue
		if i+1 < len(score) and score[i+1] == ":": # ヘッダー
			after_soundname = False
			in_header = True
		if score[i] == "%": # コメント
			after_soundname = False
			in_comment = True
		if score[i] == '"': #コード名
			in_chord_name = not in_chord_name
			continue
		if score[i] == "\n": # 改行文字が入れば全て無効
			in_chord_name = False
			in_header = False
			in_comment = False
		if in_chord_name or in_header or in_comment:
			continue

		# メロディ部
		if after_soundname:
			if score[i] == '#' :
				score_list[i] = '^'
				rotate_sublist_right(score_list, start_soundname, i)
			if score[i] == 'b' :
				score_list[i] = '_'
				rotate_sublist_right(score_list, start_soundname, i)
			
		after_soundname = score[i].isalpha() or score[i] in {"'", ','}
		if score[i].isalpha(): start_soundname = i
	return "".join(score_list)
