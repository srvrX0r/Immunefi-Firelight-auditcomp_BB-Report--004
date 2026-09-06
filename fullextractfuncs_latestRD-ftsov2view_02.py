import re

def extract_function_full(code, func_name):
    pattern = rf'function\s+{func_name}\s*\([^)]*\)[^{{]*\{{'
    match = re.search(pattern, code)
    if not match:
        return None
    start = match.start()
    brace_count = 0
    in_string = False
    string_char = None
    i = start
    while i < len(code):
        c = code[i]
        if not in_string:
            if c in '"\'':
                in_string = True
                string_char = c
            elif c == '{':
                brace_count += 1
            elif c == '}':
                brace_count -= 1
                if brace_count == 0:
                    return code[start:i+1]
        else:
            if c == string_char and code[i-1] != '\\':
                in_string = False
                string_char = None
        i += 1
    return code[start:]

REPO = "/tmp/audit-comp-firelight-1_audit_ready"

def read_file(path):
    with open(path, 'r') as f:
        return f.read()

ftso = read_file(f"{REPO}/contracts/oracle/FtsoChainlinkAdapter.sol")
incident_manager = read_file(f"{REPO}/contracts/core/IncidentManager.sol")

latest_round = extract_function_full(ftso, 'latestRoundData')
print("=== latestRoundData ===")
print(latest_round)
print("\n" + "="*80 + "\n")

ftso_view = extract_function_full(ftso, '_ftsoV2View')
print("=== _ftsoV2View ===")
print(ftso_view)
