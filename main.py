import json
import time

from logger import add_log
from modules.ner import find_entities
from modules.stt import voice_to_text
from modules.translate import translate_text
from modules.tts import text_to_voice

# ---------- Settings ----------
paragraph = (
    "Last Tuesday morning, Priya Sharma and Rajesh Kumar met James Wilson "
    "at the Infosys campus in Bangalore. The team announced a 250 crore rupee "
    "partnership with Microsoft that will create 1200 jobs by March 2027. "
    "Shares of Infosys climbed 4 percent on the NSE after the news. "
    "Priya said the first office will open in Hyderabad next month, while "
    "Rajesh will lead a smaller team in Chennai. "
    "Analysts at Goldman Sachs called it the biggest deal of the year."
)


to_lang = "en"       # output kis language me chahiye
from_lang = "en"     # input kis language me hai (Hindi ho to "hi")

errors = []


def run_step(name, func, *args):
    """Step chalao, time log karo. Fail ho to None milta hai, program rukta nahi."""
    print(f"{name}...")
    start = time.time()

    try:
        value = func(*args)
    except Exception as e:
        value = None
        errors.append(f"{name} failed: {e}")
        print("   failed")

    add_log(name, time.time() - start)
    return value


# ---------- Step 1: Translate ----------
translated = run_step("1. Translate", translate_text, paragraph, to_lang, from_lang)

if translated is None:
    translated = paragraph       # fail ho to original text se aage badho

# ---------- Step 2: Text to Voice ----------
audio_path = run_step("2. Text to Voice", text_to_voice, translated, to_lang)

# ---------- Step 3: Voice to Text ----------
transcript = ""
language = ""

if audio_path is None:
    audio_path = ""
    errors.append("3. Voice to Text skipped - audio file nahi bani")
else:
    answer = run_step("3. Voice to Text", voice_to_text, audio_path)
    if answer is not None:
        transcript = answer[0]
        language = answer[1]

# ---------- Step 4: NER ----------
if transcript != "":
    text_for_ner = transcript    # transcript mila to usi par
else:
    text_for_ner = translated

entities = run_step("4. NER", find_entities, text_for_ner)

if entities is None:
    entities = []

# ---------- Show ----------
print("\n--- Original ---")
print(paragraph)

print("\n--- Translated ---")
print(translated)

print("\n--- Transcript ---")
if transcript != "":
    print(transcript)
else:
    print("(nahi mila)")

print("\n--- Entities ---")
for text, label in entities:
    print(f"{text} -> {label}")

if errors:
    print("\n--- Problems ---")
    for e in errors:
        print("!", e)

# ---------- Save ----------
entity_list = []
for text, label in entities:
    entity_list.append({"text": text, "label": label})

result = {
    "original_text": paragraph,
    "translated_text": translated,
    "audio_path": audio_path,
    "transcript": transcript,
    "language": language,
    "entities": entity_list,
    "errors": errors,
}

with open("result.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print("\nDone! Check result.json and logs.md")