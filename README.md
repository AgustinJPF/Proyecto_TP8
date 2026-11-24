# PRGII-PRJ08 – Monitor de ocupación del espectro radioeléctrico

Programación II (5002) – Ingeniería en Telecomunicaciones.
Interfaz gráfica en **PySide6** + back-end en **pandas/numpy** + gráficos **matplotlib**.

## Instalación y ejecución
```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python tools/generar_datos.py espectro.csv   # solo si no tienen el CSV real
python main.py
python -m unittest discover tests            # pruebas del back-end
```
Coloquen el `espectro.csv` real en la raíz del proyecto (o elíjanlo con el botón «…»).

## Estructura
```
PRGII-PRJ08/
├── main.py                      # punto de entrada
├── requirements.txt
├── backend/
│   ├── carga.py                 # CargadorCSV: lectura, duplicados, inválidos (ERROR, NaN, -999)
│   ├── ocupacion.py             # CalculadorOcupacion: grilla 10 min, % ocupación, promedio móvil
│   ├── anomalias.py             # DetectorAnomalias, CriteriosAnomalia, EstadisticasCanal
│   └── analizador.py            # AnalizadorEspectro: fachada usada por la GUI
├── frontend/
│   ├── ventana_principal.py     # VentanaPrincipal (integra todo)
│   ├── panel_parametros.py      # PanelParametros
│   ├── panel_informe.py         # PanelInforme
│   ├── grafico_potencia.py      # GraficoPotencia
│   ├── grafico_ocupacion.py     # GraficoOcupacion
│   ├── tabla_resumen.py         # TablaResumen
│   └── utilidades.py            # fmt(): formato numérico es-AR
├── tools/generar_datos.py       # genera un espectro.csv de ejemplo
├── tests/test_backend.py        # pruebas unitarias
└── docs/                        # guías de Git, reparto e informe
```

## Criterios de anomalía (ajustables en `CriteriosAnomalia`)
| Observación | Criterio por defecto |
|---|---|
| Ocupación persistente | ocupación ≥ 50 % **o** racha continua ≥ 72 muestras (12 h) |
| Actividad en horario laboral | ≥ 80 % de las muestras ocupadas en lun–vie 08–18 h |
| Actividad nocturna | ≥ 80 % de las muestras ocupadas entre 20 y 06 h |
| Picos aislados | ≥ 5 muestras ocupadas aisladas (racha de 1), ocupación < 10 % |
| Emisiones intermitentes | ≥ 15 ráfagas y ocupación ≥ 10 % (sin patrón horario) |
| Reportes faltantes | faltan > 2 % de las 1008 muestras esperadas |
| Mediciones inválidas | > 2 % de los registros con ERROR, vacío o −999 |

Ocupación (%) = mediciones **válidas** con potencia > umbral ÷ mediciones **válidas** × 100.
