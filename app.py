import logging
import random
import math
from math import sqrt, atan2
import time
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

# silencia o logger do werkzeug, deixando só erros aparecerem
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

jogadores = {}

pickups = []
pickup = {
    "pos_x":None,
    "pos_y":None,
    "tipo":None,
}
pickups.append(pickup)
blt_id = 0
swg_id = 0
bullets={

}

kamehamehas_ativos = {}
kmh_id = 0
KAMEHAMEHA_DURATION_S = 5

swing = {

}

mapa = []
end_game = False
game_start = False
pos_x_parede = []
pos_y_parede = []

paredes = {}

import random

import random

# Representação visual da tela (32 colunas x 18 linhas)
# 0 = Caminho livre | 1 = Parede
MAPA_1 = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0],
    [0,0,1,0,0,1,0,0,0,1,1,0,0,0,0,0,0,0,0,0,1,1,0,0,0,1,0,0,1,1,0,0],
    [0,0,1,0,0,1,0,0,0,1,1,0,0,0,0,0,0,0,0,0,1,1,0,0,0,1,0,0,1,1,0,0],
    [0,0,1,1,1,1,0,0,0,0,0,0,0,0,1,1,0,0,1,1,0,0,0,0,0,1,1,1,1,1,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0],
    [0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,1,1,0,0,0,0,0,0,0,0,0,0,1,1,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0],
    [0,0,1,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,1,1,0,0,0,0],
    [0,0,1,1,1,1,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,1,1,1,1,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
]

MAPA_2 = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,1,1,1,1,0,0,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,1,1,1,1,0,0,0,0],
    [0,0,1,0,0,1,0,0,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,1,0,0,1,0,0,0,0],
    [0,0,1,0,0,1,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,1,0,1,0,0,0,0],
    [0,0,1,1,1,1,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,1,1,1,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,1,1,0,0,0,0,0,0,0,0,1,1,0,0,1,1,0,0,0,0,1,1,0,0,0,0,0,0],
    [0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,1,1,0,0,1,1,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0],
    [0,0,0,0,1,1,0,0,0,0,0,0,0,0,1,1,0,0,1,1,0,0,0,0,1,1,0,0,0,0,0,0],
    [0,0,0,0,1,1,0,0,0,0,0,0,0,0,1,1,0,0,1,1,0,0,0,0,1,1,0,0,0,0,0,0],
    [0,0,1,1,1,1,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,1,1,1,0,0,0,0],
    [0,0,1,0,0,1,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,1,0,1,0,0,0,0],
    [0,0,1,0,0,1,0,0,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,1,0,0,1,0,0,0,0],
    [0,0,1,1,1,1,0,0,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,1,1,1,1,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
]

MAPA_3 = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0],
    [0,0,1,1,0,0,1,0,1,0,0,0,1,1,0,0,0,0,1,1,0,1,0,0,1,1,0,0,0,0,0,0],
    [0,0,1,1,0,0,1,0,1,0,0,0,1,1,0,0,0,0,1,1,0,1,0,0,1,1,0,0,0,0,0,0],
    [0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,1,1,0,0,0,0,0,0,1,1,1,1,0,0,1,1,1,1,0,0,1,1,0,0,0,0,0,0],
    [0,0,0,0,1,1,0,0,0,0,0,0,1,0,0,1,0,0,1,0,0,1,0,0,1,1,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0,0,1,0,0,1,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,1,1,0,0,0,0,0,0,1,1,1,1,0,0,1,1,1,1,0,0,1,1,0,0,0,0,0,0],
    [0,0,0,0,1,1,0,0,0,0,0,0,0,0,1,1,0,0,1,1,0,0,0,0,1,1,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,1,1,0,0,1,0,1,0,0,0,1,1,0,0,0,0,1,1,0,0,1,0,1,1,0,0,0,0,0,0],
    [0,0,1,1,0,0,1,0,1,0,0,0,1,1,0,0,0,0,1,1,0,0,1,0,1,1,0,0,0,0,0,0],
    [0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
]


# Lista com todos os layouts pré-desenhados
TODOS_OS_MAPAS = [MAPA_1, MAPA_2]
killed_players = []

MELEE_RANGE = 75           
LARGURA_DO_ARCO = math.radians(180)

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





