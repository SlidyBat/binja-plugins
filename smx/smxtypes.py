from binaryninja import *

uint32_t = Type.int(4, False)
uint16_t = Type.int(2, False)
uint8_t = Type.int(1, False)
int32_t = Type.int(4, True)
int16_t = Type.int(2, True)
int8_t = Type.int(1, True)

sp_file_hdr_t = Structure()
sp_file_hdr_t.packed = True
sp_file_hdr_t.append(uint32_t, 'magic')
sp_file_hdr_t.append(uint16_t, 'version')
sp_file_hdr_t.append(uint8_t, 'compression')
sp_file_hdr_t.append(uint32_t, 'disksize')
sp_file_hdr_t.append(uint32_t, 'imagesize')
sp_file_hdr_t.append(uint8_t, 'sections')
sp_file_hdr_t.append(uint32_t, 'stringtab')
sp_file_hdr_t.append(uint32_t, 'dataoffs')

sp_file_section_t = Structure()
sp_file_section_t.packed = True
sp_file_section_t.append(uint32_t, 'nameoffs')
sp_file_section_t.append(uint32_t, 'dataoffs')
sp_file_section_t.append(uint32_t, 'size')

sp_file_code_t = Structure()
sp_file_code_t.packed = True
sp_file_code_t.append(uint32_t, 'codesize')
sp_file_code_t.append(uint8_t, 'cellsize')
sp_file_code_t.append(uint8_t, 'codeversion')
sp_file_code_t.append(uint16_t, 'flags')
sp_file_code_t.append(uint32_t, 'main')
sp_file_code_t.append(uint32_t, 'code')
sp_file_code_t.append(uint32_t, 'features')

sp_file_data_t = Structure()
sp_file_data_t.packed = True
sp_file_data_t.append(uint32_t, 'datasize')
sp_file_data_t.append(uint32_t, 'memsize')
sp_file_data_t.append(uint32_t, 'data')

sp_file_publics_t = Structure()
sp_file_publics_t.packed = True
sp_file_publics_t.append(uint32_t, 'address')
sp_file_publics_t.append(uint32_t, 'name')

sp_file_pubvars_t = Structure()
sp_file_pubvars_t.packed = True
sp_file_pubvars_t.append(uint32_t, 'address')
sp_file_pubvars_t.append(uint32_t, 'name')

sp_file_natives_t = Structure()
sp_file_natives_t.packed = True
sp_file_natives_t.append(uint32_t, 'name')

smx_rtti_table_header = Structure()
smx_rtti_table_header.packed = True
smx_rtti_table_header.append(uint32_t, 'header_size')
smx_rtti_table_header.append(uint32_t, 'row_size')
smx_rtti_table_header.append(uint32_t, 'row_count')

sp_fdbg_info_t = Structure()
sp_fdbg_info_t.packed = True
sp_fdbg_info_t.append(uint32_t, 'num_files')
sp_fdbg_info_t.append(uint32_t, 'num_lines')
sp_fdbg_info_t.append(uint32_t, 'num_syms')
sp_fdbg_info_t.append(uint32_t, 'num_arrays')

sp_fdbg_file_t = Structure()
sp_fdbg_file_t.packed = True
sp_fdbg_file_t.append(uint32_t, 'addr')
sp_fdbg_file_t.append(uint32_t, 'name')

sp_fdbg_line_t = Structure()
sp_fdbg_line_t.packed = True
sp_fdbg_line_t.append(uint32_t, 'addr')
sp_fdbg_line_t.append(uint32_t, 'name')

smx_rtti_enum = Structure()
smx_rtti_enum.packed = True
smx_rtti_enum.append(uint32_t, 'name')
smx_rtti_enum.append(uint32_t, 'reserved0')
smx_rtti_enum.append(uint32_t, 'reserved1')
smx_rtti_enum.append(uint32_t, 'reserved2')

smx_rtti_method = Structure()
smx_rtti_method.packed = True
smx_rtti_method.append(uint32_t, 'name')
smx_rtti_method.append(uint32_t, 'pcode_start')
smx_rtti_method.append(uint32_t, 'pcode_end')
smx_rtti_method.append(uint32_t, 'signature')

smx_rtti_native = Structure()
smx_rtti_native.packed = True
smx_rtti_native.append(uint32_t, 'name')
smx_rtti_native.append(uint32_t, 'signature')

smx_rtti_typedef = Structure()
smx_rtti_typedef.packed = True
smx_rtti_typedef.append(uint32_t, 'name')
smx_rtti_typedef.append(uint32_t, 'type_id')

smx_rtti_typeset = Structure()
smx_rtti_typeset.packed = True
smx_rtti_typeset.append(uint32_t, 'name')
smx_rtti_typeset.append(uint32_t, 'signature')

smx_rtti_enumstruct = Structure()
smx_rtti_enumstruct.packed = True
smx_rtti_enumstruct.append(uint32_t, 'name')
smx_rtti_enumstruct.append(uint32_t, 'first_field')
smx_rtti_enumstruct.append(uint32_t, 'size')

smx_rtti_es_field = Structure()
smx_rtti_es_field.packed = True
smx_rtti_es_field.append(uint32_t, 'name')
smx_rtti_es_field.append(uint32_t, 'type_id')
smx_rtti_es_field.append(uint32_t, 'offset')

smx_rtti_classdef = Structure()
smx_rtti_classdef.packed = True
smx_rtti_classdef.append(uint32_t, 'flags')
smx_rtti_classdef.append(uint32_t, 'name')
smx_rtti_classdef.append(uint32_t, 'first_field')
smx_rtti_classdef.append(uint32_t, 'reserved0')
smx_rtti_classdef.append(uint32_t, 'reserved1')
smx_rtti_classdef.append(uint32_t, 'reserved2')
smx_rtti_classdef.append(uint32_t, 'reserved3')

smx_rtti_field = Structure()
smx_rtti_field.packed = True
smx_rtti_field.append(uint16_t, 'flags')
smx_rtti_field.append(uint32_t, 'name')
smx_rtti_field.append(uint32_t, 'type_id')

smx_rtti_debug_method = Structure()
smx_rtti_debug_method.packed = True
smx_rtti_debug_method.append(uint16_t, 'method_index')
smx_rtti_debug_method.append(uint32_t, 'first_local')

smx_rtti_debug_var = Structure()
smx_rtti_debug_var.packed = True
smx_rtti_debug_var.append(int32_t, 'address')
smx_rtti_debug_var.append(uint8_t, 'vclass')
smx_rtti_debug_var.append(uint32_t, 'name')
smx_rtti_debug_var.append(uint32_t, 'code_start')
smx_rtti_debug_var.append(uint32_t, 'code_end')
smx_rtti_debug_var.append(uint32_t, 'type_id')