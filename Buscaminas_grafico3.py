import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox
from datetime import datetime
import random

class Casilla:
    def __init__(self, valor=0):
        self.valor = valor
        self.apretada = False
        self.marcada_bandera = False
        self.bomba = False
        self.boton = None # Nuevo atributo para almacenar el botón asociado a la casilla

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
            cls._instance.gano = False
            cls._instance.perdio = False
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
        self.casillas = [[Casilla() for _ in range(self.columnas)] for _ in range(self.filas)]
        self.casilla_apretada = 0
        self.casilla_bandera = 0
        self.cronometro = None
        self.gano = False
        self.perdio = False
        self.colocar_minas()

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
                if not self.tablero.perdio:
                    self.revelar_bombas()
                return False
            elif casilla.valor == 0:
                self.descubrir_casillas_vecinas(fila, columna)
            if self.tablero.casilla_apretada == self.tablero.casilla_total - self.tablero.contador_minas:
                self.tablero.gano = True
                self.revelar_bombas()
                return True
        return None

    def revelar_bombas(self):
        for i in range(self.tablero.filas):
            for j in range(self.tablero.columnas):
                if self.tablero.casillas[i][j].valor == -1:
                    self.revelar_bomba(i, j)

    def revelar_bomba(self, fila, columna):
        self.tablero.casillas[fila][columna].descubrir()
        self.actualizar_interfaz()

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
                boton = tk.Button(self.ventana, width=4, height=2)
                boton.grid(row=i, column=j)
                self.juego.tablero.casillas[i][j].boton = boton
                boton.casilla = self.juego.tablero.casillas[i][j]
                boton.bind('<Button-1>', lambda event, i=i, j=j: self.clic_izquierdo(event, i, j))
                boton.bind('<Button-3>', lambda event, i=i, j=j: self.clic_derecho(event, i, j))

        # Agregar botones para reiniciar y cambiar dificultad
        reiniciar_button = tk.Button(self.ventana, text="Reiniciar", command=self.reiniciar_juego)
        reiniciar_button.grid(row=self.juego.tablero.filas, column=0, columnspan=self.juego.tablero.columnas, sticky='we')

        dificultad_button = tk.Button(self.ventana, text="Cambiar Dificultad", command=self.cambiar_dificultad)
        dificultad_button.grid(row=self.juego.tablero.filas + 1, column=0, columnspan=self.juego.tablero.columnas, sticky='we')

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
                boton = casilla.boton
                if casilla.apretada:
                    boton.config(state=tk.DISABLED, text=str(casilla.valor))
                elif casilla.marcada_bandera:
                    boton.config(text='🚩')
                elif casilla.valor == -1 and not casilla.apretada:
                    boton.config(text='💣')
                else:
                    boton.config(text='')

        if self.juego.tablero.perdio:
            self.juego.fin_del_juego()
        elif self.juego.tablero.gano:
            self.juego.victoria_del_juego()

    def reiniciar_juego(self):
        self.juego.reiniciar_partida()
        self.limpiar_interfaz()
        self.actualizar_interfaz()

    def cambiar_dificultad(self):
        #dificultad = tk.simpledialog.askstring("Cambiar Dificultad", "Ingrese la dificultad (facil, intermedio, dificil):")
        dificultad = simpledialog.askstring("Cambiar Dificultad", "Ingrese la dificultad (facil, intermedio, dificil):")
        if dificultad:
            if dificultad.lower() == 'facil':
                self.juego.establecer_dificultad(filas=5, columnas=5, num_minas=5)
            elif dificultad.lower() == 'intermedio':
                self.juego.establecer_dificultad(filas=7, columnas=7, num_minas=10)
            elif dificultad.lower() == 'dificil':
                self.juego.establecer_dificultad(filas=10, columnas=10, num_minas=20)
            self.reiniciar_juego()

    def limpiar_interfaz(self):
        def limpiar_interfaz(self):
            for i in range(self.juego.tablero.filas):
                for j in range(self.juego.tablero.columnas):
                    if self.juego.tablero.casillas[i][j].boton is not None:
                        self.juego.tablero.casillas[i][j].boton.config(state=tk.NORMAL, text='')

if __name__ == "__main__":
    dificultad = tk.simpledialog.askstring("Seleccionar Dificultad", "Ingrese la dificultad (facil(1), intermedio(2), dificil(3)):")
    filas, columnas, num_minas = 0, 0, 0

    if dificultad == "1":
        filas, columnas, num_minas = 5, 5, 3
    elif dificultad == "2":
        filas, columnas, num_minas = 7, 7, 10
    elif dificultad == "3":
        filas, columnas, num_minas = 10, 10, 15
    else:
        print("Dificultad no válida. Estableciendo dificultad por defecto.")
        filas, columnas, num_minas = 8, 8, 12

    juego = Juego(filas=filas, columnas=columnas, num_minas=num_minas)
    juego.partida()
    interfaz = InterfazGrafica(juego)
    interfaz.ventana.mainloop()

