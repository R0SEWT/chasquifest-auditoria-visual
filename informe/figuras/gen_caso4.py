"""Genera las figuras del Caso 4 -- Impacto departamental (Operacion ChasquiFest).

Reemplaza el mapa de burbujas que escalaba el DIAMETRO linealmente al valor
(inflando el AREA percibida) y pintaba la intensidad con el colormap `jet`
(no perceptualmente uniforme) por tres figuras que responden tareas
analiticas reales: comparar tres rankings con denominadores distintos,
localizar + normalizar en un mapa con area y viridis correctos, y demostrar
numericamente la distorsion diametro-vs-area.

Ejecutar:
    cd /home/rosewt-dell/Code/cursos/data-viz/ef
    uv run python informe/figuras/gen_caso4.py
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Circle

import estilo_figuras as ef

df = ef.load(4)


# ---------------------------------------------------------------------
# Figura 1 (Pregunta 1) -- tres rankings ordenados, mismo denominador
#   distinto por panel. Tarea: RANKING / comparacion de magnitud
#   (canal = posicion en eje, Cleveland & McGill). Lima y Cusco resaltados
#   para visualizar el reordenamiento segun el denominador.
# ---------------------------------------------------------------------
metrics = [
    ("asistentes_2025", "RANKING 1: VOLUMEN\nasistentes_2025 (den = ninguno)",
     "Asistencias 2025", "{:,.0f}"),
    ("alcance_por_1000_hab", "RANKING 2: ALCANCE\nvisit. unicos / poblacion x 1000",
     "Visit. unicos / 1,000 hab.", "{:,.1f}"),
    ("reclamos_por_10000_asistencias", "RANKING 3: RECLAMOS\nreclamos / asistencias x 10000",
     "Reclamos / 10,000 asist.", "{:,.1f}"),
]

fig, axes = plt.subplots(1, 3, figsize=(15.5, 5.6))

for ax, (col, title, xlabel, fmt) in zip(axes, metrics):
    d = df.sort_values(col, ascending=True)
    colors = [ef.ROJO if c == "Lima" else ef.AZUL if c == "Cusco" else ef.MUTED
              for c in d["ciudad"]]
    bars = ax.barh(d["ciudad"], d[col], color=colors, zorder=3)
    ax.set_title(title, fontsize=9.5)
    ax.set_xlabel(xlabel, fontsize=8.7)
    ax.tick_params(labelsize=8)
    xmax = d[col].max()
    for bar, val in zip(bars, d[col]):
        ax.text(bar.get_width() + xmax * 0.02, bar.get_y() + bar.get_height() / 2,
                 fmt.format(val), va="center", fontsize=7.3, color=ef.TINTA)
    ax.set_xlim(0, xmax * 1.24)
    ef.limpia(ax)

fig.legend(handles=[Patch(color=ef.ROJO, label="Lima"),
                     Patch(color=ef.AZUL, label="Cusco"),
                     Patch(color=ef.MUTED, label="Resto (9 sedes)")],
           loc="upper center", ncol=3, bbox_to_anchor=(0.5, 1.04),
           fontsize=9, frameon=False)
fig.suptitle(
    "Tarea: RANKING -- mismas 12 sedes, 2025, tres denominadores distintos\n"
    "(Lima #1 en volumen -> #12 en alcance | Cusco #2 en volumen -> #1 en alcance y #1 en reclamos)",
    y=1.16, fontsize=10.5, fontweight="bold",
)
fig.tight_layout()
ef.guardar(fig, "caso4_q1_rankings.pdf")


# ---------------------------------------------------------------------
# Figura 2 (Pregunta 2) -- mapa de burbujas: localizacion + intensidad
#   Tarea: LOCALIZACION geografica + tasa normalizada.
#   area (no diametro) ~ asistentes_2025 (volumen absoluto);
#   color = viridis sobre alcance_por_1000_hab (tasa normalizada).
# ---------------------------------------------------------------------
fig, ax = ef.fig(8.6, 7.4)

s_area = df["asistentes_2025"] / df["asistentes_2025"].max() * 1600  # s = k*valor => area ~ valor
sc = ax.scatter(
    df["longitud"], df["latitud"], s=s_area, c=df["alcance_por_1000_hab"],
    cmap="viridis", alpha=0.88, edgecolors=ef.TINTA, linewidths=0.7, zorder=3,
)
for _, row in df.iterrows():
    ax.annotate(
        f"{row['ciudad']}\n{row['alcance_por_1000_hab']:.0f}",
        (row["longitud"], row["latitud"]),
        fontsize=7.6, ha="center", va="center", fontweight="bold", color=ef.TINTA,
        zorder=4,
    )

cbar = plt.colorbar(sc, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label("alcance_por_1000_hab (viridis, escala perceptualmente uniforme)", fontsize=8.5)
cbar.ax.tick_params(labelsize=7.5)

ax.set_xlabel("Longitud", fontsize=9.5)
ax.set_ylabel("Latitud", fontsize=9.5)
ax.set_title(
    "Tarea: LOCALIZACION + tasa normalizada -- 12 sedes, 2025\n"
    "area del simbolo $\\propto$ asistentes_2025 (volumen)  |  color = alcance_por_1000_hab (tasa)",
    fontsize=10,
)
ax.tick_params(labelsize=8.5)
ax.grid(True, linewidth=0.5, color=ef.GRID, zorder=0)
fig.tight_layout()
ef.guardar(fig, "caso4_q2_mapa.pdf")


# ---------------------------------------------------------------------
# Figura 3 (Pregunta 3) -- distorsion diametro-vs-area, Lima vs Pucallpa
#   Tarea: mostrar la distorsion perceptual del area cuando el diametro
#   se escala linealmente al valor, y su correccion.
# ---------------------------------------------------------------------
val_lima = df.loc[df.ciudad == "Lima", "asistentes_2025"].item()
val_puca = df.loc[df.ciudad == "Pucallpa", "asistentes_2025"].item()
r_valor = val_lima / val_puca  # razon de VALOR real

fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(11.5, 6.0))
for ax in (ax0, ax1):
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.08, 1.12)
    ax.set_aspect("equal")
    ax.axis("off")

# --- Panel izquierdo: INCORRECTO, diametro ~ valor ---
max_r = 0.30
ax0.text(0.5, 1.04, "Diametro $\\propto$ valor (INCORRECTO)", ha="center",
         fontsize=10.5, fontweight="bold", color=ef.MALO)
ax0.text(0.5, 0.95, f"razon diametros = r = {r_valor:.2f}x", ha="center", fontsize=8.8)
ax0.text(0.5, 0.89, f"razon AREAS = r$^2$ = {r_valor**2:.2f}x  (lo que el ojo integra)",
         ha="center", fontsize=8.8, color=ef.MALO, fontweight="bold")
ax0.add_patch(Circle((0.28, 0.42), max_r, color=ef.ROJO, alpha=0.62, zorder=3))
ax0.add_patch(Circle((0.78, 0.42), max_r / r_valor, color=ef.MUTED, alpha=0.75, zorder=3))
ax0.text(0.28, 0.42 - max_r - 0.07, f"Lima\n{val_lima:,.0f}", ha="center", va="top", fontsize=8.6)
ax0.text(0.78, 0.42 - max_r / r_valor - 0.07, f"Pucallpa\n{val_puca:,.0f}", ha="center", va="top", fontsize=8.6)
ax0.text(0.5, -0.06, f"sobre-representacion visual extra = r$^2$/r = {r_valor**2/r_valor:.2f}x  ( = r )",
         ha="center", fontsize=8, style="italic", color=ef.TINTA2)

# --- Panel derecho: CORREGIDO, area ~ valor ---
max_r2 = 0.30
ax1.text(0.5, 1.04, "Area $\\propto$ valor (CORREGIDO)", ha="center",
         fontsize=10.5, fontweight="bold", color=ef.BUENO)
ax1.text(0.5, 0.95, f"razon diametros = $\\sqrt{{r}}$ = {np.sqrt(r_valor):.2f}x", ha="center", fontsize=8.8)
ax1.text(0.5, 0.89, f"razon AREAS = r = {r_valor:.2f}x  (coincide con el dato real)",
         ha="center", fontsize=8.8, color=ef.BUENO, fontweight="bold")
ax1.add_patch(Circle((0.28, 0.42), max_r2, color=ef.VERDE, alpha=0.62, zorder=3))
ax1.add_patch(Circle((0.78, 0.42), max_r2 / np.sqrt(r_valor), color=ef.MUTED, alpha=0.75, zorder=3))
ax1.text(0.28, 0.42 - max_r2 - 0.07, f"Lima\n{val_lima:,.0f}", ha="center", va="top", fontsize=8.6)
ax1.text(0.78, 0.42 - max_r2 / np.sqrt(r_valor) - 0.07, f"Pucallpa\n{val_puca:,.0f}", ha="center", va="top", fontsize=8.6)
ax1.text(0.5, -0.06, "diametro $\\propto \\sqrt{valor}$  =>  area = razon real de asistentes",
         ha="center", fontsize=8, style="italic", color=ef.TINTA2)

fig.suptitle(
    "Tarea: demostrar la distorsion perceptual del area -- Lima vs. Pucallpa, asistentes_2025",
    fontsize=11, fontweight="bold", y=1.03,
)
fig.tight_layout()
ef.guardar(fig, "caso4_q3_distorsion.pdf")

print("Caso 4: 3 figuras generadas.")
