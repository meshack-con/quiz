import streamlit as st
import pandas as pd
import random
from supabase import create_client, Client
from datetime import datetime

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="Programming Quiz System",
    page_icon="🧠",
    layout="wide"
)

# -------------------------
# CUSTOM CSS & HTML (Kwa ajili ya Muonekano na Contrast)
# -------------------------
def apply_custom_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

        /* Background safi na Font ya Kisasa */
        .stApp {
            background-color: #ffffff;
            font-family: 'Poppins', sans-serif;
        }

        /* Maandishi yawe meusi ili yaonekane vizuri (Contrast) */
        h1, h2, h3, p, span, label, .stMarkdown {
            color: #1e293b !important;
        }

        /* Sidebar Styling (Dark Theme) */
        section[data-testid="stSidebar"] {
            background-color: #0f172a !important;
        }
        section[data-testid="stSidebar"] * {
            color: #ffffff !important;
        }

        /* Question & Result Cards */
        .q-card, .result-box {
            background: #f8fafc;
            padding: 30px;
            border-radius: 15px;
            border-left: 8px solid #3b82f6;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            margin-bottom: 20px;
        }
        
        /* Result Score highlight */
        .score-highlight {
            font-size: 48px;
            font-weight: 700;
            color: #3b82f6;
            margin: 10px 0;
        }

        /* Button Styling */
        .stButton>button {
            width: 100%;
            border-radius: 10px;
            height: 3.5em;
            background-color: #3b82f6 !important;
            color: white !important;
            font-weight: 600;
            border: none;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #2563eb !important;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        }

        /* Login Box */
        .login-box {
            background: white;
            padding: 2.5rem;
            border-radius: 20px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            border: 1px solid #e2e8f0;
        }
        </style>
    """, unsafe_allow_html=True)

apply_custom_style()

# -------------------------
# Supabase Config (As it was)
# -------------------------
SUPABASE_URL = "https://pnpjfaalcvetdjbcuadj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBucGpmYWFsY3ZldGRqYmN1YWRqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMyMjM5NTYsImV4cCI6MjA3ODc5OTk1Nn0.5AmOhm_ATsZTX1Vkg5_XHKEytVVpBsGCfATM4dqWlOo"

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# -------------------------
# Session Defaults
# -------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.quiz_started = False
    st.session_state.quiz_finished = False
    st.session_state.current_q = 0
    st.session_state.score = 0
    st.session_state.answers = {}
    st.session_state.quiz_questions = []

# -------------------------
# AUTHENTICATION
# -------------------------
st.markdown('<h1 style="text-align:center;">🧠 Programming Quiz System</h1>', unsafe_allow_html=True)

users_data = supabase.table("quiz_users").select("id, username, password").execute().data
usernames = [u["username"] for u in users_data]

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.subheader("🔐 Ingia Kwenye Mfumo")
        username = st.selectbox("Username", usernames)
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            user = next((u for u in users_data if u["username"] == username), None)
            if user and user["password"] == password:
                st.session_state.authenticated = True
                st.session_state.user_id = user["id"]
                st.session_state.username = username
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid credentials")
        st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# MAIN SYSTEM
# -------------------------
if st.session_state.authenticated:

    # -------- SIDEBAR --------
    st.sidebar.markdown(f"### 👤 {st.session_state.username}")
    st.sidebar.markdown("---")

    history = (
        supabase.table("test_results")
        .select("score, date_taken")
        .eq("user_id", st.session_state.user_id)
        .order("date_taken", desc=True)
        .limit(5).execute().data
    )

    st.sidebar.subheader("📜 Historia ya Majaribio")
    if history:
        for h in history:
            date_str = pd.to_datetime(h['date_taken']).strftime('%d %b %Y')
            st.sidebar.info(f"🗓 {date_str} → **{h['score']} / 20**")
    else:
        st.sidebar.write("Huna majaribio bado.")

    st.sidebar.markdown("---")
    st.sidebar.subheader("🏆 Top 3 Scores")
    top_scores = supabase.table("test_results").select("user_id, score").order("score", desc=True).limit(3).execute().data
    for i, t in enumerate(top_scores):
        user = next((u for u in users_data if u["id"] == t["user_id"]), {"username": "User"})
        st.sidebar.write(f"{i+1}. {user['username']} → **{t['score']}**")

    # -------- START QUIZ SCREEN --------
    if not st.session_state.quiz_started and not st.session_state.quiz_finished:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("📘 Maelekezo ya Jaribio")
            st.info("""
            • Jaribio lina maswali **20** ya kuchagua.
            • Kila swali lina jibu moja sahihi.
            • Alama zako zitahifadhiwa ukimaliza.
            """)
            if st.button("🚀 Anza Jaribio Sasa"):
                all_questions = supabase.table("quiz_questions").select("*").execute().data
                st.session_state.quiz_questions = random.sample(all_questions, 20)
                st.session_state.quiz_started = True
                st.session_state.quiz_finished = False
                st.session_state.current_q = 0
                st.session_state.score = 0
                st.session_state.answers = {}
                st.rerun()
        with col2:
            st.image("https://cdn-icons-png.flaticon.com/512/5692/5692030.png", width=200)

    # -------- QUIZ FLOW --------
    if st.session_state.quiz_started:
        q_idx = st.session_state.current_q
        
        if q_idx < 20:
            question = st.session_state.quiz_questions[q_idx]
            st.progress((q_idx) / 20)
            st.write(f"Swali la **{q_idx + 1}** kati ya 20")

            st.markdown('<div class="q-card">', unsafe_allow_html=True)
            st.subheader(question['question'])
            
            options = {
                "A": f"A. {question['option_a']}",
                "B": f"B. {question['option_b']}",
                "C": f"C. {question['option_c']}",
                "D": f"D. {question['option_d']}",
            }

            selected = st.radio("Chagua jibu sahihi:", list(options.values()), key=f"q_{q_idx}")

            if st.button("Next ➡️"):
                user_key = next(k for k, v in options.items() if selected == v)
                st.session_state.answers[q_idx] = user_key
                
                if user_key == question["correct_option"]:
                    st.session_state.score += 1

                st.session_state.current_q += 1
                if st.session_state.current_q >= 20:
                    st.session_state.quiz_started = False
                    st.session_state.quiz_finished = True
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # -------- RESULTS DISPLAY (Kipengele Kilichorekebishwa) --------
    if st.session_state.quiz_finished:
        st.balloons()
        
        # 1. Hifadhi matokeo mara moja tu
        if "data_saved" not in st.session_state:
            supabase.table("test_results").insert({
                "user_id": st.session_state.user_id,
                "score": st.session_state.score,
                "date_taken": datetime.now().isoformat()
            }).execute()
            st.session_state.data_saved = True

        # 2. Onyesha Score kwa uzuri
        st.markdown('<div class="result-box" style="text-align:center;">', unsafe_allow_html=True)
        st.markdown(f"## 🎉 Hongera sana, {st.session_state.username}!")
        st.markdown("### Jaribio lako limekamilika")
        st.markdown(f'<div class="score-highlight">{st.session_state.score} / 20</div>', unsafe_allow_html=True)
        
        percent = (st.session_state.score / 20) * 100
        st.write(f"Ufaulu wako ni **{percent}%**")
        st.markdown('</div>', unsafe_allow_html=True)

        # 3. Uchambuzi wa Majibu
        with st.expander("🔍 Angalia Uchambuzi wa Majibu"):
            results_data = []
            for i, q in enumerate(st.session_state.quiz_questions):
                user_key = st.session_state.answers.get(i)
                correct_key = q['correct_option']
                status = "✅ Sahihi" if user_key == correct_key else "❌ Kosa"
                
                results_data.append({
                    "Swali #": i+1,
                    "Hali": status,
                    "Swali": q['question'],
                    "Jibu Lako": user_key,
                    "Jibu Sahihi": correct_key
                })
            st.table(results_data)

        # 4. Kitufe cha kuanza upya
        if st.button("🔄 Anza Jaribio Jipya"):
            # Kusafisha session ili kuanza upya
            for key in ['quiz_started', 'quiz_finished', 'current_q', 'score', 'answers', 'data_saved']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
