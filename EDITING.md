# Updating your website

Edit the files in `content/` with any text editor, then run this command from the website folder:

```bash
python3 build.py
```

Python 3.8 or newer is enough; there are no packages to install. Open `index.html` in your browser to preview, or refresh your existing local server. When publishing, include both your edited text files and the regenerated HTML files in your usual Git commit and push.

Changing a `.txt` file alone does not update the visible website until you run the command. The website itself stays ordinary static HTML and CSS and works on GitHub Pages.

## Where to edit

| File | Content |
| --- | --- |
| `content/home.txt` | Homepage introduction, section labels, portrait path, Persian verse, selected project IDs |
| `content/research.txt` | Research projects, paper/code links, ongoing work, publications |
| `content/life.txt` | Personal stories |
| `content/writing.txt` | Technical notes |
| `content/about.txt` | Homepage biography, education, supervision, technical skills |
| `content/code.txt` | Earlier code implementations |
| `content/site.txt` | Profile sidebar, name, email, social links, optional CV, navigation, footer |

The homepage reads research highlights from `research.txt`, biography and experience from `about.txt`, and the latest dated note from `writing.txt` or `life.txt`. The full biography appears only on Home; the Background page provides the detailed education and supervision entries. The sidebar uses the `[profile]` section of `site.txt`. You only maintain each entry in one place.

To add your CV later, copy the PDF into the website folder and set `cv = your-cv.pdf` in `site.txt`. Leaving that field empty hides the CV link.

## Writing text

Keep the names in square brackets and the field names before `=`. Edit the text after `=`. Save files as UTF-8, which preserves Persian characters.

For a longer field, place its text on the following lines with four spaces at the beginning of each line. Blank lines separate paragraphs:

```text
body =
    This is my first paragraph.

    This is my second paragraph.
```

Text is plain text, not HTML or Markdown. The builder handles characters such as `&`, `<`, and `>` for you. The poem preserves line breaks; other paragraphs wrap naturally.

## Adding a story or technical note

Append a block like this to `life.txt` or `writing.txt`:

```text
[entry:a-walk-in-karlsruhe]
title = A walk in Karlsruhe
short_title = A walk in Karlsruhe
date = 2026-09-25
body =
    Write your story here.

    Add as many paragraphs as you like.
```

Use a unique identifier after `entry:` with lowercase letters, numbers, and hyphens. Dates can be `YYYY-MM` or `YYYY-MM-DD`. Entries are displayed newest first, and the newest dated entry appears on the homepage. If two notes share a date, Writing takes priority.

For an article hosted elsewhere, add these optional fields:

```text
source = On Medium
link = https://example.com/your-story
link_label = Read the story
```

Omit those fields to publish the full body directly on your own site.

## Adding research

Copy an existing `[project:...]` block in `research.txt` and use a new identifier. Keep existing identifiers when editing an existing project so saved links still work. `paper` and `figure` are optional. A separate `thumbnail` with `thumbnail_alt` can illustrate the homepage preview; otherwise it uses the project figure or a venue label. A figure needs `figure_alt` and `figure_caption` too.

To feature a project on the homepage, give it `summary` and optionally `short_title`, then add its identifier to `selected_projects` in `home.txt`. The full `body` remains on Research. Put images in this website folder or its `assets/` directory.

## Checking a build

```bash
python3 build.py --check
```

This checks whether your generated pages match the text files. Build errors leave the previously generated pages intact.

The layout lives in `build.py`, `templates/`, and `style.css`. You do not need to edit them for ordinary content updates. The Persian font and its license are stored locally in `assets/fonts/`; no external font service is used.
