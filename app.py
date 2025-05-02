import streamlit as st
from openai import OpenAI
import requests
import os
import time
from dotenv import load_dotenv
from pydub import AudioSegment
from io import BytesIO
import base64
import tempfile

# Load environment variables
load_dotenv("key.env")

# --- Set Page Config ---
st.set_page_config(
    page_title="Melody Magic",
    page_icon="🎶",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Background Image ---
def add_bg_from_local(image_file):
    with open(image_file, "rb") as image:
        encoded_string = base64.b64encode(image.read()).decode()
    
    bg_css = f"""
    <style>
    .stApp {{
        background-image: url(data:image/jpg;base64,{encoded_string});
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        background-color: rgba(0, 0, 0, 0.6);
        background-blend-mode: overlay;
    }}
    </style>
    """
    st.markdown(bg_css, unsafe_allow_html=True)

# Add your background image (replace with your image path)
add_bg_from_local("background.jpg")

# --- Custom CSS ---
custom_css = """
<style>
    /* Main containers */
    .main {
        background-color: rgba(0, 0, 0, 0.7);
        border-radius: 15px;
        padding: 2rem;
        margin-bottom: 2rem;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ffffff !important;
        text-shadow: 2px 2px 4px #000000;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #6e8efb, #a777e3);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 1.5rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    
    /* Input fields */
    .stTextInput>div>div>input, 
    .stSelectbox>div>div>select {
        background-color: rgba(255,255,255,0.9) !important;
        border-radius: 10px !important;
    }
    
    /* Progress bars */
    .stProgress>div>div>div>div {
        background: linear-gradient(90deg, #ff7e5f, #feb47b);
    }
    
    /* Audio player */
    audio {
        width: 100% !important;
        border-radius: 15px !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
    }
    
    /* Cards */
    .card {
        background-color: rgba(0,0,0,0.6) !important;
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-left: 5px solid #6e8efb;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- API KEYS ---
AIML_API_KEY = os.getenv("AIML_API_KEY", "1ca28fad60a345b7bbd663b6ce22b143")  # Fallback to demo key

if not AIML_API_KEY:
    st.error("❌ AIML_API_KEY not found. Make sure it's set in key.env.")
    st.stop()

# --- Initialize AI/ML clients ---
try:
    aiml_api = OpenAI(
        api_key=AIML_API_KEY,
        base_url="https://api.aimlapi.com/v1"
    )
except Exception as e:
    st.error(f"❌ Failed to initialize AIML API client: {e}")
    st.stop()

# --- Available TTS Models ---
TTS_MODELS = {
    "🎤 Aura-Angus (Male)": "#g1_aura-angus-en",
    "🎤 Aura-Arcas (Male)": "#g1_aura-arcas-en",
    "🎤 Aura-Asteria (Female)": "#g1_aura-asteria-en",
    "🎤 Aura-Athena (Female)": "#g1_aura-athena-en",
    "🎤 Aura-Helios (Male)": "#g1_aura-helios-en",
    "🎤 Aura-Hera (Female)": "#g1_aura-hera-en",
    "🎤 Aura-Luna (Female)": "#g1_aura-luna-en",
    "🎤 Aura-Orion (Male)": "#g1_aura-orion-en",
    "🎤 Aura-Orpheus (Male)": "#g1_aura-orpheus-en",
    "🎤 Aura-Perseus (Male)": "#g1_aura-perseus-en",
    "🎤 Aura-Stella (Female)": "#g1_aura-stella-en",
    "🎤 Aura-Zeus (Male)": "#g1_aura-zeus-en"
}

# --- App Header ---
st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <h1 style="font-size: 3.5rem; margin-bottom: 0.5rem;">🎵 Melody Magic</h1>
    <p style="font-size: 1.2rem; color: #ddd;">Create professional songs with AI-powered lyrics, vocals, and instrumentals</p>
</div>
""", unsafe_allow_html=True)

# --- Audio Processing Functions ---
def save_temp_audio(data, suffix):
    """Save audio data to a temporary file"""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    temp_file.write(data)
    temp_file.close()
    return temp_file.name

