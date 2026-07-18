"""Figuras del Caso 2 -- El espagueti de los Andes y la lluvia todopoderosa.

Genera los 4 PDF vectoriales citados en informe/secciones/caso2.tex a partir
de data/caso2_logistica_chasquifest.csv. Cada número que aparece en el texto
del informe se recalcula aquí desde el CSV (no hay cifras "de memoria").

Ejecutar desde la raíz del proyecto:
    uv run python informe/figuras/gen_caso2.py
"""
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

import estilo_figuras as ef

df = ef.load(2)

# Colores fijos por transportista: redundantes con la etiqueta directa
# (posición en X / título de panel), nunca el color como único canal.
TRANSPORTISTAS = ["Apu Express", "Costa Norte", "Río Rápido"]
COLOR_TRANSPORTISTA = {"Apu Express": ef.AZUL, "Costa Norte": ef.VERDE, "Río Rápido": ef.NARANJA}
MACROZONAS = ["Costa", "Sierra", "Selva"]


# ---------------------------------------------------------------------------
# Figura 1 (Pregunta 1d): R^2 de distancia vs. lluvia sobre minutos_reales
# Tarea: comparar la fuerza de dos asociaciones -> barras (posición, no dual-axis)
# ---------------------------------------------------------------------------
def fig_q1_r2():
    corr_dist = df["distancia_km"].corr(df["minutos_reales"])
    corr_lluvia = df["lluvia_mm"].corr(df["minutos_reales"])
    r2_dist, r2_lluvia = corr_dist ** 2, corr_lluvia ** 2

    fig, ax = ef.fig(6.0, 4.3)
    rects = ax.bar(
        ["Distancia (km)", "Lluvia (mm)"],
        [r2_dist, r2_lluvia],
        color=[ef.VIOLETA, ef.MUTED],
        width=0.5,
    )
    ef.etiqueta_barras(ax, rects, fmt="{:.1%}", dy=4)
    ax.set_ylabel(r"R$^2$ sobre minutos reales (n = 1\,728)")
    ax.set_title("¿Qué explica los minutos reales: distancia o lluvia?")
    ax.set_ylim(0, 1.0)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    ef.guardar(fig, "caso2_q1_r2.pdf")


# ---------------------------------------------------------------------------
# Figura 2 (Pregunta 2, Vista 1): distribución de minutos_reales
# por transportista, faceteada por macrozona, eje Y compartido.
# Tarea: comparar mediana y dispersión -> boxplot (posición = canal preciso)
# ---------------------------------------------------------------------------
def fig_q2_box():
    y_max = df["minutos_reales"].quantile(0.99) * 1.05
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 4.8), sharey=True)

    for ax, mz in zip(axes, MACROZONAS):
        sub = df[df["macrozona"] == mz]
        data = [sub.loc[sub["transportista"] == t, "minutos_reales"].values for t in TRANSPORTISTAS]
        ns = [len(d) for d in data]
        bp = ax.boxplot(
            data, patch_artist=True, widths=0.55,
            medianprops=dict(color=ef.TINTA, linewidth=1.8),
            flierprops=dict(marker="o", markersize=3, markerfacecolor=ef.MUTED,
                             markeredgecolor="none", alpha=0.6),
        )
        for patch, t in zip(bp["boxes"], TRANSPORTISTAS):
            patch.set_facecolor(COLOR_TRANSPORTISTA[t])
            patch.set_alpha(0.78)
        ax.set_xticks(range(1, len(TRANSPORTISTAS) + 1))
        ax.set_xticklabels([f"{t}\n(n={n})" for t, n in zip(TRANSPORTISTAS, ns)], fontsize=7.6)
        ax.set_title(mz, fontsize=10.5, fontweight="bold")
        ax.set_ylim(0, y_max)
        ax.grid(axis="x", visible=False)

    axes[0].set_ylabel("Minutos reales")
    fig.suptitle(
        "Minutos reales por transportista, dentro de cada macrozona\n"
        "(posición = mediana; caja = IQR; eje Y compartido entre paneles)",
        fontsize=10.5, fontweight="bold",
    )
    fig.tight_layout(rect=[0, 0, 1, 0.90])
    ef.guardar(fig, "caso2_q2_box.pdf")


