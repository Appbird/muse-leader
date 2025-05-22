def insert_midi_chords(T):
    # 読み込むコード情報
    with open("src/midi_comments.txt", "r", encoding="utf-8") as f:
        S = f.read().strip()
    
    # Tを行ごとに分割
    lines = T.split("\n")
    
    # 新しいテキストを格納するリスト
    new_lines = []
    
    found = False
    for line in lines:
        new_lines.append(line)
        if line.strip().startswith("K:") and not found:
            new_lines.append(S)  # 次の行にSを挿入
            found = True  # 最初に見つけた場所のみ適用
    
    # 新しいテキストを結合して返す
    return "\n".join(new_lines)