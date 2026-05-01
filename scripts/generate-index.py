#!/usr/bin/env python3
"""
Auto-generates skills/index.json by scanning all skills/<category>/*.md files
and parsing their Metadata table. Run by GitHub Actions on every push.
"""

import os
import json
import re

SKILLS_DIR = os.path.join(os.path.dirname(__file__), '..', 'skills')

EMOJI_MAP = {
    'developer': '🛠️',
    'security': '🔒',
    'data': '📊',
    'writing': '✍️',
    'architecture': '🏗️',
    'devops': '⚙️',
    'productivity': '🧩',
    'creative': '🎨',
}

def parse_metadata(content):
    """Extract values from the Metadata table."""
    meta = {}
    # Match | **Key** | Value | table rows
    for m in re.finditer(r'\|\s*\*\*(.+?)\*\*\s*\|\s*(.+?)\s*\|', content):
        key = m.group(1).strip().lower().replace(' ', '_')
        val = m.group(2).strip()
        meta[key] = val
    return meta

def extract_title_and_desc(content):
    """Get title from # heading and description from > blockquote."""
    title_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
    desc_match  = re.search(r'^>\s+(.+)', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else ''
    desc  = desc_match.group(1).strip()  if desc_match  else ''
    return title, desc

def slug(title):
    """Convert title like '🔍 Code Reviewer' to 'code-reviewer'."""
    t = re.sub(r'[^\w\s-]', '', title).strip().lower()
    return re.sub(r'[\s_]+', '-', t).strip('-')

def main():
    skills = []

    for category in sorted(os.listdir(SKILLS_DIR)):
        cat_path = os.path.join(SKILLS_DIR, category)
        if not os.path.isdir(cat_path):
            continue

        for filename in sorted(os.listdir(cat_path)):
            if not filename.endswith('.md'):
                continue

            filepath = os.path.join(cat_path, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            title, description = extract_title_and_desc(content)
            meta = parse_metadata(content)

            difficulty  = meta.get('difficulty', '⭐')
            works_with  = meta.get('works_with', 'Claude.ai, Claude Code, API')
            tokens      = meta.get('estimated_tokens', 'unknown')

            name = slug(title) if title else filename.replace('.md', '')
            emoji = EMOJI_MAP.get(category, '⚡')

            skills.append({
                'name': name,
                'title': title,
                'category': category,
                'emoji': emoji,
                'description': description,
                'difficulty': difficulty,
                'works_with': [w.strip() for w in works_with.split(',')],
                'tokens': tokens,
                'path': f'skills/{category}/{filename}'
            })
            print(f"  + [{category}] {title}")

    output_path = os.path.join(os.path.dirname(__file__), '..', 'skills', 'index.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(skills, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Generated {len(skills)} skills → skills/index.json")

if __name__ == '__main__':
    main()
