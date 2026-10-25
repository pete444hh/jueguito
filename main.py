"""Ejecución del programa y casos de prueba obligatorios.

Uso:  python main.py
"""
import sys

from personajes import Personaje, Guerrero, Mago, Arquero, Combate

resultados = []


def titulo(texto):
    print(f"\n{'=' * 60}\n{texto}\n{'=' * 60}")


def comprobar(descripcion, condicion):
    resultados.append(bool(condicion))
    print(f"  [{'OK' if condicion else 'FALLO'}] {descripcion}")


def lanza(excepcion, funcion):
    """True si funcion() lanza la excepción esperada."""
    try:
        funcion()
    except excepcion:
        return True
    return False


def main():
    # 1. Creación correcta
    titulo("1. Creación de los tres tipos de personajes")
    arthas = Guerrero("Arthas", 100, 30, 20)
    gandalf = Mago("Gandalf", 80, 40, 10)
    legolas = Arquero("Legolas", 90, 35, 15)
    for p in (arthas, gandalf, legolas):
        print("  " + p.mostrar_estado())
    comprobar("Se crearon Guerrero, Mago y Arquero",
              isinstance(arthas, Guerrero) and isinstance(gandalf, Mago) and isinstance(legolas, Arquero))
    comprobar("Los tres son Personaje",
              all(isinstance(p, Personaje) for p in (arthas, gandalf, legolas)))
    comprobar("Personaje (abstracta) no se puede instanciar",
              lanza(TypeError, lambda: Personaje("X", 10, 10, 10)))

    # 2. Vida inválida
    titulo("2. Rechazo de vida superior a 100 o negativa")
    comprobar("Vida 101 -> ValueError", lanza(ValueError, lambda: Guerrero("A", 101, 10, 5)))
    comprobar("Vida -1 -> ValueError", lanza(ValueError, lambda: Guerrero("A", -1, 10, 5)))
    comprobar("Vida 'cien' -> TypeError", lanza(TypeError, lambda: Guerrero("A", "cien", 10, 5)))

    # 3. Nombre vacío
    titulo("3. Rechazo de nombres vacíos")
    comprobar("Nombre '' -> ValueError", lanza(ValueError, lambda: Mago("", 50, 10, 5)))
    comprobar("Nombre '   ' -> ValueError", lanza(ValueError, lambda: Mago("   ", 50, 10, 5)))
    comprobar("Nombre 123 -> TypeError", lanza(TypeError, lambda: Mago(123, 50, 10, 5)))

    # 4. Ataque y defensa inválidos
    titulo("4. Rechazo de ataques y defensas inválidos")
    comprobar("Ataque 0 -> ValueError", lanza(ValueError, lambda: Arquero("A", 50, 0, 5)))
    comprobar("Ataque -5 -> ValueError", lanza(ValueError, lambda: Arquero("A", 50, -5, 5)))
    comprobar("Ataque 'fuerte' -> TypeError", lanza(TypeError, lambda: Arquero("A", 50, "fuerte", 5)))
    comprobar("Defensa -1 -> ValueError", lanza(ValueError, lambda: Arquero("A", 50, 10, -1)))
    comprobar("Defensa 3.5 -> TypeError", lanza(TypeError, lambda: Arquero("A", 50, 10, 3.5)))
    comprobar("Defensa 0 sí es válida", Arquero("A", 50, 10, 0).defensa == 0)

    # 5. Habilidad del Guerrero
    titulo("5. Golpe poderoso del Guerrero (30 de ataque vs 10 de defensa)")
    guerrero = Guerrero("Guerrero", 100, 30, 20)
    objetivo = Mago("Objetivo", 100, 10, 10)
    danio = guerrero.atacar(objetivo)
    print(f"  Daño causado: {danio}, vida del objetivo: {objetivo.vida}")
    comprobar("Daño = 26", danio == 26)
    comprobar("Vida del objetivo = 74", objetivo.vida == 74)

    # 6. Habilidad del Mago
    titulo("6. Hechizo penetrante del Mago (40 de ataque vs 20 de defensa)")
    mago = Mago("Mago", 100, 40, 5)
    objetivo = Guerrero("Objetivo", 100, 10, 20)
    danio = mago.atacar(objetivo)
    print(f"  Daño causado: {danio}, vida del objetivo: {objetivo.vida}")
    comprobar("Daño = 40 (ignora la defensa)", danio == 40)

    # 7. Habilidad del Arquero
    titulo("7. Disparo crítico del Arquero")
    arquero = Arquero("Arquero", 100, 35, 5)
    objetivo = Guerrero("Objetivo", 100, 10, 15)
    danio = arquero.atacar(objetivo)
    print(f"  35 de ataque vs 15 de defensa -> daño {danio}")
    comprobar("Daño = 40 (20 base x 2)", danio == 40)
    blindado = Guerrero("Blindado", 100, 10, 35)
    danio = arquero.atacar(blindado)
    print(f"  35 de ataque vs 35 de defensa -> daño {danio}")
    comprobar("Si el ataque no supera la defensa, el daño es 0", danio == 0)

    # 8. Vida nunca negativa
    titulo("8. Imposible tener vida negativa")
    debil = Guerrero("Débil", 20, 10, 5)
    efectivo = debil.recibir_danio(50)
    print(f"  Recibió 50 de daño con 20 de vida -> efectivo {efectivo}, vida {debil.vida}")
    comprobar("Vida = 0 (no -30)", debil.vida == 0)
    comprobar("Daño efectivo = 20", efectivo == 20)
    comprobar("Ya no está vivo", not debil.esta_vivo())
    comprobar("Daño negativo -> ValueError", lanza(ValueError, lambda: arthas.recibir_danio(-5)))
    comprobar("Poner vida -10 con el setter -> ValueError", lanza(ValueError, lambda: setattr(arthas, "vida", -10)))

    # 9. Derrotado no ataca
    titulo("9. Un personaje derrotado no puede atacar")
    caido = Mago("Caído", 10, 10, 5)
    vivo = Guerrero("Vivo", 100, 10, 5)
    caido.recibir_danio(10)
    comprobar("Atacante derrotado -> ValueError", lanza(ValueError, lambda: caido.atacar(vivo)))
    comprobar("Objetivo derrotado -> ValueError", lanza(ValueError, lambda: vivo.atacar(caido)))
    comprobar("Objetivo inválido (None) -> TypeError", lanza(TypeError, lambda: vivo.atacar(None)))
    comprobar("Atacarse a sí mismo -> ValueError", lanza(ValueError, lambda: vivo.atacar(vivo)))

    # 10 y 11. Combate completo y ganador
    titulo("10 y 11. Combate completo: Arthas vs Gandalf")
    arthas = Guerrero("Arthas", 100, 30, 20)
    gandalf = Mago("Gandalf", 80, 40, 10)
    combate = Combate(arthas, gandalf)
    combate.iniciar()
    print("\nComprobaciones:")
    comprobar("El combate terminó en victoria", combate.resultado == "victoria")
    comprobar("El ganador es Gandalf", combate.ganador is gandalf)
    comprobar("Arthas quedó con 0 y Gandalf con 2 de vida", arthas.vida == 0 and gandalf.vida == 2)
    comprobar("Duró 3 rondas (6 turnos)", combate.rondas == 3)

    # 12. Empate técnico
    titulo("12. Combate sin daño: empate técnico")
    a1 = Arquero("Arquero A", 100, 10, 20)
    a2 = Arquero("Arquero B", 100, 10, 20)
    combate = Combate(a1, a2)
    combate.iniciar()
    print("\nComprobaciones:")
    comprobar("Resultado = empate técnico", combate.resultado == "empate_tecnico")
    comprobar("No hay ganador", combate.ganador is None)

    # Extra: empate por 50 rondas
    titulo("Extra: 50 rondas sin ganador (se muestra solo el final)")
    m1 = Mago("Mago A", 100, 1, 0)
    m2 = Mago("Mago B", 100, 1, 0)
    combate = Combate(m1, m2)
    # para no llenar la consola, silencio los prints solo durante este combate
    import contextlib, io
    with contextlib.redirect_stdout(io.StringIO()):
        combate.iniciar()
    combate.mostrar_resultado()
    comprobar("Resultado = empate por rondas", combate.resultado == "empate_rondas")
    comprobar("Se jugaron 50 rondas", combate.rondas == 50)
    comprobar("Ambos quedaron con 50 de vida", m1.vida == 50 and m2.vida == 50)

    # resumen
    titulo("Resumen")
    print(f"  {sum(resultados)} de {len(resultados)} comprobaciones correctas")
    if not all(resultados):
        sys.exit(1)


if __name__ == "__main__":
    main()
