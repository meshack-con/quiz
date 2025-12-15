# =========================
# STREAMLIT QUIZ APP
# =========================

import streamlit as st
import pandas as pd
import random
from supabase import create_client, Client
from datetime import datetime

# -------------------------
# Supabase Config
# -------------------------
SUPABASE_URL = "https://pnpjfaalcvetdjbcuadj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBucGpmYWFsY3ZldGRqYmN1YWRqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMyMjM5NTYsImV4cCI6MjA3ODc5OTk1Nn0.5AmOhm_ATsZTX1Vkg5_XHKEytVVpBsGCfATM4dqWlOo"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------
# Authentication
# -------------------------
st.title("Quiz System")

# Load users from Supabase
users_data = supabase.table("quiz_users").select("id, username, password").execute().data
usernames = [u['username'] for u in users_data]

selected_user = st.selectbox("Select Username", usernames)
password_input = st.text_input("Enter Password", type="password")

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if st.button("Login") and not st.session_state['authenticated']:
    user_record = next((u for u in users_data if u['username'] == selected_user), None)
    if user_record and password_input == user_record['password']:
        st.session_state['user_id'] = user_record['id']
        st.session_state['authenticated'] = True
        st.success(f"Welcome, {selected_user}")
    else:
        st.error("Incorrect password")

# -------------------------
# Main Quiz & Dashboard
# -------------------------
if st.session_state.get('authenticated', False):

    st.header("Your Dashboard")

    # -------------------------
    # Display user test history
    # -------------------------
    user_history = supabase.table("test_results").select("*").eq("user_id", st.session_state['user_id']).execute().data
    if user_history:
        df_history = pd.DataFrame(user_history)
        df_history['date_taken'] = pd.to_datetime(df_history['date_taken'])
        st.subheader("Your Test History")
        st.dataframe(df_history[['date_taken', 'score']].sort_values(by='date_taken', ascending=False))
    else:
        st.info("You have not taken any tests yet.")

    # -------------------------
    # Quiz Section
    # -------------------------
    st.subheader("Take a New Quiz")
    if st.button("Start Quiz"):

        # Load all questions from Supabase
        questions_data = supabase.table("quiz_questions").select("*").execute().data
        if len(questions_data) < 20:
            st.error("Not enough questions in the database (need at least 20).")
        else:
            quiz_questions = random.sample(questions_data, 20)  # Random 20 questions
            st.session_state['quiz_questions'] = quiz_questions
            st.session_state['answers'] = {}  # store answers

    # Display quiz if loaded
    if 'quiz_questions' in st.session_state:
        st.write("Answer the following 20 questions:")

        for i, q in enumerate(st.session_state['quiz_questions']):
            st.write(f"**Q{i+1}: {q['question']}**")
            st.session_state['answers'][i] = st.radio(
                "Choose an option",
                ['A', 'B', 'C', 'D'],
                key=f"q{i}"
            )

        if st.button("Submit Quiz"):

            # Calculate score
            score = 0
            for i, q in enumerate(st.session_state['quiz_questions']):
                if st.session_state['answers'][i] == q['correct_option']:
                    score += 1

            # Save result to Supabase
            supabase.table("test_results").insert({
                "user_id": st.session_state['user_id'],
                "score": score,
                "date_taken": datetime.now().isoformat()
            }).execute()

            st.success(f"You scored {score}/20")

            # Show correct answers
            st.subheader("Correct Answers")
            for i, q in enumerate(st.session_state['quiz_questions']):
                st.write(f"Q{i+1}: Correct answer is **{q['correct_option']}**")

            # Clear quiz from session state
            del st.session_state['quiz_questions']
            del st.session_state['answers']

    # -------------------------
    # Leaderboard: Top 3 Users
    # -------------------------
    st.subheader("Top 3 Scores Overall")
    top_scores = supabase.table("test_results").select("user_id, score").order("score", desc=True).limit(3).execute().data
    top_list = []
    for t in top_scores:
        user = next(u for u in users_data if u['id'] == t['user_id'])
        top_list.append({"username": user['username'], "score": t['score']})
    if top_list:
        st.table(pd.DataFrame(top_list))
    else:
        st.info("No scores yet.")

