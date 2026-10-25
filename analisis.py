"""Pipeline analisis: Pertumbuhan Ekonomi vs Tingkat Pengangguran Kab/Kota Kepri 2019-2025.

Dipakai oleh run_analisis.py (membuat tabel & grafik untuk laporan) dan app.py (Streamlit).
"""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, silhouette_score
from sklearn.model_selection import KFold, cross_val_score, train_test_split
from sklearn.preprocessing import MinMaxScaler, StandardScaler

BASE = Path(__file__).resolve().parent
DATA_DIR = BASE / "data"
OUT_DIR = BASE / "outputs"

PROVINSI = "Kepulauan Riau"
# Urutan tetap (warna mengikuti entitas, bukan peringkat)
WILAYAH = ["Batam", "Bintan", "Karimun", "Lingga", "Natuna", "Kepulauan Anambas", "Tanjungpinang"]
WARNA = {
    "Batam": "#2a78d6", "Bintan": "#eb6834", "Karimun": "#1baf7a", "Lingga": "#eda100",
    "Natuna": "#e87ba4", "Kepulauan Anambas": "#6250d6", "Tanjungpinang": "#e34948",
}
FITUR_CLUSTER = ["pertumbuhan", "tpt"]
RANDOM_STATE = 42


# ---------------------------------------------------------------- 1. Data collection
def load_raw():
    """Baca dua dataset format lebar (wilayah x tahun)."""
    pe = pd.read_csv(DATA_DIR / "pertumbuhan_ekonomi.csv")
    tpt = pd.read_csv(DATA_DIR / "tingkat_pengangguran.csv")
    return pe, tpt


