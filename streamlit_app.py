import os
import tempfile
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

# Load local environment
load_dotenv()

# Also support Streamlit Cloud secrets
if hasattr(st, "secrets"):
    for key in ["GROQ_API_KEY", "DEEPGRAM_API_KEY", "GROQ_MODEL"]:
        if key in st.secrets and not os.environ.get(key):
            os.environ[key] = st.secrets[key]

from main import process_inputs

st.set_page_config(
    page_title="AI Skin Specialist",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0051d5;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #555;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    .disclaimer-card {
        background-color: #f0f4ff;
        border-left: 4px solid #0051d5;
        padding: 12px 16px;
        border-radius: 6px;
        margin-bottom: 20px;
        font-size: 0.88rem;
        color: #203a70;
    }
    .output-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 18px;
        margin-top: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/dermatology.png", width=64)
    st.title("About AI Skin Specialist")
    st.markdown(
        """
        This AI consultation assistant accepts:
        - 🎙️ **Voice description** of symptoms
        - 📸 **Skin photo** of the concern
        - 🎥 **Optional video**
        
        It transcribes your speech via **Groq Whisper**, generates clinical insights with **Groq Vision**, and produces audio advice via **Deepgram**.
        """
    )
    st.divider()
    
    # API Key status check
    groq_ok = bool(os.environ.get("GROQ_API_KEY"))
    deepgram_ok = bool(os.environ.get("DEEPGRAM_API_KEY"))
    
    st.markdown("**API Status:**")
    st.markdown(f"- Groq: {'✅ Connected' if groq_ok else '❌ Missing Key'}")
    st.markdown(f"- Deepgram: {'✅ Connected' if deepgram_ok else '❌ Missing Key'}")

# Header
st.markdown('<div class="main-header">🩺 AI Skin Specialist Consultation</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Describe your skin symptoms and upload a photo for informational AI clinical guidance.</div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="disclaimer-card">
        ℹ️ <strong>Medical Disclaimer:</strong> This application is for educational and informational purposes only. It does not provide medical diagnoses or replace an evaluation by a licensed dermatologist.
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("1. Patient Input")
    
    st.markdown("**Voice Description**")
    audio_record = st.audio_input("Record your voice describing your symptoms")
    audio_upload = st.file_uploader("Or upload an audio file", type=["wav", "mp3", "m4a"])
    
    audio_source = audio_record or audio_upload
    
    st.markdown("**Skin Image**")
    image_file = st.file_uploader("Upload a clear photo of the skin concern", type=["jpg", "jpeg", "png"])
    if image_file:
        st.image(image_file, caption="Uploaded Skin Photo", use_container_width=True)
        
    st.markdown("**Optional Video**")
    video_file = st.file_uploader("Upload a short video showing multiple angles (optional)", type=["mp4", "mov"])
    
    analyze_btn = st.button("🩺 Analyze Concern", type="primary", use_container_width=True)

with col2:
    st.subheader("2. Doctor's Response")
    
    if analyze_btn:
        if not audio_source:
            st.error("⚠️ Please record or upload your voice description first.")
        elif not image_file and not video_file:
            st.error("⚠️ Please upload a skin photo or video for visual assessment.")
        else:
            with st.spinner("Doctor is analyzing your concern..."):
                try:
                    # Save temporary audio file
                    audio_ext = ".wav" if getattr(audio_source, "name", "").endswith(".wav") else ".mp3"
                    with tempfile.NamedTemporaryFile(delete=False, suffix=audio_ext) as tmp_audio:
                        tmp_audio.write(audio_source.read())
                        temp_audio_path = tmp_audio.name
                        
                    # Save temporary image file
                    temp_img_path = None
                    if image_file:
                        img_ext = Path(image_file.name).suffix or ".jpg"
                        with tempfile.NamedTemporaryFile(delete=False, suffix=img_ext) as tmp_img:
                            tmp_img.write(image_file.read())
                            temp_img_path = tmp_img.name
                            
                    # Save temporary video file
                    temp_vid_path = None
                    if video_file:
                        vid_ext = Path(video_file.name).suffix or ".mp4"
                        with tempfile.NamedTemporaryFile(delete=False, suffix=vid_ext) as tmp_vid:
                            tmp_vid.write(video_file.read())
                            temp_vid_path = tmp_vid.name

                    # Run analysis
                    transcript, doctor_text, doctor_audio = process_inputs(
                        audio_filepath=temp_audio_path,
                        image_filepath=temp_img_path,
                        video_filepath=temp_vid_path,
                    )
                    
                    st.success("Analysis complete!")
                    
                    st.markdown("### 🎙️ Patient Speech Transcript")
                    st.info(transcript)
                    
                    st.markdown("### 🩺 Doctor's Guidance")
                    st.markdown(f"**Dr. Sarah:** {doctor_text}")
                    
                    if doctor_audio and Path(doctor_audio).exists():
                        st.markdown("### 🔊 Spoken Consultation")
                        st.audio(str(doctor_audio), format="audio/mp3", autoplay=True)
                        
                except Exception as e:
                    st.error(f"Error during analysis: {e}")
                finally:
                    # Cleanup temporary files
                    try:
                        if temp_audio_path and os.path.exists(temp_audio_path):
                            os.remove(temp_audio_path)
                        if temp_img_path and os.path.exists(temp_img_path):
                            os.remove(temp_img_path)
                        if temp_vid_path and os.path.exists(temp_vid_path):
                            os.remove(temp_vid_path)
                    except Exception:
                        pass
    else:
        st.info("👈 Upload your details on the left and click **Analyze Concern** to see the consultation summary and hear the doctor's spoken response.")
