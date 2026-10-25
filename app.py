"""Dashboard interaktif: Pertumbuhan Ekonomi & Pengangguran Kab/Kota Kepri 2019-2025.
Jalankan: python -m streamlit run app.py
"""
import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

import analisis as a

st.set_page_config(page_title="Dashboard Ekonomi & Pengangguran Kepri", layout="wide")

# ------------------------------------------------------------------ tema CSS (tampilan modern)
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root { --biru:#2a78d6; --ungu:#6250d6; --navy:#123a6e; --garis:rgba(128,128,128,.22); --kartu:rgba(128,128,128,.07); }
html { scroll-behavior:smooth; }
.stApp, .stApp button, .stApp input, .stApp textarea { font-family:'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif; }
.block-container { padding-top:1.4rem; padding-bottom:3rem; max-width:1320px; animation:naik .55s ease both; }
@keyframes naik { from { opacity:0; transform:translateY(12px); } to { opacity:1; transform:none; } }

/* judul */
.stApp h3 { border-left:4px solid var(--biru); padding-left:.65rem; letter-spacing:-.01em; font-weight:700; margin-top:1.2rem; }

/* hero (Beranda) */
.hero { position:relative; overflow:hidden; color:#fff; border-radius:24px; padding:2.2rem 2.4rem; margin-bottom:1.4rem;
  background:linear-gradient(135deg,#123a6e 0%,#2a78d6 55%,#6250d6 100%); box-shadow:0 18px 40px rgba(42,120,214,.28); }
.hero::before { content:""; position:absolute; right:-60px; top:-80px; width:300px; height:300px; border-radius:50%; background:rgba(255,255,255,.10); }
.hero::after { content:""; position:absolute; right:120px; bottom:-110px; width:220px; height:220px; border-radius:50%; background:rgba(255,255,255,.07); }
.hero .lencana { display:inline-block; font-size:.72rem; font-weight:700; letter-spacing:.14em; padding:.3rem .8rem; border-radius:999px; background:rgba(255,255,255,.18); }
.hero h1 { color:#fff !important; margin:.8rem 0 .4rem 0; padding:0; font-size:2.15rem; line-height:1.18; font-weight:800; letter-spacing:-.02em; position:relative; z-index:1; }
.hero p { color:rgba(255,255,255,.9); max-width:62ch; margin:0 0 1rem 0; font-size:1.02rem; position:relative; z-index:1; }
.hero .chip { display:inline-block; margin:0 .5rem .4rem 0; padding:.35rem .85rem; border-radius:999px; font-size:.82rem; font-weight:600;
  background:rgba(255,255,255,.16); border:1px solid rgba(255,255,255,.28); backdrop-filter:blur(6px); position:relative; z-index:1; }

/* banner judul halaman */
.banner { border-radius:18px; padding:1.05rem 1.4rem; margin-bottom:1.1rem; border-left:6px solid var(--biru);
  background:linear-gradient(90deg, rgba(42,120,214,.16), rgba(98,80,214,.04)); }
.banner h2 { margin:0 !important; padding:0 !important; font-size:1.6rem; font-weight:800; letter-spacing:-.02em; }
.banner p { margin:.2rem 0 0 0; opacity:.75; font-size:.95rem; }

/* sidebar */
[data-testid="stSidebar"] { background:linear-gradient(180deg, rgba(42,120,214,.16), rgba(98,80,214,.08)); border-right:1px solid var(--garis); }
[data-testid="stSidebar"] [role="radiogroup"] { gap:.25rem; }
[data-testid="stSidebar"] [role="radiogroup"] label { padding:.55rem .85rem; border-radius:12px; transition:background .2s, transform .2s; cursor:pointer; width:100%; }
[data-testid="stSidebar"] [role="radiogroup"] label:hover { background:rgba(42,120,214,.14); transform:translateX(4px); }
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) { background:linear-gradient(135deg,var(--biru),var(--ungu)); box-shadow:0 6px 16px rgba(42,120,214,.35); }
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p { color:#fff !important; font-weight:700; }

/* kartu metrik */
[data-testid="stVerticalBlockBorderWrapper"] { border-radius:18px; transition:transform .25s ease, box-shadow .25s ease; }
[data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stMetric"]) { border-left:5px solid var(--biru); background:var(--kartu); }
[data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stMetric"]):hover { transform:translateY(-4px); box-shadow:0 14px 30px rgba(42,120,214,.20); }
[data-testid="stMetricLabel"] p { font-size:.8rem; text-transform:uppercase; letter-spacing:.06em; opacity:.75; font-weight:600; }
[data-testid="stMetricValue"] { font-weight:800; letter-spacing:-.02em; }

/* tab */
.stTabs [data-baseweb="tab-list"] { gap:6px; background:var(--kartu); padding:5px; border-radius:14px; }
.stTabs [data-baseweb="tab"] { height:auto; padding:.5rem 1.05rem; border-radius:10px; transition:background .2s; }
.stTabs [data-baseweb="tab"]:hover { background:rgba(42,120,214,.14); }
.stTabs [aria-selected="true"] { background:linear-gradient(135deg,var(--biru),var(--ungu)); box-shadow:0 6px 14px rgba(42,120,214,.30); }
.stTabs [aria-selected="true"] p { color:#fff !important; font-weight:700; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display:none; }

/* grafik, tabel, expander, alert */
[data-testid="stVegaLiteChart"], [data-testid="stArrowVegaLiteChart"] { border:1px solid var(--garis); border-radius:18px; padding:.7rem .6rem .4rem .6rem; background:var(--kartu); transition:box-shadow .25s ease; }
[data-testid="stVegaLiteChart"]:hover, [data-testid="stArrowVegaLiteChart"]:hover { box-shadow:0 12px 30px rgba(0,0,0,.12); }
[data-testid="stDataFrame"] { border:1px solid var(--garis); border-radius:16px; overflow:hidden; }
[data-testid="stExpander"] { border:1px solid var(--garis); border-radius:16px; overflow:hidden; background:var(--kartu); }
[data-testid="stExpander"] summary:hover { background:rgba(42,120,214,.10); }
[data-testid="stAlert"] { border-radius:16px; }
.stButton button, .stDownloadButton button { border-radius:12px; transition:transform .2s, box-shadow .2s; }
.stButton button:hover { transform:translateY(-2px); box-shadow:0 8px 18px rgba(42,120,214,.28); }
[data-testid="stCaptionContainer"] { opacity:.8; }
@media (max-width: 768px) { .hero { padding:1.4rem 1.2rem; } .hero h1 { font-size:1.5rem; } }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def hero(judul, sub, chips):
    html = (
        '<div class="hero"><span class="lencana">DATA SAINS &middot; FTTK UMRAH</span>'
        f"<h1>{judul}</h1><p>{sub}</p>"
        + "".join(f'<span class="chip">{c}</span>' for c in chips)
        + "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)


def banner(judul, sub=""):
    st.markdown(f'<div class="banner"><h2>{judul}</h2><p>{sub}</p></div>', unsafe_allow_html=True)

# ------------------------------------------------------------------ konstanta tampilan
SKALA_WILAYAH = alt.Scale(domain=list(a.WARNA.keys()), range=list(a.WARNA.values()))
PAL_CLUSTER = ["#eb6834", "#1baf7a", "#2a78d6", "#6250d6", "#eda100", "#e34948"]
ABU = "#8a8985"
LABEL = {"pertumbuhan": "Pertumbuhan ekonomi (%)", "tpt": "Tingkat pengangguran terbuka (%)"}
TT = [
    alt.Tooltip("wilayah:N", title="Wilayah"),
    alt.Tooltip("tahun:O", title="Tahun"),
    alt.Tooltip("pertumbuhan:Q", title="Pertumbuhan (%)", format=".2f"),
    alt.Tooltip("tpt:Q", title="TPT (%)", format=".2f"),
]


def warna_wilayah(legenda=True):
    return alt.Color(
        "wilayah:N", scale=SKALA_WILAYAH,
        legend=alt.Legend(title="Wilayah (klik untuk menyorot)") if legenda else None,
    )


@st.cache_data
def muat():
    return a.bangun_semua()


R = muat()
kab, prov = R["kab"], R["prov"]
semua_tahun = sorted(kab["tahun"].unique().tolist())

# ------------------------------------------------------------------ sidebar: menu + filter global
halaman = st.sidebar.radio(
    "Menu",
    ["Beranda", "1. Data Collection", "2. Data Cleaning", "3. Normalisasi", "4. EDA",
     "5. K-Means Clustering", "6. Linear Regression & Prediksi", "7. Kesimpulan"],
)
st.sidebar.markdown("---")
st.sidebar.markdown("**Filter tampilan**")
pilih_wilayah = st.sidebar.multiselect("Wilayah", a.WILAYAH, default=a.WILAYAH)
rentang = st.sidebar.slider(
    "Rentang tahun", min_value=semua_tahun[0], max_value=semua_tahun[-1],
    value=(semua_tahun[0], semua_tahun[-1]),
)
st.sidebar.caption("Filter berlaku di Beranda dan EDA. Model K-Means dan regresi selalu memakai seluruh data.")
st.sidebar.caption("Sumber data: BPS Provinsi Kepulauan Riau, 2019-2025.")

kf = kab[kab["wilayah"].isin(pilih_wilayah) & kab["tahun"].between(*rentang)]
pf = prov[prov["tahun"].between(*rentang)]
if kf.empty and halaman in ("Beranda", "4. EDA"):
    st.warning("Pilih minimal satu wilayah di panel kiri.")
    st.stop()


def penjelasan(teks):
    with st.expander("Penjelasan sederhana (klik untuk membuka)"):
        st.markdown(teks)


# ------------------------------------------------------------------ fungsi grafik
def grafik_tren(df, pembanding, kolom, nol=False, tampil_prov=True):
    pilih = alt.selection_point(fields=["wilayah"], bind="legend")
    x = alt.X("tahun:O", title="Tahun", axis=alt.Axis(labelAngle=0))
    y = alt.Y(f"{kolom}:Q", title=LABEL[kolom])
    base = alt.Chart(df).encode(
        x=x, y=y, color=warna_wilayah(),
        opacity=alt.condition(pilih, alt.value(1.0), alt.value(0.12)),
    )
    lapisan = [
        base.mark_line(strokeWidth=2.5),
        base.mark_point(filled=True, size=80).encode(tooltip=TT),
    ]
    if tampil_prov:
        lapisan.append(
            alt.Chart(pembanding).mark_line(color=ABU, strokeDash=[6, 4], strokeWidth=2).encode(
                x=x, y=y,
                tooltip=[alt.Tooltip("tahun:O", title="Tahun"),
                         alt.Tooltip(f"{kolom}:Q", title="Provinsi Kepri", format=".2f")],
            )
        )
    if nol:
        lapisan.append(
            alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(color=ABU).encode(y=alt.Y("y:Q", title=LABEL[kolom]))
        )
    return alt.layer(*lapisan).add_params(pilih).properties(height=380)


def grafik_heat(df, kolom):
    if kolom == "pertumbuhan":
        skala = alt.Scale(domain=[-8, 0, 16], range=["#eb6834", "#f2f1ee", "#2a78d6"], clamp=True)
        ambang = 10
    else:
        skala = alt.Scale(domain=[0, 12], range=["#eaf1fb", "#123a6e"], clamp=True)
        ambang = 8
    dasar = alt.Chart(df).encode(
        x=alt.X("tahun:O", title="Tahun", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("wilayah:N", sort=a.WILAYAH, title=None),
    )
    kotak = dasar.mark_rect().encode(color=alt.Color(f"{kolom}:Q", scale=skala, title=LABEL[kolom]), tooltip=TT)
    teks = dasar.mark_text(fontSize=12).encode(
        text=alt.Text(f"{kolom}:Q", format=".1f"),
        color=alt.condition(f"datum.{kolom} > {ambang}", alt.value("white"), alt.value("#0b0b0b")),
    )
    return (kotak + teks).properties(height=320)


def grafik_batang_tahun(df, nilai_prov, kolom, tahun):
    batang = alt.Chart(df).mark_bar(cornerRadiusEnd=4).encode(
        x=alt.X(f"{kolom}:Q", title=LABEL[kolom]),
        y=alt.Y("wilayah:N", sort="-x", title=None),
        color=warna_wilayah(legenda=False),
        tooltip=TT,
    )
    garis = alt.Chart(pd.DataFrame({"v": [nilai_prov]})).mark_rule(
        color=ABU, strokeDash=[6, 4], strokeWidth=2
    ).encode(x=alt.X("v:Q", title=LABEL[kolom]))
    judul = f"{LABEL[kolom]}, {tahun} (garis putus-putus = provinsi: {nilai_prov:.2f})"
    return (batang + garis).properties(height=300, title=judul)


def grafik_scatter(df, x, y, judul_x, judul_y, tinggi=400):
    pilih = alt.selection_point(fields=["wilayah"], bind="legend")
    return (
        alt.Chart(df)
        .mark_circle(size=120, stroke="white", strokeWidth=1.2)
        .encode(
            x=alt.X(f"{x}:Q", title=judul_x, scale=alt.Scale(zero=False)),
            y=alt.Y(f"{y}:Q", title=judul_y),
            color=warna_wilayah(),
            opacity=alt.condition(pilih, alt.value(1.0), alt.value(0.12)),
            tooltip=TT,
        )
        .add_params(pilih)
        .interactive()
        .properties(height=tinggi)
    )


# ================================================================== BERANDA
if halaman == "Beranda":
    hero(
        "Pertumbuhan Ekonomi dan Pengangguran di Kabupaten/Kota Kepulauan Riau",
        "Menelusuri pola, kelompok wilayah, dan hubungan antara pengangguran dan pertumbuhan ekonomi. "
        "Arahkan kursor ke grafik untuk melihat angka, dan atur filter di panel kiri.",
        [f"{len(a.WILAYAH)} kabupaten/kota", f"{semua_tahun[0]}-{semua_tahun[-1]}", f"{len(kab)} observasi", "Sumber: BPS Kepri"],
    )

    rata = kf.groupby("wilayah")[["pertumbuhan", "tpt"]].mean()
    per_tahun = kf.groupby("tahun")["pertumbuhan"].mean()
    w_tumbuh, w_tpt = rata["pertumbuhan"].idxmax(), rata["tpt"].idxmax()
    th_buruk = per_tahun.idxmin()
    korel = kf[["pertumbuhan", "tpt"]].corr().iloc[0, 1] if len(kf) > 2 else float("nan")

    k1, k2, k3, k4 = st.columns(4)
    with k1, st.container(border=True):
        st.metric("Pertumbuhan rata-rata tertinggi", w_tumbuh, f"{rata.loc[w_tumbuh, 'pertumbuhan']:.2f}%", delta_color="off")
    with k2, st.container(border=True):
        st.metric("Pengangguran rata-rata tertinggi", w_tpt, f"{rata.loc[w_tpt, 'tpt']:.2f}%", delta_color="off")
    with k3, st.container(border=True):
        st.metric("Tahun paling terpukul", str(th_buruk), f"{per_tahun[th_buruk]:.2f}% (rata-rata)", delta_color="off")
    with k4, st.container(border=True):
        st.metric("Korelasi TPT vs pertumbuhan", f"{korel:.2f}" if korel == korel else "-", "lemah = hampir tak berhubungan", delta_color="off")

    st.subheader("Bandingkan wilayah pada satu tahun")
    daftar = sorted(kf["tahun"].unique().tolist())
    tahun_pilih = st.select_slider("Geser untuk memilih tahun", options=daftar, value=daftar[-1])
    dth = kf[kf["tahun"] == tahun_pilih]
    pv = prov[prov["tahun"] == tahun_pilih].iloc[0]
    c1, c2 = st.columns(2)
    c1.altair_chart(grafik_batang_tahun(dth, pv["pertumbuhan"], "pertumbuhan", tahun_pilih))
    c2.altair_chart(grafik_batang_tahun(dth, pv["tpt"], "tpt", tahun_pilih))

    st.subheader("Peringkat rata-rata per wilayah")
    tabel = rata.sort_values("pertumbuhan", ascending=False).round(2)
    tabel.columns = ["Rata-rata pertumbuhan (%)", "Rata-rata TPT (%)"]
    st.dataframe(
        tabel, use_container_width=True,
        column_config={
            "Rata-rata pertumbuhan (%)": st.column_config.ProgressColumn(
                "Rata-rata pertumbuhan (%)", min_value=-1.0, max_value=6.0, format="%.2f"),
            "Rata-rata TPT (%)": st.column_config.ProgressColumn(
                "Rata-rata TPT (%)", min_value=0.0, max_value=12.0, format="%.2f"),
        },
    )
    penjelasan(
        "- **Pertumbuhan ekonomi** menunjukkan seberapa cepat ekonomi suatu wilayah membesar dibanding tahun sebelumnya. "
        "Angka negatif berarti ekonomi mengecil.\n"
        "- **TPT (Tingkat Pengangguran Terbuka)** adalah persentase angkatan kerja yang tidak punya pekerjaan dan sedang mencari kerja.\n"
        "- Garis putus-putus abu-abu adalah angka **Provinsi Kepri**. Batang yang melewati garis berarti wilayah itu lebih tinggi dari rata-rata provinsi.\n"
        "- **Korelasi** mengukur apakah dua angka bergerak bersama. Nilai dekat 0 berarti hampir tidak berhubungan."
    )

# ================================================================== 1. DATA COLLECTION
elif halaman == "1. Data Collection":
    banner("Data Collection", "Dua dataset BPS yang menjadi bahan analisis.")
    st.dataframe(R["deskripsi"], use_container_width=True)
    t1, t2 = st.tabs(["Pertumbuhan ekonomi (%)", "Tingkat pengangguran terbuka (%)"])
    with t1:
        st.dataframe(R["pe"], use_container_width=True)
    with t2:
        st.dataframe(R["tpt"], use_container_width=True)
    st.caption("Baris 'Kepulauan Riau' adalah angka provinsi, dipakai sebagai pembanding.")
    penjelasan("Ini adalah dua tabel mentah dari BPS. Satu baris = satu wilayah, satu kolom = satu tahun. "
               "Datanya disebut **data sekunder** karena dikumpulkan oleh lembaga lain (BPS), bukan kita yang mengukur langsung.")

# ================================================================== 2. DATA CLEANING
elif halaman == "2. Data Cleaning":
    banner("Data Cleaning", "Memeriksa dan merapikan data sebelum dianalisis.")
    st.subheader("Pemeriksaan kualitas data")
    st.dataframe(R["kualitas"], use_container_width=True)
    st.markdown(
        "- Nama wilayah dirapikan (spasi) dan duplikat dihapus.\n"
        "- Dua tabel lebar diubah ke format panel (wilayah, tahun) lalu digabung (merge 1:1).\n"
        "- Provinsi dipisahkan sebagai pembanding; analisis memakai 7 kab/kota.\n"
        "- Ditambah variabel dummy `covid_2020` (1 untuk tahun 2020)."
    )
    st.subheader("Outlier (metode IQR)")
    if len(R["outlier"]):
        st.dataframe(R["outlier"], use_container_width=True)
        st.caption("Nilai ekstrem tidak dibuang karena merupakan data riil.")
    else:
        st.write("Tidak ada outlier.")
    st.subheader("Lihat sebaran data dan outlier")
    kolom_o = st.radio("Variabel", ["pertumbuhan", "tpt"], format_func=LABEL.get, horizontal=True)
    kotak = alt.Chart(kab).mark_boxplot(extent=1.5, size=30).encode(
        x=alt.X("wilayah:N", sort=a.WILAYAH, title=None, axis=alt.Axis(labelAngle=-30)),
        y=alt.Y(f"{kolom_o}:Q", title=LABEL[kolom_o]),
        color=warna_wilayah(legenda=False),
    ).properties(height=340)
    st.altair_chart(kotak)
    st.subheader("Data panel bersih")
    st.dataframe(kab, use_container_width=True)
    st.subheader("Statistik deskriptif")
    st.dataframe(kab[["pertumbuhan", "tpt"]].describe().round(2), use_container_width=True)
    penjelasan("**Cleaning** artinya memeriksa dan merapikan data sebelum dianalisis: ada angka kosong? ada baris ganda? "
               "Data Anda sudah rapi. **Outlier** adalah angka yang jauh berbeda dari kebanyakan data. "
               "Di kotak-garis (boxplot), titik yang berada di luar 'kumis' adalah outlier. Di sini hanya Anambas 2025 yang melonjak 15,54%.")

# ================================================================== 3. NORMALISASI
elif halaman == "3. Normalisasi":
    banner("Normalisasi data", "Menyamakan skala variabel agar adil bagi K-Means.")
    metode = st.radio(
        "Metode", ["standard", "minmax"], horizontal=True,
        format_func=lambda m: "Z-score (StandardScaler)" if m == "standard" else "Min-Max (0-1)",
    )
    Z, _ = a.normalisasi(kab, metode=metode)
    gabung = kab[["wilayah", "tahun"]].join(kab[a.FITUR_CLUSTER]).join(Z)
    st.subheader("Sebelum dan sesudah normalisasi")
    c1, c2 = st.columns(2)
    sebelum = alt.Chart(gabung).mark_circle(size=80, color="#2a78d6", opacity=0.8).encode(
        x=alt.X("tpt:Q", title="TPT (%)"), y=alt.Y("pertumbuhan:Q", title="Pertumbuhan (%)"),
        tooltip=["wilayah", "tahun", "tpt", "pertumbuhan"],
    ).properties(title="Sebelum (skala asli)", height=340).interactive()
    sesudah = alt.Chart(gabung).mark_circle(size=80, color="#eb6834", opacity=0.8).encode(
        x=alt.X("tpt_norm:Q", title="TPT (ternormalisasi)"), y=alt.Y("pertumbuhan_norm:Q", title="Pertumbuhan (ternormalisasi)"),
        tooltip=["wilayah", "tahun", alt.Tooltip("tpt_norm:Q", format=".2f"), alt.Tooltip("pertumbuhan_norm:Q", format=".2f")],
    ).properties(title="Sesudah (skala disamakan)", height=340).interactive()
    c1.altair_chart(sebelum)
    c2.altair_chart(sesudah)
    st.caption("Bentuk sebaran titik sama persis. Yang berubah hanya angka pada sumbunya.")
    st.dataframe(gabung.round(3), use_container_width=True)
    penjelasan("Pertumbuhan berkisar -8 sampai 15, sedangkan pengangguran 1 sampai 12. K-Means mengelompokkan data berdasarkan jarak, "
               "jadi variabel dengan angka lebih besar bisa mendominasi. **Normalisasi** menyamakan skala keduanya agar adil. "
               "Z-score mengubah data agar rata-ratanya 0; Min-Max memampatkan data ke rentang 0 sampai 1.")

# ================================================================== 4. EDA
elif halaman == "4. EDA":
    banner("Exploratory Data Analysis", "Mengenali pola data lewat grafik interaktif.")
    st.caption("Tips: klik nama wilayah di legenda untuk menyorot, arahkan kursor untuk melihat angka. Pada grafik titik, scroll untuk zoom dan seret untuk menggeser.")
    tab_tren, tab_heat, tab_hub, tab_dist = st.tabs(["Tren per tahun", "Peta panas", "Hubungan TPT dan pertumbuhan", "Distribusi"])

    with tab_tren:
        kolom = st.radio("Variabel", ["pertumbuhan", "tpt"], format_func=LABEL.get, horizontal=True, key="tren")
        tampil_prov = st.checkbox("Tampilkan garis Provinsi Kepri", value=True)
        st.altair_chart(grafik_tren(kf, pf, kolom, nol=(kolom == "pertumbuhan"), tampil_prov=tampil_prov))
        penjelasan("Setiap garis adalah satu wilayah. Perhatikan **tahun 2020**: hampir semua garis jatuh bersamaan karena COVID-19. "
                   "Natuna dan Anambas paling naik-turun karena ekonominya bergantung pada migas.")

    with tab_heat:
        kolom_h = st.radio("Variabel", ["pertumbuhan", "tpt"], format_func=LABEL.get, horizontal=True, key="heat")
        st.altair_chart(grafik_heat(kf, kolom_h))
        penjelasan("Peta panas menampilkan angka sebagai warna. Pada pertumbuhan: **biru = tumbuh, oranye = menyusut**. "
                   "Pada pengangguran: makin gelap makin tinggi.")

    with tab_hub:
        st.altair_chart(grafik_scatter(kf, "tpt", "pertumbuhan", LABEL["tpt"], LABEL["pertumbuhan"]))
        r = kf[["pertumbuhan", "tpt"]].corr().iloc[0, 1] if len(kf) > 2 else float("nan")
        st.metric("Korelasi Pearson (data terfilter)", f"{r:.2f}" if r == r else "-")
        st.caption("Korelasi tidak berarti sebab-akibat.")
        penjelasan("Setiap titik adalah satu wilayah pada satu tahun. Kalau titik membentuk garis miring yang jelas, berarti dua angka berhubungan. "
                   "Di sini titik menyebar, artinya **pengangguran hampir tidak menjelaskan pertumbuhan**.")

    with tab_dist:
        kolom_d = st.radio("Variabel", ["pertumbuhan", "tpt"], format_func=LABEL.get, horizontal=True, key="dist")
        c1, c2 = st.columns(2)
        hist = alt.Chart(kf).mark_bar(color="#2a78d6").encode(
            x=alt.X(f"{kolom_d}:Q", bin=alt.Bin(maxbins=15), title=LABEL[kolom_d]),
            y=alt.Y("count()", title="Jumlah data"),
            tooltip=[alt.Tooltip("count()", title="Jumlah data")],
        ).properties(title="Histogram", height=320)
        kotak = alt.Chart(kf).mark_boxplot(extent=1.5, size=26).encode(
            x=alt.X("wilayah:N", sort=a.WILAYAH, title=None, axis=alt.Axis(labelAngle=-30)),
            y=alt.Y(f"{kolom_d}:Q", title=LABEL[kolom_d]),
            color=warna_wilayah(legenda=False),
        ).properties(title="Boxplot per wilayah", height=320)
        c1.altair_chart(hist)
        c2.altair_chart(kotak)
        st.subheader("Rata-rata per wilayah")
        rr = kf.groupby("wilayah", as_index=False)[kolom_d].mean()
        st.altair_chart(
            alt.Chart(rr).mark_bar(cornerRadiusEnd=4).encode(
                x=alt.X(f"{kolom_d}:Q", title=f"Rata-rata {LABEL[kolom_d]}"),
                y=alt.Y("wilayah:N", sort="-x", title=None),
                color=warna_wilayah(legenda=False),
                tooltip=[alt.Tooltip("wilayah:N"), alt.Tooltip(f"{kolom_d}:Q", format=".2f", title="Rata-rata")],
            ).properties(height=300)
        )

# ================================================================== 5. K-MEANS
elif halaman == "5. K-Means Clustering":
    banner("K-Means Clustering", "Mengelompokkan wilayah dan tahun yang karakternya mirip.")
    st.write("Fitur: pertumbuhan ekonomi dan TPT (sudah dinormalisasi Z-score). Geser jumlah cluster dan lihat perubahannya langsung.")
    ev = R["evaluasi_k"]
    c1, c2 = st.columns(2)
    c1.altair_chart(
        alt.Chart(ev).mark_line(point=True, color="#2a78d6").encode(
            x=alt.X("k:O", title="Jumlah cluster (k)", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("inertia:Q", title="Inertia (makin kecil makin rapat)"),
            tooltip=["k", alt.Tooltip("inertia:Q", format=".2f")],
        ).properties(title="Elbow Method", height=260)
    )
    c2.altair_chart(
        alt.Chart(ev).mark_line(point=True, color="#eb6834").encode(
            x=alt.X("k:O", title="Jumlah cluster (k)", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("silhouette:Q", title="Silhouette (makin tinggi makin baik)", scale=alt.Scale(zero=False)),
            tooltip=["k", alt.Tooltip("silhouette:Q", format=".3f")],
        ).properties(title=f"Silhouette Score (terbaik: k = {R['k_terbaik']})", height=260)
    )
    k = st.slider("Jumlah cluster (k)", min_value=2, max_value=6, value=R["k_terbaik"])
    st.caption(f"Nilai k terbaik menurut Silhouette Score: {R['k_terbaik']}")
    hasil, pusat, _, _ = a.jalankan_kmeans(kab, k)
    hasil["cluster_txt"] = "Cluster " + hasil["cluster"].astype(str)
    pusat_df = pusat.reset_index()
    pusat_df["cluster_txt"] = "Cluster " + pusat_df["cluster"].astype(str)
    domain = [f"Cluster {i}" for i in range(k)]
    skala_c = alt.Scale(domain=domain, range=PAL_CLUSTER[:k])
    warna_c = alt.Color("cluster_txt:N", scale=skala_c, legend=alt.Legend(title="Cluster (klik untuk menyorot)"))

    pilih_c = alt.selection_point(fields=["cluster_txt"], bind="legend")
    tt_c = TT + [alt.Tooltip("cluster_txt:N", title="Cluster")]
    titik = alt.Chart(hasil).mark_circle(size=130, stroke="white", strokeWidth=1.2).encode(
        x=alt.X("tpt:Q", title=LABEL["tpt"], scale=alt.Scale(zero=False)),
        y=alt.Y("pertumbuhan:Q", title=LABEL["pertumbuhan"]),
        color=warna_c, opacity=alt.condition(pilih_c, alt.value(1.0), alt.value(0.12)), tooltip=tt_c,
    )
    pusat_g = alt.Chart(pusat_df).mark_point(shape="cross", size=500, strokeWidth=4, filled=False).encode(
        x=alt.X("tpt:Q", title=LABEL["tpt"], scale=alt.Scale(zero=False)),
        y=alt.Y("pertumbuhan:Q", title=LABEL["pertumbuhan"]), color=warna_c,
        tooltip=[alt.Tooltip("cluster_txt:N", title="Centroid"),
                 alt.Tooltip("pertumbuhan:Q", title="Pertumbuhan rata-rata (%)", format=".2f"),
                 alt.Tooltip("tpt:Q", title="TPT rata-rata (%)", format=".2f"),
                 alt.Tooltip("jumlah_data:Q", title="Jumlah data")],
    )
    st.subheader("Peta cluster (tanda + adalah pusat/centroid)")
    st.altair_chart((titik + pusat_g).add_params(pilih_c).interactive().properties(height=420))

    st.subheader("Centroid (satuan asli)")
    st.dataframe(pusat, use_container_width=True)

    st.subheader("Cluster tiap wilayah di setiap tahun")
    dasar = alt.Chart(hasil).encode(
        x=alt.X("tahun:O", title="Tahun", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("wilayah:N", sort=a.WILAYAH, title=None),
    )
    waktu = dasar.mark_rect(stroke="white", strokeWidth=2).encode(
        color=alt.Color("cluster_txt:N", scale=skala_c, legend=None), tooltip=tt_c)
    angka = dasar.mark_text(color="white", fontWeight="bold").encode(text="cluster:N")
    st.altair_chart((waktu + angka).properties(height=300))

    st.subheader("Jumlah tahun tiap wilayah di setiap cluster")
    hitung = hasil.groupby(["wilayah", "cluster_txt"]).size().reset_index(name="jumlah_tahun")
    st.altair_chart(
        alt.Chart(hitung).mark_bar().encode(
            x=alt.X("jumlah_tahun:Q", title="Jumlah tahun"),
            y=alt.Y("wilayah:N", sort=a.WILAYAH, title=None),
            color=alt.Color("cluster_txt:N", scale=skala_c, title="Cluster"),
            tooltip=["wilayah", "cluster_txt", "jumlah_tahun"],
        ).properties(height=300)
    )
    with st.expander("Lihat tabel lengkap"):
        st.dataframe(hasil[["wilayah", "tahun", "pertumbuhan", "tpt", "cluster"]], use_container_width=True)
    penjelasan("**K-Means** mengelompokkan data yang mirip tanpa diberi contoh jawaban. Komputer mencari pusat tiap kelompok (centroid), "
               "lalu setiap titik masuk ke pusat terdekat.\n\n"
               "- **Elbow**: pilih k di titik grafik mulai melandai.\n"
               "- **Silhouette**: skor kerapihan kelompok; k dengan skor tertinggi dipilih.\n"
               "- Pada **peta waktu**, terlihat tahun 2020-2021 sering masuk cluster krisis, sedangkan Natuna, Lingga, dan Anambas hampir selalu berada di cluster yang sama.")

# ================================================================== 6. REGRESI
elif halaman == "6. Linear Regression & Prediksi":
    banner("Linear Regression", "Menebak pertumbuhan ekonomi dari data lain.")
    st.write("Target: pertumbuhan ekonomi (%). Pembagian data: 80% latih, 20% uji (random_state=42), plus validasi silang 5-fold.")
    st.dataframe(a.ringkas_regresi(R["reg"]), use_container_width=True)
    for nama, h in R["reg"].items():
        st.markdown(f"**{nama}**: intercept = {h['intercept']:.3f}; " + "; ".join(f"koef {k} = {v:.3f}" for k, v in h["koef"].items()))
    st.warning("Model A (hanya TPT) praktis tidak mampu menjelaskan pertumbuhan (R² mendekati 0). "
               "Model B membaik karena memperhitungkan guncangan COVID-2020, bukan karena TPT.")

    st.subheader("Coba prediksi sendiri")
    nama_model = st.radio("Pilih model", list(R["reg"].keys()), horizontal=True)
    pakai_covid = nama_model.startswith("Model B")
    model = R["reg"][nama_model]["model"]
    kiri, kanan = st.columns([1, 2])
    with kiri:
        tpt_in = st.slider("Tingkat pengangguran terbuka (%)", min_value=0.0, max_value=15.0, value=5.0, step=0.1)
        covid = st.checkbox("Tahun krisis COVID-19 (2020)", disabled=not pakai_covid)
        X_in = pd.DataFrame({"tpt": [tpt_in]})
        if pakai_covid:
            X_in["covid_2020"] = int(covid)
        pred = float(model.predict(X_in)[0])
        st.metric("Prediksi pertumbuhan ekonomi", f"{pred:.2f}%",
                  f"{pred - kab['pertumbuhan'].mean():+.2f} poin dari rata-rata data ({kab['pertumbuhan'].mean():.2f}%)",
                  delta_color="off")
        h = R["reg"][nama_model]
        rumus = f"{h['intercept']:.3f}" + "".join(
            f" {'+' if h['koef'][f] >= 0 else '-'} {abs(h['koef'][f]):.3f} × {nilai}"
            for f, nilai in zip(h["fitur"], [tpt_in, int(covid)])
        ) + f" = **{pred:.2f}**"
        st.markdown("Perhitungan: " + rumus)
    with kanan:
        grid = np.linspace(0, 15, 60)
        data_titik = kab.copy()
        data_titik["Periode"] = np.where(data_titik["covid_2020"] == 1, "2020 (COVID)", "Tahun lain")
        skala_p = alt.Scale(domain=["Tahun lain", "2020 (COVID)"], range=["#2a78d6", "#eb6834"])
        sumbu_x = alt.X("tpt:Q", title=LABEL["tpt"], scale=alt.Scale(domain=[0, 15]))
        titik = alt.Chart(data_titik).mark_circle(size=70, opacity=0.75).encode(
            x=sumbu_x,
            y=alt.Y("pertumbuhan:Q", title=LABEL["pertumbuhan"]),
            color=alt.Color("Periode:N", scale=skala_p, title="Periode"), tooltip=TT,
        )
        if pakai_covid:
            gdf = pd.concat([
                pd.DataFrame({"tpt": grid, "covid_2020": f, "Periode": p,
                              "prediksi": model.predict(pd.DataFrame({"tpt": grid, "covid_2020": f}))})
                for f, p in [(0, "Tahun lain"), (1, "2020 (COVID)")]
            ])
            garis = alt.Chart(gdf).mark_line(strokeWidth=3).encode(
                x=sumbu_x, y=alt.Y("prediksi:Q", title=LABEL["pertumbuhan"]), color=alt.Color("Periode:N", scale=skala_p))
        else:
            gdf = pd.DataFrame({"tpt": grid, "prediksi": model.predict(pd.DataFrame({"tpt": grid}))})
            garis = alt.Chart(gdf).mark_line(strokeWidth=3, color=ABU, strokeDash=[6, 4]).encode(
                x=sumbu_x, y=alt.Y("prediksi:Q", title=LABEL["pertumbuhan"]))
        tanda = alt.Chart(pd.DataFrame({"tpt": [tpt_in], "prediksi": [pred], "ket": ["Prediksi Anda"]})).mark_point(
            shape="diamond", size=380, filled=True, color="#e34948", stroke="white", strokeWidth=2
        ).encode(x=sumbu_x, y=alt.Y("prediksi:Q", title=LABEL["pertumbuhan"]),
                 tooltip=[alt.Tooltip("ket:N", title=""), alt.Tooltip("prediksi:Q", format=".2f", title="Prediksi (%)")])
        st.altair_chart((titik + garis + tanda).properties(height=380))
        st.caption("Titik = data asli. Garis = hasil model. Berlian merah = prediksi sesuai pengaturan Anda.")

    st.subheader("Uji pada data nyata")
    mb = R["reg"]["Model B: TPT + dummy COVID-2020"]["model"]
    u1, u2 = st.columns(2)
    w_uji = u1.selectbox("Wilayah", a.WILAYAH)
    t_uji = u2.selectbox("Tahun", semua_tahun, index=len(semua_tahun) - 1)
    baris = kab[(kab["wilayah"] == w_uji) & (kab["tahun"] == t_uji)].iloc[0]
    pr = float(mb.predict(pd.DataFrame({"tpt": [baris["tpt"]], "covid_2020": [int(baris["covid_2020"])]}))[0])
    m1, m2, m3 = st.columns(3)
    m1.metric("Pertumbuhan aktual", f"{baris['pertumbuhan']:.2f}%")
    m2.metric("Prediksi Model B", f"{pr:.2f}%")
    m3.metric("Selisih (prediksi - aktual)", f"{pr - baris['pertumbuhan']:+.2f} poin", delta_color="off")
    st.caption("Coba Natuna atau Kepulauan Anambas tahun 2025: selisihnya sangat besar karena lonjakan sektor migas tidak tertangkap oleh model.")

    penjelasan("**Regresi linear** mencari rumus sederhana (sebuah garis lurus) untuk menebak satu angka dari angka lain.\n\n"
               "- **Intercept** adalah titik awal rumus. **Koefisien** menunjukkan seberapa besar pengaruh tiap variabel.\n"
               "- **R²** mengukur seberapa baik rumus menjelaskan data: 1 = sempurna, 0 = tidak lebih baik dari menebak rata-rata.\n"
               "- **MAE/RMSE** adalah rata-rata kesalahan tebakan (makin kecil makin baik).\n"
               "- Hasilnya lemah karena pengangguran saja memang tidak cukup untuk menjelaskan pertumbuhan, dan itulah temuan penelitian ini.")

# ================================================================== 7. KESIMPULAN
else:
    banner("Kesimpulan", "Ringkasan temuan dan keterbatasan penelitian.")
    r = R["korelasi"].iloc[0, 0]
    st.markdown(
        f"""
- **Wilayah berbeda:** Batam, Bintan, Karimun, dan Tanjungpinang umumnya berada pada cluster pertumbuhan tinggi;
  Natuna, Lingga, dan Kepulauan Anambas berada pada cluster TPT rendah dengan pertumbuhan mendekati nol.
- **Tahun 2020 (COVID-19)** menurunkan pertumbuhan hampir semua wilayah dan menaikkan TPT, terutama Batam dan Bintan.
- **Hubungan TPT dan pertumbuhan:** korelasi Pearson hanya {r:.2f}; TPT saja tidak dapat memprediksi pertumbuhan.
- **Keterbatasan:** hanya 2 variabel, 49 observasi, serta lonjakan Natuna dan Anambas (sektor migas) yang tidak
  dijelaskan oleh TPT. Korelasi tidak sama dengan sebab-akibat.
- **Saran:** penelitian lanjutan sebaiknya menambah variabel seperti PDRB sektoral, investasi, kemiskinan, atau IPM.
"""
    )
