import sys, pygame, time, math, cmath, random
from shapely.geometry import Polygon, Point


class App():
    def __init__(self, **kwargs):
        pygame.init()
        global SIZE
        SIZE  = 600, 400
        self.FPS = 50
        self.last_time = time.time()
        self.screen = pygame.display.set_mode(SIZE)
        self.peliLoppu = False

        self.levelStartTime = pygame.time.get_ticks()
        if 'level' in kwargs:
            self.level = kwargs['level']
            self.score = kwargs['score']
            self.asteroidienMäärä = self.asteroidienMäärä * 2
        else:
            self.score = 0
            self.level = 1
            self.asteroidienMäärä = 5

        self.avaruus = Avaruus(self.asteroidienMäärä)

        pygame.display.set_caption('Asteroids')

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.nollaaNäyttö()
            self.piirräAlus()
            self.piirräAsteroidit()
            self.piirräAmmukset()

            self.new_time = time.time()
            self.sleep_time = ((1000.0 / self.FPS) - (self.new_time - self.last_time)) / 1000.0
            if self.sleep_time > 0:
                time.sleep(self.sleep_time)
            self.last_time = self.new_time

            self.keyPressed()

            self.avaruus.alus.liiku()
            self.avaruus.alus.kentänSisällä()
            self.avaruus.liikutaAmmukset()
            self.avaruus.liikutaAsteroidit()
            self.avaruus.asteroiditKentänSisällä()

            if self.avaruus.asteroidinJaAluksenTörmäys():
                self.peliLoppu = True
                font = pygame.font.SysFont("monospace", 25)
                label = font.render("Peli ohi!", 1, (255, 0, 0))
                label2 = font.render("Enter - uusi peli", 1, (255, 0, 0))
                self.screen.blit(label, (300, 200))
                self.screen.blit(label2, (300, 250))
                keys = pygame.key.get_pressed()
                if keys[pygame.K_RETURN]:
                    self.__init__()

            if self.avaruus.ammuksenJaAsteroidinTörmäys():
                self.score += 1

            font = pygame.font.SysFont("monospace", 25)
            label = font.render(f"Score: {self.score}", 1, (255, 0, 0))
            self.screen.blit(label, (20, 20))

            levelEndTime = pygame.time.get_ticks()
            if levelEndTime - self.levelStartTime < 3000:
                label2 = font.render(f'level {self.level}', 1, (255, 0, 0))
                self.screen.blit(label2, (200, 200))

            if self.avaruus.asteroiditTuhottu():
                self.__init__(level = self.level+1, score = self.score)

            pygame.display.update()


    def keyPressed(self):

        if self.peliLoppu:
            return

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            kulma = self.avaruus.alus.kulma -  5
            if kulma < 0:
                kulma = 355
            self.avaruus.alus.kulma = kulma


        if keys[pygame.K_RIGHT]:
            kulma = self.avaruus.alus.kulma +  5
            if kulma == 360:
                kulma = 0
            self.avaruus.alus.kulma = kulma

        if keys[pygame.K_UP]:
            self.avaruus.alus.nopeus += 0.01

        if keys[pygame.K_DOWN]:
            self.avaruus.alus.nopeus = 0

        if keys[pygame.K_SPACE]:
            start = self.avaruus.ammuksenLuontihetki
            end = time.time()
            if(end - start > 1):
                self.avaruus.lisääAmmus()

    def piirräAlus(self):
        harmaa = (100, 100, 100)
        pygame.draw.polygon(self.screen, harmaa, self.avaruus.alus.koordinaatit)

    def piirräAsteroidit(self):
        keltainen = (255, 255, 0)
        for asteroidi in self.avaruus.asteroidit:
            pygame.draw.polygon(self.screen, keltainen, asteroidi.koordinaatit)

    def piirräAmmukset(self):
        punainen  = (255, 0, 0) #punainen
        for ammus in self.avaruus.ammukset:
            pygame.draw.circle(self.screen, punainen, (int(ammus.x), int(ammus.y)), ammus.säde)

    def nollaaNäyttö(self):
        self.screen.fill((0, 0, 0))

class Avaruus():
    # Pitää kirjaa avaruusobjekteista (alus, asteroidit ja ammukset)
    # ja hallitsee niiden toiminnallisuutta

    def __init__(self, asteroidienMäärä):
        self.asteroidienMäärä = asteroidienMäärä
        self.alus = Alus(300, 200)
        self.asteroidit = self.generoiAsteroidit()
        self.ammukset = []
        self.ammuksenLuontihetki = 0

    def generoiAsteroidit(self):
        asteroidit = []
        for i in range(self.asteroidienMäärä):
            koordinaatit = []
            for i in range(5):
                x = random.randint(100, 120)
                y = random.randint(100, 120)
                koordinaatit.append((x, y))
            asteroidit.append(Asteroidi(koordinaatit))
        return asteroidit

    def lisääAmmus(self):
        ammus = Ammus(self.alus)
        self.ammukset.append(ammus)
        self.ammuksenLuontihetki = 0

    def liikutaAsteroidit(self):
        for asteroidi in self.asteroidit:
            asteroidi.liiku()

    def liikutaAmmukset(self):
        for ammus in self.ammukset:
            ammus.liiku()

    def asteroiditKentänSisällä(self):
        for asteroidi in self.asteroidit:
            asteroidi.kentänSisällä()

    def asteroidinJaAluksenTörmäys(self):
        for asteroidi in self.asteroidit:
            if asteroidi.polygon.intersects(self.alus.polygon):
                for asteroidi in self.asteroidit:
                    asteroidi.nopeusX = 0
                    asteroidi.nopeusY = 0
                    self.alus.nopeus = 0
                return True
        return False

    def ammuksenJaAsteroidinTörmäys(self):
        for asteroidi in self.asteroidit:
            for ammus in self.ammukset:
                if asteroidi.polygon.intersects(ammus.circle):
                    self.asteroidit.remove(asteroidi)
                    return True
        return False

    def asteroiditTuhottu(self):
        if len(self.asteroidit) == 0:
            self.alus.nopeus = 0
            return True
        return False



