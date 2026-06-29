import sys


def get_reg(pos: int, token: str):
    """recup le nombre apres le r de reg (sans le ",")puis le decal de la bonne
    valeur en fonction de sa position (dest, src1, src2)"""
    return int(token[1:]) << [51, 46, 41][pos]


def instruction_table_init(tab: dict):
    tab["add"] = 1 << 56
    tab["sub"] = 2 << 56
    tab["mul"] = 3 << 56
    tab["div"] = 4 << 56
    tab["mod"] = 5 << 56
    tab["shl"] = 6 << 56
    tab["shr"] = 7 << 56
    tab["mov"] = 8 << 56
    tab["imov"] = 9 << 56
    tab["rol"] = 10 << 56
    tab["ror"] = 11 << 56
    tab["cmp"] = 12 << 56
    tab["jmp"] = 13 << 56
    tab["je"] = 14 << 56
    tab["jlt"] = 15 << 56
    tab["jgt"] = 16 << 56
    tab["jle"] = 17 << 56
    tab["jge"] = 18 << 56


def shunting_yard(toks: list[str], vars: dict) -> int:
    input = []
    value = {
        "+": 2,
        "-": 1,
        "*": 3,
        "/": 3,
        "(": 0,
        ")": 4
    }
    ops = {
        "+": lambda a, b: a + b,
        "-": lambda a, b: a - b,
        "*": lambda a, b: a * b,
        "/": lambda a, b: a / b
    }
    holding_stack = []
    solve_stack = []
    output = []
    nbrs = []

    for tok in toks:
        nbrs.append([])
        char = 0
        while char < len(tok):
            if tok in vars:
                try:
                    input.append(int(vars[tok]))
                except ValueError:
                    exit(1)
                break
            elif tok[char] in "*/-+()":
                input.append(tok[char])
                char += 1
            else:
                nbr = 0
                while char < len(tok) and tok[char].isdigit():
                    nbr = nbr * 10 + int(tok[char])
                    char += 1
                input.append(nbr)
    i = 0
    while i < len(input):
        if isinstance(input[i], int):
            output.append(input[i])
        elif input[i] == ")":
            while holding_stack[-1] != "(":
                output.append(holding_stack.pop())
            holding_stack.pop()
        else:
            while (holding_stack and value[holding_stack[-1]] > value[input[i]]
                   and input[i] != "("):
                output.append(holding_stack.pop())
            holding_stack.append(input[i])
        i += 1
    while holding_stack:
        output.append(holding_stack.pop())
    while output:
        while isinstance(output[0], int):
            solve_stack.append(output.pop(0))
        b = solve_stack.pop()
        a = solve_stack.pop()
        solve_stack.append(ops[output.pop(0)](a, b))
    return int(solve_stack[0])


def asm(executable: list):
    if len(sys.argv) != 2:
        exit(1)
    instruction_table = {}
    instruction_table_init(instruction_table)
    tokens = []
    labels = {}
    vars = {}
    const = {}
    i = 0
    with open(sys.argv[1], "r") as file:
        for line in file:
            line = line.strip(" ").rstrip("\n")
            if line.startswith(";"):
                continue
            tokens.append([])
            tokens[-1] = line.split(" ")
            label = tokens[-1][0].find(":")
            if label >= 0:
                labels[tokens[-1][0][0: label]] = i
            elif tokens[-1][0].startswith("var"):
                if len(tokens[-1]) == 3:
                    vars[tokens[-1][1]] = int(tokens[-1][2][1:])
                elif len(tokens[-1]) > 3:
                    raise ValueError("trop d'elements dans la def var")
                else:
                    vars[tokens[-1][1]] = 0
            elif tokens[-1][0].startswith("const"):
                if len(tokens[-1]) > 2:
                    const[tokens[-1][1]] = shunting_yard(tokens[-1][2:], vars)
                else:
                    raise ValueError("A ")
            else:
                i += 1
        nb_line = 0
        line_src = 0
        executable.append(0)
        # print('\n'.join(str(t) for t in tokens))
        for line in tokens:
            line_src += 1
            pos_token = 0
            for token in line:
                if token.startswith(";"):
                    continue
                if token == "var" or token == "const":
                    break
                if token == "halt":
                    executable[nb_line] |= 33 << 24
                    return
                if token in instruction_table:
                    executable[nb_line] |= instruction_table[token]
                elif token.endswith(":"):
                    continue
                elif token in vars:
                    executable[nb_line] |= vars[token]
                elif token in const:
                    executable[nb_line] |= const[token]
                elif token in labels:
                    executable[nb_line] |= labels[token]
                elif token.startswith(("r", "R")):
                    executable[nb_line] |= get_reg(pos_token, token.strip(","))
                elif token.startswith("#"):
                    executable[nb_line] |= int(token[1:])
                else:
                    raise ValueError(
                        f"Value Error at line {line_src}, {token=}")
                pos_token += 1
            if executable[nb_line]:
                executable.append(0)
                nb_line += 1


def main():
    exec = []
    try:
        asm(exec)
    except Exception as e:
        print(e)
        exit(1)
    for line in exec:
        print(hex(line))


if __name__ == "__main__":
    main()