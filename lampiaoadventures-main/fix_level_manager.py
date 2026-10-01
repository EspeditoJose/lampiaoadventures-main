import re

# Read the file
with open('src/level/level_manager.py', 'r') as f:
    content = f.read()

# Fix the LEVEL_1_CHARMAP indentation
content = re.sub(r'(\s{4})(# Row \d+)', r'\1\2', content)
content = re.sub(r'(\s{8})(\'\.\*\d+\.)', r'\1\2', content)

# Fix the class definition indentation - we need to fix the major structural issues
lines = content.split('\n')
fixed_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Skip the problematic lines
    if 'class LevelManager:' in line and i > 50 and i < 80:
        # Skip to the proper class definition at the end
        i += 1
        continue
    
    # Fix indentation for lines that should be at class level
    if line.startswith('    def ') and i > 100 and i < 200:
        # These are indented too much
        line = line[4:]
    
    fixed_lines.append(line)
    i += 1

content = '\n'.join(fixed_lines)

# Write back
with open('src/level/level_manager.py', 'w') as f:
    f.write(content)

print('Fixed level_manager.py structure')
