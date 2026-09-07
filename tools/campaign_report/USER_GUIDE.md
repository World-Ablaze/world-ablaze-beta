# Campaign report: user guide

How to turn the saves of one World Ablaze campaign into the `campaign.html` report, in three
commands. No programming knowledge needed.

## Before you start (once)

- **Python 3.11 or newer.** Open a terminal and type `python --version`; it must answer
  `Python 3.11` or higher. If not, install it from python.org and tick **Add python to PATH**
  during the install.
- **The mod folder** (`world-ablaze-beta`) on your disk. Nothing else to install: the generator
  only uses what ships with Python.
- **The saves of the campaign** in the usual HOI4 folder:
  `Documents\Paradox Interactive\Hearts of Iron IV\save games`, written as **readable text
  saves**. This is the one thing that must be set up BEFORE the campaign is played: see the
  next section. Binary saves cannot be read, and there is no way to convert them afterwards.

## Make HOI4 write readable saves (do this before playing)

By default HOI4 writes its saves in a compact binary form the generator cannot read. Switch
the game to text saves once, before the campaign starts:

1. Close the game.
2. Open `Documents\Paradox Interactive\Hearts of Iron IV\settings.txt` in Notepad.
3. Find the line `save_as_binary=yes` and change it to `save_as_binary=no`. Save the file.
4. Start the game and play: every save (manual or autosave) is now written as text. A text
   save may still be zip-compressed; that is fine, the generator opens it.
5. **Do not use Ironman.** Ironman saves are always binary, whatever the setting.

To check a save, open the `.hoi4` file in Notepad and look at the first characters:

| First characters | Meaning |
| --- | --- |
| `HOI4txt` | text save: readable |
| `PK` | zip-compressed text save: readable |
| `HOI4bin` | binary save: **not readable**, the generator reports it as skipped |

A campaign already saved in binary cannot be recovered by the generator: only saves written
after the switch are usable. The saves of one campaign are grouped by the game's own
campaign identifier, so text saves written from an old game after the switch still belong
to that campaign.

## Step 1: open a terminal in the mod folder

In the Explorer, go to the `world-ablaze-beta` folder, right-click → **Open in Terminal**
(or type `cmd` in the address bar and press Enter).

## Step 2: list the campaigns

```
python -m tools.campaign_report list
```

One line per campaign: its identifier, the number of saves, the period, the mods. Note the
first 8 characters of the identifier you want, for example `a100b67c`.

If your saves are somewhere else, point to that folder:

```
python -m tools.campaign_report list --saves "D:\my_saves"
```

## Step 3: build the report

```
python -m tools.campaign_report build --campaign a100b67c --workers 4
```

The terminal prints one line per save it reads. The first run takes about 3 to 5 minutes for
130 saves; later runs take a few seconds because the reads are cached. At the end, three
paths are printed:

| File | What it is for |
| --- | --- |
| `tools\campaign_report\output\campaign.html` | **The report.** Double-click it to open it in Chrome, Edge, Firefox or Safari. This is the file to share: it contains everything. |
| `tools\campaign_report\output\campaign.json` | The raw data, for the report's **Import JSON data** button. |
| `tools\campaign_report\output\campaign_digest.md` | A short text summary of the same numbers. |

## Useful options

| Need | Add to the `build` command |
| --- | --- |
| Only part of the campaign | `--from 1939.9.1 --to 1945.5.8` |
| Force a full re-read of every save | `--refresh` |
| Saves in another folder | `--saves "D:\my_saves"` |
| Only one campaign in the folder | `--campaign` can be omitted |

## Using the report

- **Tabs on the left**: Overview, Forces, Industry & resources, Armor, Wars & casualties,
  Country status.
- **Top bar**: choose the countries (the seven majors by default; hover a country and click
  `only` to isolate it), set the time window, move the *inspection date* slider for the
  tables and compositions.
- **Charts**: hover a point for its value. Click a legend entry to hide or show a line,
  Shift+click to keep only that one. `Data` shows the numbers, `CSV` downloads them.
- **Tables**: click a column header to sort (ascending, descending, back to the original
  order).
- **Evidence tags**: every number is **MEASURED** (read as-is from the save), **DERIVED**
  (computed from measured fields, the method is stated) or **ASSUMED** (interpretation not
  verified in-game). A `—` means the save does not carry the value; it is never a hidden
  zero. The **Sources, coverage and limitations** panel at the bottom lists every metric and
  its caveat.

## If something goes wrong

| Message | Meaning and fix |
| --- | --- |
| `ERROR: Choose a single campaign with --campaign` | Several campaigns were found: add `--campaign <first 8 characters>`. |
| `ERROR: Two different states at <date>` | Two different saves carry the same date (two branches of one game). Move one of them out of the folder. |
| `'python' is not recognized` | Python is not in the PATH: reinstall it with the PATH box ticked. |
| `SKIPPED: <file>` | That save could not be read: binary save (see *Make HOI4 write readable saves*), Ironman, or not a HOI4 save. The others are still used. |
| The report shows the old numbers after a rebuild | The browser cached the page: press Ctrl+F5. |

## Sharing

Send `campaign.html` only (about 9 MB): mail, Drive, Discord, any file host. The recipient
needs a modern browser and nothing else; no data leaves their machine.
