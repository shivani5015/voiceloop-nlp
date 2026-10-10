from deep_translator import GoogleTranslator, MyMemoryTranslator

# MyMemory ko poora code chahiye - sirf "en" nahi chalta, "en-GB" chahiye
codes = {"en": "en-GB", "hi": "hi-IN"}


def translate_text(text, to_lang="en", from_lang="hi"):
    """Text ko dusri language me badlo.

    Pehle Google - wo khud language pehchan leta hai.
    Google block kare to MyMemory - usko source language batani padti hai.
    """
    if from_lang == to_lang:
        return text

    try:
        return GoogleTranslator(source="auto", target=to_lang).translate(text)
    except Exception:
        print("   Google ne mana kiya, MyMemory se kar rahe hain")

    return MyMemoryTranslator(
        source=codes.get(from_lang, from_lang),
        target=codes.get(to_lang, to_lang),
    ).translate(text)