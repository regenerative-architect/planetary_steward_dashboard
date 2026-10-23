#!/usr/bin/env python3
"""Merge the Commons (P2P), World Map, Stewardship Journey, Guided Pathways and Offline/Depth/Explain add-ons into your own Civic Benevolence Dashboard file.

Usage:   python3 merge_addons.py [path/to/index.html]      (default: index.html in this folder)
Needs:   the five *-addon.html files (commons, map, journey, pathways, shell) next to this script (or next to index.html).
Effect:  copies index.html to index.backup.html (once), then inserts the add-ons just before the closing
         body tag, giving one standalone file. Safe to re-run: an add-on already present is skipped.
Remove:  restore the backup, or delete an add-on's block (each starts with its provenance comment).
Nothing is uploaded; this script only reads and writes local files.
"""
import pathlib
import shutil
import sys

here = pathlib.Path(__file__).resolve().parent
host = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'index.html')
ADDONS = [('commons-addon.html', 'id="cm-module"', 'Commons (P2P)'),
          ('map-addon.html', 'id="mp-module"', 'World Map'),
          ('journey-addon.html', 'id="gd-module"', 'Stewardship Journey'),
          ('pathways-addon.html', 'id="pw-module"', 'Guided Pathways'),
          ('shell-addon.html', 'id="sh-module"', 'Offline, Depth and Explain')]
HOOKS = ['function switchView', 'const VALID_VIEWS', 'const TAB_LABELS', 'id="tab-near"', 'id="tab-live"', 'let layerStatus']

if not host.is_file():
    sys.exit('Cannot find %s. Run this next to index.html, or pass its path.' % host)
html = host.read_text(encoding='utf-8')
missing = [h for h in HOOKS if h not in html]
if missing:
    print('Note: this file lacks hooks the add-ons look for (%s). An add-on that cannot find them skips itself safely.' % ', '.join(missing))
if html.lower().count('</body>') != 1:
    sys.exit('Expected exactly one closing body tag in %s; leaving it untouched.' % host)

todo = []
for fname, marker, name in ADDONS:
    if marker in html:
        print('%s is already merged; skipping.' % name)
        continue
    src = next((b / fname for b in (here, host.resolve().parent) if (b / fname).is_file()), None)
    if src is None:
        print('%s not found next to this script or index.html; skipping %s.' % (fname, name))
        continue
    todo.append((name, src.read_text(encoding='utf-8')))
if not todo:
    sys.exit('Nothing to merge.')

backup = host.with_name(host.stem + '.backup' + host.suffix)
if not backup.exists():
    shutil.copy2(host, backup)
i = html.lower().rfind('</body>')
host.write_text(html[:i] + '\n'.join(t for _, t in todo) + '\n' + html[i:], encoding='utf-8')
print('Merged: %s. Backup: %s. %s is now %.0f KB.' % (', '.join(n for n, _ in todo), backup.name, host.name, host.stat().st_size / 1024))
print('Open it over https or localhost (network rooms need a secure page) and look for the new items in the sidebar.')
if any(n.startswith('Offline') for n, _ in todo):
    print('Offline mode also needs sw.js, manifest.webmanifest and icon.svg in the same folder as %s (they come with the add-ons).' % host.name)
