import json
from utility.abc_diff import compare_blocks, parse_abc_file

def diff_param_blocks(
	original_abc: str,
	modified_abc: str,
	block_size: int = 4
) -> set[int] | None:
	ma = parse_abc_file(original_abc)
	mb = parse_abc_file(modified_abc)
	difference= compare_blocks(ma, mb, block_size)
	if difference == None: return None
	return { idx for idx,_,_ in difference }

def judge_correctness(item: dict) -> bool | None:
	if (not "result" in item): return None
	if ("result" in item and len(item["result"]) < 2):
		return None
	orig  = item["result"][0]['score']
	mod  = item["result"][1]['score']
	params_bef = item["result"][0]['param']
	params_aft = item["result"][1]['param']
	diff_blocks = diff_param_blocks(orig, mod)
	
	diff_param = set()
	for i, (p1, p2) in enumerate(zip(params_bef, params_aft)):
		if p1 != p2: diff_param.add(i)
	if not diff_blocks: return None
	if not (diff_param <= diff_blocks):
		print(item["axis_param"])
		print(params_bef, params_aft)
		print(diff_param)
		print(diff_blocks)
	return diff_param <= diff_blocks

if __name__ == "__main__":
	data = json.load(open('./result/jsai2025/result.json', encoding='utf-8'))
	total = 0
	truepoisitive = 0
	for trial in data:
		for conversation in trial:
			result = judge_correctness(conversation)
			if result != None: total += 1
			if result == True: truepoisitive += 1
	print(truepoisitive, total, truepoisitive / total)