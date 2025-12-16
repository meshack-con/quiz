# =========================
# IMPROVED STREAMLIT QUIZ APP
# =========================

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
# Supabase Config
# -------------------------
SUPABASE_URL = "https://pnpjfaalcvetdjbcuadj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBucGpmYWFsY3ZldGRqYmN1YWRqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMyMjM5NTYsImV4cCI6MjA3ODc5OTk1Nn0.5AmOhm_ATsZTX1Vkg5_XHKEytVVpBsGCfATM4dqWlOo"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------
# Session Defaults
# -------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.quiz_started = False
    st.session_state.quiz_finished = False # Kipengele kipya
    st.session_state.current_q = 0
    st.session_state.score = 0
    st.session_state.answers = {}
    st.session_state.quiz_questions = []

# -------------------------
# AUTHENTICATION
# -------------------------
st.title("🧠 Programming Quiz System")

users_data = supabase.table("quiz_users").select("id, username, password").execute().data
usernames = [u["username"] for u in users_data]

if not st.session_state.authenticated:
    with st.container(border=True):
        st.subheader("🔐 Login")

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
        .limit(5)
        .execute()
        .data
    )

    st.sidebar.subheader("📜 Test History")
    if history:
        for h in history:
            st.sidebar.write(
                f"🗓 {pd.to_datetime(h['date_taken']).strftime('%d %b %Y')} → **{h['score']} / 20**"
            )
    else:
        st.sidebar.info("No tests yet")

    st.sidebar.markdown("---")

    top_scores = (
        supabase.table("test_results")
        .select("user_id, score")
        .order("score", desc=True)
        .limit(3)
        .execute()
        .data
    )

    st.sidebar.subheader("🏆 Top 3")
    for t in top_scores:
        user = next(u for u in users_data if u["id"] == t["user_id"])
        st.sidebar.write(f"⭐ {user['username']} → {t['score']}")

    # -------- START QUIZ --------
    if not st.session_state.quiz_started and not st.session_state.quiz_finished:
        st.subheader("📘 Instructions")
        st.info(
            """
            • This quiz contains **20 multiple-choice questions** • Each question has **one correct answer** • Your score will be saved after submission 
            """
        )

        if st.button("🚀 Start Quiz"):
            all_questions = supabase.table("quiz_questions").select("*").execute().data
            st.session_state.quiz_questions = random.sample(all_questions, 20)
            st.session_state.quiz_started = True
            st.session_state.quiz_finished = False # Hakikisha inakuwa False
            st.session_state.current_q = 0
            st.session_state.score = 0
            st.session_state.answers = {}
            st.rerun()

    # -------- QUIZ FLOW --------
    if st.session_state.quiz_started:

        q_index = st.session_state.current_q
        
        # Hakikisha hatuzidi ukomo wa maswali 20
        if q_index < 20:
            question = st.session_state.quiz_questions[q_index]

            st.progress((q_index) / 20)
            st.markdown(f"### Question {q_index + 1} / 20")

            with st.container(border=True):
                st.markdown(f"**{question['question']}**")

                options = {
                    "A": f"A. {question['option_a']}",
                    "B": f"B. {question['option_b']}",
                    "C": f"C. {question['option_c']}",
                    "D": f"D. {question['option_d']}",
                }

                selected = st.radio(
                    "Choose an answer:",
                    list(options.values()),
                    key=f"q_{q_index}"
                )

                if st.button("Next"):
                    user_answer_key = None
                    for k, v in options.items():
                        if selected == v:
                            user_answer_key = k
                            break
                    
                    # Hifadhi jibu la mtumiaji
                    st.session_state.answers[q_index] = user_answer_key
                    
                    # Pima kama jibu ni sahihi na ongeza score
                    if user_answer_key == question["correct_option"]:
                        st.session_state.score += 1

                    st.session_state.current_q += 1

                    # -------- FINISH QUIZ CHECK --------
                    if st.session_state.current_q >= 20:
                        st.session_state.quiz_started = False
                        st.session_state.quiz_finished = True
                    
                    st.rerun()
        else:
             # Kwa namna yoyote, ikifikia hapa, imemaliza
             st.session_state.quiz_started = False
             st.session_state.quiz_finished = True
             st.rerun()
             
    # -------- RESULTS DISPLAY (Kipengele Kipya) --------
    if st.session_state.quiz_finished:
        
        # Pongezi na Balloons
        st.balloons()
        st.success(f"🎉 **HONGERA! UMEPATA {st.session_state.score} KATI YA 20!** 🎉")
        
        # Hifadhi matokeo kwenye Supabase (Imehama hapa kwa uhakika zaidi)
        supabase.table("test_results").insert({
             "user_id": st.session_state.user_id,
             "score": st.session_state.score,
             "date_taken": datetime.now().isoformat()
        }).execute()

        st.markdown("---")
        st.subheader("📝 Uchambuzi wa Matokeo")
        st.info("Angalia majibu yako hapa chini: Jibu lako linapatikana ndani ya mabano `()`.")

        results_data = []
        for i, question in enumerate(st.session_state.quiz_questions):
            user_key = st.session_state.answers.get(i)
            correct_key = question['correct_option']

            # Pata jibu kamili kutoka kwenye options
            option_map = {
                 "A": question['option_a'],
                 "B": question['option_b'],
                 "C": question['option_c'],
                 "D": question['option_d'],
            }
            
            # Hakikisha majibu yapo
            correct_answer_text = option_map.get(correct_key, "N/A")
            user_answer_text = option_map.get(user_key, "Hakujibu")

            status = "✅ SAHIHI" if user_key == correct_key else "❌ KOSA"
            
            results_data.append({
                "Swali": f"{i+1}. {question['question']}",
                "Hali": status,
                "Jibu Lako": f"({user_key}) {user_answer_text}",
                "Jibu Sahihi": f"({correct_key}) {correct_answer_text}",
            })

        # Display matokeo kama DataFrame au kwa kutumia Markdown
        results_df = pd.DataFrame(results_data)
        
        # Tumia st.table (au st.dataframe) kuonyesha matokeo
        st.dataframe(
            results_df,
            column_config={
                "Swali": st.column_config.Column(width="medium"),
                "Hali": st.column_config.Column(width="small"),
                "Jibu Lako": st.column_config.Column(width="medium"),
                "Jibu Sahihi": st.column_config.Column(width="medium"),
            },
            hide_index=True,
        )
        
        st.markdown("---")
        if st.button("Anza Jaribio Jipya"):
            st.session_state.quiz_finished = False
            st.session_state.quiz_started = False
            st.session_state.current_q = 0
            st.session_state.score = 0
            st.session_state.answers = {}
            st.rerun()
