from enum import Enum

class Type(Enum):
    R = 0
    I = 1
    S = 2
    B = 3
    U = 4
    J = 5

class DataType(Enum):
    INT     = 0
    SHORT   = 1
    CHAR    = 2
    UINT    = 3
    USHORT  = 4
    UCHAR   = 5

class T:
    def __init__(self, op, pc):
        self.opcode=op
        self.pc=pc

class VarDef:
    def __init__(self, type, reg):
        self.reg=reg
        self.type=type

class TypeVar(T):
    def __init__(self, op, pc, rd, rs1, imm):
        super().__init__(op, pc)
        self.rd=rd
        self.rs1=rs1
        self.imm=imm

class TypeR(T):
    def __init__(self, op, pc, rd, rs1, rs2):
        super().__init__(op, pc)
        self.rd=rd
        self.rs1=rs1
        self.rs2=rs2

class TypeI(T):
    def __init__(self, op, pc, rd, rs1, imm):
        super().__init__(op, pc)
        self.rd=rd
        self.rs1=rs1
        self.imm=imm

class TypeU(T):
    def __init__(self, op, pc, rd, imm):
        super().__init__(op, pc)
        self.rd=rd
        self.imm=imm

class TypeB(T):
    def __init__(self, op, pc, rs1, rs2, label):
        super().__init__(op, pc)
        self.rs1=rs1
        self.rs2=rs2
        self.label=label

class TypeJ(T):
    def __init__(self, op, pc, rd, label):
        super().__init__(op, pc)
        self.rd=rd
        self.label=label

class TypeS(T):
    def __init__(self, op, pc, rs1, rs2):
        super().__init__(op, pc)
        self.rs1=rs1
        self.rs2=rs2

class Instruction:
    tab = {
    "add":       (0x30, Type.R),
    "sub":       (0x40000030, Type.R),
    "and":       (0x7030, Type.R),
    "or":        (0x6030, Type.R),
    "xor":       (0x4030, Type.R),

    "jal":       (0x6C, Type.J),
    "jalr":      (0x64, Type.I),
    "lui":       (0x34, Type.U),
    "auipc":     (0x14, Type.U),

    "sll":       (0x1030, Type.R),
    "slt":       (0x2030, Type.R),
    "sltu":      (0x3030, Type.R),
    "sra":       (0x40005030, Type.R),
    "srl":       (0x5030, Type.R),

    "beq":       (0x0060, Type.B),
    "bge":       (0x5060, Type.B),
    "bgeu":      (0x7060, Type.B),
    "blt":       (0x4060, Type.B),
    "bltu":      (0x6060, Type.B),
    "bne":       (0x1060, Type.B),

    "lb":        (0x0000, Type.R),
    "lh":        (0x1000, Type.R),
    "lw":        (0x2000, Type.R),
    "lbu":       (0x4000, Type.R),
    "lhu":       (0x5000, Type.R),

    "sb":        (0x0020, Type.S),
    "sh":        (0x1020, Type.S),
    "sw":        (0x2020, Type.S),

    "addi":      (0x10, Type.I),
    "subi":      (0x40000010, Type.I),
    "andi":      (0x7010, Type.I),
    "ori":       (0x6010, Type.I),
    "xori":      (0x4010, Type.I),
    "slli":      (0x1010, Type.I),
    "slti":      (0x2010, Type.I),
    "sltui":     (0x3010, Type.I),
    "srai":      (0x40005010, Type.I),
    "srli":      (0x5010, Type.I),

    "read_file": (0x20000000, Type.R),
    "halt":      (0xFFFFFFF0, Type.R),
    }

    def get_opcode_type(name: str):
        val =  Instruction.tab.get(name)
        if val:
            return val[1]
        return None

class Reg:
    reg = {
        "x0": 0,
        "ra": 1,
        "sp": 2,
        "gp": 3,
        "tp": 4,
        "t0": 5,
        "t1": 6,
        "t2": 7,
        "fp": 8,
        "s1": 9,
        "a0": 10,
        "a1": 11,
        "a2": 12,
        "a3": 13,
        "a4": 14,
        "a5": 15,
        "a6": 16,
        "a7": 17,
        "s2": 18,
        "s3": 19,
        "s4": 20,
        "s5": 21,
        "s6": 22,
        "s7": 23,
        "s8": 24,
        "s9": 25,
        "s10": 26,
        "s11": 27,
        "t3": 28,
        "t4": 29,
        "t5": 30,
        "t6": 31
    }

    def get_reg(pos: int, token: str) ->int:
        return Reg.reg[token] << [7, 15, 20][pos]
