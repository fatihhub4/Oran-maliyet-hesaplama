import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# --- 1. KONFİGÜRASYON ---
st.set_page_config(
    page_title="Pro Lab",
    page_icon="🧪",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- SABİT DEĞERLER (DATABASE) ---
FIXED_DENSITY_ALCOHOL = 0.80  # 1 ml = 0.80 gr kabul edildi
FIXED_DENSITY_WATER = 1.00    # 1 ml = 1.00 gr kabul edildi
SOURCE_ALCOHOL_DEGREE = 96.6  # Kullanılan alkolün saflık derecesi (Varsayılan)

# --- CSS VE TASARIM (ŞİŞE SİMÜLASYONU DAHİL) ---
st.markdown("""
    <style>
    /* Genel Temizlik */
    .block-container {padding-top: 2rem; padding-bottom: 5rem;}
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    
    /* Başlık Stili */
    .main-title {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-size: 2rem;
        font-weight: 300;
        letter-spacing: 2px;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-size: 0.9rem;
        opacity: 0.6;
        text-align: center;
        margin-bottom: 3rem;
        letter-spacing: 1px;
    }

    /* --- CSS PARFÜM ŞİŞESİ --- */
    .bottle-container {
        display: flex;
        justify-content: center;
        margin-bottom: 30px;
    }
    .bottle {
        width: 120px;
        height: 180px;
        border: 2px solid var(--text-color); 
        border-radius: 15px 15px 5px 5px;
        position: relative;
        overflow: hidden;
        background-color: rgba(255,255,255,0.05);
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        transition: border-color 0.5s; 
    }
    /* Şişe Kapağı */
    .bottle::before {
        content: '';
        position: absolute;
        top: -25px;
        left: 35px;
        width: 50px;
        height: 20px;
        background-color: #333;
        border-radius: 2px;
    }
    /* Sıvı Katmanları */
    .liquid-alcohol {
        width: 100%;
        background-color: #BDBDBD; /* Gri */
        transition: height 0.5s ease;
    }
    .liquid-water {
        width: 100%;
        background-color: #81D4FA; /* Açık Mavi */
        transition: height 0.5s ease;
    }
    .liquid-essence {
        width: 100%;
        background-color: #FFD700; /* Altın */
        transition: height 0.5s ease;
    }
    
    /* Lejant (Açıklama) */
    .legend-box {
        display: flex;
        justify-content: center;
        gap: 15px;
        font-size: 0.8rem;
        margin-bottom: 20px;
        opacity: 0.8;
    }
    .dot {
        height: 10px;
        width: 10px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 5px;
    }

    /* Metrik Kartları */
    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.05);
        border: 1px solid rgba(128, 128, 128, 0.1);
        border-radius: 8px;
        padding: 10px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# --- PDF FONKSİYONU ---
def create_pdf(vol, mass, data, final_alc_degree):
    pdf = FPDF()
    pdf.add_page()
    
    # Başlık
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 15, "PRO LAB RECETESI", 0, 1, 'C')
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 10, f"Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M')}", 0, 1, 'C')
    pdf.ln(10)
    
    # Özet
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"HEDEF HACIM: {vol} ML  |  TOPLAM KUTLE: {mass:.2f} GR", 0, 1, 'C')
    pdf.cell(0, 10, f"FINAL ALKOL DERECESI: {final_alc_degree:.2f}°", 0, 1, 'C')
    pdf.ln(10)
    
    # Tablo Başlıkları
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(60, 10, "BILESEN", 1, 0, 'L', 1)
    pdf.cell(40, 10, "MIKTAR", 1, 0, 'C', 1)
    pdf.cell(40, 10, "ORAN", 1, 1, 'C', 1)
    
    # İçerik
    pdf.set_font("Arial", '', 10)
    for item in data:
        # Birim Düzeltmesi (Esans: GR, Diğerleri: ML)
        unit = "Gr" if item['name'] == "ESANS" else "Ml"
        val = item['mass'] if unit == "Gr" else item['vol']
        
        pdf.cell(60, 10, item['name'], 1)
        pdf.cell(40, 10, f"{val:.2f} {unit}", 1, 0, 'C')
        pdf.cell(40, 10, f"%{item['pct']:.1f}", 1, 1, 'C')
        pdf.ln()
        
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- HTML ŞİŞE ÇİZİM FONKSİYONU ---
def render_bottle(e_pct, w_pct, a_pct):
    # Yüzdelerin Toplamı %100'ü geçmeyeceği garanti
    h_ess = e_pct
    h_wat = w_pct
    h_alc = a_pct
    
    # Boşluk
    h_empty = 100 - (h_ess + h_wat + h_alc)
    if h_empty < 0: h_empty = 0

    html = f"""
    <div class="bottle-container">
        <div class="bottle">
            <div style="height: {h_empty}%; width:100%;"></div>
            <div class="liquid-alcohol" style="height: {h_alc}%;"></div>
            <div class="liquid-water" style="height: {h_wat}%;"></div>
            <div class="liquid-essence" style="height: {h_ess}%;"></div>
        </div>
    </div>
    <div class="legend-box">
        <span><span class="dot" style="background-color: #FFD700;"></span>Esans</span>
        <span><span class="dot" style="background-color: #81D4FA;"></span>Su</span>
        <span><span class="dot" style="background-color: #BDBDBD;"></span>Alkol</span>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# --- UYGULAMA GÖVDESİ ---
st.markdown('<div class="main-title">PRO LAB</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">KÜTLESEL HESAPLAYICI</div>', unsafe_allow_html=True)

# Sekmeler
tab1, tab2 = st.tabs(["REÇETE", "MALİYET"])

# --- SEKME 1: REÇETE ---
with tab1:
    # 1. Girdiler
    col_L, col_R = st.columns(2)
    
    with col_L:
        target_vol = st.number_input("Şişe Hacmi (ML)", value=100, step=10, key="v1")
        # Esans yoğunluğu varsayılan 0.98 ve değiştirilebilir
        essence_dens = st.number_input("Esans Yoğunluğu (gr/ml)", value=0.98, step=0.01, format="%.2f", key="d1")
        
    with col_R:
        essence_pct = st.number_input("Esans Oranı (%)", value=20.0, step=0.5, format="%.1f", key="p1")
        water_pct = st.number_input("Saf Su Oranı (%)", value=0.0, step=0.5, format="%.1f", key="p2")

    # Alkol Hesaplama
    alcohol_pct = 100 - (essence_pct + water_pct)
    
    if alcohol_pct < 0:
        st.error("⚠️ Hata: Oranlar toplamı %100'ü geçiyor!")
    else:
        st.markdown("---")
        
        # 1. Matematik
        # Hacimler (ML)
        v_ess = target_vol * (essence_pct / 100)
        v_wat = target_vol * (water_pct / 100)
        v_alc = target_vol * (alcohol_pct / 100)
        
        # Kütleler (GR)
        m_ess = v_ess * essence_dens
        m_wat = v_wat * FIXED_DENSITY_WATER
        m_alc = v_alc * FIXED_DENSITY_ALCOHOL
        
        total_mass = m_ess + m_wat + m_alc
        
        # 2. ALKOL DERECESİ HESAPLAMA (YENİ EKLENEN KISIM)
        final_alc_degree = (v_alc / target_vol) * SOURCE_ALCOHOL_DEGREE
        
        # 3. Şişe Görseli
        render_bottle(essence_pct, water_pct, alcohol_pct)
        
        # 4. Sonuçlar
        st.markdown("### 📋 Reçete Detayı")
        
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("ESANS", f"{m_ess:.2f} gr") 
        k2.metric("SU", f"{v_wat:.1f} ml")    
        k3.metric("ALKOL", f"{v_alc:.1f} ml") 
        k4.metric("FINAL ALKOL", f"{final_alc_degree:.2f}°") # Yeni Metrik
        
        st.info(f"⚖️ **TOPLAM KÜTLE:** {total_mass:.2f} Gram (Tam {target_vol} ML Şişe)")
        
        # 5. PDF İndirme
        export_list = [
            {'name': 'ESANS', 'mass': m_ess, 'vol': v_ess, 'pct': essence_pct},
            {'name': 'SAF SU', 'mass': m_wat, 'vol': v_wat, 'pct': water_pct},
            {'name': 'ALKOL', 'mass': m_alc, 'vol': v_alc, 'pct': alcohol_pct}
        ]
        pdf_data = create_pdf(target_vol, total_mass, export_list, final_alc_degree)
        st.download_button("📥 Reçeteyi İndir (PDF)", pdf_data, file_name="prolab_recete.pdf", mime="application/pdf", use_container_width=True)

# --- SEKME 2: MALİYET ---
with tab2:
    st.caption("Birim fiyatları girerek sıvı maliyetini hesaplayın.")
    
    col_miktarlar, col_fiyatlar = st.columns(2)
    with col_miktarlar:
        st.markdown("**Kullanılan Miktarlar**")
        u_ess = st.number_input("Esans (Gr)", value=0.0, step=1.0, key="ugr")
        u_wat = st.number_input("Su (Ml)", value=0.0, step=1.0, key="uwml")
        u_alc = st.number_input("Alkol (Ml)", value=0.0, step=1.0, key="uaml")
    
    with col_fiyatlar:
        st.markdown("**Birim Fiyatlar**")
        p_ess = st.number_input("Esans (TL / 1 Gr)", value=0.0, step=0.5, key="pgr")
        p_wat = st.number_input("Su (TL / 1 Litre)", value=0.0, step=1.0, key="plt_w")
        p_alc = st.number_input("Alkol (TL / 1 Litre)", value=0.0, step=10.0, key="plt_a")
        
    # Hesaplama: (Miktar x Birim Fiyat)
    cost_e = u_ess * p_ess
    cost_w = (u_wat / 1000) * p_wat 
    cost_a = (u_alc / 1000) * p_alc 
    total_cost = cost_e + cost_w + cost_a
    
    st.divider()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Esans Tutarı", f"{cost_e:.2f} TL")
    c2.metric("Su Tutarı", f"{cost_w:.2f} TL")
    c3.metric("Alkol Tutarı", f"{cost_a:.2f} TL")
    
    if total_cost > 0:
        st.success(f"💰 **SIVI MALİYETİ:** {total_cost:.2f} TL")
    else:
        st.warning("Maliyet hesaplaması için miktar ve fiyat giriniz.")

