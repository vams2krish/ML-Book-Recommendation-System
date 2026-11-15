from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st

from recommender import BookRecommender

ROOT = Path(__file__).resolve().parent

st.set_page_config(page_title="Next Chapter | Book Discovery", page_icon="📚")
st.html(str(ROOT / "styles.css"))


@st.cache_resource
def load_catalog():
    data = ROOT / "artifacts"
    return BookRecommender(
        pd.read_pickle(data / "book_pivot.pkl"),
        pd.read_pickle(data / "final_rating.pkl"),
    )


def render_cards(titles, catalog):
    cards = []
    for rank, title in enumerate(titles, 1):
        safe_title = escape(title)
        author = escape(str(catalog.authors.get(title, "Author unavailable")))
        initial = escape(title.strip()[:1].upper())
        cards.append(f"""
            <li class="book-card">
                <div class="book-art tone-{(rank - 1) % 5}" aria-hidden="true">
                    <span class="book-initial">{initial}</span>
                    <span class="book-rank">{rank:02d}</span>
                </div>
                <div class="book-copy"><h3>{safe_title}</h3><p>{author}</p></div>
            </li>""")
    st.html('<ol class="book-grid">' + "".join(cards) + "</ol>")


try:
    catalog = load_catalog()
except (OSError, ValueError, ImportError, KeyError):
    st.error("The book catalog could not be loaded. Check that the included data files and dependencies are installed.")
    st.stop()

st.html(f"""
    <div class="masthead"><span>◈ &nbsp; NEXT CHAPTER</span>
    <span class="catalog-count">{len(catalog.titles):,} BOOKS TO EXPLORE</span></div>
    <div class="hero">
        <div class="eyebrow">THE READING ROOM</div>
        <h1>Find your<br><em>next chapter.</em></h1>
        <p>Start with a book you enjoyed. Discover what to read next based on how readers rated it and other books.</p>
    </div>
""")
with st.form("discovery", border=False):
    selected = st.selectbox("Start with a book", sorted(catalog.titles, key=str.casefold),
                            index=None, placeholder="Search by book title")
    submitted = st.form_submit_button("Find similar books →", type="primary")

if submitted:
    if selected is None:
        st.warning("Choose a book to see recommendations.")
    else:
        st.session_state["seed_title"] = selected

seed = st.session_state.get("seed_title")
if seed:
    matches = catalog.recommend(seed)
    st.html(f"""
        <div class="section-label">YOUR READING LIST &nbsp; / &nbsp; {len(matches):02d} MATCHES</div>
        <h2 class="section-title">If you liked <em>{escape(seed)}</em></h2>
    """)
    if matches:
        render_cards(matches, catalog)
    else:
        st.info("There are no other books in this catalog.")
else:
    st.html("""
        <div class="empty-list"><div class="section-label">THE NEXT FIVE</div>
        <h2>Your reading list starts here.</h2>
        <p>Pick a title above to discover five books with similar reader ratings.</p></div>
    """)

st.html('<div class="app-footer"><span>◈ NEXT CHAPTER</span><span>POWERED BY BOOK-CROSSING RATINGS</span></div>')
