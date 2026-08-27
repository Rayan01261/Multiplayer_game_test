from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

jogadores = {}
plr = 0


@app.route("/")
def index():
    return render_template("index.html")



def checa_colisao(pos_x_a, pos_y_a, pos_x_b, pos_y_b, size=40):
    sobrepoe_x = pos_x_a < pos_x_b + size and pos_x_a + size > pos_x_b
    sobrepoe_y = pos_y_a < pos_y_b + size and pos_y_a + size > pos_y_b
    return sobrepoe_x and sobrepoe_y


@socketio.on('connect')
def handle_connect():
    global plr
    print('Cliente conectado:', request.sid)
    jogadores[request.sid] = {
        'pos_x':0,
        'pos_y':0,
        'plr':plr,
    }
    plr = plr +1
    print(jogadores)

@socketio.on('disconnect')
def handle_disconnect():
    global plr
    print('Desconectou', request.sid)
    jogadores.pop(request.sid,None)
    plr = plr -1




@socketio.on('move_up')
def handle_move_up(data):
    jogador = jogadores.get(request.sid)

    if(jogador['pos_x'] == None or jogador['pos_y'] == None):
        jogador['pos_x'] = 0
        jogador['pos_y'] = 0
        emit('update_player_pos', {'sid': request.sid, 'jogador': jogador}, broadcast=True)
        return

    nova_pos_y = jogador['pos_y'] - data['speed']

    outro_sid = next((sid for sid in jogadores if sid != request.sid), None)
    outro = jogadores.get(outro_sid)

    if outro and checa_colisao(jogador['pos_x'], nova_pos_y, outro['pos_x'], outro['pos_y']):
        return

    jogador['pos_y'] = nova_pos_y
    emit('update_player_pos', {'sid': request.sid, 'jogador': jogador}, broadcast=True)


@socketio.on('move_down')
def handle_move_down(data):
    jogador = jogadores.get(request.sid)

    if(jogador['pos_x'] == None or jogador['pos_y'] == None):
        jogador['pos_x'] = 0
        jogador['pos_y'] = 0
        emit('update_player_pos', {'sid': request.sid, 'jogador': jogador}, broadcast=True)
        return

    nova_pos_y = jogador['pos_y'] + data['speed']

    outro_sid = next((sid for sid in jogadores if sid != request.sid), None)
    outro = jogadores.get(outro_sid)

    if outro and checa_colisao(jogador['pos_x'], nova_pos_y, outro['pos_x'], outro['pos_y']):
        return

    jogador['pos_y'] = nova_pos_y
    emit('update_player_pos', {'sid': request.sid, 'jogador': jogador}, broadcast=True)


@socketio.on('move_left')
def handle_move_left(data):
    jogador = jogadores.get(request.sid)

    if(jogador['pos_x'] == None or jogador['pos_y'] == None):
        jogador['pos_x'] = 0
        jogador['pos_y'] = 0
        emit('update_player_pos', {'sid': request.sid, 'jogador': jogador}, broadcast=True)
        return

    nova_pos_x = jogador['pos_x'] - data['speed']

    outro_sid = next((sid for sid in jogadores if sid != request.sid), None)
    outro = jogadores.get(outro_sid)

    if outro and checa_colisao(nova_pos_x, jogador['pos_y'], outro['pos_x'], outro['pos_y']):
        return

    jogador['pos_x'] = nova_pos_x
    emit('update_player_pos', {'sid': request.sid, 'jogador': jogador}, broadcast=True)


@socketio.on('move_right')
def handle_move_right(data):
    jogador = jogadores.get(request.sid)

    if(jogador['pos_x'] == None or jogador['pos_y'] == None):
        jogador['pos_x'] = 0
        jogador['pos_y'] = 0
        emit('update_player_pos', {'sid': request.sid, 'jogador': jogador}, broadcast=True)
        return

    nova_pos_x = jogador['pos_x'] + data['speed']

    outro_sid = next((sid for sid in jogadores if sid != request.sid), None)
    outro = jogadores.get(outro_sid)

    if outro and checa_colisao(nova_pos_x, jogador['pos_y'], outro['pos_x'], outro['pos_y']):
        return

    jogador['pos_x'] = nova_pos_x
    emit('update_player_pos', {'sid': request.sid, 'jogador': jogador}, broadcast=True)




if __name__ == "__main__":
    app.run(debug=True)
