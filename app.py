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
    metadata = pd.read_pickle(data / "final_rating.pkl")
    catalog = BookRecommender(pd.read_pickle(data / "book_pivot.pkl"), metadata)
    isbns = metadata["ISBN"].astype(str).str.strip().str.upper()
    valid = metadata.assign(ISBN=isbns)[isbns.str.fullmatch(r"(?:[0-9]{9}[0-9X]|[0-9]{13})")]
    editions = valid.groupby(["title", "ISBN"]).size().reset_index(name="ratings")
    preferred = editions.sort_values(["ratings", "ISBN"], ascending=[False, True]).drop_duplicates("title")
    return catalog, dict(zip(preferred["title"], preferred["ISBN"]))


def render_cards(titles, catalog, isbns):
    cards = []
    for rank, title in enumerate(titles, 1):
        safe_title = escape(title)
        author = escape(str(catalog.authors.get(title, "Author unavailable")))
        initial = escape(title.strip()[:1].upper())
        isbn = isbns.get(title)
        cover = ""
        if isbn:
            url = f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg?default=false"
            cover = f'<span class="cover-image" style="background-image:url({url})"></span>'
        cards.append(f"""
            <li class="book-card">
                <div class="book-art tone-{(rank - 1) % 5}" aria-hidden="true">
                    <span class="book-initial">{initial}</span>
                    {cover}
                </div>
                <div class="book-copy"><h3>{safe_title}</h3><p>{author}</p></div>
            </li>""")
    st.html('<ol class="book-grid">' + "".join(cards) + "</ol>")


try:
    catalog, isbns = load_catalog()
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
        render_cards(matches, catalog, isbns)
    else:
        st.info("There are no other books in this catalog.")
else:
    st.html('<h2 class="section-title">Explore the catalog</h2>')
    featured = ("1984", "The Da Vinci Code", "The Lovely Bones: A Novel",
                "The Secret Life of Bees", "Life of Pi")
    render_cards([title for title in featured if title in catalog.positions], catalog, isbns)

st.html('<div class="app-footer"><span>◈ NEXT CHAPTER</span><span>BOOK-CROSSING RATINGS · <a href="https://openlibrary.org/dev/docs/api/covers">Covers by Open Library</a></span></div>')
