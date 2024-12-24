import sys, time, socket, pickle, subprocess
import keyboard as k
from TheHub.points import *
from TheHub.commands import *
from collections import deque
from pathlib import Path
import threading as t

# Nombre del programa: JaimakEditor
# Autor: KaminatorJoula
# Comentario del autor: No creo que haya necesidad de escribir mi nombre y el nombre del
# programa, pero lo hago por que soy un mamador pretencioso (broma).

# Easter Egg: No hay.
# Agradecimientos a: Nadie, solo yo B) (no tengo amigos o gente con quien socializar).

# Secuencias de escape ANSI
CLEAR_SCREEN = '\033[2J\033[0;0H' # Limpia toda la pantalla
MOVE_CURSOR = '\033[{row};{col}H' # Mueve el cursor a (row, col)
HIDE_CURSOR = '\033[?25l'
DISPLAY_CURSOR = '\033[?25h'

# Informacion inicial del jodido cursor y mas
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

# Dimensiones de la pantalla
wx, wy = None, None

# Servidor (La pantalla de configuracion)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 5059))
server.listen(1)

# Funcion para limpiar la pantalla
def clear():
    sys.stdout.write(CLEAR_SCREEN)
    sys.stdout.flush()

# Funcion para cambiar el color de un texto
def rgb(a, b, text):
    return '\033[48;2;{0};{1};{2}m\033[38;2;{3};{4};{5}m{6}\033[0m'.format(a[0], a[1], a[2], b[0], b[1], b[2], text)

# Datos del cursor
cursor = Point(1, 1, info['cursor-digit'], ['cursor'], [info['colors']['background'], info['colors']['foreground']])

window_background_digit = [rgb(info['colors_all']['background'], info['colors_all']['foreground'], info['all'][0]), info['all'][1].copy(), [info['colors_all']['background'], info['colors_all']['foreground']]]

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
def get_data(config:socket.socket):
    global info, cursor, window_background_digit

    while True:
        try:
            data = recv_all(config)
            info = pickle.loads(data)
        except:
            return

        window_background_digit = [rgb(info['colors_all']['background'], info['colors_all']['foreground'], info['all'][0]), info['all'][1].copy(), [info['colors_all']['background'], info['colors_all']['foreground']]]

        cursor = Point(cursor.x, cursor.y, info['cursor-digit'], ['cursor'], [info['colors']['background'], info['colors']['foreground']])
        info['points'].pop()
        info['points'].append(cursor)

# Funcion de envio de datos
def send_data(config:socket.socket):
    global info

    serialized_data = pickle.dumps(info)
    config.sendall(serialized_data)

# Reiniciar todo por predeterminado
def reset():
    global info, cursor, window_background_digit
    info = {
        'all': [' ', ['']],
        'points': deque([]),
        'cursor-digit': 'x',
        'cursor-id': [],
        'colors': {'foreground': (255, 255, 255), 'background': (0, 0, 0)},
        'colors_all': {'foreground': (255, 255, 255), 'background': (0, 0, 0)},
        'mode': 1,
        'temp-point': False,
        'args': {'circle': None, 'text': None}
    }
    
    window_background_digit = [rgb(info['colors_all']['background'], info['colors_all']['foreground'], info['all'][0]), info['all'][1].copy(), [info['colors_all']['background'], info['colors_all']['foreground']]]
    cursor = Point(1, 1, info['cursor-digit'], ['cursor'], [info['colors']['background'], info['colors']['foreground']])
    info['points'].append(cursor)

# Funcion para mover el cursor del CMD
def move_cursor(row, col):
    sys.stdout.write(MOVE_CURSOR.format(row=row, col=col))

# Funcion para dibujar el mapa
def draw_map():
    global info, MOVE_CURSOR, window_background_digit

    # Se carga el mapa para ser dibujado en la pantalla
    window = graph(wx, wy, info['points'].copy(), window_background_digit)

    # Dibujo del mapa en el CMD
    row = 1
    for v in window.values():
        line = ''
        for i in v:
            line += i[0]
        move_cursor(row, 0)
        sys.stdout.write(line)
        sys.stdout.flush()
        row += 1
    move_cursor(row, 0)
    
    mode:str
    match info['mode']:
        case 1: mode = 'point'
        case 2: mode = 'line'
        case 3: mode = 'square'
        case 4: mode = 'circle'
        case 5: mode = 'text'
    
    # Datos adicionales (pero importantes)

    colors = 'Foreground: ' + str(info['colors']['foreground']) + '; Background: ' + str(info['colors']['background']) + ';'
    down_text = f'Position: ({cursor.x}, {cursor.y}); Mode: {mode}; {colors}'
    sys.stdout.write(down_text + ' ' * (wx - len(down_text)))
    sys.stdout.flush()

# Meter el cursor
info['points'].append(cursor)

