"""Apply a trusted AI × WPS patch ZIP: manifest.json and files/ tree."""
import sys, json, zipfile, shutil, tempfile, datetime, os
from pathlib import Path
ROOT=Path(__file__).resolve().parent
if len(sys.argv)!=2: sys.exit('Usage: python update.py /path/to/patch.zip')
allowed={'app.py','platform_pages.py','ai_wps_engine.py','educational_content.py','reporting.py','ai_advisor.py','ardin_map.html','requirements.txt','README.md','.streamlit/config.toml'}
with zipfile.ZipFile(Path(sys.argv[1]).expanduser()) as z:
    m=json.loads(z.read('manifest.json')); current=(ROOT/'VERSION').read_text().strip()
    if m['from_version']!=current: sys.exit(f'Patch requires {m["from_version"]}; installed {current}')
    version=m['to_version']; names=m['files']
    if not isinstance(version,str) or not version or not names or len(set(names))!=len(names): sys.exit('Invalid manifest')
    for n in names:
        p=Path(n)
        if p.is_absolute() or '..' in p.parts or not (n in allowed or n.startswith(('assets/images/','assets/maps/','scenarios/'))): sys.exit(f'Forbidden patch path: {n}')
        if not (ROOT/p).resolve().is_relative_to(ROOT): sys.exit('Unsafe destination')
    backup=ROOT/'backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'); backup.mkdir(parents=True)
    with tempfile.TemporaryDirectory() as t:
        stage=Path(t)
        for n in names:
            p=stage/n; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(z.read('files/'+n))
            if p.suffix=='.py': compile(p.read_bytes(),n,'exec')
        existing=[]
        for n in names+['VERSION']:
            p=ROOT/n
            if p.exists():
                b=backup/n; b.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,b); existing.append(n)
        try:
            for n in names:
                p=ROOT/n; p.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(stage/n,p)
            (ROOT/'VERSION').write_text(version+'\n')
        except BaseException:
            for n in names+['VERSION']:
                p=ROOT/n
                if n in existing: shutil.copy2(backup/n,p)
                elif p.exists(): p.unlink()
            raise
    print(f'Updated {current} → {version}. Backup: {backup}')
