"""Export the Python model's top five matches for the Vercel browser demo."""
import json
from pathlib import Path

import pandas as pd

from recommender import BookRecommender

ROOT = Path(__file__).resolve().parent


def main():
    artifacts = ROOT / "artifacts"
    metadata = pd.read_pickle(artifacts / "final_rating.pkl")
    ratings = pd.read_pickle(artifacts / "book_pivot.pkl")
    recommender = BookRecommender(ratings, metadata)

    isbns = metadata["ISBN"].astype(str).str.strip().str.upper()
    valid_isbns = isbns.str.fullmatch(r"(?:[0-9]{9}[0-9X]|[0-9]{13})")
    editions = metadata.assign(ISBN=isbns).loc[valid_isbns]
    counts = editions.groupby(["title", "ISBN"]).size().reset_index(name="ratings")
    preferred = counts.sort_values(
        ["ratings", "ISBN"], ascending=[False, True]
    ).drop_duplicates("title")
    cover_isbns = dict(zip(preferred["title"], preferred["ISBN"]))

    catalog = []
    for title in recommender.titles:
        matches = [
            [recommender.positions[match], recommender.shared_explicit_ratings(title, match)]
            for match in recommender.recommend(title)
        ]
        catalog.append([
            title, str(recommender.authors.get(title, "")), cover_isbns.get(title, ""), matches
        ])

    output = ROOT / "vercel-demo" / "catalog.json"
    output.write_text(json.dumps(catalog, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


if __name__ == "__main__":
    main()
