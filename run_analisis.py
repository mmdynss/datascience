"""Jalankan: python run_analisis.py  -> membuat tabel (CSV) dan grafik (PNG) di folder outputs/."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

import analisis as a

INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e6e5e1", "#fcfcfb"
BLUE, ORANGE = "#2a78d6", "#eb6834"
plt.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "text.color": INK, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "axes.spines.top": False, "axes.spines.right": False, "font.size": 10,
    "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlelocation": "left",
    "legend.frameon": False,
})
a.OUT_DIR.mkdir(exist_ok=True)
DIV = LinearSegmentedColormap.from_list("div", [ORANGE, "#f2f1ee", BLUE])
SEQ = LinearSegmentedColormap.from_list("seq", ["#eaf1fb", BLUE, "#123a6e"])


def simpan(fig, nama):
    fig.tight_layout()
    fig.savefig(a.OUT_DIR / nama, dpi=160)
    plt.close(fig)


R = a.bangun_semua()
kab, prov = R["kab"], R["prov"]
tahun = sorted(kab["tahun"].unique())

# ---- tabel
R["deskripsi"].to_csv(a.OUT_DIR / "t1_deskripsi_dataset.csv", index=False)
R["kualitas"].to_csv(a.OUT_DIR / "t2_kualitas_data.csv", index=False)
kab.to_csv(a.OUT_DIR / "t3_data_panel_bersih.csv", index=False)
kab[["pertumbuhan", "tpt"]].describe().round(2).to_csv(a.OUT_DIR / "t4_statistik_deskriptif.csv")
R["outlier"].to_csv(a.OUT_DIR / "t5_outlier_iqr.csv", index=False)
R["korelasi"].to_csv(a.OUT_DIR / "t6_korelasi.csv")
a.ringkas_regresi(R["reg"]).to_csv(a.OUT_DIR / "t7_evaluasi_regresi.csv", index=False)
R["evaluasi_k"].round(4).to_csv(a.OUT_DIR / "t8_evaluasi_k.csv", index=False)
norm, _ = a.normalisasi(kab)
kab.join(norm).round(3).to_csv(a.OUT_DIR / "t9_data_ternormalisasi.csv", index=False)
hasil_km, pusat, km, _ = a.jalankan_kmeans(kab, R["k_terbaik"])
hasil_km.to_csv(a.OUT_DIR / "t10_hasil_cluster.csv", index=False)
pusat.to_csv(a.OUT_DIR / "t11_centroid_cluster.csv")

# ---- G1 rata-rata pertumbuhan per wilayah
rata = kab.groupby("wilayah")["pertumbuhan"].mean().sort_values()
fig, ax = plt.subplots(figsize=(7, 3.8))
b = ax.barh(rata.index, rata.values, color=BLUE, height=0.55)
for r, v in zip(b, rata.values):
    ax.text(v + 0.05, r.get_y() + r.get_height() / 2, f"{v:.2f}", va="center", fontsize=9, color=INK)
ax.axvline(prov["pertumbuhan"].mean(), color=INK2, ls="--", lw=1)
ax.text(prov["pertumbuhan"].mean(), -0.75, f"Provinsi {prov['pertumbuhan'].mean():.2f}", ha="center", fontsize=8, color=INK2)
ax.set_title("Rata-rata pertumbuhan ekonomi 2019-2025 (%)")
ax.grid(axis="y", visible=False)
simpan(fig, "g1_rata_pertumbuhan.png")


# ---- G2/G3 garis per tahun
def garis(kolom, judul, nama, pembanding):
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    for w in a.WILAYAH:
        d = kab[kab["wilayah"] == w]
        ax.plot(d["tahun"], d[kolom], color=a.WARNA[w], lw=2, marker="o", ms=4, label=w)
    ax.plot(prov["tahun"], prov[kolom], color=INK2, lw=1.5, ls="--", label="Provinsi Kepri")
    ax.set_xticks(tahun)
    ax.set_title(judul)
    ax.set_ylabel("%")
    if pembanding:
        ax.axhline(0, color=INK2, lw=0.8)
    ax.legend(ncol=4, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.1))
    simpan(fig, nama)


garis("pertumbuhan", "Pertumbuhan ekonomi per tahun (%)", "g2_tren_pertumbuhan.png", True)
garis("tpt", "Tingkat pengangguran terbuka per tahun (%)", "g3_tren_tpt.png", False)

# ---- G4 distribusi (boxplot)
fig, axs = plt.subplots(1, 2, figsize=(8, 3.8))
for ax, k, jd in zip(axs, ["pertumbuhan", "tpt"], ["Distribusi pertumbuhan (%)", "Distribusi TPT (%)"]):
    ax.boxplot(kab[k], widths=0.4, patch_artist=True,
               boxprops=dict(facecolor="#eaf1fb", edgecolor=BLUE), medianprops=dict(color=ORANGE, lw=2),
               whiskerprops=dict(color=BLUE), capprops=dict(color=BLUE),
               flierprops=dict(marker="o", markerfacecolor=ORANGE, markeredgecolor=SURF, ms=6))
    ax.set_title(jd)
    ax.set_xticks([])
    ax.grid(axis="x", visible=False)
simpan(fig, "g4_boxplot.png")

# ---- G5/G6 heatmap
def heat(kolom, judul, nama, cmap, tengah=None):
    pv = kab.pivot(index="wilayah", columns="tahun", values=kolom).loc[a.WILAYAH]
    fig, ax = plt.subplots(figsize=(8, 4.2))
    vmax = np.abs(pv.values).max()
    im = ax.imshow(pv.values, cmap=cmap, aspect="auto",
                   vmin=-vmax if tengah == 0 else pv.values.min(), vmax=vmax if tengah == 0 else pv.values.max())
    ax.set_xticks(range(len(pv.columns)), pv.columns)
    ax.set_yticks(range(len(pv.index)), pv.index)
    ax.grid(False)
    for i in range(pv.shape[0]):
        for j in range(pv.shape[1]):
            v = pv.values[i, j]
            ax.text(j, i, f"{v:.1f}", ha="center", va="center", fontsize=8,
                    color="white" if (tengah is None and v > pv.values.mean() * 1.2) else INK)
    ax.set_title(judul)
    for s in ax.spines.values():
        s.set_visible(False)
    fig.colorbar(im, ax=ax, shrink=0.8)
    simpan(fig, nama)


heat("pertumbuhan", "Pertumbuhan ekonomi (%): biru = naik, oranye = turun", "g5_heatmap_pertumbuhan.png", DIV, 0)
heat("tpt", "Tingkat pengangguran terbuka (%)", "g6_heatmap_tpt.png", SEQ)

# ---- G7 scatter + garis regresi (Model A)
fig, ax = plt.subplots(figsize=(7, 4.6))
for w in a.WILAYAH:
    d = kab[kab["wilayah"] == w]
    ax.scatter(d["tpt"], d["pertumbuhan"], s=36, color=a.WARNA[w], edgecolor=SURF, linewidth=1.2, label=w)
ma = R["reg"]["Model A: TPT"]["model"]
xs = np.linspace(kab["tpt"].min(), kab["tpt"].max(), 50)
ax.plot(xs, ma.predict(xs.reshape(-1, 1)), color=INK2, lw=1.5, ls="--")
ax.set_xlabel("Tingkat pengangguran terbuka (%)")
ax.set_ylabel("Pertumbuhan ekonomi (%)")
r = R["korelasi"].loc["pertumbuhan vs tpt", "Pearson"]
ax.set_title(f"TPT vs pertumbuhan ekonomi (r = {r:.2f})")
ax.legend(fontsize=8, ncol=2)
simpan(fig, "g7_scatter_tpt_pertumbuhan.png")

# ---- G8 elbow & silhouette
ev = R["evaluasi_k"]
fig, axs = plt.subplots(1, 2, figsize=(8.5, 3.6))
axs[0].plot(ev["k"], ev["inertia"], color=BLUE, lw=2, marker="o", ms=5)
axs[0].set_title("Elbow Method (inertia)")
axs[1].plot(ev["k"], ev["silhouette"], color=BLUE, lw=2, marker="o", ms=5)
kb = R["k_terbaik"]
axs[1].scatter([kb], [ev.set_index("k").loc[kb, "silhouette"]], s=90, color=ORANGE, zorder=5, edgecolor=SURF, linewidth=2)
axs[1].set_title(f"Silhouette Score (terbaik k = {kb})")
for ax in axs:
    ax.set_xlabel("Jumlah cluster (k)")
    ax.set_xticks(ev["k"])
simpan(fig, "g8_elbow_silhouette.png")

# ---- G9 scatter cluster
nama_cl = a.beri_nama_cluster(pusat)
pal = [ORANGE, "#1baf7a", BLUE, "#6250d6", "#eda100"]
fig, ax = plt.subplots(figsize=(7.5, 4.8))
for c in sorted(hasil_km["cluster"].unique()):
    d = hasil_km[hasil_km["cluster"] == c]
    ax.scatter(d["tpt"], d["pertumbuhan"], s=40, color=pal[c], edgecolor=SURF, linewidth=1.2, label=nama_cl[c])
    ax.scatter(pusat.loc[c, "tpt"], pusat.loc[c, "pertumbuhan"], marker="X", s=150, color=pal[c], edgecolor=INK, linewidth=1.2)
ax.set_xlabel("Tingkat pengangguran terbuka (%)")
ax.set_ylabel("Pertumbuhan ekonomi (%)")
ax.set_title(f"Hasil K-Means (k = {kb}); X = centroid")
ax.legend(fontsize=8, loc="lower right")
simpan(fig, "g9_cluster.png")

# ---- G10 aktual vs prediksi (Model B, data test)
hb = R["reg"]["Model B: TPT + dummy COVID-2020"]
fig, ax = plt.subplots(figsize=(5.2, 4.8))
ax.scatter(hb["yte"], hb["pred_te"], s=40, color=BLUE, edgecolor=SURF, linewidth=1.2)
lim = [min(hb["yte"].min(), hb["pred_te"].min()) - 1, max(hb["yte"].max(), hb["pred_te"].max()) + 1]
ax.plot(lim, lim, color=INK2, ls="--", lw=1)
ax.set_xlabel("Aktual (%)")
ax.set_ylabel("Prediksi (%)")
ax.set_title("Aktual vs prediksi (data uji, Model B)")
simpan(fig, "g10_aktual_vs_prediksi.png")

print("selesai:", sorted(p.name for p in a.OUT_DIR.iterdir()))
