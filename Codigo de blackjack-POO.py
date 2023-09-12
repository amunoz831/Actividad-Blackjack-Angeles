import random
from dataclasses import dataclass, field
from typing import ClassVar, Optional, Union

CORAZON = "\u2764\uFE0F"
TREBOL = "\u2663\uFE0F"
DIAMANTE = "\u2666\uFE0F"
ESPADA = "\u2660\uFE0F"
TAPADA = "\u25AE\uFE0F"
FICHAS_INICIALES = 100


@dataclass
class Carta:
    VALORES: ClassVar[list[str]] = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    PINTAS: ClassVar[list[str]] = [CORAZON, TREBOL, DIAMANTE, ESPADA]
    pinta: str
    valor: str
    tapada: bool = field(default=False, init=False)

    def calcular_valor(self, as_como_11=True) -> int:
        if self.valor == "A":
            if as_como_11:
                return 11
            else:
                return 1
        elif self.valor in ["J", "Q", "K"]:
            return 10
        else:
            return int(self.valor)

    def __str__(self):
        if self.tapada:
            return f"{TAPADA}"
        else:
            return f"{self.valor}{self.pinta}"


class Mano:

    def __init__(self, cartas: list[Carta]):
        self.cartas: list[Carta] = []
        self.cartas.extend(cartas)

    def es_blackjack(self) -> bool:
        if len(self.cartas) == 2:
            return self.calcular_valor() == 21
        return False

    def agregar_carta(self, carta: Carta):
        self.cartas.append(carta)

    def calcular_valor(self) -> int:
        valor = sum(carta.calcular_valor() for carta in self.cartas)
        num_as = sum(1 for carta in self.cartas if carta.valor == "A")
        while valor > 21 and num_as > 0:
            valor -= 10
            num_as -= 1
        return valor

    def destapar(self):
        for carta in self.cartas:
            carta.tapada = False

    def limpiar(self):
        self.cartas.clear()

    def __str__(self):
        str_mano = ""
        for carta in self.cartas:
            str_mano += f"{str(carta):^5}"
        return str_mano


class Baraja:

    def __init__(self):
        self.cartas: list[Carta] = [Carta(pinta, valor) for valor in Carta.VALORES for pinta in Carta.PINTAS]

    def reiniciar(self):
        self.cartas = [Carta(pinta, valor) for valor in Carta.VALORES for pinta in Carta.PINTAS]

    def revolver(self):
        random.shuffle(self.cartas)

    def repartir_carta(self, tapada=False) -> Optional[Carta]:
        if len(self.cartas) > 0:
            carta = self.cartas.pop()
            carta.tapada = tapada
            return carta
        else:
            return None


@dataclass
class Jugador:
    nombre: str
    fichas: int
    mano: Optional[Mano] = field(default=None, init=False)

    def inicializar_mano(self, cartas: list[Carta]):
        self.mano = Mano(cartas)

    def recibir_carta(self, carta: Carta):
        self.mano.agregar_carta(carta)

    def agregar_fichas(self, fichas: int):
        self.fichas += fichas

    def tiene_fichas(self) -> bool:
        return self.fichas > 0

    def puede_apostar(self, cantidad: int):
        return self.fichas >= cantidad


class Casa:

    def __init__(self):
        self.mano: Optional[Mano] = None

    def inicializar_mano(self, cartas: list[Carta]):
        self.mano = Mano(cartas)

    def recibir_carta(self, carta: Carta):
        self.mano.agregar_carta(carta)


