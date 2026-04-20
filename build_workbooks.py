#!/usr/bin/env python3
"""Build both workbook HTMLs from Markdown sources."""

import re
import shutil
import sys
from pathlib import Path

# ═══════════════════════════════════════════════════
# CSS – shared by both workbooks
# ═══════════════════════════════════════════════════

CSS = r"""
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { font-size: 16px; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif; background: #f0f0f0; color: #1a1a1a; line-height: 1.7; -webkit-font-smoothing: antialiased; }
.page-container { max-width: 820px; margin: 0 auto; background: #fff; box-shadow: 0 0 40px rgba(0,0,0,0.08); min-height: 100vh; }
.content { padding: 0 48px 60px; }

/* NAV */
.nav { position: sticky; top: 0; z-index: 100; background: #1a1a1a; padding: 12px 48px; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; border-bottom: 3px solid #E53935; }
.nav a { color: #fff; text-decoration: none; font-size: 0.78rem; font-weight: 500; padding: 4px 10px; border-radius: 4px; transition: all 0.2s; white-space: nowrap; }
.nav a:hover { background: #E53935; color: #fff; }
.nav-brand { font-weight: 700; color: #E53935 !important; font-size: 0.85rem !important; margin-right: 12px; }

/* COVER */
.cover { background: #1a1a1a; color: #fff; padding: 60px 48px 50px; text-align: center; position: relative; overflow: hidden; }
.cover::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: #E53935; }
.cover-title { font-size: 2.2rem; font-weight: 800; margin-bottom: 10px; letter-spacing: -0.5px; line-height: 1.2; }
.cover-subtitle { font-size: 1.1rem; color: #ccc; font-weight: 300; margin-bottom: 24px; }
.cover-line { width: 60px; height: 3px; background: #E53935; margin: 0 auto; }
.cover-badge { display: inline-block; background: #E53935; color: #fff; padding: 6px 18px; border-radius: 20px; font-size: 0.85rem; font-weight: 600; margin-top: 18px; }

/* PREFACE */
.preface { background: #fafafa; border-left: 4px solid #E53935; padding: 32px 36px; margin: 40px 0; border-radius: 0 8px 8px 0; }
.preface h3 { color: #E53935; font-size: 1.2rem; margin-bottom: 16px; }
.preface p { color: #444; font-style: italic; line-height: 1.8; margin-bottom: 12px; }
.preface .author { font-style: normal; font-weight: 600; color: #1a1a1a; margin-top: 16px; }

/* ABOUT */
.about-section { background: #f9f9f9; padding: 36px; border-radius: 12px; margin: 32px 0; border: 1px solid #eee; }
.about-title { font-size: 1.5rem; color: #1a1a1a; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 2px solid #E53935; }

/* TOC */
.toc-section { margin: 32px 0; padding: 36px; background: #fff; border: 2px solid #1a1a1a; border-radius: 12px; }
.toc-title { font-size: 1.5rem; color: #1a1a1a; margin-bottom: 20px; text-align: center; padding-bottom: 12px; border-bottom: 2px solid #E53935; }

/* EXERCISE CARDS */
.exercise-card { background: #fff; border: 1px solid #e5e5e5; border-radius: 12px; padding: 32px; margin: 28px 0; box-shadow: 0 2px 12px rgba(0,0,0,0.04); transition: box-shadow 0.2s; page-break-inside: avoid; }
.exercise-card:hover { box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
.exercise-header { display: flex; align-items: center; gap: 16px; padding-bottom: 14px; border-bottom: 2px solid #E53935; margin-bottom: 20px; }
.exercise-title { font-size: 1.25rem; font-weight: 700; color: #1a1a1a; margin-bottom: 0; flex: 1; }
.exercise-meta { display: flex; gap: 16px; margin-bottom: 16px; flex-wrap: wrap; }
.exercise-meta span { font-size: 0.85rem; color: #666; }

/* HEADINGS INSIDE CARDS */
.detail-title { font-size: 1.05rem; font-weight: 700; color: #E53935; margin: 24px 0 12px; }
.subsection-title { font-size: 1.1rem; font-weight: 700; color: #333; margin: 24px 0 12px; }

/* SELLING LINE */
.selling-line { background: #fef7f7; border-left: 4px solid #E53935; padding: 14px 20px; margin: 0 0 20px; border-radius: 0 8px 8px 0; font-style: italic; color: #555; }
.selling-line p { margin: 0; }

/* TYPOGRAPHY */
p { margin-bottom: 14px; line-height: 1.7; color: #333; }
strong { font-weight: 700; color: #1a1a1a; }
em { font-style: italic; }
a { color: #E53935; text-decoration: none; border-bottom: 1px solid transparent; transition: border-color 0.2s; }
a:hover { border-bottom-color: #E53935; }
.inline-code { background: #f5f5f5; padding: 2px 6px; border-radius: 4px; font-family: 'SF Mono','Fira Code','Consolas',monospace; font-size: 0.88em; color: #E53935; border: 1px solid #e8e8e8; }

/* LISTS */
.bullet-list, .numbered-list { margin: 12px 0 16px 24px; }
.bullet-list li, .numbered-list li { padding: 4px 0; line-height: 1.7; color: #333; }
.bullet-list li::marker { color: #E53935; }
.numbered-list li::marker { color: #E53935; font-weight: 600; }

/* CHECKLISTS */
.checklist { list-style: none; margin: 12px 0 16px 0; padding: 0; }
.checklist-item { padding: 8px 12px; margin: 4px 0; background: #fafafa; border-radius: 6px; border: 1px solid #eee; }
.checklist-item label { display: flex; align-items: flex-start; gap: 10px; cursor: pointer; }
.checklist-item input[type="checkbox"] { margin-top: 4px; width: 18px; height: 18px; accent-color: #E53935; flex-shrink: 0; }

/* CODE */
.code-block { background: #1a1a2e; border-radius: 8px; margin: 16px 0; overflow-x: auto; border: 1px solid #333; }
.code-block pre { padding: 20px; margin: 0; }
.code-block code { font-family: 'SF Mono','Fira Code','Consolas',monospace; font-size: 0.85rem; color: #e0e0e0; line-height: 1.6; white-space: pre-wrap; word-break: break-word; }

/* TABLES */
.table-wrapper { overflow-x: auto; margin: 16px 0; border-radius: 8px; border: 1px solid #e5e5e5; }
.data-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
.data-table th { background: #1a1a1a; color: #fff; padding: 12px 16px; text-align: left; font-weight: 600; font-size: 0.85rem; }
.data-table td { padding: 10px 16px; border-bottom: 1px solid #eee; color: #333; }
.data-table tbody tr:hover { background: #fafafa; }
.data-table tbody tr:nth-child(even) { background: #f9f9f9; }

/* SPECIAL BLOCKS */
.warning-block { background: #fff3e0; border-left: 4px solid #ff9800; padding: 16px 20px; margin: 16px 0; border-radius: 0 8px 8px 0; }
.warning-block p { margin: 0; color: #e65100; font-weight: 500; }
.tip-block { background: #e8f5e9; border-left: 4px solid #4caf50; padding: 16px 20px; margin: 16px 0; border-radius: 0 8px 8px 0; }
.tip-block p { margin: 0; color: #2e7d32; font-weight: 500; }

/* IMAGES */
.accent-image, .accent-image-left { width: 48px; flex-shrink: 0; opacity: 0.45; transition: opacity 0.3s; }
.accent-image:hover, .accent-image-left:hover { opacity: 0.8; }
.accent-image img, .accent-image-left img { width: 100%; height: auto; display: block; }
.diagram-image { text-align: center; margin: 24px auto; max-width: 380px; }
.diagram-image img { width: 100%; height: auto; opacity: 0.85; border-radius: 4px; }
.img-caption { font-size: 0.78rem; color: #aaa; text-align: center; margin-top: 4px; font-style: italic; }
@media print { .accent-image, .accent-image-left { display: none; } }

/* DIVIDERS */
.divider { border: none; height: 1px; background: #e5e5e5; margin: 32px 0; }

/* RESOURCES */
.resources-section { margin: 40px 0; padding: 32px; background: #f9f9f9; border-radius: 12px; border: 1px solid #eee; }
.resources-title { margin-bottom: 20px; padding-bottom: 12px; border-bottom: 2px solid #E53935; }

/* CONCLUSION */
.conclusion-section { margin: 48px 0 0; padding: 48px 40px 40px; background: #fafafa; border-top: 3px solid #E53935; }
.conclusion-icon { font-size: 2.4rem; margin-bottom: 8px; text-align: center; }
.conclusion-heading { font-size: 1.6rem; font-weight: 800; color: #1a1a1a; margin-bottom: 8px; letter-spacing: -0.3px; text-align: center; }
.conclusion-lead { color: #555; font-size: 1.05rem; margin-bottom: 32px; text-align: center; }
.conclusion-columns { display: flex; gap: 32px; text-align: left; max-width: 560px; margin: 0 auto 32px; }
.conclusion-col { flex: 1; }
.conclusion-col h4 { font-size: 0.9rem; font-weight: 700; color: #E53935; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #e0e0e0; }
.conclusion-col p { font-size: 0.9rem; color: #555; margin-bottom: 8px; line-height: 1.5; }
.conclusion-cta { font-size: 1rem; font-weight: 600; color: #1a1a1a; padding-top: 24px; border-top: 1px solid #e0e0e0; }

/* FOOTER */
.footer { text-align: center; padding: 24px; color: #999; font-size: 0.82rem; border-top: 1px solid #eee; margin-top: 40px; }

/* RESPONSIVE */
@media (max-width: 860px) {
    .content { padding: 0 24px 40px; }
    .nav { padding: 10px 24px; }
    .cover { padding: 40px 24px; }
    .exercise-card { padding: 24px; }
    .about-section, .toc-section, .resources-section { padding: 24px; }
    .accent-image, .accent-image-left { width: 36px; }
}
@media (max-width: 480px) {
    .content { padding: 0 16px 32px; }
    .cover-title { font-size: 1.6rem; }
    .nav { gap: 4px; }
    .nav a { font-size: 0.7rem; padding: 3px 6px; }
    .conclusion-columns { flex-direction: column; gap: 20px; }
}

/* PRINT */
@page { size: A4; margin: 20mm 15mm 25mm 15mm; @bottom-center { content: counter(page); font-size: 9pt; color: #999; } }
@media print {
    body { background: #fff; }
    .page-container { max-width: 100%; box-shadow: none; }
    .nav { display: none; }
    .content { padding: 0 10px 20px; }
    .cover { padding: 40px 20px; page-break-after: always; }
    .exercise-card { page-break-inside: avoid; box-shadow: none; border: 1px solid #ccc; }
    .code-block { background: #f5f5f5 !important; border: 1px solid #ddd; }
    .code-block code { color: #333 !important; }
    a { color: #333 !important; }
}
"""

