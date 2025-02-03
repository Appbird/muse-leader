import os
from conversion.abc2audio import write_midi_from_abc_with_abc2midi
from tempfile import NamedTemporaryFile

class ValidationResult:
    def __init__(self, suc:bool, reason:str):
        self.success = suc
        self.reason = reason
    def is_ok(self) -> bool:
        return self.success
    

def Ok():
    return ValidationResult(True, "")

def Err(reason:str):
    return ValidationResult(False, reason)

def validate_abc(abc_score:str) -> ValidationResult:
    with NamedTemporaryFile("+w", delete=False) as abc_file:
        abc_file.write(abc_score)
    with open(abc_file.name, "r") as abc_file:
        with NamedTemporaryFile("+w") as midi_file:
            result = write_midi_from_abc_with_abc2midi(abc_file.name, midi_file.name)
    os.remove(abc_file.name)
    print(result.is_ok())
    if result.is_ok():
        return Ok()
    else:
        return Err(result.reason)