def checa_colisao(pos_x_a, pos_y_a, pos_x_b, pos_y_b, size_a=40, size_b=40):
    try:
        sobrepoe_x = pos_x_a < pos_x_b + size_b and pos_x_a + size_a > pos_x_b
        sobrepoe_y = pos_y_a < pos_y_b + size_b and pos_y_a + size_a > pos_y_b
    except:
        return
    return sobrepoe_x and sobrepoe_y


def checa_colisao_melee(pos_x_a, pos_y_a, size_a, angulo_golpe,
                         pos_x_b, pos_y_b, size_b):


    centro_x_a = pos_x_a + size_a / 2
    centro_y_a = pos_y_a + size_a / 2
    centro_x_b = pos_x_b + size_b / 2
    centro_y_b = pos_y_b + size_b / 2

    dx = centro_x_b - centro_x_a
    dy = centro_y_b - centro_y_a


    distancia_alvo = math.sqrt(dx**2 + dy**2)
    alcance = (size_a / 2) + MELEE_RANGE + (size_b / 2)

    if distancia_alvo > alcance:
        return False


    angulo_para_alvo = math.atan2(dy, dx)
    diferenca = angulo_para_alvo - angulo_golpe


    diferenca = (diferenca + math.pi) % (2 * math.pi) - math.pi

    dentro_do_arco = abs(diferenca) <= (LARGURA_DO_ARCO / 2)

    return dentro_do_arco



def checa_colisao_kamehameha(pos_x_a, pos_y_a, size_a, angulo_golpe,
                         pos_x_b, pos_y_b, size_b):

    centro_x_a = pos_x_a + size_a / 2
    centro_y_a = pos_y_a + size_a / 2
    centro_x_b = pos_x_b + size_b / 2
    centro_y_b = pos_y_b + size_b / 2

    dx = centro_x_b - centro_x_a
    dy = centro_y_b - centro_y_a


    cos_a = math.cos(-angulo_golpe)
    sin_a = math.sin(-angulo_golpe)
    frente = dx * cos_a - dy * sin_a
    lado = dx * sin_a + dy * cos_a

    # Retângulo do golpe: começa na borda do atacante e vai até MELEE_RANGE,
    # com metade da largura pra cada lado
    inicio = size_a / 2
    fim = size_a / 2 + 9999
    metade_largura = 120 / 2  # substitui o LARGURA_DO_ARCO

    raio_alvo = size_b / 2

    dentro_frente = (inicio - raio_alvo) <= frente <= (fim + raio_alvo)
    dentro_lado = abs(lado) <= (metade_largura + raio_alvo)

    return dentro_frente and dentro_lado


def checa_win_condition():
    global end_game
    while True: 
        for id, player in jogadores.items():
            if player['kills'] >= 20:
                end_game = True
                socketio.emit('end_game')
        
        socketio.sleep(0.01667)


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
        colide = True
        
        if(len(pos_x_parede)>0):
            while colide:
                colide_aux = False
                pos_x = random.randint(0,1270)
                pos_y = random.randint(0,710)
                tipo = random.randint(2,5)
                for x in range(len(pos_x_parede)):
                    if checa_colisao(pos_x,pos_y,pos_x_parede[x],pos_y_parede[x],10,40):
                        colide_aux = True
                if not colide_aux:
                    colide = False 
                    colide_aux = True
                    

            with app.app_context():
                socketio.emit("spawn_pickup", {"pickups":pickups})


            pickup = {
                "pos_x":pos_x,
                "pos_y":pos_y,
                "tipo":tipo
            }
            pickups.append(pickup)
            print(f"Objeto Spawnado {tipo} na posição ({pos_x},{pos_y})")
        
        if(len(pos_x_parede)>0):
            colide = True
            
            while colide:
                colide_aux = False
                pos_x = random.randint(0,1270)
                pos_y = random.randint(0,710)
                tipo = 1
                for x in range(len(pos_x_parede)):
                    if checa_colisao(pos_x,pos_y,pos_x_parede[x],pos_y_parede[x],10,40):
                        colide_aux = True
                if not colide_aux:
                    colide = False 
                    colide_aux = True
            pickup = {
                "pos_x":pos_x,
                "pos_y":pos_y,
                "tipo":tipo
            }
            pickups.append(pickup)

            with app.app_context():
                socketio.emit("spawn_pickup", {"pickups":pickups})
        socketio.sleep(10)

