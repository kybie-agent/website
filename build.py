#!/usr/bin/env python3
"""Parse awesome-ky readme.md and generate a static searchable page."""
import re, html, json

SRC = "readme.md"

def esc(s):
    return html.escape(s, quote=True)

sections = []
current = None
entry_re = re.compile(r'^(\t*)- \[(.+?)\]\((.+?)\)(?: - (.*))?$')
plain_re = re.compile(r'^(\t*)- ([^\[].*)$')

def safe_url(u):
    u = u.strip()
    if re.match(r'^https?://', u, re.I):
        return u
    return None

with open(SRC, encoding="utf-8") as f:
    for line in f:
        line = line.rstrip("\n")
        m = re.match(r'^## (.+)$', line)
        if m:
            title = m.group(1).strip()
            if title.lower() == "contents":
                current = None
                continue
            current = {"title": title, "entries": []}
            sections.append(current)
            continue
        if current is None:
            continue
        m = entry_re.match(line)
        if m:
            depth = len(m.group(1))
            name, url, desc = m.group(2).strip(), m.group(3).strip(), (m.group(4) or "").strip()
            url = safe_url(url)
            if url is None:
                continue
            current["entries"].append({"name": name, "url": url, "desc": desc, "depth": min(depth, 2)})
            continue
        m = plain_re.match(line)
        if m:
            depth = len(m.group(1))
            rest = m.group(2).strip()
            if " - " in rest:
                name, desc = rest.split(" - ", 1)
            else:
                name, desc = rest, ""
            current["entries"].append({"name": name.strip(), "url": None, "desc": desc.strip(), "depth": min(depth, 2)})

sections = [s for s in sections if s["entries"]]
print(f"{len(sections)} sections, {sum(len(s['entries']) for s in sections)} entries")

def slug(t):
    return re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')

nav_chips = "\n".join(
    f'      <a class="chip" href="#{slug(s["title"])}">{esc(s["title"])} <span class="count">{len(s["entries"])}</span></a>'
    for s in sections
)

body_sections = []
for s in sections:
    items = []
    for e in s["entries"]:
        name = esc(e["name"])
        desc = f'<span class="desc">{esc(e["desc"])}</span>' if e["desc"] else ""
        if e["url"]:
            link = f'<a href="{esc(e["url"])}" target="_blank" rel="noopener noreferrer">{name}</a>'
        else:
            link = f'<span class="plain">{name}</span>'
        items.append(f'        <li class="d{e["depth"]}">{link}{(" " + desc) if desc else ""}</li>')
    body_sections.append(
        f'    <section id="{slug(s["title"])}" data-section>\n'
        f'      <h2>{esc(s["title"])}</h2>\n'
        f'      <ul>\n' + "\n".join(items) + "\n      </ul>\n    </section>"
    )
body = "\n".join(body_sections)

page = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Awesome Lists &mdash; amazonian.help</title>
<meta name="description" content="A curated directory of awesome lists on every topic, served from amazonian.help">
<style>
:root{--bg:#ffffff;--fg:#1a1a1a;--muted:#5b5b5b;--accent:#e8750a;--card:#f6f6f4;--line:#e6e6e2;--chip:#f0efec}
@media(prefers-color-scheme:dark){:root{--bg:#141412;--fg:#ececea;--muted:#a9a9a4;--card:#1d1d1b;--line:#2c2c29;--chip:#232320}}
[data-theme="dark"]{--bg:#141412;--fg:#ececea;--muted:#a9a9a4;--card:#1d1d1b;--line:#2c2c29;--chip:#232320}
[data-theme="light"]{--bg:#ffffff;--fg:#1a1a1a;--muted:#5b5b5b;--card:#f6f6f4;--line:#e6e6e2;--chip:#f0efec}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;line-height:1.55}
header.top{position:sticky;top:0;z-index:10;background:var(--bg);border-bottom:1px solid var(--line);padding:14px 20px}
.wrap{max-width:1060px;margin:0 auto}
.brand{font-size:13px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
h1{margin:4px 0 2px;font-size:30px;letter-spacing:-.01em}
.sub{color:var(--muted);margin:0 0 12px;font-size:15px}
.searchrow{display:flex;gap:10px;align-items:center}
#q{flex:1;padding:11px 14px;font-size:16px;border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--fg)}
#q:focus{outline:2px solid var(--accent);border-color:var(--accent)}
#theme{background:var(--chip);border:1px solid var(--line);color:var(--fg);border-radius:10px;padding:10px 12px;cursor:pointer;font-size:15px}
nav.chips{display:flex;flex-wrap:wrap;gap:8px;padding:16px 20px 4px}
.chip{text-decoration:none;color:var(--fg);background:var(--chip);border:1px solid var(--line);border-radius:999px;padding:6px 12px;font-size:13px}
.chip:hover{border-color:var(--accent)}
.chip .count{color:var(--muted);font-size:12px;margin-left:4px}
main{padding:8px 20px 60px}
section{margin-top:34px}
section h2{font-size:22px;margin:0 0 10px;padding-bottom:8px;border-bottom:2px solid var(--accent);display:inline-block}
ul{list-style:none;margin:0;padding:0}
li{padding:7px 0;border-bottom:1px solid var(--line)}
li.d1{margin-left:26px}
li.d2{margin-left:52px}
li a{color:var(--fg);font-weight:600;text-decoration:none;border-bottom:1px dotted var(--muted)}
li a:hover{color:var(--accent);border-bottom-color:var(--accent)}
.desc{color:var(--muted)}
.plain{font-weight:600}
#noresults{display:none;text-align:center;color:var(--muted);padding:40px 0}
footer{border-top:1px solid var(--line);padding:22px 20px;color:var(--muted);font-size:13px}
footer a{color:var(--muted)}
</style>
</head>
<body>
<header class="top">
  <div class="wrap">
    <div class="brand">amazonian.help</div>
    <h1>&#x2728; Awesome Lists</h1>
    <p class="sub">A curated directory of awesome lists on every topic. Search it all below.</p>
    <div class="searchrow">
      <input id="q" type="search" placeholder="Search 700+ lists&hellip;" autocomplete="off" aria-label="Search lists">
      <button id="theme" aria-label="Toggle dark mode">&#x1f319;</button>
    </div>
  </div>
</header>
<div class="wrap">
<nav class="chips" aria-label="Categories">
""" + nav_chips + """
</nav>
<main>
""" + body + """
<div id="noresults">No lists match your search.</div>
</main>
</div>
<footer>
  <div class="wrap">
    Content curated from the <a href="https://github.com/kybie-agent/awesome-ky" target="_blank" rel="noopener noreferrer">awesome-ky</a> list
    (a fork of <a href="https://github.com/sindresorhus/awesome" target="_blank" rel="noopener noreferrer">sindresorhus/awesome</a>).
    Served from amazonian.help &mdash; this page makes zero external requests and sets no cookies.
  </div>
</footer>
<script>
(function(){
  var q=document.getElementById('q'),nr=document.getElementById('noresults'),t=0;
  function norm(s){return s.toLowerCase()}
  q.addEventListener('input',function(){
    clearTimeout(t);
    t=setTimeout(function(){
      var needle=norm(q.value.trim()),shown=0;
      document.querySelectorAll('[data-section]').forEach(function(sec){
        var vis=0;
        sec.querySelectorAll('li').forEach(function(li){
          var hit=!needle||norm(li.textContent).indexOf(needle)>-1;
          li.style.display=hit?'':'none';
          if(hit)vis++;
        });
        sec.style.display=vis?'':'none';
        if(vis)shown++;
      });
      nr.style.display=shown?'none':'block';
    },120);
  });
  var btn=document.getElementById('theme'),root=document.documentElement;
  function setIcon(){btn.innerHTML=root.getAttribute('data-theme')==='dark'?'&#x2600;&#xfe0f;':'&#x1f319;'}
  try{
    var saved=localStorage.getItem('ah-theme');
    if(saved)root.setAttribute('data-theme',saved);
  }catch(e){}
  setIcon();
  btn.addEventListener('click',function(){
    var cur=root.getAttribute('data-theme');
    var dark=cur?cur!=='dark':window.matchMedia('(prefers-color-scheme: dark)').matches;
    var next=dark?'light':'dark';
    root.setAttribute('data-theme',next);
    try{localStorage.setItem('ah-theme',next)}catch(e){}
    setIcon();
  });
})();
</script>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(page)
with open("CNAME", "w") as f:
    f.write("amazonian.help\n")
print("wrote index.html + CNAME")
