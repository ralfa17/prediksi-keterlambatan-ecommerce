import streamlit as st
import pandas as pd
import joblib

model = joblib.load("hasil/model_telat.pkl")
kolom_model = joblib.load("hasil/kolom_model.pkl")
daftar_provinsi = joblib.load("hasil/daftar_provinsi.pkl")
daftar_payment = joblib.load("hasil/daftar_payment.pkl")

st.title("🚚 Prediksi Keterlambatan Pengiriman")
st.write("Masukkan detail pesanan untuk memprediksi risiko keterlambatan.")

payment_value = st.number_input("Nilai Pembayaran (R$)", min_value=0.0, value=100.0)
payment_installments = st.number_input("Jumlah Cicilan", min_value=1, value=1)
estimasi_hari = st.number_input("Estimasi Hari Pengiriman", min_value=1, value=15)
hari_dalam_minggu_beli = st.selectbox("Hari Pembelian",
    options=[0,1,2,3,4,5,6],
    format_func=lambda x: ["Senin","Selasa","Rabu","Kamis","Jumat","Sabtu","Minggu"][x])
bulan_beli = st.selectbox("Bulan Pembelian", options=list(range(1,13)))
payment_type = st.selectbox("Metode Pembayaran", options=daftar_payment)
customer_state = st.selectbox("Provinsi Pelanggan", options=daftar_provinsi)

if st.button("Prediksi"):

    data_baru = pd.DataFrame([[0]*len(kolom_model)], columns=kolom_model)

    data_baru["payment_value"] = payment_value
    data_baru["payment_installments"] = payment_installments
    data_baru["estimasi_hari"] = estimasi_hari
    data_baru["hari_dalam_minggu_beli"] = hari_dalam_minggu_beli
    data_baru["bulan_beli"] = bulan_beli

    kolom_payment = f"payment_type_{payment_type}"
    kolom_state = f"customer_state_{customer_state}"
    if kolom_payment in data_baru.columns:
        data_baru[kolom_payment] = 1
    if kolom_state in data_baru.columns:
        data_baru[kolom_state] = 1

    proba = model.predict_proba(data_baru)[0, 1]
    prediksi = "BERISIKO TELAT" if proba >= 0.4 else "AMAN (Tepat Waktu)"

    if proba >= 0.4:
        st.error(f"⚠️ {prediksi} — Keyakinan: {proba:.1%}")
    else:
        st.succes(f"✅ {prediksi} — Keyakinan tidak telat: {1-proba:.1%}")