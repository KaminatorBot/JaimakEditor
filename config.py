from TheHub.commands import *
from TheHub.points import *
import socket, sys, pickle, os
from collections import deque
import threading as t

# Panel de configuracion

info = {
    'all': [' ', [], [(0, 0, 0), (255, 255, 255)]],
    'points': deque([]),
    'cursor-digit': 'x',
    'cursor-id': [],
    'colors': {'foreground': (255, 255, 255), 'background': (0, 0, 0)},
    'colors_all': {'foreground': (255, 255, 255), 'background': (0, 0, 0)},
    'mode': 1,
    'temp-point': False,
    'args': {'circle': None, 'text': None}
}

def rgb(a, b, text):
    return '\033[48;2;{0};{1};{2}m\033[38;2;{3};{4};{5}m{6}\033[0m'.format(a[0], a[1], a[2], b[0], b[1], b[2], text)

# Iniciamos el socket
config = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Limpieza inicial de la consola 
sys.stdout.write('\033[H\033[2J')

# Envio de paquetitos xd
def recv_all(config:socket.socket):
    data = b''

    while True:
        packet = config.recv(4096)

        if not packet:
            break

        data += packet

        if len(packet) < 4096:
            break
    return data

# Funcion de obtencion de datos
def get_data():
    global config, info

    while True:
        try:
            data = recv_all(config)
            info = pickle.loads(data)
        except:
            exit()

# Funcion de envio de datos
def send_data():
    global config, info

    serialized_data = pickle.dumps(info)
    config.sendall(serialized_data)

# Intentar conectar con el programa BitMapEditor
try:
    print('Iniciando ventana...')
    config.connect(('localhost', 5059))
    t.Thread(target=get_data).start()
    sys.stdout.write('\033[H\033[2J')
except:
    print('Primero inicia el programa BitMapEditor!')
    input()
    exit()

# Comandos
class Clear(Command):
    name = 'clear'
    static_args = []

    @classmethod
    def execute(cls):
        sys.stdout.write('\033[H\033[2J')

class Cursor(Command):
    name = 'cursor'
    static_args = [Argument('action', None, 'text'), Argument('obj', None, 'text')]
    more_args = []

    @classmethod
    # Funcion set(): Cambiar algun dato en especifico del cursor
    def set_(cls):
        global info
        match (cls.static_args[1].value.lower()):
            case 'digit':
                try:
                    info['cursor-digit'] = str(cls.more_args[0])
                    send_data()
                except:
                    print('Error -> Faltan argumentos!')
                    return
                print('Aviso -> Se a cambiado el digito del cursor!')
            case 'bgcolor':
                try:
                    info['colors']['background'] = (int(cls.more_args[0]), int(cls.more_args[1]), int(cls.more_args[2]))
                    send_data()
                except:
                    print('Error -> Faltan argumentos!')
                    return
                print('Aviso -> Se a cambiado el color de fondo!')
            case 'fgcolor':
                try:
                    info['colors']['foreground'] = (int(cls.more_args[0]), int(cls.more_args[1]), int(cls.more_args[2]))
                    send_data()
                except:
                    print('Error -> Faltan argumentos!')
                    return
                print('Aviso -> Se a cambiado el color del cursor!')
            case 'id':
                info['cursor-id'] = []
                for i in cls.more_args:
                    info['cursor-id'].append(str(i))
                send_data()
            case 'mode':
                try:
                    cls.more_args[0]
                except:
                    print('Error -> Faltan argumentos!')
                    return
                
                match(cls.more_args[0]):
                    case 'point':
                        if info['temp-point'] is False:
                            info['mode'] = 1
                            send_data()
                            print('Aviso -> Se a cambiado a modo "point"!')
                            return
                        else:
                            print('Error -> No se puede cambiar de modo en este momento!')
                            return
                    case 'line':
                        if info['temp-point'] is False:
                            info['mode'] = 2
                            send_data()
                            print('Aviso -> Se a cambiado a modo "line"!')
                            return
                        else:
                            print('Error -> No se puede cambiar de modo en este momento!')
                            return
                    case 'square':
                        if info['temp-point'] is False:
                            info['mode'] = 3
                            send_data()
                            print('Aviso -> Se a cambiado a modo "square"!')
                            return
                        else:
                            print('Error -> No se puede cambiar de modo en este momento!')
                            return
                    case 'circle':
                        if info['temp-point'] is False:
                            try:
                                info['mode'] = 4
                                info['args']['circle'] = int(cls.more_args[1])
                                send_data()
                                print('Aviso -> Se a cambiado a modo "circle"!')
                                return
                            except:
                                print('Error -> Se debe proporcionar un radio! (numero entero)')
                                return
                        else:
                            print('Error -> No se puede cambiar de modo en este momento')
                            return
                    case 'text':
                        if info['temp-point'] is False:
                            try:
                                info['mode'] = 5

                                info['args']['text'] = str(cls.more_args[1])
                                send_data()
                                print('Aviso -> Se a cambiado a modo "text"!')
                            except:
                                print('Error -> Se debe proporcionar un texto!')
                                return
                        else:
                            print('Error -> No se puede cambiar de modo en este momento!')
                            return
                    case _:
                        print('Error -> No existe ese tipo de trazado!')
                        return
            case _: print('Error -> Argumento no valido!')

    @classmethod
    # Funcion get(): Obtener algun dato en especifico del cursor
    def get(cls):
        global info
        match (cls.static_args[1].value.lower()):
            case 'digit':
                print(info['cursor-digit'])
            case 'id':
                if len(info['cursor-id']) == 0:
                    print('Aviso -> No hay id que mostrar!')
                    return
                j = 0
                for i in info['cursor-digit']:
                    print(f'"{i}"', end=' ' if j < 3 else '\n')
                    j = j+1 if j != 3 else 0
            case 'bgcolor':
                print(info['colors']['background'])
            case 'fgcolor':
                print(info['colors']['foreground'])

    @classmethod
    def execute(cls):
        match cls.static_args[0].value.lower():
            case 'set':
                cls.set_()
            case 'get':
                cls.get()
            case _:
                print('Error -> Argumento no aceptado!')
                return 

