from flask import Flask, render_template_string, Response
import requests

app = Flask(__name__)

# Inline HTML that is identical in functionality to your original index.html.
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Book of Mormon Scripture Copier</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
        }
        label, select, input {
            margin-right: 10px;
        }
        #scripture-text {
            width: 100%;
            height: 300px;
            margin-top: 20px;
            padding: 10px;
            font-size: 14px;
        }
        button {
            padding: 10px;
            font-size: 16px;
        }
    </style>
</head>
<body>

    <h1>Book of Mormon Scripture Copier</h1>

    <label for="book">Select Book:</label>
    <select id="book">
        <option value="1nephi">1 Nephi</option>
        <option value="2nephi">2 Nephi</option>
        <option value="jacob">Jacob</option>
        <option value="enos">Enos</option>
        <option value="jarom">Jarom</option>
        <option value="omni">Omni</option>
        <option value="wordsofmormon">Words of Mormon</option>
        <option value="mosiah">Mosiah</option>
        <option value="alma">Alma</option>
        <option value="helaman">Helaman</option>
        <option value="3nephi">3 Nephi</option>
        <option value="4nephi">4 Nephi</option>
        <option value="mormon">Mormon</option>
        <option value="ether">Ether</option>
        <option value="moroni">Moroni</option>
    </select>

    <label for="start-chapter">Start Chapter:</label>
    <input type="number" id="start-chapter" value="1" min="1">

    <label for="end-chapter">End Chapter (optional):</label>
    <input type="number" id="end-chapter" min="1">

    <button id="fetch-scripture-btn">Fetch Scripture</button>
    <button id="copy-btn">Copy to Clipboard</button>

    <textarea id="scripture-text" readonly></textarea>

    <script>
        document.getElementById('fetch-scripture-btn').addEventListener('click', function() {
            const book = document.getElementById('book').value;
            const startChapter = document.getElementById('start-chapter').value;
            const endChapter = document.getElementById('end-chapter').value || startChapter; // If no end chapter, fetch only the start chapter

            // Note: We use a relative URL so that the API call works on the same host.
            const url = `/scripture/${book}/${startChapter}/${endChapter}`;

            fetch(url)
                .then(response => response.text()) // expecting plain text
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

# Serve the HTML page at the root URL.
@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

# Create the API endpoint with an optional end chapter.
@app.route("/scripture/<book>/<int:start_chapter>", defaults={'end_chapter': None})
@app.route("/scripture/<book>/<int:start_chapter>/<int:end_chapter>")
def scripture(book, start_chapter, end_chapter):
    # If the end chapter isn't provided, use the start chapter.
    if end_chapter is None:
        end_chapter = start_chapter

    # Validate chapter numbers (similar to your Node code).
    if start_chapter < 1 or end_chapter < start_chapter:
        return Response("Invalid chapter numbers.", status=400, mimetype="text/plain")

    chapter_promises = []  # In Python we'll accumulate chapter texts in a list.
    for chapter in range(start_chapter, end_chapter + 1):
        url = f"https://openscriptureapi.org/api/scriptures/v1/lds/en/volume/bookofmormon/{book}/{chapter}"
        try:
            resp = requests.get(url)
            resp.raise_for_status()  # Will raise an HTTPError for bad responses
            data = resp.json()
            chapter_text = format_chapter_text(data)
        except Exception as e:
            chapter_text = f"Error fetching chapter {chapter}: {str(e)}\n"
        chapter_promises.append(chapter_text)

    # Combine all chapter texts, separated by two newlines.
    scripture_text = "\n\n".join(chapter_promises).strip()
    return Response(scripture_text, mimetype="text/plain")

def format_chapter_text(data):
    # Format the chapter data exactly as in your Node code.
    text = f"\n\n{data['chapter']['bookTitle']} Chapter {data['chapter']['number']}\n\n"
    for idx, verse in enumerate(data['chapter']['verses'], start=1):
        text += f"{idx}. {verse['text']}\n"
    return text

if __name__ == "__main__":
    app.run(debug=True, port=5000)
