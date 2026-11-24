"""Cálculo de ocupación, series temporales y promedio móvil (BACK-END)."""
import numpy as np
import pandas as pd

from backend.carga import INTERVALO


class CalculadorOcupacion:
    """Trabaja sobre el DataFrame limpio entregado por CargadorCSV."""

    def __init__(self, df: pd.DataFrame):
        if df.empty:
            raise ValueError("El archivo no contiene mediciones utilizables.")
        self._df = df
        self.grilla = pd.date_range(df["timestamp"].min(),
                                    df["timestamp"].max(), freq=INTERVALO)
        self._series = {}      # potencia válida reindexada a la grilla
        self._presentes = {}   # registros existentes por canal
        self._invalidas = {}   # registros inválidos por canal
        self._frec = {}
        for canal, g in df.groupby("canal"):
            validos = g.loc[g["valida"]].set_index("timestamp")["potencia_dbm"]
            self._series[canal] = validos.reindex(self.grilla)
            self._presentes[canal] = len(g)
            self._invalidas[canal] = int((~g["valida"]).sum())
            self._frec[canal] = float(g["frecuencia_mhz"].median())

    # --- Consultas básicas ---
    def canales(self):
        return sorted(self._series)

    def frecuencia(self, canal):
        return self._frec[canal]

    def registros_presentes(self, canal):
        return self._presentes[canal]

    def invalidas(self, canal):
        return self._invalidas[canal]

    def serie_canal(self, canal) -> pd.Series:
        """Potencia válida en la grilla completa (NaN = faltante o inválida)."""
        return self._series[canal]

    # --- Ocupación ---
    def mascara_ocupada(self, canal, umbral) -> np.ndarray:
        return (self._series[canal] > umbral).to_numpy()

    def ocupacion(self, canal, umbral):
        """Devuelve (ocupadas, válidas, porcentaje)."""
        s = self._series[canal]
        validas = int(s.notna().sum())
        ocupadas = int((s > umbral).sum())
        pct = 100.0 * ocupadas / validas if validas else 0.0
        return ocupadas, validas, pct

    # --- Evolución temporal ---
    def serie_con_promedio(self, canal, ventana) -> pd.DataFrame:
        s = self._series[canal]
        prom = s.rolling(window=max(1, int(ventana)), min_periods=1).mean()
        prom[s.isna()] = np.nan   # deja huecos donde no hay dato válido
        return pd.DataFrame({"potencia": s, "promedio": prom})
