# Prediksi Keterlambatan Pengiriman E-Commerce

Proyek ini dibuat untuk kompetisi Data Mining ICONFEST 2026, memprediksi
risiko keterlambatan pengiriman pesanan e-commerce menggunakan machine
learning.

## Struktur Proyek
- `analisis_keterlambatan.ipynb` — notebook analisis lengkap (EDA, cleaning,
  feature engineering, modeling, evaluasi, insight bisnis)
- `app.py` — prototype aplikasi prediksi (Streamlit)
- `hasil/` — visualisasi, model terlatih, dan file submission
- `data/` — dataset (tidak disertakan di repository karena ukuran besar)

## Cara Menjalankan Prototype
pip install -r requirements.txt
python -m streamlit run app.py

## Hasil Utama
- Model Random Forest dengan ROC-AUC 0,767
- Recall 76% untuk mendeteksi pesanan berisiko telat
- Insight: pengaruh Karnaval Brasil, efek penumpukan hari Senin, pola
  geografis Timur Laut vs Tenggara Brasil

## Tim
[TimTam] — ICONFEST 2026 Data Mining Competition