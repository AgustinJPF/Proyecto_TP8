"""Pruebas unitarias del back-end.  Ejecutar: python -m unittest discover tests"""
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from backend.analizador import AnalizadorEspectro


def crear_csv(filas):
    f = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False)
    f.write("timestamp,canal,frecuencia_mhz,potencia_dbm,estado_sensor\n")
    f.write("\n".join(filas))
    f.close()
    return f.name


def filas_canal(canal, potencias, estados=None):
    ts = pd.date_range("2026-11-16", periods=len(potencias), freq="10min")
    estados = estados or ["OK"] * len(potencias)
    return [f"{t},{canal},433.1,{p},{e}" for t, p, e in zip(ts, potencias, estados)]


class TestBackend(unittest.TestCase):
    def analizar(self, filas, umbral=-85):
        ruta = crear_csv(filas)
        self.addCleanup(Path(ruta).unlink)
        a = AnalizadorEspectro()
        a.cargar(ruta)
        return a, a.analizar(umbral)

    def test_ocupacion_basica(self):
        _, est = self.analizar(filas_canal("C01", [-100, -80, -90, -70]))
        self.assertEqual(est["C01"].validas, 4)
        self.assertEqual(est["C01"].ocupadas, 2)
        self.assertAlmostEqual(est["C01"].ocupacion_pct, 50.0)

    def test_invalidas_excluidas(self):
        filas = filas_canal("C01", [-70, -999, -70, -70, ""],
                            ["OK", "OK", "ERROR", "OK", "OK"])
        a, est = self.analizar(filas)
        self.assertEqual(est["C01"].validas, 2)       # solo 1.º y 4.º
        self.assertEqual(est["C01"].invalidas, 3)
        self.assertEqual(a.resumen_carga.codigo_999, 1)
        self.assertEqual(a.resumen_carga.estado_error, 1)
        self.assertEqual(a.resumen_carga.potencia_faltante, 1)

    def test_duplicados(self):
        filas = filas_canal("C01", [-70, -70, -70])
        a, est = self.analizar(filas + [filas[0]])
        self.assertEqual(a.resumen_carga.duplicados, 1)
        self.assertEqual(est["C01"].validas, 3)

    def test_registros_faltantes(self):
        filas = filas_canal("C01", [-90] * 10)
        filas_c2 = filas_canal("C02", [-90] * 10)
        del filas_c2[3:6]                                # faltan 3 de 10
        _, est = self.analizar(filas + filas_c2)
        self.assertEqual(est["C02"].faltantes, 3)
        self.assertIn("Reportes faltantes", est["C02"].observaciones)

    def test_umbral_configurable(self):
        filas = filas_canal("C01", [-100, -80, -60])
        _, e1 = self.analizar(filas, -85)
        _, e2 = self.analizar(filas, -70)
        self.assertEqual(e1["C01"].ocupadas, 2)
        self.assertEqual(e2["C01"].ocupadas, 1)

    def test_persistente(self):
        _, est = self.analizar(filas_canal("C01", [-60] * 100))
        self.assertIn("Ocupación persistente", est["C01"].observaciones)

    def test_promedio_movil(self):
        a, _ = self.analizar(filas_canal("C01", [-90, -80, -70]))
        df = a.serie("C01", 2)
        self.assertAlmostEqual(df["promedio"].iloc[2], -75.0)


if __name__ == "__main__":
    unittest.main()
