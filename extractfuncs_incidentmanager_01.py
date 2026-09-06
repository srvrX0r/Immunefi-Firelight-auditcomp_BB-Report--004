funcs = re.findall(r'function\s+(\w+)', incident_manager)
print("Functions in IncidentManager:")
for f in funcs:
    print(f"    {f}")