"""Syntax, local Markdown file-link and release hygiene checks; no Rhino needed."""
import ast
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote


def check(root=None):
    root = Path(root) if root else Path(__file__).resolve().parents[1]
    errors = []
    files = [p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    for p in files:
        rel = p.relative_to(root).as_posix()
        if p.suffix == '.py':
            try: ast.parse(p.read_text(encoding='utf-8'),filename=rel)
            except SyntaxError as e: errors.append(rel+': '+str(e))
        if p.suffix == '.md':
            content = p.read_text(encoding='utf-8')
            for target in re.findall(r'\]\(([^)]+)\)',content):
                target = unquote(target.split('#',1)[0].strip('<>'))
                if not target or '://' in target: continue
                if not (p.parent/target).is_file():errors.append(rel+': missing link '+target)
            if re.search(r'[A-Z]:[\\/]',content):errors.append(rel+': machine-specific absolute path')
        if p.suffix.lower() in {'.pdf','.png','.jpg','.jpeg','.pyc'}:
            errors.append(rel+': non-release media/cache file')
    skill = (root/'SKILL.md').read_text(encoding='utf-8')
    if not skill.startswith('---\nname: rhino-mcp-surface-skill\n'):
        errors.append('Invalid skill frontmatter/name')
    manifest = [{'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,
                 'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
                for p in sorted(files) if p.name!='release-manifest.json']
    result = {'passed':not errors,'file_count':len(files),'errors':errors,'files':manifest}
    if errors: raise AssertionError(json.dumps(result,ensure_ascii=False))
    return result


if __name__ == '__main__':
    result = check()
    print(json.dumps({'passed':result['passed'],'file_count':result['file_count'],
                      'errors':result['errors']},ensure_ascii=False))
