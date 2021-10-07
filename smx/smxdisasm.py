from binaryninja import *
from .smxopcodes import *
from struct import unpack

def read_cell(data, index):
    return unpack('<i', data[index*4:(index+1)*4])[0]

def sp_decode(instr_data, addr):
    cell = read_cell(instr_data, 0)
    if not (cell >= 0 and cell < SMX_NUM_OPS):
        return None, None
    op = SmxOp(cell)
    cells = sp_opcode_cells(op)
    return op, cells

def sp_disasm(instr_data, addr, code_addr, data_addr):
    op, cells = sp_decode(instr_data, addr)
    mnem = sp_opcode_mnemonic(op)
    if cells <= 0:
        raise NotImplementedError('unimplemented instruction %s' % mnem)
    
    result = [InstructionTextToken(InstructionTextTokenType.TextToken, mnem)]
    params = sp_opcode_params(op)
    
    debug = mnem
    
    if len(params) >= 1:
        result += [InstructionTextToken(InstructionTextTokenType.TextToken, ' ')]
        
        for i in range(len(params)):
            param_type = params[i]
            param_val = read_cell(instr_data, i+1)
            if param_type == SmxParam.CONSTANT:
                result += [InstructionTextToken(InstructionTextTokenType.IntegerToken, str(param_val), value=param_val, size=4)]
                debug += str(param_val)
            elif param_type == SmxParam.STACK or param_type == SmxParam.NATIVE:
                result += [InstructionTextToken(InstructionTextTokenType.IntegerToken, hex(param_val), value=param_val, size=4)]
                debug += hex(param_val)
            elif param_type == SmxParam.JUMP or param_type == SmxParam.FUNCTION:
                result += [InstructionTextToken(InstructionTextTokenType.PossibleAddressToken, hex(param_val + code_addr), value=param_val + code_addr, size=4)]
                debug += hex(param_val + code_addr)
            elif param_type == SmxParam.ADDRESS:
                result += [InstructionTextToken(InstructionTextTokenType.PossibleAddressToken, hex(param_val + data_addr), value=param_val + data_addr, size=4)]
                debug += hex(param_val + data_addr)
            
            if i < len(params) - 1:
                result += [InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ',')]
                result += [InstructionTextToken(InstructionTextTokenType.TextToken, ' ')]
                debug += ', '
    
    #print(debug)
    if op == SmxOp.CASETBL:
        ncases = read_cell(instr_data, 1)
        cells += ncases * 2
    
    return result, cells * 4

def sp_instruction_info(instr_data, addr, code_addr, data_addr):
    op, cells = sp_decode(instr_data, addr)
    info = InstructionInfo()
    if cells == 0:
        raise NotImplementedError('unimplemented instruction')
    
    if op in [SmxOp.HALT, SmxOp.RETN]:
        info.add_branch(BranchType.FunctionReturn)
    if op in [SmxOp.SYSREQ_C, SmxOp.SYSREQ_N]:
        info.add_branch(BranchType.SystemCall)
    elif op == SmxOp.CALL:
        target = read_cell(instr_data, 1)
        info.add_branch(BranchType.CallDestination, code_addr + target)
    elif op == SmxOp.JUMP:
        target = read_cell(instr_data, 1)
        info.add_branch(BranchType.UnconditionalBranch, code_addr + target)
    elif op in [SmxOp.JZER, SmxOp.JNZ, SmxOp.JEQ, SmxOp.JNEQ, SmxOp.JSLESS, SmxOp.JSLEQ, SmxOp.JSGRTR, SmxOp.JSGEQ]:
        target = read_cell(instr_data, 1)
        info.add_branch(BranchType.TrueBranch, code_addr + target)
        info.add_branch(BranchType.FalseBranch, addr + 8)
    elif op == SmxOp.SWITCH:
        info.add_branch(BranchType.IndirectBranch)
    elif op == SmxOp.CASETBL:
        # Variable length instruction that needs to be handled specially
        ncases = read_cell(instr_data, 1)
        cells += ncases * 2
    info.length = cells * 4
    
    return info