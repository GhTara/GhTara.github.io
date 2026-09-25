# Tara Gheshlaghi — personal website

A minimal portfolio and two separate writing streams. The generated site is in `docs/` and can be published directly with GitHub Pages.

## Preview and edit

```bash
npm install
npm run build
python3 -m http.server 8000 -d docs
```

Open `http://localhost:8000`. Edit `build.mjs` for page copy, `assets/style.css` for design, and Markdown files in `content/science/` or `content/life/` for new articles. Each article starts with YAML front matter:

```markdown
---
title: An article title
date: 2026-09-25
description: A sentence about the article.
---

Write in Markdown. Equations may use `$...$` or `$$...$$`.
```

Run `npm run build` again and commit both source and `docs/`.

## Publish at GitHub Pages

Create a repository named `GhTara.github.io` under the `GhTara` account and upload this project's contents to its `main` branch. In repository **Settings → Pages**, choose **Deploy from a branch**, branch **main**, folder **/docs**. The site will be served at `https://ghtara.github.io/` after GitHub builds it. This repository and its photo/content become public when you make it public. Review the pages first.

The design draws on the restrained academic typography of al-folio, but uses a small independent static generator so the site stays focused and the source remains easy to edit.
