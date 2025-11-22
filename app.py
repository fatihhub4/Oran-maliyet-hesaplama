import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64
from datetime import datetime
import plotly.graph_objects as go

# --- 1. SAYFA VE TASARIM AYARLARI ---
st.set_page_config(
    page_title="Pro Lab",
    page_icon="🧪",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Minimalist CSS (Gece/Gündüz Modu Uyumlu & Estetik İyileştirmeler)
st.markdown("""
    <style>
    /* Ana Başlık Gizle ve Boşluğu Al */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding-top: 2rem; padding-bottom: 2rem;}
    
    /* Tab Tasarımı */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(128, 128, 128, 0.1);
        border-bottom: 2px solid #ff4b4b;
    }
    
    /* Metrik Kutuları */
    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.05);
        border-radius: 10px;
        padding: 15px;
        border: 1px solid rgba(128, 128, 128, 0.1);
    }
    
    /* Minimalist Başlık */
    .pro-title {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 300;
        font-size: 1.8rem;
        margin-bottom: 0.5rem;
        letter-spacing: 1px;
    }
    .pro-subtitle {
        font-size: 0.9rem;
        opacity: 0.7;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. SABİT YOĞUNLUKLAR (DATABASE) ---
# Alkol: 1gr = 0.80 ml (Bu fiziksel olarak ters (d=1.25) ama isteğine sadık kaldım. 
# Normalde Alkol d=0.789'dur. Eğer 1ml = 0.8gr kastediyorsan d=0.80'dir. 
# Aşağıda d=0.80 (1ml = 0.8gr) mantığını kullandım çünkü parfümde standart budur.)
DENSITY_ALCOHOL = 0.80 
DENSITY_WATER = 1.00

# --- PDF OLUŞTURMA ---
def create_pdf(vol_total, mass_total, recipe_data):
    pdf = FPDF()
    pdf.add_page()
    
    # Modern Başlık
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 15, "PRO LAB RECETE", 0, 1, 'C')
    
    pdf.set_font("Arial", '', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, f"Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M')}", 0, 1, 'C')
    pdf.ln(10)
    
    # Özet Bilgi Kutusu
    pdf.set_fill_color(240, 240, 240)
    pdf.rect(10, 35, 190, 25, 'F')
    pdf.set_xy(15, 40)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(90, 15, f"HEDEF HACIM: {vol_total} ML", 0, 0)
    pdf.cell(90, 15, f"TOPLAM KUTLE: {mass_total:.2f} GR", 0, 1, 'R')
    pdf.ln(15)
    
    # Tablo Başlık
    pdf.set_font("Arial", 'B', 10)
    pdf.set_fill_color(200, 200, 200)
    pdf.cell(60, 10, "BILESEN", 1, 0, 'L', 1)
    pdf.cell(45, 10, "MIKTAR (GR)", 1, 0, 'C', 1)
    pdf.cell(45, 10, "HACIM (ML)", 1, 0, 'C', 1)
    pdf.cell(40, 10, "ORAN (%)", 1, 1, 'C', 1)
    
    # Tablo İçeriği
    pdf.set_font("Arial", '', 10)
    for item in recipe_data:
        pdf.cell(60, 10, item['name'], 1)
        pdf.cell(45, 10, f"{item['mass']:.2f}", 1, 0, 'C')
        pdf.cell(45, 10, f"{item['vol']:.2f}", 1, 0, 'C')
        pdf.cell(40, 10, f"%{item['pct']:.1f}", 1, 1, 'C')
        
    # Alt Bilgi
    pdf.set_y(-30)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, "Pro Lab Sistem Tarafindan Olusturulmustur.", 0, 0, 'C')
    
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- ŞİŞE GÖRSELLEŞTİRME (PLOTLY) ---
def draw_bottle_chart(ess_pct, wat_pct, alc_pct):
    fig = go.Figure()
    
    # Esans (En Alt - Altın Rengi)
    fig.add_trace(go.Bar(
        name='Esans', x=['Şişe'], y=[ess_pct],
        marker_color='#D4AF37', hoverinfo='text',
        text=f"Esans<br>%{ess_pct:.1f}", textposition='auto'
    ))
    
    # Su (Orta - Açık Mavi)
    if wat_pct > 0:
        fig.add_trace(go.Bar(
            name='Su', x=['Şişe'], y=[wat_pct],
            marker_color='#4FC3F7', hoverinfo='text',
            text=f"Su<br>%{wat_pct:.1f}", textposition='auto'
        ))
        
    # Alkol (En Üst - Şeffaf/Gri)
    fig.add_trace(go.Bar(
        name='Alkol', x=['Şişe'], y=[alc_pct],
        marker_color='#E0E0E0', hoverinfo='text',
        text=f"Alkol<br>%{alc_pct:.1f}", textposition='auto'
    ))

    fig.update_layout(
        barmode='stack',
        yaxis=dict(range=[0, 100], visible=False),
        xaxis=dict(visible=False),
        margin=dict(l=20, r=20, t=0, b=0),
        height=300,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

# --- ARAYÜZ ---
st.markdown('<div class="pro-title">PRO LAB</div>', unsafe_allow_html=True)
st.markdown('<div class="pro-subtitle">Kütlesel Formülasyon & Maliyet</div>', unsafe_allow_html=True)

# Sekmeler
tab_recipe, tab_cost = st.tabs(["⚗️ ORANLAR & REÇETE", "💰 MALİYET HESAPLAMA"])

# ==========================================
# SEKME 1: ORANLAR VE REÇETE
# ==========================================
with tab_recipe:
    # --- Üst Panel: Girişler ---
    col_in1, col_in2 = st.columns(2)
    
    with col_in1:
        target_vol = st.number_input("Hedef Şişe (ML)", value=100, step=10)
        essence_dens = st.number_input("Esans Yoğunluğu", value=0.98, step=0.01, format="%.2f")
        
    with col_in2:
        essence_pct = st.number_input("Esans Oranı (%)", value=20.0, step=0.5, format="%.1f")
        # Su ml olarak istenmedi çünkü oran bozulur, kullanıcı % girmeli, biz ml hesaplarız.
        # Ama isteğe sadık kalmak için buraya % koyuyorum, çünkü formül % üzerine kurulu.
        water_pct = st.number_input("Saf Su Oranı (%)", value=0.0, step=0.5, format="%.1f")

    # Alkol Hesaplama
    alcohol_pct = 100 - (essence_pct + water_pct)
    
    if alcohol_pct < 0:
        st.error("⚠️ HATA: Toplam oran %100'ü geçiyor!")
    else:
        # --- Hesaplama Motoru ---
        # Hacimler (ML)
        vol_ess = target_vol * (essence_pct / 100)
        vol_wat = target_vol * (water_pct / 100)
        vol_alc = target_vol * (alcohol_pct / 100)
        
        # Kütleler (Gram)
        mass_ess = vol_ess * essence_dens
        mass_wat = vol_wat * DENSITY_WATER
        mass_alc = vol_alc * DENSITY_ALCOHOL
        
        total_mass = mass_ess + mass_wat + mass_alc
        
        st.markdown("---")
        
        # --- Görsel ve Sonuç Paneli ---
        c_vis, c_res = st.columns([1, 2])
        
        with c_vis:
            # Şişe Grafiği
            st.plotly_chart(draw_bottle_chart(essence_pct, water_pct, alcohol_pct), use_container_width=True)
            
        with c_res:
            st.caption("🧪 REÇETE (TERAZİYE KONACAKLAR)")
            
            # Modern Kartlar
            m1, m2, m3 = st.columns(3)
            m1.metric("ESANS", f"{mass_ess:.2f} g", f"{vol_ess:.1f} ml")
            m2.metric("SU", f"{mass_wat:.2f} g", f"{vol_wat:.1f} ml")
            m3.metric("ALKOL", f"{mass_alc:.2f} g", f"{vol_alc:.1f} ml")
            
            st.success(f"⚖️ **TOPLAM AĞIRLIK: {total_mass:.2f} Gram** (Tam {target_vol} ML)")
            
            # Veri Hazırlığı (PDF İçin)
            recipe_data = [
                {'name': 'ESANS', 'mass': mass_ess, 'vol': vol_ess, 'pct': essence_pct},
                {'name': 'SAF SU', 'mass': mass_wat, 'vol': vol_wat, 'pct': water_pct},
                {'name': 'ALKOL', 'mass': mass_alc, 'vol': vol_alc, 'pct': alcohol_pct}
            ]
            
            # PDF İndirme
            pdf_bytes = create_pdf(target_vol, total_mass, recipe_data)
            st.download_button(
                label="📄 REÇETEYİ İNDİR (PDF)",
                data=pdf_bytes,
                file_name="prolab_recete.pdf",
                mime="application/pdf",
                use_container_width=True
            )

# ==========================================
# SEKME 2: BİRİM FİYAT HESAPLAMA
# ==========================================
with tab_cost:
    st.info("Burada sadece elindeki miktarları ve birim fiyatları gir, maliyeti gör.")
    
    c_cost1, c_cost2 = st.columns(2)
    
    with c_cost1:
        st.markdown("###### 📦 Kullanılan Miktarlar")
        # Kullanıcı buraya reçeteden aldığı gramajı girecek
        use_ess_g = st.number_input("Kullanılan Esans (Gr)", value=0.0, step=1.0)
        use_wat_ml = st.number_input("Kullanılan Su (ML)", value=0.0, step=1.0)
        use_alc_ml = st.number_input("Kullanılan Alkol (ML)", value=0.0, step=1.0)
        
    with c_cost2:
        st.markdown("###### 🏷️ Birim Fiyatlar")
        price_ess = st.number_input("Esans Fiyatı (TL / 1 Gr)", value=0.0, step=0.5)
        price_wat = st.number_input("Saf Su Fiyatı (TL / 1 Lt)", value=0.0, step=5.0)
        price_alc = st.number_input("Alkol Fiyatı (TL / 1 Lt)", value=0.0, step=10.0)
        
    st.markdown("---")
    
    # Hesaplama
    cost_essence = use_ess_g * price_ess
    cost_water = (use_wat_ml / 1000) * price_wat
    cost_alcohol = (use_alc_ml / 1000) * price_alc
    total_cost_liquid = cost_essence + cost_water + cost_alcohol
    
    # Sonuç Kartları
    cc1, cc2, cc3 = st.columns(3)
    cc1.metric("Esans Tutarı", f"{cost_essence:.2f} TL")
    cc2.metric("Su Tutarı", f"{cost_water:.2f} TL")
    cc3.metric("Alkol Tutarı", f"{cost_alcohol:.2f} TL")
    
    st.success(f"💰 **SIVI MALİYETİ (Şişe Hariç): {total_cost_liquid:.2f} TL**")

