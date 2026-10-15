# French Weave

Learn French passively from the English you already read. French Weave swaps a few French words into AI chat
replies and the web pages you read, at your level, and moves words from learning to known as you see them.

> The build passes maintenant, mais the cache is stale, donc I cleared it.
> (maintenant = now, "man-tuh-nahn"; mais = but, "meh"; donc = so, "donk")

## Set up

**Claude Code or Codex.** Tell your agent:

```
Set up French Weave from https://github.com/jackieoliver/french-weave
```

It first asks a few questions in one go: how much French you know already (none, a few basic words, or simple
French, which starts you at Stage 1, 2 or 3), where French should show up (Claude Code, Codex, the Chrome
extension, a claude.ai or ChatGPT block), whether the extension runs on every site or only ones you turn on, and
how you'll give it a Gemini key. Skip any question to take the default. Rerunning setup (`/french-weave:setup`)
asks again and never resets your progress.

Then you do up to four things (your agent tells you when):
1. Extension: a free Gemini API key from [aistudio.google.com/apikey](https://aistudio.google.com/apikey), as a file path or pasted into the extension popup.
2. Extension: in Chrome, `chrome://extensions`, turn on **Developer mode**, **Load unpacked**, pick the folder it names.
3. Extension: click the French Weave toolbar icon and **Allow all websites** (Chrome asks once; until then it only
   runs on X). If you chose only sites you turn on, tick **This site** in the same popup on each site you want.
4. Codex only: at the next `codex` start, choose **Trust all and continue** for the new hook.

**claude.ai or ChatGPT, with Claude Code installed.** Run `/french-weave:export` (or `/french-weave:export --chatgpt`)
and paste the block it prints:
- claude.ai: Settings > Profile > "What personal preferences should Claude consider in responses?"
- ChatGPT: Settings > Personalization > Custom instructions (two boxes, each block fits 1,500 characters).

Re-export about once a week; Claude Code reminds you when the pasted block is more than a week behind.

**claude.ai or ChatGPT only, nothing to install.** Open [blocks/level-01.md](blocks/level-01.md), paste its block
into the same settings box, and chat as usual. When the 30 words in it feel easy, paste level 2 instead, and so on
through level 35.

Agents: follow [INSTALL-FOR-AGENTS.md](INSTALL-FOR-AGENTS.md).

## Set up by hand (no agent)

An agent only asks the questions above and runs these commands for you. You need Python 3.9+; Claude Code and
Codex are optional.

```sh
git clone -b firefox https://github.com/maxgmr/french-weave && cd french-weave
python3 scripts/fw.py setup --dry-run     # shows what it would do; changes nothing
python3 scripts/fw.py setup               # plus any options below
python3 scripts/fw.py check               # every line should say ok
```

| You want | Add to `setup` |
|---|---|
| Some French already | `--known-top 40` (a few basic words) or `--known-top 150` (simple French) |
| The extension only on sites you turn on | `--sites ask` (default: every site; you can still turn sites off) |
| The Gemini key from a file (holding only the key) | `--gemini-key-file PATH`; otherwise paste it into the extension popup |
| French in Codex CLI | `--codex`, then pick **Trust all and continue** at the next `codex` start |
| Chrome or Chromium run with `--user-data-dir` | `--user-data-dir DIR` (repeatable) |

Rerunning setup is safe: it never resets your progress, and leaving out `--sites` keeps your earlier choice. Then
pick what you use:

- **Firefox**: see [Firefox (this fork)](#firefox-this-fork) below.
- **Chrome**: `chrome://extensions` > **Developer mode** > **Load unpacked** > `~/.french-weave/extension`, then the
  French Weave toolbar icon > **Allow all websites** (or tick **This site**).
- **Claude Code**: `claude plugin marketplace add jackieoliver/french-weave`, then
  `claude plugin install french-weave@french-weave`. Its hook and `/french-weave:*` commands use the word state
  this setup made. Don't run `/french-weave:setup`: it is the upstream setup, which doesn't install the Firefox
  host. Rerun `scripts/fw.py setup` from this checkout instead.
- **claude.ai or ChatGPT**: `python3 scripts/fw.py export` (or `export --chatgpt`) and paste the block as described above.

Without Claude Code or Codex, the extension still works: words advance from what you see on web pages, and every
command in [Commands](#commands-claude-code) runs as `python3 ~/.french-weave/app/scripts/fw.py <command>`.

## Firefox (this fork)

The same extension runs in Firefox 142 or newer on desktop, including the Snap build on Ubuntu. Firefox only keeps
add-ons it can verify, so instead of "Load unpacked" you sign your own copy as an unlisted add-on on
addons.mozilla.org (AMO). It is never listed publicly, and the automatic review takes minutes.

1. Run setup and check from this checkout, as in [Set up by hand](#set-up-by-hand-no-agent).
   Besides the Chrome files, setup writes the Firefox native host for the add-on ID `french-weave@maxgmr` to
   `~/.mozilla/native-messaging-hosts/` (macOS: `~/Library/Application Support/Mozilla/NativeMessagingHosts/`).
2. Once: create AMO API credentials at https://addons.mozilla.org/developers/addon/api/key/ and put them in a
   `.env` file at the repo root (git ignores it; `chmod 600 .env`):
   ```
   WEB_EXT_API_KEY=user:12345:678
   WEB_EXT_API_SECRET=...
   ```
3. Commit any changes under `extension/`, then run `python3 scripts/sign_firefox.py`. It needs Node.js (`npx` fetches
   `web-ext`) and saves the signed `.xpi` in `dist/`. `--lint-only` checks the add-on without signing.
4. In Firefox: `about:addons` > gear menu > **Install Add-on From File** > the `.xpi`. Then click the French Weave
   toolbar icon and **Allow all websites** (or tick **This site**), and paste a Gemini key if setup didn't store one.
5. Snap Firefox asks once, through the desktop portal, whether Firefox may start the French Weave host; allow it.
   To revoke that later:
   `gdbus call --session --dest org.freedesktop.impl.portal.PermissionStore --object-path /org/freedesktop/impl/portal/PermissionStore --method org.freedesktop.impl.portal.PermissionStore.Delete webextensions com.frenchweave.host`

**Updating:** after pulling or changing code, rerun setup (your progress is kept), commit, sign again, and install
the new `.xpi` over the old one; settings and a pasted key are kept. Signed copies are versioned
`<manifest version>.<commit count>`, because AMO signs each version only once.

**Removing:** remove the add-on in `about:addons`, then run `python3 scripts/fw.py uninstall`. It removes the Chrome
and Firefox host files but keeps `~/.french-weave` (your progress). Also run the `gdbus` command above on Snap.


## What it does

- **Claude Code and Codex**: a prompt hook gives the model your stage and word lists every turn. Every sentence
  stays an English sentence, new words get a one-line gloss with a sound hint at the end, and every third reply
  opens with a recall cue. Never in code, files, commits or anything meant to be shared, and never in scripted
  runs (`claude -p`, `codex exec`).
- **claude.ai and ChatGPT**: the same rules as a pasted preferences block. No hooks there, so the block is static
  until you refresh it.
- **Any website in Chrome** (extension): a few English words on the page become French. Hover for the meaning,
  click to flip back. On for every site by default; turn sites off from the toolbar popup, or set it to only the
  sites you turn on. Swaps are chosen by Gemini on your own key.

All of it shares one word list on your machine, so words you see on the web count toward the chat and the other way round.

## Commands (Claude Code)

| Command | What it does |
|---|---|
| `/french-weave:status` | Stage, word counts, the words you're learning |
| `/french-weave:known <word>` | Mark a word known (no more glosses) |
| `/french-weave:learn <word>` | Put a word back into the learning set |
| `/french-weave:stage 1-4\|auto` | Pin your stage, or let it follow your known words |
| `/french-weave:pause` / `resume` | Stop or restart French in chat and on websites |
| `/french-weave:export [--chatgpt] [--log-day]` | Paste-ready block for claude.ai or ChatGPT |

The same commands work from a terminal as `python3 ~/.french-weave/app/scripts/fw.py <command>`.

## How words advance

Words come from [`data/lexicon.csv`](data/lexicon.csv): about 1,000 French words and short phrases in
frequency/usefulness order (connectors and adverbs first, then everyday nouns, adjectives and verbs), each with a
gloss and a sound hint.

- **Exposure day**: a day you saw the word in a Claude Code or Codex reply, or on a web page.
- **Learning (active)**: up to 20 at a time; at most 5 new words a day, and none while 5 or more are shaky.
- **Learning -> known**: 3 exposure days, with no flip, `learn` or peek on the last 3.
- **Flip or `learn` -> shaky**: clicking a French word on a web page back to English, or `/french-weave:learn`. A **peek**
  (hovering until the meaning shows) holds back a learning word; a known word peeked on 2 days within a week turns
  shaky. **Shaky -> known** after 7 days with no flip or peek.
- **Stage** follows your known words: 1 to start, 2 at 40 known, 3 at 150, 4 at 400.
  `/french-weave:stage N` pins it; `/french-weave:stage auto` unpins.

| Stage | French in a reply | Per sentence | Shape |
|---|---|---|---|
| 1 | about 6%, never over 10% | at most 2 | English sentences with swapped words |
| 2 | about 12%, never over 20% | at most 4 | same |
| 3 | about 25%, never over 35% | at most 4 | plus one short French sentence in five |
| 4 | about 40%, never over 55% | at most 4 | plus two in five |

Once you know 150 words, the brief and exports stop listing them: they name the band ("about the 400 most common
French words") plus the exceptions, so a thousand known words still fit in about 3 KB.

**Chats that can't be scanned** (claude.ai, ChatGPT) don't count toward exposure. If you mostly read French there,
`fw.py log-chat-day` (or `export --log-day`) counts today as exposure for your learning words. It's off by default
because it's a guess: it never makes a word known on its own; a word still needs one real sighting.

**Only in conversations you read.** The hook weaves in every chat surface (terminal, desktop, IDE, Remote Control,
claude.ai/code, the Codex TUI) and stays silent only in one-shot scripted runs: `claude -p` without
`--sdk-url`/`--input-format stream-json`, Agent SDK scripts (`CLAUDE_CODE_ENTRYPOINT` `sdk-ts` or `sdk-py`) and
`codex exec`. Set `FRENCH_WEAVE_OFF=1` to switch it off for anything else, or `FRENCH_WEAVE_FORCE=1` to weave in a
script. Health, medication, legal, money, safety,
emergency and driving topics get no French at all.

The extension's prompts are built for levels 1-2; at Stage 3-4 it uses the level 2 rules.

## Privacy

Everything stays on your machine in `~/.french-weave` (override with `FRENCH_WEAVE_HOME`). The hook reads your
local Claude Code and Codex transcripts to count exposure and never sends them anywhere. By default the extension
runs on every site you allow, and readable page text from those sites goes to Google's Gemini API with your key
(free-tier keys allow Google to train on prompts); webmail, AI chat sites and local addresses start off. It talks
to the plugin through a Chrome native messaging host that only this extension's ID may call. If setup stored
your Gemini key, it sits in `~/.french-weave/gemini_key` (mode 600) and is handed only to the extension's
background worker, never to the pages it runs on.

## Layout

```
.claude-plugin/   marketplace.json + plugin.json (the repo is both)
hooks/            UserPromptSubmit hook -> scripts/weave.py
commands/         /french-weave:* slash commands
scripts/          fwlib.py (state, rules, transcript scan), weave.py (hook), fw.py (CLI, setup),
                  fw_host.py (native host), export.py (claude.ai / ChatGPT blocks), make_blocks.py (blocks/)
data/lexicon.csv  ranked words: fr, en, sound hint
blocks/           ready-made claude.ai / ChatGPT blocks, one per level (generated)
extension/        Chrome MV3 extension (no build step, no runtime dependencies)
tests/            python tests, live model checks, extension end-to-end check
```

## Develop

```sh
python3 -m unittest discover -s tests            # hook, rules, exports, native host, setup, Codex merge
python3 scripts/make_blocks.py                   # regenerate blocks/ after changing the rules or lexicon
cd extension && bun install && bun test           # extension (happy-dom)
python3 tests/model_eval.py --out /tmp/fw-eval    # live check via claude -p, isolated from your own config
python3 tests/model_eval.py --paste level-01 --stages 1 --out /tmp/fw-eval   # simulate claude.ai with a block
node tests/extension_e2e.mjs                      # after setup: Playwright Chromium + fake X and article pages + real Gemini
```

## License

MIT