@socketio.on('change_name')
def change_name(data):
    jogadores[request.sid]['nickname'] = data['name']
    emit('update_player_pos', {'jogadores': jogadores}, broadcast=True)
    print(f"jogador {jogadores[request.sid]['nickname']}")



@socketio.on('connect')
def handle_connect():

    print('Cliente conectado:', request.sid, '/n')

    pos_x = random.randint(0,1240)
    pos_y = random.randint(0,680)
    jogadores[request.sid] = {
        'nickname':None,
        'pos_x':pos_x,
        'pos_y':pos_y,
        'hp':20,
        'pickup':0,
        'color':f"#{random.randint(0, 0xFFFFFF):06x}",
        'size':40,
        'mouse_x':0,
        'mouse_y':0,
        'alive':True,
        'kills':0,
        'death':0,
        'velocidade':1,
        'ammo':0,
        'dmg_modifier':1,
        'kill_streak':0
    }
    emit('spawn_bullets', {'bullets':bullets}, broadcast=True)
    emit('update_player_pos', {'sid': request.sid, 'jogadores': jogadores},broadcast=True)
    emit('recebe_mapa', {"paredes":paredes}, broadcast=True)
    emit("spawn_pickup", {"pickups":pickups})
    emit('update_game_state', {'game_start': game_start}, broadcast=True)
    print(jogadores)

@socketio.on('disconnect')
def handle_disconnect():
    print('Desconectou', request.sid)
    jogadores.pop(request.sid,None)
    if len(jogadores) == 0:
        global end_game, game_start
        end_game = False
        game_start = False
        paredes.clear()
        pickups.clear()
        pickups.append({
            "pos_x":None,
            "pos_y":None,
            "tipo":None,
        })
    emit('update_player_pos', {'jogadores': jogadores}, broadcast=True)
    emit('end_game', broadcast=True)

@socketio.on('end_game')
def EndGame():
    global end_game
    end_game = False
    paredes.clear()
    for sid, player in jogadores.items():
        jogadores[sid]['pos_x'] = None
        jogadores[sid]['pos_y'] = None
        jogadores[sid]['hp'] = 20
        jogadores[sid]['dmg_modifier'] = 1
        jogadores[sid]['pickup'] = 0
        jogadores[sid]['alive'] = False
        jogadores[sid]['kills'] = 0
        jogadores[sid]['death'] = 0
        jogadores[sid]['ammo'] = 0
        jogadores[sid]['kill_streak'] = 0
        jogadores[sid]['velocidade'] = 1

    emit('update_player_pos', {'jogadores': jogadores}, broadcast=True)
    emit('recebe_mapa', {"paredes":paredes}, broadcast=True)
    pickups.clear()
    pickups.append({
        "pos_x":None,
        "pos_y":None,
        "tipo":None,
    })
    emit("spawn_pickup", {"pickups":pickups}, broadcast=True)




@socketio.on('start_game')
def StartGame():

    global end_game, game_start
    end_game = False
    game_start = True
    
    criar_mapa()
    emit('recebe_mapa', {"paredes":paredes}, broadcast=True)
    pickups = [{
        "pos_x":None,
        "pos_y":None,
        "tipo":None,
    }]
    emit("spawn_pickup",{"pickups":pickups})
    colide = True
    num_colide = 0
    for sid,player in jogadores.items():
        while colide:
            num_colide = 0
            pos_x = random.randint(0,1240)
            pos_y = random.randint(0,680)
            for x in range(len(pos_x_parede)):
                if checa_colisao(pos_x,pos_y,pos_x_parede[x],pos_y_parede[x]):
                    num_colide += 1
            if num_colide == 0:
                colide = False
                
        jogadores[sid]['pos_x'] = pos_x
        jogadores[sid]['pos_y'] = pos_y
        jogadores[sid]['hp'] = 20
        jogadores[sid]['dmg_modifier'] = 1
        jogadores[sid]['pickup'] = 0
        jogadores[sid]['alive'] = True
        jogadores[sid]['kills'] = 0
        jogadores[sid]['death'] = 0
        jogadores[sid]['ammo'] = 0
        jogadores[sid]['kill_streak'] = 0
        jogadores[sid]['velocidade'] = 1
        pickups = [{
            "pos_x":None,
            "pos_y":None,
            "tipo":None,
        }]
        emit("spawn_pickup",{"pickups":pickups}, broadcast=True)
        emit('update_player_pos', {'sid': sid, 'jogadores': jogadores}, broadcast=True)
        emit('update_game_state', {'game_start': game_start}, broadcast=True)
        colide = True
        num_colide = 0

