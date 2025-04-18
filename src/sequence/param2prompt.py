

def sequence_param_2_table(axis_name:str, params:list[float]) -> str:
    header_row = f"| parameter name |"
    separator_row = f"|---|"
    param_row = f"| {axis_name} |"

    for i in range(len(params)):
        (start, end) = (i * 4 + 1, i * 4 + 4)
        header_row += f" measure {start}-{end} |"
        separator_row += f"---|"
        param_row += f" {params[i]} |"
    total_txt = f"# Current Customizable Semantic Parameters\n{header_row}\n{separator_row}\n{param_row}\n"
    return total_txt

def input_table() -> str | None:
    """
    パラメータ値を標準入力から受け取る。
    標準入力は次のような形式で1行に記述する。
    ```zsh
    [axis name] [value for measure 1-4] [value for measure 5-8] [value for measure 9-12] ...
    ```
    """
    print("> Enter the parameter sequence in a line. To quit, Ctrl+D.")
    line_inputs = input().strip().split(" ")
    axis_name = line_inputs[0]
    param_sequence = map(float, line_inputs[1:])
    
    return sequence_param_2_table(axis_name, list(param_sequence))

def form_table(axis:str, params:list[float]) -> str | None:
    """
    パラメータ値を標準入力から受け取る。
    標準入力は次のような形式で1行に記述する。
    ```zsh
    [axis name] [value for measure 1-4] [value for measure 5-8] [value for measure 9-12] ...
    ```
    """
    axis_name = axis
    param_sequence = params
    return sequence_param_2_table(axis_name, list(param_sequence))