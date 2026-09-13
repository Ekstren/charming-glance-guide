import pathlib, codecs
path = pathlib.Path(r'C:\Users\ekstren\Documents\Local AI Projects\GUI Projects\charming-glance-guide\update_script2.py')
content = path.read_text(encoding='utf-8', errors='strict')
for i, ch in enumerate(content):
    if ord(ch) > 127:
        print(i, ch, hex(ord(ch)))
print('done')
