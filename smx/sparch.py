from binaryninja import *
from .smxdisasm import *
from .smxtypes import *
from .smxlifter import *

class SourceMod(Platform):
    name = 'sourcemod-sourcepawn'

class SourcePawn(Architecture):
    name = 'sourcepawn'
    
    address_size = 4
    default_int_size = 4
    instr_alignment = 4
    max_instr_length = 256
    
    sp_code = 0
    sp_data = 0
    
    regs = {
        'pri': RegisterInfo('pri', 4),
        'alt': RegisterInfo('alt', 4),
        
        'heap': RegisterInfo('frm', 4),
        'frm': RegisterInfo('frm', 4),
        'sp': RegisterInfo('sp', 4),
    }
    
    stack_pointer = 'sp'
    
    def __init__(self):
        Architecture.__init__(self)
    
    def get_instruction_info(self, data, addr):
        return sp_instruction_info(data, addr, CODE_SEGMENT, DATA_SEGMENT)
    
    def get_instruction_text(self, data, addr):
        return sp_disasm(data, addr, CODE_SEGMENT, DATA_SEGMENT)
    
    def get_instruction_low_level_il(self, data, addr, il):
        if il.source_function == None:
            return None
        
        op, cells = sp_decode(data, addr)
        lifter = SmxLifter(data, addr, il)
        lifter.visit(op)
        return cells * 4