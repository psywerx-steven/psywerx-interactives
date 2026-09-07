#!/usr/bin/env python3
"""Inline this self-contained homepage preview for double-click viewing."""
from pathlib import Path
import base64,mimetypes,re
R=Path(__file__).resolve().parents[1]
SITE=R.parent/'homepage-preview'
def uri(path):
 typ=mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
 return f'data:{typ};base64,'+base64.b64encode(path.read_bytes()).decode()
def make():
 text=(SITE/'index.html').read_text(encoding='utf-8')
 css=(SITE/'assets/home.css').read_text(encoding='utf-8').replace("url('brand-banner.webp')",f"url('{uri(SITE/'assets/brand-banner.webp')}')")
 text=text.replace('<link rel="stylesheet" href="assets/home.css">','<style>'+css+'</style>')
 for name in ('home-data.js','home.js'):
  script=(SITE/'assets'/name).read_text(encoding='utf-8').replace('</script','<\\/script')
  text=text.replace(f'  <script src="assets/{name}" defer></script>','')
  text=text.replace('</body>',f'<script>{script}</script>\n</body>')
 for f in (SITE/'assets').iterdir():
  if f.suffix in ('.webp','.png'):
   text=text.replace('"assets/'+f.name+'"','"'+uri(f)+'"')
 out=R/'qa/PSYWERX_Homepage_Preview.html'; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(text,encoding='utf-8')
 return out
if __name__=='__main__': print(make())