# ═══════════════════════════════════════════════════
# IMAGE MAP – which images go where
# ═══════════════════════════════════════════════════

# For Sešit 1
SESIT1_IMAGES = {
    1: ("accent-image", "images/01.png"),       # Cvičení 1 – quick access
    2: ("accent-image-left", "images/05.png"),  # Cvičení 2 – prompt generator
    3: ("accent-image", "images/09.png"),       # Cvičení 3 – find tool
    5: ("accent-image-left", "images/14.png"),  # Cvičení 5 – data
    6: ("accent-image", "images/17.png"),       # Cvičení 6 – 3C
    7: ("accent-image-left", "images/20.png"),  # Cvičení 7 – assistants
    8: ("accent-image", "images/24.png"),       # Cvičení 8 – setup
}

# For Sešit 1 v2 (exercises 0–9, decorative images reused)
SESIT1_V2_IMAGES = {
    1: ("accent-image", "images/01.png"),
    2: ("accent-image-left", "images/05.png"),
    3: ("accent-image", "images/09.png"),
    5: ("accent-image-left", "images/14.png"),
    6: ("accent-image", "images/17.png"),
    7: ("accent-image-left", "images/20.png"),
    8: ("accent-image", "images/24.png"),
    9: ("accent-image-left", "images/03.png"),
}

