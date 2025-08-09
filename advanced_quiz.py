# Install packages before running:
# pip install streamlit streamlit-lottie requests

import streamlit as st
from streamlit_lottie import st_lottie
import requests
import time
import threading

# Load Lottie animations from URL
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Confetti animation for celebration
lottie_confetti = load_lottieurl("https://assets2.lottiefiles.com/packages/lf20_jbrw3hcz.json")
# Welcome animation
lottie_welcome = load_lottieurl("https://assets1.lottiefiles.com/packages/lf20_UJNc2t.json")

# Define quiz questions with different types and explanations
quiz = [
    {
        "type": "mcq",
        "question": "What is the capital of India?",
        "options": ["Mumbai", "Delhi", "Kolkata", "Chennai"],
        "answer": "Delhi",
        "explanation": "Delhi is the capital city of India, known for its historical landmarks."
    },
    {
        "type": "checkbox",
        "question": "Select the prime numbers:",
        "options": ["2", "3", "4", "9", "11"],
        "answer": ["2", "3", "11"],
        "explanation": "Prime numbers are numbers that are divisible only by 1 and themselves."
    },
    {
        "type": "text",
        "question": "Who developed the theory of relativity? (Type full name)",
        "answer": "Albert Einstein",
        "explanation": "Albert Einstein formulated the theory of relativity, revolutionizing physics."
    },
    {
        "type": "mcq",
        "question": "Which planet is known as the Red Planet?",
        "options": ["Earth", "Venus", "Mars", "Jupiter"],
        "answer": "Mars",
        "explanation": "Mars is called the Red Planet due to the iron oxide on its surface."
    },
]

st.set_page_config(page_title="🚀 Advanced Interactive Quiz", page_icon="🧠", layout="centered")

# Dark/Light mode toggle
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

def toggle_mode():
    st.session_state.dark_mode = not st.session_state.dark_mode

mode_text = "Switch to Dark Mode" if not st.session_state.dark_mode else "Switch to Light Mode"
st.sidebar.button(mode_text, on_click=toggle_mode)

# Styling based on mode
if st.session_state.dark_mode:
    bg_color = "#121212"
    text_color = "#f0f0f0"
    btn_color = "#bb86fc"
    btn_hover = "#9f6ef2"
else:
    bg_color = "#ffffff"
    text_color = "#000000"
    btn_color = "#8c52ff"
    btn_hover = "#6b35cc"

st.markdown(f"""
    <style>
    body {{
        background-color: {bg_color};
        color: {text_color};
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    .quiz-container {{
        background: {'#2c2c2c' if st.session_state.dark_mode else '#f0f2f6'};
        border-radius: 20px;
        padding: 30px;
        max-width: 650px;
        margin: auto;
        box-shadow: 0 12px 36px rgba(0,0,0,0.12);
    }}
    .option-button {{
        width: 100%;
        margin: 8px 0;
        font-size: 18px;
        padding: 15px;
        border-radius: 15px;
        background-color: {btn_color};
        color: white;
        border: none;
        transition: background-color 0.3s ease;
        font-weight: 600;
    }}
    .option-button:hover {{
        background-color: {btn_hover};
        cursor: pointer;
    }}
    .correct {{
        background-color: #28a745 !important;
    }}
    .incorrect {{
        background-color: #dc3545 !important;
    }}
    .explanation {{
        font-style: italic;
        margin-top: 15px;
        padding: 12px;
        background-color: {'#3a3a3a' if st.session_state.dark_mode else '#e0e0e0'};
        border-radius: 12px;
        color: {'#dcdcdc' if st.session_state.dark_mode else '#333'};
    }}
    .scoreboard {{
        max-width: 650px;
        margin: auto;
        padding: 20px;
        background-color: {'#2c2c2c' if st.session_state.dark_mode else '#fefefe'};
        border-radius: 20px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.1);
        color: {text_color};
    }}
    </style>
""", unsafe_allow_html=True)

st.title("🧠 Advanced Interactive Quiz")
st_lottie(lottie_welcome, height=180)

if "score" not in st.session_state:
    st.session_state.score = 0
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
if "answered" not in st.session_state:
    st.session_state.answered = False
if "selected" not in st.session_state:
    st.session_state.selected = None
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "time_left" not in st.session_state:
    st.session_state.time_left = 20  # 20 seconds per question default

def reset_quiz():
    st.session_state.score = 0
    st.session_state.q_index = 0
    st.session_state.answered = False
    st.session_state.selected = None
    st.session_state.time_left = 20
    st.session_state.start_time = None

def calculate_grade(percentage):
    if percentage >= 90:
        return "A+ (Excellent)"
    elif percentage >= 75:
        return "A (Very Good)"
    elif percentage >= 60:
        return "B (Good)"
    elif percentage >= 50:
        return "C (Average)"
    else:
        return "F (Needs Improvement)"

def show_timer():
    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()
    elapsed = int(time.time() - st.session_state.start_time)
    remaining = max(0, 20 - elapsed)
    st.session_state.time_left = remaining
    st.progress(remaining / 20)

    if remaining == 0 and not st.session_state.answered:
        st.write("⏰ Time's up! Moving to next question...")
        time.sleep(1.5)
        next_question()

