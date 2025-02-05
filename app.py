from flask import Flask, render_template_string, Response
import os
import requests

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Standard Works Scripture Copier</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    label, select, input { margin-right: 10px; }
    #scripture-text { width: 100%; height: 300px; margin-top: 20px; padding: 10px; font-size: 14px; }
    button { padding: 10px; font-size: 16px; }
  </style>
</head>
<body>
  <h1>Standard Works Scripture Copier</h1>
  
  <label for="volume">Select Volume:</label>
  <select id="volume">
    <option value="bible">Bible</option>
    <option value="bookofmormon">Book of Mormon</option>
    <option value="doctrineandcovenants">Doctrine and Covenants</option>
    <option value="pearlofgreatprice">Pearl of Great Price</option>
  </select>
  
  <label for="book">Select Book:</label>
  <select id="book">
    <!-- Options populated via JavaScript -->
  </select>
  
  <label for="start-chapter">Start Chapter:</label>
  <input type="number" id="start-chapter" value="1" min="1">
  
  <label for="end-chapter">End Chapter (optional):</label>
  <input type="number" id="end-chapter" min="1">
  
  <button id="fetch-scripture-btn">Fetch Scripture</button>
  <button id="copy-btn">Copy to Clipboard</button>
  
  <textarea id="scripture-text" readonly></textarea>
  
  <script>
    // Define the books for each volume.
    const booksByVolume = {
      "bible": [
        { value: "genesis", text: "Genesis" },
        { value: "exodus", text: "Exodus" },
        { value: "leviticus", text: "Leviticus" },
        { value: "numbers", text: "Numbers" },
        { value: "deuteronomy", text: "Deuteronomy" },
        { value: "joshua", text: "Joshua" },
        { value: "judges", text: "Judges" },
        { value: "ruth", text: "Ruth" },
        { value: "1samuel", text: "1 Samuel" },
        { value: "2samuel", text: "2 Samuel" },
        { value: "1kings", text: "1 Kings" },
        { value: "2kings", text: "2 Kings" },
        { value: "1chronicles", text: "1 Chronicles" },
        { value: "2chronicles", text: "2 Chronicles" },
        { value: "ezra", text: "Ezra" },
        { value: "nehemiah", text: "Nehemiah" },
        { value: "esther", text: "Esther" },
        { value: "job", text: "Job" },
        { value: "psalms", text: "Psalms" },
        { value: "proverbs", text: "Proverbs" },
        { value: "ecclesiastes", text: "Ecclesiastes" },
        { value: "songofsolomon", text: "Song of Solomon" },
        { value: "isaiah", text: "Isaiah" },
        { value: "jeremiah", text: "Jeremiah" },
        { value: "lamentations", text: "Lamentations" },
        { value: "ezekiel", text: "Ezekiel" },
        { value: "daniel", text: "Daniel" },
        { value: "hosea", text: "Hosea" },
        { value: "joel", text: "Joel" },
        { value: "amos", text: "Amos" },
        { value: "obadiah", text: "Obadiah" },
        { value: "jonah", text: "Jonah" },
        { value: "micah", text: "Micah" },
        { value: "nahum", text: "Nahum" },
        { value: "habakkuk", text: "Habakkuk" },
        { value: "zephaniah", text: "Zephaniah" },
        { value: "haggai", text: "Haggai" },
        { value: "zechariah", text: "Zechariah" },
        { value: "malachi", text: "Malachi" },
        { value: "matthew", text: "Matthew" },
        { value: "mark", text: "Mark" },
        { value: "luke", text: "Luke" },
        { value: "john", text: "John" },
        { value: "acts", text: "Acts" },
        { value: "romans", text: "Romans" },
        { value: "1corinthians", text: "1 Corinthians" },
        { value: "2corinthians", text: "2 Corinthians" },
        { value: "galatians", text: "Galatians" },
        { value: "ephesians", text: "Ephesians" },
        { value: "philippians", text: "Philippians" },
        { value: "colossians", text: "Colossians" },
        { value: "1thessalonians", text: "1 Thessalonians" },
        { value: "2thessalonians", text: "2 Thessalonians" },
        { value: "1timothy", text: "1 Timothy" },
        { value: "2timothy", text: "2 Timothy" },
        { value: "titus", text: "Titus" },
        { value: "philemon", text: "Philemon" },
        { value: "hebrews", text: "Hebrews" },
        { value: "james", text: "James" },
        { value: "1peter", text: "1 Peter" },
        { value: "2peter", text: "2 Peter" },
        { value: "1john", text: "1 John" },
        { value: "2john", text: "2 John" },
        { value: "3john", text: "3 John" },
        { value: "jude", text: "Jude" },
        { value: "revelation", text: "Revelation" }
      ],
      "bookofmormon": [
        { value: "1nephi", text: "1 Nephi" },
        { value: "2nephi", text: "2 Nephi" },
        { value: "jacob", text: "Jacob" },
        { value: "enos", text: "Enos" },
        { value: "jarom", text: "Jarom" },
        { value: "omni", text: "Omni" },
        { value: "wordsofmormon", text: "Words of Mormon" },
        { value: "mosiah", text: "Mosiah" },
        { value: "alma", text: "Alma" },
        { value: "helaman", text: "Helaman" },
        { value: "3nephi", text: "3 Nephi" },
        { value: "4nephi", text: "4 Nephi" },
        { value: "mormon", text: "Mormon" },
        { value: "ether", text: "Ether" },
        { value: "moroni", text: "Moroni" }
      ],
      "doctrineandcovenants": [
        { value: "doctrineandcovenants", text: "Sections" }
      ],
      "pearlofgreatprice": [
        { value: "moses", text: "Moses" },
        { value: "abraham", text: "Abraham" },
        { value: "josephsmithmatthew", text: "Joseph Smith–Matthew" },
        { value: "josephsmithhistory", text: "Joseph Smith–History" },
        { value: "articlesoffaith", text: "Articles of Faith" }
      ]
    };

    function populateBooks() {
      const volumeSelect = document.getElementById("volume");
      const bookSelect = document.getElementById("book");
      const selectedVolume = volumeSelect.value;
      const books = booksByVolume[selectedVolume] || [];
      bookSelect.innerHTML = "";
      books.forEach(book => {
        const option = document.createElement("option");
        option.value = book.value;
        option.text = book.text;
        bookSelect.appendChild(option);
      });
    }

    // Populate the book selector on page load and update it when the volume changes.
    populateBooks();
    document.getElementById("volume").addEventListener("change", populateBooks);

    document.getElementById('fetch-scripture-btn').addEventListener('click', function() {
      const volume = document.getElementById('volume').value;
      const book = document.getElementById('book').value;
      const startChapter = document.getElementById('start-chapter').value;
      const endChapter = document.getElementById('end-chapter').value || startChapter;
      const url = `/scripture/${volume}/${book}/${startChapter}/${endChapter}`;
      fetch(url)
        .then(response => response.text())
        .then(data => {
          document.getElementById('scripture-text').value = data;
        })
        .catch(error => {
          document.getElementById('scripture-text').value = `Error: ${error.message}`;
        });
    });

    document.getElementById('copy-btn').addEventListener('click', function() {
      const textArea = document.getElementById('scripture-text');
      textArea.select();
      document.execCommand('copy');
      alert('Text copied to clipboard!');
    });
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

