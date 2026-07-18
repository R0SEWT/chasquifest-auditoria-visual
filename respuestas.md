# Operación ChasquiFest — Respuestas del examen de Data Visualization

**Rol:** auditor(a) visual. **Regla de juego:** cada respuesta lleva 4 piezas cuando corresponde — (1) concepto técnico, (2) evidencia con campos/números concretos del CSV, (3) decisión de cálculo o diseño, (4) límite/trade-off. Las fórmulas se dan en sintaxis Tableau **y** su símil en pandas. La pregunta 4 de cada caso cierra con la **bitácora** de 5 frases del protocolo.

**Cómo leer este documento:** este `respuestas.md` es el consolidado en prosa. Cada afirmación numérica está **recalculada y validada** contra el CSV en el notebook ejecutable del caso (`notebook/casoN.ipynb`), que además contiene las figuras corregidas.

| Caso | Notebook | Datos |
|------|----------|-------|
| 1 · Taquilla | `notebook/caso1.ipynb` | `data/caso1_taquilla_chasquifest.csv` |
| 2 · Logística | `notebook/caso2.ipynb` | `data/caso2_logistica_chasquifest.csv` |
| 3 · Asistencia | `notebook/caso3.ipynb` | `data/caso3_asistencia_mensual_chasquifest.csv` |
| 4 · Impacto | `notebook/caso4.ipynb` | `data/caso4_impacto_departamental_chasquifest.csv` |
| 5 · Campaña | `notebook/caso5.ipynb` | `data/caso5_campania_killa_chasquifest.csv` |



<br>

---

> 📓 **Computación y figuras ejecutadas:** [`notebook/caso1.ipynb`](notebook/caso1.ipynb)


# CASO 1 — Taquilla (Operación ChasquiFest)
## Auditoría de visualización — la torta falsa de "participación en el éxito"

**Rol:** Auditor de Visualización. **Rigor:** cada afirmación se ancla en un número recalculado directamente del CSV en este notebook, con numerador y denominador declarados.

**Diagnóstico del error del practicante:** tomó `ocupacion_fila_pct` (un ratio YA calculado por fila, `evento_id × canal`, NO aditivo) y lo **sumó** por canal para armar una torta (App 35.7%, Web 33.8%, Taquilla 30.5%). El denominador de esa torta es "la suma de 216 porcentajes de fila" — una cantidad sin significado de negocio, no un total real (no es ventas, no es cupos, no es ocupación). Por eso "nadie sabe qué total representa ese 35.7%": **no representa ningún total**, es un artefacto aritmético (∑ de ratios ≠ ratio de sumas, y menos aún una proporción parte-todo válida).

Este notebook reproduce los números ancla, corrige el error y responde las 4 preguntas del caso.



### 0. Verificación de fórmulas ancla (nivel de fila)

Antes de agregar nada, confirmamos que `ocupacion_fila_pct` y `margen_fila_pct` son en efecto ratios **row-level** (una fórmula por fila `evento_id × canal`), no medidas agregadas.



---
## Pregunta 1 — Promedio de promedios



**1) Concepto técnico.** Hay dos maneras de agregar una columna que ya es un ratio: (a) **ratio-of-sums** (agregar primero numerador y denominador por separado y dividir al final — pondera cada fila por su tamaño real) o (b) **mean-of-ratios** (promediar los ratios de fila ya calculados — le da el mismo peso a una fila de 521 cupos que a una de 4 812 cupos). `AVG([ocupacion_fila_pct])` es (b): responde "¿cuál es el ratio promedio de una fila evento-canal cualquiera?", no "¿qué fracción de la capacidad total del festival se ocupó?". La pregunta de negocio de la jefa de taquilla ("¿el festival ocupó su capacidad?") es una pregunta de **capacidad total**, que solo (a) responde correctamente.

**2) Evidencia (num/den declarados).**
- Ocupación ponderada = SUM(`ingresos_validados`) / SUM(`cupos_ofertados`) × 100 = **281 091 / 311 400 × 100 = 90.27%**.
- Ocupación promedio simple = AVG(`ocupacion_fila_pct`) sobre **n = 216 filas** = **88.17%**.
- Meta = 88.0% (columna `meta_ocupacion_pct`, valor único).
- A nivel global de temporada completa (N=216, grano homogéneo evento×canal) **ambas superan la meta**, pero con colchones muy distintos: **+2.27 pp** (ponderada) vs **+0.17 pp** (promedio simple) — la lectura ponderada dice "cumplida con holgura", la no ponderada dice "cumplida raspando, un evento chico y flojo la tumba".
- A un corte más fino (mensual) **sí se observa una divergencia de signo**: en 2026-07 la ponderada da 89.91% (CUMPLE) y la no ponderada da 87.14% (**NO CUMPLE**) — evidencia directa de que ambos KPI pueden decidir distinto frente a la misma meta.
- ⚠️ **Advertencia de periodos no homólogos:** los 12 eventos de julio-2026 están fechados el 25-jul-2026, **posterior** a "hoy" (18-jul-2026 según el contexto del examen), igual que los 12 de agosto. El CSV ya trae `ingresos_validados` cargado para esas filas, así que es una temporada completa pre-cargada (no un feed operativo en vivo). **No se debe presentar el corte mensual como "tendencia hacia el presente"** sin aclarar que julio/agosto son fechas programadas, no eventos ya ocurridos al momento del análisis; el corte mensual aquí sirve solo para *ilustrar* que promedio simple y razón ponderada pueden discrepar, no para narrar una tendencia temporal real. El KPI oficial de temporada debe reportarse a **nivel global (N=216, grano homogéneo)**.

**3) Decisión de cálculo — fórmulas.**

Tableau (medida agregada, ratio-of-sums):
```
Ocupación Global % =
SUM([ingresos_validados]) / SUM([cupos_ofertados])
```
(formatear como porcentaje ×100, o multiplicar explícito: `... * 100`)

pandas símil:
```python
occ_weighted = df['ingresos_validados'].sum() / df['cupos_ofertados'].sum() * 100
```

Lo que **NO** se debe usar (lo que hizo el practicante en espíritu, aplicado a ocupación):
```
AVG([ocupacion_fila_pct])          -- Tableau, mean-of-ratios, sesgado
df['ocupacion_fila_pct'].mean()    -- pandas, mismo sesgo
```

**4) Límite / trade-off.** El ratio-of-sums exige que el numerador y el denominador estén en la MISMA unidad y grano que la pregunta de negocio (aquí: personas y cupos, sumables directamente) — funciona perfecto para ocupación y margen, pero no sirve para razones que no son sumables (ej. promediar tasas ya normalizadas por tamaños heterogéneos sin más contexto, como un NPS por evento). Además, la ponderada oculta la varianza entre filas: un festival puede tener 90.27% ponderado y aun así una fila puntual muy floja (ver Taquilla más abajo); conviene reportar ambas cifras junto con la dispersión, no solo la ponderada. Y como se advirtió arriba, cualquier corte temporal (mensual) debe declarar explícitamente si compara eventos ya realizados vs programados — de lo contrario se compara peras con manzanas.



---
## Pregunta 2 — Nivel del cálculo



**1) Concepto técnico — nivel del cálculo.**
- `ocupacion_fila_pct` y `margen_fila_pct`: **row-level** (una fórmula evaluada por cada fila `evento_id × canal`; NO aditivas entre filas).
- Ocupación global, Margen global, Ticket promedio: **medidas agregadas**, que solo tienen sentido calculadas como ratio-of-sums en el grano deseado (festival / canal / depto / periodo), nunca como `AVG()` de una columna row-level ya calculada.

**2) Evidencia (num/den declarados, fórmulas defendibles).**

Margen global %:
```
-- Tableau (agregada, protegida contra división por cero)
Margen Global % =
IIF(SUM([ventas_soles]) = 0, NULL,
    (SUM([ventas_soles]) - SUM([costo_variable_soles])) / SUM([ventas_soles]))
```
```python
# pandas símil
num = df['ventas_soles'].sum() - df['costo_variable_soles'].sum()
den = df['ventas_soles'].sum()
margen_global = np.where(den == 0, np.nan, num/den*100)
```
Resultado: num = 10 473 741.35 − 4 523 995.12 (¡ojo!: en el notebook el numerador se calculó directo como `SUM(ventas)-SUM(costo)` = **5 949 746.23**; den = SUM(ventas) = **10 473 741.35** → **56.81%** ponderado, vs **57.33%** promedio simple de `margen_fila_pct` (n=216). Ambos existen pero responden preguntas distintas — igual que en Ocupación (Pregunta 1).

**Periodo, comparación y acción (Margen Global).** Calculado sobre la temporada completa **abr–ago 2026** (N=216 filas / 72 eventos). El CSV no trae una meta externa de margen; se declara explícito el benchmark: **sin meta externa en el CSV; benchmark interno = mediana de margen ponderado entre los 3 canales** = 56.56% (App 56.18%, Web 56.56%, Taquilla 59.20%). El 56.81% global queda apenas 0.25 pp por encima de esa mediana y muy cerca del margen propio de **App** (56.18%), el canal de mayor volumen — señal de que el global está siendo "jalado" hacia abajo por el peso de App. **Acción:** revisar la mezcla de canales (¿conviene reasignar cupos hacia Taquilla/Web, de mayor margen, sin sacrificar la ocupación que aporta App?) antes de decidir cualquier cambio de precio o comisión.

Ticket promedio por orden:
```
-- Tableau
Ticket Promedio =
IIF(SUM([ordenes]) = 0, NULL, SUM([ventas_soles]) / SUM([ordenes]))
```
```python
ticket_prom = np.where(df['ordenes'].sum() == 0, np.nan, df['ventas_soles'].sum()/df['ordenes'].sum())
```
Resultado: num = SUM(ventas_soles) = 10 473 741.35; den = SUM(ordenes) = 140 308 → **S/ 74.65 por orden**.

**Periodo, comparación y acción (Ticket promedio).** Mismo periodo, **abr–ago 2026** (N=216 filas / 72 eventos). Sin meta externa de ticket en el CSV; benchmark interno = **mediana de ticket promedio entre canales** = S/ 73.26 (App S/ 78.72, Web S/ 73.26, Taquilla S/ 66.04). El S/ 74.65 global queda ligeramente por encima de esa mediana, arrastrado por el peso de App. **Acción:** evaluar una política de precio/paquetes diferenciada para Taquilla (el canal con ticket más bajo, S/ 66.04, pero el margen más alto, 59.20%) para subir su ticket sin erosionar ese margen ya elevado.

**Nota sobre `ZN()`:** `ZN()` en Tableau solo convierte NULL en 0 (protege agregaciones de nulos), **no** protege división por cero — para eso se necesita `IIF(denominador=0, NULL, ...)` como arriba; usar `ZN()` solo en el denominador de una división puede convertir un NULL válido en 0 y producir un error de división por cero real. Por eso la protección aquí es `IIF`, no `ZN`.

**Error de promediar ratios de fila (sesgo de tamaño), cuantificado:** si en vez de `SUM(ventas)-SUM(costo))/SUM(ventas)` se promediara `margen_fila_pct` fila a fila, cada evento-canal —sea uno de S/ 11 987 en ventas o uno de S/ 200 000— pesa igual (1 voto), inflando el resultado hacia el comportamiento de las filas pequeñas/numerosas. Aquí la distorsión es leve (56.81% vs 57.33%, 0.52 pp) porque los tamaños de fila del CSV son relativamente homogéneos, pero en Ocupación fue mayor (90.27% vs 88.17%, 2.10 pp) porque `cupos_ofertados` varía más entre canales (App/Web ~2 700–4 800 vs Taquilla ~1 800–1 925) — el sesgo de tamaño crece con la heterogeneidad del denominador.

**3) Clasificación de negocio — resultado / eficiencia / guardrail.**
- **Ocupación % (vs meta 88%) → GUARDRAIL.** `cupos_ofertados` es un tope físico/contractual por sede-canal-evento; la meta 88% es un piso operativo pactado (no un objetivo de rentabilidad). Operar muy por debajo desperdicia capacidad ya comprometida con la sede; no puede superar 100% (tope duro). No es en sí un resultado financiero.
- **Margen % → RESULTADO.** Mide directamente la rentabilidad de cada canal-evento tras costo variable — es el resultado financiero que finalmente interesa a la organización.
- **Ticket promedio (S/ por orden) → EFICIENCIA.** Mide cuánto valor se extrae por transacción procesada (proxy de mezcla de precio/tamaño de compra); es un indicador de productividad comercial, ni el resultado final ni un límite duro de capacidad.

**Por qué mejorar uno no garantiza mejorar los otros (evidencia del propio CSV, asociación no causal):**
- Ocupación vs Margen: correlación r = **−0.43** entre `ocupacion_fila_pct` y `margen_fila_pct` (n=216 filas) — asociación negativa moderada: las filas con mayor ocupación tienden a mostrar menor margen. Esto es **asociación observacional, no causalidad**; posibles confusores: el **canal** (Taquilla concentra el mayor margen ponderado, 59.20%, con la menor ocupación ponderada, 81.15%; App concentra la mayor ocupación ponderada, 94.51%, con margen algo menor, 56.18% — probablemente por comisiones de plataforma o descuentos digitales que Taquilla física no paga), la mezcla de eventos/sedes y la estacionalidad. Coincide con el ejemplo del enunciado: "descuento sube ocupación pero baja margen" es *consistente* con lo observado, aunque no probado causalmente aquí.
- Ticket vs Ocupación: correlación r = **+0.42** (positiva, moderada) — **contradice** la intuición ingenua de "precio alto ahuyenta demanda" citada en el enunciado ("premium sube ticket pero baja ocupación"). En este CSV, el canal con mayor ticket promedio (App, S/ 78.72/orden) es también el de mayor ocupación ponderada (94.51%), probablemente confundido por el **canal** mismo (App es estructuralmente el canal dominante, no necesariamente por un efecto de precio puro). Esto es un hallazgo de auditoría en sí mismo: **no asumir un trade-off conceptual sin verificarlo en los datos** — aquí el riesgo medible y accionable es Ocupación-vs-Margen, no Ticket-vs-Ocupación.
- Ticket vs Margen: r = **−0.16** (débil) — evidencia insuficiente para una conclusión fuerte; Taquilla es un valor atípico (ticket más bajo, S/ 66.04, y margen más alto, 59.20%) que domina el signo; controlando por canal la relación podría invertirse o desaparecer.

**4) Límite / trade-off.** Ninguna correlación aquí prueba causalidad — son asociaciones a nivel evento-canal con canal, sede y estacionalidad como confusores no controlados. Antes de tomar una decisión de pricing/descuento basada en "subir ocupación baja margen", se necesitaría un diseño que aísle el efecto del canal (p. ej. comparar el mismo canal en eventos con y sin promoción) en vez de comparar canales estructuralmente distintos entre sí.