def next_question():
    st.session_state.q_index += 1
    st.session_state.answered = False
    st.session_state.selected = None
    st.session_state.start_time = None
    st.session_state.time_left = 20

def check_answer(q, user_answer):
    correct = False
    if q["type"] == "mcq":
        correct = user_answer == q["answer"]
    elif q["type"] == "checkbox":
        correct = set(user_answer) == set(q["answer"])
    elif q["type"] == "text":
        correct = user_answer.strip().lower() == q["answer"].lower()
    return correct

def play_sound(correct):
    # Play sound effect for correct or wrong answer (optional)
    if correct:
        audio_html = """
        <audio autoplay>
          <source src="https://actions.google.com/sounds/v1/cartoon/clang_and_wobble.ogg" type="audio/ogg">
        </audio>"""
    else:
        audio_html = """
        <audio autoplay>
          <source src="https://actions.google.com/sounds/v1/cartoon/cartoon_boing.ogg" type="audio/ogg">
        </audio>"""
    st.markdown(audio_html, unsafe_allow_html=True)

# Main quiz logic
with st.container():
    if st.session_state.q_index < len(quiz):
        question = quiz[st.session_state.q_index]
        st.markdown('<div class="quiz-container">', unsafe_allow_html=True)
        st.subheader(f"Q{st.session_state.q_index + 1}: {question['question']}")

        show_timer()

        if not st.session_state.answered:
            # Different input types per question
            if question["type"] == "mcq":
                for opt in question["options"]:
                    if st.button(opt, key=opt):
                        st.session_state.selected = opt
                        st.session_state.answered = True
                        is_correct = check_answer(question, opt)
                        if is_correct:
                            st.session_state.score += 1
                        play_sound(is_correct)
            elif question["type"] == "checkbox":
                selected_opts = st.multiselect("Select all that apply:", question["options"])
                if st.button("Submit Answer"):
                    st.session_state.selected = selected_opts
                    st.session_state.answered = True
                    is_correct = check_answer(question, selected_opts)
                    if is_correct:
                        st.session_state.score += 1
                    play_sound(is_correct)
            elif question["type"] == "text":
                user_input = st.text_input("Type your answer here:")
                if st.button("Submit Answer") and user_input.strip() != "":
                    st.session_state.selected = user_input.strip()
                    st.session_state.answered = True
                    is_correct = check_answer(question, user_input)
                    if is_correct:
                        st.session_state.score += 1
                    play_sound(is_correct)

        else:
            # Show results & explanation
            if question["type"] == "checkbox":
                user_ans_display = ", ".join(st.session_state.selected) if st.session_state.selected else "No Answer"
                correct_ans_display = ", ".join(question["answer"])
            else:
                user_ans_display = st.session_state.selected if st.session_state.selected else "No Answer"
                correct_ans_display = question["answer"]

            is_correct = check_answer(question, st.session_state.selected)

            st.markdown(f"""
                <button class="option-button {'correct' if is_correct else 'incorrect'}" disabled>{user_ans_display}</button>
                <p><b>Correct Answer:</b> {correct_ans_display}</p>
                <div class="explanation">{question['explanation']}</div>
            """, unsafe_allow_html=True)

            if st.session_state.q_index < len(quiz) - 1:
                if st.button("Next Question ➡️"):
                    next_question()
            else:
                st.success(f"🎉 Quiz Completed! Your Score: {st.session_state.score} / {len(quiz)}")
                percentage = (st.session_state.score / len(quiz)) * 100
                grade = calculate_grade(percentage)
                st.balloons()
                st_lottie(lottie_confetti, height=250)

                # Score summary with tabs
                tabs = st.tabs(["Summary", "Details"])
                with tabs[0]:
                    st.markdown(f"""
                        <div class="scoreboard">
                        <h3>Your Grade: {grade}</h3>
                        <p>Percentage: {percentage:.2f}%</p>
                        <p>Total Questions: {len(quiz)}</p>
                        <p>Correct Answers: {st.session_state.score}</p>
                        <p>Incorrect Answers: {len(quiz) - st.session_state.score}</p>
                        </div>
                    """, unsafe_allow_html=True)
                with tabs[1]:
                    for idx, q in enumerate(quiz):
                        st.markdown(f"**Q{idx+1}:** {q['question']}")
                        correct_ans = q["answer"] if isinstance(q["answer"], str) else ', '.join(q["answer"])
                        st.markdown(f"- Correct Answer: {correct_ans}")
                        user_ans = st.session_state.selected if idx == st.session_state.q_index else "-"
                        st.markdown(f"- Your Answer: {user_ans}")
                        st.markdown("---")

                if st.button("Restart Quiz 🔄"):
                    reset_quiz()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.write("Thanks for playing the quiz!")

# Show progress bar at bottom
progress = (st.session_state.q_index + (1 if st.session_state.answered else 0)) / len(quiz)
st.progress(progress)
