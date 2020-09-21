from binaryninja import *
from enum import IntEnum

class TypeFlag(IntEnum):
    Bool = 0x01
    Int32 = 0x06
    Float32 = 0x0c
    Char8 = 0x0e
    Any = 0x10
    TopFunction = 0x11
    
    FixedArray = 0x30
    Array = 0x31
    Function = 0x32
    
    Enum = 0x42
    Typedef = 0x43
    Typeset = 0x44
    Classdef = 0x45
    EnumStruct = 0x46
    
    Void = 0x70
    Variadic = 0x71
    ByRef = 0x72
    Const = 0x73

class TypeBuilder:
    def __init__(self, bv, offset):
        self.bv = bv
        self.br = BinaryReader(bv)
        data = bv.get_section_by_name('rtti.data')
        self.br.seek(data.start + offset)
    
    def decode_type(self):
        is_const = self.match(TypeFlag.Const)
        
        b = self.read8()
        if b in [TypeFlag.Bool, TypeFlag.Int32, TypeFlag.Char8, TypeFlag.Any, TypeFlag.TopFunction]:
            return Type.int(4)
        if b == TypeFlag.Float32:
            return Type.float(4)
        if b == TypeFlag.FixedArray:
            size = self.decode_uint32()
            inner = self.decode_type()
            return Type.pointer(self.bv.arch, inner)
        if b == TypeFlag.Array:
            inner = self.decode_type()
            return Type.pointer(self.bv.arch, inner)
        # TODO
        if b == TypeFlag.Enum:
            index = self.decode_uint32()
        if b == TypeFlag.Typedef:
            index = self.decode_uint32()
        if b == TypeFlag.Typeset:
            index = self.decode_uint32()
        if b == TypeFlag.Classdef:
            index = self.decode_uint32()
        if b == TypeFlag.EnumStruct:
            index = self.decode_uint32()
        if b == TypeFlag.Function:
            return self.decode_function()
        
        return Type.int(4)
    
    
    def decode_function(self):
        argc = self.read8()
        
        varargs = self.match(TypeFlag.Variadic)
        if self.match(TypeFlag.Void):
            ret = Type.void()
        else:
            ret = self.decode_type()
        
        args = []
        for i in range(argc):
            by_ref = self.match(TypeFlag.ByRef)
            arg = self.decode_type()
            if by_ref:
                arg = Type.pointer(self.bv.arch, arg)
            args += [arg]
        
        return Type.function(ret, args, variable_arguments=varargs)
        
    def decode_uint32(self):
        value = 0
        shift = 0
        while True:
            b = self.read8()
            value |= (b & 0x7f) << shift
            if (b & 0x80) == 0:
                break
            shift += 7
        return value
    
    # Helpers
    def read8(self):
        return self.br.read8()
    def read16(self):
        return self.br.read16()
    def read32(self):
        return self.br.read32()
    def peek8(self):
        val = self.br.read8()
        self.br.offset -= 1
        return val
    def peek16(self):
        val = self.br.read16()
        self.br.offset -= 2
        return val
    def peek32(self):
        val = self.br.read32()
        self.br.offset -= 4
        return val
    def match(self, b):
        if self.peek8() != b:
            return False
        self.offset += 1
        return True
    @property
    def offset(self):
        return self.br.offset
    @offset.setter
    def offset(self, value):
        self.br.offset = value