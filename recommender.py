"""Book retrieval and catalog metadata."""
from sklearn.neighbors import NearestNeighbors


class BookRecommender:
    def __init__(self, ratings, metadata):
        self.titles = tuple(ratings.index)
        self.positions = {title: i for i, title in enumerate(self.titles)}
        self.vectors = ratings.to_numpy(dtype=float)
        authors = metadata.dropna(subset=["author"]).drop_duplicates("title")
        self.authors = dict(zip(authors["title"], authors["author"]))
        self.model = NearestNeighbors(algorithm="brute").fit(self.vectors)

    def recommend(self, title, limit=5):
        """Return at most limit distinct alternatives, nearest first."""
        if title not in self.positions:
            raise ValueError(f"Unknown title: {title}")
        if limit <= 0:
            return []
        source = self.positions[title]
        distances, indices = self.model.kneighbors(
            self.vectors[[source]], n_neighbors=len(self.titles)
        )
        ordered = sorted(zip(distances[0], indices[0]), key=lambda pair: (
            pair[0], self.titles[pair[1]].casefold(), pair[1]
        ))
        return [self.titles[i] for _, i in ordered if i != source][:limit]