---
## Pregunta 3 — LOD, total visible y filtros



**1) Concepto técnico.** Dos formas de calcular "participación del canal dentro de su departamento" que usan denominadores con reglas de filtrado distintas:

- **`{ FIXED [departamento] : SUM([ventas_soles]) }`** — expresión de nivel de detalle (LOD) *fija*: calcula el total de ventas del departamento **ignorando los filtros de dimensión** que haya en la hoja (fecha, canal, etc.), porque en el orden de operaciones de Tableau los filtros de dimensión normales se aplican **después** de las LOD FIXED. Solo un **filtro de contexto** se aplica antes y sí recorta lo que FIXED ve.
- **`TOTAL(SUM([ventas_soles]))`** — **table calculation**: sí respeta los filtros de dimensión (se calculan sobre las marcas que ya quedaron en el panel después de filtrar), porque los filtros normales actúan antes que los table calcs.

**Declaración de partición/addressing de `TOTAL()` (obligatoria):** en una vista con `departamento` en filas/paneles y `canal` en columnas dentro de cada panel, `TOTAL(SUM([ventas_soles]))` debe **direccionarse (addressing) por `canal`** y **particionarse por `departamento`** — es decir, recalcula la suma recorriendo las marcas de canal *dentro de cada panel de departamento por separado*. Si `departamento` no se declara como partición (p. ej. ambos campos quedan en el mismo eje sin paneles separados), `TOTAL()` sumaría canal Y departamento juntos, devolviendo el gran total del festival en vez del total por departamento — error común.

**2) Evidencia (num/den declarados).**
- Participación real de cada canal dentro de su departamento (12 departamentos, num=SUM ventas canal-depto, den=SUM ventas depto): App oscila entre 53.08% (Junín) y 54.55% (Ayacucho); Web entre 28.37% (Ucayali) y 30.27% (Lambayeque); Taquilla entre 16.28% (Ayacucho) y 18.04% (Junín) — **muy estable entre departamentos**, coherente con el share nacional (App 53.7%, Web 29.3%, Taquilla 17.0%; num=SUM ventas canal, den=SUM ventas total = S/ 10 473 741.35).
- Comparación FIXED vs TOTAL panel para Lima-App: **FIXED** (6 eventos, universo histórico completo) → num=S/ 987 279.17, den=S/ 1 823 558.36 → **54.14%**. **TOTAL panel visible** (solo 4 eventos con `fecha_evento < 18-jul-2026`, filtro de fecha como filtro de dimensión) → num=S/ 682 899.45, den=S/ 1 278 780.13 → **53.40%**. Los denominadores difieren (S/ 1 823 558.36 vs S/ 1 278 780.13) porque miden universos distintos (6 eventos vs 4 eventos).

**3) Decisión de diseño — el selector de fecha con 2 lecturas.**
El dashboard debe ofrecer dos medidas calculadas en paralelo, cada una con su título aclaratorio:
- *"Participación histórica del canal en el departamento"* = `{ FIXED [departamento] : SUM([ventas_soles]) }` como denominador → **no se mueve** aunque el usuario cambie el filtro de fecha (a menos que ese filtro se convierta en filtro de **contexto**, en cuyo caso SÍ recorta lo que ve el FIXED, porque el contexto se evalúa antes que la LOD).
- *"Participación dentro del periodo visible"* = `TOTAL(SUM([ventas_soles]))` como denominador → se recalcula cada vez que el usuario mueve el filtro de fecha o de canal, porque son filtros de dimensión normales que sí afectan a los table calcs.

Titulares válidos (no se contradicen — miden universos distintos):
- Con FIXED: **"App concentra ~54% de las ventas históricas de Lima (temporada completa, 6 eventos)."**
- Con TOTAL(): **"En lo que va de la temporada (4 eventos ya realizados al 18-jul-2026), App representa 53.4% de las ventas visibles de Lima."**

**Símil pandas (groupby transform):**
```python
# FIXED -> ignora cualquier filtro de dimensión posterior
df['ventas_depto_FIXED'] = df.groupby('departamento')['ventas_soles'].transform('sum')

# TOTAL() del panel visible -> se recalcula DESPUÉS de aplicar el filtro de dimensión
visible = df[df['fecha_evento'] < '2026-07-18']              # filtro de dimensión (fecha)
visible['ventas_depto_TOTAL'] = visible.groupby('departamento')['ventas_soles'].transform('sum')
```

**4) Límite / trade-off.** Convertir `fecha_evento` o `canal` en filtro de **contexto** para que también recorte el FIXED tiene costo de performance (Tableau debe materializar una tabla temporal por cada combinación de contexto) y cambia semánticamente la pregunta: "histórico completo" deja de existir si todo se vuelve contexto. La recomendación es dejar **un** selector de fecha como filtro normal de dimensión (alimenta TOTAL/panel visible) y **no** tocar el filtro de contexto salvo que el usuario explícitamente pida "recalcular también el histórico" — de lo contrario los dos titulares dejan de ser comparables entre sí.



**Figura 1** responde la tarea analítica **parte-todo** con el denominador correcto: `SUM(ventas_soles)` total del festival (S/ 10 473 741.35). App = 53.7%, Web = 29.3%, Taquilla = 17.0% (suman 100% porque el denominador es un total real, a diferencia de la torta del practicante). Se usa barra en vez de torta porque con solo 3 categorías la barra ordenada permite comparar magnitudes con precisión (longitud vs ángulo/área), y deja espacio para anotar el valor exacto.



**Figura 2** responde la tarea analítica **comparar**: margen ponderado por canal (num=`SUM(ventas_soles)-SUM(costo_variable_soles)`, den=`SUM(ventas_soles)`, por canal) frente a la ocupación ponderada de cada canal como anotación de contexto. Se ve el trade-off del caso: **Taquilla** tiene el mayor margen (59.20%) pero la menor ocupación (81.15%); **App** tiene la mayor ocupación (94.51%) con margen algo menor (56.18%) — consistente con la asociación negativa (r=−0.43) documentada en la Pregunta 2.



---
## Pregunta 4 — Parámetro no es filtro

**1) Concepto técnico.** Un **filtro** decide qué **filas** entran al cálculo (subconjunta los datos); un **parámetro** decide **cómo** se calcula o se dibuja algo, sin quitar ninguna fila — es una variable global que se referencia dentro de un campo calculado y afecta a toda la vista de manera consistente. Si algo debe cambiar el eje/medida mostrada o un umbral de comparación **sin** alterar qué datos entran, debe ser parámetro; si algo debe **excluir** datos (un canal, un rango de fechas, un departamento), debe ser filtro (o filtro de contexto si además debe recortar una LOD FIXED, ver Pregunta 3).

**2) Diseño de controles.**

*(a) Parámetro selector de medida* — `Medida Seleccionada` (tipo string, lista: `Ventas`, `Ocupación`, `Margen`), usado en un campo calculado:
```
-- Tableau
Medida (según parámetro) =
CASE [Medida Seleccionada]
WHEN 'Ventas'     THEN SUM([ventas_soles])
WHEN 'Ocupación'  THEN SUM([ingresos_validados]) / SUM([cupos_ofertados]) * 100
WHEN 'Margen'     THEN (SUM([ventas_soles]) - SUM([costo_variable_soles])) / SUM([ventas_soles]) * 100
END
```
```python
# pandas símil
def medida(df, seleccion):
    if seleccion == 'Ventas':
        return df['ventas_soles'].sum()
    elif seleccion == 'Ocupación':
        return df['ingresos_validados'].sum() / df['cupos_ofertados'].sum() * 100
    elif seleccion == 'Margen':
        num = df['ventas_soles'].sum() - df['costo_variable_soles'].sum()
        return np.where(df['ventas_soles'].sum()==0, np.nan, num/df['ventas_soles'].sum()*100)
```

*(b) Parámetro numérico de meta* — `Meta Ocupación %` (tipo float, default = 88, rango sugerido 70–100):
```
-- Tableau
Cumple Meta? = SUM([ingresos_validados])/SUM([cupos_ofertados])*100 >= [Meta Ocupación %]
```
```python
meta = 88.0  # editable
cumple = occ_weighted >= meta
```

**Evidencia anclada (no solo rangos de diseño):** con `meta = 88` y la ocupación ponderada global del festival calculada en la Pregunta 1 = **90.27%**, el semáforo `Cumple Meta?` evalúa **90.27 >= 88 → TRUE → CUMPLE** (buffer = +2.27 pp). Si el usuario mueve el parámetro a, por ejemplo, 92%, el mismo cálculo cambiaría a **NO CUMPLE** (90.27 < 92) sin quitar ni una fila de datos — la prueba de que es parámetro y no filtro es justamente que ningún `N` de filas cambia, solo cambia el resultado del semáforo.

**Qué debe ser parámetro vs filtro (checklist del caso):**
| Control | Tipo | Por qué |
|---|---|---|
| Ventas / Ocupación / Margen (medida a graficar) | **Parámetro** | cambia el cálculo del eje, no quita filas |
| Meta de ocupación (88%) | **Parámetro** | mueve una línea de referencia y recalcula un semáforo, no filtra |
| `canal` (para explorar subconjuntos) | **Filtro** (o filtro de contexto si alimenta un FIXED, ver P3) | excluye filas |
| `fecha_evento` / rango de fechas | **Filtro** (dimensión, o contexto según la lectura que se quiera, ver P3) | excluye filas |
| `departamento` | **Filtro** | excluye filas |

**3) Reference line con la meta.** En Tableau: `Analysis > Reference Line > Add Reference Line`, tipo **Constant**, valor = `[Meta Ocupación %]` (referenciando el parámetro directamente, o vía un campo calculado auxiliar `Meta (línea)` = `[Meta Ocupación %]` si la versión de Tableau lo requiere). Etiqueta: `"Meta: " + STR([Meta Ocupación %]) + "%"`. Así, cuando el usuario cambia el parámetro (p. ej. de 88% a 90% para escenarios más exigentes), la línea y el semáforo se recalculan solos, sin tocar ningún filtro ni perder filas.

**4) Evitar comparar unidades incompatibles en dual axis.** `ventas_soles` (rango ~S/ 12 000–200 000 por fila) y `margen_fila_pct` u `ocupacion_fila_pct` (rango 0–100) **no deben compartir el mismo eje sincronizado**: si se sincronizan, una barra de soles aplastaría visualmente la línea de porcentaje (o viceversa) y la altura de las marcas dejaría de representar la magnitud real de cada serie. Reglas:
- Si se usa dual axis, **NO sincronizar** los ejes (`Synchronize Axis` desmarcado) y usar dos escalas independientes, con título y color de eje claramente diferenciados (soles a la izquierda, % a la derecha).
- Alternativa más segura: evitar el dual axis y usar **small multiples** (dos gráficos lado a lado, uno en soles y otro en %) — tarea analítica: **comparar** ambas medidas por canal/periodo (o **ver tendencia** si el eje X es tiempo) sin que la escala de una serie distorsione la lectura de la otra — o normalizar ambas series a un índice común (p. ej. % de la meta) si de verdad se necesita un solo eje.
- Nunca usar dual axis para "combinar" ventas y ocupación como si fueran comparables en magnitud — solo para verlas en el mismo eje X (tiempo/canal) con ejes Y independientes.



### BITÁCORA (5 frases)

1. **Lectura inicial:** App domina con 35.7% de "éxito", suma de porcentajes de fila sin sentido.
2. **KPI decisor:** Ocupación ponderada del festival = SUM(`ingresos_validados`)/SUM(`cupos_ofertados`)×100, periodo temporada completa (abril–agosto 2026, N=216 filas/72 eventos), segmento por canal, comparada contra la meta fija `meta_ocupacion_pct` = 88%.
3. **Giro analítico:** se cambió el denominador de "conteo de filas" (mean-of-ratios, `AVG(ocupacion_fila_pct)`) a "suma real de cupos" (ratio-of-sums, `SUM(ingresos_validados)/SUM(cupos_ofertados)`), y se abrió la segmentación por canal, revelando que Taquilla (81.15% ponderado, 61/72 filas bajo meta) es el canal que arrastra el promedio hacia abajo mientras App (94.51%) lo sostiene.
4. **Lectura revisada:** Ocupación ponderada global 90.27% cumple la meta 88%, pero Taquilla queda rezagada con 81.15%.
5. **Consecuencia:** en vez de "celebrar" el 35.7% de App como éxito aislado, taquilla debe priorizar reforzar Taquilla física (promoción, reasignación de cupos) antes de agosto; el próximo corte real (ventas de los eventos de agosto, aún no ocurridos a la fecha del examen) es la evidencia futura que podría volver a cambiar esta decisión si Taquilla revierte su rezago o si App satura su capacidad y empieza a perder margen adicional.



<br>

---

> 📓 **Computación y figuras ejecutadas:** [`notebook/caso2.ipynb`](notebook/caso2.ipynb)

# Operación ChasquiFest — CASO 2: Logística
## Auditoría de visualización e inferencia — Caravana entre 12 sedes

**Auditor:** análisis reproducible sobre `data/caso2_logistica_chasquifest.csv`
**Granularidad de los datos:** una fila = un envío. n = 1728 envíos, 12 sedes (departamento/macrozona destino), 18 semanas (`semana_inicio` 2026-03-02 a 2026-06-29), 3 transportistas (Apu Express, Río Rápido, Costa Norte), 3 vehículos (Van, Moto, Camión), 3 macrozonas (Costa, Sierra, Selva).

Cada celda de código carga o deriva los números que se citan en el texto — no hay cifras "de memoria": todo número en las respuestas de abajo tiene su celda de cálculo correspondiente arriba.


---
# Pregunta 1 — Auditoría visual e inferencial

El gráfico original: **12 líneas superpuestas, 12 colores, doble eje (tardanza % vs lluvia mm), y una línea roja de "lluvia promedio" rotulada "prueba científica"** de que la lluvia causa todas las demoras. A continuación, cuatro fallas **distintas e independientes**, cada una con concepto, evidencia numérica, decisión de corrección y límite/trade-off de la corrección.

## (a) Falla de selección de gráfico — tarea equivocada ("espagueti")

