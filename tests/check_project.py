from pathlib import Path
from html.parser import HTMLParser
import re, sys
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'src'))
from guide_content import SECTIONS,FLOW
class Parser(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.ids=[];self.links=[];self.codes=[];self.active=False;self.buf=[]
 def handle_starttag(self,t,a):
  a=dict(a)
  if 'id' in a:self.ids.append(a['id'])
  if t=='a':self.links.append(a['href'])
  if t in ('script','img','iframe','link'):assert 'src' not in a and 'href' not in a
  if t=='code':self.active=True;self.buf=[]
 def handle_data(self,d):
  if self.active:self.buf.append(d)
 def handle_endtag(self,t):
  if t=='code':self.codes.append(''.join(self.buf));self.active=False
p=Parser();html=(root/'docs/index.html').read_text(encoding='utf-8');p.feed(html)
assert len(p.ids)==len(set(p.ids))
assert len(FLOW)==19
for url in p.links:
 if url.startswith('#'):assert url[1:] in p.ids
assert p.codes==[v['text'] for s in SECTIONS for k,v in s['blocks'] if k=='code']
for f in root.rglob('*'):
 if not f.is_file() or '.git' in f.parts or '__pycache__' in f.parts:continue
 assert f.suffix.lower() not in {'.bin','.itb','.fip','.zip','.exe','.pcap','.log'}
 text=f.read_text(encoding='utf-8-sig')
 assert not re.search(r'[A-Za-z0-9._+-]+@(?:16900|16300)\.',text),f
 assert not re.search(r'(?:C:|c:)[/\\]Users[/\\]',text),f
 assert not re.search(r'(?i)(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})',text),f
print('PASS: offline HTML, anchors, code text and generic privacy checks')
