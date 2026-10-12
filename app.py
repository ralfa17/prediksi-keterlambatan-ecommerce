import os
import joblib
import pandas as pd
import streamlit as st

BASE = os.path.dirname(os.path.abspath(__file__))
THRESHOLD = 0.4
HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

st.set_page_config(page_title="Prediksi Keterlambatan Pengiriman", page_icon="🚚")

@st.cache_resource
def muat_aset():
    hasil = os.path.join(BASE, "hasil")
    model = joblib.load(os.path.join(hasil, "model_telat.pkl"))
    kolom = joblib.load(os.path.join(hasil, "kolom_model.pkl"))
    provinsi = joblib.load(os.path.join(hasil, "daftar_provinsi.pkl"))
    payment = joblib.load(os.path.join(hasil, "daftar_payment.pkl"))
    return model, kolom, provinsi, payment

model, kolom_model, daftar_provinsi, daftar_payment, = muat_aset()

st.title("🚚 Prediksi Keterlambatan Pengiriman")
st.write("Masukkan detail pesanan untuk memperkirakan risiko keterlambatan sejak pesanan dibuat.")

tab_prediksi, tab_insight, = st.tabs(["Prediksi", "Insight Data"])

with tab_prediksi:
    payment_value = st.number_input("Nilai Pembayaran (R$)", min_value=0.0, value=100.0)
    payment_installments = st.number_input("Jumlah Cicilan", min_value=1, value=1)
    estimasi_hari = st.number_input(
        "Estimasi Hari Pengiriman", min_value=1, value=15,
        help="Lama pengiriman yang dijanjikan kepada pelanggan saat checkout.",
    )
    hari_beli = st.selectbox("Hari Pembelian", options=list(range(7)), format_func=lambda x: HARI[x])
    bulan_beli = st.selectbox("Bulan Pembelian", options=list(range(1,13)))
    payment_type = st.selectbox("Metode Pembayaran", options=daftar_payment)
    customer_state = st.selectbox("Provinsi Pelanggan", options=daftar_provinsi)

if st.button("Prediksi"):

    data_baru = pd.DataFrame([[0.0] * len(kolom_model)], columns=kolom_model)

    data_baru["payment_value"] = payment_value
    data_baru["payment_installments"] = payment_installments
    data_baru["estimasi_hari"] = estimasi_hari
    data_baru["hari_dalam_minggu_beli"] = hari_beli
    data_baru["bulan_beli"] = bulan_beli

    for kolom in (f"payment_type_{payment_type}", f"cutomer_state_{customer_state}"):
        if kolom in data_baru.columns:
            data_baru[kolom] = 1.0 

    skor = float(model.predict_proba(data_baru)[0, 1])
    st.progress(min(max(skor, 0.0), 1.0))

    if skor >= THRESHOLD:
        st.error(f"⚠️ BERISIKO TELAT — Skor risiko: {skor:.1%}")
    else:
        st.success(f"✅ AMAN (Tepat Waktu) — Skor risiko: {skor:.1%}")

    st.caption(
        "Skor risiko bukan peluang sebenarnya. Rata-rata pesanan yang terlambat pada data "
        f"hanya 8,1%. Pesanan ditandai berisiko jika skor mencapai {THRESHOLD:.0%}, "
        "ambang yang dipilih agar sekitar 76% pesanan terlambat terdeteksi."
    )

with tab_insight:
    st.subheader("Pola keterlambatan pada data")
    st.write("Tiga pola utama yang ditemukan dari 96.469 pesanan terkirim.")

    st.markdown("**1. Bulan pembelian.** Februari dan Maret paling tinggi, diduga berkaitan dengan Karnaval Brasil.")
    st.image(os.path.join(BASE, "hasil", "grafik_bulan.png"))

    st.markdown("**2. Hari pembelian.** Senin tertinggi, diduga karena pesanan akhir pekan menumpuk.")
    st.image(os.path.join(BASE, "hasil", "grafik_hari.png"))

    st.markdown("**3. Provinsi.** Wilayah Timur Laut Brasil (AL, MA, PI, CE, SE) paling berisiko.")
    st.image(os.path.join(BASE, "hasil", "grafik_provinsi.png"))