# ---------------------------------------------------------------------------
# Figura 3 (Pregunta 2, Vista 2): distancia_km vs minutos_reales
# Tarea: evaluar fuerza/forma de una relación -> scatter + recta OLS
# ---------------------------------------------------------------------------
def fig_q2_scatter():
    slope, intercept, r, p, se = stats.linregress(df["distancia_km"], df["minutos_reales"])

    q1, q3 = df["minutos_reales"].quantile([0.25, 0.75])
    iqr = q3 - q1
    fence_hi = q3 + 1.5 * iqr
    is_outlier = df["minutos_reales"] > fence_hi

    fig, ax = ef.fig(6.4, 5.1)
    ax.scatter(
        df.loc[~is_outlier, "distancia_km"], df.loc[~is_outlier, "minutos_reales"],
        s=12, alpha=0.25, color=ef.AZUL, linewidths=0,
        label=f"Envíos (n={(~is_outlier).sum()})",
    )
    ax.scatter(
        df.loc[is_outlier, "distancia_km"], df.loc[is_outlier, "minutos_reales"],
        s=22, alpha=0.75, color=ef.ROJO, marker="^", linewidths=0,
        label=f"Outliers > 1.5$\\cdot$IQR (n={is_outlier.sum()})",
    )
    x_line = np.linspace(df["distancia_km"].min(), df["distancia_km"].max(), 100)
    ax.plot(
        x_line, slope * x_line + intercept, color=ef.TINTA, linewidth=1.8, linestyle="--",
        label=f"OLS: y = {slope:.2f}x + {intercept:.1f}",
    )
    ax.set_xlabel("Distancia (km)")
    ax.set_ylabel("Minutos reales")
    ax.set_title(f"Distancia vs. minutos reales  ·  r = {r:.3f}   R$^2$ = {r**2:.1%}   (n = {len(df)})")
    ax.legend(loc="upper left")
    fig.tight_layout()
    ef.guardar(fig, "caso2_q2_scatter.pdf")


# ---------------------------------------------------------------------------
# Figura 4 (Pregunta 3): pequeños múltiplos -- tasa de tardanza semanal
# por sede (12 paneles), escala común 0-100%, meta 20%, foco+contexto.
# Tarea: comparar evolución entre sedes sin espagueti.
# ---------------------------------------------------------------------------
def fig_q3_multiplos():
    wk_pivot = df.pivot_table(index="sede_id", columns="semana_inicio", values="tardanza_flag", aggfunc="mean")
    semanas = sorted(df["semana_inicio"].unique())

    sede_rate = df.groupby("sede_id")["tardanza_flag"].agg(tardios="sum", n="count")
    sede_rate["tasa"] = sede_rate["tardios"] / sede_rate["n"]
    sede_order = sede_rate.sort_values("tasa", ascending=False).index.tolist()
    peor_sede = sede_order[0]
    x = np.arange(len(semanas))

    fig, axes = plt.subplots(3, 4, figsize=(13, 8.2), sharex=True, sharey=True)
    axes = axes.flatten()

    for i, sede in enumerate(sede_order):
        ax = axes[i]
        for otra in sede_order:
            if otra == sede:
                continue
            ax.plot(x, wk_pivot.loc[otra, semanas].values, color=ef.MUTED, alpha=0.45,
                     linewidth=0.7, zorder=1)
        serie = wk_pivot.loc[sede, semanas].values
        color_foco = ef.MALO if sede == peor_sede else ef.AZUL
        ax.plot(x, serie, color=color_foco, linewidth=1.9, zorder=3)
        ax.scatter(x, serie, color=color_foco, s=8, zorder=3)
        ax.axhline(0.20, color=ef.TINTA2, linewidth=0.9, linestyle=":", zorder=2)
        ax.set_ylim(-0.05, 1.0)
        tasa_agg = sede_rate.loc[sede, "tasa"]
        ax.set_title(f"{sede}  ({tasa_agg:.0%})", fontsize=9, fontweight="bold", color=color_foco)
        ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
        ax.tick_params(labelsize=6.5)
        ax.grid(axis="x", visible=False)

    fig.suptitle(
        "Tasa de tardanza semanal por sede (n=8 envíos/sede-semana -> saltos de 12.5 pp)\n"
        "Escala común 0-100% en los 12 paneles · sede en color, resto en gris de contexto · "
        "línea punteada = meta 20% · orden de peor a mejor",
        fontsize=10.5, fontweight="bold",
    )
    fig.tight_layout(rect=[0, 0, 1, 0.90])
    ef.guardar(fig, "caso2_q3_multiplos.pdf")


if __name__ == "__main__":
    fig_q1_r2()
    fig_q2_box()
    fig_q2_scatter()
    fig_q3_multiplos()
