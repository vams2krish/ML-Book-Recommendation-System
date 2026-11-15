const find = (selector) => document.querySelector(selector);
const input = find("#title");
const status = find("#status");
const shelf = find(".book-grid");

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text) node.textContent = text;
  return node;
}

function showBooks(books, entries) {
  shelf.replaceChildren(...entries.map(([index, overlap], rank) => {
    const [title, author, isbn] = books[index];
    const card = element("li", "book-card");
    const artwork = element("div", `book-art tone-${rank % 5}`);
    artwork.setAttribute("aria-hidden", "true");
    artwork.append(element("span", "book-initial", title[0]));
    if (isbn) {
      const image = element("span", "cover-image");
      image.style.backgroundImage = `url(https://covers.openlibrary.org/b/isbn/${isbn}-M.jpg?default=false)`;
      artwork.append(image);
    }
    const copy = element("div", "book-copy");
    copy.append(element("h3", "", title), element("p", "", author || "Author unavailable"));
    if (overlap !== undefined) {
      const details = element("details", "book-reason");
      const shared = overlap === 0
        ? "No readers gave both books a score in this dataset."
        : `${overlap} ${overlap === 1 ? "reader" : "readers"} gave both books a score.`;
      details.append(element("summary", "", "Why this book?"),
        element("p", "", `Its rating pattern was among the five closest to your chosen book. ${shared}`));
      copy.append(details);
    }
    card.append(artwork, copy);
    return card;
  }));
}

try {
  const response = await fetch("./catalog.json");
  if (!response.ok) throw new Error("Catalog unavailable");
  const books = await response.json();
  const titles = new Map(books.map(([title], index) => [title, index]));
  find("#count").textContent = `${books.length} BOOKS TO EXPLORE`;
  find("#titles").append(...books.map(([title]) => element("option", "", title)));
  const featured = ["1984", "The Da Vinci Code", "The Lovely Bones: A Novel", "The Secret Life of Bees", "Life of Pi"];
  showBooks(books, featured.filter(title => titles.has(title)).map(title => [titles.get(title)]));
  find("form").addEventListener("submit", (event) => {
    event.preventDefault();
    const index = titles.get(input.value.trim());
    if (index === undefined) {
      status.textContent = "Choose a title from the catalog.";
      return;
    }
    status.textContent = "";
    find("#heading").textContent = `If you liked ${books[index][0]}`;
    find("#note").hidden = false;
    showBooks(books, books[index][3]);
  });
  input.disabled = false;
  find("button").disabled = false;
} catch {
  status.textContent = "The catalog could not load. Refresh the page to try again.";
}