1. **Concepto técnico:** superponer 12 series temporales continuas en un único plano cartesiano ("spaghetti chart") es un antipatrón de *selección de gráfico*: la tarea analítica real del gerente no es "leer 12 tendencias que se cruzan simultáneamente" sino **comparar la magnitud de tardanza entre sedes y detectar cuál se desvía de la meta** — una tarea de comparación categórica, no de trazado continuo superpuesto.
2. **Evidencia concreta:** 12 sedes × 18 semanas = 216 puntos sede-semana; con exactamente **n=8 envíos por sede-semana** (min=mediana=max=8, verificado arriba), cada tasa semanal salta en incrementos discretos de **12.5 puntos porcentuales** (0%, 12.5%, 25%, …, 87.5%). Con 12 líneas saltando en esos escalones y cruzándose constantemente, es imposible discriminar visualmente cuál línea pertenece a cuál sede en los cruces.
3. **Decisión de diseño:** reemplazar por **pequeños múltiplos** (12 paneles, uno por sede) con eje compartido, o por **serie focal + 11 en gris de contexto** (implementado en la Pregunta 3).
4. **Límite/trade-off:** los pequeños múltiplos sacrifican la comparación punto-a-punto directa entre dos sedes arbitrarias (exige memoria visual entre paneles); se mitiga ordenando los paneles por tasa agregada y compartiendo el eje Y.

## (b) Falla de codificación perceptual — 12 colores + doble eje

1. **Concepto técnico:** el canal de **color categórico** satura la capacidad de discriminación humana (~6-8 tonos distinguibles simultáneamente); el **doble eje Y** (tardanza % en un eje, lluvia mm en otro) permite escalar cada eje de forma arbitraria hasta que dos curvas *parezcan* moverse juntas, sin que exista relación real entre ellas — es el "dual-axis trick".
2. **Evidencia concreta:** se necesitan 12 colores para 12 sedes, muy por encima del límite perceptual seguro; el eje de lluvia (rango observado 0–~15 mm, media 2.5–4.7 mm según macrozona) puede reescalarse para que su curva "toque" visualmente la curva de tardanza (rango 0–100%) **aunque corr(lluvia_mm, minutos_reales) = 0.156** — la superposición visual no refleja la fuerza real (débil) de la relación.
3. **Decisión de diseño:** eliminar el doble eje; usar un solo eje Y (0–100% tardanza) por panel; si se quiere mostrar lluvia, hacerlo en un canal separado (panel aparte o barras tenues en la MISMA escala relativa 0–100%, nunca con eje libre).
4. **Límite/trade-off:** separar en paneles impide la lectura "de un vistazo" de ambas variables juntas; obliga a comparar por yuxtaposición (paneles alineados en X) en vez de superposición — más honesto, pero requiere más espacio y disciplina de alineación temporal.

## (c) Falla de accesibilidad — color como único canal de identificación

1. **Concepto técnico:** codificar 12 categorías **solo por matiz (hue)** falla bajo daltonismo (deuteranopía/protanopía, ~8% de hombres) y en impresión/escala de grises, donde matices distintos pero de luminancia similar colapsan al mismo gris.
2. **Evidencia concreta:** con 12 sedes coloreadas, pares de tonos (p. ej. verdes de Selva vs rojos de Sierra) se vuelven casi idénticos bajo simulación de daltonismo; en escala de grises, el rojo de "lluvia" y el color de "tardanza" —pensados para verse como polos opuestos— pueden converger a grises de luminancia parecida, perdiéndose exactamente el contraste que el gráfico pretende comunicar.
3. **Decisión de diseño:** **etiquetado directo** (texto) en vez de leyenda de color; reservar el color solo para **1 serie focal + resto en gris neutro** (redundancia de canal: posición + etiqueta directa, no solo color); validar con simulador de daltonismo antes de publicar.
4. **Límite/trade-off:** el etiquetado directo con 12 series simultáneas sigue compitiendo por espacio si se muestran todas a la vez; solo escala bien cuando se reduce a foco+contexto (1 serie resaltada vs 11 de fondo), como se implementa en la Pregunta 3.

## (d) Falla inferencial — causalidad desde asociación observacional

1. **Concepto técnico:** yuxtaponer una serie de "lluvia promedio" con la tasa de tardanza y rotularla **"prueba científica"** es una falacia de correlación→causalidad, reforzada visualmente por el doble eje alineado. Una asociación observacional —incluso si fuera fuerte— no aísla causa sin control de confusores ni diseño experimental/randomizado.
2. **Evidencia concreta:** corr(lluvia_mm, minutos_reales) = **0.156** (R²≈2.4%, DÉBIL) frente a corr(distancia_km, minutos_reales) = **0.922** (R²≈85%, FUERTE); y distancia_km y lluvia_mm son prácticamente independientes entre sí (corr=0.001), por lo que la distancia **no** es la vía indirecta por la que la lluvia "parecería" actuar sobre los minutos crudos. La distancia explica ~35 veces más varianza de minutos_reales que la lluvia.
3. **Decisión de diseño/analítica:** retirar la etiqueta "prueba científica"; reportar corr(lluvia, minutos_reales) **junto a** corr(distancia, minutos_reales) en el mismo texto para dar contexto de magnitud relativa; usar lenguaje de asociación ("se observa una diferencia promedio de X minutos…") en vez de causal.
4. **Límite/trade-off (matiz honesto):** aunque el R² de lluvia sobre los **minutos crudos** es bajo, al mirar el **incumplimiento binario de SLA** (`tardanza_flag`) la brecha es mayor: 32.7% = 411/1256 envíos sin lluvia vs 76.5% = 361/472 envíos con lluvia (corr punto-biserial lluvia_flag–tardanza_flag = 0.392), y esa brecha **persiste dentro de cada tercil de distancia** (~32-34% sin lluvia vs ~72-81% con lluvia en corta/media/larga distancia — ver cálculo en Pregunta 4). Es decir: la lluvia **no es irrelevante** para el incumplimiento de SLA, pero seguimos sin poder llamarla "causa" sin controlar transportista, vehículo y factores no medidos (tráfico, hora del día, prioridad de envío). Ver desarrollo completo en Pregunta 4.


---
# Pregunta 2 — La pregunta dicta el gráfico

## Vista 1 — Comparar mediana y dispersión de `minutos_reales` entre transportistas, dentro de cada macrozona

1. **Concepto técnico / tarea analítica declarada:** *comparar distribuciones* (no un solo promedio puntual) entre 3 grupos (transportista) anidados en 3 facetas (macrozona) → marca = **box plot** (posición = mediana y cuartiles; longitud = caja = IQR), que es el estándar para mostrar tendencia central **y** dispersión simultáneamente.
2. **Evidencia con números reales** (celda "Evidencia para Vista 1"): medianas por transportista×macrozona van de 166.1 min (Apu Express–Sierra, n=280) a 197.75 min (Costa Norte–Sierra, n=250); el IQR (dispersión) va de ~97 min (Apu Express–Selva) a ~140 min (Costa Norte–Sierra). El tamaño de cada celda varía de n=121 (Río Rápido–Selva) a n=280 (Apu Express–Sierra).
3. **Decisión de diseño:** eje Y = minutos_reales (**posición**, canal más preciso de la jerarquía posición > longitud > ángulo > área > color); eje X = transportista; **facet por macrozona con eje Y compartido** (mismo rango 0–y_max en los 3 paneles) para permitir comparación directa entre paneles; color de la caja = transportista, **redundante** con la posición en X (no es el único canal de identificación, cumple accesibilidad); mediana marcada con línea negra gruesa; outliers mostrados como puntos (no eliminados).
4. **Límite/trade-off:** el box plot esconde la forma exacta de la distribución (p. ej. bimodalidad) y minimiza la lectura de N si no se anota explícitamente — aquí n varía de 121 a 280 por celda, anotado en las etiquetas del eje X para no sobre-interpretar cajas con pocos datos.

## Vista 2 — Relación `distancia_km` ↔ `minutos_reales`

1. **Concepto técnico / tarea analítica declarada:** *evaluar la fuerza y forma de una relación entre dos variables cuantitativas continuas* → marca = **scatter plot** (posición X-Y, el canal más preciso posible para 2 cuantitativas; muy superior a intentar comprimir esto en líneas/dual-axis como en el gráfico original).
2. **Evidencia con números reales:** corr = **0.922**, R² = **84.9%**; recta OLS *y = 1.43·x + 60.1* (p≈0, n=1728). Tratamiento de outliers: regla 1.5×IQR marca **62 outliers** en minutos_reales (>444.1 min, 3.6%) y **49 outliers** en distancia_km (>260.8 km, 2.8%).
3. **Decisión de diseño:** transparencia (alpha=0.25) para mitigar sobre-trazado (*overplotting*) de 1728 puntos; línea de tendencia OLS anotada con su ecuación y R²; los outliers **no se eliminan** — se resaltan con marcador y color distintos (triángulo vermellón) porque representan casos reales de negocio (p. ej. camiones a distancias largas en Selva) que el gerente necesita ver, no ocultar.
4. **Límite/trade-off:** la recta OLS asume relación lineal y homocedástica; a distancias muy largas la dispersión podría crecer (heterocedasticidad) — antes de usar esta recta para pronóstico habría que revisar residuales por tramo de distancia; además, eliminar outliers "para limpiar el gráfico" sin justificación operativa ocultaría exactamente los envíos que más le cuestan a la operación.

## Elección de KPI principal: tasa de tardanza vs SLA (con P90 como guardrail)

1. **Concepto técnico:** un KPI operacional debe ser **accionable frente a una meta**, no solo descriptivo de una distribución.
2. **Evidencia** (periodo: 18 semanas, `semana_inicio` 2026-03-02 a 2026-06-29): tasa de tardanza agregada = 772/1728 = **44.68%** vs meta 20% (más del doble); P90 por transportista (Apu Express 312.8 min, Costa Norte 354.2 min, Río Rápido 349.9 min) muestra la **cola**; la media (193.8 / 212.8 / 212.3 min) está sesgada por outliers y por la mezcla de distancias; la mediana (175.3 / 187.4 / 187.3 min) es robusta pero esconde justamente esa cola.
3. **Decisión:** recomendar la **tasa de tardanza vs SLA** (`SUM(tardanza_flag)/COUNT(envio_id)`) como KPI decisor primario — es binario, está directamente ligado a la meta operativa del 20% y admite una reference line clara (Pregunta 4); usar **P90** como guardrail de cola, con umbral propuesto **meta P90 ≤ 300 min** (los tres transportistas ya lo superan: 312.8–354.2 min), para detectar si el 10% peor de envíos se dispara aunque la mediana luzca aceptable.
4. **Límite — qué esconde cada estadístico descartado:** la **media** es sensible a outliers y a cambios en el mix de rutas (una semana con más envíos largos la mueve sin que cambie el desempeño real por ruta); la **mediana** esconde la cola (el P90 puede duplicarse sin que la mediana se mueva); la **tasa de tardanza sola** no dice *cuánto* tarde llega un envío (por eso se complementa con P90); ninguna de las cuatro controla por transportista/macrozona por sí sola — deben reportarse siempre segmentadas, no solo en agregado.

**Fórmulas (Tableau + pandas):**
- Mediana por celda: Tableau `{ FIXED [Macrozona],[Transportista] : MEDIAN([Minutos Reales]) }` — pandas `df.groupby(['macrozona','transportista'])['minutos_reales'].median()`
- P90 por transportista: Tableau `{ FIXED [Transportista] : PERCENTILE([Minutos Reales], 0.9) }` (campo calculado con agregación de percentil) — pandas `df.groupby('transportista')['minutos_reales'].quantile(0.9)`
- Tasa de tardanza por transportista: Tableau `SUM([Tardanza Flag]) / COUNT([Envio Id])` con `[Transportista]` en Filas — pandas `df.groupby('transportista')['tardanza_flag'].agg(['sum','count'])` y luego `sum/count`


---
# Pregunta 3 — Doce series sin espagueti

**Tarea analítica declarada:** seguir la *evolución semanal de la tasa de tardanza por sede* para detectar cuáles sedes están sistemáticamente por encima de la meta, sin perder la capacidad de comparar magnitudes entre sedes.

1. **Concepto técnico:** con 12 series de solo 18 puntos cada una y ruido alto (ver punto 2), superponerlas en un único plano es un antipatrón de selección de gráfico. La solución es **pequeños múltiplos** (facet por sede) **combinado con foco+contexto** (la sede de cada panel resaltada en color, las otras 11 dibujadas en gris de fondo como referencia) — así se preserva tanto la comparación "dentro de panel vs meta" como la comparación "entre sedes" sin espagueti ni leyenda de 12 colores.
2. **Evidencia con números reales:** 12 sedes × 18 semanas = 216 celdas sede-semana, cada una con **exactamente 8 envíos** (min=mediana=max=8), por lo que la tasa semanal de una sede solo puede tomar valores en **incrementos de 12.5 puntos porcentuales** (0%, 12.5%, …, 87.5%): un solo envío que cruza el umbral mueve la tasa 12.5 pp de golpe. Con 8 envíos/sede-semana × 18 semanas = 144 envíos por sede, la sede con peor tasa agregada es **SED-01 (Lima, Costa) con 61.1% = 88/144**; la mejor es **SED-04 (Chiclayo, Costa) con 28.5% = 41/144** (ver tabla de la celda anterior).
3. **Decisión de diseño (comparabilidad):**
   - **Escala compartida 0–100%** en los 12 paneles (nunca autoescalada) — condición no negociable para que la altura de cada línea sea comparable entre paneles.
   - **Etiquetado directo**: el nombre de la sede y su tasa agregada se imprimen como título del panel (texto), no hay leyenda de color para 12 series.
   - **Supervivencia a daltonismo/escala de grises:** el significado no depende del matiz — depende de la **posición** de la línea coloreada respecto a la línea de referencia (meta 20%, línea punteada) y de la **etiqueta de texto** directa; en escala de grises, la línea focal (más gruesa, con marcadores) sigue siendo distinguible del fondo gris tenue por **grosor y opacidad**, no solo color.
   - **Reference line de meta (20%)** repetida en cada panel para juicio inmediato de "por encima/por debajo".
4. **Límite/trade-off — el peligro de autoescalar:** si cada panel usara su **propio eje Y** ajustado al rango local de esa sede, una sede de bajo desempeño real (ej. SED-04, 28.5% agregado, con variación semana a semana pequeña en términos absolutos) podría verse tan "dramática" en su panel como SED-01 (61.1%) — porque el eje se estira para llenar el espacio del panel. Esto es una **ilusión creada por el diseño (autoescalado), no por la magnitud real de los datos** — motivo exacto por el que se fija la escala compartida 0–100%. Además, con n=8/semana, **un solo pico de una semana aislada no debe leerse como tendencia**: se recomienda no interpretar un salto de 12.5 pp sin mirar al menos 3-4 semanas consecutivas o el agregado del panel.

