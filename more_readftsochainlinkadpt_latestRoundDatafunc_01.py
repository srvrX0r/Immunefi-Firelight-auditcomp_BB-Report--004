ftso_lines = ftso.split('\n')
for i, line in enumerate(ftso_lines, 1):
    if 'latestRoundData' in line or 'getRoundData' in line or 'function ' in line:
        print(f"L{i:3d}: {line}")