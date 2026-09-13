import re, os, json, shutil

root = r'C:\Users\ekstren\temp\charming-glance-guide'

# 1. Minify CSS
css_path = os.path.join(root, 'assets', 'site.css')
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()
# remove comments and whitespace
css_min = re.sub(r'/\*[^*]*\*+(?:[^/*][^*]*\*+)*/', '', css)  # remove comments
css_min = re.sub(r'\s+', ' ', css_min)  # collapse whitespace
css_min = css_min.replace('} ', '}')
css_min_path = os.path.join(root, 'assets', 'site.min.css')
with open(css_min_path, 'w', encoding='utf-8') as f:
    f.write(css_min)
print('Minified CSS written to', css_min_path)

# 2. Create builds.json from builds.js
builds_js = os.path.join(root, 'assets', 'builds.js')
with open(builds_js, 'r', encoding='utf-8') as f:
    data = f.read()
# find array assigned to ROLE_PRESETS
m = re.search(r'const\s+ROLE_PRESETS\s*=\s*(\[.*?\]);', data, re.S)
if not m:
    print('Could not find ROLE_PRESETS array')
else:
    array_text = m.group(1)
    # evaluate array using json-like transformation
    try:
        # replace single quotes with double, remove trailing commas
        json_text = array_text.replace("'", '"')
        json_text = re.sub(r',\s*]', ']', json_text)
        builds = json.loads(json_text)
        builds_path = os.path.join(root, 'data', 'builds.json')
        with open(builds_path, 'w', encoding='utf-8') as f:
            json.dump(builds, f, indent=2)
        print('Extracted builds JSON to', builds_path)
    except Exception as e:
        print('Error parsing builds JSON:', e)

# 3. Move .mjs scripts to ci_scripts folder
ci_dir = os.path.join(root, 'ci_scripts')
os.makedirs(ci_dir, exist_ok=True)
script_dir = os.path.join(root, 'scripts')
for fname in os.listdir(script_dir):
    if fname.endswith('.mjs'):
        src = os.path.join(script_dir, fname)
        dst = os.path.join(ci_dir, fname)
        shutil.move(src, dst)
        print('Moved', fname, 'to ci_scripts')

print('Optimization script completed')
