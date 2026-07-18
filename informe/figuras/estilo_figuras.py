"""Hoja de estilo compartida para las figuras del informe ChasquiFest.

Todas las figuras del informe importan este módulo para verse como un solo
sistema: misma tipografía serif (acorde al LaTeX Latin Modern), misma paleta
validada (colorblind-safe), mismos ejes recesivos y salida PDF vectorial.

Uso en informe/figuras/gen_casoN.py:
    import estilo_figuras as ef
    df = ef.load(1)
    fig, ax = ef.fig(ancho=6.2, alto=3.6)
    ...
    ef.guardar(fig, "caso1_q1_ocupacion.pdf")
"""
from pathlib import Path
import matplotlib
matplotlib.use("pdf")            # backend vectorial, sin display
import matplotlib.pyplot as plt
import pandas as pd

# --- rutas (robustas al cwd) ---
FIGS = Path(__file__).resolve().parent          # informe/figuras
ROOT = FIGS.parents[1]                            # ef/
DATA = ROOT / "data"

# --- paleta validada (dataviz skill, modo claro) ---
AZUL="#2a78d6"; VERDE="#008300"; MAGENTA="#e87ba4"; AMBAR="#eda100"
AQUA="#1baf7a"; NARANJA="#eb6834"; VIOLETA="#4a3aa7"; ROJO="#e34948"
CAT = [AZUL, VERDE, MAGENTA, AMBAR, AQUA, NARANJA, VIOLETA, ROJO]  # orden fijo
# estados (fijos, nunca como serie)
BUENO="#0ca30c"; BUENO_TINTA="#006300"; MALO="#d03b3b"; ALERTA="#eda100"
# tintas y cromo
TINTA="#0b0b0b"; TINTA2="#52514e"; MUTED="#898781"; GRID="#e1e0d9"; EJE="#c3c2b7"
# secuencial azul (magnitud) low->high
SEQ = ["#cde2fb","#9ec5f4","#6da7ec","#3987e5","#256abf","#184f95","#0d366b"]

plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 150,
    "figure.facecolor": "white", "savefig.facecolor": "white",
    "savefig.bbox": "tight", "savefig.pad_inches": 0.03,
    "font.family": "serif", "font.serif": ["DejaVu Serif"], "font.size": 10,
    "mathtext.fontset": "dejavuserif",
    "axes.titlesize": 11, "axes.titleweight": "bold", "axes.titlepad": 8,
    "axes.labelsize": 9.5, "axes.labelcolor": TINTA,
    "axes.edgecolor": EJE, "axes.linewidth": 0.8,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "xtick.color": TINTA2, "ytick.color": TINTA2,
    "xtick.labelsize": 8.5, "ytick.labelsize": 8.5, "text.color": TINTA,
    "legend.frameon": False, "legend.fontsize": 8.5,
})

_FILES = {1:"caso1_taquilla", 2:"caso2_logistica", 3:"caso3_asistencia_mensual",
          4:"caso4_impacto_departamental", 5:"caso5_campania_killa"}

def load(n:int) -> pd.DataFrame:
    """Carga el CSV del caso n."""
    return pd.read_csv(DATA / f"{_FILES[n]}_chasquifest.csv")

def fig(ancho=6.2, alto=3.6):
    """Devuelve (fig, ax) con el tamaño dado en pulgadas."""
    return plt.subplots(figsize=(ancho, alto))

def limpia(ax):
    """Quita spines top/right (ya por rcParams) y afina el grid al eje y."""
    ax.grid(axis="x", visible=False)
    return ax

def etiqueta_barras(ax, rects, fmt="{:.1f}", dx=0, dy=3, color=None, size=8.5):
    """Etiqueta directa sobre barras verticales."""
    for r in rects:
        h = r.get_height()
        ax.annotate(fmt.format(h), (r.get_x()+r.get_width()/2, h),
                    xytext=(dx, dy), textcoords="offset points",
                    ha="center", va="bottom", fontsize=size,
                    color=color or TINTA)

def guardar(fig, nombre:str):
    """Guarda la figura como PDF vectorial en informe/figuras/ y la cierra."""
    out = FIGS / nombre
    fig.savefig(out)
    plt.close(fig)
    print(f"  guardada: figuras/{nombre}")
    return out
