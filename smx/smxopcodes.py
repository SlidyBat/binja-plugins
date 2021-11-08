from enum import IntEnum

IMAGE_SEGMENT = 0x00000000
CODE_SEGMENT  = 0x10000000
DATA_SEGMENT  = 0x20000000

class SmxOpcodeVisitor(object):
    def __init__(self, **kw):
        super(SmxOpcodeVisitor, self).__init__()
    
    def visit(self, op):
        method_name = 'visit_%s' % op.name
        if hasattr(self, method_name):
            return getattr(self, method_name)()
        raise NotImplementedError('unimplemented op %s' % op.name)
        return None

class SmxParam(IntEnum):
    CONSTANT = 0
    STACK = 1
    JUMP = 2
    FUNCTION = 3
    NATIVE = 4
    ADDRESS = 5

class SmxOp(IntEnum):
    NONE = 0
    LOAD_PRI = 1
    LOAD_ALT = 2
    LOAD_S_PRI = 3
    LOAD_S_ALT = 4
    UNGEN_LREF_PRI = 5
    UNGEN_LREF_ALT = 6
    LREF_S_PRI = 7
    LREF_S_ALT = 8
    LOAD_I = 9
    LODB_I = 10
    CONST_PRI = 11
    CONST_ALT = 12
    ADDR_PRI = 13
    ADDR_ALT = 14
    STOR_PRI = 15
    STOR_ALT = 16
    STOR_S_PRI = 17
    STOR_S_ALT = 18
    UNGEN_SREF_PRI = 19
    UNGEN_SREF_ALT = 20
    SREF_S_PRI = 21
    SREF_S_ALT = 22
    STOR_I = 23
    STRB_I = 24
    LIDX = 25
    LIDX_B = 26
    IDXADDR = 27
    IDXADDR_B = 28
    UNGEN_ALIGN_PRI = 29
    UNGEN_ALIGN_ALT = 30
    UNGEN_LCTRL = 31
    UNGEN_SCTRL = 32
    MOVE_PRI = 33
    MOVE_ALT = 34
    XCHG = 35
    PUSH_PRI = 36
    PUSH_ALT = 37
    UNGEN_PUSH_R = 38
    PUSH_C = 39
    PUSH = 40
    PUSH_S = 41
    POP_PRI = 42
    POP_ALT = 43
    STACK = 44
    HEAP = 45
    PROC = 46
    UNGEN_RET = 47
    RETN = 48
    CALL = 49
    UNGEN_CALL_PRI = 50
    JUMP = 51
    UNGEN_JREL = 52
    JZER = 53
    JNZ = 54
    JEQ = 55
    JNEQ = 56
    UNGEN_JLESS = 57
    UNGEN_JLEQ = 58
    UNGEN_JGRTR = 59
    UNGEN_JGEQ = 60
    JSLESS = 61
    JSLEQ = 62
    JSGRTR = 63
    JSGEQ = 64
    SHL = 65
    SHR = 66
    SSHR = 67
    SHL_C_PRI = 68
    SHL_C_ALT = 69
    SHR_C_PRI = 70
    SHR_C_ALT = 71
    SMUL = 72
    SDIV = 73
    SDIV_ALT = 74
    UNGEN_UMUL = 75
    UNGEN_UDIV = 76
    UNGEN_UDIV_ALT = 77
    ADD = 78
    SUB = 79
    SUB_ALT = 80
    AND = 81
    OR = 82
    XOR = 83
    NOT = 84
    NEG = 85
    INVERT = 86
    ADD_C = 87
    SMUL_C = 88
    ZERO_PRI = 89
    ZERO_ALT = 90
    ZERO = 91
    ZERO_S = 92
    UNGEN_SIGN_PRI = 93
    UNGEN_SIGN_ALT = 94
    EQ = 95
    NEQ = 96
    UNGEN_LESS = 97
    UNGEN_LEQ = 98
    UNGEN_GRTR = 99
    UNGEN_GEQ = 100
    SLESS = 101
    SLEQ = 102
    SGRTR = 103
    SGEQ = 104
    EQ_C_PRI = 105
    EQ_C_ALT = 106
    INC_PRI = 107
    INC_ALT = 108
    INC = 109
    INC_S = 110
    INC_I = 111
    DEC_PRI = 112
    DEC_ALT = 113
    DEC = 114
    DEC_S = 115
    DEC_I = 116
    MOVS = 117
    UNGEN_CMPS = 118
    FILL = 119
    HALT = 120
    BOUNDS = 121
    UNGEN_SYSREQ_PRI = 122
    SYSREQ_C = 123
    UNGEN_FILE = 124
    UNGEN_LINE = 125
    UNGEN_SYMBOL = 126
    UNGEN_SRANGE = 127
    UNGEN_JUMP_PRI = 128
    SWITCH = 129
    CASETBL = 130
    SWAP_PRI = 131
    SWAP_ALT = 132
    PUSH_ADR = 133
    NOP = 134
    SYSREQ_N = 135
    UNGEN_SYMTAG = 136
    BREAK = 137
    PUSH2_C = 138
    PUSH2 = 139
    PUSH2_S = 140
    PUSH2_ADR = 141
    PUSH3_C = 142
    PUSH3 = 143
    PUSH3_S = 144
    PUSH3_ADR = 145
    PUSH4_C = 146
    PUSH4 = 147
    PUSH4_S = 148
    PUSH4_ADR = 149
    PUSH5_C = 150
    PUSH5 = 151
    PUSH5_S = 152
    PUSH5_ADR = 153
    LOAD_BOTH = 154
    LOAD_S_BOTH = 155
    CONST = 156
    CONST_S = 157
    UNGEN_SYSREQ_D = 158
    UNGEN_SYSREQ_ND = 159
    TRACKER_PUSH_C = 160
    TRACKER_POP_SETHEAP = 161
    GENARRAY = 162
    GENARRAY_Z = 163
    STRADJUST_PRI = 164
    UNGEN_STKADJUST = 165
    ENDPROC = 166
    UNGEN_LDGFN_PRI = 167
    REBASE = 168
    INITARRAY_PRI = 169
    INITARRAY_ALT = 170
    HEAP_SAVE = 171
    HEAP_RESTORE = 172
    UNGEN_FIRST_FAKE = 173
    FABS = 174
    FLOAT = 175
    FLOATADD = 176
    FLOATSUB = 177
    FLOATMUL = 178
    FLOATDIV = 179
    RND_TO_NEAREST = 180
    RND_TO_FLOOR = 181
    RND_TO_CEIL = 182
    RND_TO_ZERO = 183
    FLOATCMP = 184
    FLOAT_GT = 185
    FLOAT_GE = 186
    FLOAT_LT = 187
    FLOAT_LE = 188
    FLOAT_NE = 189
    FLOAT_EQ = 190
    FLOAT_NOT = 191

