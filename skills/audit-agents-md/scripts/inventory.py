#!/usr/bin/env python3
"""Inventory instruction files without executing them or changing source roots."""
import argparse
import collections
import hashlib
import json
import os
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

try:
    import yaml
except ImportError:
    yaml = None

SKIP = {'.git', 'node_modules', '.venv', 'venv', '__pycache__', '.cache',
        '.pytest_cache', '.mypy_cache', '.ruff_cache'}


def frontmatter(text):
    match = re.match(r'\A---\s*\n(.*?)\n---\s*(?:\n|\Z)', text, re.S)
    if not match:
        return {}, 'missing'
    if yaml is None:
        return {}, 'parser_unavailable'
    try:
        value = yaml.safe_load(match.group(1))
        if not isinstance(value, dict):
            return {}, 'invalid_mapping'
        return value, 'parsed'
    except yaml.YAMLError:
        # Parser errors can quote source values, including secrets.
        return {}, 'parse_error'


def missing_links(path, text):
    candidates = []
    fence = None
    for number, line in enumerate(text.splitlines(), 1):
        token = re.match(r'^\s{0,3}(`{3,}|~{3,})', line)
        if token:
            marker = token.group(1)
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence):
                fence = None
            continue
        if fence:
            continue
        for item in re.finditer(r'\[[^\]]*\]\((<[^>]+>|[^)]+)\)', line):
            raw = item.group(1).strip()
            target = raw[1:-1] if raw.startswith('<') else re.split(r'\s+[\"\']', raw, maxsplit=1)[0]
            if target.startswith('#') or re.match(r'^[A-Za-z][A-Za-z0-9+.-]*:', target):
                continue
            if target in {'...', 'url', '链接'} or any(c in target for c in '*${}<>'):
                continue
            target = unquote(urlsplit(target).path)
            if not target:
                continue
            candidate = Path(target).expanduser()
            if not candidate.is_absolute():
                candidate = path.parent / candidate
            try:
                exists = candidate.exists()
            except (OSError, RuntimeError):
                exists = False
            if not exists:
                candidates.append({'line': number, 'target': target})
    return candidates


