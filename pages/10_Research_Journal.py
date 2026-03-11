"""
Research Journal — markdown notes with AI-suggested next steps.
"""
import streamlit as st
import pandas as pd
from datetime import datetime

from data.store import get_connection
from ai.client import chat

st.set_page_config(page_title="Research Journal — AlphaForge", layout="wide")
st.title("Research Journal")

JOURNAL_AI_SYSTEM = """You are a quantitative research assistant. 
The user maintains a research journal about Indian equity factor investing.
Based on their recent journal entries, suggest 3-5 specific research directions or analyses 
they should explore next. Be specific and actionable. Reference their actual observations."""

# ---- New Entry ----
with st.expander("Write New Entry", expanded=False):
    title = st.text_input("Title")
    content = st.text_area("Notes (supports markdown)", height=200,
                            placeholder="e.g. Momentum factor underperformed in Q3 2023, "
                                        "especially in IT sector. Worth investigating...")
    tags = st.text_input("Tags (comma-separated)", placeholder="momentum, IT, underperformance")
    if st.button("Save Entry", type="primary"):
        if title and content:
            conn = get_connection()
            conn.execute("""
                INSERT INTO research_journal (created_at, title, content, tags)
                VALUES (?, ?, ?, ?)
            """, (datetime.now().isoformat(), title, content, tags))
            conn.commit()
            conn.close()
            st.success("Entry saved!")
            st.rerun()

# ---- Load Entries ----
conn = get_connection()
entries = pd.read_sql(
    "SELECT * FROM research_journal ORDER BY created_at DESC", conn
)
conn.close()

if entries.empty:
    st.info("No journal entries yet. Start writing your research observations.")
    st.stop()

col_left, col_right = st.columns([2, 1])

with col_left:
    # Tag filter
    all_tags = set()
    for t in entries["tags"].dropna():
        for tag in t.split(","):
            all_tags.add(tag.strip())
    selected_tag = st.selectbox("Filter by tag", ["All"] + sorted(all_tags))

    filtered = entries if selected_tag == "All" else entries[
        entries["tags"].str.contains(selected_tag, na=False)
    ]

    st.subheader(f"{len(filtered)} Entries")
    for _, row in filtered.iterrows():
        with st.container():
            date_str = pd.Timestamp(row["created_at"]).strftime("%d %b %Y")
            st.markdown(f"**{row['title']}** — *{date_str}*")
            if row["tags"]:
                for tag in str(row["tags"]).split(","):
                    st.markdown(f"`{tag.strip()}`", unsafe_allow_html=False)
            st.markdown(row["content"])
            st.divider()

with col_right:
    st.subheader("AI Research Suggestions")
    st.caption("Based on your journal entries")

    if st.button("Get AI Suggestions", type="primary"):
        recent = entries.head(5)
        context = "\n\n".join([
            f"Entry: {row['title']}\n{row['content']}"
            for _, row in recent.iterrows()
        ])
        with st.spinner("Generating suggestions..."):
            suggestions = chat(JOURNAL_AI_SYSTEM, context, max_tokens=800)
        st.session_state.journal_suggestions = suggestions

    if "journal_suggestions" in st.session_state:
        st.markdown(st.session_state.journal_suggestions)
