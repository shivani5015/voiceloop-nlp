# VoiceLoop NLP

A small Python project that takes a paragraph, translates it, speaks it out loud,
listens to that audio back as text, and then pulls out the names, places, companies
and dates it finds.

Every step is timed, and the whole run is saved as JSON.

---
## How it works

```
 Text ──► Translate ──► Speech ──► Text again ──► Entities ──► JSON
          (Google)      (gTTS)    (Whisper)       (spaCy)
```

| Step | Library | What it does |
|---|---|---|
| 1. Translate | deep-translator | Converts the input to English |
| 2. Text to speech | gTTS | Saves it as an MP3 |
| 3. Speech to text | faster-whisper | Listens to the MP3 and writes it back out |
| 4. Entities | spaCy | Finds `PERSON`, `ORG`, `GPE`, `DATE` and more |

**Why translate first?** The last two steps only understand English. spaCy's model is
trained on English, and gTTS set to `en` mispronounces anything else. Translation is
the bridge that lets the pipeline accept Hindi or any other language.

---

## Files

```
voiceloop-nlp/
├── main.py              runs the four steps and saves the result
├── logger.py            writes each step's time into logs.md
└── modules/
    ├── translate.py     deep-translator
    ├── tts.py           gTTS
    ├── stt.py           faster-whisper
    └── ner.py           spaCy
```

Each file does one job, so you can read any one of them on its own.

---

## Setup

```bash
python -m venv venv
venv\Scripts\activate           # Mac/Linux: source venv/bin/activate

pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## Run

```bash
python main.py
```

Change these three lines at the top of `main.py`:

```python
paragraph = "your text here"
to_lang   = "en"     # language to translate into
from_lang = "hi"     # language your text is in ("en" skips translation)
```

Needs internet. The Whisper model downloads once on the first run, then it is cached.

---

## Example

Input:

```
Last Tuesday morning, Priya Sharma and Rajesh Kumar met James Wilson
at the Infosys campus in Bangalore.
```

Output:

```
Priya Sharma  -> PERSON
Rajesh Kumar  -> PERSON
James Wilson  -> PERSON
Infosys       -> ORG
Bangalore     -> GPE
Last Tuesday  -> DATE
```

You also get:
- `result.json` — the full run: translation, transcript, entities, timings
- `logs.md` — how long each step took
- `audio_files/` — the generated MP3, named with a timestamp

---

## What I found while testing

Running it on Indian text showed a few limits of spaCy's small English model:

- **Full names only.** `Priya Sharma` is tagged `PERSON`, but `Priya` alone comes back
  as `ORG` — even though the full name appeared earlier in the same paragraph.
- **Crore and rupee aren't money.** `250 crore rupee` is tagged `CARDINAL`, a plain
  number. `$500 million` works fine.
- **Entities can merge.** `Hyderabad next month` came out as one `DATE`, and the city
  disappeared.
- **Mistakes travel.** spaCy never hears the audio, only what Whisper thought it
  heard. One wrong vowel — `sapna` heard as `Subna` — was enough to turn a person into
  a `WORK_OF_ART`.

All of these produced clean, confident-looking output with no errors or warnings.
Those are the ones to watch for.

---

## Next steps

- Compare the `tiny` and `base` Whisper models on the same audio
- Try a bigger spaCy model, or train one on Indian names and amounts
- Read the input from a file instead of editing `main.py`

## Tech

Python · deep-translator · gTTS · faster-whisper · spaCy
