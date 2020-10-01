from binaryninja import *

def read_ptr(bv, br):
    if bv.address_size == 4: return br.read32()
    if bv.address_size == 8: return br.read64()
    raise NotImplementedError()

# From https://github.com/0x1F9F1/binja-msvc/blob/master/rtti.py
def demangle_vtable_name(bv, name):
    try:
        if name[:4] in [ '.?AU', '.?AV' ]:
            # demangle_ms doesn't support flags (UNDNAME_32_BIT_DECODE | UNDNAME_NAME_ONLY | UNDNAME_NO_ARGUMENTS | UNDNAME_NO_MS_KEYWORDS)
            demangle_type, demangle_name = demangle.demangle_ms(bv.arch, '??_6%s6B@' % name[4:])

            if demangle_type is not None:
                return demangle.get_qualified_name(demangle_name)
    except:
        pass
    
    return 'vtable_{0}'.format(name)

def get_class_name(bv, name):
    try:
        if name[:4] in [ '.?AU', '.?AV' ]:
            # demangle_ms doesn't support flags (UNDNAME_32_BIT_DECODE | UNDNAME_NAME_ONLY | UNDNAME_NO_ARGUMENTS | UNDNAME_NO_MS_KEYWORDS)
            demangle_type, demangle_name = demangle.demangle_ms(bv.arch, '??_6%s6B@' % name[4:])

            if demangle_type is not None:
                return demangle_name[0]
    except:
        pass
    
    return name

def is_vtable_func(bv, addr):
    segment = bv.get_segment_at(addr)
    return segment and segment.executable

def is_complete_object_locator(bv, addr):
    rdata = bv.sections['.rdata']
    if rdata.start < addr and addr < rdata.end:
        br = BinaryReader(bv)
        br.seek(addr)
        signature = br.read32()
        return signature == 0
    return False

def vtable_t(bv, count):
    return Type.array(Type.pointer(bv.arch, Type.void()), count)

def type_descriptor_t(bv, str_size):
    type_descriptor_struct = Structure()
    type_descriptor_struct.append(Type.pointer(bv.arch, Type.void()), 'vtable')
    type_descriptor_struct.append(Type.pointer(bv.arch, Type.void()), 'runtime_ref')
    type_descriptor_struct.append(Type.array(Type.int(1), str_size), 'name')
    return Type.structure_type(type_descriptor_struct)

def base_class_desc_t(bv):
    base_class_desc_struct = Structure()
    base_class_desc_struct.append(Type.pointer(bv.arch, Type.void()), 'pTypeDescriptor')
    base_class_desc_struct.append(Type.int(4, False), 'numContainedBases')
    base_class_desc_struct.append(Type.int(4), 'mdisp')
    base_class_desc_struct.append(Type.int(4), 'pdisp')
    base_class_desc_struct.append(Type.int(4), 'vdisp')
    base_class_desc_struct.append(Type.int(4, False), 'attributes')
    return Type.structure_type(base_class_desc_struct)

def class_hierarchy_desc_t(bv):
    class_hierarchy_desc_struct = Structure()
    class_hierarchy_desc_struct.append(Type.int(4, False), 'signature')
    class_hierarchy_desc_struct.append(Type.int(4, False), 'attributes')
    class_hierarchy_desc_struct.append(Type.int(4, False), 'numBaseClasses')
    class_hierarchy_desc_struct.append(Type.pointer(bv.arch, base_class_desc_t(bv)), 'pBaseClassArray')
    return Type.structure_type(class_hierarchy_desc_struct)

def complete_object_locator_t(bv):
    complete_object_locator_struct = Structure()
    complete_object_locator_struct.append(Type.int(4, False), 'signature')
    complete_object_locator_struct.append(Type.int(4, False), 'offset')
    complete_object_locator_struct.append(Type.int(4, False), 'cdOffset')
    complete_object_locator_struct.append(Type.pointer(bv.arch, Type.void()), 'pTypeDescriptor')
    complete_object_locator_struct.append(Type.pointer(bv.arch, class_hierarchy_desc_t(bv)), 'pClassDescriptor')
    return Type.structure_type(complete_object_locator_struct)

