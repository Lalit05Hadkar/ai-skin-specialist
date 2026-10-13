import os
import tempfile
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

# Load local environment
load_dotenv()

# Support Streamlit Cloud secrets seamlessly
if hasattr(st, "secrets"):
    for key in ["GROQ_API_KEY", "DEEPGRAM_API_KEY", "GROQ_MODEL"]:
        if key in st.secrets and not os.environ.get(key):
            os.environ[key] = st.secrets[key]

# Fallback default model
if not os.environ.get("GROQ_MODEL"):
    os.environ["GROQ_MODEL"] = "qwen/qwen3.8-27b"

from main import process_inputs

st.set_page_config(
    page_title="AI Skin Specialist | Clinical Consultation",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Comprehensive Material & Clinical Design System CSS
st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet"/>
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>

    <style>
    /* Reset & Global */
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        background-color: #f7f9fb !important;
        color: #191c1e !important;
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    #MainMenu, footer {
        visibility: hidden;
    }

    .block-container {
        max-width: 1280px !important;
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
    }

    /* Top Navigation Bar */
    .ais-topbar {
        background: #ffffff;
        border: 1px solid #c6c6cd;
        border-radius: 20px;
        padding: 20px 28px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 24px;
        box-shadow: 0 4px 18px rgba(19, 27, 46, 0.04);
    }
    .ais-brand h1 {
        font-size: 26px;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin: 0;
        color: #191c1e;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .ais-brand p {
        font-size: 13px;
        font-weight: 500;
        color: #45464d;
        margin: 4px 0 0;
    }
    .ais-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: #f2f4f6;
        border: 1px solid #c6c6cd;
        padding: 8px 14px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 600;
        color: #0051d5;
    }

    /* Clinical Cards */
    .ais-panel {
        background: #ffffff;
        border: 1px solid #c6c6cd;
        border-radius: 18px;
        padding: 24px;
        box-shadow: 0 10px 30px rgba(19, 27, 46, 0.05);
        margin-bottom: 20px;
    }
    .ais-section-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 18px;
    }
    .ais-section-header h2 {
        font-size: 20px;
        font-weight: 650;
        margin: 0;
        color: #191c1e;
    }
    .ais-icon-blue {
        color: #0051d5;
        font-size: 24px;
    }

    /* Informational Notes */
    .ais-note {
        background: rgba(219, 225, 255, 0.6);
        border-radius: 12px;
        padding: 12px 16px;
        display: flex;
        align-items: flex-start;
        gap: 10px;
        color: #003ea8;
        font-size: 13px;
        font-weight: 500;
        margin-top: 14px;
    }

    /* Empty State */
    .ais-empty {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 70px 20px;
        min-height: 480px;
    }
    .ais-empty-icon {
        width: 88px;
        height: 88px;
        border-radius: 999px;
        background: #f2f4f6;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 18px;
    }
    .ais-empty-title {
        font-size: 20px;
        font-weight: 700;
        color: #191c1e;
        margin-bottom: 6px;
    }
    .ais-empty-desc {
        font-size: 14px;
        color: #45464d;
        max-width: 360px;
        line-height: 1.5;
    }

    /* Output Results Styling */
    .ais-result-box {
        background: #f2f4f6;
        border: 1px solid #eceef0;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 18px;
    }
    .ais-result-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #45464d;
        margin-bottom: 10px;
    }
    .ais-transcript-text {
        font-size: 15px;
        font-style: italic;
        color: #191c1e;
        line-height: 1.6;
    }
    .ais-doctor-box {
        background: #ffffff;
        border: 1.5px solid #dbe1ff;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 14px rgba(0, 81, 213, 0.06);
    }
    .ais-doctor-text {
        font-size: 16px;
        line-height: 1.65;
        color: #191c1e;
        font-weight: 450;
    }

    /* Streamlit Button Overrides */
    div.stButton > button[kind="primary"] {
        background: #316bf3 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 16px !important;
        font-weight: 650 !important;
        font-size: 17px !important;
        padding: 18px 24px !important;
        min-height: 60px !important;
        box-shadow: 0 10px 24px rgba(0, 81, 213, 0.2) !important;
        transition: all 0.2s ease !important;
        margin-top: 10px !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background: #0051d5 !important;
        box-shadow: 0 12px 28px rgba(0, 81, 213, 0.3) !important;
        transform: translateY(-1px);
    }

    /* Streamlit Input Cleanups */
    [data-testid="stFileUploader"] {
        background: #fafbfc;
        border: 1px dashed #c6c6cd;
        border-radius: 14px;
        padding: 10px;
        transition: border-color 0.2s ease;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #316bf3;
    }
    [data-testid="stAudioInput"] {
        background: #fafbfc;
        border: 1px solid #c6c6cd;
        border-radius: 14px;
        padding: 10px;
    }

    /* Footer */
    .ais-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-top: 1px solid #c6c6cd;
        margin-top: 36px;
        padding-top: 20px;
        font-size: 12px;
        font-weight: 500;
        color: #45464d;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Top Bar