**Table calc declarado (partición + addressing):** el ranking de paneles usa `RANK(SUM([Tardanza_flag])/COUNT([Envio_id]))` con **Partición = ninguna (toda la tabla es una sola partición)** y **Addressing = [Sede_id]** (recorre las 12 sedes, sin reinicio) — de ahí el orden de peor a mejor en la figura.


---
# Pregunta 4 — Declarar no es inferir

## KPI decisor: tasa de tardanza agregada vs meta

1. **Concepto técnico:** una **reference line** de meta convierte una tasa descriptiva en un juicio operativo binario (¿cruza o no cruza la meta?) — no es un promedio ilustrativo, es un umbral de decisión.
2. **Evidencia con números reales:** `num` = envíos con `tardanza_flag=1` = **772**; `den` = envíos totales = **1728**; **tasa de tardanza agregada = 772/1728 = 44.68%**. Periodo: 18 semanas, `semana_inicio` 2026-03-02 a 2026-06-29. Segmento: agregado, todas las sedes/transportistas. Meta operativa declarada: **20%**. El KPI está **24.68 puntos porcentuales por encima de la meta** (2.23× la meta).
3. **Decisión:** dibujar una **reference line horizontal en 20%** sobre la serie/barra de tasa de tardanza (ver Figura D, panel izquierdo) y reportar siempre `num/den` junto al porcentaje — nunca el porcentaje solo. Fórmula Tableau: `SUM([Tardanza_flag]) / COUNT([Envio_id])`, con reference line constante en `0.20` (campo calculado `Meta = 0.20` o parámetro). Pandas: `df['tardanza_flag'].sum() / len(df)`.
4. **Límite:** la tasa agregada mezcla transportistas muy distintos (Apu Express 32.4% = 211/651 vs Río Rápido 57.2% = 269/470) y sedes muy distintas (SED-04 28.5% = 41/144 – SED-01 61.1% = 88/144) — cruzar la meta en agregado no dice **dónde** actuar; siempre debe acompañarse de la vista segmentada (Pregunta 2/3) antes de tomar una decisión de asignación.

## Trend line lluvia↔demora: pregunta distinta, no causal

1. **Concepto técnico:** una trend line (OLS) entre `lluvia_mm` y `minutos_reales` responde a la pregunta **"¿cuál es la mejor recta lineal que resume cómo covarían estas dos variables en los datos observados?"** — una pregunta **descriptiva/asociativa** (¿cuánto se mueve Y en promedio por unidad de X, en esta muestra?), **no** la pregunta causal **"¿si yo pudiera cambiar la lluvia (manteniendo todo lo demás fijo), cambiaría el tiempo de entrega?"** Esta segunda pregunta requiere un diseño que aísle la lluvia de sus co-variables (experimento o cuasi-experimento), algo que un CSV observacional de un período no ofrece.
2. **Evidencia:** OLS lluvia→minutos_reales: *y = 2.01·lluvia_mm + 198.2* (r=0.156, R²=2.4%, p=6.8e-11 — significativo pero de **efecto pequeño** sobre los minutos crudos). Sin embargo, sobre `tardanza_flag` la asociación naive es mayor: 32.7% = 411/1256 (sin lluvia) vs 76.5% = 361/472 (con lluvia), y esa brecha de ~38-48 puntos porcentuales **persiste dentro de cada tercil de distancia** (corta/media/larga) — ver celda de estratificación arriba. Transportista y vehículo están balanceados entre lluvia=0/1 (no son confusores fuertes de la exposición); macrozona sí varía en incidencia de lluvia (Selva 41.7% = 180/432 vs Costa 16.5% = 95/576) pero su tasa de tardanza propia es casi plana (43.7%-45.7%, es decir Selva 189/432 a Costa 263/576), por lo que tampoco explica la brecha por sí sola.
3. **Supuestos que revisaría antes de confiar en la trend line:**
   - **Linealidad:** ¿el efecto de la lluvia es realmente lineal en mm, o hay un umbral (p. ej. "llueve o no llueve" importa más que los mm exactos)? El salto grande en `tardanza_flag` vs el R² bajo en minutos crudos sugiere que el mecanismo real puede ser un efecto de umbral sobre el *ratio* minutos_reales/objetivo (corr(lluvia_mm, ratio)=0.489, mucho mayor que corr(lluvia_mm, minutos_reales)=0.156), no una recta continua.
   - **Confusores:** distancia (r=0.922 con el resultado, pero r=0.001 con lluvia → no es confusor clásico de la relación lluvia-minutos, aunque sí domina la varianza total); transportista y vehículo (balanceados, chequeado arriba); macrozona (asociada a la exposición, tasa de tardanza propia casi plana); **factores no medidos** (tráfico, hora del día, prioridad de envío, día de semana) que podrían co-variar con la lluvia y explicar parte de la brecha.
4. **Por qué ni una pendiente ni un buen R² demuestran causalidad:** los datos son **observacionales** (nadie asignó aleatoriamente qué envíos "reciben" lluvia); un R² alto solo certifica buen ajuste dentro de la muestra, no aislamiento de la causa. Aquí, además, el R² de lluvia sobre minutos crudos es **bajo** (2.4%) precisamente porque distancia domina la varianza (85%) — mezclar ambas señales en un gráfico de doble eje, como hacía el original, es lo que producía la ilusión de "prueba científica".

## BITÁCORA (5 frases)

1. **Lectura inicial (≤15 palabras):** "La lluvia parece causar toda la tardanza; el gráfico de 12 líneas lo prueba."
2. **KPI decisor:** Tasa de tardanza vs SLA — Tableau `SUM([Tardanza_flag])/COUNT([Envio_id])`, pandas `df['tardanza_flag'].sum()/len(df)` — periodo 2026-03-02 a 2026-06-29 (18 semanas) — segmento agregado y por transportista/sede — meta 20%.
3. **Giro analítico:** al descomponer por distancia y transportista, distancia explica 84.9% de la varianza de minutos_reales (r=0.922) frente a 2.4% de la lluvia (r=0.156); Río Rápido (57.2% = 269/470 tardíos) casi duplica a Apu Express (32.4% = 211/651) — el problema es mayormente operativo (ruteo/transportista), no meteorológico, aunque la lluvia sigue asociada al incumplimiento de SLA dentro de cada tercil de distancia.
4. **Lectura revisada (≤15 palabras):** "Distancia y transportista se asocian con la tardanza; la lluvia es secundaria pero no nula."
5. **Consecuencia:** la decisión que cambia es priorizar la renegociación de rutas/SLA con Río Rápido y Costa Norte y revisar la asignación en distancias largas, en vez de invertir primero en "gestión de lluvia"; el dato que **refutaría** esta lectura revisada sería una regresión múltiple (lluvia_flag + distancia_km + transportista + vehículo + macrozona + semana) donde el coeficiente de lluvia_flag **deje de ser significativo** tras controlar todo lo demás, o —mejor aún— un experimento/cuasi-experimento que compare la misma ruta/transportista/vehículo en semanas de lluvia vs sin lluvia y muestre que la tardanza no cambia; si en cambio el coeficiente de lluvia se mantiene significativo y sizable tras esos controles, habría que reincorporar la lluvia como factor operativo real (no como "prueba científica" única, sino como covariable relevante junto a distancia y transportista).



<br>

---

> 📓 **Computación y figuras ejecutadas:** [`notebook/caso3.ipynb`](notebook/caso3.ipynb)


# CASO 3 — Auditoría de Asistencia Mensual (ChasquiFest)
### Operación ChasquiFest · Auditor de Visualización

**Dataset:** `data/caso3_asistencia_mensual_chasquifest.csv` — granularidad **una fila por mes × sede** (372 filas = 31 meses × 12 sedes, ene-2024 a jul-2026).

**Campos clave:** `mes`, `anio`, `numero_mes`, `sede_id`, `dias_observados`/`dias_del_mes` (completitud), `cobertura_periodo_pct`, `asistentes` (volumen **observado**, no proyectado), `meta_asistentes` (ya ajustada a los días observados), `evento_contexto` (marca el quiebre ficticio).

**El disparador del caso:** el editor compara julio-2026 (corte a 12 días) contra julio-2025 **completo** (31 días) y anuncia una caída de 57%. Esta auditoría verifica esa cifra, la contextualiza y ofrece una comparación homóloga válida.


## 0. Verificación de números ancla (julio 2025 vs julio 2026)


## Pregunta 1 — Componentes de la serie

### (1) Concepto técnico
Toda serie mensual observada se descompone en **tendencia** (nivel de largo plazo), **estacionalidad** (patrón que se repite cada año en los mismos meses), **ruido** (variación mes a mes no explicada por lo anterior) y, cuando existe, un **quiebre estructural** (choque puntual y localizado que no es ni tendencia ni estacionalidad). Julio-2026 exige además un quinto concepto: **cobertura/completitud del periodo** — un mes con `dias_observados < dias_del_mes` no es un valor de la serie comparable con un mes cerrado; es una medición parcial.

### (2) Evidencia con números reales del CSV

**Tendencia (leve alza):** total anual `asistentes` 2024 = 2,471,862 → 2025 = 2,703,721 (+9.38%). Los 12 meses de 2025 superan a su homólogo 2024 sin excepción (mínimo +3.60% en abril, máximo +15.58% en febrero) — ver tabla de abajo. Notable: incluso marzo–mayo 2025 (meses del quiebre) crecen vs. 2024 — mar: 203,347 vs 182,929 = +11.16%; abr: 202,776 vs 195,726 = +3.60%; may: 201,999 vs 190,133 = +6.24% — porque el quiebre solo golpea 2 de 12 sedes; a nivel agregado la tendencia de fondo no se rompe (ver tabla de abajo para el resto de meses).

**Estacionalidad (picos jul/dic):** en 2025, julio = 281,044 y diciembre = 321,462, frente a una base de meses no-pico que oscila entre 183,751 (feb) y 226,442 (nov), media ≈ 210,122. El mismo patrón se repite en 2024 (jul = 250,847, dic = 292,448, vs base ~180–210k). Es estructural y recurrente cada año.

**Ruido:** oscilación mes a mes sin patrón, p.ej. 2025: ene 206,593 → feb 183,751 (−11.06%) → mar 203,347 (+10.66%). Fluctuación de corto plazo no atribuible a tendencia ni estación.

**Quiebre (Loreto/Ucayali, mar–may 2025):** SED-11 (Iquitos) y SED-12 (Pucallpa) muestran `evento_contexto = "Interrupción logística ficticia"` en exactamente 6 de 372 filas (2025-03, 2025-04, 2025-05). Iquitos: 8,518 / 8,485 / 7,459 asistentes (vs. su propio enero-2025 = 13,411, es decir índice ≈63.5/63.3/55.6 sobre base 100). Pucallpa: 7,429 / 7,109 / 7,147 (vs. enero-2025 = 11,242, índice ≈66.1/63.2/63.6). Ambas sedes se recuperan en junio-2025 (Iquitos 13,665 = índice 101.9; Pucallpa 11,520 = índice 102.5). Es un evento localizado y temporal (forma de "V"), no una tendencia estructural nueva; el resto de sedes y meses = "Sin quiebre registrado" (366/372 filas), y en 2026 ambas sedes vuelven a "Sin quiebre registrado" en las 14 filas correspondientes.

**Julio 2026:** `dias_observados=12`, `dias_del_mes=31`, `cobertura_periodo_pct=38.71%`, total asistentes = 121,281.

### (3) Decisión de cálculo/diseño — cómo se clasifica julio-2026
Julio-2026 **no se etiqueta automáticamente como "caída" ni como "outlier"**:
- Para sostener **"caída"** se necesita una comparación entre periodos *homólogos* (misma cobertura). Comparar el total de 12 días contra el total de 31 días del año anterior (`LOOKUP(..., -12)` ingenuo) no es una comparación homóloga — ver Pregunta 3.
- Para sostener **"outlier"** primero hay que descartar que la anomalía se explique por cobertura. Aquí se explica enteramente por cobertura: `cobertura_periodo_pct=38.71%` es el único campo que difiere estructuralmente de cualquier otro julio en el dataset (todos los demás meses de la serie tienen cobertura 100%, ver chequeo abajo).
- Diagnóstico correcto: **periodo truncado / observación incompleta**, no un evento del negocio.

**Titular inicial (el que produce el gráfico ingenuo):** *"Julio se desploma 57%: la asistencia colapsa en ChasquiFest."*

**Titular revisado (tras revisar `cobertura_periodo_pct`):** *"Julio-2026 solo tiene 12 de 31 días registrados (38.71% de cobertura); al ritmo diario observado, la asistencia va +11.5% por encima de julio-2025."*

### (4) Límite/trade-off
Clasificar automáticamente por umbral (p.ej. "toda caída >50% es alerta roja") es peligroso si el pipeline de reporting no verifica `cobertura_periodo_pct` antes de calcular variaciones — el mismo dato genera una alerta falsa de crisis o una lectura correcta de crecimiento, dependiendo de si se audita la completitud primero.


### Figura 1 — Comparar magnitudes vs. tasas: el titular bruto vs. la lectura corregida por ritmo diario


## Pregunta 2 — Ventana, acumulado y dirección

### (1) Concepto técnico
Una **media móvil** (window function `WINDOW_AVG`) suaviza estacionalidad y ruido para leer la *dirección reciente* del nivel de la serie. Un **acumulado** (`RUNNING_SUM`) mide *progreso* hacia una meta dentro de una ventana temporal (típicamente el año) y por diseño es monótono no-decreciente si la métrica es siempre ≥0. Son respuestas a preguntas distintas y no deben graficarse en el mismo eje/línea sin aclarar la diferencia de semántica (uno es una "tasa/nivel", el otro es un "stock acumulado").

### (2) Fórmulas Tableau + declaración de addressing/partición/orden

**(a) Media móvil de 3 meses (total festival):**
```
WINDOW_AVG(SUM([asistentes]), -2, 0)
```
- **Addressing:** Along `Mes` (table-down si `Mes` está en filas / Pane down).
- **Partición:** por `Sede` si se quiere la media móvil de cada sede por separado; **sin partición por sede** (total festival) si se agregó primero `SUM([asistentes])` a nivel mes — este notebook usa el total festival.
- **Orden:** `Mes` ascendente (obligatorio para que `-2,0` tome "los 2 meses previos + el actual").
- **Símil pandas:** `serie.groupby('mes')['asistentes'].sum().sort_index().rolling(3).mean()`

