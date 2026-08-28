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
blt_id = 0
bullets={

}

mapa = []

pos_x_parede = []
pos_y_parede = []

paredes = {}

import random

import random

# Representação visual da tela (20 colunas x 15 linhas)
# 0 = Caminho livre | 1 = Parede
MAPA_1 = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,1,1,1,0,0,0,1,1,1,1,0,0,0,1,1,1,0,0],
    [0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0],
    [0,0,1,0,0,0,1,1,0,0,0,0,1,1,0,0,0,1,0,0],
    [0,0,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,1,1,0,0,0,0,0,1,1,0,0,0,0,0,1,1,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,0,0],
    [0,0,1,0,0,0,1,1,0,0,0,0,1,1,0,0,0,1,0,0],
    [0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0],
    [0,0,1,1,1,0,0,0,1,1,1,1,0,0,0,1,1,1,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
]

MAPA_2 = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,1,1,0,0,1,1,0,0,0,0,1,1,0,0,1,1,0,0],
    [0,0,1,1,0,0,1,1,0,0,0,0,1,1,0,0,1,1,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,1,1,0,0,0,0,1,1,1,1,0,0,0,0,1,1,0,0],
    [0,0,1,1,0,0,0,0,1,1,1,1,0,0,0,0,1,1,0,0],
    [0,0,1,1,0,0,0,0,1,1,1,1,0,0,0,0,1,1,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,1,1,0,0,1,1,0,0,0,0,1,1,0,0,1,1,0,0],
    [0,0,1,1,0,0,1,1,0,0,0,0,1,1,0,0,1,1,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
]

# Lista com todos os layouts pré-desenhados
TODOS_OS_MAPAS = [MAPA_1, MAPA_2]


def criar_mapa():
    global pos_x_parede, pos_y_parede, paredes, mapa

    TAMANHO_TILE = 40
    parede_id = 0

    pos_x_parede = []
    pos_y_parede = []
    paredes = {}
    mapa = []

    # Escolhe um mapa aleatoriamente da lista
    matriz_escolhida = random.choice(TODOS_OS_MAPAS)

    for y, linha in enumerate(matriz_escolhida):
        linha_mapa = []
        for x, parede in enumerate(linha):

            tile = {
                "parede": parede,
                "pos_x": x * TAMANHO_TILE,
                "pos_y": y * TAMANHO_TILE
            }

            if parede == 1:
                pos_x_parede.append(tile['pos_x'])
                pos_y_parede.append(tile['pos_y'])
                paredes[parede_id] = tile
                parede_id += 1

            linha_mapa.append(tile)

        mapa.append(linha_mapa)

    print("Mapa selecionado aleatoriamente e carregado!")


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
        colide = True
        while colide:
            pos_x = random.randint(0,800)
            pos_y = random.randint(0,600)
            for x in range(len(pos_x_parede)):
                if not checa_colisao(pos_x,pos_y,pos_x_parede[x],pos_y_parede[x]):
                    colide = False
        if number<25:
            with app.app_context():
                socketio.emit("spawn_pickup", {"pos_x":pos_x,"pos_y":pos_y})
            pickup = {
                "pos_x":pos_x,
                "pos_y":pos_y
            }
            print(f"Objeto Spawnado na posição ({pos_x},{pos_y})")
        socketio.sleep(10)


@socketio.on('connect')
def handle_connect():
    global plr
    print('Cliente conectado:', request.sid)

    if plr==0:
        jogadores[request.sid] = {
            'pos_x':0,
            'pos_y':0,
            'hp':20,
            'plr':plr,
            'pickup':0,
            'color':f"#{random.randint(0, 0xFFFFFF):06x}",
            'size':40,
            'mouse_x':0,
            'mouse_y':0,
            'alive':True
        }
    else:
        jogadores[request.sid] = {
            'pos_x':400,
            'pos_y':0,
            'hp':20,
            'plr':plr,
            'pickup':0,
            'color':f"#{random.randint(0, 0xFFFFFF):06x}",
            'size':40,
            'mouse_x':0,
            'mouse_y':0,
            'alive':True
        }
    plr = plr +1
    if(plr == 2):
        criar_mapa()
        emit('recebe_mapa', {"paredes":paredes}, broadcast=True)
    emit('spawn_bullets', {'bullets':bullets}, broadcast=True)
    emit('update_player_pos', {'sid': request.sid, 'jogadores': jogadores},broadcast=True)
    print(jogadores)

