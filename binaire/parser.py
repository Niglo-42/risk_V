from data_asm import Type, Instruction, TypeB, TypeI, \
TypeJ, TypeR, TypeS, TypeU, VarDef
from shunting_yard import shunting_yard
from lexer import Token, TokenType, OP, VARS

class ParsingError(Exception):
    ...

class Parser:
    def __init__(self):
        self.ast = []
        self.reg = ["s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10", "s11"]
        self.index_reg = 0
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
            first_tok = line[0]
            if first_tok.type == TokenType.VAR_DEF:
                self.verif_var_def(line)
            elif first_tok.type == TokenType.CONST_DEF:
                self.verif_const_def(line)
            elif first_tok.type == TokenType.LABEL_DEF:
                self.verif_label_def(line)
            elif first_tok.type == TokenType.OPCODE:
                self.ast.append(self.verif_opcode(line))
                self.pc += 1
            elif first_tok.type == TokenType.IDENT:
                self.var_assign(line)
            else:
                print(f"unexpected token: {first_tok.value}")
                exit(1)
        self.pc = 0

    def verif_label_def(self, line: list[Token]):
        if len(line) != 1:
            raise ParsingError(f"error at line {line[0].line} col {line[0].col}")
        else:
            self.labels[line[0].value] = self.pc

    def verif_const_def(self, line: list[Token]):
        if len(line) < 3:
            raise ParsingError(f"error at line {line[0].line} col {line[0].col}")
        elif line[1].type != TokenType.IDENT:
            raise ParsingError(f"error at line {line[0].line} col {line[0].col}")
        else:
            expr = []
            for t in line[2:]:
                if t.type != TokenType.NUMBER and t.value not in OP:
                    raise ParsingError(f"error at line {line[0].line} col {line[0].col}\
val = '{t.value}' not accepted")
                else:
                    expr.append(t.value)
            self.const[line[1].value] = shunting_yard(expr, {})

    def var_assign(self, line):
        is_type_r = 0
        if len(line) < 3:
            raise ParsingError(f"error at line {line[0].line} col {line[0].col}")
        else:
            if line[1].type != TokenType.ASSIGN:
                raise ParsingError(f"error at line {line[0].line} col {line[0].col}")
            elif line[2].type != TokenType.IDENT:
                raise ParsingError(f"error at line {line[0].line} col {line[0].col}"
                                   f"at least one var is required")
            elif self.vars.get(line[0].value) == None:
                raise ParsingError(f"error at line {line[0].line} col {line[0].col}"
                                   f"{line[0].value} has not been defined")
            else:
                expr = []
                first_reg = line[2].value
                if len(line) == 3:
                    var = TypeI(Token(
                    TokenType.OPCODE, "addi", line[1].line, line[1].col),
                    self.pc,
                    Token(TokenType.REG, self.vars[line[0].value].reg, 0, 0),
                    Token(TokenType.REG, self.vars[first_reg].reg, 0, 0), 0)
                    self.pc += 1
                    self.ast.append(var)
                    return # addi rd, 
                for t in line[3:]:
                    if t.type != TokenType.NUMBER\
                        and t.value not in OP and self.vars.get(t.value) == None:
                        raise ParsingError(
                            f"error at line {line[0].line} col {line[0].col}"
                            f"val = '{t.value}' not accepted")
                    else:
                        expr.append(t.value)
                if all(x.value in OP or x.type == TokenType.IDENT for x in line[3:]):
                    if len(line) != 5:
                        raise ParsingError(f"error at line {line[0].line} col {line[0].col}")
                    is_type_r = 1
                    operator = line[3].value
                    second_reg = line[4].value
                operator = line[3].value
                if is_type_r:
                    var = TypeR(Token(
                    TokenType.OPCODE, Instruction.op_reg[operator], line[1].line, line[1].col),
                    self.pc,
                    Token(TokenType.REG, self.vars[line[0].value].reg, 0, 0),
                    Token(TokenType.REG, self.vars[first_reg].reg, 0, 0),
                    Token(TokenType.REG, self.vars[second_reg].reg, 0, 0))
                else:
                    var = TypeI(Token(
                    TokenType.OPCODE, Instruction.op_imm[operator], line[1].line, line[1].col),
                    self.pc,
                    Token(TokenType.REG, self.vars[first_reg].reg, 0, 0),
                    Token(TokenType.REG, "x0", 0, 0),
                    shunting_yard(expr, 0))
                self.pc += 1
                self.ast.append(var)
            

    def verif_var_def(self, line: list[Token]):
        if len(line) < 2:
            raise ParsingError(f"error at line {line[0].line} col {line[0].col}")
        if line[1].type != TokenType.IDENT:
            raise ParsingError(f"error at line {line[0].line} col {line[0].col}")
        elif line[2].type != TokenType.ASSIGN:
            if len(line) > 2:
                raise ParsingError(f"error at line {line[0].line} col {line[0].col}")
            else:
                if self.vars.get(line[1].value) ==  None:
                    self.vars[line[1].value] = VarDef(VARS[line[0]],
                                                       self.reg[self.index_reg], 0)
                    self.index_reg += 1
                else:
                    raise ParsingError(f"Duplicate var def for {line[1].value}"
                                       f" line: {line[1].line}, col: {line[0].col}")
        else:
            expr = []
            for t in line[3:]:
                if t.type != TokenType.NUMBER and t.value not in OP:
                    raise ParsingError(f"error at line {line[0].line} col {line[0].col}\
val = '{t.value}' not accepted")
                else:
                    expr.append(t.value)
            self.vars[line[1].value] = VarDef(VARS[line[0].value], self.reg[self.index_reg], int(line[3].value))
            var = TypeI(Token(
                TokenType.OPCODE, "addi", line[1].line, line[1].col),
                self.pc,
                Token(TokenType.REG, self.reg[self.index_reg], 0, 0),
                Token(TokenType.REG, "x0", 0, 0),
                shunting_yard(expr, self.vars))
            self.index_reg += 1
            self.pc += 1
            self.ast.append(var)

    def verif_opcode(self, line):
        first_tok = line[0]
        type = Instruction.get_opcode_type(first_tok.value)
        if type == Type.R:
            return self.verif_type_r(line)
        elif type == Type.U:
            return self.verif_type_u(line)
        elif type == Type.I:
            return self.verif_type_i(line)
        elif type == Type.J:
            return self.verif_type_j(line)
        elif type == Type.B:
            return self.verif_type_b(line)
        elif type == Type.S:
            return self.verif_type_s(line)

    def verif_type_r(self, line):
        if len(line) != 6:
            raise ParsingError(f"error at line: {line[0].line} col: {line[0].col}"
                               "not the right number of elements, type R")
        else:
            op, rd, comma, rs1, comma2, rs2 = line
            if rd.type != TokenType.REG or rs1.type != TokenType.REG or rs2.type != TokenType.REG:
                raise ParsingError(f"error at line: {line[0].line} col: {line[0].col}")
            elif comma.type != TokenType.COMMA or comma2.type != TokenType.COMMA:
                raise ParsingError(f"error at line: {line[0].line} col: {line[0].col}")
            else:
                instance = TypeR(op, self.pc, rd, rs1, rs2)
                return instance
    
    def verif_type_i(self, line):
        if len(line) != 6:
            raise ParsingError(f"error at line: {line[0].line} col: {line[0].col}"
                               "not the right number of elements, type I")
        else:
            op, rd, comma, rs1, comma2, imm = line
            if rd.type != TokenType.REG or rs1.type != TokenType.REG:
                raise ParsingError(f"error at line: {line[0].line} col: {line[0].col}")
            elif imm.type != TokenType.NUMBER:
                raise ParsingError(f"error at line: {line[0].line} col: {line[0].col}")
            elif comma.type != TokenType.COMMA or comma2.type != TokenType.COMMA:
                raise ParsingError(f"error at line: {line[0].line} col: {line[0].col}")
            else:
                instance = TypeI(op, self.pc, rd, rs1, int(imm.value))
                return instance
            
    def verif_type_u(self, line):
        if len(line) != 4:
            raise ParsingError(f"error at line: {line[0].line} col: {line[0].col}"
                               "not the right number of elements, type I")
        else:
            op, rd, comma, imm = line
            if rd.type != TokenType.REG:
                raise ParsingError(f"error at line: {line[0].line} col: {line[0].col}")
            elif imm.type != TokenType.NUMBER:
                raise ParsingError(f"error at line: {line[0].line} col: {line[0].col}")
            elif comma.type != TokenType.COMMA:
                raise ParsingError(f"error at line: {line[0].line} col: {line[0].col}")
            else:
                instance = TypeI(op, self.pc, rd, int(imm.value))
                return instance
    
    def verif_type_b(self, line):
        if len(line) != 5:
            raise ParsingError(f"error at line: {line[0].line} col: {line[0].col}"
                               "not the right number of elements, type B")
        else:
            op, rs1, comma, rs2, imm_label = line
            if rs1.type != TokenType.REG or rs2.type != TokenType.REG:
                raise ParsingError(f"error at line: {line[0].line} col: {line[0].col}")
            elif not imm_label.value in self.labels:
                raise ParsingError(f"error at line: {line[0].line} col: {line[0].col}"
                                   f"{imm_label} not declared before")
            elif comma.type != TokenType.COMMA:
                raise ParsingError(f"error at line: {line[0].line} col: {line[0].col}")
            else:
                return TypeB(op, self.pc, rs1, rs2, self.labels[imm_label.value])
            
    def verif_type_j(self, line):
        if len(line) != 4:
            raise ParsingError(f"error at line: {line[0].line} col: {line[0].col}"
                               "not the right number of elements, type J")
        else:
            op, rd, comma, imm_label = line
            if rd.type != TokenType.REG:
                raise ParsingError(f"error at line: {line[0].line} col: {line[0].col}")
            elif not imm_label.value in self.labels:
                raise ParsingError(f"error at line: {line[0].line} col: {line[0].col}"
                                   f"{imm_label} not declared before")
            elif comma.type != TokenType.COMMA:
                raise ParsingError(f"error at line: {line[0].line} col: {line[0].col}")
            else:
                return TypeJ(op, self.pc, rd, self.labels[imm_label.value])
            
    def verif_type_s(self, line):
        if len(line) != 4:
            raise ParsingError(f"error at line: {line[0].line} col: {line[0].col}"
                               "not the right number of elements, type S")
        else:
            op, rs1, comma, rs2 = line
            if rs1.type != TokenType.REG or rs2.type != TokenType.REG:
                raise ParsingError(f"error at line: {line[0].line} col: {line[0].col}")
            elif comma.type != TokenType.COMMA:
                raise ParsingError(f"error at line: {line[0].line} col: {line[0].col}")
            else:
                return TypeS(op, self.pc, rs1, rs2)

    def print_ast(self):
        for k, v in self.vars.items():
            print(k, ": ", v.reg, v.type)
        print(self.const, self.labels)
        for instr in self.ast:
            if isinstance(instr, TypeR):
                print(f"Instru line: {instr.pc}", end=" ")
                print(instr.opcode.value, instr.rd.value,
                      instr.rs1.value, instr.rs2.value)
                print()
            elif isinstance(instr, TypeI):
                print(f"Instru line: {instr.pc}", end=" ")
                print(instr.opcode.value, instr.rd.value,
                      instr.rs1.value, instr.imm)
                print()
            elif isinstance(instr, TypeJ):
                print(f"Instru line: {instr.pc}", end=" ")
                print(instr.opcode.value, instr.rd.value,
                      instr.label)
                print()
            elif isinstance(instr, TypeU):
                print(f"Instru line: {instr.pc}", end=" ")
                print(instr.opcode.value, instr.rd.value,
                      instr.imm)
                print()
            elif isinstance(instr, TypeB):
                print(f"Instru line: {instr.pc}", end=" ")
                print(instr.opcode.value,
                      instr.rs1.value, instr.rs2.value, instr.label)
                print()

def print_tok(line):
    for tok in line:
        print(f"line: {tok.line}, col: {tok.col}"
            f"\tvalue: '{tok.value}' of type: {tok.type}")
    print()