def __rgb(b:tuple, f:tuple, text:str):
    return '\033[48;2;{0};{1};{2}m\033[38;2;{3};{4};{5}m{6}\033[0m'.format(b[0],b[1],b[2],f[0],f[1],f[2],text)

class Point:
    def __init__(self, x:int, y:int, d:str=None, id_:list[str]=[], colors:list[tuple]=[(0, 0, 0), (255, 255, 255)]):
        self.x = x
        self.y = y
        self.d = d
        self.colors = colors
        self.id_ = id_
    
    def __str__(self):
        return f'Point d="{self.d}" id={self.id_} ({self.x}, {self.y})'
    def copy(self):
        return Point(self.x, self.y, self.d, self.id_.copy(), self.colors.copy())

class Line:
    def __init__(self, pi:Point, pf:Point, d:str, id_:list[str]=[], colors:list[tuple]=[(0, 0, 0), (255, 255, 255)]):
        self.pi = pi
        self.pf = pf
        self.d = d
        self.colors = colors
        self.id_ = id_
    
    def __str__(self):
        return f'Line d="{self.d}" id_={self.id_} [({self.pi.x}, {self.pi.y}), ({self.pf.x}, {self.pf.y})]'
    def copy(self):
        return Line(self.pi.copy(), self.pf.copy(), self.d, self.id_.copy(), self.colors.copy())
    
class Square:
    def __init__(self, pi:Point, pf:Point, d:str, id_:list[str]=[], colors:list[tuple]=[(0, 0, 0), (255, 255, 255)]):
        self.pi = pi
        self.pf = pf
        self.d = d
        self.colors = colors
        self.id_ = id_
    
    def __str__(self):
        return f'Square d="{self.d}" id_={self.id_} [({self.pi.x}, {self.pi.y}), ({self.pf.x}, {self.pf.y})]'
    def copy(self):
        return Square(self.pi.copy(), self.pf.copy(), self.d, self.id_.copy(), self.colors.copy())

class Text:
    def __init__(self, text:str|list[str], position:Point, id_:list[str]=[], colors:list[tuple]=[(0, 0, 0), (255, 255, 255)]):
        self.text = text
        self.position = position
        self.colors = colors
        self.id_ = id_

    def __str__(self):
        return f'Text text="{self.text}" id={self.id_} ({self.position.x}, {self.position.y})'
    def copy(self):
        return Text(self.text, self.position.copy(), self.id_.copy(), self.colors.copy())

class Circle:
    def __init__(self, position:Point, radius:int, d:str, id_:list[str]=[], colors:list[tuple]=[(0, 0, 0), (255, 255, 255)]):
        self.position = position
        self.radius = radius
        self.d = d
        self.colors = colors
        self.id_ = id_
    
    def __str__(self):
        return f'Circle radius={self.radius} d="{self.d}" id="{self.id_}" [({self.position.x}, {self.position.y})]'
    def copy(self):
        return Circle(self.position.copy(), self.radius, self.d, self.id_.copy(), self.colors.copy())

def __draw_line(p: Line, wx: int, wy: int, window: dict):
    delta_x = abs(p.pf.x - p.pi.x)
    delta_y = abs(p.pf.y - p.pi.y)
    xi, xf, yi, yf = p.pi.x, p.pf.x, p.pi.y, p.pf.y
    step_x = 1 if xi < xf else -1
    step_y = 1 if yi < yf else -1

    error = delta_x - delta_y

    while xi != xf or yi != yf:
        if 0 <= xi < wx and 1 <= yi < wy:
            window[yi][xi-1] = [__rgb(p.colors[0], p.colors[1], p.d), p.id_ + window[yi][xi-1][1], p.colors]

        double_error = 2 * error

        if double_error > -delta_y:
            error -= delta_y
            xi += step_x

        if double_error < delta_x:
            error += delta_x
            yi += step_y

    if 0 <= xi < wx and 0 <= yi < wy:
        window[yi][xi-1] = [__rgb(p.colors[0], p.colors[1], p.d), p.id_ + window[yi][xi-1][1], p.colors]
        
    return window