def find_rtti(bv):
    rdata = bv.sections['.rdata']
    br = BinaryReader(bv)
    br.seek(rdata.start)
    vtable_count = 0
    while br.offset < rdata.end:
        p_col = br.offset
        col = read_ptr(bv, br)
        if col == None:
            break
            
        p_vtable = br.offset
        vtable_func = read_ptr(bv, br)
        if vtable_func == None:
            break
            
        if is_complete_object_locator(bv, col) and is_vtable_func(bv, vtable_func):
            vtable_count += 1
            # Define complete object locator
            bv.define_data_var(p_col, Type.pointer(bv.arch, complete_object_locator_t(bv)))
            bv.define_data_var(col, complete_object_locator_t(bv))
            
            # Define type descriptor
            br.seek(col + 0xC)
            typedesc = read_ptr(bv, br)
            mangled_name = bv.get_string_at(typedesc + 8)
            vtable_name = demangle_vtable_name(bv, mangled_name.value)
            class_name = get_class_name(bv, mangled_name.value)
            bv.define_data_var(typedesc, type_descriptor_t(bv, mangled_name.length))
            typedesc_name = '%s::`RTTI Type Descriptor\'' % class_name
            bv.define_user_symbol(Symbol(SymbolType.DataSymbol, typedesc, typedesc_name, raw_name='%s_%i' % (typedesc_name, vtable_count)))
            print('[%i] vtable at : 0x%0x (%s)' % (vtable_count, p_vtable, vtable_name))
            
            # Now that we have the class name, rename complete object locator to something more suitable
            p_col_name = 'locator_%s' % class_name
            bv.define_user_symbol(Symbol(SymbolType.DataSymbol, p_col, p_col_name, raw_name='%s_%i' % (p_col_name, vtable_count)))
            col_name = '%s::`RTTI Complete Object Locator\'' % class_name
            bv.define_user_symbol(Symbol(SymbolType.DataSymbol, col, col_name, raw_name='%s_%i' % (col_name, vtable_count)))
            
            # Define class hierarchy desc
            br.seek(col + 0x10)
            classhier = read_ptr(bv, br)
            bv.define_data_var(classhier, class_hierarchy_desc_t(bv))
            hierdesc_name = '%s::`RTTI Class Hierarchy Descriptor\'' % class_name
            bv.define_user_symbol(Symbol(SymbolType.DataSymbol, classhier, hierdesc_name, raw_name='%s_%i' % (hierdesc_name, vtable_count)))
            
            # Define base class array
            br.seek(classhier + 8)
            num_baseclasses = br.read32()
            baseclasses = read_ptr(bv, br)
            bv.define_data_var(baseclasses, Type.array(Type.pointer(bv.arch, base_class_desc_t(bv)), num_baseclasses))
            baseclasses_name = '%s::`RTTI Base Class Array\'' % class_name
            bv.define_user_symbol(Symbol(SymbolType.DataSymbol, baseclasses, baseclasses_name, raw_name='%s_%i' % (baseclasses_name, vtable_count)))
            
            # Count number of functions in vtable and mark as array
            br.seek(p_vtable)
            vfunc_count = 0
            while True:
                vtable_func = read_ptr(bv, br)
                if not is_vtable_func(bv, vtable_func):
                    break
                vfunc_count += 1
                bv.add_function(vtable_func)
            bv.define_data_var(p_vtable, vtable_t(bv, vfunc_count))
            bv.define_user_symbol(Symbol(SymbolType.DataSymbol, p_vtable, vtable_name, raw_name='%s_%i' % (vtable_name, vtable_count)))
        
        # The last vtable func check failed, back up in case this is a locator
        br.offset -= 4
    
    print('Found %i vtables' % vtable_count)\

class ScanRtti(BackgroundTaskThread):
    def __init__(self, msg, bv):
        BackgroundTaskThread.__init__(self, msg, True)
        self.bv = bv

    def run(self):
        find_rtti(self.bv)

def command_scan_rtti(bv):
    task = ScanRtti('Scanning RTTI', bv)
    task.start()

PluginCommand.register('Scan RTTI', 'Scans for MSVC RTTI', command_scan_rtti)