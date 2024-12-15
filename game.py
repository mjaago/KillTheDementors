from http.server import * #HTTP seadete paketi lisamine
import re #Lihtsustatud tekstitöötluse funktsionaalsuse lisamine
import pygame
import threading
from random import randint
import socket
import time
import asyncio
from websockets.server import serve


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)


pygame.init()


size = (1200, 600)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("My Game")
clock = pygame.time.Clock()

def tekst(screen, koordinaadid, sõne):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            import sys
            pygame.quit()
            sys.exit()

    font = pygame.font.SysFont("comicsansms", 49)
    tekst = font.render(sõne, True, WHITE)
    screen.blit(tekst, koordinaadid)
    pygame.display.flip()

class Stick(pygame.sprite.Sprite):
    def __init__(self, image, *groups):
        super(Stick, self).__init__(*groups)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.move_ip(+400, 480)

    def liikumine(self, y):
        if self.can_move(y):
            self.rect.move_ip(y , 0)

    def can_move(self, x):
        # kills sprite when out of bounds.
        if self.rect.x + x < 0 or self.rect.x + x > screen.get_width():
            return False
        return True


class Dementor(pygame.sprite.Sprite):
    def __init__(self, image, pos, *groups):
        super(Dementor, self).__init__(*groups)


        self.image = image
        self.rect = image.get_rect(x=pos[0], y=pos[1])

        self.speed = (0, 0.16)

    def update(self, ms):
        self.check_bounds()
        self.rect.x += self.speed[0] * ms
        self.rect.y += self.speed[1] * ms

    def check_bounds(self):
        # kills sprite when out of bounds.
        if self.rect.x < -10 or self.rect.x > screen.get_width() + 10 or self.rect.y < -10 or self.rect.y > screen.get_height() + 10:
            self.kill()
            global game_over
            game_over = True


class Kuul(pygame.sprite.Sprite):
    def __init__(self, image, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = image.get_rect(x=pos[0], y=pos[1])

        self.speed = (0, -0.1)
    def update(self, ms):
        self.rect.y -= 3

    def check_bounds(self):
        # kills sprite when out of bounds.
        if self.rect.x < -10 or self.rect.x > screen.get_width() + 10 or self.rect.y < -10 or self.rect.y > screen.get_height() + 10:
            self.kill()



magicstick = pygame.image.load("kepp.png")
mängijasuurus = pygame.transform.scale(magicstick, (40, 110))
mängija = Stick(mängijasuurus)
grupp = pygame.sprite.Group()
grupp.add(mängija)
vastased = pygame.sprite.Group()
välk = pygame.sprite.Group()
taust = pygame.image.load("taust2.jpg")
taustasuurus = pygame.transform.scale(taust, size)
can_fire = True


def peli(y, x):
    global algus
    global can_fire

    ajalõpp = round(pygame.time.get_ticks() / 1000)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            import sys
            pygame.quit()
            sys.exit()

    if x >= 1.5 and can_fire:
        img = pygame.image.load("pauk.png")
        suurus = pygame.transform.scale(img,(50, 80))
        välk.add(Kuul(suurus, (mängija.rect[0], 380)))
        can_fire = False
    elif x <= 0:
        can_fire = True

    if ajalõpp - algus == 3:
        pilt = pygame.image.load("dementor.png")
        õigesuurus = pygame.transform.scale(pilt, (100, 100))
        vastased.add(Dementor(õigesuurus, (randint(50, 1150), 10)))
        algus = ajalõpp

    mängija.liikumine(y)

    ms = clock.tick(80)
    screen.blit(taustasuurus, (0,0))

    grupp.update()
    grupp.draw(screen)
    vastased.update(ms)
    välk.update(ms)
    vastased.draw(screen)
    välk.draw(screen)
    pygame.sprite.groupcollide(välk, vastased, True, True)
    pygame.display.flip()


class MyHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global a
        global b
        self.send_response(200)  # Lisatakse vastuse päis
        self.send_header("Content-type", "text/html")  # Päis puhvrisse
        self.end_headers()  # Kirjutatkse puhvris olev info väljundisse
        # Väljundite kirjutamise vormindamine
        if self.path.startswith("/update_servo"):
            # Muutujate määramine
            m = re.search("/update_servo\\?x=([^&]*)&y=(.*)", self.path)
            x = float(m.group(1))
            y = float(m.group(2))
            b = -x
            a = y
        else:  # index faili kirjutamine/lugemine
            f = open("index.html", "rb")
            self.wfile.write(f.read())
            f.close()

def echo(websocket):
    for message in websocket:
        websocket.send(message)

def run_server(server_class=HTTPServer, handler_class=MyHTTPHandler):
    with serve(echo, "localhost", 8081) as server:
        server.serve_forever()

    server_address = ('', 8080)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

# server

a = 0
b = 0
telefon_ühendatud = False
minu_ip = socket.gethostbyname(socket.gethostname())
game_over = False

server_thread = threading.Thread(target=run_server)
server_thread.daemon = True
server_thread.start()

def main(a, b):
    global telefon_ühendatud
    global algus
    global game_over

    if a != 0:
        telefon_ühendatud = True

    if telefon_ühendatud == False:
        algus = round(pygame.time.get_ticks() / 1000)
        tekst(screen, (0, 300), "Sisesta aadressiribale telefonis:" + minu_ip + ":8080")

    elif game_over == True:
        pygame.init()

        size = (1200, 600)
        tagumik = pygame.display.set_mode(size)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                import sys
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_over = False
                    vastased.empty()
                    main(a, b)

        tekst(tagumik, (0, 400), "Vajuta Space, et uuesti mängida")
        pygame.display.flip()
    else:
        peli(a, b)


while True:
    main(a, b)
