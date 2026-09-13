"""Safe CSS minification: remove comments, collapse whitespace.
Conservative approach - only removes whitespace and comments, no structural changes."""
import re, os, sys

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
css_path = os.path.join(base, 'assets', 'site.css')

with open(css_path, 'r', encoding='utf-8') as f:
    original = f.read()

original_size = len(original)
original_lines = original.count('\n') + 1

# Step 1: Remove CSS comments, preserving strings
def remove_comments(css):
    result = []
    i = 0
    n = len(css)
    in_string = False
    string_char = None
    while i < n:
        c = css[i]
        if in_string:
            result.append(c)
            if c == '\\' and i + 1 < n:
                result.append(css[i+1])
                i += 2
                continue
            if c == string_char:
                in_string = False
            i += 1
        elif c in ('"', "'"):
            in_string = True
            string_char = c
            result.append(c)
            i += 1
        elif c == '/' and i + 1 < n and css[i+1] == '*':
            end = css.find('*/', i + 2)
            if end == -1:
                i = n
            else:
                i = end + 2
        else:
            result.append(c)
            i += 1
    return ''.join(result)

no_comments = remove_comments(original)

# Step 2: Collapse whitespace, preserving strings
def collapse_whitespace(css):
    result = []
    i = 0
    n = len(css)
    in_string = False
    string_char = None
    while i < n:
        c = css[i]
        if in_string:
            result.append(c)
            if c == '\\' and i + 1 < n:
                result.append(css[i+1])
                i += 2
                continue
            if c == string_char:
                in_string = False
            i += 1
        elif c in ('"', "'"):
            in_string = True
            string_char = c
            result.append(c)
            i += 1
        elif c in ' \t\n\r\f':
            # Collapse run of whitespace to single space
            while i < n and css[i] in ' \t\n\r\f':
                i += 1
            # Add single space if both neighbors are "word" chars
            prev = result[-1] if result else ''
            nxt = css[i] if i < n else ''
            if prev and nxt and prev not in '{}:;,()' and nxt not in '{}:;,()':
                result.append(' ')
        else:
            result.append(c)
            i += 1
    return ''.join(result)

minified = collapse_whitespace(no_comments)

# Step 3: Remove spaces before structural chars (safe)
minified = re.sub(r'\s+([{};:,>])', r'\1', minified)
# Step 4: Remove spaces after { (safe)
minified = re.sub(r'\{\s+', '{', minified)
# Step 5: Remove trailing semicolons before } (safe)
minified = re.sub(r';\}', '}', minified)
# Step 6: Remove empty rule blocks
minified = re.sub(r'[^{}@]+\{\s*\}', '', minified)
# Step 7: Remove duplicate semicolons
minified = re.sub(r';{2,}', ';', minified)
# Step 8: Strip leading/trailing whitespace
minified = minified.strip()

minified_size = len(minified)
minified_lines = minified.count('\n') + 1
savings = original_size - minified_size
savings_pct = (savings / original_size) * 100

print(f'Original:  {original_size/1024:.1f} KB, {original_lines} lines')
print(f'Minified:  {minified_size/1024:.1f} KB, {minified_lines} lines')
print(f'Savings:   {savings/1024:.1f} KB ({savings_pct:.1f}%)')

# Validate brace balance
open_b = minified.count('{')
close_b = minified.count('}')
print(f'Braces:    {open_b} open, {close_b} close, {"OK" if open_b == close_b else "MISMATCH!"}')

# Validate: no unterminated strings
in_str = False
str_char = None
for i, c in enumerate(minified):
    if in_str:
        if c == '\\':
            continue
        if c == str_char:
            in_str = False
    elif c in ('"', "'"):
        in_str = True
        str_char = c
if in_str:
    print('WARNING: unterminated string detected!')
else:
    print('Strings:   all terminated OK')

# Write
with open(css_path, 'w', encoding='utf-8') as f:
    f.write(minified)
print(f'\nWrote {css_path}')
