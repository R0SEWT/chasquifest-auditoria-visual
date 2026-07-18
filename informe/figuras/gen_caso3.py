"""Genera las figuras del Caso 3 (asistencia mensual, ChasquiFest).

Ejecutar desde la raiz del proyecto:
    uv run python informe/figuras/gen_caso3.py
"""
import estilo_figuras as ef
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

df = ef.load(3)
df["mes"] = pd.to_datetime(df["mes"])

# ------------------------------------------------------------------
# Serie total mensual (todas las sedes) y sus derivados
# ------------------------------------------------------------------
serie = (
    df.groupby("mes", as_index=False)["asistentes"].sum().sort_values("mes").reset_index(drop=True)
)
serie["anio"] = serie["mes"].dt.year
serie["numero_mes"] = serie["mes"].dt.month
serie["media_movil_3m"] = serie["asistentes"].rolling(3).mean()
serie["ytd"] = serie.groupby("anio")["asistentes"].cumsum()

# Numeros ancla de julio 2025 vs julio 2026 (recalculados desde el CSV)
jul25 = df[(df["anio"] == 2025) & (df["numero_mes"] == 7)]
jul26 = df[(df["anio"] == 2026) & (df["numero_mes"] == 7)]
tot25, tot26 = jul25["asistentes"].sum(), jul26["asistentes"].sum()
d25, d26 = jul25["dias_observados"].iloc[0], jul26["dias_observados"].iloc[0]
caida_bruta = (tot26 - tot25) / tot25 * 100
ritmo25, ritmo26 = tot25 / d25, tot26 / d26
cambio_ritmo = (ritmo26 - ritmo25) / ritmo25 * 100

print(f"jul25={tot25:,} jul26={tot26:,} caida_bruta={caida_bruta:+.2f}% cambio_ritmo={cambio_ritmo:+.2f}%")

# ====================================================================
# Figura Q1 -- serie mensual: tendencia + estacionalidad + quiebre + cobertura
# ====================================================================
fig, ax = ef.fig(ancho=8.6, alto=4.4)

ax.plot(
    serie["mes"], serie["asistentes"], marker="o", ms=3.4, lw=1.5, color=ef.AZUL,
    label="Asistentes (total festival, mensual)",
)

# Picos estacionales jul/dic (se excluye jul-2026, que esta truncado, no es un pico real)
picos = serie[
    serie["numero_mes"].isin([7, 12]) & ~((serie["anio"] == 2026) & (serie["numero_mes"] == 7))
]
ax.scatter(picos["mes"], picos["asistentes"], color=ef.AMBAR, s=42, zorder=4, label="Pico estacional (jul/dic)")

# Banda del quiebre Loreto/Ucayali
ax.axvspan(pd.Timestamp("2025-03-01"), pd.Timestamp("2025-06-01"), color=ef.MALO, alpha=0.10, zorder=1)
abr25_val = serie.loc[serie["mes"] == pd.Timestamp("2025-04-01"), "asistentes"].values[0]
ax.annotate(
    "Quiebre Loreto/Ucayali\n(mar-may 2025, solo 2/12 sedes)",
    xy=(pd.Timestamp("2025-04-01"), abr25_val),
    xytext=(pd.Timestamp("2024-05-01"), 148000),
    fontsize=8, color=ef.TINTA2,
    arrowprops=dict(arrowstyle="->", color=ef.MUTED, lw=0.9),
)

# Julio 2026 truncado
jul26_val = serie.loc[serie["mes"] == pd.Timestamp("2026-07-01"), "asistentes"].values[0]
ax.scatter(
    [pd.Timestamp("2026-07-01")], [jul26_val], color=ef.ALERTA, s=95, zorder=5,
    edgecolor=ef.TINTA, linewidth=0.6, label="Jul-2026 (12/31 dias)",
)
ax.annotate(
    "Jul-2026: 12 de 31 dias\n(cobertura 38.71%) -> NO\ncomparable con meses cerrados",
    xy=(pd.Timestamp("2026-07-01"), jul26_val),
    xytext=(pd.Timestamp("2025-05-15"), 128000),
    fontsize=8, color=ef.TINTA,
    arrowprops=dict(arrowstyle="->", color=ef.ALERTA, lw=1.0),
)

