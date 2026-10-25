"""Pruebas automatizadas con pytest.

Uso:  pytest -v
"""
import pytest

from personajes import Personaje, Guerrero, Mago, Arquero, Combate


# ---------- creación y validaciones ----------

@pytest.mark.parametrize("clase", [Guerrero, Mago, Arquero])
def test_creacion_valida(clase):
    p = clase("Hero", 100, 30, 20)
    assert p.nombre == "Hero"
    assert p.vida == 100
    assert p.ataque == 30
    assert p.defensa == 20
    assert isinstance(p, Personaje)
    assert p.esta_vivo()


def test_personaje_es_abstracta():
    with pytest.raises(TypeError):
        Personaje("X", 10, 10, 10)


@pytest.mark.parametrize("vida", [101, -1, 1000])
def test_vida_fuera_de_rango(vida):
    with pytest.raises(ValueError):
        Guerrero("A", vida, 10, 5)


def test_vida_de_otro_tipo():
    with pytest.raises(TypeError):
        Guerrero("A", "100", 10, 5)


@pytest.mark.parametrize("nombre", ["", "   "])
def test_nombre_vacio(nombre):
    with pytest.raises(ValueError):
        Mago(nombre, 50, 10, 5)


@pytest.mark.parametrize("ataque", [0, -3])
def test_ataque_no_positivo(ataque):
    with pytest.raises(ValueError):
        Arquero("A", 50, ataque, 5)


def test_defensa_negativa():
    with pytest.raises(ValueError):
        Arquero("A", 50, 10, -1)


def test_defensa_cero_es_valida():
    assert Arquero("A", 50, 10, 0).defensa == 0


def test_setters_validan():
    p = Guerrero("A", 50, 10, 5)
    with pytest.raises(ValueError):
        p.vida = 150
    with pytest.raises(ValueError):
        p.ataque = 0
    with pytest.raises(ValueError):
        p.defensa = -2
    p.vida = 70
    assert p.vida == 70


# ---------- daño de cada clase ----------

def test_dano_guerrero():
    objetivo = Mago("Obj", 100, 10, 10)
    assert Guerrero("G", 100, 30, 5).atacar(objetivo) == 26
    assert objetivo.vida == 74


def test_guerrero_redondea_hacia_abajo():
    # 33 * 1.2 = 39.6 -> 39, menos 10 de defensa = 29
    objetivo = Mago("Obj", 100, 10, 10)
    assert Guerrero("G", 100, 33, 5).atacar(objetivo) == 29


def test_guerrero_no_causa_dano_negativo():
    objetivo = Mago("Obj", 100, 10, 50)
    assert Guerrero("G", 100, 10, 5).atacar(objetivo) == 0
    assert objetivo.vida == 100


def test_dano_mago_ignora_defensa():
    objetivo = Guerrero("Obj", 100, 10, 20)
    assert Mago("M", 100, 40, 5).atacar(objetivo) == 40


def test_dano_arquero_critico():
    objetivo = Guerrero("Obj", 100, 10, 15)
    assert Arquero("A", 100, 35, 5).atacar(objetivo) == 40


@pytest.mark.parametrize("defensa", [35, 50])
def test_arquero_sin_critico_si_no_supera_defensa(defensa):
    objetivo = Guerrero("Obj", 100, 10, defensa)
    assert Arquero("A", 100, 35, 5).atacar(objetivo) == 0


# ---------- vida y estado ----------

def test_vida_nunca_negativa():
    p = Guerrero("A", 20, 10, 5)
    efectivo = p.recibir_danio(50)
    assert efectivo == 20
    assert p.vida == 0
    assert not p.esta_vivo()


def test_recibir_danio_negativo_falla():
    with pytest.raises(ValueError):
        Guerrero("A", 20, 10, 5).recibir_danio(-1)


def test_recibir_danio_no_resta_defensa_otra_vez():
    p = Guerrero("A", 100, 10, 50)
    assert p.recibir_danio(10) == 10
    assert p.vida == 90


def test_mostrar_estado_incluye_datos():
    estado = Mago("Gandalf", 80, 40, 10).mostrar_estado()
    assert "Gandalf" in estado and "80" in estado and "Mago" in estado


# ---------- validaciones al atacar ----------

def test_derrotado_no_puede_atacar():
    caido = Mago("Caído", 10, 10, 5)
    caido.recibir_danio(10)
    with pytest.raises(ValueError):
        caido.atacar(Guerrero("V", 100, 10, 5))


def test_no_se_ataca_a_un_derrotado():
    caido = Guerrero("Caído", 10, 10, 5)
    caido.recibir_danio(10)
    with pytest.raises(ValueError):
        Mago("M", 100, 10, 5).atacar(caido)


def test_objetivo_invalido():
    with pytest.raises(TypeError):
        Mago("M", 100, 10, 5).atacar("no soy un personaje")


# ---------- combate ----------

def test_combate_ejemplo_gana_gandalf():
    arthas = Guerrero("Arthas", 100, 30, 20)
    gandalf = Mago("Gandalf", 80, 40, 10)
    combate = Combate(arthas, gandalf)
    ganador = combate.iniciar()
    assert ganador is gandalf
    assert combate.resultado == "victoria"
    assert arthas.vida == 0
    assert gandalf.vida == 2
    assert combate.rondas == 3


def test_combate_empate_tecnico():
    a = Arquero("A", 100, 10, 20)
    b = Arquero("B", 100, 10, 20)
    combate = Combate(a, b)
    assert combate.iniciar() is None
    assert combate.resultado == "empate_tecnico"
    assert combate.rondas == 1


def test_combate_empate_por_50_rondas():
    a = Mago("A", 100, 1, 0)
    b = Mago("B", 100, 1, 0)
    combate = Combate(a, b)
    combate.iniciar()
    assert combate.resultado == "empate_rondas"
    assert combate.rondas == 50
    assert a.vida == 50 and b.vida == 50


def test_combate_validaciones():
    a = Guerrero("A", 100, 10, 5)
    with pytest.raises(TypeError):
        Combate(a, "no soy un personaje")
    with pytest.raises(ValueError):
        Combate(a, a)
    caido = Mago("C", 10, 10, 5)
    caido.recibir_danio(10)
    with pytest.raises(ValueError):
        Combate(a, caido)


def test_combate_no_se_puede_repetir():
    combate = Combate(Guerrero("A", 100, 30, 5), Mago("B", 10, 10, 5))
    combate.iniciar()
    with pytest.raises(RuntimeError):
        combate.iniciar()


def test_verificar_ganador_sin_ganador():
    combate = Combate(Guerrero("A", 100, 30, 5), Mago("B", 100, 10, 5))
    assert combate.verificar_ganador() is None


def test_cambiar_turno_alterna():
    a = Guerrero("A", 100, 30, 5)
    b = Mago("B", 100, 10, 5)
    combate = Combate(a, b)
    assert combate._turno == 0
    combate.cambiar_turno()
    assert combate._turno == 1
    combate.cambiar_turno()
    assert combate._turno == 0