# For Sešit 2
SESIT2_IMAGES = {
    1: ("accent-image", "images/03.png"),
    2: ("accent-image-left", "images/07.png"),
    3: ("accent-image", "images/11.png"),
    4: ("accent-image-left", "images/15.png"),
    5: ("accent-image", "images/22.png"),
    6: ("accent-image-left", "images/26.png"),
}


def slugify(text):
    """Create a URL-safe slug from text."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    text = text.strip('-')
    return text


def md_inline(text):
    """Convert inline Markdown to HTML."""
    # Bold + italic
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # Inline code
    text = re.sub(r'`([^`]+)`', r'<span class="inline-code">\1</span>', text)
    # Links
    text = re.sub(r'\[([^\]]+)\]\((https?://[^\)]+)\)', r'<a href="\2" target="_blank">\1</a>', text)
    # Auto-link bare URLs
    text = re.sub(r'(?<!["\'>])(https?://[^\s<\)]+)', r'<a href="\1" target="_blank">\1</a>', text)
    return text


# Czech preface (Filip tone: direct, practical, first person)
PREFACE_CS = """
            <h3>📝 Předmluva</h3>
            <p>Milí čtenáři,</p>
            <p>když jsem psal knihu <strong>Budoucnost nepráce</strong>, měl jsem jednu věc jasnou: samotné čtení vás neposune tak rychle jako jeden odvážný experiment. Teorie je důležitá — ale teprve když si něco zkusíte na vlastní soubory, vlastní emaily a vlastní chaos v hlavě, začne to dávat smysl.</p>
            <p>Proto existuje tento (ne)pracovní sešit. Není to další teorie. Jsou to úkoly, které můžete udělat dnes odpoledne: nastavit si nástroje, napsat první pořádný prompt, porovnat dva chatboty na stejném zadání, nebo si postavit mini-systém pro informace. Přesně to dělám i já — neustále zkouším, co funguje, a co je jen hype.</p>
            <p>Nemusíte jít cvičení za cvičením jako po přesném seznamu. Klidně přeskočte, co už umíte, a vracejte se k tomu, co vás pálí. Důležité je, abyste si odnášeli <em>konkrétní výsledek</em> — záložku, šablonu, fungující automatizaci, ne jen pocit, že jste „něco četli o AI“.</p>
            <p>A když to nepůjde napoprvé? Normální. AI je nástroj — a jako každý nástroj ho musíte chytit za správný konec. Čím víc si budete hrát, tím dřív zjistíte, kde vám šetří čas a kde vám naopak bere pozornost.</p>
            <p>Přeji vám hodně malých vítězství, pár překvapení a hlavně chuť to zkoušet v praxi.</p>
            <p class="author">— Filip Dřímalka</p>