# Funcion para modificar el mapa
def draw_process():
    global cursor, wx, wy, info, HIDE_CURSOR, DISPLAY_CURSOR
    global server

    # Abriendo panel de configuracion
    print('Abriendo el panel de configuracion...')
    subprocess.Popen(['start', 'cmd', '/k', 'python', 'config.py'], shell=True)
    config, _ = server.accept()

    t.Thread(target=get_data, args=(config,)).start()

    send_data(config)

    sys.stdout.write(HIDE_CURSOR)
    sys.stdout.flush()

    # Variables estaticas
    tfs = 0.05

    # Variables temporales
    time_for_step_while = time.time()

    # Point temporal para cuando se active el modo Line o Square
    temp_point:Point|None = None

    # Variables para verificar la presion de una tecla
    e = False
    esc_pressed = False
    z_pressed = False

    # Tecla para bloquear/desbloquear teclado
    esc_actived = False

    # Movimientos del cursor
    while True:
        move_cursor(0, 0)
        draw_map()

        # Right
        if k.is_pressed('d') and time.time() - time_for_step_while >= tfs and not esc_actived and cursor.x < wx:
            cursor.x, time_for_step_while = cursor.x + 1, time.time()
        # Left
        elif k.is_pressed('a') and time.time() - time_for_step_while >= tfs and not esc_actived and cursor.x > 1:
            cursor.x, time_for_step_while = cursor.x - 1, time.time()
        # Up
        elif k.is_pressed('w') and time.time() - time_for_step_while >= tfs and not esc_actived and cursor.y < wy:
            cursor.y, time_for_step_while = cursor.y + 1, time.time()
        # Down
        elif k.is_pressed('s') and time.time() - time_for_step_while >= tfs and not esc_actived and cursor.y > 1:
            cursor.y, time_for_step_while = cursor.y - 1, time.time()
        
        # Dibujar objeto segun el modo seleccionado (point/line/square/circle/text)
        if k.is_pressed('e') and not e and not esc_actived:
            e = True

            match (info['mode']):
                # Point
                case 1:
                    info['points'].pop()
                    info['points'].append(Point(cursor.x, cursor.y, info['cursor-digit'], info['cursor-id'].copy(), [info['colors']['background'], info['colors']['foreground']]))
                    info['points'].append(cursor)
                    send_data(config)
                # Line
                case 2:
                    if temp_point is None:
                        temp_point = Point(cursor.x, cursor.y)
                        info['temp-point'] = True
                        send_data(config)
                    else:
                        info['points'].pop()
                        info['points'].append(Line(temp_point, Point(cursor.x, cursor.y), info['cursor-digit'], info['cursor-id'].copy(), [info['colors']['background'], info['colors']['foreground']]))
                        temp_point = None
                        info['temp-point'] = False
                        info['points'].append(cursor)
                        send_data(config)
                # Square
                case 3:
                    if temp_point is None:
                        temp_point = Point(cursor.x, cursor.y)
                        info['temp-point'] = True
                        send_data(config)
                    else:
                        info['points'].pop()
                        info['points'].append(Square(temp_point, Point(cursor.x, cursor.y), info['cursor-digit'], info['cursor-id'].copy(), [info['colors']['background'], info['colors']['foreground']]))
                        temp_point = None
                        info['temp-point'] = False
                        info['points'].append(cursor)
                        send_data(config)
                # Circle
                case 4:
                    info['points'].pop()
                    info['points'].append(Circle(Point(cursor.x, cursor.y), info['args']['circle'], info['cursor-digit'], info['cursor-id'].copy(), [info['colors']['background'], info['colors']['foreground']]))
                    info['points'].append(cursor)
                    send_data(config)
                # Text
                case 5:
                    info['points'].pop()
                    info['points'].append(Text(info['args']['text'], Point(cursor.x, cursor.y), info['cursor-id'].copy(), [info['colors']['background'], info['colors']['foreground']]))
                    info['points'].append(cursor)
                    send_data(config)
        elif not k.is_pressed('e') and e:
            e = False

        # Bloquear teclado excepto ESC
        if k.is_pressed('esc') and not esc_pressed:
            esc_pressed = True

            esc_actived = not esc_actived
        elif not k.is_pressed('esc') and esc_pressed:
            esc_pressed = False

        # Eliminar el ultimo objeto dibujado
        if k.is_pressed('z') and not z_pressed:
            z_pressed = True
            if len(info['points']) > 1:
                info['points'].pop()
                info['points'].pop()
                info['points'].append(cursor)
                send_data(config)
        elif not k.is_pressed('z') and z_pressed:
            z_pressed = False
        
        # Salir y guardar 
        if k.is_pressed('q') and not esc_actived and not info['temp-point']:
            info['points'].pop()
            sys.stdout.write(DISPLAY_CURSOR)
            sys.stdout.flush()
            config.close()
            return
        
        sys.stdout.flush()