# Single endpoint for all volumes (all URLs become /volume/<volume>/<book>/<chapter>)
@app.route("/scripture/<volume>/<book>/<int:start_chapter>", defaults={'end_chapter': None})
@app.route("/scripture/<volume>/<book>/<int:start_chapter>/<int:end_chapter>")
def scripture(volume, book, start_chapter, end_chapter):
    if end_chapter is None:
        end_chapter = start_chapter
    if start_chapter < 1 or end_chapter < start_chapter:
        return Response("Invalid chapter numbers.", status=400, mimetype="text/plain")
    
    chapters_text = []
    for chapter in range(start_chapter, end_chapter + 1):
        url = f"https://openscriptureapi.org/api/scriptures/v1/lds/en/volume/{volume}/{book}/{chapter}"
        try:
            resp = requests.get(url)
            resp.raise_for_status()
            data = resp.json()
            chapter_text = format_chapter_text(data)
        except Exception as e:
            chapter_text = f"Error fetching chapter {chapter}: {str(e)}\n"
        chapters_text.append(chapter_text)
    scripture_text = "\n\n".join(chapters_text).strip()
    return Response(scripture_text, mimetype="text/plain")

def format_chapter_text(data):
    text = f"\n\n{data['chapter']['bookTitle']} Chapter {data['chapter']['number']}\n\n"
    for idx, verse in enumerate(data['chapter']['verses'], start=1):
        text += f"{idx}. {verse['text']}\n"
    return text

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)