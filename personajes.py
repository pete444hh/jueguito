"""Clases de Guardians of the Ancient Kingdom.

Aquí solo se define cómo funciona el sistema. Las pruebas y la
ejecución están en main.py, así que importar este archivo no imprime nada.
"""
from abc import ABC, abstractmethod


def _es_entero(valor):
    # bool es subclase de int en Python, así que True/False los dejo fuera a propósito
    return isinstance(valor, int) and not isinstance(valor, bool)


class Personaje(ABC):
    """Clase base abstracta: lo que tienen en común todos los guardianes."""

    VIDA_MAXIMA = 100

    def __init__(self, nombre, vida, ataque, defensa):
        # uso los setters para que el constructor valide igual que cualquier cambio posterior
        self.nombre = nombre
        self.vida = vida
        self.ataque = ataque
        self.defensa = defensa

    # ---------- getters y setters con validación ----------

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not isinstance(valor, str):
            raise TypeError("El nombre debe ser un texto")
        if not valor.strip():
            raise ValueError("El nombre no puede estar vacío")
        self._nombre = valor.strip()

    @property
    def vida(self):
        return self._vida

    @vida.setter
    def vida(self, valor):
        if not _es_entero(valor):
            raise TypeError("La vida debe ser un número entero")
        if not 0 <= valor <= self.VIDA_MAXIMA:
            raise ValueError(f"La vida debe estar entre 0 y {self.VIDA_MAXIMA}")
        self._vida = valor

    @property
    def ataque(self):
        return self._ataque

    @ataque.setter
    def ataque(self, valor):
        if not _es_entero(valor):
            raise TypeError("El ataque debe ser un número entero")
        if valor <= 0:
            raise ValueError("El ataque debe ser positivo")
        self._ataque = valor

    @property
    def defensa(self):
        return self._defensa

    @defensa.setter
    def defensa(self, valor):
        if not _es_entero(valor):
            raise TypeError("La defensa debe ser un número entero")
        if valor < 0:
            raise ValueError("La defensa no puede ser negativa")
        self._defensa = valor

    # ---------- comportamiento común ----------

    def recibir_danio(self, cantidad):
        """Resta vida y devuelve el daño que realmente se aplicó.

        El daño ya llega calculado (con la defensa descontada), aquí no se vuelve a restar.
        """
        if not _es_entero(cantidad):
            raise TypeError("El daño debe ser un número entero")
        if cantidad < 0:
            raise ValueError("El daño no puede ser negativo")

        # si el golpe es mayor que la vida que queda, solo se descuenta lo que había
        danio_efectivo = min(cantidad, self._vida)
        self._vida -= danio_efectivo
        return danio_efectivo

    def esta_vivo(self):
        return self._vida > 0

    def mostrar_estado(self):
        return (f"{self.nombre} ({self.__class__.__name__}) | "
                f"Vida: {self.vida}/{self.VIDA_MAXIMA} | "
                f"Ataque: {self.ataque} | Defensa: {self.defensa}")

    def _validar_ataque(self, objetivo):
        # revisiones que comparten las tres subclases, para no repetirlas en cada atacar()
        if not isinstance(objetivo, Personaje):
            raise TypeError("El objetivo debe ser un Personaje")
        if objetivo is self:
            raise ValueError("Un personaje no puede atacarse a sí mismo")
        if not self.esta_vivo():
            raise ValueError(f"{self.nombre} está derrotado y no puede atacar")
        if not objetivo.esta_vivo():
            raise ValueError(f"{objetivo.nombre} ya está derrotado")

    @abstractmethod
    def atacar(self, objetivo):
        """Cada subclase calcula su daño a su manera. Devuelve el daño efectivo."""


class Guerrero(Personaje):
    """Golpe poderoso: +20% de ataque antes de restar la defensa."""

    def atacar(self, objetivo):
        self._validar_ataque(objetivo)
        # el 20% lo hago con enteros (// redondea hacia abajo) para no tener líos con los flotantes
        ataque_potenciado = self.ataque * 120 // 100
        danio = max(0, ataque_potenciado - objetivo.defensa)
        return objetivo.recibir_danio(danio)


