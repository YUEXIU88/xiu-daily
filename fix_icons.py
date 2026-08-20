# -*- coding: utf-8 -*-
import shutil, os

html_path = 'index.html'
data = open(html_path, encoding='utf-8').read()

# Two-phase replacement: old -> placeholder -> new
# This avoids chain issues (e.g. A->B, B->C would make A->C in single pass)
REPLACE = [
    (r"\ud83d\udc30",         r"\ud83d\udc71"),           # rabbit -> cat face
    (r"\ud83c\udf1f",         r"\u2728"),                  # star -> sparkles
    (r"\ud83d\udc23",         r"\ud83d\udc25"),           # hatching chick -> baby chick
    (r"\ud83c\udff7\ufe0f",   r"\ud83c\udf80"),           # label -> ribbon
    (r"\ud83d\udd01",         r"\ud83d\udd04"),           # repeat -> counterclockwise
    (r"\ud83c\udfb5",         r"\ud83c\udfb6"),           # single note -> multiple notes
    (r"\ud83c\udd50",         r"\ud83c\udf80"),           # A button -> ribbon
    (r"\ud83e\udde9",         r"\ud83e\uddf8"),           # puzzle -> teddy bear
    (r"\ud83d\udde3\ufe0f",   r"\ud83d\udcad"),           # speaking head -> thought
    (r"\ud83c\udf0d",         r"\ud83c\udf10"),           # globe -> globe meridians
    (r"\ud83d\udcac",         r"\ud83d\udcad"),           # speech -> thought
    (r"\ud83d\uded2",         r"\ud83d\udecd\ufe0f"),     # cart -> bags
    (r"\ud83d\udd0d",         r"\ud83d\udd0e"),           # search -> search cuter
    (r"\ud83c\udf8a",         r"\ud83c\udf89"),           # confetti -> party popper
    (r"\ud83c\udf7f",         r"\ud83c\udf88"),           # popcorn -> balloon
    (r"\ud83d\udd16",         r"\ud83d\udcd1"),           # bookmark -> bookmark tabs
    (r"\ud83d\uddd3\ufe0f",   r"\ud83d\udcc5"),           # calendar -> calendar
    (r"\ud83c\udf81",         r"\ud83c\udf80"),           # gift -> ribbon
    (r"\ud83c\udfc5",         r"\ud83c\udfc6"),           # medal -> trophy
    (r"\ud83d\udcc8",         r"\ud83d\udcca"),           # chart up -> bar chart
    (r"\ud83e\udffe",         r"\ud83e\udd1d"),           # push hand -> handshake
    (r"\ud83e\udd1d",         r"\ud83e\udd17"),           # handshake -> hugging face
    (r"\ud83d\udcc3",         r"\ud83d\udcc4"),           # page curl -> page
    (r"\ud83d\udcdd",         r"\ud83d\udccb"),           # memo -> clipboard
    (r"\ud83c\udf3a",         r"\ud83c\udf38"),           # hibiscus -> cherry blossom
    (r"\u2699\ufe0f",         r"\ud83d\udd27"),           # gear -> wrench
    (r"\ud83d\udcda",         r"\ud83d\udcd6"),           # books -> open book
]

# Phase 1: replace each old value with a unique placeholder
total = 0
for i, (old, new) in enumerate(REPLACE):
    old_full = "icon:'" + old + "'"
    placeholder = "icon:'@@PH" + str(i) + "@@'"
    n = data.count(old_full)
    if n > 0:
        data = data.replace(old_full, placeholder)
        total += n
        print(f"  Phase1 [{i}]: {old!r} -> placeholder ({n} found)")
    else:
        print(f"  Phase1 [{i}]: {old!r} -> NOT FOUND")

print(f"\nPhase 1 total: {total}")

# Phase 2: replace placeholders with new values
for i, (old, new) in enumerate(REPLACE):
    placeholder = "icon:'@@PH" + str(i) + "@@'"
    new_full = "icon:'" + new + "'"
    data = data.replace(placeholder, new_full)

print("Phase 2 done (placeholders replaced)")

# Write safely
tmp_path = html_path + '.tmp'
with open(tmp_path, 'w', encoding='utf-8') as f:
    f.write(data)

tmp_size = os.path.getsize(tmp_path)
orig_size = os.path.getsize(html_path)
print(f"Original: {orig_size} bytes, New: {tmp_size} bytes")
if tmp_size < orig_size * 0.95:
    print("ERROR: File shrunk too much! Aborting.")
    os.remove(tmp_path)
else:
    shutil.move(tmp_path, html_path)
    print("File written successfully!")
    print("=== ICONS DONE ===")