class Avaruusobjekti(Avaruus):

    def __init__(self, x, y):
        self.x0 = self.x = x
        self.y0 = self.y = y
        self.dx = self.dy = 0
        self.koordinaatit = [(self.x, self.y - 20),
                             (self.x + 10, self.y + 20), (self.x - 10, self.y + 20)]
        self.polygon = Polygon(self.koordinaatit)
        self.kulma = 0
        self.nopeus = 0
        self.kaannoksetCache = {}
        for i in range(360):
            self.kaannoksetCache[i] = self.kaanny(i)

    def kaanny(self, kulma):
        kompleksikulma = cmath.exp(math.radians(kulma) * 1j)
        keskipiste = complex(self.x, self.y)
        koordinaatit = []
        for i, (x, y) in enumerate(self.koordinaatit):
            v = kompleksikulma * (complex(x, y) - keskipiste) + keskipiste
            koordinaatit.append((v.real, v.imag))
        return koordinaatit

    def liiku(self):
        # aluksen asentokoordinaatit pisteessä x0, y0
        self.koordinaatit = self.kaannoksetCache[self.kulma]
        # aluksen asentokoordinaatit pisteessä x, y
        self.dx = self.x - self.x0
        self.dy = self.y - self.y0
        xArvot = list(map(lambda a: a[0] + self.dx, self.koordinaatit))
        yArvot = list(map(lambda a: a[1] + self.dy, self.koordinaatit))
        self.koordinaatit = list(zip(xArvot, yArvot))
        # aluksen keulan suuntainen muutos
        self.dx = self.nopeus * (self.kaannoksetCache[self.kulma][0][0] - self.x0)
        self.dy = self.nopeus * (self.kaannoksetCache[self.kulma][0][1] - self.y0)
        # uudet koordinaatit
        self.x += self.dx
        self.y += self.dy
        xArvot = list(map(lambda a: a[0] + self.dx, self.koordinaatit))
        yArvot = list(map(lambda a: a[1] + self.dy, self.koordinaatit))
        self.koordinaatit = list(zip(xArvot, yArvot))
        self.polygon = Polygon(self.koordinaatit)

    def kentänSisällä(self):
        if self.x > SIZE[0]:
            self.x = 0
            self.dx = -SIZE[0]
            self.dy = 0
            xArvot = list(map(lambda a: a[0] + self.dx, self.koordinaatit))
            yArvot = list(map(lambda a: a[1] + self.dy, self.koordinaatit))
            self.koordinaatit = list(zip(xArvot, yArvot))

        if self.x < 0:
            self.x = SIZE[0]
            self.dx = SIZE[0]
            self.dy = 0
            xArvot = list(map(lambda a: a[0] + self.dx, self.koordinaatit))
            yArvot = list(map(lambda a: a[1] + self.dy, self.koordinaatit))
            self.koordinaatit = list(zip(xArvot, yArvot))

        if self.y > SIZE[1]:
            self.y = 0
            self.dx = 0
            self.dy = -SIZE[1]
            xArvot = list(map(lambda a: a[0] + self.dx, self.koordinaatit))
            yArvot = list(map(lambda a: a[1] + self.dy, self.koordinaatit))
            self.koordinaatit = list(zip(xArvot, yArvot))

        if self.y < 0:
            self.y = SIZE[1]
            self.dx = 0
            self.dy = SIZE[1]
            xArvot = list(map(lambda a: a[0] + self.dx, self.koordinaatit))
            yArvot = list(map(lambda a: a[1] + self.dy, self.koordinaatit))
            self.koordinaatit = list(zip(xArvot, yArvot))


class Alus(Avaruusobjekti):

    def __init__(self, x, y):
        Avaruusobjekti.__init__(self, x, y)


class Asteroidi(Avaruusobjekti):

    def __init__(self, koordinaatit):
        self.x = 100
        self.y = 100
        super().__init__(self.x, self.y)
        self.koordinaatit = koordinaatit
        self.nopeusX = random.uniform(-1.5, 1.5)
        self.nopeusY = random.uniform(-1.5, 1.5)

    def liiku(self):
        dx = self.nopeusX
        dy = self.nopeusY
        # uudet koordinaatit
        self.x += dx
        self.y += dy
        xArvot = list(map(lambda a: a[0] + dx, self.koordinaatit))
        yArvot = list(map(lambda a: a[1] + dy, self.koordinaatit))
        self.koordinaatit = list(zip(xArvot, yArvot))
        self.polygon = Polygon(self.koordinaatit)


class Ammus(Avaruusobjekti):

    def __init__(self, alus):
        self.x = alus.x
        self.y = alus.y
        super().__init__(self.x, self.y)
        self.säde = 5
        # aluksen keulan suuntainen muutos
        self.dx = alus.koordinaatit[0][0] - alus.x
        self.dy = alus.koordinaatit[0][1] - alus.y
        self.circle = Point(self.x, self.y).buffer(5)

    def liiku(self):
        # uudet koordinaatit
        self.x += self.dx
        self.y += self.dy
        self.circle = Point(self.x, self.y).buffer(5)


app = App()