class Window(Command):
    name = 'window'
    static_args = [Argument('action', None, 'text'), Argument('obj', None, 'text')]
    more_args = []

    @classmethod
    def set_(cls):
        match cls.static_args[1].value.lower():
            case 'digit':
                try:
                    info['all'][0] = str(cls.more_args[0])
                except:
                    print('Error -> Falta de argumentos!')
                    return
                else:
                    send_data()
                    print('Aviso -> Se a cambiado el digito de fondo!')
                    return
            case 'fgcolor':
                try:
                    info['colors_all']['foreground'] = (int(cls.more_args[0]), int(cls.more_args[1]), int(cls.more_args[2]))
                except ValueError:
                    print('Error -> Los argumentos deben ser enteros!')
                    return
                except:
                    print('Error -> Falta de argumentos!')
                    return
                else:
                    send_data()
                    print('Aviso -> Se a cambiado el color del digito de fondo!')
                    return
            case 'bgcolor':
                try:
                    info['colors_all']['background'] = (int(cls.more_args[0]), int(cls.more_args[1]), int(cls.more_args[2]))
                except ValueError:
                    print('Error -> Los argumentos deben ser enteros!')
                    return
                except Exception:
                    print('Error -> Falta de argumentos!')
                    return
                else:
                    send_data()
                    print('Aviso -> Se a cambiado el color de fondo del digito de fondo!')
                    return
            case 'id':
                try:
                    info['all'][1] = []
                    for i in cls.more_args:
                        info['all'][1].append(str(i))
                except:
                    print('Error -> Falta argumentos!')
                    return
                else:
                    send_data()
                    print('Aviso -> Se a cambiado el ID!')
                    return
    @classmethod
    def get(cls):
        match cls.static_args[1].value:
            case 'digit':
                print('"' + info['all'][0] + '"')
            case 'fgcolor':
                print(info['colors_all']['foreground'][0], info['colors_all']['foreground'][1], info['colors_all']['foreground'][2], end=' ')
            case 'bgcolor':
                print(info['colors_all']['background'][0], info['colors_all']['background'][1], info['colors_all']['background'][2], end=' ')
            case 'id':
                print(info['all'][1])

    @classmethod
    def execute(cls):
        if cls.static_args[0].value == 'set':
            cls.set_()
        elif cls.static_args[0].value == 'get':
            cls.get()
        else:
            print('Error -> Argumento invalido')
            return

VRS_CODE['COMMANDS'] = [Clear, Cursor, Window]

while True:
    sys.stdin = os.fdopen(0)
    compiler()