@socketio.on("respawn")
def Respawn():
    jogadores[request.sid]['alive'] = True
    colide = True
    num_colide = 0
    for sid,player in jogadores.items():
        while colide:
            num_colide = 0
            pos_x = random.randint(0,1280)
            pos_y = random.randint(0,720)
            for x in range(len(pos_x_parede)):
                if checa_colisao(pos_x,pos_y,pos_x_parede[x],pos_y_parede[x]):
                    num_colide += 1
            if num_colide == 0:
                colide = False
                
        jogadores[request.sid]['pos_x'] = pos_x
        jogadores[request.sid]['pos_y'] = pos_y
        jogadores[request.sid]['alive'] = True
        emit('update_player_pos', {'sid': sid, 'jogadores': jogadores})
        colide = True
        num_colide = 0



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
        jogadores[request.sid]['ammo'] -= 1
        if(jogadores[request.sid]['ammo'] <= 0):
            jogadores[request.sid]['pickup'] = 0
        emit('update_player_pos', {'sid': request.sid, 'jogadores': jogadores}, broadcast=True)
        blt_id += 1


@socketio.on('kamehameha')
def handle_kamehameha(data):
    global kmh_id
    kamehamehas_ativos[kmh_id] = {
        'dono_sid': request.sid,
        'angulo': data['angulo'],
        'inicio': time.time(),
    }
    kmh_id += 1

    
    socketio.emit('kamehameha_fire', {'sid': request.sid, 'angulo': data['angulo']})

    

def kamehamehaAtivo():
    while True:
        agora = time.time()
        ids_expirados = []

        for kid, kmh in list(kamehamehas_ativos.items()):
            if agora - kmh['inicio'] > KAMEHAMEHA_DURATION_S:
                ids_expirados.append(kid)
                continue

            dono_sid = kmh['dono_sid']
            dono = jogadores.get(dono_sid)
            if not dono or not dono['alive']:
                ids_expirados.append(kid)
                continue

            for sid, player in jogadores.items():
                if sid == dono_sid or not player['alive']:
                    continue
                if checa_colisao_kamehameha(
                    dono['pos_x'], dono['pos_y'], 40, kmh['angulo'],
                    player['pos_x'], player['pos_y'], 40
                ):
                    jogadores[sid]['hp'] -= 9999
                    if jogadores[sid]['hp'] <= 0 and jogadores[sid]['alive']:
                        jogadores[sid]['alive'] = False
                        jogadores[sid]['pos_x'] = None
                        jogadores[sid]['pos_y'] = None
                        jogadores[sid]['death'] += 1
                        jogadores[dono_sid]['kills'] += 1
                        jogadores[dono_sid]['kill_streak'] += 1
                        jogadores[sid]['kill_streak'] = 0
                        with app.app_context():
                            socketio.emit('kill_feed', {
                                'killer_name': jogadores[dono_sid]['nickname'],
                                'victim_name': jogadores[sid]['nickname']
                            })
                        killed_players.append(sid)
                        socketio.start_background_task(auto_spawn)
                    with app.app_context():
                        socketio.emit('update_player_pos', {'sid': sid, 'jogadores': jogadores})

        for kid in ids_expirados:
           jogadores[kamehamehas_ativos.pop(kid, None)['dono_sid']]['pickup'] = 0

            

        socketio.sleep(0.01667)

