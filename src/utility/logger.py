from io import TextIOWrapper


def write_new_message(log:TextIOWrapper, who:str, message:str):
	log.write(f"# {who}  \n{message}\n\n")
