from flask import Flask, render_template, request
import pyttsx3
import wikipedia

app = Flask(__name__)

def page(title: str, sentences=2):
    content = wikipedia.summary(title, sentences=sentences)
    return content

def voicing_text(text):

    # Initialize the engine
    engine = pyttsx3.init()

    # Set the voice to be used
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)

    # Speak the text
    engine.say(text)
    engine.runAndWait()
    return text

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        wiki_page = request.form["wiki_page"]
        specify_num_of_sentences = request.form.get("specify_sentences")
        num_of_sentences = request.form.get("num_of_sentences")

        if specify_num_of_sentences == "y":
            summary = page(wiki_page, int(num_of_sentences))
        else:
            summary = page(wiki_page)

        voicing_text(summary)  

        return render_template("index.html", summary=summary)

    return render_template("index.html", summary=None)


if __name__ == "__main__":
    app.run(debug=True)






























    """
    :param title: (str) the title of the Wikipedia page to summarize
    :param sentences: (int) the number of sentences to include in the summary (optional, default is 2)
    :return: (str) the summary of the Wikipedia page
    """

    """
    Speaks the given text using the text-to-speech engine
    :param text: (str) the text to speak
    :return: (str) the input text
    """