from binaryninja import *
from .smxopcodes import *
from struct import unpack

class SmxLifter(SmxOpcodeVisitor):
    def __init__(self, data, addr, il):
        super(SmxLifter, self).__init__()
        self.data = il.source_function.view
        self.addr = addr
        self.il = il
    
    # Helpers
    def read_cell(self, addr):
        return unpack('<I', self.data.read(addr, 4))[0]
    
    def read_param(self, n):
        return self.read_cell(self.addr + 4 + 4*n)
    
    def read_params(self, nparams):
        return [self.read_param(n) for n in range(nparams)]
    
    def read_jump_target(self):
        return self.read_param(0) + CODE_SEGMENT
    
    def read_addr(self, n):
        return self.read_param(n) + DATA_SEGMENT
    
    def read_addrs(self, nparams):
        return [self.read_addr(n) for n in range(nparams)]
    
    # Easy access to registers
    @property
    def pri(self):
        return self.il.reg(4, 'pri')
    @property
    def alt(self):
        return self.il.reg(4, 'alt')
    @property
    def heap(self):
        return self.il.reg(4, 'heap')
    @property
    def frm(self):
        return self.il.reg(4, 'frm')
    @property
    def sp(self):
        return self.il.reg(4, 'sp')
    
    def label(self, addr):
        return self.il.get_label_for_address(self.data.arch, addr)
    
    def i(self, instr):
        self.il.append(instr)
    # In SP everything is a 4 byte cell, gets tedious having to specify with every function...
    def push(self, val):
        return self.il.push(4, val)
    def pop(self):
        return self.il.pop(4)
    def set_reg(self, reg, value):
        return self.il.set_reg(4, reg, value)
    def const(self, c):
        return self.il.const(4, c)
    def ptr(self, p):
        return self.il.const_pointer(4, p)
    def add(self, a, b):
        return self.il.add(4, a, b)
    def sub(self, a, b):
        return self.il.sub(4, a, b)
    def mult(self, a, b):
        return self.il.mult(4, a, b)
    def ret(self, addr):
        return self.il.ret(addr)
    def store(self, addr, value):
        return self.il.store(4, addr, value)
    def load(self, addr):
        return self.il.load(4, addr)
    def frame_value(self, offset):
        return self.add(self.frm, self.const(offset))
    def jump_cond(self, cond, target, fallthrough=None):
        if fallthrough == None:
            fallthrough = self.addr + 8
        true = self.label(target)
        false = self.label(fallthrough)
        if true != None and false != None:
            self.i(self.il.if_expr(cond, true, false))
            return
        if true != None:
            false = LowLevelILLabel()
            self.i(self.il.if_expr(cond, true, false))
            self.il.mark_label(false)
            self.i(self.il.jump(self.ptr(fallthrough)))
            return
        if false != None:
            true = LowLevelILLabel()
            self.i(self.il.if_expr(cond, true, false))
            self.il.mark_label(true)
            self.i(self.il.jump(self.ptr(target)))
            return
        
        true = LowLevelILLabel()
        false = LowLevelILLabel()
        self.i(self.il.if_expr(cond, true, false))
        self.il.mark_label(true)
        self.i(self.il.jump(self.ptr(target)))
        self.il.mark_label(false)
        self.i(self.il.jump(self.ptr(fallthrough)))
    
    def visit_NONE(self):
        self.i(self.il.nop())
    def visit_BREAK(self):
        pass
    
    def visit_PROC(self):
        self.i(self.push(self.frm))
        self.i(self.push(self.heap))
        self.i(self.set_reg('frm', self.sp))
    
    def visit_ENDPROC(self):
        pass
    
    def visit_HALT(self):
        self.i(self.il.no_ret())
    
    def visit_RETN(self):
        self.i(self.set_reg('heap', self.pop()))
        self.i(self.set_reg('frm', self.pop()))
        self.i(self.ret(self.pop()))
    
    def visit_PUSH_C_n(self, nvals):
        vals = self.read_params(nvals)
        for val in vals:
            self.i(self.push(self.const(val)))
    def visit_PUSH_C(self):
        self.visit_PUSH_C_n(1)
    def visit_PUSH2_C(self):
        self.visit_PUSH_C_n(2)
    def visit_PUSH3_C(self):
        self.visit_PUSH_C_n(3)
    def visit_PUSH4_C(self):
        self.visit_PUSH_C_n(4)
    def visit_PUSH5_C(self):
        self.visit_PUSH_C_n(5)
    
    def visit_PUSH_ADR_n(self, nvals):
        offsets = self.read_params(nvals)
        for offset in offsets:
            self.i(self.push(self.frame_value(offset)))
    def visit_PUSH_ADR(self):
        self.visit_PUSH_ADR_n(1)
    def visit_PUSH2_ADR(self):
        self.visit_PUSH_ADR_n(2)
    def visit_PUSH3_ADR(self):
        self.visit_PUSH_ADR_n(3)
    def visit_PUSH4_ADR(self):
        self.visit_PUSH_ADR_n(4)
    def visit_PUSH5_ADR(self):
        self.visit_PUSH_ADR_n(5)
    
    def visit_PUSH_n(self, nvals):
        addresses = self.read_addrs(nvals)
        for address in addresses:
            self.i(self.push(self.load(self.ptr(address))))
    def visit_PUSH(self):
        self.visit_PUSH_n(1)
    def visit_PUSH2(self):
        self.visit_PUSH_n(2)
    def visit_PUSH3(self):
        self.visit_PUSH_n(3)
    def visit_PUSH4(self):
        self.visit_PUSH_n(4)
    def visit_PUSH5(self):
        self.visit_PUSH_n(5)
    
    def visit_PUSH_S_n(self, nvals):
        offsets = self.read_params(nvals)
        for offset in offsets:
            self.i(self.push(self.load(self.frame_value(offset))))
    def visit_PUSH_S(self):
        self.visit_PUSH_S_n(1)
    def visit_PUSH2_S(self):
        self.visit_PUSH_S_n(2)
    def visit_PUSH3_S(self):
        self.visit_PUSH_S_n(3)
    def visit_PUSH4_S(self):
        self.visit_PUSH_S_n(4)
    def visit_PUSH5_S(self):
        self.visit_PUSH_S_n(5)
    
    def visit_PUSH_PRI(self):
        self.i(self.push(self.pri))
    def visit_PUSH_ALT(self):
        self.i(self.push(self.alt))
    
    def visit_POP_PRI(self):
        self.i(self.set_reg('pri', self.pop()))
    def visit_POP_ALT(self):
        self.i(self.set_reg('alt', self.pop()))
    
    def visit_LOAD_PRI(self):
        self.i(self.set_reg('pri', self.load(self.ptr(self.read_addr(0)))))
    def visit_LOAD_ALT(self):
        self.i(self.set_reg('alt', self.load(self.ptr(self.read_addr(0)))))
    def visit_LOAD_S_PRI(self):
        self.i(self.set_reg('pri', self.load(self.frame_value(self.read_param(0)))))
    def visit_LOAD_S_ALT(self):
        self.i(self.set_reg('alt', self.load(self.frame_value(self.read_param(0)))))
    def visit_LOAD_BOTH(self):
        self.i(self.set_reg('pri', self.load(self.ptr(self.read_addr(0)))))
        self.i(self.set_reg('alt', self.load(self.ptr(self.read_addr(1)))))
    def visit_LOAD_S_BOTH(self):
        self.i(self.set_reg('pri', self.load(self.frame_value(self.read_param(0)))))
        self.i(self.set_reg('alt', self.load(self.frame_value(self.read_param(1)))))
    def visit_LOAD_I(self):
        self.i(self.set_reg('pri', self.load(self.pri)))
    def visit_LODB_I(self):
        width = self.read_param(0)
        if width == 1:
            self.i(self.il.set_reg(1, 'pri', self.load(self.pri)))
        elif width == 2:
            self.i(self.il.set_reg(2, 'pri', self.load(self.pri)))
        else:
            self.i(self.set_reg('pri', self.load(self.pri)))
    
    def visit_STOR_PRI(self):
        self.i(self.store(self.ptr(self.read_addr(0)), self.pri))
    def visit_STOR_ALT(self):
        self.i(self.store(self.ptr(self.read_addr(0)), self.alt))
    def visit_STOR_S_PRI(self):
        self.i(self.store(self.frame_value(self.read_param(0)), self.pri))
    def visit_STOR_S_ALT(self):
        self.i(self.store(self.frame_value(self.read_param(0)), self.alt))
    def visit_STOR_I(self):
        self.i(self.store(self.alt, self.pri))
    def visit_STRB_I(self):
        width = self.read_param(0)
        if width == 1:
            self.i(self.il.store(1, self.alt, self.pri))
        elif width == 2:
            self.i(self.il.store(2, self.alt, self.pri))
        else:
            self.i(self.store(self.alt, self.pri))
    
    # TODO: how to handle this
    def visit_SYSREQ_C(self):
        self.i(self.push(self.const(index)))
        self.i(self.il.system_call())
        #self.i(self.set_reg('sp', self.add(self.sp, self.const(4))))
    def visit_SYSREQ_N(self):
        index = self.read_param(0)
        nparams = self.read_param(1)
        self.i(self.push(self.const(index)))
        self.i(self.il.system_call())
        self.i(self.set_reg('sp', self.add(self.sp, self.mult(self.const(nparams + 1), self.const(4)))))
    
    def visit_ADDR_PRI(self):
        self.i(self.set_reg('pri', self.frame_value(self.read_param(0))))
    def visit_ADDR_ALT(self):
        self.i(self.set_reg('alt', self.frame_value(self.read_param(0))))
    
    def visit_ZERO_PRI(self):
        self.i(self.set_reg('pri', self.const(0)))
    def visit_ZERO_ALT(self):
        self.i(self.set_reg('alt', self.const(0)))
    def visit_ZERO(self):
        self.i(self.store(self.ptr(self.read_param(0)), self.const(0)))
    def visit_ZERO_S(self):
        self.i(self.store(self.frame_value(self.read_param(0)), self.const(0)))
    
    def visit_CONST_PRI(self):
        self.i(self.set_reg('pri', self.const(self.read_param(0))))
    def visit_CONST_ALT(self):
        self.i(self.set_reg('alt', self.const(self.read_param(0))))
    def visit_CONST(self):
        self.i(self.store(self.ptr(self.read_param(0)), self.const(self.read_param(1))))
    def visit_CONST_S(self):
        self.i(self.store(self.frame_value(self.read_param(0)), self.const(self.read_param(1))))
    
    def visit_CALL(self):
        # Save number of args into temp register
        # We do this so it doesn't show up as a function parameter
        self.i(self.set_reg(LLIL_TEMP(1), self.pop()))
        
        self.i(self.il.call(self.ptr(self.read_jump_target())))
        
        # Clean up stack
        # This should really be done in RETN, but we do it here so the temp reg hack above works
        self.i(self.set_reg('sp', self.add(self.sp, self.mult(self.il.reg(4, LLIL_TEMP(1)), self.const(4)))))
    
    def visit_JUMP(self):
        self.i(self.il.jump(self.const(self.read_jump_target())))
    def visit_JZER(self):
        self.jump_cond(self.il.compare_equal(4, self.pri, self.const(0)), self.read_jump_target())
    def visit_JNZ(self):
        self.jump_cond(self.il.compare_not_equal(4, self.pri, self.const(0)), self.read_jump_target())
    def visit_JEQ(self):
        self.jump_cond(self.il.compare_equal(4, self.pri, self.alt), self.read_jump_target())
    def visit_JNEQ(self):
        self.jump_cond(self.il.compare_not_equal(4, self.pri, self.alt), self.read_jump_target())
    def visit_JSLESS(self):
        self.jump_cond(self.il.compare_signed_less_than(4, self.pri, self.alt), self.read_jump_target())
    def visit_JSLEQ(self):
        self.jump_cond(self.il.compare_signed_less_equal(4, self.pri, self.alt), self.read_jump_target())
    def visit_JSGRTR(self):
        self.jump_cond(self.il.compare_signed_greater_than(4, self.pri, self.alt), self.read_jump_target())
    def visit_JSGEQ(self):
        self.jump_cond(self.il.compare_signed_greater_equal(4, self.pri, self.alt), self.read_jump_target())
    
    def visit_ADD_C(self):
        self.i(self.set_reg('pri', self.add(self.pri, self.const(self.read_param(0)))))
    def visit_ADD(self):
        self.i(self.set_reg('pri', self.add(self.pri, self.alt)))
    def visit_SUB(self):
        self.i(self.set_reg('pri', self.sub(self.pri, self.alt)))
    def visit_SUB_ALT(self):
        self.i(self.set_reg('pri', self.sub(self.alt, self.pri)))
    def visit_SMUL_C(self):
        self.i(self.set_reg('pri', self.il.mult(4, self.pri, self.const(self.read_param(0)))))
    def visit_SMUL(self):
        self.i(self.set_reg('pri', self.il.mult(4, self.pri, self.alt)))
    def visit_SDIV(self):
        self.i(self.set_reg(LLIL_TEMP(0), self.il.div_signed(4, self.pri, self.alt)))
        self.i(self.set_reg('alt', self.il.mod_signed(4, self.pri, self.alt)))
        self.i(self.set_reg('pri', self.il.reg(4, LLIL_TEMP(0))))
    def visit_SDIV_ALT(self):
        self.i(self.set_reg(LLIL_TEMP(0), self.il.div_signed(4, self.alt, self.pri)))
        self.i(self.set_reg('alt', self.il.mod_signed(4, self.alt, self.pri)))
        self.i(self.set_reg('pri', self.il.reg(4, LLIL_TEMP(0))))
    def visit_AND(self):
        self.i(self.set_reg('pri', self.il.and_expr(4, self.pri, self.alt)))
    def visit_OR(self):
        self.i(self.set_reg('pri', self.il.or_expr(4, self.pri, self.alt)))
    def visit_XOR(self):
        self.i(self.set_reg('pri', self.il.xor_expr(4, self.pri, self.alt)))
    def visit_NEG(self):
        self.i(self.set_reg('pri', self.il.neg_expr(4, self.pri)))
    def visit_NOT(self):
        true = LowLevelILLabel()
        false = LowLevelILLabel()
        exit = LowLevelILLabel()
        self.i(self.il.if_expr(self.il.compare_not_equal(4, self.pri, self.const(0)), true, false))
        self.il.mark_label(true)
        self.i(self.set_reg('pri', self.const(0)))
        self.il.goto(exit)
        self.il.mark_label(false)
        self.i(self.set_reg('pri', self.const(1)))
        self.il.mark_label(exit)
    def visit_INVERT(self):
        self.i(self.set_reg('pri', self.il.not_expr(4, self.pri)))
    def visit_SHL_C_PRI(self):
        self.i(self.set_reg('pri', self.il.shift_left(4, self.pri, self.const(self.read_param(0)))))
    def visit_SHL_C_ALT(self):
        self.i(self.set_reg('alt', self.il.shift_left(4, self.alt, self.const(self.read_param(0)))))
    def visit_SHL(self):
        self.i(self.set_reg('pri', self.il.shift_left(4, self.pri, self.alt)))
    def visit_SHR(self):
        self.i(self.set_reg('pri', self.il.logical_shift_right(4, self.pri, self.alt)))
    def visit_SSHR(self):
        self.i(self.set_reg('pri', self.il.arith_shift_right(4, self.pri, self.alt)))
    
    def visit_EQ(self):
        self.i(self.set_reg('pri', self.il.compare_equal(4, self.pri, self.alt)))
    def visit_NEQ(self):
        self.i(self.set_reg('pri', self.il.compare_not_equal(4, self.pri, self.alt)))
    def visit_SLESS(self):
        self.i(self.set_reg('pri', self.il.compare_signed_less_than(4, self.pri, self.alt)))
    def visit_SLEQ(self):
        self.i(self.set_reg('pri', self.il.compare_signed_less_equal(4, self.pri, self.alt)))
    def visit_SGRTR(self):
        self.i(self.set_reg('pri', self.il.compare_signed_greater_than(4, self.pri, self.alt)))
    def visit_SGEQ(self):
        self.i(self.set_reg('pri', self.il.compare_signed_greater_equal(4, self.pri, self.alt)))
    def visit_EQ_C_PRI(self):
        self.i(self.set_reg('pri', self.il.compare_equal(4, self.pri, self.const(self.read_param(0)))))
    def visit_EQ_C_ALT(self):
        self.i(self.set_reg('pri', self.il.compare_equal(4, self.alt, self.const(self.read_param(0)))))
    
    def visit_INC_PRI(self):
        self.i(self.set_reg('pri', self.add(self.pri, self.const(1))))
    def visit_INC_ALT(self):
        self.i(self.set_reg('alt', self.add(self.alt, self.const(1))))
    def visit_INC(self):
        self.i(self.store(self.pri, self.add(self.load(self.pri), self.const(1))))
    def visit_INC_S(self):
        addr = self.frame_value(self.read_param(0))
        self.i(self.store(addr, self.add(self.load(addr), self.const(1))))
    def visit_INC_I(self):
        addr = self.ptr(self.read_addr(0))
        self.i(self.store(addr, self.add(self.load(addr), self.const(1))))
    def visit_DEC_PRI(self):
        self.i(self.set_reg('pri', self.sub(self.pri, self.const(1))))
    def visit_DEC_ALT(self):
        self.i(self.set_reg('alt', self.sub(self.alt, self.const(1))))
    def visit_DEC(self):
        self.i(self.store(self.pri, self.sub(self.load(self.pri), self.const(1))))
    def visit_DEC_S(self):
        addr = self.frame_value(self.read_param(0))
        self.i(self.store(addr, self.sub(self.load(addr), self.const(1))))
    def visit_DEC_I(self):
        addr = self.ptr(self.read_addr(0))
        self.i(self.store(addr, self.sub(self.load(addr), self.const(1))))
    
    def visit_MOVS(self):
        self.i(self.il.unimplemented())
    def visit_FILL(self):
        self.i(self.set_reg(LLIL_TEMP(0), self.const(self.read_param(0))))
        loop = LowLevelILLabel()
        exit = self.il.get_label_for_address(self.data.arch, self.addr + 8)
        if exit == None:
            exit = LowLevelILLabel()
        self.il.mark_label(loop)
        self.i(self.set_reg(LLIL_TEMP(0), self.sub(self.il.reg(4, LLIL_TEMP(0)), self.const(4))))
        self.i(self.store(self.add(self.alt, self.il.reg(4, LLIL_TEMP(0))), self.pri))
        self.i(self.il.if_expr(self.il.compare_not_equal(4, self.il.reg(4, LLIL_TEMP(0)), self.const(0)), loop, exit))
        self.il.mark_label(exit)
    
    def visit_SWITCH(self):
        self.i(self.il.jump(self.const(self.read_jump_target())))
    def visit_CASETBL(self):
        ncases = self.read_param(0)
        default = self.read_addr(1)
        for i in range(ncases):
            value = self.read_param(2 + 2*i + 0)
            target = self.read_addr(2 + 2*i + 1)
            self.jump_cond(self.il.compare_equal(4, self.pri, self.const(value)), target)
    
    def visit_LIDX(self):
        addr = self.add(self.alt, self.mult(self.pri, self.const(4)))
        self.i(self.set_reg('pri', self.load(addr)))
    def visit_IDXADDR(self):
        addr = self.add(self.alt, self.mult(self.pri, self.const(4)))
        self.i(self.set_reg('pri', addr))
    def visit_LREF_S_PRI(self):
        address = self.frame_value(self.read_param(0))
        self.i(self.set_reg('pri', self.load(address)))
    def visit_LREF_S_ALT(self):
        address = self.frame_value(self.read_param(0))
        self.i(self.set_reg('alt', self.load(address)))
    def visit_SREF_S_PRI(self):
        address = self.frame_value(self.read_param(0))
        self.i(self.store(address, self.pri))
    def visit_SREF_S_ALT(self):
        address = self.frame_value(self.read_param(0))
        self.i(self.store(address, self.alt))
    
    def visit_MOVE_PRI(self):
        self.i(self.set_reg('pri', self.alt))
    def visit_MOVE_ALT(self):
        self.i(self.set_reg('alt', self.pri))
    def visit_SWAP_PRI(self):
        self.i(self.set_reg(LLIL_TEMP(0), self.pri))
        self.i(self.set_reg('pri', self.pop()))
        self.i(self.push(self.il.reg(4, LLIL_TEMP(0))))
    def visit_SWAP_ALT(self):
        self.i(self.set_reg(LLIL_TEMP(0), self.alt))
        self.i(self.set_reg('alt', self.pop()))
        self.i(self.push(self.il.reg(4, LLIL_TEMP(0))))
    def visit_XCHG(self):
        self.i(self.set_reg(LLIL_TEMP(0), self.pri))
        self.i(self.set_reg('pri', self.alt))
        self.i(self.set_reg('alt', self.il.reg(4, LLIL_TEMP(0))))
    
    def visit_STACK(self):
        self.i(self.set_reg('sp', self.add(self.sp, self.const(self.read_param(0)))))
    def visit_HEAP(self):
        self.i(self.set_reg('alt', self.heap))
        self.i(self.set_reg('heap', self.add(self.heap, self.const(self.read_param(0)))))
    
    def visit_TRACKER_PUSH_C(self):
        amount = self.read_param(0)
        self.i(self.store(self.heap, self.const(amount)))
        self.i(self.set_reg('heap', self.add(self.heap, self.const(amount))))
    def visit_TRACKER_POP_SETHEAP(self):
        self.i(self.set_reg('heap', self.sub(self.heap, self.const(4))))
        amount = self.load(self.heap)
        self.i(self.set_reg('heap', self.sub(self.heap, amount)))
    
    def visit_GENARRAY(self):
        self.i(self.il.unimplemented())
    def visit_GENARRAY_Z(self):
        self.i(self.il.unimplemented())
    def visit_IDXADDR(self):
        self.i(self.set_reg('pri', self.add(self.alt, self.mult(self.pri, self.const(4)))))
    def visit_BOUNDS(self):
        pass
    def visit_REBASE(self):
        self.i(self.il.unimplemented())
    
    def visit_STRADJUST_PRI(self):
        self.i(self.set_reg('pri', self.il.arith_shift_right(4, self.add(self.pri, self.const(4)), self.const(2))))
    
    def visit_FABS(self):
        self.i(self.set_reg('pri', self.pop()))
        self.i(self.set_reg('pri', self.il.float_abs(4, self.pri)))
    def visit_FLOAT(self):
        self.i(self.set_reg('pri', self.pop()))
        self.i(self.set_reg('pri', self.il.int_to_float(4, self.pri)))
    def visit_FLOATADD(self):
        left = self.pop()
        right = self.pop()
        self.i(self.set_reg('pri', self.il.float_add(4, left, right)))
    def visit_FLOATSUB(self):
        left = self.pop()
        right = self.pop()
        self.i(self.set_reg('pri', self.il.float_sub(4, left, right)))
    def visit_FLOATMUL(self):
        left = self.pop()
        right = self.pop()
        self.i(self.set_reg('pri', self.il.float_mult(4, left, right)))
    def visit_FLOATMUL(self):
        left = self.pop()
        right = self.pop()
        self.i(self.set_reg('pri', self.il.float_div(4, left, right)))
    def visit_RND_TO_NEAREST(self):
        self.i(self.set_reg('pri', self.pop()))
        self.i(self.set_reg('pri', self.il.round_to_int(4, self.pri)))
    def visit_RND_TO_FLOOR(self):
        self.i(self.set_reg('pri', self.pop()))
        self.i(self.set_reg('pri', self.il.round_to_int(4, self.pri)))
    def visit_RND_TO_FLOOR(self):
        self.i(self.set_reg('pri', self.pop()))
        self.i(self.set_reg('pri', self.il.floor(4, self.pri)))
    def visit_RND_TO_CEIL(self):
        self.i(self.set_reg('pri', self.pop()))
        self.i(self.set_reg('pri', self.il.ceil(4, self.pri)))
    def visit_RND_TO_ZERO(self):
        self.i(self.il.unimplemented())
    def visit_FLOATCMP(self):
        self.i(self.il.unimplemented())
    def visit_FLOAT_GT(self):
        self.i(self.il.unimplemented())
    def visit_FLOAT_GE(self):
        self.i(self.il.unimplemented())
    def visit_FLOAT_LE(self):
        self.i(self.il.unimplemented())
    def visit_FLOAT_LT(self):
        self.i(self.il.unimplemented())
    def visit_FLOAT_EQ(self):
        self.i(self.il.unimplemented())
    def visit_FLOAT_NE(self):
        self.i(self.il.unimplemented())
    def visit_FLOAT_NOT(self):
        self.i(self.il.unimplemented())