import streamlit as st
import random
import re

# Custom styling for high-density mobile views and theme adaptability
st.markdown("""
<style>
/* Healthy top padding to push content comfortably down past the browser ceiling */
.block-container {
    padding-top: 5rem !important;
    padding-bottom: 1rem !important;
}
/* Clean, non-intrusive Start Page Title */
.start-title {
    font-size: 32px !important;
    font-weight: bold;
    text-align: center;
    margin-bottom: 5px;
}
.start-subtitle {
    font-size: 16px;
    text-align: center;
    opacity: 0.8;
    margin-bottom: 25px;
}
/* Aesthetically uniform progress tracker header */
.progress-header {
    font-size: 16px !important;
    font-weight: 500;
    text-align: left;
    margin-bottom: 0px !important;
    opacity: 0.8;
}
/* Beautifully compact question text to prevent scrolling */
.english-question {
    font-size: 19px !important;
    font-weight: bold;
    text-align: center;
    margin: 10px 0 !important;
}
/* Make choice lists matching and clear */
div[data-testid="stMarkdownContainer"] p {
    font-size: 19px !important;
}
/* Center the Begin Quiz button */
div.stButton button[key="start_game_btn"] {
    margin: 0 auto !important;
    display: block !important;
}
/* Styling to make the custom button row look pristine and uniform */
.custom-btn-container {
    display: flex;
    gap: 10px;
    width: 100%;
    margin-top: 10px;
}
/* Minimize inner system padding gaps */
[data-testid="stVerticalBlock"] {
    gap: 0.4rem !important;
}
hr {
    margin: 8px 0 !important;
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
    
    # Robust multi-line/whitespace flexible regex pattern matching the modern block layouts
    pattern = r"-\s+\*\*([^*]+)\s+\(([^)]+)\)\*\*(?:\s+-\s+)?_The Surface Word:_\s+([^_]+)\s+\(([^/]+)/\s*\"([^\"]+)\"\)(?:\s+-\s+)?_Phonetic Pronunciation:_\s+\*\*([^*]+)\*\*(?:\s+-\s+)?_The Raw Root Meaning:_\s+\*\*([^*]+?)\*\*(?=\n-|\n\n|\Z)"
    matches = re.findall(pattern, content, flags=re.DOTALL)
    
    for r_heb, r_eng, s_heb, s_trans, s_mean, phon, r_mean in matches:
        root_hebrew = r_heb.strip()
        root_english = r_eng.strip()
        surface_hebrew = s_heb.strip()
        surface_translit = s_trans.strip()
        surface_meaning = s_mean.strip()
        phonetic = phon.strip()
        root_meaning = r_mean.strip()
        
        # Strip out loose inline markdown formatting leaks if any exist within raw variables
        surface_meaning = surface_meaning.replace('"', '').replace('_', '')
        root_meaning = root_meaning.rstrip('. ')
        
        full_root_string = root_hebrew
        quiz_items.append({
            "english_meaning": surface_meaning,
            "correct_root": full_root_string,
            "transliteration": surface_translit,
            "surface_word": surface_hebrew,
            "hint": f"The word from the Hebrew text is transliterated as: \n✨ **{surface_translit}**",
            "explanation": f"The root is {full_root_string} ({root_english}), which means '{root_meaning}'. It appeared in the text as the surface word '{surface_hebrew}' ({surface_translit})."
        })
    return quiz_items

# --- INITIALIZE SESSION STATE ---
if "quiz_data" not in st.session_state:
    RAW_DATA = parse_hebrew_markdown("GenesisRootWordLexicon1.md")
    
    # 1. First randomize the entire lexicon dataset
    random.shuffle(RAW_DATA)
    
    # 2. Slice to limit the active session to exactly 33 items (or less if file size is small)
    RAW_DATA = RAW_DATA[:33]
    
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
if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False

QUIZ_DATA = st.session_state.quiz_data

# --- APP LAYOUT RUNNER ---
if not QUIZ_DATA:
    st.error("Could not find or match entries in the lexicon file. Make sure GenesisRootWordLexicon1.md is formatted correctly and in the same directory!")

# 1. THE LANDING PAGE SPLASH SCREEN
elif not st.session_state.quiz_started:
    st.write("")
    st.markdown('<div class="start-title">📖 Genesis Chapter 1<br>Root Recall</div>', unsafe_allow_html=True)
    st.markdown('<div class="start-subtitle">Look at the English meaning and select the correct hidden Hebrew Root word from the choices below. Extract the three-letter Shoresh out of the verse surface text.</div>', unsafe_allow_html=True)
    
    if st.button("🚀 Begin Quiz", key="start_game_btn"):
        st.session_state.quiz_started = True
        st.rerun()

# 2. THE ACTIVE INTERACTIVE QUIZ ENGINE
elif st.session_state.current_index < len(QUIZ_DATA):
    current_q = QUIZ_DATA[st.session_state.current_index]
    
    st.markdown(f'<div class="progress-header">📊 Question {st.session_state.current_index + 1} of {len(QUIZ_DATA)} | Correct: {st.session_state.score}</div>', unsafe_allow_html=True)
    st.divider()
    
    # Question Card
    st.markdown(f'<div class="english-question">What is the Hebrew root for the word translated as: <br>🔍 "{current_q["english_meaning"]}"</div>', unsafe_allow_html=True)
    
    main_col1, main_col2 = st.columns(2)
    
    with main_col1:
        choice = st.radio("", current_q["options"], key=f"radio_{st.session_state.current_index}", label_visibility="collapsed")
        submit_disabled = st.session_state.answered
        
        btn_cols = st.columns()
        with btn_cols:
            if st.button("Submit", disabled=submit_disabled, key=f"sub_{st.session_state.current_index}"):
                st.session_state.selected_option = choice
                st.session_state.answered = True
                if choice == current_q["correct_root"]:
                    st.session_state.score += 1
                st.rerun()
                
        with btn_cols:
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

# 3. END GAME VIEW
else:
    st.balloons()
    st.title("🎉 Quiz Complete!")
    st.success("You finished the vocabulary list!")
    st.metric(label="Final Score", value=f"{st.session_state.score} / {len(QUIZ_DATA)}")
    
    if st.button("🔄 Restart"):
        st.session_state.current_index = 0
        st.session_state.score = 0
        st.session_state.answered = False
        st.session_state.selected_option = None
        st.session_state.quiz_started = False
        if "quiz_data" in st.session_state:
            del st.session_state.quiz_data
        st.rerun()
