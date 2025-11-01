from enum import Enum
import anthropic
from anthropic.types import MessageParam
import utility.important_path as IPATH

class Model(Enum):
    claude_sonnet_4_2025_0514 = "claude-sonnet-4-20250514"
    claude_3_7_sonnet_20250219       = "claude-3-7-sonnet-20250219"
    
class Claude:
    def __init__(self, model:Model, system_message:str, temparature:float = 1.0):
        """
        クライアントオブジェクトを作る。これを作らないとAPIへの問い合わせができない。
        ターミナルのカレントディレクトリから見て、`./src/credential/OPEN_AI_KEY.txt`に記述されているAPIキーを読み取って実行します。
        """
        API_KEY = ""
        with open(IPATH.CREDENTIAL/"ANTHROPIC_API_KEY.txt") as f:
            API_KEY = f.read()
        self.client = anthropic.Anthropic(api_key=API_KEY)
        self.dialog:list[MessageParam] = [ {"role": "user", "content": system_message} ]
        self.model = model
        self.system_msg = system_message
        self.temparature = temparature
    
    def tell(self, message:str):
        self.dialog.append({
            "role": "user", "content": message
        })
    def remember(self, message:str):
        self.dialog.append({
            "role": "assistant", "content": message
        })
    def forget_without_system_msg(self):
        self.dialog = list(filter((lambda msg: msg["role"] == "system"), self.dialog))
    
    def dump_dialog(self):
        print(f"[dump_dialog]")
        for msg in self.dialog:
            if msg["role"] == "system": continue
            assert "content" in msg
            print(f"{msg["role"]}: {msg["content"]}\n")
        print(f"[end dump_dialog]\n\n")
    def ask(self, remember_self_msg:bool) -> str:
        """
        clientオブジェクトを使って、promptの内容でGPT-4に問い合わせる。
        問い合わせた結果が返り値になります。
        """
        
        response = self.client.messages.create(
            model = self.model.value,
            max_tokens=10000,
            messages=self.dialog,
            temperature=1.0
        )
        result = response.content[0].text # type: ignore
        if result != None:
            if remember_self_msg: self.remember(result)
            return result
        else:
            return  "[There is no content in response.choices[0].message.]"

    if __name__ == "__main__":
        print()