ax.set_title("Asistencia mensual ChasquiFest: tendencia, estacionalidad, quiebre y cobertura")
ax.set_ylabel("Asistentes (total, 12 sedes)")
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
plt.setp(ax.get_xticklabels(), rotation=40, ha="right")
ax.legend(loc="upper left", fontsize=8)
ef.limpia(ax)
ef.guardar(fig, "caso3_q1_serie.pdf")

# ====================================================================
# Figura Q2 -- dos paneles: media movil 3m (arriba) y YTD por anio (abajo)
# ====================================================================
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8.2, 6.2))

# Panel superior: media movil 3 meses (linea continua sobre todo el rango)
ax1.plot(serie["mes"], serie["asistentes"], color=ef.MUTED, lw=1.0, alpha=0.55, label="Asistentes (mensual, referencia)")
ax1.plot(serie["mes"], serie["media_movil_3m"], color=ef.NARANJA, lw=2.2, label="Media movil 3 meses")

jun26_mm = serie.loc[serie["mes"] == pd.Timestamp("2026-06-01"), "media_movil_3m"].values[0]
jul26_mm = serie.loc[serie["mes"] == pd.Timestamp("2026-07-01"), "media_movil_3m"].values[0]
ax1.scatter([pd.Timestamp("2026-07-01")], [jul26_mm], color=ef.ALERTA, s=70, zorder=5)
ax1.annotate(
    f"jul-26: {jul26_mm:,.0f}\n(contaminado por mes truncado,\nvs {jun26_mm:,.0f} en jun-26)",
    xy=(pd.Timestamp("2026-07-01"), jul26_mm),
    xytext=(pd.Timestamp("2025-01-15"), 138000),
    fontsize=8, color=ef.TINTA,
    arrowprops=dict(arrowstyle="->", color=ef.ALERTA),
)
ax1.set_ylabel("Asistentes")
ax1.set_title("Direccion reciente: media movil de 3 meses (WINDOW_AVG)", fontsize=10.5)
ax1.legend(loc="upper left", fontsize=8)
ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
plt.setp(ax1.get_xticklabels(), rotation=35, ha="right")
ef.limpia(ax1)

# Panel inferior: YTD por anio (reinicia en enero, eje X = mes del anio)
colores_anio = {2024: ef.AZUL, 2025: ef.VERDE, 2026: ef.AMBAR}
for anio, g in serie.groupby("anio"):
    g = g.sort_values("numero_mes")
    ls = (0, (4, 1.5)) if anio == 2026 else "-"
    ax2.plot(g["numero_mes"], g["ytd"], color=colores_anio[anio], lw=2.0, marker="o", ms=3, ls=ls, label=str(anio))

ytd_jul25 = serie.loc[serie["mes"] == pd.Timestamp("2025-07-01"), "ytd"].values[0]
ytd_jul26 = serie.loc[serie["mes"] == pd.Timestamp("2026-07-01"), "ytd"].values[0]
ax2.scatter([7, 7], [ytd_jul25, ytd_jul26], color=[ef.VERDE, ef.AMBAR], s=45, zorder=5, edgecolor="white", linewidth=0.6)
ax2.annotate(
    f"YTD-jul: 2025={ytd_jul25:,.0f}  2026={ytd_jul26:,.0f}\n(diferencia de solo -0.59%: 'falsa tranquilidad')",
    xy=(7, ytd_jul26), xytext=(7.3, 420000),
    fontsize=8, color=ef.TINTA,
    arrowprops=dict(arrowstyle="->", color=ef.MUTED),
)
ax2.axhline(0, color=ef.EJE, lw=0.6)
ax2.set_xlabel("Mes del anio")
ax2.set_ylabel("Asistentes acumulados (YTD)")
ax2.set_xticks(range(1, 13))
ax2.set_title("Progreso del anio: acumulado YTD, reinicia por anio (RUNNING_SUM)", fontsize=10.5)
ax2.legend(loc="upper left", fontsize=8, title="Anio")
ef.limpia(ax2)