def robust_audio_mixer(vocals_data, instrumental_data):
    """More reliable audio mixing function"""
    try:
        # Save to temporary files
        vocal_file = save_temp_audio(vocals_data, ".wav")
        instrumental_file = save_temp_audio(instrumental_data, ".wav")
        
        # Load with explicit format
        vocals = AudioSegment.from_file(vocal_file, format="wav")
        instrumental = AudioSegment.from_file(instrumental_file, format="wav")
        
        # Align lengths
        target_length = min(len(vocals), len(instrumental))
        vocals = vocals[:target_length]
        instrumental = instrumental[:target_length]
        
        # Adjust volumes
        instrumental = instrumental - 6  # Lower instrumental volume
        vocals = vocals + 3  # Boost vocals slightly
        
        # Mix audio
        final_song = BytesIO()
        instrumental.overlay(vocals).export(final_song, format="mp3", bitrate="192k", codec="libmp3lame")
        final_song.seek(0)
        
        # Clean up
        os.unlink(vocal_file)
        os.unlink(instrumental_file)
        
        return final_song.getvalue()
        
    except Exception as e:
        st.error(f"Audio mixing error: {str(e)}")
        return None

# --- Main Container ---
with st.container():
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("""
        <div class="card">
            <h3>🎚️ Song Settings</h3>
        </div>
        """, unsafe_allow_html=True)
        
        mood = st.selectbox("Mood", ["Happy 😊", "Sad 😢", "Chill 😎", "Energetic ⚡", "Romantic ❤️"])
        genre = st.selectbox("Genre", ["Pop 🎤", "Hip Hop 🎧", "Classical 🎻", "EDM 🎹", "Rock 🤘", "R&B 🎶"])
        keywords = st.text_input("Theme/Keywords", placeholder="e.g., love, rain, party, summer")
        voice_model = st.selectbox("Vocal Voice", options=list(TTS_MODELS.keys()))
        
        if st.button("✨ Create My Song", use_container_width=True):
            st.session_state['create_song'] = True
        else:
            st.session_state['create_song'] = False
    
    with col2:
        st.markdown("""
        <div class="card">
            <h3>🎼 Preview</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if 'final_song' in st.session_state:
            st.audio(st.session_state['final_song'], format="audio/mp3")
            st.download_button(
                label="⬇️ Download Song",
                data=st.session_state['final_song'],
                file_name=f"{st.session_state.get('title', 'my_song')}.mp3",
                mime="audio/mp3",
                use_container_width=True
            )
        
        if 'lyrics' in st.session_state:
            with st.expander("📝 View Lyrics", expanded=True):
                st.write(st.session_state['lyrics'])
                st.download_button(
                    label="⬇️ Download Lyrics",
                    data=st.session_state['lyrics'],
                    file_name=f"{st.session_state.get('title', 'my_song')}_lyrics.txt",
                    mime="text/plain",
                    use_container_width=True
                )

# --- Song Generation Logic ---
if st.session_state.get('create_song', False):
    with st.spinner("🎶 Composing your masterpiece..."):
        # Clear previous results
        st.session_state.pop('final_song', None)
        
        # --- Step 1: Generate Lyrics ---
        with st.status("🎤 Writing lyrics...", expanded=True) as status:
            try:
                lyric_prompt = f"""Write professional {genre.split(' ')[0]} song lyrics with:
                                - Mood: {mood.split(' ')[0]}
                                - Theme: {keywords or 'general'}
                                - Clear verse/chorus structure
                                - 3 verses and 2 repeating choruses
                                - Each line max 40 characters"""
                
                lyrics_result = aiml_api.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": lyric_prompt}],
                    temperature=0.7,
                    max_tokens=500
                )
                st.session_state['lyrics'] = lyrics_result.choices[0].message.content
                status.update(label="✅ Lyrics complete!", state="complete")
                
            except Exception as e:
                status.update(label="❌ Lyrics generation failed", state="error")
                st.error(f"Error: {e}")
                st.stop()

        # --- Step 2: Generate Title ---
        with st.status("🧠 Creating title...", expanded=True) as status:
            try:
                title_prompt = f"Create a short, catchy {genre.split(' ')[0]} song title for these lyrics:\n\n{st.session_state['lyrics']}"
                title_result = aiml_api.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": title_prompt}],
                    temperature=0.7,
                    max_tokens=30
                )
                st.session_state['title'] = title_result.choices[0].message.content.strip('"')
                status.update(label=f"✅ Title: {st.session_state['title']}", state="complete")
                
            except Exception as e:
                st.session_state['title'] = "My AI Song"
                status.update(label="⚠️ Using default title", state="complete")

        # --- Step 3: Generate Vocals ---
        with st.status("🎤 Recording vocals...", expanded=True) as status:
            try:
                # Clean lyrics
                clean_lyrics = "\n".join(
                    line for line in st.session_state['lyrics'].split("\n") 
                    if line.strip() and not line.startswith(("[", "(", "-"))
                )
                
                if len(clean_lyrics) > 3000:
                    clean_lyrics = clean_lyrics[:3000]
                
                # TTS Request
                tts_response = requests.post(
                    "https://api.aimlapi.com/v1/tts",
                    headers={
                        "Authorization": f"Bearer {AIML_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": TTS_MODELS[voice_model],
                        "text": clean_lyrics,
                        "container": "wav",
                        "encoding": "linear16",
                        "sample_rate": "44100"  # Higher quality
                    },
                    timeout=60
                )
                
                if tts_response.status_code == 201:
                    st.session_state['vocals'] = tts_response.content
                    status.update(label="✅ Vocals recorded!", state="complete")
                else:
                    status.update(label="❌ Vocal generation failed", state="error")
                    st.error(f"API Error: {tts_response.text}")
                    st.stop()
                    
            except Exception as e:
                status.update(label="❌ Vocal generation error", state="error")
                st.error(f"Error: {e}")
                st.stop()

        # --- Step 4: Generate Instrumental ---
        with st.status("🎹 Composing instrumental...", expanded=True) as status:
            try:
                instrumental_prompt = (
                    f"Professional {genre.split(' ')[0]} instrumental music matching theme: {keywords or ''}. "
                    f"Mood: {mood.split(' ')[0]}. No vocals. Studio quality."
                )
              
                response = requests.post(
                    "https://api.aimlapi.com/v2/generate/audio",
                    headers={
                        "Authorization": f"Bearer {AIML_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "stable-audio",
                        "prompt": instrumental_prompt[:500],
                        "seconds_start": 1,
                        "seconds_total": 30,  # Within 47-second limit
                        "steps": 100
                    },
                    timeout=30
                )
                
                if response.status_code == 201:
                    generation_data = response.json()
                    generation_id = generation_data.get("id")
                    
                    # Poll for completion
                    max_attempts = 15
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    instrumental_url = None
                    
                    for attempt in range(max_attempts):
                        time.sleep(5)
                        progress = (attempt + 1) / max_attempts
                        progress_bar.progress(progress)
                        
                        status_response = requests.get(
                            "https://api.aimlapi.com/v2/generate/audio",
                            headers={
                                "Authorization": f"Bearer {AIML_API_KEY}",
                                "Content-Type": "application/json"
                            },
                            params={"generation_id": generation_id},
                            timeout=30
                        )
                        
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            current_status = status_data.get("status")
                            status_text.info(f"Status: {current_status} (Attempt {attempt + 1}/{max_attempts})")
                            
                            if current_status == "completed":
                                instrumental_url = status_data.get("audio_file", {}).get("url")
                                break
                            elif current_status == "failed":
                                st.error(f"Generation failed: {status_data.get('error', 'Unknown error')}")
                                break
                    
                    progress_bar.empty()
                    
                    if instrumental_url:
                        instrumental_data = requests.get(instrumental_url).content
                        st.session_state['instrumental'] = instrumental_data
                        status.update(label="✅ Instrumental composed!", state="complete")
                    else:
                        status.update(label="⚠️ Instrumental generation incomplete", state="error")
                        st.stop()
                else:
                    status.update(label="❌ Instrumental generation failed", state="error")
                    st.error(f"API Error: {response.text}")
                    st.stop()
                    
            except Exception as e:
                status.update(label="❌ Instrumental generation error", state="error")
                st.error(f"Error: {e}")
                st.stop()

        # --- Step 5: Mix Song ---
        with st.status("🎚️ Mixing final song...", expanded=True) as status:
            try:
                if 'vocals' not in st.session_state or 'instrumental' not in st.session_state:
                    st.error("Missing audio components for mixing")
                    st.stop()
                
                mixed_audio = robust_audio_mixer(st.session_state['vocals'], st.session_state['instrumental'])
                
                if mixed_audio:
                    st.session_state['final_song'] = mixed_audio
                    status.update(label="🎉 Your song is ready!", state="complete")
                    st.balloons()
                else:
                    status.update(label="❌ Mixing failed", state="error")
                    st.stop()
                
            except Exception as e:
                status.update(label="❌ Mixing error", state="error")
                st.error(f"Error: {e}")
                st.stop()

# --- Footer ---
st.markdown("""
<div style="text-align: center; margin-top: 3rem; color: #aaa; font-size: 0.9rem;">
    <p>Created with ❤️ using AI Magic</p>
    <p>Note: Song generation may take 2-3 minutes</p>
</div>
""", unsafe_allow_html=True)
