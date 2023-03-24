
from flask import Flask, request, render_template
import json
import os, time
import re
import random

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
            # line = re.sub(r"[\n\r]", '', line)
            k = re.split(r"[:=]", line, maxsplit=1)[0].strip('\'\"')
            k = re.sub(r"^\s+\-?\s*", '', k)
            v = re.split(r"[:=]", line, maxsplit=1)[1].strip('\'\"')
            p[k] = v
            print(f"→{k}←   :   →{v}←")
        return p
    except:
        return {'error': 'parse failed by some reason'}

app.jinja_env.globals.update(version=version)

@app.route('/', methods=['GET', 'POST'])
def form():
    payload = {}
    raw = {}
    if request.method == 'POST':
        rq = dict(request.form)
        data = rq['input']
        raw = data
        parsed = parse(data)
        try:
            if rq['filetype'] != 'none':
                parsed['__type__'] = rq['filetype']
                print(rq['filename'])
                if len(rq['filename']) > 0:
                    parsed['__filename__'] = rq['filename']
                else:
                    parsed['__filename__'] = ''.join([random.choice('0123456789abcdefghikmnoprstuvwxy') for _ in range(16)]) \
                        + '.' + rq['filetype']
                if rq['filetype'] == 'file':
                    parsed['__filename__'] += '.b64encoded'
                if len(rq['filepath']) > 0:
                    parsed['__path__'] = rq['filepath']
        except:
            pass
        payload['JSON'] = json.dumps(parsed, indent=4)
        payload['KV'] = '\n'.join(['='.join([k, v]) for k, v in parsed.items()])
        payload['KVL'] = '\n'.join(['='.join([f"- {k}", v]) for k, v in parsed.items()])
        payload['QKV'] = '\n'.join([': '.join([f"'{k}'", f"'{v}'"]) for k, v in parsed.items()])
        payload['QKVL'] = '\n'.join([': '.join([f"- '{k}'", f"'{v}'"]) for k, v in parsed.items()])


        return render_template('index.html', payload=payload, raw=raw)
    return render_template('index.html', payload={'info': 'no payload'}, raw=raw)
 
if __name__=='__main__':
#    app.run()
    from waitress import serve
    serve(app, host="0.0.0.0", port=80)