@socketio.on('disconnect')
def handle_disconnect():
    global plr
    print('Desconectou', request.sid)
    jogadores.pop(request.sid,None)
    plr = plr -1


@socketio.on('attack')
def handle_attack(data):

    global blt_id
    if jogadores[request.sid]['pickup'] == 1:
        bullets[blt_id] ={
            'pos_x': data['pos_x'],
            'pos_y': data['pos_y'],
            'vel_x': data['vel_x'],
            'vel_y': data['vel_y'],
            'dono_sid': request.sid,
            'angulo': data['angulo'],
            'alive':True,
        }
        
        emit('spawn_bullets', {'bullets':bullets}, broadcast=True)
        
        blt_id += 1
    
def balaAndando():
    while True:
        for id,bala in bullets.items():
            nova_pos_x = bala['pos_x'] + bala['vel_x']
            nova_pos_y = bala['pos_y'] + bala['vel_y']

            for x in range(len(pos_x_parede)):
                if checa_colisao(nova_pos_x,nova_pos_y,pos_x_parede[x],pos_y_parede[x]):
                    bullets[id]['alive'] = False


            if bullets[id]["alive"]:
                for sid,player in jogadores.items():
                    if checa_colisao(nova_pos_x, nova_pos_y, player['pos_x'], player['pos_y']) and bullets[id]['dono_sid'] != sid:

                        jogadores[sid]['hp'] -= 1

                        if jogadores[sid]['hp'] <= 0:
                            jogadores[sid]['alive'] = True
                            jogadores[sid]["pos_x"] = 0
                            jogadores[sid]["pos_y"] = 0
                        bullets[id]['alive'] = False
                        with app.app_context():
                            socketio.emit('update_player_pos', {'sid': sid, 'jogadores': jogadores})
                bala['pos_x'] += bala['vel_x']
                bala['pos_y'] += bala['vel_y']


        with app.app_context():
            socketio.emit("spawn_bullets", {"bullets":bullets})

        socketio.sleep(0.01667)



@socketio.on('send_mouse')
def update_player_mouse(data):
    jogadores[request.sid]['mouse_x'] = data['mouse_x']
    jogadores[request.sid]['mouse_y'] = data['mouse_y']

    emit('update_player_pos', {'sid': request.sid, 'jogadores': jogadores}, broadcast=True)


        


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

    for x in range(len(pos_x_parede)):
        if checa_colisao(jogador["pos_x"],nova_pos_y,pos_x_parede[x],pos_y_parede[x]):
            return
        


    if nova_pos_y>560 or nova_pos_y<0:
        return

    for sid,player in jogadores.items():
        if sid != request.sid and checa_colisao(jogador['pos_x'], nova_pos_y, player['pos_x'], player['pos_y']):
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

    for x in range(len(pos_x_parede)):
        if checa_colisao(jogador["pos_x"],nova_pos_y,pos_x_parede[x],pos_y_parede[x]):
            return

    
    if nova_pos_y>560 or nova_pos_y<0:
        return

    for sid,player in jogadores.items():
        if sid != request.sid and checa_colisao(jogador['pos_x'], nova_pos_y, player['pos_x'], player['pos_y']):
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

    for x in range(len(pos_x_parede)):
        if checa_colisao(nova_pos_x,jogador["pos_y"],pos_x_parede[x],pos_y_parede[x]):
            return

    if nova_pos_x > 760 or nova_pos_x < 0:
        return


    for sid,player in jogadores.items():
        if sid != request.sid and checa_colisao(nova_pos_x, jogador['pos_y'], player['pos_x'], player['pos_y']):
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

    for x in range(len(pos_x_parede)):
        if checa_colisao(nova_pos_x,jogador["pos_y"],pos_x_parede[x],pos_y_parede[x]):
            return

    if nova_pos_x > 760 or nova_pos_x < 0:
        return


    for sid,player in jogadores.items():
        if sid != request.sid and checa_colisao(nova_pos_x, jogador['pos_y'], player['pos_x'], player['pos_y']):
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
    socketio.start_background_task(balaAndando)
    socketio.run(app, host='0.0.0.0', port=5080, debug=True, log_output=False)
