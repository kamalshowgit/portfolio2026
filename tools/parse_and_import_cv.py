#!/usr/bin/env python3
import os, sys, re
# ensure project root is on path
sys.path.insert(0, os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE','siteproject.settings')
import django
django.setup()
from personal.models import Profile, Experience, Education
pfile = os.path.join(os.getcwd(), 'cv_extracted.txt')
if not os.path.exists(pfile):
    print('cv_extracted.txt not found')
    sys.exit(1)
with open(pfile, encoding='utf-8') as f:
    text = f.read()
text = re.sub(r'--- PAGE \d+ ---\n', '', text)
# helpers
def get_section(name):
    m = re.search(rf"{name}", text)
    if not m:
        return ''
    start = m.end()
    # look for next all-caps heading line
    m2 = re.search(r"\n([A-Z][A-Z &]{2,})\n", text[start:])
    end = m2.start() + start if m2 else len(text)
    return text[start:end].strip()
exp_block = get_section('EXPERIENCE')
edu_block = get_section('EDUCATION')
print('EXPERIENCE BLOCK LEN', len(exp_block))
print('EDUCATION BLOCK LEN', len(edu_block))
# parse experiences
lines = [ln.strip() for ln in exp_block.split('\n') if ln.strip()]
entries = []
cur = None
month_rx = re.compile(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s?\d{4}', re.I)
for i, line in enumerate(lines):
    if month_rx.search(line):
        # if previous line looks like company (short), use it
        employer = lines[i-1] if i>0 and len(lines[i-1].split())<7 else ''
        meta = line
        cur = {'employer': employer or line, 'meta': meta, 'desc': []}
        entries.append(cur)
    else:
        # bullet lines or continuation
        if cur is None:
            # if line looks like company in uppercase, start new
            if line.isupper() and len(line.split())<8:
                cur = {'employer': line, 'meta': '', 'desc': []}
                entries.append(cur)
            else:
                continue
        else:
            cur['desc'].append(line)
# fallback
if not entries and exp_block:
    entries = [{'employer':'Experience','meta':'','desc':[exp_block]}]
# save
profile = Profile.objects.first()
if not profile:
    print('NO PROFILE; create one first')
    sys.exit(1)
created_exp = 0
for e in entries:
    employer = e['employer'][:200]
    meta = e['meta']
    desc = '\n'.join(e['desc']).strip()
    # parse meta
    title = ''
    location = ''
    start = ''
    end = ''
    dr = re.search(r'((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s?\d{4})\s*[–-]\s*(Present|\w+\s?\d{4})', meta)
    if dr:
        start = dr.group(1)
        end = dr.group(3)
    # split title/location if em dash present
    if '—' in meta:
        parts = meta.split('—',1)
        title = parts[0].strip()
        location = parts[1].strip()
    exp = Experience.objects.create(profile=profile, employer=employer, title=title, location=location, start=start, end=end, description=desc)
    created_exp += 1
print('Created experiences:', created_exp)
# parse education
edu_lines = [ln.strip() for ln in edu_block.split('\n') if ln.strip()]
edus = []
current = None
year_rx = re.compile(r'\b(19|20)\d{2}\b')
for line in edu_lines:
    y = year_rx.search(line)
    if y:
        inst = line
        current = {'institution':inst, 'degree':'', 'year':y.group(0), 'details':''}
        edus.append(current)
    else:
        if current:
            if not current['degree']:
                current['degree'] = line
            else:
                current['details'] += '\n' + line
        else:
            # stray line
            edus.append({'institution':line, 'degree':'', 'year':'', 'details':''})
created_edu = 0
for ed in edus:
    Education.objects.create(profile=profile, institution=ed['institution'][:300], degree=ed['degree'][:300], year=ed['year'][:20], details=ed['details'])
    created_edu += 1
print('Created educations:', created_edu)
print('Done')
