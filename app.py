import streamlit as st
import random
import re

# Custom styling that respects the user's local system preferences (Light vs Dark Mode)
st.markdown("""
    <style>
    /* Relaxed top padding for a comfortable header margin */
    .block-container {
        padding-top: 5rem !important;
        padding-bottom: 1rem !important;
    }
    /* Compact Header */
    h1 {
        margin-bottom: 0px !important;
        padding-bottom: 0px !important;
        font-size: 28px !important;
    }
    /* English Question Styling */
    .english-question { 
        font-size: 22px !important; 
        font-weight: bold; 
        text-align: center; 
        margin: 12px 0 !important; 
    }
    /* Make the radio button Hebrew choices large and crisp */
    div[data-testid="stMarkdownContainer"] p { font-size: 20px !important; }
    .stButton button { width: 100%; }
    
    /* Minimize spacing inside the columns */
    [data-testid="stVerticalBlock"] {
        gap: 0.5rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- ADVANCED MARKDOWN PARSER (CLOUD VERSION) ---
def parse_hebrew_markdown(file_path):
    quiz_items = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        return []

    pattern = r"-\s+\*\*([^*]+)\s+\(([^)]+)\)\*\*\s+-\s+_The Surface Word:_\s+([^_]+)\s+\(([^/]+)/\s*\"([^\"]+)\"\)\s+-\s+_Phonetic Pronunciation:_\s+\*\*([^*]+)\*\*\s+-\s+_The Raw Root Meaning:_\s+\*\*([^*]+)\*\*"
    matches = re.findall(pattern, content)
    
    for match in matches:
        # FIXED: Correctly unpacking each individual item from the tuple package one by one
        root_hebrew = match[0].strip()
        root_english = match[1].strip()
        surface_hebrew = match[2].strip()
        surface_translit = match[3].strip()
        surface_meaning = match[4].strip()
        phonetic = match[5].strip()
        root_meaning = match[6].strip()
        
        full_root_string = root_hebrew
        
        quiz_items.append({
            "english_meaning": surface_meaning,
            "correct_root": full_root_string,
            "transliteration": surface_translit,
            "surface_word": surface_hebrew,
            "hint": f"The word from the Hebrew text is transliterated as:  \n✨ **{surface_translit}**",
            "explanation": f"The root is {full_root_string} ({root_english}), which means '{root_meaning}'. It appeared in the text as the surface word '{surface_hebrew}' ({surface_translit})."
        })
    return quiz_items

# --- INITIALIZE SESSION STATE ---
if "quiz_data" not in st.session_state:
    RAW_DATA = parse_hebrew_markdown("GenesisRootWordLexicon1.md")
    random.shuffle(RAW_DATA)
    
    QUIZ_DATA = []
    all_roots = [item["correct_root"] for item in RAW_DATA]

    for item in RAW_DATA:
        wrong_pool = [r for r in all_roots if r != item["correct_root"]]
        num_options = min(3, len(wrong_pool))
        wrong_choices = random.sample(wrong_pool, num_options)
        
        options = wrong_choices + [item["correct_root"]]
        random.shuffle(options)
        
        quiz_item = item.copy()
        quiz_item["options"] = options
        QUIZ_DATA.append(quiz_item)
        
    st.session_state.quiz_data = QUIZ_DATA

if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "selected_option" not in st.session_state:
    st.session_state.selected_option = None
if "answered" not in st.session_state:
    st.session_state.answered = False

# --- STREAMLIT UI ENGINE ---
st.title("📖 Genesis Chapter 1 Root Recall")
st.caption("Select the correct hidden Hebrew Root based on the English meaning.")

QUIZ_DATA = st.session_state.quiz_data

if not QUIZ_DATA:
    st.error("Could not find the lexicon file. Make sure GenesisRootWordLexicon1.md is in the same folder as app.py!")
elif st.session_state.current_index < len(QUIZ_DATA):
    current_q = QUIZ_DATA[st.session_state.current_index]
    
    st.caption(f"Question {st.session_state.current_index + 1} of {len(QUIZ_DATA)} | Score: {st.session_state.score}")
    
    # Question Card
    st.markdown(f'<div class="english-question">What is the Hebrew root for the word translated as: <br>🔍 "{current_q["english_meaning"]}"</div>', unsafe_allow_html=True)
    
    main_col1, main_col2 = st.columns(2)
    
    with main_col1:
        choice = st.radio("Select the correct Hebrew Root word:", current_q["options"], key=f"radio_{st.session_state.current_index}")
        
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            submit_disabled = st.session_state.answered
            if st.button("Submit", disabled=submit_disabled, key=f"sub_{st.session_state.current_index}"):
                st.session_state.selected_option = choice
                st.session_state.answered = True
                if choice == current_q["correct_root"]:
                    st.session_state.score += 1
                st.rerun()
                
        with btn_col2:
            if st.session_state.answered:
                if st.button("Next Word ➡️", key=f"next_{st.session_state.current_index}"):
                    st.session_state.current_index += 1
                    st.session_state.answered = False
                    st.session_state.selected_option = None
                    st.rerun()

    with main_col2:
        if st.session_state.answered:
            if st.session_state.selected_option == current_q["correct_root"]:
                st.success(f"✨ Correct!\n\n{current_q['explanation']}")
            else:
                st.error(f"❌ Not quite.\n\n{current_q['explanation']}")
        else:
            with st.expander("💡 Reveal Surface Word Hint", expanded=False):
                st.info(current_q["hint"])
else:
    st.balloons()
    st.success("🎉 You finished the vocabulary list!")
    st.metric(label="Final Score", value=f"{st.session_state.score} / {len(QUIZ_DATA)}")
    
    if st.button("🔄 Restart"):
        st.session_state.current_index = 0
        st.session_state.score = 0
        st.session_state.answered = False
        st.session_state.selected_option = None
        del st.session_state.quiz_data
        st.rerun()