#@socketio.on('kamehameha')
def handle_kamehameha_dummy(data):
    socketio.emit('kamehameha_fire', {'sid': request.sid, 'angulo': data['angulo']})
    for sid, player in jogadores.items():
        if sid == request.sid:
            continue  # não bate em si mesmo
        if checa_colisao_kamehameha(
            jogadores[request.sid]['pos_x'], jogadores[request.sid]['pos_y'], 40, data['angulo'],
            player['pos_x'], player['pos_y'], 40
        ):      
            jogadores[sid]['hp'] -= 9999
            if jogadores[sid]['hp'] <= 0:
                jogadores[sid]['alive'] = False
                jogadores[sid]["pos_x"] = None
                jogadores[sid]["pos_y"] = None
                jogadores[sid]['death'] += 1
                jogadores[request.sid]['kills'] += 1
                jogadores[request.sid]['kill_streak'] += 1
                jogadores[sid]['kill_streak'] = 0
                
                with app.app_context():
                    socketio.emit('kill_feed',{'killer_name':jogadores[request.sid]['nickname'],'victim_name':jogadores[sid]['nickname']})
                killed_players.append(sid)
                socketio.start_background_task(auto_spawn)
            with app.app_context():
                socketio.emit('update_player_pos', {'sid': sid, 'jogadores': jogadores})
        jogadores[request.sid]['pickup'] = 0
        jogadores[request.sid]['ammo'] = 0
        with app.app_context():
            socketio.emit('update_player_pos', {'sid': sid, 'jogadores': jogadores})
       

@socketio.on('melee')
def handle_melee(data):
    socketio.emit('melee_swing', {'sid': request.sid, 'angulo': data['angulo']})
    for sid, player in jogadores.items():
        if sid == request.sid:
            continue  # não bate em si mesmo
        if checa_colisao_melee(
            jogadores[request.sid]['pos_x'], jogadores[request.sid]['pos_y'], 40, data['angulo'],
            player['pos_x'], player['pos_y'], 40
        ):  
            
            jogadores[sid]['hp'] -= 10
            if jogadores[sid]['hp'] <= 0:
                jogadores[sid]['alive'] = False
                jogadores[sid]["pos_x"] = None
                jogadores[sid]["pos_y"] = None
                jogadores[sid]['death'] += 1
                jogadores[request.sid]['kills'] += 1
                jogadores[request.sid]['kill_streak'] += 1
                jogadores[sid]['kill_streak'] = 0
                with app.app_context():
                    socketio.emit('kill_feed',{'killer_name':jogadores[request.sid]['nickname'],'victim_name':jogadores[sid]['nickname']})
                killed_players.append(sid)
                socketio.start_background_task(auto_spawn)
            with app.app_context():
                socketio.emit('update_player_pos', {'sid': sid, 'jogadores': jogadores})
    
def balaAndando():

    


    while True:
        socketio.emit("spawn_pickup", {"pickups":pickups})
        bullets_aux = bullets.copy()
        for id,bala in bullets_aux.items():
            nova_pos_x = bala['pos_x'] + bala['vel_x']
            nova_pos_y = bala['pos_y'] + bala['vel_y']

            for x in range(len(pos_x_parede)):
                if checa_colisao(nova_pos_x,nova_pos_y,pos_x_parede[x],pos_y_parede[x],10,40):
                    bullets_aux[id]['alive'] = False


            if bullets_aux[id]["alive"]:
                for sid,player in jogadores.items():
                    if checa_colisao(nova_pos_x, nova_pos_y, player['pos_x'], player['pos_y'],10,40) and bullets_aux[id]['dono_sid'] != sid:

                        jogadores[sid]['hp'] -= 1*jogadores[bullets_aux[id]['dono_sid']]['dmg_modifier']

                        if jogadores[sid]['hp'] <= 0:
                            jogadores[sid]['alive'] = False
                            jogadores[sid]["pos_x"] = None
                            jogadores[sid]["pos_y"] = None
                            jogadores[sid]['death'] += 1
                            jogadores[bullets_aux[id]['dono_sid']]['kills'] += 1
                            jogadores[bullets_aux[id]['dono_sid']]['kill_streak'] += 1
                            jogadores[sid]['kill_streak'] = 0
                            jogadores[sid]['velocidade'] = 1

                            with app.app_context():
                                socketio.emit('kill_feed',{'killer_name':jogadores[bullets_aux[id]['dono_sid']]['nickname'],'victim_name':jogadores[sid]['nickname']})
                            killed_players.append(sid)
                            socketio.start_background_task(auto_spawn)
                        bullets_aux[id]['alive'] = False
                        with app.app_context():
                            socketio.emit('update_player_pos', {'sid': sid, 'jogadores': jogadores})
                bala['pos_x'] += bala['vel_x']
                bala['pos_y'] += bala['vel_y']


        with app.app_context():
            socketio.emit("spawn_bullets", {"bullets":bullets.copy()})

        socketio.sleep(0.01667)



