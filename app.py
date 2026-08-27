import logging
import random
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

# silencia o logger do werkzeug, deixando só erros aparecerem
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

jogadores = {}
pickup = {
    "pos_x":None,
    "pos_y":None,
}
plr = 0


@app.route("/")
def index():
    return render_template("index.html")



def checa_colisao(pos_x_a, pos_y_a, pos_x_b, pos_y_b, size=40):
    try:
        sobrepoe_x = pos_x_a < pos_x_b + size and pos_x_a + size > pos_x_b
        sobrepoe_y = pos_y_a < pos_y_b + size and pos_y_a + size > pos_y_b
    except:
        print("outro jogador não está em jogo")
        return
    return sobrepoe_x and sobrepoe_y

def checa_colisao_pickup(pos_x_a, pos_y_a, pos_x_b, pos_y_b, size=40, size_pickup=10):
    try:
        sobrepoe_x = pos_x_a < pos_x_b + size_pickup and pos_x_a + size > pos_x_b
        sobrepoe_y = pos_y_a < pos_y_b + size_pickup and pos_y_a + size > pos_y_b
    except:
        return
    return sobrepoe_x and sobrepoe_y


def spawn_pickup_chance():
    while True:
        global pickup
        number = 2
        pos_x = random.randint(0,800)
        pos_y = random.randint(0,600)
        if number<25:
            with app.app_context():
                socketio.emit("spawn_pickup", {"pos_x":pos_x,"pos_y":pos_y})
            pickup = {
                "pos_x":pos_x,
                "pos_y":pos_y
            }
            print(f"Objeto Spawnado na posição ({pos_x},{pos_y})")
        socketio.sleep(30)


@socketio.on('connect')
def handle_connect():
    global plr
    print('Cliente conectado:', request.sid)
    jogadores[request.sid] = {
        'pos_x':None,
        'pos_y':None,
        'plr':plr,
        'pickup':0,
        'color':f"#{random.randint(0, 0xFFFFFF):06x}",
        'size':40,
        'alive':True
    }
    plr = plr +1
    print(jogadores)

@socketio.on('disconnect')
def handle_disconnect():
    global plr
    print('Desconectou', request.sid)
    jogadores.pop(request.sid,None)
    plr = plr -1


@socketio.on('attack')
def handle_attack():
    bullet = {
        'size':10,
        'color':'#FF0000'
    }
    



@socketio.on('move_up')
def handle_move_up(data):
    global pickup
    jogador = jogadores.get(request.sid)

    if(jogador['pos_x'] == None or jogador['pos_y'] == None):
        jogadores.get(request.sid)['pos_x'] = 0
        jogadores.get(request.sid)['pos_y'] = 0
        emit('update_player_pos', {'sid': request.sid, 'jogadores': jogadores}, broadcast=True)
        return

    nova_pos_y = jogador['pos_y'] - data['speed']


    if nova_pos_y>560 or nova_pos_y<0:
        return

    for sid,player in jogadores.items():
        if sid != request.sid and checa_colisao(jogador['pos_x'], nova_pos_y, player['pos_x'], player['pos_y']):
            if jogador['pickup'] == 1:
                jogadores.get(sid)['alive'] = False
                emit('update_player_pos', {'sid': request.sid, 'jogadores': jogadores},broadcast=True)
            return



    if checa_colisao_pickup(jogador['pos_x'], nova_pos_y, pickup['pos_x'], pickup['pos_y']):
        emit('spawn_pickup', {"pos_x":None,"pos_y":None})
        pickup = {
            "pos_x":None,
            "pos_y":None,
            "size": 10,
            "color": "#ff69b4"
        }
        jogadores.get(request.sid)['pickup'] = 1
        emit('pickup_dispawn',{'pickup':pickup}, broadcast=True)
        emit('equip_weapon',{'sid':request.sid})
        print("Jogador pegou o objeto")

    jogadores.get(request.sid)['pos_y'] = nova_pos_y
    emit('update_player_pos', {'sid': request.sid, 'jogadores': jogadores}, broadcast=True)