SMX_NUM_OPS = 192

# Pseudo-opcode
SmxOp.CASE = 255

sp_opcode_info = {
    SmxOp.NONE: ["none", 1],
    SmxOp.LOAD_PRI: ["load.pri", 2],
    SmxOp.LOAD_ALT: ["load.alt", 2],
    SmxOp.LOAD_S_PRI: ["load.s.pri", 2],
    SmxOp.LOAD_S_ALT: ["load.s.alt", 2],
    SmxOp.UNGEN_LREF_PRI: ["lref.pri", 0],
    SmxOp.UNGEN_LREF_ALT: ["lref.alt", 0],
    SmxOp.LREF_S_PRI: ["lref.s.pri", 2],
    SmxOp.LREF_S_ALT: ["lref.s.alt", 2],
    SmxOp.LOAD_I: ["load.i", 1],
    SmxOp.LODB_I: ["lodb.i", 2],
    SmxOp.CONST_PRI: ["const.pri", 2],
    SmxOp.CONST_ALT: ["const.alt", 2],
    SmxOp.ADDR_PRI: ["addr.pri", 2],
    SmxOp.ADDR_ALT: ["addr.alt", 2],
    SmxOp.STOR_PRI: ["stor.pri", 2],
    SmxOp.STOR_ALT: ["stor.alt", 2],
    SmxOp.STOR_S_PRI: ["stor.s.pri", 2],
    SmxOp.STOR_S_ALT: ["stor.s.alt", 2],
    SmxOp.UNGEN_SREF_PRI: ["sref.pri", 0],
    SmxOp.UNGEN_SREF_ALT: ["sref.alt", 0],
    SmxOp.SREF_S_PRI: ["sref.s.pri", 2],
    SmxOp.SREF_S_ALT: ["sref.s.alt", 2],
    SmxOp.STOR_I: ["stor.i", 1],
    SmxOp.STRB_I: ["strb.i", 2],
    SmxOp.LIDX: ["lidx", 1],
    SmxOp.LIDX_B: ["lidx.b", 2],
    SmxOp.IDXADDR: ["idxaddr", 1],
    SmxOp.IDXADDR_B: ["idxaddr.b", 2],
    SmxOp.UNGEN_ALIGN_PRI: ["align.pri", 0],
    SmxOp.UNGEN_ALIGN_ALT: ["align.alt", 0],
    SmxOp.UNGEN_LCTRL: ["lctrl", 0],
    SmxOp.UNGEN_SCTRL: ["sctrl", 0],
    SmxOp.MOVE_PRI: ["move.pri", 1],
    SmxOp.MOVE_ALT: ["move.alt", 1],
    SmxOp.XCHG: ["xchg", 1],
    SmxOp.PUSH_PRI: ["push.pri", 1],
    SmxOp.PUSH_ALT: ["push.alt", 1],
    SmxOp.UNGEN_PUSH_R: ["push.r", 0],
    SmxOp.PUSH_C: ["push.c", 2],
    SmxOp.PUSH: ["push", 2],
    SmxOp.PUSH_S: ["push.s", 2],
    SmxOp.POP_PRI: ["pop.pri", 1],
    SmxOp.POP_ALT: ["pop.alt", 1],
    SmxOp.STACK: ["stack", 2],
    SmxOp.HEAP: ["heap", 2],
    SmxOp.PROC: ["proc", 1],
    SmxOp.UNGEN_RET: ["ret", 0],
    SmxOp.RETN: ["retn", 1],
    SmxOp.CALL: ["call", 2],
    SmxOp.UNGEN_CALL_PRI: ["call.pri", 0],
    SmxOp.JUMP: ["jump", 2],
    SmxOp.UNGEN_JREL: ["jrel", 0],
    SmxOp.JZER: ["jzer", 2],
    SmxOp.JNZ: ["jnz", 2],
    SmxOp.JEQ: ["jeq", 2],
    SmxOp.JNEQ: ["jneq", 2],
    SmxOp.UNGEN_JLESS: ["jless", 0],
    SmxOp.UNGEN_JLEQ: ["jleq", 0],
    SmxOp.UNGEN_JGRTR: ["jgrtr", 0],
    SmxOp.UNGEN_JGEQ: ["jgeq", 0],
    SmxOp.JSLESS: ["jsless", 2],
    SmxOp.JSLEQ: ["jsleq", 2],
    SmxOp.JSGRTR: ["jsgrtr", 2],
    SmxOp.JSGEQ: ["jsgeq", 2],
    SmxOp.SHL: ["shl", 1],
    SmxOp.SHR: ["shr", 1],
    SmxOp.SSHR: ["sshr", 1],
    SmxOp.SHL_C_PRI: ["shl.c.pri", 2],
    SmxOp.SHL_C_ALT: ["shl.c.alt", 2],
    SmxOp.SHR_C_PRI: ["shr.c.pri", 2],
    SmxOp.SHR_C_ALT: ["shr.c.alt", 2],
    SmxOp.SMUL: ["smul", 1],
    SmxOp.SDIV: ["sdiv", 1],
    SmxOp.SDIV_ALT: ["sdiv.alt", 1],
    SmxOp.UNGEN_UMUL: ["umul", 0],
    SmxOp.UNGEN_UDIV: ["udiv", 0],
    SmxOp.UNGEN_UDIV_ALT: ["udiv.alt", 0],
    SmxOp.ADD: ["add", 1],
    SmxOp.SUB: ["sub", 1],
    SmxOp.SUB_ALT: ["sub.alt", 1],
    SmxOp.AND: ["and", 1],
    SmxOp.OR: ["or", 1],
    SmxOp.XOR: ["xor", 1],
    SmxOp.NOT: ["not", 1],
    SmxOp.NEG: ["neg", 1],
    SmxOp.INVERT: ["invert", 1],
    SmxOp.ADD_C: ["add.c", 2],
    SmxOp.SMUL_C: ["smul.c", 2],
    SmxOp.ZERO_PRI: ["zero.pri", 1],
    SmxOp.ZERO_ALT: ["zero.alt", 1],
    SmxOp.ZERO: ["zero", 2],
    SmxOp.ZERO_S: ["zero.s", 2],
    SmxOp.UNGEN_SIGN_PRI: ["sign.pri", 0],
    SmxOp.UNGEN_SIGN_ALT: ["sign.alt", 0],
    SmxOp.EQ: ["eq", 1],
    SmxOp.NEQ: ["neq", 1],
    SmxOp.UNGEN_LESS: ["less", 0],
    SmxOp.UNGEN_LEQ: ["leq", 0],
    SmxOp.UNGEN_GRTR: ["grtr", 0],
    SmxOp.UNGEN_GEQ: ["geq", 0],
    SmxOp.SLESS: ["sless", 1],
    SmxOp.SLEQ: ["sleq", 1],
    SmxOp.SGRTR: ["sgrtr", 1],
    SmxOp.SGEQ: ["sgeq", 1],
    SmxOp.EQ_C_PRI: ["eq.c.pri", 2],
    SmxOp.EQ_C_ALT: ["eq.c.alt", 2],
    SmxOp.INC_PRI: ["inc.pri", 1],
    SmxOp.INC_ALT: ["inc.alt", 1],
    SmxOp.INC: ["inc", 2],
    SmxOp.INC_S: ["inc.s", 2],
    SmxOp.INC_I: ["inc.i", 1],
    SmxOp.DEC_PRI: ["dec.pri", 1],
    SmxOp.DEC_ALT: ["dec.alt", 1],
    SmxOp.DEC: ["dec", 2],
    SmxOp.DEC_S: ["dec.s", 2],
    SmxOp.DEC_I: ["dec.i", 1],
    SmxOp.MOVS: ["movs", 2],
    SmxOp.UNGEN_CMPS: ["cmps", 0],
    SmxOp.FILL: ["fill", 2],
    SmxOp.HALT: ["halt", 2],
    SmxOp.BOUNDS: ["bounds", 2],
    SmxOp.UNGEN_SYSREQ_PRI: ["sysreq.pri", 0],
    SmxOp.SYSREQ_C: ["sysreq.c", 2],
    SmxOp.UNGEN_FILE: ["file", 0],
    SmxOp.UNGEN_LINE: ["line", 0],
    SmxOp.UNGEN_SYMBOL: ["symbol", 0],
    SmxOp.UNGEN_SRANGE: ["srange", 0],
    SmxOp.UNGEN_JUMP_PRI: ["jump.pri", 0],
    SmxOp.SWITCH: ["switch", 2],
    SmxOp.CASETBL: ["casetbl", 3], # Actually variable length, but we handle that as a special case
    SmxOp.SWAP_PRI: ["swap.pri", 1],
    SmxOp.SWAP_ALT: ["swap.alt", 1],
    SmxOp.PUSH_ADR: ["push.adr", 2],
    SmxOp.NOP: ["nop", 1],
    SmxOp.SYSREQ_N: ["sysreq.n", 3],
    SmxOp.UNGEN_SYMTAG: ["symtag", 0],
    SmxOp.BREAK: ["break", 1],
    SmxOp.PUSH2_C: ["push2.c", 3],
    SmxOp.PUSH2: ["push2", 3],
    SmxOp.PUSH2_S: ["push2.s", 3],
    SmxOp.PUSH2_ADR: ["push2.adr", 3],
    SmxOp.PUSH3_C: ["push3.c", 4],
    SmxOp.PUSH3: ["push3", 4],
    SmxOp.PUSH3_S: ["push3.s", 4],
    SmxOp.PUSH3_ADR: ["push3.adr", 4],
    SmxOp.PUSH4_C: ["push4.c", 5],
    SmxOp.PUSH4: ["push4", 5],
    SmxOp.PUSH4_S: ["push4.s", 5],
    SmxOp.PUSH4_ADR: ["push4.adr", 5],
    SmxOp.PUSH5_C: ["push5.c", 6],
    SmxOp.PUSH5: ["push5", 6],
    SmxOp.PUSH5_S: ["push5.s", 6],
    SmxOp.PUSH5_ADR: ["push5.adr", 6],
    SmxOp.LOAD_BOTH: ["load.both", 3],
    SmxOp.LOAD_S_BOTH: ["load.s.both", 3],
    SmxOp.CONST: ["const", 3],
    SmxOp.CONST_S: ["const.s", 3],
    SmxOp.UNGEN_SYSREQ_D: ["sysreq.d", 0],
    SmxOp.UNGEN_SYSREQ_ND: ["sysreq.nd", 0],
    SmxOp.TRACKER_PUSH_C: ["trk.push.c", 2],
    SmxOp.TRACKER_POP_SETHEAP: ["trk.pop", 1],
    SmxOp.GENARRAY: ["genarray", 2],
    SmxOp.GENARRAY_Z: ["genarray.z", 2],
    SmxOp.STRADJUST_PRI: ["stradjust.pri", 1],
    SmxOp.UNGEN_STKADJUST: ["stackadjust", 0],
    SmxOp.ENDPROC: ["endproc", 1],
    SmxOp.UNGEN_LDGFN_PRI: ["ldgfn.pri", 0],
    SmxOp.REBASE: ["rebase", 4],
    SmxOp.INITARRAY_PRI: ["initarray.pri", 6],
    SmxOp.INITARRAY_ALT: ["initarray.alt", 6],
    SmxOp.HEAP_SAVE: ["heap.save", 1],
    SmxOp.HEAP_RESTORE: ["heap.restore", 1],
    SmxOp.UNGEN_FIRST_FAKE: ["firstfake", 0],
    SmxOp.FABS: ["fabs", 1],
    SmxOp.FLOAT: ["float", 1],
    SmxOp.FLOATADD: ["float.add", 1],
    SmxOp.FLOATSUB: ["float.sub", 1],
    SmxOp.FLOATMUL: ["float.mul", 1],
    SmxOp.FLOATDIV: ["float.div", 1],
    SmxOp.RND_TO_NEAREST: ["round", 1],
    SmxOp.RND_TO_FLOOR: ["floor", 1],
    SmxOp.RND_TO_CEIL: ["ceil", 1],
    SmxOp.RND_TO_ZERO: ["rndtozero", 1],
    SmxOp.FLOATCMP: ["float.cmp", 1],
    SmxOp.FLOAT_GT: ["float.gt", 1],
    SmxOp.FLOAT_GE: ["float.ge", 1],
    SmxOp.FLOAT_LT: ["float.lt", 1],
    SmxOp.FLOAT_LE: ["float.le", 1],
    SmxOp.FLOAT_NE: ["float.ne", 1],
    SmxOp.FLOAT_EQ: ["float.eq", 1],
    SmxOp.FLOAT_NOT: ["float.not", 1],
    SmxOp.CASE: ["case", 3],
}

