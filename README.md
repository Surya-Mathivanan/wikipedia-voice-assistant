# wikipedia-voice-assistant
A simple Flask web application that fetches Wikipedia summaries and converts the text into speech using pyttsx3.
## Features
Fetches summaries from Wikipedia based on user input
Allows users to specify the number of sentences in the summary
Converts the summary into speech using the text-to-speech engine
## Technologies Used
Python (Flask)
Wikipedia API (wikipedia library)
Text-to-Speech (pyttsx3)
HTML & CSS (for the frontend)  

## Working Process
### User Input (HTML Form - index.html)

Takes a topic name from the user (<input name="wiki_page">).
Optional: Allows the user to specify the number of sentences (<input name="num_of_sentences">).
### Flask Backend (app.py)

Receives user input via request.form.
Fetches Wikipedia summary using wikipedia.summary().
Converts text to speech using pyttsx3.
### Response & Output

Displays the summary on the webpage ({{ summary }}).
Plays the summary as speech using voicing_text().
## Usage
Enter a topic in the input field.
Choose whether to specify the number of sentences.
Click submit to get the summary and hear the voice output.
## License
This project is open-source and available under the MIT License.
