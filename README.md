# VoiceLoop NLP

Take a paragraph in any language, translate it, speak it out loud, listen to that
audio back as text, and pull the named entities out of the result — with every
step timed and the whole run saved as JSON.

Started as a single 80-line script. This is version 2: the same idea split into
one small module per library, with a translation step, error handling and
structured output. The first version is in the commit history.

---

## Pipeline

```
 Text ──► Translate ──► Text-to-Speech ──► Speech-to-Text ──► NER ──► JSON
          (Google)       (gTTS)            (faster-whisper)   (spaCy)
             │              │                    │              │
             └──────────────┴────────────────────┴──────────────┘
                        each step timed into logs.md
```

| Step | Library | Output |
|---|---|---|
| Translate | `deep-translator` (Google) | English text, source language auto-detected |
| Text → Speech | `gTTS` | `audio_files/voice.mp3` |
| Speech → Text | `faster-whisper` (`tiny`, int8 CPU) | transcript + detected language |
| NER | `spaCy` (`en_core_web_sm`) | `ORG`, `GPE`, `PERSON`, `DATE`… |
| Output | — | `result.json` + timings in `logs.md` |

## Files

```
voiceloop-nlp/
├── main.py                  runs the four steps in order, saves the result
├── logger.py                writes each step's timing into logs.md
├── modules/
│   ├── translate.py         deep-translator
│   ├── tts.py               gTTS
│   ├── stt.py               faster-whisper
│   └── ner.py               spaCy
├── requirements.txt
└── .gitignore
```

---

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## Run

```bash
python main.py
```

The input paragraph and the target language sit at the top of `main.py` — change
`paragraph` and `to_lang` there.

Needs internet: translation and gTTS call Google, and faster-whisper downloads the
`tiny` model on first run (cached after that).

---

## Why the translation step exists

Both of the later stages are English-only. `en_core_web_sm` is trained on English,
and gTTS with `lang="en"` will mispronounce anything else. So translation is the
bridge that lets the pipeline accept any input language.

This showed up clearly in testing. Running with the network blocked, translation
failed and the Hinglish input went straight into spaCy, which returned nonsense:

```
Delhi ke address -> PERSON
Maine            -> GPE
```

With translation working, the same sentence gives `Amazon -> ORG`, `Delhi -> GPE`,
`Gurgaon -> GPE`. The step isn't decoration — it's what makes the rest work.

---

## What v2 fixed

Running v1 and reading its logs carefully turned up five real problems:

1. **One failure killed everything.** v1 had no error handling — when gTTS could not
   reach Google, the whole script died and the NER step never ran. Each step is now
   wrapped separately: a failed translation falls back to the original text and the
   run continues. Tested by running with the network blocked — NER still produced
   entities and the failures were recorded in the JSON instead of crashing.

2. **A broken 0-byte MP3 was left behind.** When gTTS failed mid-save it still created
   the file. The next run would then hand that empty file to Whisper and get a
   confusing error. `tts.py` now deletes it and re-raises.

3. **The timing logs were lying.** v1 loaded the Whisper model inside the timed block,
   so the first run logged 22.97 sec for "transcription" when most of that was a
   one-time model download. The model is now loaded once and reused.

4. **The same four timing lines were copy-pasted under every step.** They live once in
   `run_step()`.

5. **Failed steps were missing from the logs.** An early version only wrote the timing
   after a step finished, so a step that threw was never logged. `run_step()` now logs
   the time either way — which is exactly when you want to know how long something ran
   before giving up.

## What I learned

- **A pipeline is only as accurate as its weakest step.** Whatever the transcriber
  mishears becomes the NER model's input. Speech errors don't stay in the speech layer.
- **Small models have blind spots.** `en_core_web_sm` tags Samsung and Amazon as
  organisations and Delhi and Gurgaon as locations, but misses "Rahul" as a `PERSON`
  entirely — it is trained mostly on Western news text. Worth knowing before trusting
  it on Indian data.
- **Timing each step separately pays off.** The logs are what revealed the model-load
  bug above. Without them I would have assumed transcription was just slow.
- **Failing loudly beats failing silently.** Collecting errors into the output instead
  of crashing means a partial result is still useful — and the broken output above is
  what proved the translation step was doing real work.

## Next steps

- Compare `tiny` vs `base` Whisper accuracy on the same audio
- A larger spaCy model, or a custom-trained one, for Indian names
- Read the input from a file or a command-line argument
- Retry the translation call before giving up on it

## Tech

Python · deep-translator · gTTS · faster-whisper · spaCy
