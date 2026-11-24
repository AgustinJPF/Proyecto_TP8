"""Genera un espectro.csv de ejemplo (12 canales, 1 semana, cada 10 min).

Uso:  python tools/generar_datos.py [salida.csv]
Incluye: actividad laboral/nocturna, ocupación persistente, picos aislados,
registros faltantes, mediciones inválidas (ERROR, -999, vacías) y duplicados.
"""
import sys

import numpy as np
import pandas as pd


def rafagas(rng, n, prob, largo):
    inicios = (rng.random(n) < prob).astype(float)
    return np.convolve(inicios, np.ones(largo))[:n] > 0


def main(salida="espectro.csv"):
    rng = np.random.default_rng(42)
    ts = pd.date_range("2026-11-16", periods=7 * 144, freq="10min")  # lunes
    n, hora, dow = len(ts), ts.hour.to_numpy(), ts.weekday.to_numpy()
    bloques = []
    for i in range(12):
        canal, frec = f"C{i + 1:02d}", round(433.100 + 0.025 * i, 3)
        pot = rng.normal(-100, 3, n)
        act = rafagas(rng, n, 0.01, 8)                       # actividad base
        if canal == "C02":
            act = np.zeros(n, bool)
            idx = rng.choice(n, 14, replace=False)
            act[idx] = True
        elif canal == "C03":
            act = (hora >= 8) & (hora < 18) & (dow < 5)
        elif canal == "C04":
            act = (dow >= 4) | rafagas(rng, n, 0.02, 6)
        elif canal == "C05":
            act = rafagas(rng, n, 0.025, 5)
        elif canal == "C06":
            act = np.zeros(n, bool)
        elif canal == "C09":
            act = (hora >= 22) | (hora < 4)
        pot[act] = rng.normal(-72, 5, int(act.sum()))
        df = pd.DataFrame({"timestamp": ts, "canal": canal,
                           "frecuencia_mhz": frec,
                           "potencia_dbm": np.round(pot, 1),
                           "estado_sensor": "OK"})
        if canal == "C07":      # registros faltantes (5 %)
            df = df.drop(df.index[rng.choice(n, int(0.05 * n), replace=False)])
        if canal == "C11":      # mediciones inválidas (5 %)
            idx = rng.choice(n, int(0.05 * n), replace=False)
            for j, k in enumerate(idx):
                if j % 3 == 0:
                    df.iloc[k, df.columns.get_loc("estado_sensor")] = "ERROR"
                elif j % 3 == 1:
                    df.iloc[k, df.columns.get_loc("potencia_dbm")] = -999
                else:
                    df.iloc[k, df.columns.get_loc("potencia_dbm")] = np.nan
        bloques.append(df)
    datos = pd.concat(bloques).sort_values(["timestamp", "canal"])
    datos = pd.concat([datos, datos.sample(10, random_state=1)])  # duplicados
    datos.to_csv(salida, index=False, date_format="%Y-%m-%d %H:%M:%S")
    print(f"Archivo generado: {salida} ({len(datos)} filas)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "espectro.csv")