@socketio.on('move_down')
def handle_move_down(data):
    jogador = jogadores.get(request.sid)

    global pickup

    if(jogador['pos_x'] == None or jogador['pos_y'] == None):
        jogadores.get(request.sid)['pos_x'] = 0
        jogadores.get(request.sid)['pos_y'] = 0
        emit('update_player_pos', {'sid': request.sid, 'jogadores': jogadores}, broadcast=True)
        return

    nova_pos_y = jogador['pos_y'] + data['speed']

    if nova_pos_y>560 or nova_pos_y<0:
        return

    for sid,player in jogadores.items():
        if sid != request.sid and checa_colisao(jogador['pos_x'], nova_pos_y, player['pos_x'], player['pos_y']):
            if jogador['pickup'] == 1:
                jogadores.get(sid)['alive'] = False
                emit('update_player_pos', {'sid': request.sid, 'jogadores': jogadores},broadcast=True)
            return



    if checa_colisao_pickup(jogador['pos_x'], nova_pos_y, pickup['pos_x'], pickup['pos_y']):
        emit('spawn_pickup', {"pos_x":None,"pos_y":None})
        pickup = {
            "pos_x":None,
            "pos_y":None,
            "size": 10,
            "color": "#ff69b4"
        }
        jogadores.get(request.sid)['pickup'] = 1
        print("Jogador pegou o objeto")

    jogadores.get(request.sid)['pos_y'] = nova_pos_y
    emit('update_player_pos', {'sid': request.sid, 'jogadores': jogadores}, broadcast=True)



@socketio.on('move_left')
def handle_move_left(data):
    jogador = jogadores.get(request.sid)

    global pickup

    if(jogador['pos_x'] == None or jogador['pos_y'] == None):
        jogadores.get(request.sid)['pos_x'] = 0
        jogadores.get(request.sid)['pos_y'] = 0
        emit('update_player_pos', {'sid': request.sid, 'jogadores': jogadores}, broadcast=True)
        return

    nova_pos_x = jogador['pos_x'] - data['speed']

    if nova_pos_x > 760 or nova_pos_x < 0:
        return

    for sid,player in jogadores.items():
        if sid != request.sid and checa_colisao(nova_pos_x, jogador['pos_y'], player['pos_x'], player['pos_y']):
            if jogador['pickup'] == 1:
                jogadores.get(sid)['alive'] = False
                emit('update_player_pos', {'sid': request.sid, 'jogadores': jogadores},broadcast=True)
            return


    if checa_colisao_pickup(nova_pos_x,jogador['pos_y'],pickup["pos_x"],pickup['pos_y']):
            emit('spawn_pickup', {"pos_x":None,"pos_y":None})
            pickup = {
                "pos_x":None,
                "pos_y":None,
                "size": 10,
                "color": "#ff69b4"
            }
            jogadores.get(request.sid)['pickup'] = 1
            print("Jogador pegou o objeto")

    jogadores.get(request.sid)['pos_x'] = nova_pos_x
    emit('update_player_pos', {'sid': request.sid, 'jogadores': jogadores}, broadcast=True)


@socketio.on('move_right')
def handle_move_right(data):
    jogador = jogadores.get(request.sid)

    global pickup

    if(jogador['pos_x'] == None or jogador['pos_y'] == None):
        jogador['pos_x'] = 0
        jogador['pos_y'] = 0
        emit('update_player_pos', {'sid': request.sid, 'jogadores': jogadores}, broadcast=True)
        return

    nova_pos_x = jogador['pos_x'] + data['speed']

    if nova_pos_x > 760 or nova_pos_x < 0:
        return

    for sid,player in jogadores.items():
        if sid != request.sid and checa_colisao(nova_pos_x, jogador['pos_y'], player['pos_x'], player['pos_y']):
            if jogador['pickup'] == 1:
                jogadores.get(sid)['alive'] = False
                emit('update_player_pos', {'sid': request.sid, 'jogadores': jogadores},broadcast=True)
            return


    if checa_colisao_pickup(nova_pos_x,jogador['pos_y'],pickup["pos_x"],pickup['pos_y']):
            emit('spawn_pickup', {"pos_x":None,"pos_y":None})
            pickup = {
                "pos_x":None,
                "pos_y":None,
                "size": 10,
                "color": "#ff69b4"
            }
            jogadores.get(request.sid)['pickup'] = 1
            print("Jogador pegou o objeto")

    jogadores.get(request.sid)['pos_x'] = nova_pos_x
    emit('update_player_pos', {'sid': request.sid, 'jogadores': jogadores}, broadcast=True)




if __name__ == "__main__":
    socketio.start_background_task(spawn_pickup_chance)
    socketio.run(app, host='0.0.0.0', port=5080, debug=True, log_output=False)
