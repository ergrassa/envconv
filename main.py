
from flask import Flask, request, render_template
import json
import os, time
import re

def version():
    version = 'None'
    message = ''
    (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat('./version')
    with open('./version', 'r') as f:
        version = f"{str(f.read())} of {time.ctime(mtime)}"
    return version

app = Flask(__name__,
            static_url_path='', static_folder='static')


def parse(data:str):
    try:
        p = json.loads(data)
        return p
    except:
        pass
    try:
        p = {}
        for line in iter(data.splitlines()):
            if re.match(r"^\s*$", line):
                print('empty line')
                continue
            if re.match(r"^\s*#.*", line):
                print('comment line')
                continue
            line = re.sub(r"\s", '', line).strip().strip('-')
            k = re.split(r"[:=]", line)[0].strip('\'\"')
            v = re.split(r"[:=]", line)[1].strip('\'\"')
            p[k] = v  
        return p
    except:
        return {'error': 'parse failed by some reason'}

app.jinja_env.globals.update(version=version)

@app.route('/', methods=['GET', 'POST'])
def form():
    payload = {}
    raw = {}
    if request.method == 'POST':
        data = dict(request.form)['input']
        raw = data
        parsed = parse(data)
        payload['JSON'] = json.dumps(parsed, indent=4)
        payload['KV'] = '\n'.join(['='.join([k, v]) for k, v in parsed.items()])
        payload['KVL'] = '\n'.join(['='.join([f"- {k}", v]) for k, v in parsed.items()])
        payload['QKV'] = '\n'.join([': '.join([f"'{k}'", f"'{v}'"]) for k, v in parsed.items()])
        payload['QKVL'] = '\n'.join([': '.join([f"- '{k}'", f"'{v}'"]) for k, v in parsed.items()])


        return render_template('index.html', payload=payload, raw=raw)
    return render_template('index.html', payload='not payload', raw=raw)
 
if __name__=='__main__':
#    app.run()
    from waitress import serve
    serve(app, host="0.0.0.0", port=80)