@socketio.on('send_mouse')
def update_player_mouse(data):
    jogadores[request.sid]['mouse_x'] = data['mouse_x']
    jogadores[request.sid]['mouse_y'] = data['mouse_y']

    emit('update_player_pos', {'sid': request.sid, 'jogadores': jogadores}, broadcast=True)

def auto_spawn():
    sid = killed_players.pop()
    socketio.sleep(5)
    jogadores[sid]['alive'] = True
    colide = True
    num_colide = 0
   
    while colide:
        num_colide = 0
        pos_x = random.randint(0,1240)
        pos_y = random.randint(0,680)
        for x in range(len(pos_x_parede)):
            if checa_colisao(pos_x,pos_y,pos_x_parede[x],pos_y_parede[x]):
                num_colide += 1
        if num_colide == 0:
            colide = False
            
    jogadores[sid]['pos_x'] = pos_x
    jogadores[sid]['pos_y'] = pos_y
    jogadores[sid]['alive'] = True
    jogadores[sid]['hp'] = 20
    socketio.emit('update_player_pos', {'sid': sid, 'jogadores': jogadores})
    colide = True
    num_colide = 0

@socketio.on('move_up')
def handle_move_up(data):
    global pickup
    jogador = jogadores.get(request.sid)

    if(jogador['alive']==False):
        return

    if(jogador['pos_x'] == None or jogador['pos_y'] == None):
        jogadores.get(request.sid)['pos_x'] = 0
        jogadores.get(request.sid)['pos_y'] = 0
        emit('update_player_pos', {'sid': request.sid, 'jogadores': jogadores}, broadcast=True)
        return

    nova_pos_y = jogador['pos_y'] - data['speed'] * jogador['velocidade']

    for x in range(len(pos_x_parede)):
        if checa_colisao(jogador["pos_x"],nova_pos_y,pos_x_parede[x],pos_y_parede[x]):
            nova_pos_y = jogador["pos_y"] + 40 - abs((jogador['pos_y']-pos_y_parede[x]))
            break

        


    if nova_pos_y>680 or nova_pos_y<0:
        return

    for sid,player in jogadores.items():
        if sid != request.sid and checa_colisao(jogador['pos_x'], nova_pos_y, player['pos_x'], player['pos_y']):
            return

    pickups_copy = pickups.copy()
    for index,pickup in enumerate(pickups_copy):
        if checa_colisao_pickup(jogador['pos_x'], nova_pos_y, pickup['pos_x'], pickup['pos_y']):

            if(pickup['tipo']==1 and jogadores[request.sid]['pickup'] != 100):
                pickups.pop(index)
                jogadores.get(request.sid)['pickup'] = 1
                jogadores[request.sid]['ammo'] = 10
            if(pickup['tipo']==2):
                pickups.pop(index)
                new_health = jogadores[request.sid]['hp'] + 10

                if new_health > 20:
                    jogadores[request.sid]['hp'] = 20
                else:
                    jogadores[request.sid]['hp'] = new_health
            if(pickup['tipo']==3):
                pickups.pop(index)
                dmg_modifier = 2
                jogadores[request.sid]['dmg_modifier'] = dmg_modifier
            if(pickup['tipo']==4 and jogadores[request.sid]['pickup'] != 100):
                pickups.pop(index)
                jogadores[request.sid]['pickup'] = 4
            if(pickup['tipo']==5):
                pickups.pop(index)
                jogadores[request.sid]['velocidade'] += 0.5

                
            emit('pickup_dispawn',{'pickup':pickup}, broadcast=True)
            emit('equip_weapon',{'sid':request.sid})
            print("Jogador pegou o objeto")

    jogadores.get(request.sid)['pos_y'] = nova_pos_y
    emit('update_player_pos', {'sid': request.sid, 'jogadores': jogadores}, broadcast=True)


