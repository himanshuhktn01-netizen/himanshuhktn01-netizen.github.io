# Goblin Slayer — Browser Version

This is a browser-specific copy of the game. The desktop source and its assets remain
unchanged. `main.py` retains the existing gameplay classes and mechanics and uses an
async game loop that yields to the browser every frame using `asyncio.sleep(0)`.

## Dependencies

`requirements.txt` lists the game runtime dependencies:

- `pygame-ce` — Pygbag's supported Pygame implementation.

Pygbag is the build tool and is installed separately from the runtime requirements.
The original desktop source uses the third-party `emoji` package for decorative
glyphs; this browser copy uses text-only equivalents to avoid a runtime PyPI install.
The desktop game remains unchanged.

## Audio and fonts

The original MP3 files are retained in `Myassests/`. Matching OGG/Vorbis files are
included for the browser build; the browser selects OGG while desktop runs select the
original MP3. Background music starts after the player presses Enter, satisfying the
browser's user-interaction requirement. Pygame's bundled default font is used instead
of relying on operating-system fonts.

## Build and preview

From this directory, build with:

```text
python -m pygbag --build --ume_block=0 --cdn https://pygame-web.github.io/archives/0.9/ .
```

Pygbag's generated web package is written under `build/web/`. Run
`python -m pygbag --ume_block=0 --cdn https://pygame-web.github.io/archives/0.9/ .`
to preview using Pygbag's local server. The user-media startup gate is disabled so
the browser does not wait for a media gesture before starting. Music still waits for
the Enter key. Upload the contents of `build/web/` to a static web host; this project
has not been deployed.

## Netlify deployment

Pygbag 0.9.3's generated `pythons.js` sizes the APK buffer from the
JavaScript-visible `Content-Length`. Netlify may Brotli- or gzip-encode the APK
even when `_headers` specifies `no-transform`; the Fetch API exposes the decoded
body, so the header can be missing or unsuitable for sizing that body. The
resulting zero-length buffer causes the BrowserFS mount to fail.

The generated `build/web/pythons.js` is patched to read the response body to EOF
and size its buffer from the decoded bytes. Its terminal-module imports still use
the configured Pygbag CDN. `build/web/index.html` loads this local runtime
instead of the unpatched CDN copy. Keep both files together with
`browser_version.apk` in Netlify's publish directory. The `_headers` rule is
retained but is not relied on to fix the loader.

Pygbag regenerates `index.html` during a build. If you rebuild, reapply the local
loader patch and local script reference before deploying. After redeployment,
verify a fresh browser load completes the APK mount before enabling the
website's PLAY NOW link.

## Browser verification

A Pygbag 0.9.3 build using the official `https://pygame-web.github.io/archives/0.9/`
runtime was tested in a normal browser preview. The game menu rendered; Enter started
wave 1; Space fired; R displayed the reload message; and enemy damage, wave
progression, a Boss, and the victory screen were observed. The browser accepted real
keyboard input during these checks.

## Known limitations

- Music and sound effect playback have not been confirmed by listening in a browser.
- The game-over screen was not verified in the browser.
- The original game does not implement player movement; controls are Enter, Space, R,
  and H. No movement mechanic was added in the browser port.
- The game uses fixed 1000x600 coordinates and has not been adapted for touch input.