sp_opcode_params_data = {
    SmxOp.ADD: [],
    SmxOp.ADD_C: [SmxParam.CONSTANT],
    SmxOp.ADDR_ALT: [SmxParam.STACK],
    SmxOp.ADDR_PRI: [SmxParam.STACK],
    SmxOp.AND: [],
    SmxOp.BOUNDS: [SmxParam.CONSTANT],
    SmxOp.BREAK: [],
    SmxOp.CALL: [SmxParam.FUNCTION],
    SmxOp.CASETBL: [SmxParam.CONSTANT, SmxParam.JUMP],
    SmxOp.CONST: [SmxParam.ADDRESS, SmxParam.CONSTANT],
    SmxOp.CONST_ALT: [SmxParam.CONSTANT],
    SmxOp.CONST_PRI: [SmxParam.CONSTANT],
    SmxOp.CONST_S: [SmxParam.STACK, SmxParam.CONSTANT],
    SmxOp.DEC: [SmxParam.ADDRESS],
    SmxOp.DEC_ALT: [],
    SmxOp.DEC_I: [],
    SmxOp.DEC_PRI: [],
    SmxOp.DEC_S: [SmxParam.STACK],
    SmxOp.EQ: [],
    SmxOp.EQ_C_ALT: [SmxParam.CONSTANT],
    SmxOp.EQ_C_PRI: [SmxParam.CONSTANT],
    SmxOp.FILL: [SmxParam.CONSTANT],
    SmxOp.GENARRAY: [SmxParam.CONSTANT],
    SmxOp.GENARRAY_Z: [SmxParam.CONSTANT],
    SmxOp.HALT: [SmxParam.CONSTANT],
    SmxOp.HEAP: [SmxParam.CONSTANT],
    SmxOp.IDXADDR: [],
    SmxOp.IDXADDR_B: [SmxParam.CONSTANT],
    SmxOp.INC: [SmxParam.ADDRESS],
    SmxOp.INC_ALT: [],
    SmxOp.INC_I: [],
    SmxOp.INC_PRI: [],
    SmxOp.INC_S: [SmxParam.STACK],
    SmxOp.INVERT: [],
    SmxOp.JEQ: [SmxParam.JUMP],
    SmxOp.JNEQ: [SmxParam.JUMP],
    SmxOp.JNZ: [SmxParam.JUMP],
    SmxOp.JSGEQ: [SmxParam.JUMP],
    SmxOp.JSGRTR: [SmxParam.JUMP],
    SmxOp.JSLEQ: [SmxParam.JUMP],
    SmxOp.JSLESS: [SmxParam.JUMP],
    SmxOp.JUMP: [SmxParam.JUMP],
    SmxOp.JZER: [SmxParam.JUMP],
    SmxOp.LIDX: [],
    SmxOp.LIDX_B: [SmxParam.CONSTANT],
    SmxOp.LOAD_ALT: [SmxParam.CONSTANT],
    SmxOp.LOAD_BOTH: [SmxParam.CONSTANT, SmxParam.CONSTANT],
    SmxOp.LOAD_I: [],
    SmxOp.LOAD_PRI: [SmxParam.CONSTANT],
    SmxOp.LOAD_S_ALT: [SmxParam.STACK],
    SmxOp.LOAD_S_BOTH: [SmxParam.STACK, SmxParam.STACK],
    SmxOp.LOAD_S_PRI: [SmxParam.STACK],
    SmxOp.LODB_I: [SmxParam.CONSTANT],
    SmxOp.LREF_S_ALT: [SmxParam.STACK],
    SmxOp.LREF_S_PRI: [SmxParam.STACK],
    SmxOp.MOVE_ALT: [],
    SmxOp.MOVE_PRI: [],
    SmxOp.MOVS: [SmxParam.CONSTANT],
    SmxOp.NEG: [],
    SmxOp.NEQ: [],
    SmxOp.NOP: [],
    SmxOp.NOT: [],
    SmxOp.OR: [],
    SmxOp.POP_ALT: [],
    SmxOp.POP_PRI: [],
    SmxOp.PROC: [],
    SmxOp.PUSH_ALT: [],
    SmxOp.PUSH_PRI: [],
    SmxOp.PUSH: [SmxParam.ADDRESS],
    SmxOp.PUSH2: [SmxParam.ADDRESS, SmxParam.ADDRESS],
    SmxOp.PUSH3: [SmxParam.ADDRESS, SmxParam.ADDRESS, SmxParam.ADDRESS],
    SmxOp.PUSH4: [SmxParam.ADDRESS, SmxParam.ADDRESS, SmxParam.ADDRESS, SmxParam.ADDRESS],
    SmxOp.PUSH5: [
      SmxParam.ADDRESS,
      SmxParam.ADDRESS,
      SmxParam.ADDRESS,
      SmxParam.ADDRESS,
      SmxParam.ADDRESS,
    ],
    SmxOp.PUSH_C: [SmxParam.CONSTANT],
    SmxOp.PUSH2_C: [SmxParam.CONSTANT, SmxParam.CONSTANT],
    SmxOp.PUSH3_C: [SmxParam.CONSTANT, SmxParam.CONSTANT, SmxParam.CONSTANT],
    SmxOp.PUSH4_C: [SmxParam.CONSTANT, SmxParam.CONSTANT, SmxParam.CONSTANT, SmxParam.CONSTANT],
    SmxOp.PUSH5_C: [
      SmxParam.CONSTANT,
      SmxParam.CONSTANT,
      SmxParam.CONSTANT,
      SmxParam.CONSTANT,
      SmxParam.CONSTANT,
    ],
    SmxOp.PUSH_S: [SmxParam.STACK],
    SmxOp.PUSH2_S: [SmxParam.STACK, SmxParam.STACK],
    SmxOp.PUSH3_S: [SmxParam.STACK, SmxParam.STACK, SmxParam.STACK],
    SmxOp.PUSH4_S: [SmxParam.STACK, SmxParam.STACK, SmxParam.STACK, SmxParam.STACK],
    SmxOp.PUSH5_S: [SmxParam.STACK, SmxParam.STACK, SmxParam.STACK, SmxParam.STACK, SmxParam.STACK],
    SmxOp.PUSH_ADR: [SmxParam.STACK],
    SmxOp.PUSH2_ADR: [SmxParam.STACK, SmxParam.STACK],
    SmxOp.PUSH3_ADR: [SmxParam.STACK, SmxParam.STACK, SmxParam.STACK],
    SmxOp.PUSH4_ADR: [SmxParam.STACK, SmxParam.STACK, SmxParam.STACK, SmxParam.STACK],
    SmxOp.PUSH5_ADR: [SmxParam.STACK, SmxParam.STACK, SmxParam.STACK, SmxParam.STACK, SmxParam.STACK],
    SmxOp.RETN: [],
    SmxOp.SDIV: [],
    SmxOp.SDIV_ALT: [],
    SmxOp.SGEQ: [],
    SmxOp.SGRTR: [],
    SmxOp.SHL: [],
    SmxOp.SHL_C_ALT: [SmxParam.CONSTANT],
    SmxOp.SHL_C_PRI: [SmxParam.CONSTANT],
    SmxOp.SHR: [],
    SmxOp.SHR_C_ALT: [SmxParam.CONSTANT],
    SmxOp.SHR_C_PRI: [SmxParam.CONSTANT],
    SmxOp.SLEQ: [],
    SmxOp.SLESS: [],
    SmxOp.SMUL: [],
    SmxOp.SMUL_C: [SmxParam.CONSTANT],
    SmxOp.SREF_S_ALT: [SmxParam.STACK],
    SmxOp.SREF_S_PRI: [SmxParam.STACK],
    SmxOp.SSHR: [],
    SmxOp.STACK: [SmxParam.CONSTANT],
    SmxOp.STOR_ALT: [SmxParam.CONSTANT],
    SmxOp.STOR_I: [],
    SmxOp.STOR_PRI: [SmxParam.CONSTANT],
    SmxOp.STOR_S_ALT: [SmxParam.STACK],
    SmxOp.STOR_S_PRI: [SmxParam.STACK],
    SmxOp.STRADJUST_PRI: [],
    SmxOp.STRB_I: [SmxParam.CONSTANT],
    SmxOp.SUB: [],
    SmxOp.SUB_ALT: [],
    SmxOp.SWAP_ALT: [],
    SmxOp.SWAP_PRI: [],
    SmxOp.SWITCH: [SmxParam.JUMP],
    SmxOp.SYSREQ_C: [SmxParam.NATIVE],
    SmxOp.SYSREQ_N: [SmxParam.NATIVE, SmxParam.CONSTANT],
    SmxOp.TRACKER_POP_SETHEAP: [],
    SmxOp.TRACKER_PUSH_C: [SmxParam.CONSTANT],
    SmxOp.XCHG: [],
    SmxOp.XOR: [],
    SmxOp.ZERO: [SmxParam.ADDRESS],
    SmxOp.ZERO_ALT: [],
    SmxOp.ZERO_PRI: [],
    SmxOp.ZERO_S: [SmxParam.STACK],
    SmxOp.REBASE: [SmxParam.ADDRESS, SmxParam.CONSTANT, SmxParam.CONSTANT],
    SmxOp.INITARRAY_PRI: [SmxParam.ADDRESS, SmxParam.CONSTANT, SmxParam.CONSTANT, SmxParam.CONSTANT, SmxParam.CONSTANT],
    SmxOp.INITARRAY_ALT: [SmxParam.ADDRESS, SmxParam.CONSTANT, SmxParam.CONSTANT, SmxParam.CONSTANT, SmxParam.CONSTANT],
    SmxOp.HEAP_SAVE: [],
    SmxOp.HEAP_RESTORE: [],
    SmxOp.CASE: [SmxParam.CONSTANT, SmxParam.JUMP],
}

def sp_opcode_mnemonic(op):
    if op in sp_opcode_info:
        #print('mnem op : %i %s' % (op, sp_opcode_info[op][0]))
        return sp_opcode_info[op][0]
    #print('mnem op : %i unknown' % (op))
    return 'unknown'

def sp_opcode_cells(op):
    if op in sp_opcode_info:
        #print('size op : %i %s' % (op, sp_opcode_info[op][0]))
        return sp_opcode_info[op][1]
    #print('size op : %i unknown' % op)
    return 1

def sp_opcode_params(op):
    if op in sp_opcode_params_data:
        #print('size op : %i %s' % (op, sp_opcode_info[op][0]))
        return sp_opcode_params_data[op]
    #print('size op : %i unknown' % op)
    return []
