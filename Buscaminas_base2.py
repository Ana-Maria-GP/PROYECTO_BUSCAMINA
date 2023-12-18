import random
from datetime import datetime

class Casilla:
    def __init__(self):
        self.valor = 0
        self.apretada = False
        self.marcada_bandera = False

    def descubrir(self):
        self.apretada = True

class Tablero:
    def __init__(self, filas, columnas, num_minas):
        self.filas = filas
        self.columnas = columnas
        self.casillas = [[Casilla() for _ in range(columnas)] for _ in range(filas)]
        self.contador_minas = num_minas
        self.casilla_total = filas * columnas
        self.casilla_apretada = 0
        self.casilla_bandera = 0
        self.cronometro = None

    def colocar_minas(self):
        # Coloca minas aleatoriamente en el tablero
        minas_colocadas = 0
        while minas_colocadas < self.contador_minas:
            fila = random.randint(0, self.filas - 1)
            columna = random.randint(0, self.columnas - 1)
            if not self.casillas[fila][columna].valor == -1:
                self.casillas[fila][columna].valor = -1
                minas_colocadas += 1

    def contar_minas_alrededor(self, fila, columna):
        # Cuenta el número de minas alrededor de una casilla
        contador = 0
        for i in range(max(0, fila - 1), min(self.filas, fila + 2)):
            for j in range(max(0, columna - 1), min(self.columnas, columna + 2)):
                if self.casillas[i][j].valor == -1:
                    contador += 1
        return contador

    def inicializar_tablero(self):
        # Inicializa el tablero colocando minas y calculando los valores de las casillas
        self.colocar_minas()
        for i in range(self.filas):
            for j in range(self.columnas):
                if self.casillas[i][j].valor != -1:
                    self.casillas[i][j].valor = self.contar_minas_alrededor(i, j)

    def reiniciar(self):
        # Reinicia el tablero
        self.casillas = [[Casilla() for _ in range(self.columnas)] for _ in range(self.filas)]
        self.casilla_apretada = 0
        self.casilla_bandera = 0
        self.cronometro = None

class Ranking:
    def __init__(self, nombre, tiempo):
        self.nombre = nombre
        self.tiempo = tiempo

class Juego:
    def __init__(self, filas, columnas, num_minas):
        self.ranking = []
        self.tablero = Tablero(filas, columnas, num_minas)

    def partida(self):
        self.tablero.inicializar_tablero()
        self.tablero.cronometro = datetime.now()

    def descubrir_casilla(self, fila, columna):
        casilla = self.tablero.casillas[fila][columna]
        if not casilla.apretada and not casilla.marcada_bandera:
            casilla.descubrir()
            self.tablero.casilla_apretada += 1
            if casilla.valor == -1:
                return False  # Fin del juego (mina descubierta)
            elif casilla.valor == 0:
                self.descubrir_casillas_vecinas(fila, columna)
            if self.tablero.casilla_apretada == self.tablero.casilla_total - self.tablero.contador_minas:
                return True  # Ganaste el juego (todas las casillas sin minas fueron descubiertas)
        return None  # Continuar jugando

    def descubrir_casillas_vecinas(self, fila, columna):
        # Descubre las casillas vecinas si la casilla actual es vacía
        for i in range(max(0, fila - 1), min(self.tablero.filas, fila + 2)):
            for j in range(max(0, columna - 1), min(self.tablero.columnas, columna + 2)):
                if not self.tablero.casillas[i][j].apretada:
                    self.descubrir_casilla(i, j)

    def poner_bandera(self, fila, columna):
        casilla = self.tablero.casillas[fila][columna]
        if not casilla.apretada:
            if casilla.marcada_bandera:
                casilla.marcada_bandera = False
                self.tablero.casilla_bandera -= 1
            else:
                casilla.marcada_bandera = True
                self.tablero.casilla_bandera += 1

    def reiniciar_partida(self):
        self.tablero.reiniciar()

    def establecer_dificultad(self, filas, columnas, num_minas):
        self.tablero = Tablero(filas, columnas, num_minas)

# Ejemplo de uso:
juego = Juego(filas=8, columnas=8, num_minas=10)
juego.partida()
juego.descubrir_casilla(2, 2)
juego.poner_bandera(3, 3)
juego.reiniciar_partida()
juego.establecer_dificultad(filas=10, columnas=10, num_minas=15)
