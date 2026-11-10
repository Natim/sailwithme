#!/usr/bin/env python3
"""Fill empty (or placeholder) msgstr entries in locale/*/LC_MESSAGES/django.po."""

from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

import polib
from deep_translator import MyMemoryTranslator

ROOT = Path(__file__).resolve().parents[1]
CACHE_PATH = ROOT / "locale" / ".translation_cache.json"
FR_MSGID_TO_EN: dict[str, str] = json.loads((ROOT / "scripts" / "fr_msgid_to_en.json").read_text(encoding="utf-8"))

_raw = json.loads((ROOT / "scripts" / "fr_to_en_msgids.json").read_text(encoding="utf-8"))
EN_TO_FR: dict[str, str] = {en: fr for fr, en in _raw.items()}

EN_TO_FR.update(
    {
        "Skipper+": "Skipper+",
        "Photo": "Photo",
        "Messages": "Messages",
        "Lifetime": "À vie",
        "Conversation": "Conversation",
        "Compte": "Compte",
        "Alerte annonces": "Alerte annonces",
        "Ton message…": "Ton message…",
        "Milles": "Milles",
        "Shown publicly on listings, reviews, and the crew directory.": (
            "Nom affiché publiquement (annonces, avis, annuaire)."
        ),
    }
)

MYMEMORY = {
    "es": MyMemoryTranslator(source="en-GB", target="es-ES"),
    "de": MyMemoryTranslator(source="en-GB", target="de-DE"),
}

FRENCH_RE = re.compile(
    r"[àâäéèêëïîôùûüçÀÂÄÉÈÊËÏÎÔÙÛÜÇ]|" r"\b(conformément|les utilisateurs|tu acceptes|tu es sur le point)\b",
    re.I,
)

SLEEP_SECONDS = 0.85


def is_french_msgid(msgid: str) -> bool:
    if msgid in EN_TO_FR:
        return False
    return bool(FRENCH_RE.search(msgid))


def canonical_english(msgid: str) -> str:
    if msgid in FR_MSGID_TO_EN and FR_MSGID_TO_EN[msgid]:
        return FR_MSGID_TO_EN[msgid]
    return msgid


def load_cache() -> dict[str, str]:
    if CACHE_PATH.is_file():
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    return {}


def save_cache(cache: dict[str, str]) -> None:
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def needs_work(entry: polib.POEntry, locale: str) -> bool:
    if not entry.msgid:
        return False
    if locale == "en":
        return entry.msgstr != canonical_english(entry.msgid)
    if locale == "fr":
        return not (entry.msgstr and entry.msgstr.strip())
    if locale in ("es", "de"):
        if not (entry.msgstr and entry.msgstr.strip()):
            return True
        # Re-translate placeholder copies left when Google failed
        return entry.msgstr == canonical_english(entry.msgid)
    return not (entry.msgstr and entry.msgstr.strip())


def translate_one(locale: str, text: str, cache: dict[str, str]) -> str:
    key = f"en-GB:{locale}:{text}"
    if key in cache:
        return cache[key]
    if not text.strip():
        return text
    translator = MYMEMORY[locale]
    for attempt in range(4):
        try:
            out = translator.translate(text[:4800])
            cache[key] = out
            time.sleep(SLEEP_SECONDS)
            return out
        except Exception as exc:  # noqa: BLE001
            wait = SLEEP_SECONDS * (attempt + 2)
            print(f"  retry {attempt + 1}: {exc!s}"[:100], flush=True)
            time.sleep(wait)
    cache[key] = text
    return text


def translate_batch(locale: str, texts: list[str], cache: dict[str, str]) -> list[str]:
    return [translate_one(locale, text, cache) for text in texts]


def fill_po(locale: str, cache: dict[str, str]) -> int:
    path = ROOT / "locale" / locale / "LC_MESSAGES" / "django.po"
    po = polib.pofile(str(path))
    updated = 0

    if locale in ("es", "de"):
        work = [e for e in po if needs_work(e, locale)]
        sources = [canonical_english(e.msgid) for e in work]
        if sources:
            print(f"  translating {len(sources)} strings via MyMemory…", flush=True)
            translated = translate_batch(locale, sources, cache)
            for entry, msgstr in zip(work, translated, strict=True):
                entry.msgstr = msgstr
                entry.fuzzy = False
                updated += 1
    else:
        for entry in po:
            if not entry.msgid:
                if entry.fuzzy:
                    entry.fuzzy = False
                continue
            if not needs_work(entry, locale):
                continue
            msgid = entry.msgid
            if locale == "fr":
                if is_french_msgid(msgid):
                    entry.msgstr = msgid
                elif msgid in EN_TO_FR:
                    entry.msgstr = EN_TO_FR[msgid]
                else:
                    entry.msgstr = msgid
            else:
                entry.msgstr = canonical_english(msgid)
            entry.fuzzy = False
            updated += 1

    po.metadata["Language"] = locale
    po.metadata.pop("fuzzy", None)
    po.save(str(path))
    return updated


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--locales",
        default=",".join(["fr", "en", "es", "de"]),
        help="Comma-separated locale codes",
    )
    args = parser.parse_args()
    locales = [x.strip() for x in args.locales.split(",") if x.strip()]

    cache = load_cache()
    for locale in locales:
        print(f"Filling locale/{locale}/LC_MESSAGES/django.po …", flush=True)
        n = fill_po(locale, cache)
        print(f"  updated {n} entries", flush=True)
    save_cache(cache)
    print("Done.", flush=True)


if __name__ == "__main__":
    main()
