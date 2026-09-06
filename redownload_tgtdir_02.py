import os, subprocess

#re-dl
os.system('cd /tmp && curl -sL -o firelight.zip "https://github.com/immunefi-team/audit-comp-firelight/archive/refs/heads/v1_audit_ready.zip" 2>&1 | tail -5')
os.system('cd /tmp && unzip -q -o firelight.zip 2>&1 | tail -5')

# Find the extracted directory
for item in os.listdir('/tmp'):
    if item.startswith('audit-comp-firelight'):
        REPO = f"/tmp/{item}"
        print(f"Found repo at: {REPO}")
        break

# List root contents
print("\nRoot files:")
for f in sorted(os.listdir(REPO)):
    print(f"  {f}")