**(b) Acumulado que reinicia cada año (YTD):**
```
RUNNING_SUM(SUM([asistentes]))
```
- **Addressing:** Along `Mes`.
- **Partición/reinicio:** compute using `Mes`, **restarting every `Año`** (el acumulado vuelve a 0 en enero de cada año).
- **Orden:** `Mes` ascendente dentro de cada `Año`.
- **Símil pandas:** `df.sort_values('mes').groupby('anio')['asistentes'].transform(lambda s: s.groupby(df['numero_mes']).sum())` → más simple: `serie.groupby('anio')['asistentes'].cumsum()` sobre la serie mensual ya agregada.

### (3) Decisión de diseño — por qué NO van en la misma línea, y cuál es KPI vs contexto
La media móvil responde **"¿cuál es la tendencia reciente?"** (nivel/dirección); el acumulado responde **"¿cuánto llevamos en el año?"** (progreso). Ponerlas en el mismo eje es engañoso: el acumulado casi siempre sube (es una suma), mientras que la media móvil puede subir o bajar — un lector que mira ambas líneas juntas tiende a anclarse en la que sube y descarta la que cae.

Para decidir la **programación del próximo mes**:
- **KPI decisor** = media móvil de 3 meses (o el YoY por ritmo diario homólogo de la Pregunta 3) — mide la dirección real y reciente.
- **Contexto** = acumulado YTD — sirve para verificar avance hacia la meta anual, no para decidir el mes siguiente.
- **Falsa tranquilidad** = el acumulado YTD, con evidencia concreta abajo: YTD-hasta-julio-2025 (mes completo) = 1,496,024; YTD-hasta-julio-2026 (mes truncado a 12 días) = 1,487,219 → diferencia de solo **−0.59%**. Un lector que solo mira el acumulado concluiría "vamos casi igual que el año pasado", ocultando que julio-2026 está truncado y que el ritmo corregido va **+11.5%** por encima. El acumulado diluye el problema (o, en este caso, diluye la buena noticia) porque 6 meses completos ya "amortiguan" cualquier mes parcial — y nunca puede bajar, así que jamás avisará de un verdadero deterioro hasta que ya sea muy tarde en el año.

### (4) Límite/trade-off
La media móvil de 3 meses retrasa la detección de un quiebre ~1–2 meses, y su último punto se contamina si el mes está truncado (jul-2026: cae a 199,654 al incluir el mes parcial, frente a 236,608 en jun-2026 con 3 meses completos) — no es una lectura limpia del nivel reciente cuando el mes más nuevo no ha cerrado. El YTD nunca decrece (es una suma acumulada de una métrica ≥0), así que por diseño no puede avisar de deterioros: en el peor escenario posible seguiría subiendo mes a mes aunque el negocio se esté desplomando, solo más lento.


### Figura 2 — Evolución temporal con anotación de quiebre: serie mensual, quiebre Loreto/Ucayali y cobertura de julio-2026


## Pregunta 3 — Comparación interperiodo (YoY válida para julio 2026)

### (1) Concepto técnico
Una comparación año contra año (YoY) solo es válida entre **periodos homólogos**: misma unidad de exposición (aquí, días observados). `LOOKUP(SUM([asistentes]), -12)` en una tabla mensual trae, para julio-2026, el valor 12 meses atrás = julio-2025 (281,044, con cobertura 100%). Compararlo directo contra julio-2026 (121,281, cobertura 38.71%) mezcla un mes de 31 días contra uno de 12 — **no son periodos homólogos** y la diferencia resultante (−56.8%) mide sobre todo la diferencia de cobertura, no de desempeño.

### (2) Evidencia — contraste explícito bruto vs. ritmo diario
- **Caída bruta:** num = `asistentes(Jul26) − asistentes(Jul25)` = 121,281 − 281,044 = −159,763; den = `asistentes(Jul25)` = 281,044 → **−56.8%**. Compara **totales de mes** (magnitudes con exposición distinta: 31 días vs 12 días).
- **Ritmo diario:** num = `asistentes(Jul26)/dias_observados(Jul26) − asistentes(Jul25)/dias_observados(Jul25)` = 10,106.75 − 9,065.94 = 1,040.80; den = `asistentes(Jul25)/dias_observados(Jul25)` = 9,065.94 → **+11.5%**. Compara **tasas por día** (controla la exposición).

**El signo se invierte (−56.8% → +11.5%) sin que ningún dato del CSV cambie.** Lo único que cambia es el **denominador**: "31 días fijos" (el mes completo del año anterior) vs "días realmente observados" (12, este año). Es la misma trampa que comparar las ventas totales de una tienda abierta 12 días del mes contra una tienda abierta los 31 días completos, sin normalizar por días de apertura.

### (3) Decisión de cálculo — 3 formas de construir un YoY válido
**(a) Días homólogos:** ideal = comparar los primeros 12 días de julio-2025 contra los 12 días observados de julio-2026. **Limitación de datos:** este CSV tiene granularidad **mensual × sede**, no diaria — no existe un campo que permita aislar "los primeros 12 días de julio-2025" directamente. Proxy calculado (asumiendo distribución uniforme dentro del mes): `ritmo_diario(Jul25) × 12 = 9,065.94 × 12 = 108,791.23` asistentes "equivalentes a 12 días". Comparado con el real de julio-2026 (121,281) → **+11.48%** (idéntico al cambio de ritmo diario, por construcción lineal). Límite explícito: asume que la afluencia diaria es uniforme dentro del mes (sin efecto fin de semana ni aceleración de cierre), supuesto no verificable sin datos diarios reales.

**(b) Esperar el cierre del mes:** posponer el YoY oficial hasta que `dias_observados(Jul26)=31`; mientras tanto reportar el ritmo diario como indicador provisional, no la variación bruta.

**(c) Proyectar (con incertidumbre declarada):** extrapolar `ritmo_diario(Jul26) × 31 = 10,106.75 × 31 = 313,309.25` asistentes proyectados. Vs. julio-2025 real (281,044) → **+11.48%**. Supuesto declarado: ritmo diario constante durante el resto del mes (sin aceleración de fin de mes ni feriados). **Incertidumbre:** es una proyección, no una observación — el número real de cierre podría diferir si hay estacionalidad intra-mes; no debe presentarse como cifra oficial, solo como rango orientativo con el ritmo diario como referencia central.

### (4) Fórmulas Tableau + símil pandas
```
// YoY bruto (NO valido si difiere cobertura)
(SUM([asistentes]) - LOOKUP(SUM([asistentes]), -12)) / LOOKUP(SUM([asistentes]), -12)

// Ritmo diario (version corregida por cobertura)
SUM([asistentes]) / SUM([dias_observados])
```
**Addressing:** along `Mes` continuo (SIN partición por año, para que −12 cruce el límite de año). **Orden:** `Mes` ascendente.

Pandas:
```python
lookup_12 = serie.set_index('mes')['asistentes'].shift(12)   # simil LOOKUP(..., -12)
ritmo = df.groupby(['anio','numero_mes']).apply(lambda g: g['asistentes'].sum() / g['dias_observados'].iloc[0])
```



## Pregunta 4 — Comparar las 12 sedes

### (1) Concepto técnico
**Pequeños múltiplos con escala común** (mismo eje Y en los 12 paneles) responden **"¿qué sede aporta más volumen absoluto?"** — comparación de *magnitud*. **Pequeños múltiplos con índice base 100** (cada sede reescalada a su propio valor de referencia) responden **"¿qué sede creció, cayó o se recuperó en términos relativos?"** — comparación de *forma/recuperación*, independiente del tamaño. Esta segunda vista es la que se necesita cuando las sedes tienen tamaños muy distintos y existe un quiebre que solo afecta a algunas.

### (2) Evidencia con números reales
**Magnitud (escala común):** tamaño medio mensual 2025 — Lima (SED-01) = 38,557; Cusco (SED-06) = 23,500; Arequipa (SED-05) = 22,333; … ; Iquitos (SED-11) = 13,037; Pucallpa (SED-12) = 11,242 (la más pequeña). Lima es **3.4× más grande** que Pucallpa. En una vista de escala común, la caída de Iquitos/Pucallpa durante el quiebre (a ~7,100–8,518) queda visualmente aplastada contra el eje Y dominado por Lima — el quiebre casi no se nota.

**Recuperación relativa (índice base 100, referencia = enero-2025):** Iquitos cae a 63.5 (mar-25) → 63.3 (abr-25) → 55.6 (may-25), y se recupera a 101.9 en jun-25, alcanzando 125.8 en jul-25 (estacionalidad) y 151.0 en dic-25 (pico). Pucallpa: 66.1 → 63.2 → 63.6, recupera a 102.5 en jun-25, 154.0 en dic-25. Lima, en la misma ventana, solo fluctúa por estacionalidad normal (106.4 en mar-25, 99.9 en abr-25, 112.9 en may-25, sin ningún dip). El índice hace visible una **"V" clara de caída y recuperación en 3 meses** que la vista de escala común esconde por completo.

### (3) Decisión de diseño
- **Granularidad:** mantener 1 punto por mes × sede en ambas vistas (no agregar a trimestre/año) — 12 paneles (uno por sede) con el eje X = mes, ene-2024 a jul-2026.
- **Anotar el quiebre sin confundirlo con tendencia estructural:** banda sombreada (`axvspan`) entre 2025-03 y 2025-05, aplicada **solo** en los paneles de Loreto y Ucayali, con etiqueta explícita "Interrupción logística ficticia (evento puntual, 6/372 filas)" — distinta de la banda/anotación de estacionalidad (jul/dic, que sí es recurrente y estructural). En 2026 ambas sedes vuelven a "Sin quiebre registrado", confirmando que no es una tendencia nueva.

### (4) Límite/trade-off
El índice base 100 oculta la magnitud absoluta: una sede pequeña con alta variabilidad relativa puede parecer "más dramática" que Lima aunque mueva muchas menos personas en términos absolutos. Por eso ninguna de las dos vistas reemplaza a la otra — se presentan **una al lado de la otra**, cada una etiquetada con la pregunta que responde.

### BITÁCORA (Pregunta 4)
1. **Lectura inicial:** Lima domina el festival; las demás sedes parecen estancadas o irrelevantes.
2. **KPI decisor:** Índice de recuperación post-quiebre = (`asistentes_mes` / `asistentes_ene-2025`) × 100, mensual, por sede (Loreto/Ucayali), meta ≥ 100 para junio-2025.
3. **Giro analítico:** al indexar cada sede a base 100, Loreto y Ucayali muestran una V completa (63 → 101 en 3 meses) que la vista de escala común, dominada por Lima, no deja ver.
4. **Lectura revisada:** el quiebre fue real pero temporal; ambas sedes se recuperaron para junio-2025.
5. **Consecuencia:** el comité debería evaluar la resiliencia logística de Loreto/Ucayali (tiempo de recuperación) en vez de recortar presupuesto por "bajo desempeño" —una decisión que solo emerge al mirar recuperación relativa (índice base 100) y que la vista de magnitud absoluta (donde Lima domina) habría llevado a ignorar o mal-interpretar como debilidad estructural de la Selva.


### Figura 3 — Pequeños múltiplos: escala común vs. índice base 100 (Lima, Iquitos, Pucallpa)


## Cierre

Los cinco números ancla del enunciado se reprodujeron exactamente a partir del CSV: total jul-2025 = 281,044; total jul-2026 = 121,281; cobertura jul-2026 = 38.71%; caída bruta = −56.85% (≈ el titular −57%); ritmo diario +11.48%. El hallazgo central es metodológico, no de negocio: **el "colapso" de julio-2026 es un artefacto de comparar un mes truncado (12/31 días) contra un mes cerrado, no una caída real de asistencia** — corregido por cobertura, el ritmo diario y el cumplimiento de meta (num = SUM(asistentes jul-2026) = 121,281 / den = SUM(meta_asistentes jul-2026) = 120,838 → 100.37%) muestran a ChasquiFest por encima del año anterior.



<br>

---

> 📓 **Computación y figuras ejecutadas:** [`notebook/caso4.ipynb`](notebook/caso4.ipynb)


# CASO 4 — Impacto departamental (Operación ChasquiFest)
## Auditoría de visualización — el mapa de burbujas que confunde "más grande" con "más querido"

**Rol:** Auditor de Visualización. **Rigor:** cada afirmación se ancla en un número recalculado directamente del CSV en este notebook, con numerador y denominador declarados.

**El caso:** el comité recibió un mapa de burbujas con asistencias ABSOLUTAS por sede: Lima tiene la burbuja mayor, el
DIÁMETRO fue escalado linealmente al valor (lo que distorsiona el ÁREA) y el colormap `jet` pinta una falsa "montaña de
intensidad". El título concluye que Lima "ama más" al festival. Población, capacidad instalada y tasas normalizadas no
llegaron a la reunión — y sin ellas, el comité no puede decidir dónde reforzar seguridad, dónde ampliar alcance ni dónde
mejorar la experiencia.

**Granularidad del dataset:** 1 fila = 1 sede/departamento, año 2025 (12 sedes, 12 eventos cada una). No hay una segunda
columna de año, por lo tanto **todas** las comparaciones de este notebook son intra-2025 (periodos homólogos por
construcción; no se compara contra otro año porque el CSV no lo contiene).



### 0. Verificación de fórmulas ancla (nivel de fila)

Antes de rankear nada, confirmamos que las 4 tasas ya provistas en el CSV son en efecto lo que dicen ser: una
fórmula `numerador / denominador` por fila (sede), no una medida agregada opaca.



---
## Pregunta 1 — Un ranking por decisión

Cada decisión del comité necesita una métrica distinta, con un **denominador distinto**. Ninguna es "la verdadera":
responden preguntas diferentes.



**Evidencia del reordenamiento.** A continuación, la posición (1 = primero) de cada una de las 12 sedes en los tres
rankings simultáneamente.



### Respuesta — P1

**(a) VOLUMEN — asignar personal de seguridad**
1. **Concepto técnico:** aforo absoluto (conteo de asistencias, no de personas distintas). Mide carga operativa total a
   custodiar; no se normaliza porque la seguridad se dimensiona contra multitudes físicas reales, no contra tasas.