# Funcion principal / Pantalla de inicio
def main():
    global wx, wy, window_background_digit, cursor
    while True:
        logo = open('logo.txt', 'r')
        print('\033[38;2;170;255;170m' + logo.read() + '\033[0m')
        logo.close()

        print('1 - Create map')
        print('2 - Load map')
        print('3 - Exit')

        response:str = ''
        while response not in ['1', '2', '3']:
            response = input('Elige una opcion: ')
            clear()
            print('Error -> Esa no es una opcion valida, intenta de nuevo.')
        clear()

        match (int(response)):
            case 1:
                # Reiniciar la variable 'info'
                reset()
                
                # Obtener dimensiones del mapa
                # Obtener el ancho
                while True:
                    try:
                        while wx is None or wx < 1:
                            wx = int(input('Ancho: '))
                    except:
                        clear()
                        print('Error -> Escribe un valor numerico valido.')
                        wx = None
                    else:
                        break
                clear()

                # Obtener el largo
                while True:
                    try:
                        while wy is None or wy < 1:
                            wy = int(input('Alto: '))
                    except:
                        clear()
                        print('Error -> Escribe un valor numerico valido')
                        wy = None
                    else:
                        break
                clear()

                # Identificador del mapa
                map_id = input('ID del mapa: ')
                clear()

                # Nombre del mapa
                map_name = ''
                while map_name.replace(' ', '') == '':
                    map_name = input('Map name: ')
                    clear()
                    print('Error -> Nombre no aceptado!')
                clear()

                # Ruta del directorio donde se guardara el mapa
                map_path = ''
                while map_path.replace(' ', '') == '' or not Path(map_path).exists() or not Path(map_path).is_dir():
                    map_path = input('Directorio donde se guardara el mapa: ')
                    clear()
                    print('Error -> Ruta no encontrada! (asegurate de escribir un directorio/carpeta y no un archivo)')
                clear()
                
                # Inicio de dibujo del mapa
                draw_process()
                clear()

                # Guardado del mapa
                try:
                    map_data = {'map': info['points'].copy(), 'all': [info['all'][0], info['all'][1].copy(), [info['colors_all']['background'], info['colors_all']['foreground']]], 'id': map_id, 'screen': [wx, wy]}
                    pickle.dump(map_data, open(Path(map_path + '/' + map_name), 'wb'))
                except:
                    print('Error -> Hubo un error al guardar el mapa.')

                print('Aviso -> El mapa se a creado. (Press ENTER)')
                input()

                clear()
                print('Espera un momento...')
                time.sleep(0.5)
                clear()
            case 2:
                # Reiniciar la variable 'info'
                reset()
                map_path = ''
                # Obtencion de la ruta COMPLETA (con directorio/archivo) del archivo donde se ubica el mapa
                while map_path.replace(' ', '') == '' or not Path(map_path).exists() or not Path(map_path).is_file():
                    map_path = input('Archivo donde se ubica el mapa: ')
                    clear()
                    print('Error -> Mapa no encontrado! (asegurate de abrir un archivo y no un directiorio/carpeta)')
                clear()

                # Obtenemos todos los puntos del mapa seleccionado
                map_data = pickle.load(open(Path(map_path), 'rb'))
                temp_points = []
                for i in map_data['map']:
                    temp_points.append(i)
                info['points'] = deque(temp_points.copy())
                info['points'].append(cursor)

                # Obtenemos el fondo
                info['all'] = [map_data['all'][0], map_data['all'][1].copy()]
                info['colors_all'] = {'foreground': map_data['all'][2][1], 'background': map_data['all'][2][0]}
                window_background_digit = [rgb(info['colors_all']['background'], info['colors_all']['foreground'], info['all'][0]), info['all'][1].copy(), [info['colors_all']['background'], info['colors_all']['foreground']]]
                
                # Obtenemos las dimensiones
                wx, wy = map_data['screen'][0], map_data['screen'][1]

                # ID nuevo del mapa
                map_id = input('Nuevo ID del mapa (si no quieres cambiarle el ID, solo dejalo en blanco): ')
                clear()

                # Inicio del dibujo del mapa
                draw_process()
                clear()

                # Guardado de cambios
                try:
                    map_data = {'map': info['points'].copy(), 'all': [info['all'][0], info['all'][1].copy(), [info['colors_all']['background'], info['colors_all']['foreground']]], 'id': map_data['id'] if map_id.replace(' ', '') == '' else map_id, 'screen': map_data['screen'].copy()}
                    pickle.dump(map_data, open(Path(map_path), 'wb'))
                except:
                    print('Error -> El mapa no se pudo modificar, ocurrio un error en el sistema. (Press ENTER)')
                else:
                    print('Aviso -> El mapa se a modificado. (Press ENTER)')
                input()

                clear()
                print('Espera un minuto...')
                time.sleep(0.5)
                clear()
            case 3:
                exit()
                
main()