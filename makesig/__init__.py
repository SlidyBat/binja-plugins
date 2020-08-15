from binaryninja import *

def decode_sig(sig):
    return sig.decode('unicode_escape')

def encode_sig(sig):
    t = ''
    for b in sig:
        t += '\\x%02X' % ord(b)
    return t

def get_function_end(func):
    end = func.start
    for bb in func:
        if bb.end > end:
            end = bb.end
    return end

def find_sig(bv, sig, max_results=1):
    br = BinaryReader(bv)
    results = []
    
    # Store non-wildcarded start of signature
    sig_start = ''
    for c in sig:
        if c == '*': break
        sig_start += c
    
    curr_search = bv.start
    while True:
        curr_search = bv.find_next_data(curr_search + 1, sig_start, FindFlag.FindCaseSensitive)
        if curr_search == None:
            break
        br.offset = curr_search
        
        for i in range(len(sig)):
            byte = br.read8()
            if byte == None:
                break
            if sig[i] != '*' and ord(sig[i]) != byte:
                break
        else:
            results += [curr_search]
            if len(results) >= max_results:
                return results
        
        if byte == None:
            break
        
    return results

def is_good_sig(bv, sig):
    if len(sig) < 5:
        return False
    addrs = find_sig(bv, sig, max_results=2)
    return len(addrs) == 1

def find_sig_from_input(bv):
    sig = interaction.get_text_line_input('Signature:', 'Enter signature to search for...')
    addrs = find_sig(bv, decode_sig(sig.strip()), max_results=100)
    if len(addrs) == 0:
        print('No matches found for signature')
    else:
        print('Found match at 0x%x' % addrs[0])

def sig_for_function(bv, func):
    func_start = func.start
    func_end = get_function_end(func)
    
    sig = ''
    br = BinaryReader(bv)
    br.seek(func_start)
    while br.offset < func_end:
        curr_instr = br.offset
        instr_len = bv.get_instruction_length(curr_instr)
        
        for i in range(instr_len):
            relocations = bv.relocation_ranges_at(br.offset)
            # Wildcard bytes that will be relocated
            if len(relocations) == 0:
                sig += chr(br.read8())
            else:
                sig += '*'
        
        if is_good_sig(bv, sig):
            print(encode_sig(sig))
            return
        
        br.offset = curr_instr + instr_len
    print('Function too short to generate unique signature')

PluginCommand.register("Find signature", "Searches the current binary for the given signature", find_sig_from_input)
PluginCommand.register_for_function("Make signature for current function", "Generates a unique signature for the current selected function", sig_for_function)