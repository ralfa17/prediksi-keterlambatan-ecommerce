import os
import joblib
import pandas as pd
import streamlit as st

# ==============================================================================
# KONFIGURASI HALAMAN & TEMA STREAMLIT
# ==============================================================================
st.set_page_config(
    page_title="LateRisk AI | Prediksi Keterlambatan Pengiriman",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE = os.path.dirname(os.path.abspath(__file__))
THRESHOLD = 0.4
BASELINE_RATE = 0.0811  # Rata-rata 8,11% pesanan terlambat pada dataset historis

HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

PROVINSI_MAP = {
    "AC": "AC — Acre (Utara)",
    "AL": "AL — Alagoas (Timur Laut ⚠️ Wilayah Rawan)",
    "AM": "AM — Amazonas (Utara)",
    "AP": "AP — Amapá (Utara)",
    "BA": "BA — Bahia (Timur Laut)",
    "CE": "CE — Ceará (Timur Laut ⚠️ Wilayah Rawan)",
    "DF": "DF — Distrito Federal (Brasília)",
    "ES": "ES — Espírito Santo (Tenggara)",
    "GO": "GO — Goiás (Barat Tengah)",
    "MA": "MA — Maranhão (Timur Laut ⚠️ Wilayah Rawan)",
    "MG": "MG — Minas Gerais (Tenggara)",
    "MS": "MS — Mato Grosso do Sul (Barat Tengah)",
    "MT": "MT — Mato Grosso (Barat Tengah)",
    "PA": "PA — Pará (Utara)",
    "PB": "PB — Paraíba (Timur Laut)",
    "PE": "PE — Pernambuco (Timur Laut)",
    "PI": "PI — Piauí (Timur Laut ⚠️ Wilayah Rawan)",
    "PR": "PR — Paraná (Selatan)",
    "RJ": "RJ — Rio de Janeiro (Tenggara)",
    "RN": "RN — Rio Grande do Norte (Timur Laut)",
    "RO": "RO — Rondônia (Utara)",
    "RR": "RR — Roraima (Utara)",
    "RS": "RS — Rio Grande do Sul (Selatan)",
    "SC": "SC — Santa Catarina (Selatan)",
    "SE": "SE — Sergipe (Timur Laut ⚠️ Wilayah Rawan)",
    "SP": "SP — São Paulo (Tenggara ✅ Hub Tercepat)",
    "TO": "TO — Tocantins (Utara)",
}

PAYMENT_MAP = {
    "credit_card": "💳 Kartu Kredit (Credit Card)",
    "boleto": "📄 Boleto Bancário (Virtual Account / Faktur)",
    "debit_card": "💳 Kartu Debit (Debit Card)",
    "voucher": "🎟️ Voucher / Kupon Diskon",
}

BULAN_MAP = {
    1: "Januari",
    2: "Februari (⚠️ Musim Karnaval Brasil)",
    3: "Maret (⚠️ Efek Penumpukan Pasca-Karnaval)",
    4: "April",
    5: "Mei",
    6: "Juni",
    7: "Juli",
    8: "Agustus",
    9: "September",
    10: "Oktober",
    11: "November (Puncak Black Friday)",
    12: "Desember (Libur Akhir Tahun)",
}

HARI_MAP = {
    0: "Senin (⚠️ Lonjakan Backlog Akhir Pekan)",
    1: "Selasa",
    2: "Rabu",
    3: "Kamis",
    4: "Jumat",
    5: "Sabtu (Akhir Pekan)",
    6: "Minggu (Akhir Pekan)",
}

# ==============================================================================
# CUSTOM CSS STYLING (Aesthetic, Adaptable & Responsive)
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Hero Banner Header */
    .hero-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 55%, #1e3a8a 100%);
        padding: 30px 36px;
        border-radius: 20px;
        color: #ffffff;
        margin-bottom: 24px;
        box-shadow: 0 12px 30px -5px rgba(15, 23, 42, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.12);
    }
    
    .badge-pill {
        display: inline-block;
        padding: 4px 14px;
        background: rgba(59, 130, 246, 0.25);
        border: 1px solid rgba(96, 165, 250, 0.45);
        border-radius: 9999px;
        color: #bfdbfe;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 10px;
    }

    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0;
        color: #ffffff;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .hero-subtitle {
        font-size: 0.98rem;
        color: #cbd5e1;
        margin-top: 8px;
        line-height: 1.6;
    }

    /* Metric Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(148, 163, 184, 0.22);
        border-radius: 14px;
        padding: 16px 20px;
        margin-bottom: 12px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: #3b82f6;
    }
    .metric-card .title {
        font-size: 0.78rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .metric-card .value {
        font-size: 1.75rem;
        font-weight: 800;
        margin: 4px 0;
    }
    .metric-card .subtitle {
        font-size: 0.78rem;
        color: #64748b;
    }

    /* Card Box */
    .custom-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 18px;
    }

    /* Result Alert Box */
    .result-alert {
        border-radius: 16px;
        padding: 22px 26px;
        margin: 18px 0;
        border: 1.5px solid;
        animation: fadeIn 0.35s ease;
    }
    .result-danger {
        background: rgba(239, 68, 68, 0.12);
        border-color: #ef4444;
        color: #dc2626;
    }
    .result-safe {
        background: rgba(16, 185, 129, 0.12);
        border-color: #10b981;
        color: #16a34a;
    }
    .result-title {
        font-size: 1.45rem;
        font-weight: 800;
        margin: 0 0 6px 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .result-desc {
        font-size: 0.95rem;
        margin: 0;
        line-height: 1.5;
        color: inherit;
    }

    /* Insight Bullet Item */
    .insight-item {
        background: rgba(148, 163, 184, 0.08);
        border-left: 4px solid #3b82f6;
        padding: 12px 16px;
        border-radius: 0 10px 10px 0;
        margin-bottom: 10px;
        font-size: 0.88rem;
        line-height: 1.5;
    }

    /* Action SOP Box */
    .sop-box {
        background: rgba(148, 163, 184, 0.08);
        border-radius: 12px;
        padding: 16px 20px;
        border: 1px solid rgba(148, 163, 184, 0.2);
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        margin-bottom: 16px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 22px;
        font-weight: 600;
        border-radius: 10px;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(6px); }
        to { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# MEMUAT MODEL DAN DATA PENDUKUNG (CACHED)
# ==============================================================================
@st.cache_resource
def muat_aset():
    hasil = os.path.join(BASE, "hasil")
    model = joblib.load(os.path.join(hasil, "model_telat.pkl"))
    kolom = joblib.load(os.path.join(hasil, "kolom_model.pkl"))
    provinsi = joblib.load(os.path.join(hasil, "daftar_provinsi.pkl"))
    payment = joblib.load(os.path.join(hasil, "daftar_payment.pkl"))
    return model, kolom, provinsi, payment

try:
    model, kolom_model, daftar_provinsi, daftar_payment = muat_aset()
except Exception as e:
    st.error(f"❌ Gagal memuat model dari direktori 'hasil/'. Pastikan file .pkl tersedia. Error: {e}")
    st.stop()

# ==============================================================================
# STATE MANAGEMENT & PRESETS SIMULASI
# ==============================================================================
default_payment = "credit_card" if "credit_card" in daftar_payment else daftar_payment[0]
default_state = "SP" if "SP" in daftar_provinsi else daftar_provinsi[0]

if "pv" not in st.session_state:
    st.session_state.pv = 145.0
if "pi" not in st.session_state:
    st.session_state.pi = 1
if "eh" not in st.session_state:
    st.session_state.eh = 15
if "hb" not in st.session_state:
    st.session_state.hb = 0  # Senin
if "bb" not in st.session_state:
    st.session_state.bb = 2  # Februari
if "pt" not in st.session_state:
    st.session_state.pt = default_payment
if "cs" not in st.session_state:
    st.session_state.cs = "AL" if "AL" in daftar_provinsi else default_state

def hitung_prediksi(pv_val, pi_val, eh_val, hb_val, bb_val, pt_val, cs_val):
    data_baru = pd.DataFrame([[0.0] * len(kolom_model)], columns=kolom_model)
    data_baru["payment_value"] = float(pv_val)
    data_baru["payment_installments"] = int(pi_val)
    data_baru["estimasi_hari"] = int(eh_val)
    data_baru["hari_dalam_minggu_beli"] = int(hb_val)
    data_baru["bulan_beli"] = int(bb_val)

    # Perbaikan typo asli: customer_state_ (sebelumnya: cutomer_state_)
    for kolom in (f"payment_type_{pt_val}", f"customer_state_{cs_val}"):
        if kolom in data_baru.columns:
            data_baru[kolom] = 1.0

    skor = float(model.predict_proba(data_baru)[0, 1])
    return {
        "skor": skor,
        "pv": pv_val,
        "pi": pi_val,
        "eh": eh_val,
        "hb": hb_val,
        "bb": bb_val,
        "pt": pt_val,
        "cs": cs_val
    }

def apply_preset(pv, pi, eh, hb, bb, pt, cs):
    st.session_state.pv = float(pv)
    st.session_state.pi = int(pi)
    st.session_state.eh = int(eh)
    st.session_state.hb = int(hb)
    st.session_state.bb = int(bb)
    st.session_state.pt = pt if pt in daftar_payment else default_payment
    st.session_state.cs = cs if cs in daftar_provinsi else default_state
    # Otomatis langsung kalkulasi hasil agar demo interaktif
    st.session_state.hasil_prediksi = hitung_prediksi(
        st.session_state.pv,
        st.session_state.pi,
        st.session_state.eh,
        st.session_state.hb,
        st.session_state.bb,
        st.session_state.pt,
        st.session_state.cs
    )

# ==============================================================================
# SIDEBAR: KONTROL SIMULASI & INFO LOMBA
# ==============================================================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 10px 0 14px 0;">
        <span style="font-size: 40px;">🚚</span>
        <h3 style="margin: 4px 0 2px 0; font-weight: 800;">LateRisk AI</h3>
        <p style="font-size: 0.8rem; opacity: 0.7; margin: 0;">Sistem Deteksi Dini Risiko Logistik</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("⚡ Simulasi 1-Klik (Presets)")
    st.caption("Pilih skenario siap-uji untuk melihat respon model secara langsung:")

    if st.button("🚨 Skenario Risiko Tinggi", use_container_width=True, help="Timur Laut (Alagoas), Bulan Karnaval (Feb), Order Hari Senin"):
        apply_preset(320.0, 6, 25, 0, 2, "boleto", "AL")
        st.rerun()

    if st.button("🛡️ Skenario Aman / Tepat Waktu", use_container_width=True, help="São Paulo, Nilai Standar, Estimasi Cepat"):
        apply_preset(75.0, 1, 9, 3, 6, "credit_card", "SP")
        st.rerun()

    if st.button("🔄 Reset ke Standar", use_container_width=True):
        apply_preset(145.0, 1, 15, 2, 8, "credit_card", "RJ")
        st.rerun()

    st.markdown("---")
    st.subheader("⚙️ Spesifikasi Model")
    with st.expander("ℹ️ Parameter & Metrik ML", expanded=True):
        st.markdown(f"""
        - **Model:** `Random Forest Classifier` (300 Trees)
        - **Decision Threshold:** `{THRESHOLD:.0%}` *(Recall-Tuned)*
        - **Recall (Deteksi Telat):** `76.0%`
        - **ROC-AUC:** `0.767`
        - **Dataset:** 96.469 Transaksi Olist Brasil
        """)

    st.markdown("---")
    st.markdown("""
    <div style="font-size: 0.78rem; opacity: 0.75; text-align: center; line-height: 1.4;">
        <b>ICONFEST 2026 Data Mining Competition</b><br>
        Developed by <b>TimTam</b> 🏆
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# MAIN PAGE: HERO BANNER
# ==============================================================================
st.markdown("""
<div class="hero-banner">
    <div class="badge-pill">Early Warning System (t₀)</div>
    <div class="hero-title">
        <span>🚚 Prediksi Keterlambatan Pengiriman E-Commerce</span>
    </div>
    <div class="hero-subtitle">
        Memperkirakan risiko keterlambatan pesanan sejak detik pertama transaksi dibuat (t₀), 
        sebelum barang diproses oleh kurir atau gudang untuk mencegah penalti SLA dan menjaga kepuasan pelanggan.
    </div>
</div>
""", unsafe_allow_html=True)

# Navigasi Tab
tab_prediksi, tab_insight, tab_metodologi = st.tabs([
    "🎯 Simulator Prediksi Pesanan",
    "📈 Business & Data Insights",
    "🧠 Metodologi & Arsitektur ML"
])

# ==============================================================================
# TAB 1: SIMULATOR PREDIKSI
# ==============================================================================
with tab_prediksi:
    st.markdown("##### 📝 Masukkan Detail Transaksi Pesanan")
    st.caption("Semua variabel diambil pada saat checkout (mencegah *data leakage* sebelum barang dikirim).")

    col_input1, col_input2 = st.columns(2, gap="large")

    with col_input1:
        st.markdown("###### 💳 Finansial & Pembayaran")
        
        payment_value = st.number_input(
            "Nilai Pembayaran (R$ - Brazilian Real)",
            min_value=0.0,
            max_value=15000.0,
            step=10.0,
            key="pv",
            help="Total nilai transaksi yang dibayarkan pembeli dalam mata uang Real Brasil (R$)."
        )

        payment_installments = st.slider(
            "Jumlah Cicilan Pembayaran",
            min_value=1,
            max_value=24,
            key="pi",
            help="Banyaknya kali angsuran yang dipilih oleh pembeli."
        )

        payment_type = st.selectbox(
            "Metode Pembayaran",
            options=daftar_payment,
            format_func=lambda x: PAYMENT_MAP.get(x, x),
            key="pt",
            help="Metode pembayaran yang digunakan pada transaksi."
        )

    with col_input2:
        st.markdown("###### 📍 Logistik & Jadwal Pengiriman")

        customer_state = st.selectbox(
            "Provinsi Tujuan Pelanggan (Customer State)",
            options=daftar_provinsi,
            format_func=lambda x: PROVINSI_MAP.get(x, x),
            key="cs",
            help="Provinsi alamat tujuan paket di Brasil."
        )

        estimasi_hari = st.slider(
            "Estimasi Hari Pengiriman (Dijanjikan saat Checkout)",
            min_value=1,
            max_value=60,
            key="eh",
            help="Jumlah hari estimasi pengiriman yang dijanjikan kepada pembeli saat checkout."
        )

        col_waktu1, col_waktu2 = st.columns(2)
        with col_waktu1:
            bulan_beli = st.selectbox(
                "Bulan Pembelian",
                options=list(range(1, 13)),
                format_func=lambda x: BULAN_MAP.get(x, str(x)),
                key="bb"
            )
        with col_waktu2:
            hari_beli = st.selectbox(
                "Hari Pembelian",
                options=list(range(7)),
                format_func=lambda x: HARI_MAP.get(x, HARI[x]),
                key="hb"
            )

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    tombol_prediksi = st.button("🔍 Hitung Risiko Keterlambatan", type="primary", use_container_width=True)

    if tombol_prediksi:
        st.session_state.hasil_prediksi = hitung_prediksi(
            payment_value,
            payment_installments,
            estimasi_hari,
            hari_beli,
            bulan_beli,
            payment_type,
            customer_state
        )

    # Tampilkan Hasil Jika Sudah Dihitung
    if "hasil_prediksi" in st.session_state:
        hasil = st.session_state.hasil_prediksi
        skor = hasil["skor"]
        is_telat = skor >= THRESHOLD

        st.markdown("---")
        
        # 1. Banner Keputusan
        if is_telat:
            st.markdown(f"""
            <div class="result-alert result-danger">
                <div class="result-title">
                    <span>🚨</span> STATUS: BERISIKO TINGGI TERLAMBAT ({skor:.1%})
                </div>
                <div class="result-desc">
                    Probabilitas keterlambatan melampaui ambang batas keputusan (<b>{THRESHOLD:.0%}</b>). 
                    Disarankan segera memprioritaskan packing & menggunakan opsi ekspedisi prioritas.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="result-alert result-safe">
                <div class="result-title">
                    <span>✅</span> STATUS: AMAN / POTENSI TEPAT WAKTU ({skor:.1%})
                </div>
                <div class="result-desc">
                    Skor risiko pesanan berada di bawah batas ambang kritis (<b>{THRESHOLD:.0%}</b>). 
                    Pesanan aman untuk diproses melalui jalur operasional reguler standar.
                </div>
            </div>
            """, unsafe_allow_html=True)

        # 2. Metrik Cards
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.metric(
                label="Skor Risiko Model",
                value=f"{skor:.1%}",
                delta=f"{(skor - THRESHOLD):.1%} vs Batas Peringatan",
                delta_color="inverse"
            )
        with col_m2:
            st.metric(
                label="Ambang Batas Keputusan",
                value=f"{THRESHOLD:.0%}",
                help="Threshold probabilitas optimal untuk mencapai Recall 76%."
            )
        with col_m3:
            st.metric(
                label="Baseline Keterlambatan Riil",
                value=f"{BASELINE_RATE:.1%}",
                help="Rata-rata persentase keterlambatan pada data riil."
            )
        with col_m4:
            rasio = skor / BASELINE_RATE
            st.metric(
                label="Faktor Risiko Relatif",
                value=f"{rasio:.1f}x",
                delta="Lebih rawan dari rata-rata" if rasio > 1.0 else "Di bawah rata-rata",
                delta_color="inverse" if rasio > 1.0 else "normal"
            )

        # 3. Visual Progress Bar Meter
        st.markdown("**Visualisasi Tingkat Risiko:**")
        st.progress(min(max(skor, 0.0), 1.0))
        col_bar_l, col_bar_r = st.columns(2)
        with col_bar_l:
            st.caption(f"🟢 **Zona Aman:** 0% — {THRESHOLD:.0%}")
        with col_bar_r:
            st.caption(f"<div style='text-align: right;'>🔴 **Zona Berisiko:** {THRESHOLD:.0%} — 100%</div>", unsafe_allow_html=True)

        # 4. Driver Risiko & Rekomendasi Mitigasi
        col_drv, col_mit = st.columns(2, gap="medium")

        with col_drv:
            st.markdown("##### 🔍 Analisis Faktor Pemicu (Risk Drivers)")
            pemicu = False

            # Cek Wilayah
            wilayah_rawan = ["AL", "MA", "PI", "CE", "SE", "PB", "RN", "BA"]
            if hasil["cs"] in wilayah_rawan:
                st.markdown(f"""
                <div class="insight-item" style="border-left-color: #ef4444;">
                    <b>📍 Lokasi Tujuan ({hasil['cs']}):</b> Berada di wilayah Timur Laut Brasil (Nordeste). 
                    Data historis membuktikan rute ini memiliki durasi transit terpanjang dan tingkat keterlambatan tertinggi.
                </div>
                """, unsafe_allow_html=True)
                pemicu = True
            elif hasil["cs"] in ["SP", "RJ", "MG", "PR"]:
                st.markdown(f"""
                <div class="insight-item" style="border-left-color: #10b981;">
                    <b>📍 Lokasi Tujuan ({hasil['cs']}):</b> Berada di kawasan hub logistik utama Tenggara/Selatan dengan transit tercepat.
                </div>
                """, unsafe_allow_html=True)

            # Cek Hari Beli
            if hasil["hb"] == 0:
                st.markdown("""
                <div class="insight-item" style="border-left-color: #f59e0b;">
                    <b>📆 Hari Pembelian (Senin):</b> Tingkat keterlambatan paling tinggi dalam seminggu akibat 
                    akumulasi pesanan selama akhir pekan (<i>weekend backlog</i>).
                </div>
                """, unsafe_allow_html=True)
                pemicu = True

            # Cek Bulan Beli
            if hasil["bb"] in [2, 3]:
                st.markdown(f"""
                <div class="insight-item" style="border-left-color: #ef4444;">
                    <b>📅 Periode Pembelian ({BULAN_MAP[hasil['bb']]}):</b> Bertepatan dengan musim Karnaval Brasil 
                    yang memicu penurunan kapasitas operasional ekspedisi secara masif.
                </div>
                """, unsafe_allow_html=True)
                pemicu = True

            if not pemicu:
                st.markdown("""
                <div class="insight-item" style="border-left-color: #10b981;">
                    <b>✨ Profil Pesanan Netral:</b> Tidak terdeteksi pemicu anomali risiko tinggi.
                </div>
                """, unsafe_allow_html=True)

        with col_mit:
            st.markdown("##### 📋 Rekomendasi Operasional (Actionable SOP)")
            if is_telat:
                st.markdown("""
                <div class="sop-box">
                    <p style="font-weight: 700; color: #dc2626; margin: 0 0 8px 0;">Langkah Mitigasi Cepat:</p>
                    <ol style="margin: 0; padding-left: 20px; font-size: 0.88rem; line-height: 1.6;">
                        <li><b>Fast-Track Packing:</b> Berikan label prioritas pada nota agar langsung dikemas dalam shift pertama.</li>
                        <li><b>Ekspedisi Alternatif:</b> Alihkan pengiriman ke kurir kargo udara untuk tujuan luar pulau/antar-provinsi.</li>
                        <li><b>Buffer SLA Proaktif:</b> Tambahkan buffer estimasi (+2 hari) di dashboard pembeli guna mencegah komplain.</li>
                    </ol>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="sop-box">
                    <p style="font-weight: 700; color: #16a34a; margin: 0 0 8px 0;">Jalur Reguler:</p>
                    <ul style="margin: 0; padding-left: 20px; font-size: 0.88rem; line-height: 1.6;">
                        <li>Pesanan diproses menggunakan alur normal (FIFO).</li>
                        <li>Gunakan opsi kurir darat berkontrak standar untuk efisiensi biaya logistik.</li>
                        <li>Tidak diperlukan pemantauan manual khusus.</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

        st.caption(
            f"ℹ️ *Catatan:* Skor risiko dihasilkan dari model Random Forest. Ambang batas <b>{THRESHOLD:.0%}</b> "
            f"dipilih secara strategis agar <b>76%</b> seluruh potensi pesanan terlambat dapat terdeteksi sejak awal."
        )
    else:
        st.info("💡 Klik tombol **'🔍 Hitung Risiko Keterlambatan'** di atas atau pilih salah satu tombol **Simulasi 1-Klik** di sidebar untuk melihat hasil prediksi.")

# ==============================================================================
# TAB 2: BUSINESS & DATA INSIGHTS
# ==============================================================================
with tab_insight:
    st.markdown("### 📊 Pola Keterlambatan Utama pada Data Historis")
    st.write("Temuan analitis dari **96.469 pesanan terkirim** yang menjadi landasan fitur model:")

    # Top KPI Metrics Row
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.markdown("""
        <div class="metric-card">
            <div class="title">Total Pesanan Dianalisis</div>
            <div class="value">96.469</div>
            <div class="subtitle">Transaksi E-Commerce Olist</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi2:
        st.markdown("""
        <div class="metric-card">
            <div class="title">Tingkat Keterlambatan Alami</div>
            <div class="value" style="color: #ea580c;">8,11%</div>
            <div class="subtitle">~340 pesanan komplain/bulan</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi3:
        st.markdown("""
        <div class="metric-card">
            <div class="title">Sensitivitas Model (Recall)</div>
            <div class="value" style="color: #2563eb;">76,0%</div>
            <div class="subtitle">Pesanan telat berhasil dijaring</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi4:
        st.markdown("""
        <div class="metric-card">
            <div class="title">Kemampuan Diskriminasi</div>
            <div class="value" style="color: #16a34a;">0,767</div>
            <div class="subtitle">Skor ROC-AUC Model Final</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # 2x2 Grid of Insight Charts
    col_c1, col_c2 = st.columns(2, gap="large")

    with col_c1:
        st.markdown("""
        <div class="custom-card">
            <h4 style="margin-top:0;">1. Pola Musiman: Efek Karnaval Brasil</h4>
            <p style="font-size: 0.88rem; opacity: 0.85;">
                Tingkat keterlambatan melonjak tajam pada bulan <b>Februari dan Maret</b>. 
                Hal ini berkorelasi langsung dengan festival nasional tahunan Karnaval Brasil di mana libur panjang, 
                penutupan akses jalan raya, dan kapasitas operasional kurir menurun drastis.
            </p>
        </div>
        """, unsafe_allow_html=True)
        img_bulan = os.path.join(BASE, "hasil", "grafik_bulan.png")
        if os.path.exists(img_bulan):
            st.image(img_bulan, use_container_width=True)

    with col_c2:
        st.markdown("""
        <div class="custom-card">
            <h4 style="margin-top:0;">2. Pola Mingguan: Efek Penumpukan Hari Senin</h4>
            <p style="font-size: 0.88rem; opacity: 0.85;">
                Pesanan yang masuk di hari <b>Senin</b> memiliki tingkat keterlambatan paling tinggi. 
                Penyebab utamanya adalah penumpukan pesanan yang masuk selama Sabtu dan Minggu saat gudang tutup, 
                sehingga terjadi bottleneck proses sortir pada awal pekan.
            </p>
        </div>
        """, unsafe_allow_html=True)
        img_hari = os.path.join(BASE, "hasil", "grafik_hari.png")
        if os.path.exists(img_hari):
            st.image(img_hari, use_container_width=True)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    col_c3, col_c4 = st.columns(2, gap="large")

    with col_c3:
        st.markdown("""
        <div class="custom-card">
            <h4 style="margin-top:0;">3. Pola Geografis: Disparitas Antar Wilayah</h4>
            <p style="font-size: 0.88rem; opacity: 0.85;">
                Wilayah <b>Timur Laut (Nordeste: AL, MA, PI, CE, SE)</b> memiliki risiko keterlambatan tertinggi, 
                sementara wilayah <b>Tenggara (Sudeste: SP, RJ, MG)</b> mencatat performa pengiriman paling konsisten dan tepat waktu.
            </p>
        </div>
        """, unsafe_allow_html=True)
        img_provinsi = os.path.join(BASE, "hasil", "grafik_provinsi.png")
        if os.path.exists(img_provinsi):
            st.image(img_provinsi, use_container_width=True)

    with col_c4:
        st.markdown("""
        <div class="custom-card">
            <h4 style="margin-top:0;">4. Evaluasi Model: Validasi Kurva ROC</h4>
            <p style="font-size: 0.88rem; opacity: 0.85;">
                Kurva <b>ROC-AUC (0,767)</b> membuktikan stabilitas model dalam membedakan pesanan berisiko. 
                Dengan threshold 0,4, tim logistik mampu mendeteksi <b>76% potensi keterlambatan</b> dengan beban peringatan palsu yang tetap rasional.
            </p>
        </div>
        """, unsafe_allow_html=True)
        img_roc = os.path.join(BASE, "hasil", "grafik_roc.png")
        if os.path.exists(img_roc):
            st.image(img_roc, use_container_width=True)

    # Rekomendasi Strategi Bisnis
    st.markdown("---")
    st.markdown("### 💡 Strategi Rekomendasi Bisnis & Logistik")
    
    strat1, strat2, strat3 = st.columns(3)
    with strat1:
        st.markdown("""
        <div class="custom-card" style="height: 100%;">
            <h5 style="color: #3b82f6; margin-top:0;">🎯 Dynamic SLA Buffer</h5>
            <p style="font-size: 0.85rem; opacity: 0.85;">
                Secara otomatis menambahkan toleransi estimasi waktu pengiriman (+2 s.d. +4 hari) pada halaman checkout 
                selama bulan Karnaval atau transaksi yang dilakukan pada hari Senin.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with strat2:
        st.markdown("""
        <div class="custom-card" style="height: 100%;">
            <h5 style="color: #3b82f6; margin-top:0;">📦 Regional Fulfillment Hub</h5>
            <p style="font-size: 0.85rem; opacity: 0.85;">
                Membangun atau menyewa fasilitas fulfillment satelit di kawasan Timur Laut (seperti Bahia atau Ceará) 
                untuk memangkas jarak transit antar-provinsi.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with strat3:
        st.markdown("""
        <div class="custom-card" style="height: 100%;">
            <h5 style="color: #3b82f6; margin-top:0;">🔔 Integrasi WMS Otomatis</h5>
            <p style="font-size: 0.85rem; opacity: 0.85;">
                Mengintegrasikan skor risiko ini langsung ke Warehouse Management System untuk memberi tagging prioritas 
                pada invoice gudang saat order pertama kali dicetak.
            </p>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# TAB 3: METODOLOGI & ARSITEKTUR ML
# ==============================================================================
with tab_metodologi:
    st.markdown("### 🧠 Metodologi & Pencegahan Data Leakage")
    st.markdown("""
    Dalam kompetisi **ICONFEST 2026 Data Mining**, kejujuran metodologi dan penerapan *clean data science practices* menjadi fokus utama:
    """)

    col_m_left, col_m_right = st.columns(2, gap="large")

    with col_m_left:
        st.markdown("""
        <div class="custom-card">
            <h4 style="margin-top:0;">🛡️ Pencegahan Kebocoran Data (Data Leakage)</h4>
            <p style="font-size: 0.88rem; opacity: 0.85; line-height: 1.6;">
                Banyak analisis pemula keliru memasukkan fitur seperti <i>lama pengiriman aktual</i>, <i>tanggal kurir mengambil paket</i>, 
                atau <i>tanggal persetujuan</i>. Variabel tersebut memang memiliki korelasi tinggi dengan keterlambatan, 
                namun <b>belum ada saat pesanan baru dibuat (t₀)</b>!
            </p>
            <p style="font-size: 0.88rem; opacity: 0.85; line-height: 1.6;">
                Model kami strictly hanya menggunakan data yang sudah valid saat checkout:
            </p>
            <ul style="font-size: 0.85rem; opacity: 0.9;">
                <li>Nilai transaksi (R$) & jumlah cicilan</li>
                <li>Metode pembayaran (kartu kredit, boleto, dll.)</li>
                <li>Provinsi tujuan penerima</li>
                <li>Estimasi durasi yang dijanjikan sistem checkout</li>
                <li>Waktu checkout (Hari & Bulan)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col_m_right:
        st.markdown("""
        <div class="custom-card">
            <h4 style="margin-top:0;">⚖️ Mengapa Decision Threshold 0,4?</h4>
            <p style="font-size: 0.88rem; opacity: 0.85; line-height: 1.6;">
                Distribusi data sangat timpang (hanya <b>8,1%</b> pesanan yang telat). Model tanpa penanganan khusus akan menghasilkan 
                akurasi semu 91,9% namun dengan <b>Recall 0%</b> (tidak mendeteksi satu pun keterlambatan).
            </p>
            <p style="font-size: 0.88rem; opacity: 0.85; line-height: 1.6;">
                Dengan <code>class_weight="balanced"</code> dan menurunkan ambang batas ke <b>0,40</b>:
            </p>
            <ul style="font-size: 0.85rem; opacity: 0.9;">
                <li><b>Recall melesat ke 76%:</b> Mencegah 3 dari setiap 4 pesanan telat sebelum terjadi komplain.</li>
                <li><b>Cost-benefit logistik:</b> Biaya audit status paket jauh lebih murah daripada biaya refund atau kehilangan loyalitas pelanggan e-commerce.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align: center; margin-top: 24px; padding: 16px; background: rgba(148, 163, 184, 0.08); border-radius: 12px; border: 1px dashed rgba(148, 163, 184, 0.3);">
        <span style="font-size: 0.85rem; opacity: 0.8;">
            📦 LogiLate AI prototype dikembangkan untuk <b>ICONFEST 2026 Data Mining Competition</b> oleh <b>[TimTam]</b>.
        </span>
    </div>
    """, unsafe_allow_html=True)