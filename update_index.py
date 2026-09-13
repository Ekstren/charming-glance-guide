import re, sys
path = r'C:\Users\ekstren\Documents\Local AI Projects\GUI Projects\charming-glance-guide\index.html'
with open(path,'r',encoding='utf-8') as f:
    content=f.read()
# replace runtime.min.js with runtime.js
content=re.sub(r'<script src="assets/runtime.min.js"><\/script>', '<script src="assets/runtime.js"></script>', content)
# replace companions.min.js with companions.js
content=re.sub(r'<script src="assets/companions.min.js"><\/script>', '<script src="assets/companions.js"></script>', content)
# replace builds.min.js with builds.js
content=re.sub(r'<script src="assets/builds.min.js"><\/script>', '<script src="assets/builds.js"></script>', content)
with open(path,'w',encoding='utf-8') as f:
    f.write(content)
print('Updated')