def deskripsi_dataset(pe, tpt):
    rows = []
    for nama, df, sumber in [
        ("Pertumbuhan Ekonomi (%, y-on-y)", pe, "BPS Provinsi Kepulauan Riau"),
        ("Tingkat Pengangguran Terbuka (%)", tpt, "BPS Provinsi Kepulauan Riau"),
    ]:
        rows.append({
            "Nama dataset": nama, "Instansi": sumber,
            "Periode": f"{df.columns[1]}-{df.columns[-1]}",
            "Jumlah baris": len(df), "Jumlah variabel": df.shape[1],
            "Format": "CSV (wide: wilayah x tahun)",
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- 2. Cleaning
def laporan_kualitas(pe, tpt):
    """Ringkasan pemeriksaan kualitas data (dipakai di laporan)."""
    out = []
    for nama, df in [("Pertumbuhan Ekonomi", pe), ("TPT", tpt)]:
        angka = df.drop(columns="Wilayah")
        out.append({
            "Dataset": nama,
            "Missing value": int(angka.isna().sum().sum()),
            "Baris duplikat": int(df.duplicated().sum()),
            "Nama wilayah duplikat": int(df["Wilayah"].duplicated().sum()),
            "Tipe kolom angka": ", ".join(sorted({str(t) for t in angka.dtypes})),
        })
    return pd.DataFrame(out)


def bersihkan(pe, tpt):
    """Cleaning + integrasi -> tabel panel (wilayah, tahun, pertumbuhan, tpt)."""
    def long(df, nilai):
        d = df.copy()
        d["Wilayah"] = d["Wilayah"].astype(str).str.strip()
        d = d.drop_duplicates()
        d = d.melt(id_vars="Wilayah", var_name="tahun", value_name=nilai)
        d["tahun"] = d["tahun"].astype(int)
        d[nilai] = pd.to_numeric(d[nilai], errors="coerce")
        return d

    panel = long(pe, "pertumbuhan").merge(long(tpt, "tpt"), on=["Wilayah", "tahun"], how="inner", validate="1:1")
    panel = panel.rename(columns={"Wilayah": "wilayah"})
    panel["covid_2020"] = (panel["tahun"] == 2020).astype(int)
    return panel.sort_values(["wilayah", "tahun"]).reset_index(drop=True)


def pisah_provinsi(panel):
    """Provinsi dipakai sebagai pembanding (benchmark), bukan objek analisis."""
    prov = panel[panel["wilayah"] == PROVINSI].reset_index(drop=True)
    kab = panel[panel["wilayah"].isin(WILAYAH)].reset_index(drop=True)
    return kab, prov


def deteksi_outlier(df, kolom=("pertumbuhan", "tpt")):
    """Outlier metode IQR (1.5 x IQR)."""
    hasil = []
    for k in kolom:
        q1, q3 = df[k].quantile([0.25, 0.75])
        iqr = q3 - q1
        lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        o = df[(df[k] < lo) | (df[k] > hi)][["wilayah", "tahun", k]].copy()
        o["variabel"] = k
        o["batas_bawah"], o["batas_atas"] = round(lo, 2), round(hi, 2)
        o = o.rename(columns={k: "nilai"})
        hasil.append(o)
    return pd.concat(hasil, ignore_index=True)


# ---------------------------------------------------------------- 3. Normalisasi
def normalisasi(df, kolom=FITUR_CLUSTER, metode="standard"):
    scaler = StandardScaler() if metode == "standard" else MinMaxScaler()
    Z = scaler.fit_transform(df[kolom])
    return pd.DataFrame(Z, columns=[f"{k}_norm" for k in kolom], index=df.index), scaler


# ---------------------------------------------------------------- 4a. K-Means
def evaluasi_k(Z, k_range=range(2, 7)):
    rows = []
    for k in k_range:
        km = KMeans(n_clusters=k, n_init=20, random_state=RANDOM_STATE).fit(Z)
        rows.append({"k": k, "inertia": km.inertia_, "silhouette": silhouette_score(Z, km.labels_)})
    return pd.DataFrame(rows)


def jalankan_kmeans(df, k):
    Z, scaler = normalisasi(df)
    km = KMeans(n_clusters=k, n_init=20, random_state=RANDOM_STATE).fit(Z)
    out = df.copy()
    out["cluster_id"] = km.labels_
    # Beri label berdasar centroid pada satuan asli: urut dari pertumbuhan terendah
    pusat = out.groupby("cluster_id")[FITUR_CLUSTER].mean().sort_values("pertumbuhan")
    urutan = {cid: i for i, cid in enumerate(pusat.index)}
    out["cluster"] = out["cluster_id"].map(urutan)
    pusat = out.groupby("cluster")[FITUR_CLUSTER].mean().round(2)
    pusat["jumlah_data"] = out.groupby("cluster").size()
    return out, pusat, km, scaler


def beri_nama_cluster(pusat):
    """Label cluster berdasar angka centroid (satuan asli), bukan klaim kualitatif."""
    return {
        c: f"Cluster {c}: pertumbuhan {r['pertumbuhan']:.1f}%, TPT {r['tpt']:.1f}% (n={int(r['jumlah_data'])})"
        for c, r in pusat.iterrows()
    }


# ---------------------------------------------------------------- 4b. Regresi
def korelasi(df):
    return pd.DataFrame({
        "Pearson": df[["pertumbuhan", "tpt"]].corr().iloc[0, 1],
        "Spearman": df[["pertumbuhan", "tpt"]].corr(method="spearman").iloc[0, 1],
    }, index=["pertumbuhan vs tpt"]).round(3)


def _metrik(y, p):
    return {
        "MAE": mean_absolute_error(y, p),
        "RMSE": float(np.sqrt(mean_squared_error(y, p))),
        "R2": r2_score(y, p),
    }


def regresi(df, fitur, test_size=0.2):
    X, y = df[fitur], df["pertumbuhan"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=test_size, random_state=RANDOM_STATE)
    model = LinearRegression().fit(Xtr, ytr)
    cv = cross_val_score(LinearRegression(), X, y, cv=KFold(5, shuffle=True, random_state=RANDOM_STATE), scoring="r2")
    return {
        "model": model, "fitur": fitur, "Xtr": Xtr, "Xte": Xte, "ytr": ytr, "yte": yte,
        "pred_te": model.predict(Xte),
        "metrik_train": _metrik(ytr, model.predict(Xtr)),
        "metrik_test": _metrik(yte, model.predict(Xte)),
        "cv_r2_mean": float(cv.mean()), "cv_r2_std": float(cv.std()),
        "koef": dict(zip(fitur, model.coef_)), "intercept": float(model.intercept_),
    }


def ringkas_regresi(hasil_dict):
    rows = []
    for nama, h in hasil_dict.items():
        rows.append({
            "Model": nama,
            "MAE (test)": round(h["metrik_test"]["MAE"], 3),
            "RMSE (test)": round(h["metrik_test"]["RMSE"], 3),
            "R2 (test)": round(h["metrik_test"]["R2"], 3),
            "R2 (train)": round(h["metrik_train"]["R2"], 3),
            "R2 CV 5-fold": f"{h['cv_r2_mean']:.3f} ± {h['cv_r2_std']:.3f}",
        })
    return pd.DataFrame(rows)


def bangun_semua():
    """Jalankan seluruh pipeline dan kembalikan dict hasil."""
    pe, tpt = load_raw()
    panel = bersihkan(pe, tpt)
    kab, prov = pisah_provinsi(panel)
    evk = evaluasi_k(normalisasi(kab)[0])
    k_terbaik = int(evk.loc[evk["silhouette"].idxmax(), "k"])
    return {
        "pe": pe, "tpt": tpt, "panel": panel, "kab": kab, "prov": prov,
        "kualitas": laporan_kualitas(pe, tpt), "deskripsi": deskripsi_dataset(pe, tpt),
        "outlier": deteksi_outlier(kab), "evaluasi_k": evk, "k_terbaik": k_terbaik,
        "korelasi": korelasi(kab),
        "reg": {
            "Model A: TPT": regresi(kab, ["tpt"]),
            "Model B: TPT + dummy COVID-2020": regresi(kab, ["tpt", "covid_2020"]),
        },
    }