st.markdown(
    """
    <div class="ais-topbar">
        <div class="ais-brand">
            <h1><span class="material-symbols-outlined ais-icon-blue" style="font-size:32px;">dermatology</span> AI Skin Specialist</h1>
            <p>Voice, image, and video based skin consultation assistant</p>
        </div>
        <div class="ais-badge">
            <span class="material-symbols-outlined" style="font-size:18px;">verified</span>
            <span>Clinically Guided AI</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 2-Column Clinical Layout
left_col, right_col = st.columns([5, 7], gap="large")

with left_col:
    st.markdown(
        """
        <div class="ais-section-header">
            <span class="material-symbols-outlined ais-icon-blue">clinical_notes</span>
            <h2>Patient Input</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container():
        st.markdown("**Describe your skin concern**")
        st.caption("Record using your microphone or upload an audio clip")
        voice_rec = st.audio_input("Record voice", label_visibility="collapsed")
        voice_up = st.file_uploader("Or upload voice audio", type=["wav", "mp3", "m4a"], key="voice_up")

        selected_audio = voice_rec or voice_up

        st.markdown("<br/>**Upload Visual References**", unsafe_allow_html=True)
        img_col, vid_col = st.columns(2)

        with img_col:
            st.caption("📸 **Skin Image** (Required)")
            img_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"], key="img_file", label_visibility="collapsed")
            if img_file:
                st.image(img_file, use_container_width=True)

        with vid_col:
            st.caption("🎥 **Skin Video** (Optional)")
            vid_file = st.file_uploader("Upload Video", type=["mp4", "mov"], key="vid_file", label_visibility="collapsed")

        st.markdown(
            """
            <div class="ais-note">
                <span class="material-symbols-outlined" style="font-size:18px; color:#0051d5;">info</span>
                <span>For better assessment, include a short video showing the affected area from multiple angles and under good lighting.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        analyze_clicked = st.button("🩺 Analyze Concern", type="primary", use_container_width=True)

with right_col:
    st.markdown(
        """
        <div class="ais-section-header">
            <span class="material-symbols-outlined ais-icon-blue">smart_toy</span>
            <h2>Doctor Response</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    result_placeholder = st.empty()

    if analyze_clicked:
        if not selected_audio:
            st.error("⚠️ Please record or upload your voice description first.")
        elif not img_file and not vid_file:
            st.error("⚠️ Please upload a skin photo or video for analysis.")
        else:
            with st.spinner("Analyzing your concern with medical AI..."):
                try:
                    # Save temporary audio file
                    audio_ext = ".wav" if getattr(selected_audio, "name", "").endswith(".wav") else ".mp3"
                    with tempfile.NamedTemporaryFile(delete=False, suffix=audio_ext) as tmp_audio:
                        tmp_audio.write(selected_audio.read())
                        temp_audio_path = tmp_audio.name

                    # Save temporary image file
                    temp_img_path = None
                    if img_file:
                        img_ext = Path(img_file.name).suffix or ".jpg"
                        with tempfile.NamedTemporaryFile(delete=False, suffix=img_ext) as tmp_img:
                            tmp_img.write(img_file.read())
                            temp_img_path = tmp_img.name

                    # Save temporary video file
                    temp_vid_path = None
                    if vid_file:
                        vid_ext = Path(vid_file.name).suffix or ".mp4"
                        with tempfile.NamedTemporaryFile(delete=False, suffix=vid_ext) as tmp_vid:
                            tmp_vid.write(vid_file.read())
                            temp_vid_path = tmp_vid.name

                    # Execute full pipeline
                    transcript, doctor_text, doctor_audio = process_inputs(
                        audio_filepath=temp_audio_path,
                        image_filepath=temp_img_path,
                        video_filepath=temp_vid_path,
                    )

                    with result_placeholder.container():
                        st.markdown(
                            f"""
                            <div class="ais-result-box">
                                <div class="ais-result-title">
                                    <span class="material-symbols-outlined" style="font-size:16px;">record_voice_over</span>
                                    Your Speech Transcript
                                </div>
                                <div class="ais-transcript-text">"{transcript}"</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        st.markdown(
                            f"""
                            <div class="ais-doctor-box">
                                <div class="ais-result-title" style="color:#0051d5;">
                                    <span class="material-symbols-outlined" style="font-size:18px;">health_and_safety</span>
                                    Doctor's Guidance
                                </div>
                                <div class="ais-doctor-text">{doctor_text}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        if doctor_audio and Path(doctor_audio).exists():
                            st.markdown("**🔊 Spoken Doctor Consultation**")
                            st.audio(str(doctor_audio), format="audio/mp3", autoplay=True)

                        st.markdown(
                            """
                            <div style="display:flex; align-items:center; justify-content:center; gap:8px; color:#45464d; font-size:12px; font-weight:600; margin-top:16px;">
                                <span class="material-symbols-outlined" style="color:#0051d5; font-size:18px;">verified</span>
                                <span>AI guidance is informational and not a medical diagnosis</span>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                except Exception as e:
                    st.error(f"Error during analysis: {e}")
                finally:
                    # Cleanup temporary files
                    for p in [temp_audio_path, temp_img_path, temp_vid_path]:
                        try:
                            if p and os.path.exists(p):
                                os.remove(p)
                        except Exception:
                            pass
    else:
        with result_placeholder.container():
            st.markdown(
                """
                <div class="ais-empty">
                    <div class="ais-empty-icon">
                        <span class="material-symbols-outlined" style="font-size:46px; color:#76777d;">pending_actions</span>
                    </div>
                    <div class="ais-empty-title">Ready for Analysis</div>
                    <div class="ais-empty-desc">Your consultation summary, AI transcript, and medical guidance will appear here after you submit your concern.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# Footer
st.markdown(
    """
    <div class="ais-footer">
        <div><strong>AI Skin Specialist</strong> · Consult a licensed dermatologist for urgent or serious symptoms.</div>
        <div>Privacy Policy · Terms of Service · Medical Disclaimer</div>
    </div>
    """,
    unsafe_allow_html=True,
)