2. **Evidencia:** `asistentes_2025`. Numerador = asistencias 2025; **denominador = ninguno** (es una magnitud absoluta,
   no una tasa). Top 5: Lima 462,690 (#1), Cusco 281,998 (#2), Arequipa 268,001 (#3), Trujillo 253,960 (#4), Piura
   246,920 (#5).
3. **Decisión de cálculo — Tableau:** `SUM([asistentes_2025])`, con table calc `RANK(SUM([asistentes_2025]))`.
   **Partición:** ninguna (la tabla completa; granularidad = 1 fila/sede, un solo año). **Addressing:** Ciudad/Departamento
   (el ranking recorre esa dimensión). — **pandas:** `df['asistentes_2025'].rank(ascending=False)`.
4. **Límite/trade-off:** ignora la ocupación relativa del recinto. Tarapoto opera al **92.46%** de su capacidad
   (asistentes=156,388 / capacidad_anual_2025=169,146) — la ocupación **más alta** de las 12 sedes — pero por volumen
   bruto cae al puesto **#9**, recibiendo relativamente poco refuerzo si el criterio fuera solo volumen. Riesgo:
   sedes pequeñas casi llenas quedan sub-atendidas en seguridad.

**(b) TASA POBLACIONAL — comparar alcance territorial**
1. **Concepto técnico:** penetración territorial — cuántas personas *distintas* de la población de referencia fueron
   alcanzadas, normalizando por tamaño poblacional para comparar sedes de escala muy distinta.
2. **Evidencia:** `alcance_por_1000_hab = visitantes_unicos_2025 / poblacion_referencial * 1000` (CONFIRMADO,
   diff máx. 0.0043 vs. recálculo). Numerador = visitantes únicos 2025; denominador = población referencial. Top 5:
   Cusco 157.89 (221,678/1,404,000), Ayacucho 146.86 (98,130/668,200), Pucallpa 135.62 (87,911/648,200), Tarapoto
   126.07 (117,551/932,400), Arequipa 123.90 (202,092/1,631,100). Lima cae a **31.96** (324,391/10,151,200).
3. **Decisión de cálculo — Tableau:** `SUM([visitantes_unicos_2025]) / SUM([poblacion_referencial]) * 1000`, con
   `RANK(...)`. **Partición:** ninguna. **Addressing:** Ciudad/Departamento. — **pandas:**
   `(df.visitantes_unicos_2025 / df.poblacion_referencial * 1000).rank(ascending=False)`.
4. **Límite/trade-off:** premia poblaciones chicas. Pucallpa (población 648,200, la **más pequeña** de las 12) entra
   al podio de alcance, mientras Lima —con 10,151,200 hab., 15.7× la población de Pucallpa— queda relegada, aunque en
   términos absolutos deja sin cubrir a **9,826,809 personas (96.80% de su población referencial)** que nunca
   asistieron en 2025. Ese mercado sin explotar no aparece en un ranking de tasas.

**(c) TASA DE RECLAMOS — priorizar calidad operativa**
1. **Concepto técnico:** intensidad de fricción por unidad de actividad — normaliza reclamos por volumen de asistencia
   para comparar "calidad percibida" entre sedes de tamaño distinto.
2. **Evidencia:** `reclamos_por_10000_asistencias = reclamos_totales / asistentes_2025 * 10000` (CONFIRMADO, diff máx.
   0.0046). Numerador = reclamos totales; denominador = asistencias 2025 (no visitantes únicos). Top 5 peor: Cusco
   69.01 (1,946/281,998), Ayacucho 65.58 (973/148,376), Piura 62.61 (1,546/246,920), Pucallpa 54.78 (739/134,905),
   Lima 42.92 (1,986/462,690).
3. **Decisión de cálculo — Tableau:** `SUM([reclamos_totales]) / SUM([asistentes_2025]) * 10000`, con `RANK(...)`
   ordenado descendente (mayor tasa = peor). **Partición:** ninguna. **Addressing:** Ciudad/Departamento. —
   **pandas:** `(df.reclamos_totales / df.asistentes_2025 * 10000).rank(ascending=False)`.
4. **Límite/trade-off:** puede castigar sedes con **mejor cultura o mayor accesibilidad de canales de reporte**
   (más fácil quejarse → más reclamos registrados, no necesariamente peor servicio), o premiar sedes con canales
   pobres. Puno tiene la tasa más baja (18.41): no podemos afirmar causalmente que da mejor servicio — podría tener
   menos canales de reporte (asociación, no causalidad). Dato de contexto: en Cusco solo el **16.70%** de sus 1,946
   reclamos son de accesibilidad (`reclamos_accesibilidad`=325) — el porcentaje **más bajo** de las 12 sedes — lo que
   sugiere que su fricción no es solo de accesibilidad, aunque tampoco prueba causa-raíz sin investigación cualitativa
   adicional.

**Por qué los tres rankings cambian sin que ninguno sea "falso":** miden objetivos distintos con denominadores
distintos. Volumen (sin denominador) responde "¿dónde hay más gente físicamente?"; alcance (den=población) responde
"¿qué proporción del territorio se activó?"; reclamos (den=asistencias) responde "¿qué tan fricción-intensiva es la
experiencia por visita?". Lima domina el primero porque concentra el **41.05%** de la población de referencia
nacional pero solo el **17.11%** de las asistencias totales: es grande en términos absolutos pero relativamente poco
penetrada. Cusco lidera el segundo **y** es alto en el tercero al mismo tiempo — alta penetración y alta fricción no
son contradictorias, son dos caras de una sede muy demandada relativa a su tamaño.



### Figura 1 — Tarea analítica: comparación de magnitud / ranking (canal = posición)

Tres barras ordenadas, una por métrica, mismas 12 sedes. La tarea analítica de esta figura es **ranking / comparación
de magnitud**: por eso el canal usado es posición en eje (barra horizontal ordenada), el canal que Cleveland &
McGill identifican como el más preciso para juicios de magnitud — muy superior a área o color. Lima (rojo) y Cusco
(azul) se resaltan para visualizar el reordenamiento.



---
## Pregunta 2 — Mapa o barra

### Respuesta — P2

**1. Concepto técnico:** dos preguntas distintas exigen dos tareas analíticas distintas, y cada tarea exige un tipo
de gráfico distinto.
- **(a) "¿DÓNDE?" → mapa — tarea analítica: localización geográfica / distribución espacial.** Usa
  `latitud`/`longitud` para posicionar cada sede en su ubicación real.
  - **Símbolos proporcionales** (bubble map) cuando la variable es un **conteo/volumen absoluto** (`asistentes_2025`):
    el tamaño del símbolo codifica magnitud sin inflar el área del polígono territorial que ya de por sí varía por
    departamento.
  - **Coroplético NORMALIZADO** (relleno de área) reservado para **tasas** por población o por actividad
    (`alcance_por_1000_hab`, `reclamos_por_10000_asistencias`, `ocupacion_pct`): el color debe representar algo *por
    unidad* de esa área/población, no un conteo bruto.
- **(b) "¿QUIÉN LIDERA Y POR CUÁNTO?" → barra ordenada — tarea analítica: ranking / comparación de magnitud (canal =
  posición en eje).** Ordenar descendente por la métrica elegida; eje corto = categoría (sede), eje largo = valor;
  etiquetas numéricas directas para lectura exacta (ver Figura 1).

**2. Evidencia:** por qué un coroplético de CONTEOS BRUTOS repite el mapa de población, y los dos titulares —ambos
ciertos— que compiten por la atención del comité.
- Si se pintara el departamento de Lima con el color más intenso solo por tener 462,690 asistentes, el mapa
  terminaría mostrando "dónde vive más gente", no "dónde el festival tuvo más impacto relativo". Lima tiene
  10,151,200 habitantes = **41.05%** de la población de referencia total (10,151,200/24,729,200); cualquier conteo
  bruto (asistentes, reclamos_totales, costo_publico_soles) se correlaciona mecánicamente con población, y las áreas
  grandes/pobladas "ganan" siempre en un coroplético de conteos, sin importar la variable.
- **VOLUMEN:** *"Lima concentra 462,690 asistencias, el mayor aforo"* (Ranking 1, P1a).
- **ALCANCE:** *"Cusco alcanza 158 visitantes por mil habitantes, el mayor alcance por habitante"* (Ranking 2, P1b).

**3. Decisión (asignaciones):** cada titular apunta a un recurso distinto del comité — no son intercambiables.
- **VOLUMEN → reforzar personal de seguridad y logística de multitudes en Lima** (Pregunta 1a): la decisión responde
  a carga física absoluta, sin denominador.
- **ALCANCE → estudiar la experiencia/calidad de servicio en Cusco** (Pregunta 1c), no necesariamente expandir
  infraestructura física: la decisión responde a penetración relativa a la población, no a volumen.
- Ambos titulares son ciertos simultáneamente porque responden preguntas distintas (ver cierre de P1); llevan a
  asignaciones de recursos distintas: seguridad/logística de multitudes a Lima (volumen absoluto), estudio de
  experiencia/servicio a Cusco (intensidad relativa a su población).

**4. Límite (caveat):** una tasa alta no es evidencia de causa ni de afecto — el mismo error que decir "Cusco ama
más". `ocupacion_pct` de Cusco es **74.96%**, la **más baja** de las 12 sedes — así que el alto alcance y la alta
tasa de reclamos de Cusco (**69.01**, Pregunta 1c) **no** se explican por saturación física del recinto (no está
"lleno"); apuntan más bien a gestión de flujos, servicios o accesibilidad, que solo una investigación cualitativa
adicional podría confirmar. "Mayor alcance por habitante" describe una **tasa de penetración territorial**, no un
sentimiento de apego: inferir "arraigo" o "amor" a partir de `alcance_por_1000_hab` cometería el mismo salto
lógico (tasa → causa/afecto) que el titular original del mapa de burbujas.



---
## Pregunta 3 — Área, color y acceso



1. **Concepto técnico:** el error clásico de "burbuja mal escalada". Si el **DIÁMETRO** se escala linealmente al
   valor, el **ÁREA** —lo que el ojo realmente integra al leer un círculo (Cleveland & McGill; Stevens)— crece con el
   **cuadrado** del valor, exagerando visualmente las diferencias.
2. **Evidencia con números reales:** Lima (462,690 asistentes) vs. Pucallpa (134,905 asistentes), razón de valores
   **r = 3.4297×**. Con diámetro ∝ valor: razón de diámetros = 3.43×, pero razón de **áreas** = 3.43² = **11.76×**.
   El área de la burbuja de Lima aparece **11.76×** más grande que la de Pucallpa aunque el dato real es solo
   **3.43×** mayor — una sobre-representación visual adicional de exactamente 3.43× (r²/r = r).
3. **Decisión de corrección:** escalar por **ÁREA**, no por diámetro: área ∝ valor ⟹ **diámetro ∝ √valor**. Con esta
   corrección, razón de diámetros = √3.43 = **1.85×**, razón de áreas = 1.85² = **3.43×** = coincide exactamente con
   la razón real. **Tableau:** en el estante *Size*, Tableau ya escala por defecto el **área** del símbolo (no el
   diámetro) al soltar un campo continuo — el error típicamente ocurre en herramientas/código que fijan
   `markersize`/`radius` de forma lineal. **pandas/matplotlib:** usar `s = k * valor` en `plt.scatter` (matplotlib
   interpreta `s` como área en puntos², por lo que `s = k*valor` ya es correcto); el error equivalente sería
   `markersize = k*valor` en `plt.plot`, porque `markersize` es un diámetro lineal.
4. **Límite/trade-off:** incluso corregido por área, el ojo humano **subestima** áreas grandes (compresión de
   Stevens, exponente ≈0.7 para área), así que ningún bubble map da lectura cuantitativa exacta — por eso debe
   acompañarse siempre de una etiqueta numérica directa o de una barra ordenada (canal de posición) para lectura
   precisa.

**Reemplazo de colormap:** `jet` no es perceptualmente uniforme — su luminancia no es monótona, crea **falsos
bordes**/bandas de contorno que no corresponden a discontinuidades reales en los datos, y no es legible en escala de
grises ni amigable para daltonismo rojo-verde (deuteranopía/protanopía). Reemplazo: **viridis** (o **cividis**,
optimizado específicamente para deuteranopía) — luminancia monótonamente creciente, perceptualmente uniforme en
CIELAB, legible en escala de grises.

**≥2 canales redundantes** (mantienen la lectura con daltonismo o en escala de grises, sin depender del color):
1. **Etiqueta numérica directa** sobre cada símbolo (ej. "Cusco 158") — lectura exacta sin decodificar color ni área.
2. **Tamaño/área del símbolo** como canal redundante con el color — ordena visualmente sin necesitar distinguir tonos.
3. (Añadido en la Figura 2) **Borde/anillo distintivo** (grosor + color de contorno) para marcar sedes que superan un
   umbral de riesgo — un tercer canal binario, legible incluso en escala de grises por el grosor del trazo.



### Figura 2 — Demostración de la distorsión diámetro-vs-área y su corrección

**Panel A** (tarea: comparación literal de dos círculos): Lima vs. Pucallpa bajo escalado incorrecto (diámetro∝valor)
y corregido (área∝valor). **Panel B** (tarea: localización geográfica, réplica del mapa original defectuoso):
símbolos con diámetro∝valor + colormap `jet`. **Panel C** (tarea: localización geográfica, versión corregida):
símbolos con área∝`asistentes_2025`, color=`viridis` sobre `alcance_por_1000_hab`, más 2 canales redundantes
(etiqueta numérica + borde rojo grueso para sedes con `reclamos_por_10000_asistencias` por encima de la mediana).



---
## Pregunta 4 — Dashboard de decisión

Primero calculamos los 4 KPI nacionales (2025, agregados como **ratio-de-sumas**, no promedio-de-tasas, para evitar
el sesgo de ponderación tipo Simpson) y sus benchmarks internos (mediana de las 12 sedes, único "periodo" disponible
en el CSV).



### Respuesta — P4

**Layout fijo 1280×720 px** (ver Figura 3, wireframe):
- **Fila 1 (título-pregunta):** *"¿Dónde reforzamos seguridad, ampliamos alcance o mejoramos experiencia? — Impacto
  departamental ChasquiFest 2025"*.
- **Fila 2 (franja de KPI, 4 tarjetas):** Resultado | Eficiencia | Riesgo | Alcance/Equidad, cada una con valor +
  comparación/meta + estado semáforo (detalle abajo).
- **Fila 3 — vista principal (izquierda, ~800px):** mapa de símbolos proporcionales (área ∝ `asistentes_2025`,
  color = viridis sobre `alcance_por_1000_hab`) — tarea: localización geográfica (P2a). **Soporte (derecha, ~450px):**
  barra ordenada configurable (volumen / alcance / reclamos) — tarea: ranking (P2b/Fig.1).
- **Fila 4 (panel de insights):** 3 bullets con números que resumen el giro analítico (Lima 41% población / 17%
  asistencias / alcance 32; Cusco #1 alcance y #1 reclamos con ocupación 74.96%, no es saturación física; 4 sedes en
  zona crítica de reclamos).
- **Fila 5 (pie metodológico):** fuente = `caso4_impacto_departamental_chasquifest.csv`, periodo = 2025, granularidad
  = 1 fila/sede (12 sedes), fórmulas de cada tasa con numerador/denominador.

**Los 4 KPI, con roles distintos y su acción/decisión asociada:**

| Rol | KPI | Fórmula (Tableau) | pandas | Valor 2025 (num/den) | Meta (declarada) | Estado | Acción / decisión |
|---|---|---|---|---|---|---|---|
| RESULTADO | `ocupación agregada` (asistentes_2025 / capacidad_anual_2025) | `SUM([asistentes_2025])/SUM([capacidad_anual_2025])*100` | `df.asistentes_2025.sum()/df.capacidad_anual_2025.sum()*100` | 83.89% (num=2,703,721 / den=3,222,747) | ocup. agregada ≥ 85% | AMARILLO (−1.11 pp) | Revisar programación y franjas horarias en sedes con capacidad ociosa para cerrar la brecha de −1.11 pp hacia la meta. |
| EFICIENCIA | `costo_por_asistente_soles` | `SUM([costo_publico_soles])/SUM([asistentes_2025])` | `df.costo_publico_soles.sum()/df.asistentes_2025.sum()` | S/ 14.03 | ≤ mediana sedes S/ 13.64 | ROJO (+2.84%) | Auditar y renegociar costos logísticos en las sedes sobre la mediana (máx. Chiclayo) para converger a S/ 13.64/asistente. |
| RIESGO | `reclamos_por_10000_asistencias` | `SUM([reclamos_totales])/SUM([asistentes_2025])*10000` | `df.reclamos_totales.sum()/df.asistentes_2025.sum()*10000` | 42.02 | ≤ mediana sedes 41.27 | ROJO/ALERTA (+1.83%) | Reforzar atención al público y protocolos de accesibilidad en Cusco, Ayacucho, Piura y Pucallpa (zona crítica >50; ver tarjeta abajo). |
| ALCANCE/EQUIDAD | `alcance_por_1000_hab` | `SUM([visitantes_unicos_2025])/SUM([poblacion_referencial])*1000` | `df.visitantes_unicos_2025.sum()/df.poblacion_referencial.sum()*1000` | 79.58 | ≥ mediana sedes 116.67 | ROJO (−31.79%) | Priorizar campañas de difusión y nuevas franjas/sedes en departamentos bajo la mediana de alcance (brecha −31.79%). |

*(Las metas de "mediana de las 12 sedes" son un benchmark interno declarado por este análisis — el CSV no trae una
meta oficial del comité; se documenta como límite explícito, no se inventa un objetivo externo.)*

**Nota técnica (evita el sesgo de "promedio de promedios"):** el agregado nacional se calcula como **ratio de sumas**
(`SUM(num)/SUM(den)`), no como promedio simple de las tasas por sede. Ejemplo: ocupación agregada = 83.89% vs.
promedio simple de `ocupacion_pct` = 84.75% — difieren porque el promedio simple pondera igual a Pucallpa (capacidad
146,046) que a Lima (capacidad 556,171). En Tableau esto se expresa con un LOD fijo:
`{FIXED : SUM([reclamos_totales])/SUM([asistentes_2025])*10000}` (una constante nacional repetible en cada fila),
en contraste con `AVG([reclamos_por_10000_asistencias])` (promedio de tasas, **no equivalente**).

**Tarjeta completa (ejemplo: RIESGO, la más ligada a "seguridad/experiencia"):**
- **Valor:** 42.02
- **Unidad:** reclamos por cada 10,000 asistencias
- **Periodo:** 2025 (año completo, 12 eventos por sede; único periodo disponible en el CSV — no se compara con otro
  año)
- **Segmento:** las 12 sedes/departamentos (agregado nacional = SUM/SUM)
- **Comparación/meta:** mediana de sedes = 41.27 (línea de referencia); meta operativa propuesta ≤ 40.00 (declarada
  por este análisis para fines de la tarjeta — límite explícito, no viene en el CSV)
- **Estado:** ícono semáforo ROJO/ÁMBAR (por encima de meta y de la mediana; 4 sedes en zona crítica >50: Cusco
  69.01, Ayacucho 65.58, Piura 62.61, Pucallpa 54.78)
- **Acción:** asignar equipos de atención al público y revisar protocolos de accesibilidad en Cusco, Ayacucho, Piura
  y Pucallpa, en ese orden de prioridad (orden = magnitud de la tasa, no del volumen absoluto).

**Jerarquía visual / proximidad / similitud (lectura en <60s):** tamaño de fuente descendente título > valor-KPI >
etiqueta; cada tarjeta agrupa valor+meta+estado en un solo bloque con espaciado uniforme (proximidad); las 4
tarjetas comparten tipografía y fondo neutro (similitud), con el color de estado (semáforo) como **único** acento
cromático variable — el ojo va directo a los 2 rojos y 1 ámbar antes de leer cualquier número.

### Bitácora (5 frases)
1. **Lectura inicial (≤15 palabras):** *"Lima domina el festival; hay que reforzar Lima."* (8 palabras)
2. **KPI decisor:** RESULTADO — ocupación agregada nacional = `SUM(asistentes_2025)/SUM(capacidad_anual_2025)*100`,
   periodo 2025, segmento = 12 sedes, meta ≥85% → valor real 83.89%.
3. **Giro analítico:** al normalizar por población (`alcance_por_1000_hab`) y por asistencia
   (`reclamos_por_10000_asistencias`), Cusco y Ayacucho emergen como focos de intensidad y fricción que el mapa de
   burbujas absolutas escondía detrás del tamaño de Lima.
4. **Lectura revisada (≤15 palabras):** *"Lima requiere volumen; Cusco y Ayacucho requieren calidad de experiencia."*
   (10 palabras)
5. **Consecuencia:** el comité reasigna presupuesto: seguridad/logística escalan con volumen en Lima, mientras
   personal de atención y accesibilidad se refuerzan en Cusco, Ayacucho, Piura y Pucallpa según su tasa de reclamos,
   no según su tamaño.



<br>

---

> 📓 **Computación y figuras ejecutadas:** [`notebook/caso5.ipynb`](notebook/caso5.ipynb)


# CASO 5 — Killa, el algoritmo y el juicio final (causalidad)
### Operación ChasquiFest · Auditoría de visualización

**Afirmación del dashboard bajo auditoría:** *"Killa causó el boom: +108% de ventas tras el video (15-abr), confirmado por un scatter vistas↔entradas con línea de tendencia."*

Este notebook reproduce los números ancla desde el CSV real, expone los confusores, construye la
contraevidencia (comparación intra-sedes-abiertas y regresión controlando confusores) y responde
las 4 preguntas del caso con el rigor exigido: cada afirmación con num/den, cada gráfico con su
tarea analítica nombrada, y **ninguna afirmación de causalidad no justificada por el diseño**.

Granularidad del CSV: **1 fila = fecha × sede** (122 días × 12 sedes = 1,464 filas, sin nulos).


## 1. Números ancla — verificación desde el CSV real

### 1.1 Diferencia ingenua PRE/POST sobre `ventas_soles` (promedio por fila fecha×sede)

**Tarea analítica:** comparación de dos agregados (media condicionada por fase de campaña) — *no* es
una prueba causal, es una diferencia bruta entre dos grupos definidos por tiempo calendario.

**Tableau:** `({FIXED : AVG(IF [fase_campania]="Después del video" THEN [ventas_soles] END)} -
{FIXED : AVG(IF [fase_campania]="Antes del video" THEN [ventas_soles] END)}) /
{FIXED : AVG(IF [fase_campania]="Antes del video" THEN [ventas_soles] END)}`

**pandas símil:** `(post.ventas_soles.mean() - pre.ventas_soles.mean()) / pre.ventas_soles.mean()`


### 1.2 ¿De dónde sale el "+108%" del titular?

El titular del dashboard no cuadra con `ventas_soles` (+100.3%). Probamos la misma cuenta sobre
`entradas_vendidas` (también fila = fecha×sede) porque el mockup del dashboard mezcla libremente
"ventas" (soles) y "entradas" (tickets) en su relato.

**Tableau:** igual fórmula que arriba pero sobre `[entradas_vendidas]`.
**pandas símil:** `(post.entradas_vendidas.mean() - pre.entradas_vendidas.mean()) / pre.entradas_vendidas.mean()`


**Verificación explícita del "+108%" (num/den):** media PRE = **108.21** entradas vendidas por
sede-día, media POST = **225.25** entradas vendidas por sede-día → num = 225.25 − 108.21 = 117.04,
den = 108.21 → **(225.25 − 108.21) / 108.21 = +108.2%**. Ese es el origen exacto del titular
"+108%": está medido en `entradas_vendidas` (tickets), no en `ventas_soles` (soles, sección 1.1).


### 1.3 Tabla de confusores — media PRE vs POST

**Tarea analítica:** *balance check* (chequeo de balance de covariables entre los dos grupos temporales),
el paso obligatorio antes de interpretar cualquier diferencia entre "antes" y "después" como efecto
de una sola causa. Si las covariables NO están balanceadas, la diferencia bruta mezcla varias fuentes.

**Tableau:** `{FIXED [fase_campania] : AVG([variable])}` por cada variable candidata a confusor.
**pandas símil:** `df.groupby('fase_campania')[variable].mean()`


### 1.4 Contraevidencia clave — comparación intra-sedes-abiertas (`festival_abierto_flag == 1`)

**Tarea analítica:** análisis de sensibilidad / *sub-group check* — se restringe la comparación
PRE/POST al subconjunto de filas donde la sede **ya operaba**, para neutralizar el confusor más
grande de la tabla 1.3 (apertura de sedes nuevas, 8→12).

**Tableau (filtro de contexto + LOD, partición/addressing explícitos):** se aplica
`[festival_abierto_flag] = 1` como **filtro de contexto** (esto particiona los datos primero); luego
`{FIXED [fase_campania] : AVG([ventas_soles])}` direcciona (addressing) el promedio dentro de esa
partición ya filtrada. Sin el filtro de contexto, el LOD FIXED se calcularía sobre las 1,464 filas
originales y no aislaría el subgrupo.

**pandas símil:** `df[df.festival_abierto_flag==1].groupby('fase_campania').ventas_soles.mean()`


### 1.5 Regresión rápida controlando confusores (statsmodels no está instalado → OLS manual con `numpy.linalg.lstsq`, equivalente a mínimos cuadrados con errores estándar clásicos)

**Tarea analítica:** ajuste multivariante para estimar la asociación de `post` con `ventas_soles`
**mientras se mantienen fijos** los confusores observados simultáneamente — el equivalente a "medias
condicionadas" pedido en el enunciado, pero con todos los confusores a la vez en vez de uno por uno.

Se corren 4 modelos para mostrar la **fragilidad** de la estimación:
- **A**: `ventas_soles ~ post` (todas las sedes, sin controles) — el número ingenuo.
- **B**: `ventas_soles ~ post + festival_abierto + inversion + promo + fin_de_semana + lluvia` (todas las sedes, CON controles).
- **C**: igual que A pero solo sedes ya abiertas — reproduce el -13% de 1.4.
- **D**: igual que B pero solo sedes ya abiertas (controla lo que 1.4 no controla: inversión y promo dentro del subgrupo).


### 1.6 La ilusión del scatter "más vistas = más entradas"

**Tarea analítica:** correlación cruda vs. correlación parcial (residualizada) — muestra por qué un
scatter con línea de tendencia sobre datos crudos sobrestima la relación "vistas del video → entradas".

**Tableau:** `CORR([vistas_video_miles],[entradas_vendidas])^2` — cálculo **agregado** sobre toda la
tabla (no es una tabla calc: no requiere partición ni addressing) para el scatter crudo, lo que hace
el dashboard; para el parcial no hay equivalente nativo simple — se calcula fuera de Tableau, o si se
implementa como tabla calc se declara explícitamente *compute using: toda la tabla, sin partición,
addressing fila fecha×sede*.
**pandas símil:** `df.vistas_video_miles.corr(df.entradas_vendidas)` (crudo) vs. correlación de
residuos tras regresar ambas variables sobre los confusores (parcial).


### 1.7 Nota adicional: apertura escalonada de sedes (relevante para la Pregunta 2)

Las 12 sedes NO abrieron todas el mismo día — se fueron incorporando de forma escalonada entre
marzo y mayo. Esto es relevante para proponer un diseño más fuerte (ver P2): la variación temporal
en fechas de apertura ya insinúa una estructura tipo *stepped-wedge*, aunque en los datos actuales
está confundida con inversión y promociones crecientes, así que no sirve todavía como cuasi-experimento limpio.


## Figuras
### Figura 1 — Balance de confusores PRE vs POST (¿qué se movió junto con la fase de campaña?)
**Tarea analítica:** *balance plot* de covariables (equivalente visual a la tabla 1.3): compara el
desplazamiento PRE→POST de cada variable candidata a confusor, para decidir cuáles contaminan la
comparación bruta y cuáles funcionan como placebo.


### Figura 2 — El titular se desinfla: ingenuo vs. controlado

**Tarea analítica:** comparación de estimaciones de efecto bajo distintos supuestos de control
(*sensitivity/robustness display*) — visualiza cómo cambia (y hasta cambia de signo) la diferencia
PRE/POST según qué confusores se dejan variar libremente y cuáles se mantienen fijos.


## Pregunta 1 — Explorar no es explicar

**1) Concepto técnico.** Hay dos productos de visualización distintos y el dashboard los mezcla:
un producto **exploratorio** (para que un analista busque patrones, con muchos filtros y vistas
alternativas) y un producto **explicativo** (para que un comité tome UNA decisión, con una sola
pregunta gobernando el diseño). El dashboard de Killa tiene forma de exploración —filtros de sobra,
un scatter con trend line sin controles, una torta de vanidad— pero se presenta como si ya
respondiera la pregunta de negocio. Esa mezcla es el problema de fondo, no un detalle estético.

**2) Evidencia concreta.** El mockup describe: filtros `sede | ciudad | macrozona | fecha | lluvia |
promo | fin de semana | canal | color favorito | horóscopo`; un **scatter "más vistas = más entradas"
con línea de tendencia** que usa `vistas_video_miles` vs `entradas_vendidas` sin partir por
`festival_abierto_flag`, `inversion_publicitaria_soles` ni `promocion_activa_flag` (con esos
controles, la R² cruda de 0.283 cae a ~0.040, sección 1.6); y una **torta "¿quién ama más a Killa?"**
que no responde ninguna pregunta operativa (es entretenimiento, no analítica).

