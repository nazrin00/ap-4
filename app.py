import streamlit as st
import google.generativeai as genai
import pypdf
from docx import Document
import io

# Səhifə nizamlamaları
st.set_page_config(page_title="Azərbaycan Dili AI Korrektor", layout="wide")
st.title("✍️ Azərbaycan Dili AI Kitab Redaktoru")
st.write("PDF kitabınızı yükləyin, AI orfoqrafiya, nöqtə-vergül və mötərizə qaydalarını tam düzəltsin.")

# API Açarını daxil edin (Bunu bura birbaşa yaza bilərsiniz)
GOOGLE_API_KEY = "SİZİN_GOOGLE_API_KEYİNİZ" 
genai.configure(api_key=GOOGLE_API_KEY)

# Gemini 1.5 Pro modelini işə salırıq (Böyük kitablar üçün ən yaxşısıdır)
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    system_instruction=(
        "Sən peşəkar Azərbaycan dili redaktorusan. Sənə verilən mətndəki bütün orfoqrafik, "
        "qrammatik, nöqtə, vergül, mötərizə və durğu işarələri səhvlərini rəsmi dil qaydalarına uyğun düzəlt. "
        "Mətnin üslubunu və mənasını dəyişmə, sadəcə səhvləri tam korreksiya et və yalnız düzəldilmiş yekun mətni qaytar."
    )
)

uploaded_file = st.file_uploader("PDF Formatında Kitab Yükləyin (400-600 səhifə dəstəklənir)", type=["pdf"])

if uploaded_file is not None:
    # PDF-i oxuyuruq
    pdf_reader = pypdf.PdfReader(uploaded_file)
    total_pages = len(pdf_reader)
    st.success(f"Kitab uğurla yükləndi! Cəmi səhifə: {total_pages}")
    
    # Ananızın işləyəcəyi redaktə sahəsi üçün boş bir mətn dəyişəni
    full_corrected_text = ""
    
    if st.button("🚀 Kitabı AI ilə Yoxlamağa Başla"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Səhifə-səhifə analiz (Yaddaşın dolmaması və donmaması üçün)
        for page_num in range(total_pages):
            status_text.text(f"Səhifə {page_num + 1}/{total_pages} analiz edilir...")
            
            # Səhifənin mətnini çıxarırıq
            page_text = pdf_reader.pages[page_num].extract_text()
            
            if page_text.strip():
                # AI-a göndəririk
                response = model.generate_content(f"Bu sənəd səhifəsini redaktə et:\n\n{page_text}")
                full_corrected_text += response.text + "\n\n--- Səhifə Sonu ---\n\n"
            
            # Proqres barı yeniləyirik
            progress_bar.progress((page_num + 1) / total_pages)
            
        st.success("🎉 Bütün kitab tam yoxlanıldı!")
        st.session_state['corrected_text'] = full_corrected_text

    # Əgər yoxlama bitibsə redaktə panelini göstər
    if 'corrected_text' in st.session_state:
        st.subheader("📝 Kitabın Redaktə və Oxu Paneli")
        
        # Şrift ölçüsü seçimi (Ananızın rahat oxuması üçün)
        font_size = st.slider("Mətnin Şrift Ölçüsü (px):", 12, 30, 16)
        
        # Redaktə edilə bilən böyük yazı qutusu
        # Ananız burada səhvləri özü də silib-yaza bilər, şrifti slider ilə böyüdə bilər
        st.markdown(f"<style>textarea {{font-size: {font_size}px !important;}}</style>", unsafe_allow_html=True)
        user_edited_text = st.text_area("AI tərəfindən düzəldilmiş tam mətn (Burada dəyişiklik edə bilərsiniz):", 
                                        st.session_state['corrected_text'], height=500)
        
        # Word (DOCX) kimi endirmək funksiyası
        doc = Document()
        doc.add_paragraph(user_edited_text)
        bio = io.BytesIO()
        doc.save(bio)
        
        st.subheader("📥 Hazır Kitabı Yükləyin")
        st.download_button(
            label="📄 Kitabı WORD (.docx) kimi telefonuova endir",
            data=bio.getvalue(),
            file_name="duzeldilmis_kitab.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )