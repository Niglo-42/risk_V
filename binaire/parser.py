from data_asm import Reg, Type, Instruction, TypeB, TypeI, TypeJ, TypeR, TypeS, TypeU
from shunting_yard import shunting_yard
from lexer import Lexer, Token, TokenType
N = 8

class ParsingError(Exception):
    ...

class Parser:
    def __init__(self):
        self.ast = []
        self.labels = {}
        self.vars = {}
        self.const = {}
        self.pc = 0

    def get_line(self, tokens):
        lst = []
        if tokens:
            cur_line = tokens[0].line
        while (tokens):
            lst.append(tokens.pop(0))
            if tokens and cur_line != tokens[0].line:
                break
        return lst

    def parser(self, tokens: list):
        while (tokens):
            line = self.get_line(tokens)
            # print_tok(line)
            first_tok = line[0]
            if first_tok.type == TokenType.VAR_DEF:
                try:
                    self.ast.append(self.verif_var_def(line))
                except Exception as e:
                    print(e)
                    exit(1)
            elif first_tok.type == TokenType.CONST_DEF:
                try:
                    self.ast.append(self.verif_const_def(line))
                except Exception as e:
                    print(e)
                    exit(1)
            elif first_tok.type == TokenType.LABEL_DEF:
                try:
                    self.ast.append(self.verif_label_def(line))
                except Exception as e:
                    print(e)
                    exit(1)
            elif first_tok.type == TokenType.OPCODE:
                try:
                    self.ast.append(self.verif_opcode(line))
                except Exception as e:
                    print(e)
                    exit(1)
            else:
                print(f"unexpected token: {first_tok}")
                exit(1)

    def verif_label_def(self, line: list[Token]):
        if len(line) != 2:
            raise ParsingError(f"error at line {line[0].line} col {line[0].col}")
        else:
            self.labels[line[0].value] = 0

    def verif_const_def(self, line: list[Token]):
        if len(line) < 3:
            raise ParsingError(f"error at line {line[0].line} col {line[0].col}")
        elif line[1].type != TokenType.IDENT:
            raise ParsingError(f"error at line {line[0].line} col {line[0].col}")
        else:
            expr = []
            for type, value, l, col in line[2:]:
                try:
                    val = int(value)
                except ValueError as e:
                    print((f"error {e} at line: {l} col: {col} for: {value}"))
                    exit(1)
                expr.append(val)
            self.const[line[1].value] = shunting_yard(expr, {})

    def verif_var_def(self, line: list[Token]):
        if len(line) < 4:
            raise ParsingError(f"error at line {line[0].line} col {line[0].col}")
        elif line[1].type != TokenType.IDENT:
            raise ParsingError(f"error at line {line[0].line} col {line[0].col}")
        elif line[2].type != TokenType.ASSIGN:
            raise ParsingError(f"error at line {line[0].line} col {line[0].col}")
        else:
            expr = []
            for type, value, l, col in line[3:]:
                try:
                    val = int(value)
                except ValueError as e:
                    print((f"error {e} at line: {l} col: {col} for: {value}"))
                    exit(1)
                expr.append(val)
            self.vars[line[1].value] = shunting_yard(expr, {})

    def verif_opcode(self, line):
        first_tok = line[0]
        type = Instruction.get_opcode_type(first_tok)
        if type == Type.R:
            return self.verif_type_r(line)
        elif type == Type.U:
            self.verif_type_u(line)
        elif type == Type.I:
            self.verif_type_i(line)
        elif type == Type.J:
            self.verif_type_j(line)
        elif type == Type.B:
            self.verif_type_b(line)
        elif type == Type.S:
            self.verif_type_s(line)

    def verif_type_r(self, line):
        if len(line) != 4:
            raise ParsingError(f"error at line: {line[0].line} col: {line[0].col}"
                               "not the right number of elements")
        else:
            if all(token.type == TokenType.REG for token in line[1:]):
                return TypeR(line[0], Type.R, line[1], line[2], line[3])
    
    def verif_type_i(self, line):
        if len(line) != 4:
            raise ParsingError(f"error at line: {line[0].line} col: {line[0].col}"
                               "not the right number of elements")
        else:
            op, rd, rs1, imm = line
            if rd.type != TokenType.REG or rs1.type != TokenType.REG:
                raise ParsingError(f"error at line: {line[0].line} col: {line[0].col}")
            elif imm.type != TokenType.NUMBER:
                raise ParsingError(f"error at line: {line[0].line} col: {line[0].col}")
            else:
                return TypeI(op, Type.I, rd, rs1, imm)
    
    def verif_type_b(self, line):
        if len(line) != 4:
            raise ParsingError(f"error at line: {line[0].line} col: {line[0].col}"
                               "not the right number of elements")
        else:
            op, rs1, rs2, imm_label = line
            if rs1.type != TokenType.REG or rs2.type != TokenType.REG:
                raise ParsingError(f"error at line: {line[0].line} col: {line[0].col}")
            elif not imm_label.type in self.labels:
                raise ParsingError(f"error at line: {line[0].line} col: {line[0].col}"
                                   f"{imm_label} not declared before")
            else:
                return TypeB(op, Type.B, rs1, rs2, imm_label)
            
    def verif_type_j(self, line):
        if len(line) != 3:
            raise ParsingError(f"error at line: {line[0].line} col: {line[0].col}"
                               "not the right number of elements")
        else:
            op, rd, imm_label = line
            if rd.type != TokenType.REG:
                raise ParsingError(f"error at line: {line[0].line} col: {line[0].col}")
            elif not imm_label.type in self.labels:
                raise ParsingError(f"error at line: {line[0].line} col: {line[0].col}"
                                   f"{imm_label} not declared before")
            else:
                return TypeJ(op, Type.J, rd, imm_label)
            
    def verif_type_s(self, line):
        if len(line) != 3:
            raise ParsingError(f"error at line: {line[0].line} col: {line[0].col}"
                               "not the right number of elements")
        else:
            op, rs1, rs2 = line
            if rs1.type != TokenType.REG or rs2.type != TokenType.REG:
                raise ParsingError(f"error at line: {line[0].line} col: {line[0].col}")
            else:
                return TypeS(op, Type.S, rs1, rs2)

        

    def verif_type_u(self, line):
        pass

    def verif_type_b(self, line):
        pass

    def verif_type_s(self, line):
        pass

    def verif_type_j(self, line):
        pass

    def verif_type_i(self, line):
        pass

def print_tok(line):
    for tok in line:
        print(f"line: {tok.line}, col: {tok.col}"
            f"\tvalue: '{tok.value}' of type: {tok.type}")
    print()