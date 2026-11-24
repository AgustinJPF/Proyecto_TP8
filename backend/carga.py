"""Carga y limpieza del archivo espectro.csv (BACK-END)."""
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

COLUMNAS_REQUERIDAS = ["timestamp", "canal", "frecuencia_mhz",
                       "potencia_dbm", "estado_sensor"]
CODIGO_ERROR = -999.0
INTERVALO = "10min"


@dataclass
class ResumenCarga:
    """Contadores de calidad de datos detectados durante la carga."""
    filas_leidas: int = 0
    timestamps_invalidos: int = 0
    duplicados: int = 0
    estado_error: int = 0
    potencia_faltante: int = 0
    codigo_999: int = 0
    filas_invalidas: int = 0   # filas con al menos un motivo de invalidez
    filas_utiles: int = 0      # filas válidas (usadas en los cálculos)


class CargadorCSV:
    """Lee espectro.csv, detecta duplicados e invalida mediciones erróneas."""

    def cargar(self, ruta):
        ruta = Path(ruta)
        if not ruta.is_file():
            raise FileNotFoundError(f"No se encontró el archivo: {ruta}")
        try:
            df = pd.read_csv(ruta)
        except Exception as exc:
            raise ValueError(f"No se pudo leer el CSV: {exc}") from exc

        df.columns = [c.strip().lower() for c in df.columns]
        faltan = [c for c in COLUMNAS_REQUERIDAS if c not in df.columns]
        if faltan:
            raise ValueError("Faltan columnas en el CSV: " + ", ".join(faltan))

        resumen = ResumenCarga(filas_leidas=len(df))
        df = df[COLUMNAS_REQUERIDAS].copy()

        # --- Tipos y normalización ---
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df["canal"] = df["canal"].astype("string").str.strip().str.upper()
        n0 = len(df)
        df = df.dropna(subset=["timestamp", "canal"])
        resumen.timestamps_invalidos = n0 - len(df)
        # Alinea a la grilla de 10 min (tolera pequeños corrimientos)
        df["timestamp"] = df["timestamp"].dt.round(INTERVALO)
        df["frecuencia_mhz"] = pd.to_numeric(df["frecuencia_mhz"], errors="coerce")
        df["potencia_dbm"] = pd.to_numeric(df["potencia_dbm"], errors="coerce")
        df["estado_sensor"] = (df["estado_sensor"].fillna("").astype(str)
                               .str.strip().str.upper())

        # --- Duplicados (mismo canal y mismo instante): se conserva el primero ---
        dup = df.duplicated(subset=["timestamp", "canal"], keep="first")
        resumen.duplicados = int(dup.sum())
        df = df[~dup].copy()

        # --- Mediciones inválidas ---
        m_error = (df["estado_sensor"] == "ERROR").to_numpy()
        m_nan = df["potencia_dbm"].isna().to_numpy()
        m_999 = (df["potencia_dbm"] == CODIGO_ERROR).to_numpy()
        invalida = m_error | m_nan | m_999
        df["valida"] = ~invalida

        resumen.estado_error = int(m_error.sum())
        resumen.potencia_faltante = int(m_nan.sum())
        resumen.codigo_999 = int(m_999.sum())
        resumen.filas_invalidas = int(invalida.sum())
        resumen.filas_utiles = int((~invalida).sum())

        df = df.sort_values(["canal", "timestamp"]).reset_index(drop=True)
        return df, resumen
