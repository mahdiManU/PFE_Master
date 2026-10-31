"""
baseline.py - snapshot verification results so refactoring can't silently change them.

Usage (from the folder containing manage.py, venv active):
    python baseline.py record   # once, BEFORE refactoring
    python baseline.py check    # after every refactoring step

Put sample .bpmn files in tests/samples/
"""
import os, sys, json, shutil, tempfile, hashlib, glob
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pfe.settings")
django.setup()

from django.conf import settings
from myapp.mabib import message
from myapp.views import modify_bpmn_file
from myapp.verification.contradiction import erreur_contradiction
import myapp.verification.temporal as temporal

# ---------------------------------------------------------------------------
# Translation cache: googletrans is an online service and fails randomly.
# The first successful translation of each sentence is stored in
# tests/baseline/translations.json and reused on every later run, so
# `check` gives the same result with or without internet.
# ---------------------------------------------------------------------------
CACHE_FILE = os.path.join("tests", "baseline", "translations.json")
_real_translate = temporal.translate_if_french
_cache = {}
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, encoding="utf-8") as f:
        _cache = json.load(f)


def _cached_translate(text):
    if text not in _cache:
        try:
            _cache[text] = _real_translate(text)
        except Exception as e:
            sys.exit(f"Translation service failed for {text!r}: {e}\n"
                     "Wait a minute and run the command again; "
                     "successful translations are already saved.")
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(_cache, f, ensure_ascii=False, indent=2)
    return _cache[text]


temporal.translate_if_french = _cached_translate

SAMPLES = os.path.join("tests", "samples")
BASELINE = os.path.join("tests", "baseline")
LOI = os.path.join(settings.MEDIA_ROOT, "loi.txt")


def run(path):
    """Same sequence as verify_diagram() in views.py, on a temporary copy."""
    with tempfile.TemporaryDirectory() as tmp:
        work = os.path.join(tmp, "verified_diagram.bpmn")
        shutil.copyfile(path, work)
        arts, arts_en = message(work, work, LOI)
        ann, ann_en = modify_bpmn_file(work)
        con, con_en = erreur_contradiction(work)
        with open(work, "rb") as f:
            xml_hash = hashlib.sha256(f.read()).hexdigest()
    return {
        "structural_fr": arts, "structural_en": arts_en,
        "missing_fr": ann, "missing_en": ann_en,
        "contradiction_fr": con, "contradiction_en": con_en,
        "colored_xml_sha256": xml_hash,
    }


def main(mode):
    os.makedirs(BASELINE, exist_ok=True)
    files = sorted(glob.glob(os.path.join(SAMPLES, "*.bpmn")))
    if not files:
        sys.exit("No .bpmn files found in tests/samples/")
    ok = True
    for path in files:
        name = os.path.basename(path)
        target = os.path.join(BASELINE, name + ".json")
        result = run(path)
        if mode == "record":
            with open(target, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"recorded {name}")
        else:
            with open(target, encoding="utf-8") as f:
                expected = json.load(f)
            diffs = [k for k in expected if expected[k] != result.get(k)]
            print(f"{'OK  ' if not diffs else 'DIFF'} {name} {diffs or ''}")
            ok = ok and not diffs
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "check")