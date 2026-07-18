# Operación ChasquiFest — Auditoría de visualización

> Cinco gráficos del festival, releídos desde los datos: lo que el titular decía y lo que los números sostienen.

**🖥️ Dashboard en vivo:** https://r0sewt.github.io/chasquifest-auditoria-visual/
**📄 Informe científico (LaTeX → PDF):** [`informe/informe.pdf`](informe/informe.pdf) — 52 páginas, 17 figuras

Examen de *Data Visualization* resuelto como una **auditoría visual**: cada caso toma un gráfico engañoso del "dashboard al borde del colapso" de un festival ficticio y lo reconstruye desde los datos, declarando numerador y denominador de cada tasa, nombrando la tarea analítica de cada gráfico y sin convertir ninguna correlación en causa. Los notebooks combinan el desarrollo reproducible con gráficos editoriales sencillos en Seaborn; el informe conserva el detalle técnico y figuras vectoriales para publicación.

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
├── informe/             # Informe científico en LaTeX
│   ├── informe.tex      #   documento maestro (carátula, intro, metodología, conclusiones)
│   ├── informe.pdf      #   PDF compilado (52 pp., 17 figuras)
│   ├── secciones/       #   una sección .tex por caso
│   └── figuras/         #   figuras PDF vectoriales + scripts matplotlib + hoja de estilo
├── notebook/            # Notebooks ejecutados, figuras PNG y análisis reproducible
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
uv run jupyter lab notebook
```

Para ejecutar y guardar los cinco notebooks desde la raíz del repositorio:

```bash
for notebook in notebook/caso{1,2,3,4,5}.ipynb; do
  uv run jupyter nbconvert --to notebook --execute --inplace "$notebook"
done
```

Cada notebook se ejecuta con su propio directorio como ubicación de trabajo: carga los CSV mediante `../data/` y guarda sus figuras PNG en `notebook/`.

Las figuras vectoriales del informe comparten la configuración de `informe/figuras/estilo_figuras.py`. Para regenerarlas:

```bash
for caso in informe/figuras/gen_caso{1,2,3,4,5}.py; do
  uv run python "$caso"
done
```

El PDF se compila desde `informe/` con una distribución de LaTeX que incluya `latexmk` y Biber:

```bash
cd informe
latexmk -pdf informe.tex
```

## Aviso

ChasquiFest, Killa (la llama-mascota) y **todas las cifras son ficticios y sintéticos**. Los nombres geográficos dan contexto peruano; los datos **no** describen el desempeño real de ninguna ciudad ni población.