fig.suptitle(
    "Media movil (direccion reciente) vs. acumulado YTD (progreso del anio): no son la misma pregunta",
    fontsize=10.5, y=0.995,
)
fig.tight_layout(rect=[0, 0, 1, 0.965])
ef.guardar(fig, "caso3_q2_ma_ytd.pdf")

# ====================================================================
# Figura Q3 -- barras divergentes: caida bruta vs cambio de ritmo diario
# ====================================================================
fig, ax = ef.fig(ancho=6.2, alto=4.2)

etiquetas = ["Caida bruta\n(total del mes)", "Cambio de ritmo diario\n(asistentes / dia)"]
valores = [caida_bruta, cambio_ritmo]
colores = [ef.MALO, ef.BUENO]
bars = ax.bar(etiquetas, valores, color=colores, width=0.55, zorder=3)
ax.axhline(0, color=ef.TINTA, lw=1.1, zorder=4)

for b, v in zip(bars, valores):
    dy, va = (4, "bottom") if v >= 0 else (-4, "top")
    ax.annotate(
        f"{v:+.1f}%", (b.get_x() + b.get_width() / 2, v), xytext=(0, dy),
        textcoords="offset points", ha="center", va=va, fontsize=9.5, color=ef.TINTA, fontweight="bold",
    )

ax.set_ylabel("Variacion julio 2026 vs. julio 2025")
ax.set_title("Mismo dato, dos denominadores: el signo se invierte")
ef.limpia(ax)
ef.guardar(fig, "caso3_q3_signo.pdf")

# ====================================================================
# Figura Q4 -- indice base 100 (ref ene-2025) por sede, resaltando el quiebre
# ====================================================================
base_ene25 = df[(df["anio"] == 2025) & (df["numero_mes"] == 1)].set_index("sede_id")["asistentes"]
sub = df[df["mes"] >= "2025-01-01"].copy()
sub["indice_base100"] = sub.apply(lambda r: r["asistentes"] / base_ene25[r["sede_id"]] * 100, axis=1)

fig, ax = ef.fig(ancho=8.4, alto=4.8)

resaltar = {"SED-11": ("Iquitos", ef.VERDE), "SED-12": ("Pucallpa", ef.MAGENTA)}
for sede_id, g in sub.groupby("sede_id"):
    g = g.sort_values("mes")
    if sede_id in resaltar:
        nombre, color = resaltar[sede_id]
        ax.plot(g["mes"], g["indice_base100"], color=color, lw=2.2, marker="o", ms=3.4, label=nombre, zorder=5)
    else:
        ax.plot(g["mes"], g["indice_base100"], color=ef.MUTED, lw=1.0, alpha=0.5, zorder=2)

ax.plot([], [], color=ef.MUTED, lw=1.4, label="Otras 10 sedes")
ax.axhline(100, color=ef.TINTA2, lw=0.8, ls="--", zorder=3)
ax.axvspan(pd.Timestamp("2025-03-01"), pd.Timestamp("2025-06-01"), color=ef.MALO, alpha=0.10, zorder=1)
ax.annotate(
    "Quiebre Loreto/Ucayali\n(interrupcion logistica ficticia)\nsolo 2 de 12 sedes",
    xy=(pd.Timestamp("2025-04-15"), 60),
    xytext=(pd.Timestamp("2025-08-15"), 52),
    fontsize=8, color=ef.TINTA,
    arrowprops=dict(arrowstyle="->", color=ef.MALO),
)

ax.set_ylabel("Indice (ene-2025 = 100)")
ax.set_title("Recuperacion relativa por sede: la V de Iquitos y Pucallpa")
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
plt.setp(ax.get_xticklabels(), rotation=40, ha="right")
ax.legend(loc="upper left", fontsize=8.5)
ef.limpia(ax)
ef.guardar(fig, "caso3_q4_index.pdf")

print("Caso 3: 4 figuras generadas.")
