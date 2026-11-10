#!/usr/bin/env python3
"""Replace French gettext msgids with English source strings (longest-first)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = Path(__file__).with_name("fr_to_en_msgids.json")

# Extend via fr_to_en_msgids.json; inline fallback for core UI.
INLINE: dict[str, str] = {
    "Annonces": "Listings",
    "Équipiers": "Crew members",
    "Mes annonces": "My listings",
    "Mes bateaux": "My boats",
    "Publier": "Post",
    "Publier une annonce": "Post a listing",
    "Connexion": "Log in",
    "Inscription": "Sign up",
    "Profil": "Profile",
    "Mon profil": "My profile",
    "Toi": "You",
    "Messages": "Messages",
    "Déconnexion": "Log out",
    "Langue": "Language",
    "Tarifs": "Pricing",
    "FAQ / Sécurité": "FAQ & safety",
    "CGU": "Terms of use",
    "Légal": "Legal",
    "Produit": "Product",
    "Trouve ton équipage. Traverse l'océan.": "Find your crew. Cross the ocean.",
}


def load_map() -> dict[str, str]:
    mapping = dict(INLINE)
    if MAP_PATH.is_file():
        mapping.update(json.loads(MAP_PATH.read_text(encoding="utf-8")))
    # Longest keys first to avoid partial replacements
    return dict(sorted(mapping.items(), key=lambda kv: -len(kv[0])))


def replace_in_text(text: str, mapping: dict[str, str]) -> str:
    for fr, en in mapping.items():
        if fr == en:
            continue
        text = text.replace(f'trans "{fr}"', f'trans "{en}"')
        text = text.replace(f"trans '{fr}'", f"trans '{en}'")
        text = text.replace(f'_("{fr}"', f'_("{en}"')
        text = text.replace(f"_('{fr}'", f"_('{en}'")
    return text


def main() -> None:
    mapping = load_map()
    exts = {".py", ".html", ".js"}
    changed_files = 0
    for path in ROOT.rglob("*"):
        if path.suffix not in exts:
            continue
        if any(p in path.parts for p in (".venv", "locale", "staticfiles", "node_modules", ".git")):
            continue
        if path.name == "fr_to_en_msgids.json":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        new = replace_in_text(text, mapping)
        if new != text:
            path.write_text(new, encoding="utf-8")
            changed_files += 1
    print(f"Updated {changed_files} files ({len(mapping)} mappings)")


if __name__ == "__main__":
    main()
