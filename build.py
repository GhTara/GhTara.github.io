#!/usr/bin/env python3
"""Build the static website from content/*.txt using Python's standard library."""

import argparse
import calendar
import configparser
from datetime import date
from html import escape
from pathlib import Path
import re
from string import Template
import sys
from textwrap import dedent, indent
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parent


def load_content(name):
    parser = configparser.ConfigParser(interpolation=None)
    with (ROOT / 'content' / f'{name}.txt').open(encoding='utf-8') as source:
        parser.read_file(source)
    return parser


def entries(content, kind):
    """Read ordered blocks such as [project:atpg] or [entry:carrot-cake]."""
    result = []
    for name in content.sections():
        if name.startswith(kind + ':'):
            identifier = name.split(':', 1)[1]
            if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', identifier):
                raise ValueError(f'[{name}]: use lowercase letters, numbers, and hyphens in identifiers.')
            result.append((identifier, content[name]))
    return result


def paragraphs(text):
    blocks = re.split(r'\n\s*\n', text.strip())
    return '\n'.join(f'<p>{escape(" ".join(block.split()))}</p>' for block in blocks if block.strip())


def safe_url(url):
    if not url or urlsplit(url).scheme.lower() not in ('', 'http', 'https', 'mailto'):
        raise ValueError(f'Unsupported link: {url!r}')
    return escape(url, quote=True)


def link(label, url, css='', accessible_label=''):
    attributes = f' class="{css}"' if css else ''
    if urlsplit(url).scheme in ('https', 'http'):
        attributes += ' target="_blank" rel="noopener noreferrer"'
    if accessible_label:
        attributes += f' aria-label="{escape(accessible_label)}"'
    return f'<a href="{safe_url(url)}"{attributes}>{escape(label)}</a>'


def asset(filename):
    path = (ROOT / filename).resolve()
    if ROOT not in path.parents or not path.is_file():
        raise ValueError(f'Missing local image: {filename}')
    return escape(filename, quote=True)


def entry_date(entry):
    value = entry['date']
    try:
        return date.fromisoformat(value + '-01' if len(value) == 7 else value)
    except ValueError as error:
        raise ValueError(f'[{entry.name}] date must be YYYY-MM or YYYY-MM-DD, got {value!r}.') from error


def date_label(entry):
    value = entry_date(entry)
    return f'{calendar.month_name[value.month]} {value.year}'


def page_head(page, extra=''):
    return f'''<header class="page-head">
  <h1>{escape(page['title'])}</h1>
  <p>{escape(page['introduction'])}</p>
  {extra}
</header>'''


def section_heading(title, identifier, extra=''):
    return f'<div class="section-heading"><h2 id="{identifier}">{escape(title)}</h2>{extra}</div>'


def render_home(home, research, journals):
    page = home['page']
    poem = home['poem']
    original = '<br>'.join(escape(line) for line in poem['persian'].strip().splitlines())
    translation = '<br>'.join(escape(line) for line in poem['english'].strip().splitlines())
    output = f'''<section class="hero" aria-labelledby="hello">
  <div class="hero-copy">
    <p class="eyebrow">{escape(page['role'])}</p>
    <h1 id="hello">{escape(page['greeting'])}</h1>
    <p class="lead">{escape(page['introduction'])}</p>
    {link(page['about_link'] + ' →', 'about.html', 'text-link')}
  </div>
  <figure class="portrait">
    <img src="{asset(page['photo'])}" alt="{escape(page['photo_alt'])}" width="1152" height="1536" fetchpriority="high">
  </figure>
</section>

<figure class="poetry-note" aria-label="A verse from {escape(poem['author'])}">
  <div class="verse-pair">
    <blockquote class="verse-original" lang="fa" dir="rtl" cite="{safe_url(poem['source'])}">
      <p>{original}</p>
    </blockquote>
    <blockquote class="verse-translation" lang="en" aria-label="English translation">
      <p>“{translation}”</p>
    </blockquote>
  </div>
  <figcaption>
    <a href="{safe_url(poem['source'])}" target="_blank" rel="noopener noreferrer"><bdi lang="fa">{escape(poem['author_persian'])}</bdi> · {escape(poem['author'])}, <cite>{escape(poem['book'])}</cite>, {escape(poem['volume'])} ↗</a>
  </figcaption>
</figure>

<section class="section" aria-labelledby="selected-research">
  {section_heading(page['research_heading'], 'selected-research', link(page['research_link'] + ' →', 'work.html', 'text-link'))}
  <div class="research-list">'''
    projects = dict(entries(research, 'project'))
    for identifier in page['selected_projects'].split(','):
        identifier = identifier.strip()
        if identifier not in projects:
            raise ValueError(f'home.txt: selected project {identifier!r} is missing from research.txt.')
        project = projects[identifier]
        actions = []
        for key, label in [('paper', 'Paper'), ('code', 'Code')]:
            if project.get(key):
                actions.append(link(label + ' ↗', project[key], accessible_label=f"{label}: {project['title']}"))
        title = project.get('short_title', project['title'])
        output += f'''
    <article class="research-row">
      <p class="row-year">{escape(project['year'])}</p>
      <div class="row-copy">
        <h3>{link(title, 'work.html#' + identifier)}</h3>
        <p>{escape(project['summary'])}</p>
      </div>
      <div class="row-meta">
        <span>{escape(project.get('short_venue', project['venue']))}</span>
        <div class="inline-links">{' '.join(actions)}</div>
      </div>
    </article>'''
    output += '\n  </div>\n</section>'

    notes = []
    for filename, journal in journals:
        for identifier, entry in entries(journal, 'entry'):
            notes.append((entry_date(entry), filename, identifier, entry, journal['page']['title']))
    if notes:
        _, filename, identifier, entry, journal_title = max(notes, key=lambda note: note[0])
        output += f'''

<section class="section notebook-section" aria-labelledby="notebook">
  {section_heading(page['notebook_heading'], 'notebook', link(journal_title + ' →', filename, 'text-link'))}
  <a class="notebook-link" href="{filename}#{identifier}">
    <span>{escape(entry.get('short_title', entry['title']))}</span>
    <span class="note-date"><time datetime="{escape(entry['date'])}">{date_label(entry)}</time><span aria-hidden="true">→</span></span>
  </a>
</section>'''
    return output


