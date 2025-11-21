import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64
from datetime import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Pro Lab Parfüm", page_icon="⚗️", layout="centered")

# --- PDF OLUŞTURMA FONKSİYONU ---
def create_pdf(product_name, total_vol, results, cost_total, cost_liquid):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Başlık
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="LABORATUVAR URETIM RECETESI", ln=1, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt=f"Tarih: {datetime.now().strftime('%d-%m-%Y %H:%M')}", ln=1, align='C')
    pdf.ln(10)
    
    # Bilgiler
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Hedef Hacim: {total_vol} ML", ln=1)
    pdf.ln(5)
    
    # Tablo Başlıkları
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(60, 10, "Bilesen", 1)
    pdf.cell(40, 10, "Miktar (Gr)", 1)
    pdf.cell(40, 10, "Hacim (Ml)", 1)
    pdf.cell(50, 10, "Maliyet (TL)", 1)
    pdf.ln()
    
    # Tablo İçeriği
    pdf.set_font("Arial", size=10)
    for item in results:
        pdf.cell(60, 10, item['name'], 1)
        pdf.cell(40, 10, f"{item['mass']:.2f}", 1)
        pdf.cell(40, 10, f"{item['vol']:.2f}", 1)
        pdf.cell(50, 10, f"{item['cost']:.2f}", 1)
        pdf.ln()
        
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=f"TOPLAM KUTLE (Terazi): {sum(x['mass'] for x in results):.2f} Gram", ln=1)
    
    if cost_total > 0:
        pdf.cell(200, 10, txt=f"TOPLAM MALIYET: {cost_liquid:.2f} TL", ln=1)
        
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- BAŞLIK ---
st.title("⚗️ Pro Lab: Kütlesel Hesaplayıcı")
st.markdown("**Gram Hassasiyetli Formülasyon ve Maliyet Analizi**")
st.info("Şişe hacmine tam sığacak NET gramajı hesaplar.")

# --- 1. BÖLÜM: HEDEF HACİM ---
st.markdown("### 1. Üretim Hedefi")
target_vol = st.number_input("Toplam Şişe Hacmi (ML)", value=100, step=10, help="Doldurmak istediğiniz şişenin hacmi.")

st.markdown("---")

# --- 2. BÖLÜM: FORMÜLASYON GİRİŞİ ---
st.markdown("### 2. Bileşenler ve Yoğunluklar")

# Kolon Yapısı: Başlıklar
c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
c1.caption("**Bileşen**")
c2.caption("**Oran (%)**")
c3.caption("**Yoğunluk (g/ml)**")
c4.caption("**Birim Fiyat (TL/gr)**")

# --- ESANS GİRİŞİ ---
col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
col1.markdown("#### 🌸 ESANS")
ess_pct = col2.number_input("Esans %", value=20.0, step=0.5, key="ep")
ess_dens = col3.number_input("Esans Yoğ.", value=1.05, step=0.01, key="ed")
ess_price = col4.number_input("Esans TL/gr", value=5.0, step=0.1, key="epr")

# --- SU GİRİŞİ ---
col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
col1.markdown("#### 💧 SAF SU")
wat_pct = col2.number_input("Su %", value=5.0, step=0.5, key="wp")
wat_dens = col3.number_input("Su Yoğ.", value=1.00, step=0.01, key="wd")
wat_price = col4.number_input("Su TL/gr", value=0.0, step=0.01, key="wpr")

# --- ALKOL GİRİŞİ (Otomatik) ---
# Hesaplama
alc_pct = 100 - (ess_pct + wat_pct)
status_color = "off" if alc_pct < 0 else "green"

col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
col1.markdown("#### 🧪 ALKOL")
col2.metric("Alkol %", f"{alc_pct:.1f}")
if alc_pct < 0:
    col2.error("HATA")
alc_dens = col3.number_input("Alkol Yoğ.", value=0.789, step=0.001, key="ad")
alc_price = col4.number_input("Alkol TL/gr", value=0.25, step=0.01, key="apr")

st.markdown("---")

# --- HESAPLAMA BUTONU VE MANTIK ---
if st.button("⚗️ HESAPLA VE ANALİZ ET", type="primary", use_container_width=True):
    
    if alc_pct < 0:
        st.error("⚠️ HATA: Girdiğiniz oranların toplamı %100'ü geçiyor! Lütfen Esans veya Su oranını düşürün.")
    else:
        # 1. Hacim Dağılımı (ML)
        vol_ess = target_vol * (ess_pct / 100)
        vol_wat = target_vol * (wat_pct / 100)
        vol_alc = target_vol * (alc_pct / 100)
        
        # 2. Kütle Dönüşümü (Gram = ML x Yoğunluk)
        mass_ess = vol_ess * ess_dens
        mass_wat = vol_wat * wat_dens
        mass_alc = vol_alc * alc_dens
        
        total_mass = mass_ess + mass_wat + mass_alc
        
        # 3. Maliyet Hesabı (Gram x Gram Fiyatı)
        cost_ess = mass_ess * ess_price
        cost_wat = mass_wat * wat_price
        cost_alc = mass_alc * alc_price
        
        total_cost = cost_ess + cost_wat + cost_alc
        
        # Veri Listesi (PDF ve Tablo için)
        results_list = [
            {"name": "ESANS", "mass": mass_ess, "vol": vol_ess, "cost": cost_ess},
            {"name": "SAF SU", "mass": mass_wat, "vol": vol_wat, "cost": cost_wat},
            {"name": "ALKOL", "mass": mass_alc, "vol": vol_alc, "cost": cost_alc}
        ]

        # --- SONUÇ EKRANI ---
        st.success("✅ Hesaplama Tamamlandı!")
        
        # Özet Metrikler
        m1, m2 = st.columns(2)
        m1.info(f"⚖️ **TERAZİDE TARTILACAK:**\n# **{total_mass:.2f} Gram**\n(Tam {target_vol} ML Hacim Yapar)")
        m2.success(f"💰 **TOPLAM MALİYET:**\n# **{total_cost:.2f} TL**")
        
        st.markdown("### 📋 Reçete Detayı")
        
        # Görsel Tablo
        df_res = pd.DataFrame(results_list)
        df_res.columns = ["Bileşen", "Kütle (Gr)", "Hacim (Ml)", "Tutar (TL)"]
        st.dataframe(df_res, use_container_width=True, hide_index=True)
        
        # --- PDF İNDİRME ---
        st.markdown("### 📤 Dışa Aktar")
        pdf_bytes = create_pdf("Ozel Formül", target_vol, results_list, total_cost, total_cost)
        
        st.download_button(
            label="📄 Reçeteyi PDF Olarak İndir",
            data=pdf_bytes,
            file_name=f"parfum_recete_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
