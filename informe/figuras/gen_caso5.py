"""Genera las figuras del Caso 5 -- Campana Killa (Operacion ChasquiFest).

El dashboard bajo auditoria afirma "Killa causo el boom: +108% de ventas tras
el video, confirmado por un scatter vistas<->entradas con linea de tendencia".
Estas tres figuras muestran, en orden, (1) que casi todos los confusores se
movieron junto con la fase de campana salvo fin de semana y lluvia, (2) que
la diferencia PRE/POST cambia de signo al fijar la poblacion de sedes, y
(3) que la correlacion cruda vistas-entradas se desinfla al controlar esos
mismos confusores -- ninguna de las tres autoriza a leer causalidad.

Ejecutar:
    cd /home/rosewt-dell/Code/cursos/data-viz/ef
    uv run python informe/figuras/gen_caso5.py
"""
import matplotlib.pyplot as plt
import numpy as np

import estilo_figuras as ef

df = ef.load(5)

pre = df[df.fase_campania == "Antes del video"]
post = df[df.fase_campania == "Después del video"]
open_df = df[df.festival_abierto_flag == 1]
pre_open = open_df[open_df.fase_campania == "Antes del video"]
post_open = open_df[open_df.fase_campania == "Después del video"]


# ---------------------------------------------------------------------
# Figura 1 (Pregunta 2) -- balance de confusores PRE vs POST
# Tarea: COMPARAR como cambia cada confusor entre fases (balance check).
# ---------------------------------------------------------------------
flags = ["festival_abierto_flag", "promocion_activa_flag", "fin_de_semana_flag", "lluvia_flag"]
labels_flags = ["Sede abierta", "Promoción\nactiva", "Fin de\nsemana", "Lluvia"]
pre_vals = [pre[c].mean() for c in flags]
post_vals = [post[c].mean() for c in flags]

fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(9.6, 4.0))

x = np.arange(len(flags))
w = 0.36
r1 = ax0.bar(x - w / 2, pre_vals, width=w, color=ef.MUTED, zorder=3, label="PRE (antes)")
r2 = ax0.bar(x + w / 2, post_vals, width=w, color=ef.VIOLETA, zorder=3, label="POST (después)")
ef.etiqueta_barras(ax0, r1, fmt="{:.2f}", size=8)
ef.etiqueta_barras(ax0, r2, fmt="{:.2f}", size=8)
ax0.set_xticks(x)
ax0.set_xticklabels(labels_flags, fontsize=8.5)
ax0.set_ylabel("proporción de filas (0-1)")
ax0.set_ylim(0, 1.16)
ax0.set_title("Confusores tipo indicador\n(sede y promo se mueven; finde y lluvia no)", fontsize=9.5)
ax0.legend(loc="upper right", fontsize=8)
ef.limpia(ax0)

cont = ["inversion_publicitaria_soles", "vistas_video_miles"]
labels_cont = ["Inversión\npublicitaria (S/)", "Vistas del\nvideo (miles)"]
razones = [post[c].mean() / pre[c].mean() for c in cont]
r3 = ax1.bar(labels_cont, razones, width=0.5, color=[ef.AMBAR, ef.AQUA], zorder=3)
ax1.axhline(1.0, color=ef.TINTA, linewidth=1.0, linestyle="--", zorder=2, label="sin cambio (razón=1)")
ef.etiqueta_barras(ax1, r3, fmt="{:.2f}x", size=9)
ax1.set_ylabel("razón POST / PRE")
ax1.set_ylim(0, max(razones) * 1.25)
ax1.set_title("Confusores continuos\n(cuántas veces más en POST que en PRE)", fontsize=9.5)
ax1.legend(loc="upper left", fontsize=8)
ef.limpia(ax1)

fig.suptitle(
    "Tarea: COMPARAR -- balance de confusores entre fases (n PRE=540, n POST=924)",
    fontsize=10.5, y=1.02,
)
fig.tight_layout()
ef.guardar(fig, "caso5_q2_confusores.pdf")


# ---------------------------------------------------------------------
# Figura 2 (Pregunta 2) -- diferencia PRE/POST: ingenua vs controlada
# Tarea: COMPARAR estimaciones del "efecto" bajo dos disenos distintos.
# ---------------------------------------------------------------------
diff_ingenua = (post.ventas_soles.mean() - pre.ventas_soles.mean()) / pre.ventas_soles.mean() * 100
diff_controlada = (
    (post_open.ventas_soles.mean() - pre_open.ventas_soles.mean()) / pre_open.ventas_soles.mean() * 100
)

