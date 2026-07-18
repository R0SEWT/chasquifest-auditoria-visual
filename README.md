# Operación ChasquiFest — Auditoría de visualización

> Cinco gráficos mintieron. Este repositorio muestra lo que los datos realmente dicen.

**🖥️ Dashboard en vivo:** https://r0sewt.github.io/chasquifest-auditoria-visual/

Examen de *Data Visualization* resuelto como una **auditoría visual**: cada caso toma un gráfico engañoso del "dashboard al borde del colapso" de un festival ficticio y lo reconstruye desde los datos, declarando numerador y denominador de cada tasa, nombrando la tarea analítica de cada gráfico y sin convertir ninguna correlación en causa.

## Los cinco casos

| # | Caso | El titular decía… | …los datos dicen |
|---|------|-------------------|------------------|
| 1 | Taquilla | "App produce el 35.7% del éxito" (suma de %) | App = **53.7%** del share **real** de ventas; ocupación global **90.27%** (no el 88.17% del promedio de promedios) |
| 2 | Logística | "La lluvia causa todas las demoras" | La **distancia** explica el 85% de la variación (r=0.92); la lluvia, el 2.4%. Tardanza agregada **44.68%** vs meta 20% |
| 3 | Asistencia | "Julio cae 57%" | Julio-2026 tiene **12 de 31 días** (cobertura 38.71%); a ritmo diario va **+11.5%**. El signo se invierte |
| 4 | Impacto | "Lima ama más al festival" | Es el mapa de la **población**. Normalizado, **Cusco** lidera alcance (157.9/1000 hab); Lima cae fuera del top-5 |
| 5 | Campaña | "El video causó el boom: +108%" | Los factores se movieron juntos (sedes 8→12, inversión ×2.9, promos 0→54%); en sedes ya abiertas el cambio es **−13%**. Efecto **no identificable** |

## Estructura

```
├── docs/index.html      # Dashboard "titular vs. realidad" (GitHub Pages)
├── notebook/            # Un notebook ejecutable por caso — recalcula cada cifra del CSV
│   ├── caso1.ipynb … caso5.ipynb
├── data/                # Los 5 CSV sintéticos
├── respuestas.md        # Solucionario consolidado en prosa (las 4 preguntas × 5 casos)
└── examen-operacion-chasquifest.pdf
```

Cada respuesta sigue la regla de auditoría del examen: **concepto técnico · evidencia con campos concretos del CSV · decisión de cálculo o diseño · límite / trade-off**. Las fórmulas se dan en sintaxis Tableau y su símil en pandas. La pregunta 4 de cada caso cierra con una *bitácora* de cinco frases (lectura inicial → KPI decisor → giro analítico → lectura revisada → consecuencia).

## Reproducir

Entorno con [uv](https://docs.astral.sh/uv/):

```bash
uv sync
uv run jupyter lab      # abre notebook/casoN.ipynb
```

Los notebooks leen los CSV desde `data/` (ejecutar desde la raíz del repo).

## Aviso

ChasquiFest, Killa (la llama-mascota) y **todas las cifras son ficticios y sintéticos**. Los nombres geográficos dan contexto peruano; los datos **no** describen el desempeño real de ninguna ciudad ni población.