def __draw_circle(c: Circle, wx: int, wy: int, window: list):
    x = c.radius
    y = 0
    radius_error = 1 - x

    while x >= y:
        if 0 <= c.position.x + x < wx and 0 <= c.position.y + y < wy:
            if c.position.y + y <= wy and c.position.x + x - 1 < wx:
                window[c.position.y + y][c.position.x + x - 1] = [__rgb(c.colors[0], c.colors[1], c.d), c.id_ + window[c.position.y + y][c.position.x + x - 1][1], c.colors]
        if 0 <= c.position.x + y < wx and 0 <= c.position.y + x < wy:
            if c.position.y + x <= wy and c.position.x + y - 1 < wx:
                window[c.position.y + x][c.position.x + y - 1] = [__rgb(c.colors[0], c.colors[1], c.d), c.id_ + window[c.position.y + x][c.position.x + y - 1][1], c.colors]
        if 0 <= c.position.x - y < wx and 0 <= c.position.y + x < wy:
            if c.position.y + x <= wy and c.position.x - y - 1 >= 0:
                window[c.position.y + x][c.position.x - y - 1] = [__rgb(c.colors[0], c.colors[1], c.d), c.id_ + window[c.position.y + x][c.position.x - y - 1][1], c.colors]
        if 0 <= c.position.x - x < wx and 0 <= c.position.y + y < wy:
            if c.position.y + y <= wy and c.position.x - x - 1 >= 0:
                window[c.position.y + y][c.position.x - x - 1] = [__rgb(c.colors[0], c.colors[1], c.d), c.id_ + window[c.position.y + y][c.position.x - x - 1][1], c.colors]
        if 0 <= c.position.x - x < wx and 0 <= c.position.y - y < wy:
            if c.position.y - y >= 1 and c.position.x - x - 1 >= 0:
                window[c.position.y - y][c.position.x - x - 1] = [__rgb(c.colors[0], c.colors[1], c.d), c.id_ + window[c.position.y - y][c.position.x - x - 1][1], c.colors] 
        if 0 <= c.position.x - y < wx and 0 <= c.position.y - x < wy:
            if c.position.y - x >= 1 and c.position.x - y - 1 >= 0:
                window[c.position.y - x][c.position.x - y - 1] = [__rgb(c.colors[0], c.colors[1], c.d), c.id_ + window[c.position.y - x][c.position.x - y - 1][1], c.colors]
        if 0 <= c.position.x + y < wx and 0 <= c.position.y - x < wy:
            if c.position.y - x >= 1 and c.position.x + y - 1 < wx:
                window[c.position.y - x][c.position.x + y - 1] = [__rgb(c.colors[0], c.colors[1], c.d), c.id_ + window[c.position.y - x][c.position.x + y - 1][1], c.colors]
        if 0 <= c.position.x + x < wx - 1 and 0 <= c.position.y - y < wy:
            if c.position.y - y >= 1 and c.position.x + x - 1 < wx:
                window[c.position.y - y][c.position.x + x - 1] = [__rgb(c.colors[0], c.colors[1], c.d), c.id_ + window[c.position.y - y][c.position.x + x - 1][1], c.colors]

        y += 1

        if radius_error < 0:
            radius_error += 2 * y + 1
        else:
            x -= 1
            radius_error += 2 * (y - x + 1)
    return window

def graph(wx:int, wy:int, points:list, all:list[str, list[str], tuple], back:list|None=None):
    window = {}
    i = wy

    if back == None:
        while i != 0:
            row = [all] * wx
            window[i] = row
            i -= 1
    if back is not None:
        while i != 0:
            for arg in back:
                window[i] = arg
                i -= 1
                
    for p in points:
        if type(p) == Point:
            if p.x <= wx and p.x >= 1 and p.y <= wy and p.y >= 1: 
                window[p.y][p.x-1] = [__rgb(p.colors[0], p.colors[1], p.d), p.id_ + window[p.y][p.x-1][1], p.colors]
            else:
                pass
        if type(p) == Line:
            window = __draw_line(p, wx, wy, window)
        if type(p) == Square:
            xi = p.pi.x
            yi = p.pi.y

            while xi <= p.pf.x:
                window[p.pi.y][xi-1] = [__rgb(p.colors[0], p.colors[1], p.d), p.id_ + window[p.pi.y][xi-1][1], p.colors]
                window[p.pf.y][xi-1] = [__rgb(p.colors[0], p.colors[1], p.d), p.id_ + window[p.pf.y][xi-1][1], p.colors]
                xi += 1

            while yi <= p.pf.y:
                window[yi][p.pi.x-1] = [__rgb(p.colors[0], p.colors[1], p.d), p.id_ + window[yi][p.pi.x-1][1], p.colors]
                window[yi][p.pf.x-1] = [__rgb(p.colors[0], p.colors[1], p.d), p.id_ + window[yi][p.pf.x-1][1], p.colors]
                yi += 1
        if type(p) == Text:
            x = p.position.x

            try:
                for char in list(p.text):
                    window[p.position.y][x-1] = [__rgb(p.colors[0], p.colors[1], char), p.id_ + window[p.position.y][x-1][1], p.colors]
                    x += 1
            except IndexError:
                pass
        if type(p) == Circle:
            window = __draw_circle(p, wx, wy, window)

    return window