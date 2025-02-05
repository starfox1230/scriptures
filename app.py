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
  <link href="https://fonts.googleapis.com/css?family=Roboto:400,500&display=swap" rel="stylesheet">
  <style>
    :root {
      --background-color: #2E2E2E;
      --text-color: #FFFFFF;
      --accent-color: #8A2BE2;
      --input-bg: #3C3C3C;
      --input-border: #555;
      --button-bg: #8A2BE2;
      --button-hover: #9D50BB;
    }
    body {
      background-color: var(--background-color);
      color: var(--text-color);
      font-family: 'Roboto', sans-serif;
      margin: 0;
      padding: 20px;
      line-height: 1.6;
    }
    h1 {
      text-align: center;
      color: var(--accent-color);
      margin-bottom: 20px;
    }
    .container {
      max-width: 800px;
      margin: 0 auto;
      padding: 20px;
      background-color: #2C2C2C;
      border-radius: 8px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.5);
    }
    .row {
      display: flex;
      flex-wrap: wrap;
      gap: 20px;
      margin-bottom: 15px;
    }
    .col {
      flex: 1;
      min-width: 200px;
    }
    label {
      display: block;
      margin-bottom: 5px;
    }
    select, input[type="text"], textarea {
      background-color: var(--input-bg);
      color: var(--text-color);
      border: 1px solid var(--input-border);
      border-radius: 4px;
      padding: 8px;
      font-size: 16px;
      width: 100%;
      box-sizing: border-box;
      margin-bottom: 10px;
    }
    textarea {
      height: 300px;
      resize: vertical;
    }
    button {
      background-color: var(--button-bg);
      border: none;
      color: var(--text-color);
      padding: 10px 20px;
      font-size: 16px;
      border-radius: 4px;
      cursor: pointer;
      transition: background-color 0.3s ease;
      margin-right: 10px;
    }
    button:hover {
      background-color: var(--button-hover);
    }
    @media (max-width: 600px) {
      .row {
        flex-direction: column;
      }
    }
    /* Hide custom input fields by default */
    .custom-input {
      display: none;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>Standard Works Scripture Copier</h1>
    
    <div class="row">
      <div class="col">
        <label for="volume">Select Volume:</label>
        <select id="volume">
          <option value="bible">Bible (KJV)</option>
          <option value="bookofmormon">Book of Mormon</option>
          <option value="doctrineandcovenants">Doctrine and Covenants</option>
          <option value="pearlofgreatprice">Pearl of Great Price</option>
        </select>
      </div>
      <div class="col">
        <label for="book">Select Book:</label>
        <select id="book">
          <!-- Options populated via JavaScript -->
        </select>
      </div>
    </div>
    
    <div class="row">
      <div class="col">
        <label for="start-chapter">Start Chapter:</label>
        <select id="start-chapter">
          <!-- Options populated via JavaScript -->
        </select>
        <input type="text" id="custom-start-chapter" class="custom-input" placeholder="Enter custom start chapter">
      </div>
      <div class="col">
        <label for="end-chapter">End Chapter:</label>
        <select id="end-chapter">
          <!-- Options populated via JavaScript -->
        </select>
        <input type="text" id="custom-end-chapter" class="custom-input" placeholder="Enter custom end chapter">
      </div>
    </div>
    
    <div class="row" style="justify-content: center;">
      <button id="fetch-scripture-btn">Fetch Scripture</button>
      <button id="copy-btn">Copy to Clipboard</button>
    </div>
    
    <textarea id="scripture-text" readonly></textarea>
  </div>
  
  <script>
    // Mapping of books for each volume.
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
        { value: "moses", text: "Book of Moses" },
        { value: "abraham", text: "Book of Abraham" },
        { value: "josephsmithmatthew", text: "Joseph Smith–Matthew" },
        { value: "josephsmithhistory", text: "Joseph Smith–History" },
        { value: "articlesoffaith", text: "Articles of Faith" }
      ]
    };

    // Chapter counts based on the provided list.
    const chapterCounts = {
      "bible": {
        "genesis": 50,
        "exodus": 40,
        "leviticus": 27,
        "numbers": 36,
        "deuteronomy": 34,
        "joshua": 24,
        "judges": 21,
        "ruth": 4,
        "1samuel": 31,
        "2samuel": 24,
        "1kings": 22,
        "2kings": 25,
        "1chronicles": 29,
        "2chronicles": 36,
        "ezra": 10,
        "nehemiah": 13,
        "esther": 10,
        "job": 42,
        "psalms": 150,
        "proverbs": 31,
        "ecclesiastes": 12,
        "songofsolomon": 8,
        "isaiah": 66,
        "jeremiah": 52,
        "lamentations": 5,
        "ezekiel": 48,
        "daniel": 12,
        "hosea": 14,
        "joel": 3,
        "amos": 9,
        "obadiah": 1,
        "jonah": 4,
        "micah": 7,
        "nahum": 3,
        "habakkuk": 3,
        "zephaniah": 3,
        "haggai": 2,
        "zechariah": 14,
        "malachi": 4,
        "matthew": 28,
        "mark": 16,
        "luke": 24,
        "john": 21,
        "acts": 28,
        "romans": 16,
        "1corinthians": 16,
        "2corinthians": 13,
        "galatians": 6,
        "ephesians": 6,
        "philippians": 4,
        "colossians": 4,
        "1thessalonians": 5,
        "2thessalonians": 3,
        "1timothy": 6,
        "2timothy": 4,
        "titus": 3,
        "philemon": 1,
        "hebrews": 13,
        "james": 5,
        "1peter": 5,
        "2peter": 3,
        "1john": 5,
        "2john": 1,
        "3john": 1,
        "jude": 1,
        "revelation": 22
      },
      "bookofmormon": {
        "1nephi": 22,
        "2nephi": 33,
        "jacob": 7,
        "enos": 1,
        "jarom": 1,
        "omni": 1,
        "wordsofmormon": 1,
        "mosiah": 29,
        "alma": 63,
        "helaman": 16,
        "3nephi": 30,
        "4nephi": 1,
        "mormon": 9,
        "ether": 15,
        "moroni": 10
      },
      "doctrineandcovenants": {
        "doctrineandcovenants": 138
      },
      "pearlofgreatprice": {
        "moses": 8,
        "abraham": 5,
        "josephsmithmatthew": 1,
        "josephsmithhistory": 1,
        "articlesoffaith": 1
      }
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
      populateChapters();
    }

    function populateChapters() {
      const volume = document.getElementById("volume").value;
      const book = document.getElementById("book").value;
      const startChapterSelect = document.getElementById("start-chapter");
      const endChapterSelect = document.getElementById("end-chapter");
      const count = (chapterCounts[volume] && chapterCounts[volume][book]) || 1;
      
      startChapterSelect.innerHTML = "";
      endChapterSelect.innerHTML = "";
      
      for (let i = 1; i <= count; i++) {
        let opt1 = document.createElement("option");
        opt1.value = i;
        opt1.text = i;
        startChapterSelect.appendChild(opt1);
        
        let opt2 = document.createElement("option");
        opt2.value = i;
        opt2.text = i;
        endChapterSelect.appendChild(opt2);
      }
      
      let customOpt1 = document.createElement("option");
      customOpt1.value = "custom";
      customOpt1.text = "Custom";
      startChapterSelect.appendChild(customOpt1);
      
      let customOpt2 = document.createElement("option");
      customOpt2.value = "custom";
      customOpt2.text = "Custom";
      endChapterSelect.appendChild(customOpt2);
      
      document.getElementById("custom-start-chapter").style.display = "none";
      document.getElementById("custom-end-chapter").style.display = "none";
    }

    function chapterChangeHandler(selectId, customInputId) {
      const selectElem = document.getElementById(selectId);
      const customInput = document.getElementById(customInputId);
      if (selectElem.value === "custom") {
        customInput.style.display = "inline";
      } else {
        customInput.style.display = "none";
      }
    }
    
    document.getElementById("volume").addEventListener("change", populateBooks);
    document.getElementById("book").addEventListener("change", populateChapters);
    document.getElementById("start-chapter").addEventListener("change", function() {
      chapterChangeHandler("start-chapter", "custom-start-chapter");
    });
    document.getElementById("end-chapter").addEventListener("change", function() {
      chapterChangeHandler("end-chapter", "custom-end-chapter");
    });

    document.getElementById('fetch-scripture-btn').addEventListener('click', function() {
      const volume = document.getElementById('volume').value;
      const book = document.getElementById('book').value;
      
      let startChapter = document.getElementById('start-chapter').value;
      if (startChapter === "custom") {
        startChapter = document.getElementById('custom-start-chapter').value;
      }
      
      let endChapter = document.getElementById('end-chapter').value;
      if (endChapter === "custom") {
        endChapter = document.getElementById('custom-end-chapter').value;
      }
      
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

    populateBooks();
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

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
            chapter_text = format_chapter_text(data, volume)
        except Exception as e:
            chapter_text = f"Error fetching chapter {chapter}: {str(e)}\n"
        chapters_text.append(chapter_text)
    scripture_text = "\n\n".join(chapters_text).strip()
    return Response(scripture_text, mimetype="text/plain")

def format_chapter_text(data, volume):
    title = data['chapter']['bookTitle']
    number = data['chapter']['number']
    # Use "Section" for Doctrine and Covenants, and "Chapter" for all others.
    label = "Section" if volume == "doctrineandcovenants" else "Chapter"
    text = f"\n\n{title} {label} {number}\n\n"
    for idx, verse in enumerate(data['chapter']['verses'], start=1):
        text += f"{idx}. {verse['text']}\n"
    return text

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
