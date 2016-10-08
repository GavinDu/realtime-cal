"""
 Using flask framework to handle the tiny real time app.
"""

import os
import json
import redis
from flask import Flask, render_template, request
from flask_socketio import SocketIO

app = Flask(__name__)
db = redis.from_url(os.environ.get("REDIS_URL"))
socketio = SocketIO(app)



###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')

"""
This function is to get all items from redis, when a new user connect
to the app. Then pour all the items into json object and push to client.
"""
@socketio.on('init', namespace='/insert')
def init_client_to_display_all_items():
    socketio.emit('msg', 
                  {'all_items': json.dumps({'data':[x.decode('utf-8') for x in db.lrange('results',0,-1)]})}, 
                  namespace='/insert')


@socketio.on('send_results', namespace='/insert')
def insert_db_and_push_to_client(message):
    # using eval is a dangerous behavoir, but a easy way.
    # we could implement calculation in client end by javascript,
    # or validate it in here.
    # Here, we assume that the expression from client is valid.

    result = message['result'] + '=' + str(eval(message['result']))
    result_size =  db.llen('results')
    
    # Here, we just keep 10 item in redis for reduing the data size.
    if result_size >= 10:
        db.rpop('results')
    db.lpush('results', result)
    socketio.emit('msg', 
                  {'all_items': json.dumps({'data':[x.decode('utf-8') for x in db.lrange('results',0,-1)]})}, 
                  namespace='/insert')



if __name__ == '__main__':
    socketio.run(app, debug=True)
    #app.run(debug=True)