fig, ax = ef.fig(7.2, 4.0)
etiquetas = [
    "Ingenua\n(todas las sedes,\nn=1,464)",
    "Controlada\n(solo sedes ya\nabiertas, n=1,097)",
]
valores = [diff_ingenua, diff_controlada]
colores = [ef.BUENO, ef.MALO]
rects = ax.barh(etiquetas, valores, color=colores, height=0.5, zorder=3)
ax.axvline(0, color=ef.TINTA, linewidth=1.1, zorder=2)
for r, v in zip(rects, valores):
    dx = 3 if v >= 0 else -3
    ha = "left" if v >= 0 else "right"
    ax.annotate(f"{v:+.1f}%", (v, r.get_y() + r.get_height() / 2), xytext=(dx, 0),
                textcoords="offset points", ha=ha, va="center", fontsize=11, fontweight="bold")
ax.set_xlabel("diferencia PRE→POST en ventas_soles promedio por sede-día (%)")
ax.set_title(
    "Tarea: COMPARAR -- el \"efecto\" cambia de signo al fijar la población de sedes\n"
    "num/den: (media POST − media PRE) / media PRE",
    fontsize=9.8,
)
xmax = max(abs(v) for v in valores) * 1.35
ax.set_xlim(-xmax, xmax)
ef.limpia(ax)
ax.grid(axis="y", visible=False)
fig.tight_layout()
ef.guardar(fig, "caso5_q2_efecto.pdf")


# ---------------------------------------------------------------------
# Figura 3 (Pregunta 3) -- scatter vistas vs entradas, cruda vs parcial
# Tarea: CORRELACIONAR -- la correlacion cruda se desinfla al controlar.
# ---------------------------------------------------------------------
r_crudo = df.vistas_video_miles.corr(df.entradas_vendidas)

feat_conf = ["festival_abierto_flag", "inversion_publicitaria_soles", "promocion_activa_flag",
             "fin_de_semana_flag", "lluvia_flag"]
Xc = np.column_stack([np.ones(len(df)), df[feat_conf].values])


def residualizar(y):
    b, _, _, _ = np.linalg.lstsq(Xc, y, rcond=None)
    return y - Xc @ b


res_vistas = residualizar(df.vistas_video_miles.values)
res_entradas = residualizar(df.entradas_vendidas.values)
r_parcial = np.corrcoef(res_vistas, res_entradas)[0, 1]

fig, ax = ef.fig(7.4, 4.6)
ax.scatter(pre.vistas_video_miles, pre.entradas_vendidas, s=16, color=ef.MUTED,
           alpha=0.6, label="PRE (antes del video)", zorder=3)
ax.scatter(post.vistas_video_miles, post.entradas_vendidas, s=16, color=ef.AZUL,
           alpha=0.55, label="POST (después del video)", zorder=3)

coef = np.polyfit(df.vistas_video_miles, df.entradas_vendidas, 1)
xs = np.linspace(df.vistas_video_miles.min(), df.vistas_video_miles.max(), 50)
ax.plot(xs, np.polyval(coef, xs), color=ef.ROJO, linewidth=1.8, zorder=4,
        label="tendencia cruda (dashboard)")

texto = (
    f"$r$ cruda = {r_crudo:.3f}  ($R^2$={r_crudo**2:.3f})\n"
    f"$r$ parcial (controlando confusores) = {r_parcial:.3f}  ($R^2$={r_parcial**2:.3f})"
)
ax.text(0.03, 0.97, texto, transform=ax.transAxes, ha="left", va="top", fontsize=9,
        bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor=ef.EJE))

ax.set_xlabel("vistas del video (miles)")
ax.set_ylabel("entradas vendidas (por fecha × sede)")
ax.set_title(
    "Tarea: CORRELACIONAR -- la asociación cruda se desinfla al controlar confusores\n"
    "misma tabla (n=1,464); color = fase de campaña, no tratamiento aleatorizado",
    fontsize=9.8,
)
ax.legend(loc="lower right", fontsize=8.3)
ef.limpia(ax)
fig.tight_layout()
ef.guardar(fig, "caso5_q3_scatter.pdf")

print("Caso 5: 3 figuras generadas.")