def detail_list(items):
    rows = [f"  <div><dt>{escape(item['title'])}</dt><dd>{escape(item['body'])}</dd></div>" for _, item in items]
    return '<dl class="detail-list">\n' + '\n'.join(rows) + '\n</dl>'


def render_research(content, site):
    page = content['page']
    projects = entries(content, 'project')
    jumps = link(page['projects_label'], '#' + projects[0][0]) if projects else ''
    jumps += link(page['ongoing_heading'], '#ongoing') + link(page['reading_heading'], '#publications')
    output = page_head(page, f'<nav class="jump-links" aria-label="On this page">{jumps}</nav>')
    for identifier, project in projects:
        actions = []
        if project.get('paper'):
            actions.append(link('Read paper ↗', project['paper']))
        if project.get('code'):
            actions.append(link('Code & documentation ↗', project['code']))
        citation = f'<p class="publication"><cite>{escape(project["paper_title"])}</cite></p>' if project.get('paper_title') else ''
        output += f'''

<article id="{identifier}" class="case-study">
  <header class="case-heading">
    <p class="case-meta">{escape(project['venue'])} · {escape(project['year'])}<span>{escape(project['credit'])}</span></p>
    <h2>{escape(project['title'])}</h2>
  </header>
  <div class="case-body">
    {paragraphs(project['body'])}
    {citation}
    <div class="project-links">{' '.join(actions)}</div>
  </div>'''
        if project.get('figure'):
            image = asset(project['figure'])
            output += f'''
  <figure class="research-figure">
    <a href="{image}" target="_blank" rel="noopener">
      <img src="{image}" alt="{escape(project['figure_alt'])}" loading="lazy">
    </a>
    <figcaption>{escape(project['figure_caption'])}</figcaption>
  </figure>'''
        output += '\n</article>'
    output += f'''
<section class="section" id="ongoing" aria-labelledby="ongoing-title">
  {section_heading(page['ongoing_heading'], 'ongoing-title')}
  {detail_list(entries(content, 'direction'))}
</section>
<section class="section" id="publications" aria-labelledby="further-reading">
  {section_heading(page['reading_heading'], 'further-reading', link(page['publications_link'] + ' ↗', site['scholar'], 'text-link'))}'''
    for _, publication in entries(content, 'publication'):
        output += f'<p class="additional-publication"><cite>{escape(publication["title"])}</cite> <span class="quiet">{escape(publication["venue"])}, {escape(publication["year"])}.</span></p>'
    output += f'<p class="quiet">{escape(page["archive_intro"])} {link(page["archive_link"] + " →", "code.html")}.</p>\n</section>'
    return output