**3) Decisión de diseño — dos elementos que RETIRARÍA de la entrega final al comité:**
- **Filtro de "color favorito" / "horóscopo"**: no son variables del negocio ni están en el CSV como
  drivers de ventas; son ruido que invita a "p-hacking visual" (buscar un corte que "confirme" la
  historia) y no aportan ninguna decisión accionable.
- **El scatter exploratorio vistas↔entradas con trend line**: es exactamente la vista que induce al
  comité a leer causalidad donde solo hay covariación con confusores comunes (sección 1.6). Se
  reemplaza en la versión explicativa por la Figura 2 (ingenuo vs. controlado), que es honesta sobre
  la incertidumbre.
  (También retiraría la torta "¿quién ama más a Killa?": es un KPI social, no de negocio.)

**Pregunta de decisión única que debe gobernar la versión explicativa:**
> *"¿El video generó ventas incrementales suficientes por sol invertido, una vez separado su efecto
> del de la apertura de sedes nuevas, el aumento de inversión publicitaria y las promociones, como
> para justificar ampliar la campaña ahora?"*

**4) Límite / trade-off.** Reducir filtros y quitar el scatter libre le cuesta al comité la capacidad
de "jugar" con los datos por su cuenta — pero esa libertad es precisamente lo que permitió la lectura
causal errónea en primer lugar. Un producto explicativo sacrifica exploración a cambio de una
conclusión defendible; si el comité necesita explorar, eso debe vivir en un workbook aparte, no en
la pantalla que van a usar para decidir.