class Blackjack:

    def __init__(self):
        self.apuesta_actual: int = 0
        self.jugador: Optional[Jugador] = None
        self.casa: Casa = Casa()
        self.baraja: Baraja = Baraja()

    def registrar_jugador(self, nombre: str):
        self.jugador = Jugador(nombre, FICHAS_INICIALES)

    def iniciar_juego(self, apuesta: int):
        self.apuesta_actual = apuesta

        self.baraja.reiniciar()
        self.baraja.revolver()

        if self.jugador.mano is not None:
            self.jugador.mano.limpiar()
            self.casa.mano.limpiar()

        # Repartir la mano del jugador
        carta_1 = self.baraja.repartir_carta()
        carta_2 = self.baraja.repartir_carta()
        self.jugador.inicializar_mano([carta_1, carta_2])

        # Repartir la mano de la casa
        carta_1 = self.baraja.repartir_carta()
        carta_2 = self.baraja.repartir_carta(tapada=True)
        self.casa.inicializar_mano([carta_1, carta_2])

    def repartir_carta_a_jugador(self):
        carta = self.baraja.repartir_carta()
        if carta:
            self.jugador.recibir_carta(carta)
            return True
        return False

    def jugador_perdio(self) -> bool:
        return self.jugador.mano.calcular_valor() > 21

    def destapar_mano_de_la_casa(self):
        self.casa.mano.destapar()

    def casa_puede_pedir(self) -> bool:
        valor_mano_casa = self.casa.mano.calcular_valor()
        return valor_mano_casa <= self.jugador.mano.calcular_valor() and valor_mano_casa <= 16

    def repartir_carta_a_la_casa(self):
        carta = self.baraja.repartir_carta()
        if carta:
            self.casa.recibir_carta(carta)
            return True
        return False

    def jugador_gano(self) -> bool:
        valor_mano_jugador = self.jugador.mano.calcular_valor()
        valor_mano_casa = self.casa.mano.calcular_valor()
        return (
            self.jugador.mano.es_blackjack()
            or (valor_mano_jugador <= 21 and (valor_mano_jugador > valor_mano_casa or valor_mano_casa > 21))
        )

    def casa_gano(self) -> bool:
        valor_mano_jugador = self.jugador.mano.calcular_valor()
        valor_mano_casa = self.casa.mano.calcular_valor()
        return (
            self.casa.mano.es_blackjack()
            or (valor_mano_jugador > 21 or (valor_mano_jugador < valor_mano_casa and valor_mano_casa <= 21))
        )

    def hay_empate(self) -> bool:
        valor_mano_jugador = self.jugador.mano.calcular_valor()
        valor_mano_casa = self.casa.mano.calcular_valor()
        return valor_mano_jugador == valor_mano_casa

    def jugar_ronda(self):
        while not self.jugador_perdio() and self.casa_puede_pedir():
            print("Mano del jugador:")
            print(self.jugador.mano)
            valor_mano_jugador = self.jugador.mano.calcular_valor()
            print(f"Valor de la mano del jugador: {valor_mano_jugador}")

            decision = input("Desea pedir otra carta? (Si o No): ").strip().lower()
            if decision == "si":
                if not self.repartir_carta_a_jugador():
                    print("No se pueden pedir más cartas.")
                else:
                    valor_mano_jugador = self.jugador.mano.calcular_valor()
                    print(f"Nuevo valor de la mano del jugador: {valor_mano_jugador}")
                if self.jugador.mano.es_blackjack():
                    print("El valor de la mano del jugador es 21, ¡gana automáticamente!")
                    return
            else:
                break

        self.destapar_mano_de_la_casa()

        while self.casa_puede_pedir():
            if not self.repartir_carta_a_la_casa():
                break

        print("Mano de la casa:")
        print(self.casa.mano)
        valor_mano_casa = self.casa.mano.calcular_valor()
        print(f"Valor de la mano de la casa: {valor_mano_casa}")

        if self.jugador_gano():
            print(f"El mazo de la mano vale {valor_mano_jugador} y el mazo de la casa vale {valor_mano_casa}, por ende, el jugador gana la ronda.")
            self.jugador.agregar_fichas(self.apuesta_actual)
        elif self.casa_gano():
            self.jugador.mano.calcular_valor()
            print(f"El mazo de la mano vale {valor_mano_jugador} y el mazo de la casa vale {valor_mano_casa}, por ende, la casa gana la ronda.")
            self.jugador.fichas -= self.apuesta_actual
        else:
            print(f"El mazo de la mano vale {valor_mano_jugador} y el mazo de la casa vale {valor_mano_casa}, por ende, hay un empate.")

        self.jugador.mano.limpiar()
        self.casa.mano.limpiar()

if __name__ == "__main__":
    juego = Blackjack()
    nombre_jugador = input("Ingrese su nombre: ")
    juego.registrar_jugador(nombre_jugador)

    while juego.jugador.tiene_fichas():
        apuesta = int(input(f"Fichas disponibles: {juego.jugador.fichas}. Ingrese su apuesta (0 para salir): "))
        if apuesta == 0:
            break

        if juego.jugador.puede_apostar(apuesta):
            juego.iniciar_juego(apuesta)
            juego.jugar_ronda()
        else:
            print("Apuesta no válida. Intente de nuevo.")

    print("Gracias por jugar. ¡Hasta la próxima!")