class Mago(Personaje):
    """Hechizo penetrante: ignora la defensa del objetivo."""

    def atacar(self, objetivo):
        self._validar_ataque(objetivo)
        return objetivo.recibir_danio(self.ataque)


class Arquero(Personaje):
    """Disparo crítico: si el ataque supera la defensa, el daño se duplica."""

    def atacar(self, objetivo):
        self._validar_ataque(objetivo)
        if self.ataque > objetivo.defensa:
            danio = (self.ataque - objetivo.defensa) * 2
        else:
            danio = 0
        return objetivo.recibir_danio(danio)


class Combate:
    """Administra el enfrentamiento entre dos personajes que ya existen (agregación)."""

    MAX_RONDAS = 50

    def __init__(self, personaje1, personaje2):
        for p in (personaje1, personaje2):
            if not isinstance(p, Personaje):
                raise TypeError("Los participantes deben ser Personajes")
        if personaje1 is personaje2:
            raise ValueError("Un combate necesita dos personajes distintos")
        if not (personaje1.esta_vivo() and personaje2.esta_vivo()):
            raise ValueError("Los dos participantes deben estar vivos para empezar")

        self._participantes = [personaje1, personaje2]
        self._turno = 0          # índice de quien ataca ahora
        self._rondas = 0
        self._ganador = None
        self._resultado = None   # "victoria", "empate_tecnico" o "empate_rondas"

    @property
    def ganador(self):
        return self._ganador

    @property
    def resultado(self):
        return self._resultado

    @property
    def rondas(self):
        return self._rondas

    def cambiar_turno(self):
        self._turno = 1 - self._turno

    def verificar_ganador(self):
        """Devuelve al ganador si ya hay uno, o None si el combate sigue."""
        a, b = self._participantes
        if not a.esta_vivo():
            self._ganador = b
        elif not b.esta_vivo():
            self._ganador = a
        return self._ganador

    def iniciar(self):
        if self._resultado is not None:
            raise RuntimeError("Este combate ya terminó")

        a, b = self._participantes
        print(f"¡Comienza el combate: {a.nombre} vs {b.nombre}!")
        print("  " + a.mostrar_estado())
        print("  " + b.mostrar_estado())

        while self._resultado is None:
            self._rondas += 1
            print(f"\n--- Ronda {self._rondas} ---")
            danio_ronda = 0

            # una ronda = un ataque de cada uno
            for _ in range(2):
                atacante = self._participantes[self._turno]
                objetivo = self._participantes[1 - self._turno]

                # no pregunto qué tipo de personaje es: cada uno sabe cómo atacar (polimorfismo)
                danio = atacante.atacar(objetivo)
                danio_ronda += danio

                print(f"{atacante.nombre} ataca a {objetivo.nombre} y le causa {danio} de daño")
                print("  " + a.mostrar_estado())
                print("  " + b.mostrar_estado())

                if self.verificar_ganador() is not None:
                    self._resultado = "victoria"
                    break
                self.cambiar_turno()

            # si nadie ganó en esta ronda, reviso si toca terminar en empate
            if self._resultado is None:
                if danio_ronda == 0:
                    self._resultado = "empate_tecnico"
                elif self._rondas >= self.MAX_RONDAS:
                    self._resultado = "empate_rondas"

        self.mostrar_resultado()
        return self._ganador

    def mostrar_resultado(self):
        print("\n=== Resultado final ===")
        if self._resultado == "victoria":
            print(f"Ganador: {self._ganador.nombre} (le quedan {self._ganador.vida} de vida)")
        elif self._resultado == "empate_tecnico":
            print(f"Empate técnico: en la ronda {self._rondas} nadie recibió daño")
        elif self._resultado == "empate_rondas":
            print(f"Empate: se completaron {self.MAX_RONDAS} rondas sin ganador")
        else:
            print("El combate todavía no ha terminado")