**Clasificación de métricas (jerarquía actividad → resultado → impacto):**

| Métrica | Categoría | Por qué |
|---|---|---|
| `vistas_video_miles` | **ACTIVIDAD (KPI de vanidad)** | Mide exposición al contenido, no comportamiento de compra. Sube 3.2x PRE→POST pero su relación cruda con entradas se explica en gran parte por confusores compartidos (sección 1.6). |
| `entradas_vendidas` | **RESULTADO** | Comportamiento real del cliente (compra), pero agregado, sin descontar qué lo causó. |
| `ventas_soles` | **RESULTADO** | Igual que entradas, en soles; es lo que el titular "+108%"/"+100%" reporta sin descomponer causas. |
| Ventas incrementales por sol invertido (controlando apertura/inversión/promo) | **IMPACTO** | Es la única métrica que conecta el gasto en campaña con un resultado *atribuible*, y es la que debe gobernar la decisión de ampliar o no. Hoy, con datos observacionales, **no se puede estimar de forma confiable** (sección 1.5: el coeficiente cambia de signo según el control) — eso en sí mismo es la respuesta honesta.

**KPI de vanidad identificado:** `vistas_video_miles` — sube de 5.51 a 17.89 miles (3.2x) pero no
prueba nada sobre ventas por sí sola.


## Pregunta 2 — Método científico y causalidad

**1) Concepto técnico.** El método científico exige recorrer *pregunta → hipótesis → datos → prueba →
decisión* sin saltarse pasos, y en particular sin confundir *asociación observacional* (lo único que
un CSV histórico puede mostrar sin experimento) con *causalidad* (lo que requeriría manipular el
tratamiento — el video — de forma independiente de todo lo demás).

**2) Cadena completa:**

| Paso | Contenido |
|---|---|
| **Pregunta** | ¿El lanzamiento del video de Killa incrementó las ventas de entradas del festival? |
| **Hipótesis (H1)** | El video causó un aumento neto de ventas, más allá de lo explicado por apertura de sedes, inversión, promociones y estacionalidad. |
| **Hipótesis nula (H0)** | El aumento observado se explica (total o mayormente) por factores que cambiaron a la vez que el video: sedes nuevas, más inversión, promociones, tendencia temporal. |
| **Datos** | `caso5_campania_killa_chasquifest.csv`, 1,464 filas fecha×sede, 2026-03-01 a 2026-06-30, video el 15-abr. |
| **Prueba** | Comparación PRE/POST bruta (sección 1.1: +100.3%) vs. comparación controlada — intra-sedes-abiertas (sección 1.4: **-12.9%**) y regresión con confusores (sección 1.5: el coeficiente de `post` **cambia de signo**, de +3,850 a -5,185 soles, según se controle o no). |
| **Decisión** | Con los datos observacionales disponibles, **no se rechaza H0**: no hay evidencia robusta de un efecto neto positivo del video una vez controlados los confusores observados. No se puede afirmar "Killa causó el boom". |

**Al menos tres variables de confusión identificadas en el CSV** (con su movimiento PRE→POST, sección 1.3):
1. `festival_abierto_flag` — apertura de sedes nuevas: 0.38 → 0.96 (8 → 12 sedes activas). Confunde
   porque el promedio POST incluye sedes que no existían en el PRE.
2. `inversion_publicitaria_soles` — gasto publicitario simultáneo: S/253.70 → S/731.53 (2.9x). Confunde
   porque más inversión, no el video en sí, puede mover ventas.
3. `promocion_activa_flag` — promociones: 0.00 → 0.54 (las promociones **solo existen** en el período POST,
   colinealidad casi perfecta con la fase). Confunde de forma severa: no hay observaciones PRE con promo
   activa para aislar su efecto.
4. (Adicional) Tendencia temporal / estacionalidad y apertura escalonada de sedes (sección 1.7): las 12
   sedes abrieron en fechas distintas entre el 1-mar y el 2-may, una de ellas (SED-09) exactamente el
   15-abr — coincidencia que refuerza visualmente la narrativa sin ser evidencia causal.
   (`fin_de_semana_flag` 0.29→0.29 y `lluvia_flag` 0.27→0.27 **no** están confundidos — sirven de control
   de que el resto del diseño del CSV es razonable.)

**3) Diseño más fuerte (decisión de cálculo/diseño) — se proponen dos, complementarios:**
- **Diseño A — Despliegue escalonado / *stepped-wedge* por sede:** dado que las sedes ya abren en
  fechas distintas (sección 1.7), se puede diseñar (prospectivamente) un cronograma de intensificación
  de campaña (vistas/inversión) **aleatorizado en el tiempo por sede**, de modo que cada sede sirva de
  control de sí misma antes de recibir el "empujón" de campaña, y de control de las demás mientras
  espera su turno. Esto separa el efecto del video del calendario de apertura y de inversión, porque
  el orden de asignación es aleatorio y no coincide por diseño con el resto de confusores.
- **Diseño B — Comparación controlada / diff-in-diff:** `ventas_soles ~ post + sede_FE + fecha_trend +
  inversion_publicitaria_soles + promocion_activa_flag + festival_abierto_flag`, con efectos fijos de
  sede y tendencia temporal, restringido a sedes abiertas todo el período (evita comparar sedes que
  no existían). Es lo que se aproxima en el Modelo D (sección 1.5), con la limitación honesta de que
  incluso así queda confundido por **cuáles** sedes están en la muestra (sesgo de selección de sede).
- Un experimento tipo A/B geográfico "puro" (video visible en unas zonas, no en otras) sería el diseño
  más limpio, pero no es viable retroactivamente sobre datos ya recolectados de un lanzamiento único
  y nacional — se deja como recomendación a futuro (piloto), no como análisis de este CSV.

**4) Umbral de decisión, definido ANTES de mirar el resultado (pre-registro):**
> Con los datos observacionales disponibles, el **efecto causal del video no está identificado**: el
> coeficiente de `post` cambia de signo según qué confusores se controlan (sección 1.5, modelos A–D).
> Por eso el umbral pre-registrado —ampliar la campaña únicamente si las **ventas incrementales por
> sol invertido en campaña son ≥ S/3 por sol**, con **intervalo de confianza al 95% que excluya el
> cero**, medido tras un diseño controlado (diff-in-diff con efectos fijos de sede + controles, o el
> piloto stepped-wedge)— queda **sin evaluar todavía**: los coeficientes disponibles (B: -5,185, D:
> -6,460 soles) son negativos, pero no son estimaciones causalmente limpias (persiste sesgo de
> selección de sede, ver límite abajo), así que no permiten declarar el umbral ni alcanzado ni
> descartado.

**Límite / trade-off:** ni el Modelo D ni la comparación intra-abiertas resuelven el confusor de
"cuáles sedes" — sedes que abrieron antes probablemente son mercados más grandes o maduros, así que
incluso restringiendo a "sedes abiertas" se compara una mezcla distinta de mercados en PRE vs. POST.
La conclusión honesta con datos puramente observacionales es: **no se puede atribuir el cambio de
ventas al video**, ni en un sentido ni en el otro; se necesita un diseño prospectivo (piloto
escalonado) para poder hablar de causalidad con algo de confianza.


## Pregunta 3 — Storyboard técnico (5 story points)

Ningún punto usa *"el video causó"* — el diseño de la P2 (datos observacionales, confusores no
resueltos) no lo justifica. Se usa *"coincide con"* / *"está asociado a"* / *"se solapa con"*.

Cada story point rotula explícitamente sus **4 piezas**: (1) título analítico, (2) tipo de
gráfico/vista, (3) evidencia mínima (datos concretos), (4) mensaje/decisión que debe extraer el
comité.

**Story point 1 — Contexto**
- **Título analítico:** "El período de campaña: 4 meses, 12 sedes, un lanzamiento el 15-abr"
- **Tipo de gráfico:** línea de tiempo (timeline) simple.
- **Evidencia mínima:** eje X = `fecha`, marcador vertical en 2026-04-15, conteo de sedes activas
  por semana (8 al inicio → 12 al final).
- **Mensaje/decisión:** establece el marco temporal sin insinuar todavía ningún efecto.

**Story point 2 — Patrón**
- **Título analítico:** "Las ventas promedio por sede-día suben +100% después del 15-abr (dato bruto)"
- **Tipo de gráfico:** barras agrupadas PRE vs. POST.
- **Evidencia mínima:** `ventas_soles` (sección 1.1), media PRE=3,839.6 vs. POST=7,689.9.
- **Mensaje/decisión:** se rotula explícitamente como *"diferencia bruta, sin controlar"* para que
  el comité no la lea como el número final.

**Story point 3 — Desagregación** *(contraevidencia)*
- **Título analítico:** "Al fijar la población de sedes, el patrón se invierte: -13%"
- **Tipo de gráfico:** balance plot de covariables (Figura 1) + barras comparativas ingenuo vs.
  controlado (Figura 2).
- **Evidencia mínima:** apertura 0.38→0.96, inversión 2.9x, promo 0→0.54 (fin de semana y lluvia sin
  cambio, sección 1.3); intra-sedes-abiertas PRE=9,130.3 vs. POST=7,956.2 → **-12.9%** (sección 1.4).
- **Mensaje/decisión:** es el punto que más debilita la historia del "boom": los confusores se
  movieron juntos, y controlando el más grande de ellos (apertura de sedes) el signo se invierte.

**Story point 4 — Método / trade-off**
- **Título analítico:** "Ni la comparación cruda ni la controlada alcanzan a aislar el efecto del video"
- **Tipo de gráfico:** tabla resumen de coeficientes de los 4 modelos.
- **Evidencia mínima:** sección 1.5: A +3,850 → B -5,185 → C -1,174 → D -6,460 soles.
- **Mensaje/decisión:** el coeficiente **cambia de signo** según qué se controla — firma clásica de
  un efecto no identificado con datos observacionales; trade-off explícito: más control reduce sesgo
  de confusión pero no elimina el sesgo de selección de sede.

**Story point 5 — Acción**
- **Título analítico:** "Recomendación: no ampliar la campaña todavía; correr un piloto escalonado con umbral pre-definido"
- **Tipo de gráfico:** tarjeta de cierre (KPI/resumen textual con el umbral, no un gráfico de datos).
- **Evidencia mínima:** umbral de decisión de la P2 (≥ S/3 de ventas incrementales por sol, IC95% sin
  cero, hoy sin evaluar) comparado contra los coeficientes observados (negativos, sección 1.5) + el
  diseño stepped-wedge propuesto como siguiente paso.
- **Mensaje/decisión:** cierra con la pregunta de decisión única de la P1.


## Pregunta 4 — Memo para el comité

> **Período:** mar-jun 2026, video 15-abr. **Métrica:** ventas incrementales por sol invertido.
> **Evidencia:** +100% bruto en ventas cae a -13% al restringir a sedes ya abiertas; el coeficiente
> post cambia de signo al controlar. **Método:** comparación intra-sedes-abiertas y regresión
> controlando apertura de sedes, inversión y promociones. **Limitación:** datos observacionales,
> efecto no identificado causalmente; sesgo de selección de sede. **Acción:** no ampliar la campaña;
> correr un piloto escalonado por sede. **Indicador futuro:** ventas incrementales por sol invertido
> en el piloto, contra umbral S/3/sol con IC95% que excluya cero.

*(Conteo real de palabras verificado por código en la celda siguiente — límite ≤90.)*


### Bitácora (5 frases)

1. **Lectura inicial (≤15 palabras):** "El video de Killa disparó las ventas +108%: hay que ampliar la campaña ya."
2. **KPI decisor:** *Ventas incrementales por sol invertido* = `(ventas_soles POST − ventas_soles esperado sin cambio de inversión/promo/apertura) / Δ inversión_publicitaria_soles`, calculado sobre `ventas_soles` por fecha×sede, período abr–jun 2026 vs. línea base mar–abr, segmento = sedes abiertas todo el período, meta = ≥ S/3 de venta incremental por sol con IC95% que excluya cero.
3. **Giro analítico:** al desagregar por `festival_abierto_flag` (sección 1.4) y correr la regresión con confusores (sección 1.5), la diferencia +100%/+108% se convierte en -13% (intra-sedes-abiertas) y el coeficiente de `post` se vuelve negativo y significativo (-5,185 a -6,460 soles) en ambos modelos controlados.
4. **Lectura revisada (≤15 palabras):** "El aumento bruto se confunde con sedes nuevas, inversión y promos; efecto no identificado."
5. **Consecuencia:** el comité no debe ampliar la campaña basándose en el titular; debe pedir un piloto escalonado con umbral pre-definido antes de comprometer presupuesto adicional.

**Por qué "vistas del video" / "+108%" NO es el KPI decisor:** `vistas_video_miles` es una métrica de
**actividad** (exposición al contenido, sube 3.2x junto con todo lo demás) y el "+108%" es una
métrica de **resultado bruto** (entradas vendidas sin descontar causas) — ninguna de las dos conecta
el gasto en campaña con un efecto *atribuible*. Ambas suben simplemente porque el tiempo avanza y
todos los confusores (sedes, inversión, promos) suben con ellas; su correlación con las ventas es en
gran parte compartida y **no identificable como causal** (sección 1.6: R² cruda 0.283 → R² parcial
~0.040 al controlar). El KPI decisor tiene que ser la métrica de **impacto** — ventas incrementales
por sol invertido, medida con un diseño que separe el video de sus confusores — porque es la única
que responde la pregunta de negocio real: *¿vale la pena poner más dinero en esto?*
