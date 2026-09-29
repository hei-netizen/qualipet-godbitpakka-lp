#!/usr/bin/env python3
"""Bygger WP-versjon (wp:html) av Tyggepakke-PDP-en fra ../tyggepakke/index.html.
- Dropper egen topbar/header/footer (global Arcads-header/footer på qualipet.no)
- Bilder → WP-media (tyggepakke_media_map.txt), også i JS-dataene
- CSS scopet under #qtp; .section → .tsec (kolliderer med Flatsome .section{display:flex})
- JS via text/template + img-onload-bootstrap (WP Rocket delay-JS), ingen rå & i script
"""
import re, sys, pathlib
HERE = pathlib.Path(__file__).parent
SRC = HERE.parent / 'tyggepakke/index.html'
html = SRC.read_text()
media = {}
for line in (HERE / 'tyggepakke_media_map.txt').read_text().splitlines():
    p = line.split()
    media[p[0]] = p[2]

css = re.search(r'<style>(.*?)</style>', html, re.S).group(1)
body = re.search(r'<body>(.*)</body>', html, re.S).group(1)
js = re.search(r'<script>(.*?)</script>', body, re.S).group(1)
body = re.sub(r'<script>.*?</script>', '', body, count=1, flags=re.S)

# fjern egen topbar, header, footer
body = re.sub(r'<!-- Topbar: verbatim fra qualipet.no -->\s*<div class="topbar">.*?</div></div>', '', body, count=1, flags=re.S)
body = re.sub(r'<header class="hdr">.*?</header>', '', body, count=1, flags=re.S)
body = re.sub(r'<footer>.*?</footer>', '', body, count=1, flags=re.S)
body = re.sub(r'<!-- Høstsalg:[^>]*-->\s*<div class="salebar hs" hidden>.*?</div>', '', body, count=1, flags=re.S)
assert 'salebar' not in body
assert 'class="topbar"' not in body and '<header' not in body and '<footer' not in body
body = body.replace('<span class="nudge" id="hNudge">', '<span class="nudge" style="margin-top:2px">Slutter om <b data-cd>–</b></span><span class="nudge" id="hNudge">', 1)
body = body.replace('<main>', '<div class="tmain">').replace('</main>', '</div>')

def fix_imgs(s):
    def sub(m):
        name = m.group(1)
        if name not in media: sys.exit('Mangler media for ' + name)
        return media[name]
    return re.sub(r'img/([\w-]+\.jpg)', sub, s)
body = fix_imgs(body); js = fix_imgs(js)
assert 'img/' not in body.replace('<img', '') and "'img/" not in js

# .section → .tsec
body = re.sub(r'class="section', 'class="tsec', body)
css = re.sub(r'\.section\b', '.tsec', css)

# CSS: fjern kommentarer, topbar/hdr/footer-regler, scope under #qtp
css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
def scope_selector(sel):
    sel = sel.strip()
    if sel in (':root', 'body'): return '#qtp'
    if sel == 'html': return None
    if sel.startswith('footer') or sel.startswith('.topbar') or sel.startswith('.hdr'): return None
    if sel == '*': return '#qtp *'
    return '#qtp ' + sel
def scope_block(block):
    out, i, n = [], 0, len(block)
    while i < n:
        j = block.find('{', i)
        if j < 0: break
        sel = block[i:j].strip()
        depth, k = 1, j + 1
        while k < n and depth:
            if block[k] == '{': depth += 1
            elif block[k] == '}': depth -= 1
            k += 1
        inner = block[j+1:k-1]
        if sel.startswith('@media'):
            b = scope_block(inner)
            if b.strip(): out.append(f'{sel}{{{b}}}\n')
        elif sel.startswith('@'):
            out.append(f'{sel}{{{inner}}}\n')
        else:
            sels = [s for s in (scope_selector(x) for x in sel.split(',')) if s]
            if sels: out.append(f'{",".join(sels)}{{{inner}}}\n')
        i = k
    return ''.join(out)
css = scope_block(css)

reset = '''
#qtp{display:block;width:100%}
#qtp .tsec{display:block;min-height:0;align-items:initial}
#qtp h1,#qtp h2,#qtp h3,#qtp h4{font-family:var(--f)!important;text-transform:none!important;margin:0;color:inherit;letter-spacing:-0.02em}
#qtp .pdp-head h1 .hl,#qtp h1 .hl{color:var(--orange)}
#qtp .about h2{color:#fff}
#qtp,#qtp p,#qtp a,#qtp span,#qtp li,#qtp label,#qtp button,#qtp summary,#qtp q,#qtp small,#qtp b{font-family:var(--f)}
#qtp p{margin:0}
#qtp ul{margin:0;padding:0}
#qtp li{margin:0}
#qtp img{margin:0;display:block;max-width:100%}
#qtp a:not(.cta):not(.go){color:inherit}
#qtp button{margin:0;text-transform:none;letter-spacing:0;min-height:0;font-weight:inherit;line-height:1.15;box-shadow:none}
#qtp .cta{color:#fff!important;border-radius:999px;min-height:0;text-transform:none;margin:0}
#qtp .cta:hover{color:#fff!important}
#qtp .gal-thumbs button{border-radius:12px;padding:0;background:#fff}
#qtp .morebtn{border-radius:999px;color:var(--green)}
#qtp .morebtn:hover{color:#fff}
#qtp label{font-weight:inherit;font-size:inherit;margin:0;display:block}
#qtp input[type=radio]{position:absolute;opacity:0;pointer-events:none;margin:0}
#qtp details{margin:0;padding:0}
#qtp details summary{list-style:none;margin:0}
#qtp details summary::-webkit-details-marker{display:none}
#qtp q:before,#qtp q:after{content:none}
#qtp .pricebox .was,#qtp .cmpc .pr s{text-decoration:line-through}
#qtp .stars svg{display:inline-block}
'''

assert '&' not in js, 'rå & i script'
boot = ("(function(){if(window.__qtpI)return;window.__qtpI=1;var t=document.getElementById('qtp-src');if(!t)return;"
        "var s=document.createElement('script');s.textContent=t.textContent;document.body.appendChild(s);})()")
bootstrap = (f'<script type="text/template" id="qtp-src">{js}</script>'
             '<img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7" alt="" width="1" height="1" '
             'data-no-lazy="1" loading="eager" decoding="sync" style="position:absolute;width:1px;height:1px;opacity:0;pointer-events:none" '
             f'onload="{boot}" onerror="{boot}">')
FONT = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap">'
page = f'''<!-- wp:html -->
<!-- ARCADS – TYGGEPAKKE-PDP (S/M/L) for qualipet.no · Mal: page-blank.php · Kilde: ~/arcads/sites/qualipet-godbitpakka-lp/tyggepakke/index.html → wp/build_tyggepakke_wp.py -->
<div id="qtp">
{FONT}
<style>
{css}{reset}
</style>
{body.strip()}
{bootstrap}
</div>
<!-- /wp:html -->
'''
(HERE / 'tyggepakke-wp.html').write_text(page)
print('OK', len(page))
