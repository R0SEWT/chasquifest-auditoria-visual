"""Genera las figuras del Caso 1 -- Taquilla (Operacion ChasquiFest).

Reemplaza la torta falsa de "participacion en el exito" (suma de
ocupacion_fila_pct por canal, denominador sin sentido de negocio) por tres
figuras que responden tareas analiticas reales: comparar estimadores del
mismo KPI, comparar metricas por segmento, y parte-todo con el denominador
correcto.

Ejecutar:
    cd /home/rosewt-dell/Code/cursos/data-viz/ef
    uv run python informe/figuras/gen_caso1.py
"""
import numpy as np

import estilo_figuras as ef

df = ef.load(1)

# orden fijo de canal usado en todas las figuras del caso
CANAL_ORDEN = ["App", "Web", "Taquilla"]


# ---------------------------------------------------------------------
# Figura 1 (Pregunta 1) -- dos estimadores del mismo KPI de ocupacion
# Tarea: COMPARAR (ratio-of-sums vs mean-of-ratios) frente a la meta.
# ---------------------------------------------------------------------
occ_weighted = df.ingresos_validados.sum() / df.cupos_ofertados.sum() * 100
occ_avg_rows = df.ocupacion_fila_pct.mean()
meta = df.meta_ocupacion_pct.iloc[0]

fig, ax = ef.fig(6.2, 3.6)
labels = ["Ponderada\n(SUM ingresos / SUM cupos)", "Promedio simple\n(AVG ocupacion_fila_pct)"]
valores = [occ_weighted, occ_avg_rows]
colores = [ef.AZUL, ef.NARANJA]
rects = ax.bar(labels, valores, color=colores, width=0.55, zorder=3)
ef.etiqueta_barras(ax, rects, fmt="{:.2f}%")

ax.axhline(meta, color=ef.MALO, linestyle="--", linewidth=1.3, zorder=2)
ax.text(1.42, meta + 2.2, f"Meta: {meta:.0f}%", color=ef.MALO, fontsize=8.5,
        va="bottom", ha="left", fontweight="bold")

ax.set_ylabel("Ocupacion global del festival (%)")
ax.set_title(
    "Tarea: COMPARAR -- dos estimadores del mismo KPI de ocupacion\n"
    "n = 216 filas evento×canal, temporada abr–ago 2026",
    fontsize=9.5,
)
ax.set_ylim(0, max(valores) * 1.24)
ax.set_xlim(-0.6, 1.9)
ef.limpia(ax)
fig.tight_layout()
ef.guardar(fig, "caso1_q1_ocupacion.pdf")


# ---------------------------------------------------------------------
# Figura 2 (Pregunta 2) -- margen % vs ocupacion % ponderados por canal
# Tarea: COMPARAR metricas por segmento (canal): no se mueven juntas.
# ---------------------------------------------------------------------
g = df.groupby("canal").agg(
    ventas=("ventas_soles", "sum"),
    costo=("costo_variable_soles", "sum"),
    ingresos=("ingresos_validados", "sum"),
    cupos=("cupos_ofertados", "sum"),
).reindex(CANAL_ORDEN)
g["margen_pond"] = (g.ventas - g.costo) / g.ventas * 100
g["occ_pond"] = g.ingresos / g.cupos * 100

x = np.arange(len(CANAL_ORDEN))
w = 0.36

fig, ax = ef.fig(6.4, 3.7)
r1 = ax.bar(x - w / 2, g.margen_pond, width=w, color=ef.VERDE, zorder=3, label="Margen % ponderado")
r2 = ax.bar(x + w / 2, g.occ_pond, width=w, color=ef.AZUL, zorder=3, label="Ocupación % ponderada")
ef.etiqueta_barras(ax, r1, fmt="{:.1f}%")
ef.etiqueta_barras(ax, r2, fmt="{:.1f}%")

ax.set_xticks(x)
ax.set_xticklabels(CANAL_ORDEN)
ax.set_ylabel("% (ratio-of-sums por canal)")
ax.set_title(
    "Tarea: COMPARAR -- margen y ocupación por canal no se mueven juntos\n"
    "num/den declarados por canal (ver texto)",
    fontsize=9.5,
)
ax.set_ylim(0, max(g.margen_pond.max(), g.occ_pond.max()) * 1.22)
ax.legend(loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.0))
ef.limpia(ax)
fig.tight_layout()
ef.guardar(fig, "caso1_q2_metricas_canal.pdf")


# ---------------------------------------------------------------------
# Figura 3 (Pregunta 3) -- "torta de %s" falsa vs share real de ventas
# Tarea: PARTE-TODO -- el denominador correcto cambia quien domina.
# ---------------------------------------------------------------------
torta_falsa = {"App": 35.7, "Web": 33.8, "Taquilla": 30.5}
ventas_canal = df.groupby("canal").ventas_soles.sum().reindex(CANAL_ORDEN)
share_real = (ventas_canal / ventas_canal.sum() * 100)

x = np.arange(len(CANAL_ORDEN))
w = 0.36

fig, ax = ef.fig(6.4, 3.8)
r1 = ax.bar(
    x - w / 2, [torta_falsa[c] for c in CANAL_ORDEN], width=w,
    color=ef.MUTED, zorder=3, label="“Torta de %” falsa\n(SUM ocupacion_fila_pct, sin denominador real)",
)
r2 = ax.bar(
    x + w / 2, share_real.values, width=w,
    color=ef.MAGENTA, zorder=3, label="Share real de ventas\n(num=SUM ventas canal, den=SUM ventas total)",
)
ef.etiqueta_barras(ax, r1, fmt="{:.1f}%")
ef.etiqueta_barras(ax, r2, fmt="{:.1f}%")

ax.set_xticks(x)
ax.set_xticklabels(CANAL_ORDEN)
ax.set_ylabel("% del canal")
ax.set_title(
    "Tarea: PARTE-TODO -- el denominador correcto cambia quién domina\n"
    f"share real: den = SUM(ventas\\_soles) total = S/ {ventas_canal.sum():,.0f}",
    fontsize=9.5,
)
ax.set_ylim(0, max(max(torta_falsa.values()), share_real.max()) * 1.32)
ax.legend(loc="upper center", ncol=1, fontsize=7.6, bbox_to_anchor=(0.78, 1.02))
ef.limpia(ax)
fig.tight_layout()
ef.guardar(fig, "caso1_q3_share.pdf")

print("Caso 1: 3 figuras generadas.")
