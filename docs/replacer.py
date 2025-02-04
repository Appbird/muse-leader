import re
import sys
from pathlib import Path

def update_audio_paths(html_file):
    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    def replacer(match):
        path = match.group(1)
        parts = Path(path).parts
        
        if len(parts) == 1:  # brightness_1.mp3 のような形式
            base_name = Path(path).stem  # brightness_1
            axis, index = base_name.rsplit("_", 1)  # brightness, 1
            new_path = f"audio/{axis}/composition-{index}.mp3"
        else:  # すでに audio/brightness/composition-0.abc 形式
            axis = parts[1]
            index = re.search(r"composition-(\d+)\.\w+$", path).group(1)
            new_path = f"audio/{axis}/composition-{index}.mp3"
        
        return f'<source src="{new_path}" type="audio/mpeg">'
    
    updated_html = re.sub(r'<source src="([^"]+)" type="audio/mpeg">', replacer, html_content)
    
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(updated_html)
    
    print(f"Updated: {html_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python update_audio_paths.py <html_file>")
        sys.exit(1)
    
    update_audio_paths(sys.argv[1])
