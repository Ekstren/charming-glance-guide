import urllib.request, json, sys
url='https://api.github.com/repos/ekstren/charming-glance-guide/actions/runs?per_page=10'
with urllib.request.urlopen(url) as resp:
    data=resp.read()
    try:
        obj=json.loads(data)
        print(json.dumps(obj, indent=2))
    except Exception as e:
        print('Error parsing JSON', e, file=sys.stderr)
        sys.exit(1)
