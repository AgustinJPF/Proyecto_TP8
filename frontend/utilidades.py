"""Funciones auxiliares de formato (FRONT-END)."""


def fmt(valor, decimales=1):
    """Formato argentino: 1.004 / 55,4."""
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "#").replace(".", ",").replace("#", ".")