@socketio.on('move_down')
def handle_move_down(data):
    jogador = jogadores.get(request.sid)

    global pickup

    if(jogador['alive']==False):
        return

    if(jogador['pos_x'] == None or jogador['pos_y'] == None):
        jogadores.get(request.sid)['pos_x'] = 0
        jogadores.get(request.sid)['pos_y'] = 0
        emit('update_player_pos', {'sid': request.sid, 'jogadores': jogadores}, broadcast=True)
        return

    nova_pos_y = jogador['pos_y'] + data['speed'] * jogador['velocidade']

    for x in range(len(pos_x_parede)):
        if checa_colisao(jogador["pos_x"],nova_pos_y,pos_x_parede[x],pos_y_parede[x]):
            nova_pos_y = jogador["pos_y"] - 40 + abs((jogador['pos_y']-pos_y_parede[x]))
            break

    
    if nova_pos_y>680 or nova_pos_y<0:
        return

    for sid,player in jogadores.items():
        if sid != request.sid and checa_colisao(jogador['pos_x'], nova_pos_y, player['pos_x'], player['pos_y']):
            return

    pickups_copy = pickups.copy()
    for index, pickup in enumerate(pickups_copy):
        if checa_colisao_pickup(jogador['pos_x'], nova_pos_y, pickup['pos_x'], pickup['pos_y']):
            if(pickup['tipo']==1 and jogadores[request.sid]['pickup'] != 100):
                pickups.pop(index)
                jogadores.get(request.sid)['pickup'] = 1
                jogadores[request.sid]['ammo'] = 10
            if(pickup['tipo']==2):
                pickups.pop(index)
                new_health = jogadores[request.sid]['hp'] + 10
                
                if new_health > 20:
                    jogadores[request.sid]['hp'] = 20
                else:
                    jogadores[request.sid]['hp'] = new_health
            if(pickup['tipo']==3):
                pickups.pop(index)
                dmg_modifier = 2
                jogadores[request.sid]['dmg_modifier'] = dmg_modifier
            if(pickup['tipo']==4 and jogadores[request.sid]['pickup'] != 100):
                pickups.pop(index)
                jogadores[request.sid]['pickup'] = 4
            if(pickup['tipo']==5):
                pickups.pop(index)
                jogadores[request.sid]['velocidade'] += 0.5
            print("Jogador pegou o objeto")

    jogadores.get(request.sid)['pos_y'] = nova_pos_y
    emit('update_player_pos', {'sid': request.sid, 'jogadores': jogadores}, broadcast=True)



@socketio.on('move_left')
def handle_move_left(data):
    jogador = jogadores.get(request.sid)

    global pickup

    if(jogador['alive']==False):
        return

    if(jogador['pos_x'] == None or jogador['pos_y'] == None):
        jogadores.get(request.sid)['pos_x'] = 0
        jogadores.get(request.sid)['pos_y'] = 0
        emit('update_player_pos', {'sid': request.sid, 'jogadores': jogadores}, broadcast=True)
        return

    nova_pos_x = jogador['pos_x'] - data['speed'] * jogador['velocidade']

    for x in range(len(pos_x_parede)):
        if checa_colisao(nova_pos_x,jogador["pos_y"],pos_x_parede[x],pos_y_parede[x]):
            nova_pos_x = jogador["pos_x"] + 40  - abs((jogador['pos_x']-pos_x_parede[x]))
            break


    if nova_pos_x > 1240 or nova_pos_x < 0:
        return


    for sid,player in jogadores.items():
        if sid != request.sid and checa_colisao(nova_pos_x, jogador['pos_y'], player['pos_x'], player['pos_y']):
            return
    pickups_copy = pickups.copy()
    for index, pickup in enumerate(pickups_copy):
        if checa_colisao_pickup(nova_pos_x,jogador['pos_y'],pickup["pos_x"],pickup['pos_y']):

                if(pickup['tipo']==1 and jogadores[request.sid]['pickup'] != 100):
                    pickups.pop(index)
                    jogadores.get(request.sid)['pickup'] = 1
                    jogadores[request.sid]['ammo'] = 10
                if(pickup['tipo']==2):
                    pickups.pop(index)
                    new_health = jogadores[request.sid]['hp'] + 10
                    
                    if new_health > 20:
                        jogadores[request.sid]['hp'] = 20
                    else:
                        jogadores[request.sid]['hp'] = new_health
                if(pickup['tipo']==3):
                    pickups.pop(index)
                    dmg_modifier = 2
                    jogadores[request.sid]['dmg_modifier'] = dmg_modifier
                if(pickup['tipo']==4 and jogadores[request.sid]['pickup'] != 100):
                    pickups.pop(index)
                    jogadores[request.sid]['pickup'] = 4
                if(pickup['tipo']==5):
                    pickups.pop(index)
                    jogadores[request.sid]['velocidade'] += 0.5
                

                print("Jogador pegou o objeto")

    jogadores.get(request.sid)['pos_x'] = nova_pos_x
    emit('update_player_pos', {'sid': request.sid, 'jogadores': jogadores}, broadcast=True)


