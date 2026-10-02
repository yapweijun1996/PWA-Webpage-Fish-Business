import sys, os, re, json
from bs4 import BeautifulSoup, NavigableString, Tag, Comment
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = {a['url']: a for a in json.load(open(os.path.join(ROOT,'source-audit','asset-inventory.json'),encoding='utf-8'))}
def dump(name):
    raw = open(os.path.join(ROOT,'source-audit','raw-html',name),'rb').read().decode('cp1252')
    soup = BeautifulSoup(raw,'lxml')
    body = soup.find('body')
    out=[]
    def walk(n):
        if isinstance(n,Comment): return
        if isinstance(n,NavigableString):
            t=re.sub(r'\s+',' ',str(n)).strip()
            if t and not t.startswith('<!--'): out.append(t)
        elif isinstance(n,Tag):
            if n.name=='img':
                s=n.get('src','')
                out.append(f"[IMG {s} {n.get('width','')}x{n.get('height','')} alt={n.get('alt')!r}]")
            elif n.name=='a' and n.get('href'):
                out.append(f"<A href={n['href']}>")
                for c in n.children: walk(c)
                out.append("</A>")
            else:
                if n.get('background'): out.append(f"[BG {n['background']}]")
                if n.name in('tr','br','p'): out.append('\n')
                for c in n.children: walk(c)
    walk(body)
    txt=' '.join(out)
    txt=re.sub(r' *\n *','\n',txt)
    txt=re.sub(r'\n+','\n',txt)
    return txt
if __name__=='__main__':
    for n in sys.argv[1:]:
        print('='*20,n); print(dump(n))