def render_journal(content, personal=False):
    page = content['page']
    output = page_head(page)
    if personal:
        output = f'''<header class="page-head life-head">
  <div>
    <p class="persian-label" lang="fa" dir="rtl">{escape(page['persian_title'])}</p>
    <h1>{escape(page['title'])}</h1>
    <p class="life-intro">{escape(page['introduction'])}</p>
  </div>
  <img class="tile-motif" src="assets/persian-tile.svg" alt="" aria-hidden="true" width="160" height="160">
</header>'''
    notes = sorted(entries(content, 'entry'), key=lambda item: entry_date(item[1]), reverse=True)
    if not notes:
        output += f'<div class="empty-note"><p>{escape(page["empty_message"])}</p></div>'
    for identifier, entry in notes:
        source = ' · ' + escape(entry['source']) if entry.get('source') else ''
        action = link(entry.get('link_label', 'Read more') + ' ↗', entry['link']) if entry.get('link') else ''
        output += f'''
<article class="journal-entry" id="{identifier}">
  <p class="entry-meta"><time datetime="{escape(entry['date'])}">{date_label(entry)}</time>{source}</p>
  <h2>{escape(entry['title'])}</h2>
  {paragraphs(entry['body'])}
  {action}
</article>'''
    return output


def render_about(content):
    page = content['page']
    output = page_head(page) + f'<div class="prose biography">{paragraphs(page["biography"])}</div>'
    output += f'<section class="section" aria-labelledby="background">{section_heading(page["background_heading"], "background")}<dl class="timeline">'
    for _, item in entries(content, 'background'):
        output += f'<div><dt>{escape(item["date"])}</dt><dd><strong>{escape(item["title"])}</strong><span>{escape(item["place"])}</span></dd></div>'
    output += '</dl></section>'
    for kind, identifier in [('teaching', 'mentoring'), ('tools', 'tools')]:
        output += f'<section class="section" id="{identifier}" aria-labelledby="{kind}-title">{section_heading(page[kind + "_heading"], kind + "-title")}'
        if kind == 'teaching':
            output += f'<div class="prose">{paragraphs(page["teaching_introduction"])}</div>'
        output += detail_list(entries(content, kind)) + '</section>'
    return output


def render_code(content):
    page = content['page']
    output = page_head(page, link('← Research', 'work.html', 'back-link'))
    output += '<section class="section archive-section" aria-label="Earlier implementations">'
    for identifier, project in entries(content, 'project'):
        output += f'<article class="archive-entry" id="{identifier}"><h2>{escape(project["title"])}</h2>{paragraphs(project["body"])}{link("Code & documentation ↗", project["code"])}</article>'
    return output + f'</section><p class="archive-note">{escape(page["research_note"])} {link(page["research_link"], "work.html")}.</p>'


def build_pages():
    content = {name: load_content(name) for name in ('site', 'home', 'research', 'writing', 'life', 'about', 'code')}
    site = content['site']['site']
    labels = content['site']['navigation']
    template = Template((ROOT / 'templates' / 'page.html').read_text(encoding='utf-8'))
    bodies = {
        'home': render_home(content['home'], content['research'], [('writing.html', content['writing']), ('life.html', content['life'])]),
        'research': render_research(content['research'], site),
        'writing': render_journal(content['writing']),
        'life': render_journal(content['life'], personal=True),
        'about': render_about(content['about']),
        'code': render_code(content['code']),
    }
    pages = {}
    for name, body in bodies.items():
        page = content[name]['page']
        navigation = []
        for key, filename in [('research', 'work.html'), ('writing', 'writing.html'), ('life', 'life.html'), ('about', 'about.html')]:
            current = ' aria-current="page"' if name == key else ''
            navigation.append(f'          <a href="{filename}"{current}>{escape(labels[key])}</a>')
        values = {key: escape(value) for key, value in site.items()}
        for key in ('github', 'scholar', 'linkedin'):
            values[key] = safe_url(site[key])
        values.update(
            title=escape(page['title']), description=escape(page['description']),
            theme_color='#faf7ef' if name == 'life' else '#faf9f6',
            body_class=' class="life-page"' if name == 'life' else '',
            home_current=' aria-current="page"' if name == 'home' else '',
            navigation='\n'.join(navigation), content=indent(dedent(body).strip(), '      '),
        )
        filename = {'home': 'index', 'research': 'work'}.get(name, name) + '.html'
        pages[filename] = template.substitute(values)
    return pages


def main():
    arguments = argparse.ArgumentParser(description=__doc__)
    arguments.add_argument('--check', action='store_true', help='Check that the HTML matches the text files without writing files.')
    options = arguments.parse_args()
    try:
        pages = build_pages()
    except (configparser.Error, KeyError, ValueError, OSError) as error:
        print(f'Could not build the site: {error}', file=sys.stderr)
        return 1
    if options.check:
        stale = [name for name, html in pages.items() if not (ROOT / name).exists() or (ROOT / name).read_text(encoding='utf-8') != html]
        if stale:
            print('Run python3 build.py to update: ' + ', '.join(stale))
            return 1
        print('All six pages match the text files.')
        return 0
    for name, html in pages.items():
        (ROOT / name).write_text(html, encoding='utf-8')
    print('Updated all six pages. Open index.html to preview the site.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