@socketio.on('move_right')
def handle_move_right(data):
    jogador = jogadores.get(request.sid)

    if(jogador['alive']==False):
        return

    global pickup

    if(jogador['pos_x'] == None or jogador['pos_y'] == None):
        jogador['pos_x'] = 0
        jogador['pos_y'] = 0
        emit('update_player_pos', {'sid': request.sid, 'jogadores': jogadores}, broadcast=True)
        return

    nova_pos_x = jogador['pos_x'] + data['speed'] * jogador['velocidade']

    for x in range(len(pos_x_parede)):
        if checa_colisao(nova_pos_x,jogador["pos_y"],pos_x_parede[x],pos_y_parede[x]):
            nova_pos_x = jogador["pos_x"] - 40 + abs((jogador['pos_x']-pos_x_parede[x]))
            break


    if nova_pos_x > 1240 or nova_pos_x < 0:
        return


    for sid,player in jogadores.items():
        if sid != request.sid and checa_colisao(nova_pos_x, jogador['pos_y'], player['pos_x'], player['pos_y']):
            return

    pickups_copy = pickups.copy()
    for index, pickup in enumerate(pickups_copy):
        if checa_colisao_pickup(nova_pos_x,jogador['pos_y'],pickup["pos_x"],pickup['pos_y']):
                
                if(pickup['tipo']==1 and jogadores[request.sid]['pickup'] != 100):
                    pickups.pop(index)
                    jogadores.get(request.sid)['pickup'] = 1
                    jogadores[request.sid]['ammo'] = 10
                if(pickup['tipo']==2):
                    pickups.pop(index)
                    new_health = jogadores[request.sid]['hp'] + 10
                    
                    if new_health > 20:
                        jogadores[request.sid]['hp'] = 20
                    else:
                        jogadores[request.sid]['hp'] = new_health
                if(pickup['tipo']==3):
                    pickups.pop(index)
                    dmg_modifier = 2
                    jogadores[request.sid]['dmg_modifier'] = dmg_modifier
                if(pickup['tipo']==4 and jogadores[request.sid]['pickup'] != 100):
                    pickups.pop(index)
                    jogadores[request.sid]['pickup'] = 4
                if(pickup['tipo']==5):
                    pickups.pop(index)
                    jogadores[request.sid]['velocidade'] += 0.5

                print("Jogador pegou o objeto")

    jogadores.get(request.sid)['pos_x'] = nova_pos_x
    emit('update_player_pos', {'sid': request.sid, 'jogadores': jogadores}, broadcast=True)

def kill_streak_prize():
    while True:
        for sid, player in jogadores.items():
            if player['kill_streak'] >= 5:
                print('concedindo prêmio de kill streak para', player['nickname'])
                player['pickup'] = 100
                player['kill_streak'] = 0
                socketio.emit('update_player_pos', {'sid': sid, 'jogadores': jogadores})
        socketio.sleep(0.01667)


if __name__ == "__main__":
    socketio.start_background_task(spawn_pickup_chance)
    socketio.start_background_task(balaAndando)
    socketio.start_background_task(checa_win_condition)
    socketio.start_background_task(kill_streak_prize)
    socketio.start_background_task(kamehamehaAtivo)
    socketio.run(app, host='0.0.0.0', port=5080, debug=True, log_output=False)
