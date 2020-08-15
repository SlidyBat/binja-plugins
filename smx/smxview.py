from binaryninja import *
from .smxtypes import *
from .smxopcodes import *
from .typebuilder import *
from struct import unpack
import zlib

class DefaultCallingConvention(CallingConvention):
    int_return_reg = 'pri'
    int_arg_regs = []
    stack_adjusted_on_return = False

class NativeCallingConvention(CallingConvention):
    int_return_reg = 'pri'
    int_arg_regs = []
    stack_adjusted_on_return = True

class SmxView(BinaryView):
    name = 'SMX'
    long_name = 'SourceMod Executable'

    @classmethod
    def is_valid_for_data(self, data):
        magic = data.read(0, 4)
        return magic == b'FFPS'
    
    def __init__(self, data):
        compression = unpack('<B', data.read(sp_file_hdr_t.members[2].offset, 1))[0]
        if compression == 1:
            dataoffs = unpack('<I', data.read(sp_file_hdr_t.members[7].offset, 4))[0]
            disksize = unpack('<I', data.read(sp_file_hdr_t.members[3].offset, 4))[0]
            imagesize = unpack('<I', data.read(sp_file_hdr_t.members[4].offset, 4))[0]
            decompressed_data = zlib.decompress(data[dataoffs:disksize], bufsize=imagesize-dataoffs)
            
            replacement_parent = BinaryView.new(data=data.read(0, dataoffs) + decompressed_data)
            BinaryView.__init__(self, parent_view=replacement_parent, file_metadata=data.file)
            
            self.data = replacement_parent
        else:
            BinaryView.__init__(self, parent_view=data, file_metadata=data.file)
            
            self.data = data
        
        self.arch = Architecture['sourcepawn']
        self.platform = Platform['sourcemod-sourcepawn']
    
    def read_cstr(self, addr):
        str = ''
        curr_char = addr
        while True:
            c = self.data[curr_char]
            curr_char += 1
            if c == b'\0':
                break
            str += c.decode('ascii')
        return str
    
    def perform_is_executable(self):
        return True
    
    def perform_get_entry_point(self):
        return self.sp_entry
    
    def init(self):
        self.arch.register_calling_convention(DefaultCallingConvention(self.arch, 'default'))
        self.arch.register_calling_convention(NativeCallingConvention(self.arch, 'native'))
        self.platform.default_calling_convention = self.arch.calling_conventions['default']
        self.platform.system_call_convention = self.arch.calling_conventions['native']
    
        self.add_auto_segment(0, len(self.parent_view), 0, len(self.parent_view), SegmentFlag.SegmentContainsData|SegmentFlag.SegmentReadable)
        
        self.init_header()
        
        for i in range(len(self.sp_sections_name)):
            self.init_section(i)
        
        self.add_analysis_completion_event(self.analyse_instrs)
        
        return True
        
    def init_header(self):
        magic, version, compression, disksize, imagesize, sections, stringtab, dataoffs = unpack('<IHBIIBII', self.data[:sp_file_hdr_t.width])
        
        self.define_data_var(0, Type.structure_type(sp_file_hdr_t))
        self.define_auto_symbol(Symbol(SymbolType.DataSymbol, 0, 'sp_file_hdr_t'))
        
        # Handle section headers
        self.sp_sections_name  = [''] * sections
        self.sp_sections_data  = [0] * sections
        self.sp_sections_size  = [0] * sections
        
        sp_stringtable_t = Structure()
        sp_stringtable_t.packed = True
        
        for i in range(sections):
            offs_start = sp_file_hdr_t.width + i*sp_file_section_t.width
            offs_end = offs_start + sp_file_section_t.width
            nameoffs, dataoffs, size = unpack('<III', self.data[offs_start:offs_end])
            
            self.sp_sections_data[i] = dataoffs
            self.sp_sections_size[i] = size
            self.sp_sections_name[i] = self.read_cstr(stringtab + nameoffs)
            
            sp_stringtable_t.append(Type.array(Type.char(), len(self.sp_sections_name[i]) + 1), 'section_%i' % i)
            self.define_data_var(offs_start, Type.structure_type(sp_file_section_t))
            self.define_auto_symbol(Symbol(SymbolType.DataSymbol, offs_start, 'sp_file_section_t %s' % self.sp_sections_name[i]))
        
        self.define_data_var(stringtab, Type.structure_type(sp_stringtable_t))
        self.define_auto_symbol(Symbol(SymbolType.DataSymbol, stringtab, 'sp_stringtable_t'))
    
    def init_section(self, index):
        name = self.sp_sections_name[index]
        dataoffs = self.sp_sections_data[index]
        size = self.sp_sections_size[index]
    
        if   name == '.code':                  self.init_code(name, dataoffs, size)
        elif name == '.data':                  self.init_data(name, dataoffs, size)
        elif name == '.publics':               self.init_publics(name, dataoffs, size)
        elif name == '.pubvars':               self.init_pubvars(name, dataoffs, size)
        elif name == '.names':                 self.init_names(name, dataoffs, size)
        elif name == 'rtti.data':              self.init_rtti_data(name, dataoffs, size)
        elif name == 'rtti.methods':           self.init_rtti_methods(name, dataoffs, size)
        elif name == 'rtti.natives':           self.init_rtti_natives(name, dataoffs, size)
        elif name == 'rtti.classdefs':         self.init_rtti_classdefs(name, dataoffs, size)
        elif name == 'rtti.fields':            self.init_rtti_fields(name, dataoffs, size)
        elif name == 'rtti.enumstructs':       self.init_rtti_enumstructs(name, dataoffs, size)
        elif name == 'rtti.enumstruct_fields': self.init_rtti_enumstruct_fields(name, dataoffs, size)
        elif name == '.dbg.files':             self.init_dbg_files(name, dataoffs, size)
        elif name == '.dbg.lines':             self.init_dbg_lines(name, dataoffs, size)
        elif name == '.dbg.info':              self.init_dbg_info(name, dataoffs, size)
        elif name == '.dbg.methods':           self.init_dbg_methods(name, dataoffs, size)
        elif name == '.dbg.globals':           self.init_dbg_globals(name, dataoffs, size)
        elif name == '.dbg.locals':            self.init_dbg_locals(name, dataoffs, size)
    
    def init_code(self, name, offs, size):
        self.add_auto_section(name, offs, size)
        
        codesize, cellsize, codeversion, flags, main, code, features = unpack('<IBBHIII', self.data.read(offs, sp_file_code_t.width))
        
        self.define_data_var(offs, Type.structure_type(sp_file_code_t))
        self.define_auto_symbol(Symbol(SymbolType.DataSymbol, offs, 'sp_file_code_t'))
        
        self.sp_code = CODE_SEGMENT
        self.sp_entry = self.sp_code + main
        self.add_auto_segment(CODE_SEGMENT, codesize, offs + code, codesize, SegmentFlag.SegmentContainsCode|SegmentFlag.SegmentReadable|SegmentFlag.SegmentExecutable)
        self.add_auto_section(name + '.unpacked', CODE_SEGMENT, codesize, SectionSemantics.ReadOnlyCodeSectionSemantics)
        self.add_entry_point(self.sp_entry)
        self.define_auto_symbol(Symbol(SymbolType.FunctionSymbol, self.sp_entry, 'main'))
        
    
    def init_data(self, name, offs, size):
        self.add_auto_section(name, offs, size)
        self.define_data_var(offs, Type.structure_type(sp_file_data_t))
        self.define_auto_symbol(Symbol(SymbolType.DataSymbol, offs, 'sp_file_data_t'))
        
        datasize, memsize, data = unpack('<III', self.data.read(offs, sp_file_data_t.width))
        
        self.sp_data = DATA_SEGMENT
        self.add_auto_segment(DATA_SEGMENT, memsize, offs + data, datasize, SegmentFlag.SegmentContainsData|SegmentFlag.SegmentReadable|SegmentFlag.SegmentWritable)
        self.add_auto_section(name + '.unpacked', DATA_SEGMENT, memsize, SectionSemantics.ReadWriteDataSectionSemantics)
    
    def init_publics(self, name, offs, size):
        self.add_auto_section(name, offs, size)
        
        row_count = size // sp_file_publics_t.width
        self.define_data_var(offs, Type.array(Type.structure_type(sp_file_publics_t), row_count))
        self.define_auto_symbol(Symbol(SymbolType.DataSymbol, offs, 'sp_file_publics_t'))
    
    def init_pubvars(self, name, offs, size):
        self.add_auto_section(name, offs, size)
        
        row_count = size // sp_file_pubvars_t.width
        self.define_data_var(offs, Type.array(Type.structure_type(sp_file_pubvars_t), row_count))
        self.define_auto_symbol(Symbol(SymbolType.DataSymbol, offs, 'sp_file_pubvars_t'))
    
    def init_natives(self, name, offs, size):
        self.add_auto_section(name, offs, size)
        self.define_data_var(offs, Type.structure_type(sp_file_natives_t))
        self.define_auto_symbol(Symbol(SymbolType.DataSymbol, offs, 'sp_file_natives_t'))
    
    def init_names(self, name, offs, size):
        self.add_auto_section(name, offs, size)
        
        stringoffs = offs
        while True:
            if stringoffs >= offs + size:
                break
            s = self.read_cstr(stringoffs)
            self.define_data_var(stringoffs, Type.array(Type.char(), len(s) + 1))
            stringoffs += len(s) + 1
    
    def init_rtti_data(self, name, offs, size):
        self.add_auto_section(name, offs, size)
    
    def init_rtti_methods(self, name, offs, size):
        self.add_auto_section(name, offs, size)
        self.define_data_var(offs, Type.structure_type(smx_rtti_table_header))
        self.define_auto_symbol(Symbol(SymbolType.DataSymbol, offs, 'smx_rtti_table_header %s' % name))
        
        _, _, row_count = unpack('<III', self.data.read(offs, smx_rtti_table_header.width))
        self.define_data_var(offs + smx_rtti_table_header.width, Type.array(Type.structure_type(smx_rtti_method), row_count))
        self.define_auto_symbol(Symbol(SymbolType.DataSymbol, offs + smx_rtti_table_header.width, 'smx_rtti_method'))
        
        for i in range(row_count):
            name, pcode_start, pcode_end, signature = unpack('<IIII', self.data.read(offs + smx_rtti_table_header.width + i*smx_rtti_method.width, smx_rtti_method.width))
            
            # Get function name
            names = self.get_section_by_name('.names')
            func_name = self.read_cstr(names.start + name)
            
            # Get function type
            typebuilder = TypeBuilder(self, signature)
            func_type = typebuilder.decode_function()
            
            self.add_function(self.sp_code + pcode_start)
            self.define_auto_symbol(Symbol(SymbolType.FunctionSymbol, self.sp_code + pcode_start, func_name))
            self.get_function_at(self.sp_code + pcode_start).set_user_type(func_type)
    
    def init_rtti_natives(self, name, offs, size):
        self.add_auto_section(name, offs, size)
        self.define_data_var(offs, Type.structure_type(smx_rtti_table_header))
        self.define_auto_symbol(Symbol(SymbolType.DataSymbol, offs, 'smx_rtti_table_header %s' % name))
        
        _, _, row_count = unpack('<III', self.data.read(offs, smx_rtti_table_header.width))
        self.define_data_var(offs + smx_rtti_table_header.width, Type.array(Type.structure_type(smx_rtti_native), row_count))
        self.define_auto_symbol(Symbol(SymbolType.DataSymbol, offs + smx_rtti_table_header.width, 'smx_rtti_native'))
        
        self.sp_natives = []
        for i in range(row_count):
            name, signature = unpack('<II', self.data.read(offs + smx_rtti_table_header.width + i*smx_rtti_native.width, smx_rtti_native.width))
            names = self.get_section_by_name('.names')
            self.sp_natives += [self.read_cstr(names.start + name)]
    
    def init_rtti_classdefs(self, name, offs, size):
        self.add_auto_section(name, offs, size)
        self.define_data_var(offs, Type.structure_type(smx_rtti_table_header))
        self.define_auto_symbol(Symbol(SymbolType.DataSymbol, offs, 'smx_rtti_table_header %s' % name))
        
        _, _, row_count = unpack('<III', self.data.read(offs, smx_rtti_table_header.width))
        self.define_data_var(offs + smx_rtti_table_header.width, Type.array(Type.structure_type(smx_rtti_classdef), row_count))
        self.define_auto_symbol(Symbol(SymbolType.DataSymbol, offs + smx_rtti_table_header.width, 'smx_rtti_classdef'))
    
    def init_rtti_fields(self, name, offs, size):
        self.add_auto_section(name, offs, size)
        self.define_data_var(offs, Type.structure_type(smx_rtti_table_header))
        self.define_auto_symbol(Symbol(SymbolType.DataSymbol, offs, 'smx_rtti_table_header %s' % name))
        
        _, _, row_count = unpack('<III', self.data.read(offs, smx_rtti_table_header.width))
        self.define_data_var(offs + smx_rtti_table_header.width, Type.array(Type.structure_type(smx_rtti_field), row_count))
        self.define_auto_symbol(Symbol(SymbolType.DataSymbol, offs + smx_rtti_table_header.width, 'smx_rtti_field'))
    
    def init_rtti_enumstructs(self, name, offs, size):
        self.add_auto_section(name, offs, size)
        self.define_data_var(offs, Type.structure_type(smx_rtti_table_header))
        self.define_auto_symbol(Symbol(SymbolType.DataSymbol, offs, 'smx_rtti_table_header %s' % name))
        
        _, _, row_count = unpack('<III', self.data.read(offs, smx_rtti_table_header.width))
        self.define_data_var(offs + smx_rtti_table_header.width, Type.array(Type.structure_type(smx_rtti_enumstruct), row_count))
        self.define_auto_symbol(Symbol(SymbolType.DataSymbol, offs + smx_rtti_table_header.width, 'smx_rtti_enumstruct'))
    
    def init_rtti_enumstruct_fields(self, name, offs, size):
        self.add_auto_section(name, offs, size)
        self.define_data_var(offs, Type.structure_type(smx_rtti_table_header))
        self.define_auto_symbol(Symbol(SymbolType.DataSymbol, offs, 'smx_rtti_table_header %s' % name))
        
        _, _, row_count = unpack('<III', self.data.read(offs, smx_rtti_table_header.width))
        self.define_data_var(offs + smx_rtti_table_header.width, Type.array(Type.structure_type(smx_rtti_es_field), row_count))
        self.define_auto_symbol(Symbol(SymbolType.DataSymbol, offs + smx_rtti_table_header.width, 'smx_rtti_es_field'))
    
    def init_dbg_files(self, name, offs, size):
        self.add_auto_section(name, offs, size)
        
        row_count = size // sp_fdbg_file_t.width
        self.define_data_var(offs, Type.array(Type.structure_type(sp_fdbg_file_t), row_count))
        self.define_auto_symbol(Symbol(SymbolType.DataSymbol, offs, 'sp_fdbg_file_t'))
    
    def init_dbg_lines(self, name, offs, size):
        self.add_auto_section(name, offs, size)
        
        row_count = size // sp_fdbg_line_t.width
        self.define_data_var(offs, Type.array(Type.structure_type(sp_fdbg_line_t), row_count))
        self.define_auto_symbol(Symbol(SymbolType.DataSymbol, offs, 'sp_fdbg_line_t'))
    
    def init_dbg_info(self, name, offs, size):
        self.add_auto_section(name, offs, size)
        self.define_data_var(offs, Type.structure_type(sp_fdbg_info_t))
        self.define_auto_symbol(Symbol(SymbolType.DataSymbol, offs + smx_rtti_table_header.width, 'sp_fdbg_info_t'))
    
    def init_dbg_methods(self, name, offs, size):
        self.add_auto_section(name, offs, size)
        self.define_data_var(offs, Type.structure_type(smx_rtti_table_header))
        self.define_auto_symbol(Symbol(SymbolType.DataSymbol, offs, 'smx_rtti_table_header %s' % name))
        
        _, _, row_count = unpack('<III', self.data.read(offs, smx_rtti_table_header.width))
        self.define_data_var(offs + smx_rtti_table_header.width, Type.array(Type.structure_type(smx_rtti_debug_method), row_count))
        self.define_auto_symbol(Symbol(SymbolType.DataSymbol, offs + smx_rtti_table_header.width, 'smx_rtti_debug_method'))
    
    def init_dbg_globals(self, name, offs, size):
        self.add_auto_section(name, offs, size)
        self.define_data_var(offs, Type.structure_type(smx_rtti_table_header))
        self.define_auto_symbol(Symbol(SymbolType.DataSymbol, offs, 'smx_rtti_table_header %s' % name))
        
        _, _, row_count = unpack('<III', self.data.read(offs, smx_rtti_table_header.width))
        self.define_data_var(offs + smx_rtti_table_header.width, Type.array(Type.structure_type(smx_rtti_debug_var), row_count))
        self.define_auto_symbol(Symbol(SymbolType.DataSymbol, offs + smx_rtti_table_header.width, 'smx_rtti_debug_var globals'))
    
    def init_dbg_locals(self, name, offs, size):
        self.add_auto_section(name, offs, size)
        self.define_data_var(offs, Type.structure_type(smx_rtti_table_header))
        self.define_auto_symbol(Symbol(SymbolType.DataSymbol, offs, 'smx_rtti_table_header %s' % name))
        
        _, _, row_count = unpack('<III', self.data.read(offs, smx_rtti_table_header.width))
        self.define_data_var(offs + smx_rtti_table_header.width, Type.array(Type.structure_type(smx_rtti_debug_var), row_count))
        self.define_auto_symbol(Symbol(SymbolType.DataSymbol, offs + smx_rtti_table_header.width, 'smx_rtti_debug_var locals'))
    
    def analyse_instrs(self):
        for func in self.functions:
            for bb in func:
                addr = bb.start
                while addr < bb.end:
                    data = self.read(addr, 6*4)
                    op = unpack('<I', data[:4])[0]
                    info = self.arch.get_instruction_info(data, addr)
                    self.analyse_instr(func, addr, op)
                    addr += info.length
    
    def analyse_instr(self, func, addr, op):
        if op == SmxOp.SWITCH:
            branches = []
            casetbl = unpack('<I', self.read(addr+4, 4))[0] + self.sp_code
            _, ncases, default = unpack('<III', self.read(casetbl, 3*4))
            branches += [(self.arch, default + self.sp_code)]
            for case in range(ncases):
                _, target = unpack('<II', self.read(casetbl + 3*4 + case*2*4, 2*4))
                branches += [(self.arch, target + self.sp_code)]
            func.set_user_indirect_branches(addr, branches)