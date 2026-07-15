"""Optional web UI for the Owkin assistant.

Run with:  streamlit run streamlit_app.py
It reuses the same agent as the command-line app.
"""

import os

import streamlit as st
from dotenv import load_dotenv

from src.agent import build_agent

load_dotenv()

st.set_page_config(page_title="Owkin gene-expression assistant", page_icon="🧬")


@st.cache_resource
def get_agent(force_offline: bool):
    return build_agent(force_rule=force_offline)


has_key = bool(os.environ.get("ANTHROPIC_API_KEY"))

# AI mode is only possible when a key is present. When a key exists, offer a
# toggle so you can still demo the offline behaviour.
if has_key:
    force_offline = st.sidebar.checkbox(
        "Offline mode (no AI)",
        value=False,
        help="When on, uses the rule-based agent instead of Claude.",
    )
else:
    st.sidebar.info("No API key found - running in offline mode. Add a key to enable AI mode.")
    force_offline = True

use_llm = has_key and not force_offline
agent = get_agent(not use_llm)
mode = "Claude (LLM mode)" if use_llm else "Offline mode"

st.title("🧬 Owkin gene-expression assistant")
st.caption(f"Ask about genes and expression values in the dataset. Running in: {mode}")

question = st.text_input(
    "Your question",
    value="What are the main genes involved in lung cancer?",
)

if st.button("Ask", type="primary") and question.strip():
    with st.spinner("Thinking..."):
        answer = agent.ask(question)
    st.markdown(answer)

st.caption(
    "Each question is answered on its own (no chat memory), "
    "so just type your next question in the box above."
)

st.divider()
st.write("Try one of these:")
examples = [
    "How can you help me?",
    "What are the main genes involved in lung cancer?",
    "What is the median expression of genes involved in breast cancer?",
    "What is the median expression of genes involved in esophageal cancer?",
]

# These show off what the LLM can do beyond simple keyword matching, so they
# only really work well in Claude (LLM) mode.
llm_examples = [
    "Which gene has the highest expression in prostate cancer?",
    "Compare the genes involved in lung and breast cancer.",
    "For melanoma, list only the genes with expression above 0.5.",
    "whats imprtant in beast cancr",  # handles typos / loose phrasing
    "Give me the top 3 highest-expression genes in renal cancer.",
]

for ex in examples:
    if st.button(ex):
        with st.spinner("Thinking..."):
            answer = agent.ask(ex)
        st.markdown(answer)

if use_llm:
    st.divider()
    st.write("These need AI mode (an API key):")
    for ex in llm_examples:
        if st.button(ex):
            with st.spinner("Thinking..."):
                answer = agent.ask(ex)
            st.markdown(answer)
