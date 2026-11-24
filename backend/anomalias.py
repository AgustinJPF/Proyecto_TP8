"""Detección de comportamientos anormales por canal (BACK-END)."""
from dataclasses import dataclass, field

import numpy as np

from backend.ocupacion import CalculadorOcupacion

OBS_PERSISTENTE = "Ocupación persistente"
OBS_LABORAL = "Actividad en horario laboral"
OBS_NOCTURNA = "Actividad nocturna"
OBS_PICOS = "Picos aislados"
OBS_INTERMITENTE = "Emisiones intermitentes"
OBS_FALTANTES = "Reportes faltantes"
OBS_INVALIDAS = "Mediciones inválidas"


@dataclass
class CriteriosAnomalia:
    """Parámetros ajustables de los criterios de detección."""
    ocupacion_persistente_pct: float = 50.0
    racha_persistente: int = 72          # 72 muestras = 12 h seguidas
    concentracion_horaria: float = 0.80  # fracción de ocupadas en la franja
    min_ocupadas_horario: int = 20
    min_picos: int = 5
    max_ocupacion_picos_pct: float = 10.0
    min_rachas_intermitente: int = 15
    min_ocupacion_intermitente_pct: float = 10.0
    max_faltantes_pct: float = 2.0
    max_invalidas_pct: float = 2.0


@dataclass
class EstadisticasCanal:
    canal: str
    frecuencia_mhz: float
    validas: int
    ocupadas: int
    ocupacion_pct: float
    esperadas: int
    faltantes: int
    faltantes_pct: float
    invalidas: int
    invalidas_pct: float
    racha_max: int
    n_rachas: int
    picos_aislados: int
    potencia_media: float
    potencia_max: float
    observaciones: list = field(default_factory=list)

    @property
    def anomalo(self) -> bool:
        return bool(self.observaciones)

    @property
    def persistente(self) -> bool:
        return OBS_PERSISTENTE in self.observaciones


class DetectorAnomalias:
    def __init__(self, calculador: CalculadorOcupacion, criterios=None):
        self.calc = calculador
        self.crit = criterios or CriteriosAnomalia()

    @staticmethod
    def rachas(mascara: np.ndarray) -> np.ndarray:
        """Longitudes de los tramos consecutivos de True."""
        m = np.concatenate(([0], mascara.astype(int), [0]))
        d = np.diff(m)
        inicios = np.where(d == 1)[0]
        fines = np.where(d == -1)[0]
        return fines - inicios

    def evaluar(self, canal, umbral) -> EstadisticasCanal:
        c, k = self.calc, self.crit
        ocupadas, validas, pct = c.ocupacion(canal, umbral)
        mascara = c.mascara_ocupada(canal, umbral)
        rachas = self.rachas(mascara)
        racha_max = int(rachas.max()) if rachas.size else 0
        n_rachas = int(rachas.size)
        picos = int((rachas == 1).sum())

        esperadas = len(c.grilla)
        presentes = c.registros_presentes(canal)
        faltantes = max(0, esperadas - presentes)
        pct_falt = 100.0 * faltantes / esperadas if esperadas else 0.0
        inval = c.invalidas(canal)
        pct_inv = 100.0 * inval / presentes if presentes else 0.0

        serie = c.serie_canal(canal)
        media = float(serie.mean()) if validas else float("nan")
        maximo = float(serie.max()) if validas else float("nan")

        # Distribución horaria de las muestras ocupadas
        frac_lab = frac_noc = 0.0
        if ocupadas >= k.min_ocupadas_horario:
            ts = c.grilla[mascara]
            h, wd = np.asarray(ts.hour), np.asarray(ts.weekday)
            frac_lab = float(((h >= 8) & (h < 18) & (wd < 5)).mean())
            frac_noc = float(((h >= 20) | (h < 6)).mean())

        obs = []
        if pct >= k.ocupacion_persistente_pct or racha_max >= k.racha_persistente:
            obs.append(OBS_PERSISTENTE)
        else:
            horario = False
            if frac_lab >= k.concentracion_horaria:
                obs.append(OBS_LABORAL)
                horario = True
            elif frac_noc >= k.concentracion_horaria:
                obs.append(OBS_NOCTURNA)
                horario = True
            if (picos >= k.min_picos and pct < k.max_ocupacion_picos_pct
                    and picos >= 0.5 * n_rachas):
                obs.append(OBS_PICOS)
            elif (not horario and n_rachas >= k.min_rachas_intermitente
                  and pct >= k.min_ocupacion_intermitente_pct):
                obs.append(OBS_INTERMITENTE)
        if pct_falt > k.max_faltantes_pct:
            obs.append(OBS_FALTANTES)
        if pct_inv > k.max_invalidas_pct:
            obs.append(OBS_INVALIDAS)

        return EstadisticasCanal(
            canal=canal, frecuencia_mhz=c.frecuencia(canal), validas=validas,
            ocupadas=ocupadas, ocupacion_pct=pct, esperadas=esperadas,
            faltantes=faltantes, faltantes_pct=pct_falt, invalidas=inval,
            invalidas_pct=pct_inv, racha_max=racha_max, n_rachas=n_rachas,
            picos_aislados=picos, potencia_media=media, potencia_max=maximo,
            observaciones=obs)
