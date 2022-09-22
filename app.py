from flask import Flask
from flask import request
app = Flask(__name__)

from time import sleep
import talomotor as tm


@app.route("/")
async def root():
    return {"message": "Hello World"}

@app.route('/play_chapu/')
def play_chapu():
    name = request.args['name']
    print('Playing ' + name)
    if name == 'kchapu':
        tm.play_custom('P5')
    elif name == 'mchapu':
        tm.play_custom('P7')
    elif name == 'schapu':
        tm.play_custom('P9')
    else:
        return {'status': 'error', 'msg': 'Unknown chapu thala'}
    return {'status': 'success'}

@app.route('/play_thalam/')
def play_thalam():
    name = request.args['name']
    jathi = int(request.args.get('jathi', 4))
    nadai = int(request.args.get('nadai', 4))
    kalai = int(request.args.get('kalai', 1))
    speed = request.args.get('speed', 'medium')

    sfactor = {'low': 1.25, 'medium': 1, 'high': 0.75}
    print('Playing thalam: {name}, jathi: {jathi}, nadai: {nadai}, kalai: {kalai}, speed: {speed}'.format(**request.args))
    tm.play_thalam(name, jathi=jathi, nadai=nadai, kalai=kalai, speed=sfactor.get(speed, 1))
    return {'status': 'success'}

@app.route('/play_custom/')
def play_custom():
    pattern = request.args['pattern']
    print('Playing custom: ' + pattern)
    tm.play_custom(pattern)
    return {'status': 'success'}