def collect(roots, include_claude=False):
    names = {'skill.md', 'agents.md', 'agents.override.md'}
    if include_claude:
        names.add('claude.md')
    documents, events, visited = {}, [], set()
    linked_directories = set()

    def visit(path, ancestors):
        key = str(path.absolute())
        if key in visited:
            return
        visited.add(key)
        try:
            real = path.resolve(strict=True)
        except (OSError, RuntimeError) as error:
            kind = 'broken_or_cyclic_symlink' if path.is_symlink() else 'unreadable_or_missing'
            events.append({'path': key, 'kind': kind, 'error_type': type(error).__name__})
            return
        try:
            if path.is_dir():
                if path.is_symlink():
                    linked_directories.add(str(real))
                if str(real) in ancestors:
                    events.append({'path': key, 'resolved_path': str(real), 'kind': 'directory_cycle'})
                    return
                for child in sorted(path.iterdir()):
                    if child.name in SKIP and child.is_dir():
                        continue
                    visit(child, ancestors | {str(real)})
                return
            if path.name.lower() not in names or not path.is_file():
                return
            raw = path.read_bytes()
            text = raw.decode('utf-8-sig')
        except (OSError, UnicodeError) as error:
            events.append({'path': key, 'kind': 'read_error', 'error_type': type(error).__name__})
            return
        fm, status = frontmatter(text)
        policy_path = path.parent / 'agents/openai.yaml'
        invocation = 'unspecified'
        policy_status = 'absent'
        if path.name.lower() == 'skill.md' and policy_path.exists():
            if yaml is None:
                policy_status = 'parser_unavailable'
            else:
                try:
                    data = yaml.safe_load(policy_path.read_text(encoding='utf-8-sig'))
                    if not isinstance(data, dict) or not isinstance(data.get('policy', {}), dict):
                        policy_status = 'invalid_mapping'
                    else:
                        policy_status = 'parsed'
                        value = data.get('policy', {}).get('allow_implicit_invocation')
                        invocation = value if isinstance(value, bool) else 'unspecified'
                except (OSError, UnicodeError, yaml.YAMLError):
                    policy_status = 'read_or_parse_error'
        name = fm.get('name')
        documents[key] = {
            'path': key, 'resolved_path': str(real), 'kind': path.name,
            'name': name if isinstance(name, str) else None,
            'bytes': len(raw), 'characters': len(text), 'lines': len(text.splitlines()),
            'sha256': hashlib.sha256(raw).hexdigest(),
            'frontmatter_status': status if path.name.lower() == 'skill.md' else 'not_applicable',
            'description_characters': len(fm['description']) if isinstance(fm.get('description'), str) else None,
            'declares_manual_only': fm.get('disable-model-invocation') is True,
            'codex_allow_implicit_invocation': invocation,
            'codex_policy_status': policy_status,
            'missing_link_candidates': missing_links(path, text),
            'review_status': 'static_scan_only',
        }

    for root in roots:
        visit(Path(root).expanduser().absolute(), set())
    docs = sorted(documents.values(), key=lambda d: d['path'])
    real_groups, name_groups, hash_groups = (collections.defaultdict(list) for _ in range(3))
    for doc in docs:
        real_groups[doc['resolved_path']].append(doc['path'])
        hash_groups[doc['sha256']].append(doc['path'])
        if doc['name']:
            name_groups[doc['name']].append(doc['path'])
    return {
        'roots': [str(Path(r).expanduser().absolute()) for r in roots],
        'excluded_directory_names': sorted(SKIP),
        'linked_directory_targets': sorted(linked_directories),
        'yaml_parser_available': yaml is not None,
        'documents': docs, 'events': events,
        'aliases': {k: v for k, v in real_groups.items() if len(v) > 1},
        'same_name_candidates': {k: v for k, v in name_groups.items() if len(v) > 1},
        'same_content_candidates': {k: v for k, v in hash_groups.items() if len(v) > 1},
        'summary': {'logical_documents': len(docs), 'physical_documents': len(real_groups),
                    'skill_entries': sum(d['kind'].lower() == 'skill.md' for d in docs),
                    'events': len(events)},
        'limits': ['Static inventory, not semantic or runtime validation.',
                   'Missing inline Markdown links are candidates; inspect context.',
                   'Same names and hashes do not prove redundant installations.',
                   'Character counts are not tokens or runtime context usage.'],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument('--root', action='append', help='Explicit directory or instruction file; repeatable')
    scope.add_argument('--global', dest='global_scope', action='store_true', help='Personal skill roots and global instruction files')
    parser.add_argument('--include-claude', action='store_true')
    parser.add_argument('--output', type=Path, help='New JSON file outside the audited roots; otherwise stdout')
    args = parser.parse_args()
    roots = args.root or []
    if args.global_scope:
        home = Path.home()
        codex = Path(os.environ.get('CODEX_HOME') or home / '.codex').expanduser()
        roots = [home / '.agents/skills', codex / 'skills']
        companions = [home / 'AGENTS.md', home / 'AGENTS.override.md',
                      home / '.agents/AGENTS.md', home / '.agents/AGENTS.override.md',
                      codex / 'AGENTS.md', codex / 'AGENTS.override.md']
        if args.include_claude:
            companions += [home / 'CLAUDE.md', codex / 'CLAUDE.md']
        roots += [p for p in companions if p.exists() or p.is_symlink()]
    if args.output:
        output = args.output.expanduser().resolve()
        for root in roots:
            try:
                real = Path(root).expanduser().resolve()
            except (OSError, RuntimeError):
                continue  # collect() reports the inaccessible root.
            if output == real or real in output.parents:
                parser.error('--output must be outside audited roots')
        if output.exists():
            parser.error('--output already exists; choose a new file')
        if not output.parent.is_dir():
            parser.error('--output parent directory must already exist')
    result = collect(roots, args.include_claude)
    if args.output:
        for target in result['linked_directory_targets']:
            real = Path(target)
            if output == real or real in output.parents:
                parser.error('--output must be outside followed source directories')
    payload = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        with output.open('x', encoding='utf-8') as stream:
            stream.write(payload)
        print(json.dumps({'output': str(output), **result['summary']}, ensure_ascii=False))
    else:
        print(payload, end='')


if __name__ == '__main__':
    main()
