import datetime
from pathlib import Path
CREDENTIAL = Path("./src/credential")
PROMPT = Path("./src/prompt")
def RESULT(parent_folder:str, date:datetime.datetime) -> Path:
    return Path("./result")/parent_folder/date.strftime("%Y%m%d_%H%M%S")


def get_same_name_file(file_path:Path, ext:str) -> Path:
    return file_path.parent/f"{file_path.stem}.{ext}"