"""Genera un tablero con bombas, se pueden descubir casillas y poner banderas,
pero las bombas se muestran luego del primer clic izquierdo."""

import random
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

class Casilla:
    def __init__(self, valor=0):
        self.valor = valor
        self.apretada = False
        self.marcada_bandera = False
        self.bomba = False  # Nuevo atributo para indicar si la casilla contiene una bomba

    def descubrir(self):
        self.apretada = True

class Tablero:
    _instance = None

    def __new__(cls, filas, columnas, num_minas):
        if cls._instance is None:
            cls._instance = super(Tablero, cls).__new__(cls)
            cls._instance.filas = filas
            cls._instance.columnas = columnas
            cls._instance.casillas = [[Casilla() for _ in range(columnas)] for _ in range(filas)]
            cls._instance.contador_minas = num_minas
            cls._instance.casilla_total = filas * columnas
            cls._instance.casilla_apretada = 0
            cls._instance.casilla_bandera = 0
            cls._instance.cronometro = None
            cls._instance.colocar_minas()
        return cls._instance

    def colocar_minas(self):
        minas_colocadas = 0
        while minas_colocadas < self.contador_minas:
            fila = random.randint(0, self.filas - 1)
            columna = random.randint(0, self.columnas - 1)
            if not self.casillas[fila][columna].valor == -1:
                self.casillas[fila][columna].valor = -1
                minas_colocadas += 1

    def contar_minas_alrededor(self, fila, columna):
        contador = 0
        for i in range(max(0, fila - 1), min(self.filas, fila + 2)):
            for j in range(max(0, columna - 1), min(self.columnas, columna + 2)):
                if self.casillas[i][j].valor == -1:
                    contador += 1
        return contador

    def inicializar_tablero(self):
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
        self.gano = False  # Nuevo atributo para controlar si se ganó
        self.perdio = False  # Nuevo atributo para controlar si se perdió

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
                if not self.tablero.perdio:  # Solo si no se ha perdido antes
                    self.revelar_bombas()  # Revelar bombas solo si ya se ha perdido
                return False  # Fin del juego (mina descubierta)
            elif casilla.valor == 0:
                self.descubrir_casillas_vecinas(fila, columna)
            if self.tablero.casilla_apretada == self.tablero.casilla_total - self.tablero.contador_minas:
                self.tablero.gano = True  # Marcar que se ha ganado el juego
                self.revelar_bombas()  # Revelar bombas al ganar
                return True  # Ganó el juego (todas las casillas sin minas fueron descubiertas)
        return None  # Continuar jugando

    def revelar_bombas(self):
        for i in range(self.tablero.filas):
            for j in range(self.tablero.columnas):
                if self.tablero.casillas[i][j].valor == -1:
                    self.revelar_bomba(i, j)

    def revelar_bomba(self, fila, columna):
        self.tablero.casillas[fila][columna].descubrir()
        self.actualizar_interfaz()  # Actualizar la interfaz después de revelar una bomba

    def descubrir_casillas_vecinas(self, fila, columna):
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

    def fin_del_juego(self):
        messagebox.showinfo("Fin del juego", "¡Has perdido!")
        self.tablero.reiniciar()

    def victoria_del_juego(self):
        tiempo_transcurrido = datetime.now() - self.tablero.cronometro
        messagebox.showinfo("Victoria", f"¡Has ganado!\nTiempo: {tiempo_transcurrido}")
        self.tablero.reiniciar()

class InterfazGrafica:
    def __init__(self, juego):
        self.juego = juego
        self.ventana = tk.Tk()
        self.ventana.title("Buscaminas")
        self.inicializar_interfaz()

    def inicializar_interfaz(self):
        for i in range(self.juego.tablero.filas):
            for j in range(self.juego.tablero.columnas):
                # Crear botón y asignar función de clic izquierdo y derecho
                boton = tk.Button(self.ventana, width=4, height=2)
                boton.grid(row=i, column=j)
                # Guardar el botón en el juego para poder accederlo más tarde
                self.juego.tablero.casillas[i][j].boton = boton
                # Asociar eventos de clic izquierdo y derecho al botón
                boton.bind('<Button-1>', lambda event, i=i, j=j: self.clic_izquierdo(event, i, j))
                boton.bind('<Button-3>', lambda event, i=i, j=j: self.clic_derecho(event, i, j))

    def clic_izquierdo(self, event, fila, columna):
        self.juego.descubrir_casilla(fila, columna)
        self.actualizar_interfaz()

    def clic_derecho(self, event, fila, columna):
        self.juego.poner_bandera(fila, columna)
        self.actualizar_interfaz()

    def actualizar_interfaz(self):
        for i in range(self.juego.tablero.filas):
            for j in range(self.juego.tablero.columnas):
                casilla = self.juego.tablero.casillas[i][j]
                boton = casilla.boton  # Acceder al botón guardado en el juego
                if casilla.apretada:
                    boton.config(state=tk.DISABLED, text=str(casilla.valor))
                elif casilla.marcada_bandera:
                    boton.config(text='🚩')
                elif casilla.valor == -1 and not casilla.apretada:
                    boton.config(text='💣')
                else:
                    boton.config(text='')

if __name__ == "__main__":
    juego = Juego(filas=8, columnas=8, num_minas=10)
    juego.partida()
    interfaz = InterfazGrafica(juego)
    interfaz.ventana.mainloop()