"""

# English preface (aligned with Filip’s public voice: practical, optimistic, no corporate fluff)
PREFACE_EN = """
            <h3>📝 Foreword</h3>
            <p>Hi there,</p>
            <p>When I wrote <strong>The Future of No Work</strong>, one thing was clear to me: reading alone won’t move you as fast as a single bold experiment. Ideas matter — but they click when you try them on your own files, your own inbox, and your own messy real-life context.</p>
            <p>That’s why this workbook exists. It’s not more theory to “consume.” It’s a set of tasks you can actually do this afternoon: set up your tools, write a proper prompt, run the same task in two different assistants, or sketch a simple system for how you capture information. That’s what I do too — I’m constantly testing what’s real and what’s just hype.</p>
            <p>You don’t have to follow the exercises in perfect order. Skip what you already know. Come back to what hurts. The point is to walk away with something <em>concrete</em> — a bookmark, a template, a working automation — not just the feeling that you “read something about AI.”</p>
            <p>And if it doesn’t work on the first try? Totally normal. AI is a tool — and like any tool, you learn where it saves you time and where it steals your attention.</p>
            <p>Here’s to small wins, a few surprises, and the habit of learning in practice.</p>
            <p class="author">— Filip Dřímalka</p>
"""


def convert_md_to_html(
    md_content,
    images_map,
    title,
    subtitle,
    badge,
    footer_text,
    *,
    locale="cs",
    cover_title=None,
    preface_html=None,
    nav_home_href="workbook-repo/index.html",
):
    """Convert a workbook Markdown to styled HTML. locale: 'cs' or 'en'.

    nav_home_href: link for the workbook title in the top nav (rozcestník).
    Default points from WORKBOOKS/*.html to workbook-repo/index.html; use index.html for files deployed inside workbook-repo.
    """
    lines = md_content.split('\n')
    if cover_title is None:
        cover_title = "Budoucnost nepráce" if locale == "cs" else "The Future of No Work"
    if preface_html is None:
        preface_html = PREFACE_CS if locale == "cs" else PREFACE_EN
    lang = "cs" if locale == "cs" else "en"
    ex_word = "Cvičení" if locale == "cs" else "Exercise"
    nav_prefix = "Cv." if locale == "cs" else "Ex."
    toc_title = "📋 Obsah" if locale == "cs" else "📋 Contents"
    conclusion_heading = "Závěr" if locale == "cs" else "Conclusion"
    rights = "© 2025 Filip Dřímalka · Všechna práva vyhrazena" if locale == "cs" else "© 2026 Filip Drimalka · All rights reserved"
    html_parts = []
    
    in_code_block = False
    code_lines = []
    in_table = False
    table_rows = []
    in_list = False
    list_type = None
    list_items = []
    in_checklist = False
    checklist_items = []
    exercise_num = 0
    exercise_open = False
    in_resources = False
    in_toc_section = False

    def flush_list():
        nonlocal in_list, list_type, list_items
        if not list_items:
            in_list = False
            return
        tag = 'ol' if list_type == 'ol' else 'ul'
        cls = 'numbered-list' if list_type == 'ol' else 'bullet-list'
        html_parts.append(f'<{tag} class="{cls}">')
        for item in list_items:
            html_parts.append(f'  <li>{md_inline(item)}</li>')
        html_parts.append(f'</{tag}>')
        in_list = False
        list_items = []

    def flush_checklist():
        nonlocal in_checklist, checklist_items
        if not checklist_items:
            in_checklist = False
            return
        html_parts.append('<ul class="checklist">')
        for item in checklist_items:
            html_parts.append(f'  <li class="checklist-item"><label><input type="checkbox"> {md_inline(item)}</label></li>')
        html_parts.append('</ul>')
        in_checklist = False
        checklist_items = []

    def flush_table():
        nonlocal in_table, table_rows
        if len(table_rows) < 2:
            in_table = False
            table_rows = []
            return
        html_parts.append('<div class="table-wrapper"><table class="data-table">')
        # Header
        headers = [c.strip() for c in table_rows[0].strip('|').split('|')]
        html_parts.append('<thead><tr>')
        for h in headers:
            html_parts.append(f'  <th>{md_inline(h)}</th>')
        html_parts.append('</tr></thead>')
        # Body (skip separator row)
        html_parts.append('<tbody>')
        for row in table_rows[2:]:
            cells = [c.strip() for c in row.strip('|').split('|')]
            html_parts.append('<tr>')
            for col_idx, c in enumerate(cells):
                # In TOC section: make the exercise name column (index 1) a link
                if in_toc_section and col_idx == 1 and len(cells) >= 2:
                    # Determine exercise number from first cell
                    try:
                        ex_n = int(cells[0].strip())
                        html_parts.append(f'  <td><a href="#cviceni-{ex_n}" style="color:#E53935;text-decoration:none;font-weight:600;">{md_inline(c)}</a></td>')
                    except ValueError:
                        html_parts.append(f'  <td>{md_inline(c)}</td>')
                else:
                    html_parts.append(f'  <td>{md_inline(c)}</td>')
            html_parts.append('</tr>')
        html_parts.append('</tbody></table></div>')
        in_table = False
        table_rows = []

    # Build navigation items (exercises)
    nav_items = []
    toc_items = []
    ex_pat = re.compile(r'^## (?:Cvičení|Exercise) (\d+): (.+)$')
    for line in lines:
        m = ex_pat.match(line)
        if m:
            num = int(m.group(1))
            name = m.group(2).strip()
            slug = f'cviceni-{num}'
            nav_items.append((slug, f'{nav_prefix} {num}'))
            toc_items.append((slug, f'{ex_word} {num}: {name}'))

    # Build HTML
    for i, line in enumerate(lines):
        stripped = line.strip()

        # Skip the top-level title and subtitle (handled by cover)
        if i < 6 and (
            stripped.startswith('# ')
            or (
                stripped.startswith('## ')
                and (
                    'Pro každého' in stripped
                    or 'Pro manažery' in stripped
                    or 'Od teorie' in stripped
                    or 'For everyone' in stripped
                    or 'For managers' in stripped
                    or 'From theory' in stripped
                )
            )
        ):
            continue

        # Code blocks
        if stripped.startswith('```'):
            if in_code_block:
                html_parts.append('<div class="code-block"><pre><code>' + '\n'.join(code_lines) + '</code></pre></div>')
                code_lines = []
                in_code_block = False
            else:
                flush_list()
                flush_checklist()
                in_code_block = True
            continue
        if in_code_block:
            code_lines.append(line.replace('<', '&lt;').replace('>', '&gt;'))
            continue

        # Horizontal rules → dividers
        if stripped == '---':
            flush_list()
            flush_checklist()
            flush_table()
            if exercise_open:
                html_parts.append('</div><!-- /exercise-card -->')
                exercise_open = False
            if in_resources:
                html_parts.append('</div><!-- /resources -->')
                in_resources = False
            in_toc_section = False
            html_parts.append('<hr class="divider">')
            continue

        # Tables
        if stripped.startswith('|') and '|' in stripped[1:]:
            flush_list()
            flush_checklist()
            if not in_table:
                in_table = True
                table_rows = []
            table_rows.append(stripped)
            continue
        elif in_table:
            flush_table()

        # Checklist items
        if stripped.startswith('- [ ] ') or stripped.startswith('- [x] '):
            flush_list()
            if not in_checklist:
                in_checklist = True
                checklist_items = []
            checklist_items.append(stripped[6:])
            continue
        elif in_checklist and not stripped.startswith('- ['):
            flush_checklist()

        # List items
        m_ul = re.match(r'^[-*] (.+)$', stripped)
        m_ol = re.match(r'^(\d+)\. (.+)$', stripped)
        if m_ul and not stripped.startswith('- [ ]'):
            flush_checklist()
            if not in_list or list_type != 'ul':
                flush_list()
                in_list = True
                list_type = 'ul'
            list_items.append(m_ul.group(1))
            continue
        elif m_ol:
            flush_checklist()
            if not in_list or list_type != 'ol':
                flush_list()
                in_list = True
                list_type = 'ol'
            list_items.append(m_ol.group(2))
            continue
        elif in_list and stripped == '':
            flush_list()
            continue
        elif in_list and not m_ul and not m_ol:
            flush_list()

        # Empty lines
        if stripped == '':
            continue

        # Exercise headers
        m_ex = ex_pat.match(stripped)
        if m_ex:
            flush_list()
            flush_checklist()
            flush_table()
            if exercise_open:
                html_parts.append('</div><!-- /exercise-card -->')
            in_toc_section = False
            exercise_num = int(m_ex.group(1))
            ex_title = m_ex.group(2)
            slug = f'cviceni-{exercise_num}'
            html_parts.append(f'<div class="exercise-card" id="{slug}">')
            # Wrap image + title in flex header
            html_parts.append('<div class="exercise-header">')
            if exercise_num in images_map:
                img_cls, img_src = images_map[exercise_num]
                html_parts.append(f'<div class="{img_cls}"><img src="{img_src}" alt="" loading="lazy"></div>')
            html_parts.append(f'<h2 class="exercise-title">{ex_word} {exercise_num}: {md_inline(ex_title)}</h2>')
            html_parts.append('</div><!-- /exercise-header -->')
            exercise_open = True
            continue

        # Blockquote (selling line)
        if stripped.startswith('> '):
            text = stripped[2:].strip()
            html_parts.append(f'<div class="selling-line"><p>{md_inline(text)}</p></div>')
            continue

        # h3 headings
        m_h3 = re.match(r'^### (.+)$', stripped)
        if m_h3:
            flush_list()
            flush_checklist()
            heading = m_h3.group(1).strip()
            slug = slugify(heading)
            if heading.startswith('📋'):
                # TOC table section — enable clickable rows
                in_toc_section = True
                html_parts.append(f'<div class="toc-section" id="{slug}">')
                html_parts.append(f'<h3 class="toc-title" style="font-size:1.3rem">{md_inline(heading)}</h3>')
            elif heading.startswith('💭'):
                in_toc_section = False
                html_parts.append(f'<h3 class="detail-title" id="{slug}">{md_inline(heading)}</h3>')
            elif heading.startswith('Krok') or heading.startswith('Step '):
                in_toc_section = False
                html_parts.append(f'<h3 class="subsection-title" id="{slug}">{md_inline(heading)}</h3>')
            else:
                in_toc_section = False
                html_parts.append(f'<h3 class="subsection-title" id="{slug}">{md_inline(heading)}</h3>')
            continue

        # h2 headings (section headers)
        m_h2 = re.match(r'^## (.+)$', stripped)
        if m_h2:
            flush_list()
            flush_checklist()
            flush_table()
            if exercise_open:
                html_parts.append('</div><!-- /exercise-card -->')
                exercise_open = False
            heading = m_h2.group(1).strip()
            slug = slugify(heading)
            
            if heading.startswith('📖'):
                html_parts.append(f'<div class="about-section" id="{slug}">')
                html_parts.append(f'<h2 class="about-title">{md_inline(heading)}</h2>')
                in_toc_section = False
                # Auto-close later
            elif heading.startswith('📋'):
                html_parts.append(f'<div class="toc-section" id="{slug}">')
                html_parts.append(f'<h2 class="toc-title">{md_inline(heading)}</h2>')
                in_toc_section = True
            elif heading.startswith('📚'):
                if in_resources:
                    html_parts.append('</div>')
                in_toc_section = False
                in_resources = True
                html_parts.append(f'<div class="resources-section" id="{slug}">')
                html_parts.append(f'<h2 class="resources-title">{md_inline(heading)}</h2>')
            elif heading.startswith('🎓'):
                html_parts.append(f'<div class="conclusion-section" id="{slug}">')
                html_parts.append(f'<div class="conclusion-icon">🎓</div>')
                html_parts.append(f'<h2 class="conclusion-heading">{conclusion_heading}</h2>')
            else:
                html_parts.append(f'<h2 class="subsection-title" id="{slug}">{md_inline(heading)}</h2>')
            continue

        # Warning blocks
        if stripped.startswith('⚠️'):
            html_parts.append(f'<div class="warning-block"><p>{md_inline(stripped)}</p></div>')
            continue

        # Tip blocks
        if stripped.startswith('💡'):
            html_parts.append(f'<div class="tip-block"><p>{md_inline(stripped)}</p></div>')
            continue

        # Regular paragraphs
        html_parts.append(f'<p>{md_inline(stripped)}</p>')

    # Close any open elements
    flush_list()
    flush_checklist()
    flush_table()
    if exercise_open:
        html_parts.append('</div><!-- /exercise-card -->')
    if in_resources:
        html_parts.append('</div><!-- /resources -->')

    body_html = '\n'.join(html_parts)

    # Build navigation (brand → rozcestník / hub)
    nav_html = f'<a href="{nav_home_href}" class="nav-brand">📖 {badge}</a>\n'
    for slug, label in nav_items:
        nav_html += f'    <a href="#{slug}">{label}</a>\n'

    # TOC is rendered inline from the ## 📋 section in the markdown (with clickable links).
    # No separate auto-generated TOC block needed.
    toc_html = ''

    # Assemble full HTML
    html = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
{CSS}
    </style>
</head>
<body>
<div class="page-container">
    <nav class="nav">
        {nav_html}
    </nav>

    <div class="cover">
        <h1 class="cover-title">{cover_title}</h1>
        <p class="cover-subtitle">{subtitle}</p>
        <div class="cover-line"></div>
        <div class="cover-badge">{badge}</div>
    </div>

    <div class="content">
        <div class="preface">
{preface_html}
        </div>

        {toc_html}

        {body_html}
    </div>

    <div class="footer">
        <p>{footer_text}</p>
        <p>{rights}</p>
    </div>
</div>
</body>
</html>"""

    return html


def _html_for_repo_deploy(html: str) -> str:
    """Paths inside workbook-repo: hub is index.html at the same level as sešit HTML."""
    return html.replace('href="workbook-repo/index.html"', 'href="index.html"')


def main():
    # Read Markdown sources (same folder as this script)
    base = Path(__file__).resolve().parent

    md1 = (base / 'SESIT 1 - Pro kazdeho.md').read_text(encoding='utf-8')
    md2 = (base / 'SESIT 2 - Pro manazery.md').read_text(encoding='utf-8')

    # Build Sešit 1
    html1 = convert_md_to_html(
        md1,
        images_map=SESIT1_IMAGES,
        title='Budoucnost nepráce — (ne)pracovní sešit · Pro každého',
        subtitle='(ne)pracovní sešit — od teorie k praxi',
        badge='Pro každého',
        footer_text='Budoucnost nepráce — (ne)pracovní sešit · Pro každého · Od teorie k praxi'
    )
    
    out1 = base / 'SESIT 1 - Pro kazdeho - KOMPLETNI.html'
    out1.write_text(html1, encoding='utf-8')
    print(f'✅ Sešit 1: {out1}  ({len(html1)} chars, {html1.count(chr(10))} lines)')

    # Build Sešit 1 v2
    md1v2_path = base / 'SESIT 1 - Pro kazdeho - v2.md'
    html1v2 = None
    if md1v2_path.is_file():
        md1v2 = md1v2_path.read_text(encoding='utf-8')
        html1v2 = convert_md_to_html(
            md1v2,
            images_map=SESIT1_V2_IMAGES,
            title='Budoucnost nepráce — (ne)pracovní sešit · Pro každého · v2',
            subtitle='(ne)pracovní sešit — od teorie k praxi · vylepšená verze',
            badge='Pro každého · v2',
            footer_text='Budoucnost nepráce — (ne)pracovní sešit · Pro každého · v2 · Od teorie k praxi'
        )
        out1v2 = base / 'SESIT 1 - Pro kazdeho - v2 - KOMPLETNI.html'
        out1v2.write_text(html1v2, encoding='utf-8')
        print(f'✅ Sešit 1 v2: {out1v2}  ({len(html1v2)} chars, {html1v2.count(chr(10))} lines)')
        deploy_v2 = base / 'sesit-1-pro-kazdeho-v2.html'
        deploy_v2.write_text(_html_for_repo_deploy(html1v2), encoding='utf-8')
        print(f'📎 Deploy: {deploy_v2.name}')

    # Build Sešit 2
    html2 = convert_md_to_html(
        md2,
        images_map=SESIT2_IMAGES,
        title='Budoucnost nepráce — (ne)pracovní sešit · Pro manažery a lídry',
        subtitle='(ne)pracovní sešit — pro manažery a lídry',
        badge='Pro manažery',
        footer_text='Budoucnost nepráce — (ne)pracovní sešit · Pro manažery a lídry · Od teorie k praxi'
    )

    out2 = base / 'SESIT 2 - Pro manazery - KOMPLETNI.html'
    out2.write_text(html2, encoding='utf-8')
    print(f'✅ Sešit 2: {out2}  ({len(html2)} chars, {html2.count(chr(10))} lines)')

    # Build Sešit 2 v2
    md2v2_path = base / 'SESIT 2 - Pro manazery - v2.md'
    html2v2 = None
    if md2v2_path.is_file():
        md2v2 = md2v2_path.read_text(encoding='utf-8')
        html2v2 = convert_md_to_html(
            md2v2,
            images_map=SESIT2_IMAGES,
            title='Budoucnost nepráce — (ne)pracovní sešit · Pro manažery a lídry · v2',
            subtitle='(ne)pracovní sešit — pro manažery a lídry · vylepšená verze',
            badge='Pro manažery · v2',
            footer_text='Budoucnost nepráce — (ne)pracovní sešit · Pro manažery a lídry · v2 · Od teorie k praxi'
        )
        out2v2 = base / 'SESIT 2 - Pro manazery - v2 - KOMPLETNI.html'
        out2v2.write_text(html2v2, encoding='utf-8')
        print(f'✅ Sešit 2 v2: {out2v2}  ({len(html2v2)} chars, {html2v2.count(chr(10))} lines)')
        deploy_v2_2 = base / 'sesit-2-pro-manazery-v2.html'
        deploy_v2_2.write_text(_html_for_repo_deploy(html2v2), encoding='utf-8')
        print(f'📎 Deploy: {deploy_v2_2.name}')

    # English HTML v1 (from SESIT 1 - For everyone.md / SESIT 2 - For managers.md)
    md1_en = base / 'SESIT 1 - For everyone.md'
    md2_en = base / 'SESIT 2 - For managers.md'
    html1_en = None
    html2_en = None
    if md1_en.is_file():
        html1_en = convert_md_to_html(
            md1_en.read_text(encoding='utf-8'),
            images_map=SESIT1_IMAGES,
            title='The Future of No Work — Workbook · For everyone',
            subtitle='Workbook — from theory to practice',
            badge='For everyone',
            footer_text='The Future of No Work — Workbook · For everyone · From theory to practice',
            locale='en',
        )
        out1e = base / 'SESIT 1 - For everyone - COMPLETE.html'
        out1e.write_text(html1_en, encoding='utf-8')
        print(f'✅ Workbook 1 (EN): {out1e}')

    if md2_en.is_file():
        html2_en = convert_md_to_html(
            md2_en.read_text(encoding='utf-8'),
            images_map=SESIT2_IMAGES,
            title='The Future of No Work — Workbook · For managers and leaders',
            subtitle='Workbook — for managers and leaders',
            badge='For managers',
            footer_text='The Future of No Work — Workbook · For managers and leaders · From theory to practice',
            locale='en',
        )
        out2e = base / 'SESIT 2 - For managers - COMPLETE.html'
        out2e.write_text(html2_en, encoding='utf-8')
        print(f'✅ Workbook 2 (EN): {out2e}')

    # English HTML v2
    md1_en_v2 = base / 'SESIT 1 - For everyone - v2.md'
    md2_en_v2 = base / 'SESIT 2 - For managers - v2.md'
    html1_en_v2 = None
    html2_en_v2 = None
    if md1_en_v2.is_file():
        html1_en_v2 = convert_md_to_html(
            md1_en_v2.read_text(encoding='utf-8'),
            images_map=SESIT1_V2_IMAGES,
            title='The Future of No Work — Workbook · For Everyone · v2',
            subtitle='Workbook — from theory to practice · improved edition',
            badge='For Everyone · v2',
            footer_text='The Future of No Work — Workbook · For Everyone · From theory to practice',
            locale='en',
        )
        out1e_v2 = base / 'SESIT 1 - For everyone - v2 - COMPLETE.html'
        out1e_v2.write_text(html1_en_v2, encoding='utf-8')
        print(f'✅ Workbook 1 v2 (EN): {out1e_v2}  ({len(html1_en_v2)} chars)')
        deploy_en_v2_1 = base / 'sesit-1-for-everyone-v2.html'
        deploy_en_v2_1.write_text(_html_for_repo_deploy(html1_en_v2), encoding='utf-8')
        print(f'📎 Deploy: {deploy_en_v2_1.name}')

    if md2_en_v2.is_file():
        html2_en_v2 = convert_md_to_html(
            md2_en_v2.read_text(encoding='utf-8'),
            images_map=SESIT2_IMAGES,
            title='The Future of No Work — Workbook · For Managers and Leaders · v2',
            subtitle='Workbook — for managers and leaders · improved edition',
            badge='For Managers · v2',
            footer_text='The Future of No Work — Workbook · For Managers and Leaders · From theory to practice',
            locale='en',
        )
        out2e_v2 = base / 'SESIT 2 - For managers - v2 - COMPLETE.html'
        out2e_v2.write_text(html2_en_v2, encoding='utf-8')
        print(f'✅ Workbook 2 v2 (EN): {out2e_v2}  ({len(html2_en_v2)} chars)')
        deploy_en_v2_2 = base / 'sesit-2-for-managers-v2.html'
        deploy_en_v2_2.write_text(_html_for_repo_deploy(html2_en_v2), encoding='utf-8')
        print(f'📎 Deploy: {deploy_en_v2_2.name}')

    # Deploy copies: same HTML as canonical names in workbook-repo/ (direct URLs on Vercel)
    repo = base / 'workbook-repo'
    if repo.is_dir():
        deploy = [
            (html1, 'sesit-1-pro-kazdeho.html'),
            (html2, 'sesit-2-pro-manazery.html'),
        ]
        if html1v2:
            deploy.append((html1v2, 'sesit-1-pro-kazdeho-v2.html'))
        if html1_en:
            deploy.append((html1_en, 'sesit-1-for-everyone.html'))
        if html2_en:
            deploy.append((html2_en, 'sesit-2-for-managers.html'))
        if html1_en_v2:
            deploy.append((html1_en_v2, 'sesit-1-for-everyone-v2.html'))
        if html2_en_v2:
            deploy.append((html2_en_v2, 'sesit-2-for-managers-v2.html'))
        for content, name in deploy:
            dest = repo / name
            dest.write_text(_html_for_repo_deploy(content), encoding='utf-8')
            print(f'📎 Repo: {dest.name}')
        images_src = base / 'images'
        images_dst = repo / 'images'
        if images_src.is_dir():
            shutil.copytree(images_src, images_dst, dirs_exist_ok=True)
            print(f'📎 Repo: images/ synced')


if __name__ == '__main__':
    main()
