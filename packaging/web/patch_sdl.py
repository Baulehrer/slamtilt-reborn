#!/usr/bin/env python3
"""Keep document-owned fullscreen independent of SDL canvas lifetimes."""
from pathlib import Path
import sys
path = Path(sys.argv[1]) / 'src/video/emscripten/SDL_emscriptenvideo.c'
text = path.read_text()
marker = '// Reborn: do not leave fullscreen owned by the persistent HTML document.'
anchor = '        EmscriptenFullscreenChangeEvent fsevent;\n'
patch = '''        // Reborn: do not leave fullscreen owned by the persistent HTML document.
        if (fullscreen == SDL_FULLSCREEN_OP_LEAVE && MAIN_THREAD_EM_ASM_INT({
            return !!document.fullscreenElement &&
                document.fullscreenElement !== document.querySelector(UTF8ToString($0));
        }, data->canvas_id)) {
            return SDL_FULLSCREEN_SUCCEEDED;
        }

'''
if marker not in text:
    if text.count(anchor) != 1:
        raise SystemExit('SDL fullscreen adapter changed; review the browser patch')
    path.write_text(text.replace(anchor, patch + anchor))
print('SDL browser document-fullscreen ownership patch ready')
