import sys
import json
from loguru import logger
import datetime

__author__ = 'Sergey Poterianski'


SKIPED_ITEMS = ['password', 'fields', 'sections', 'URLs', 'notesPlain', 'passwordHistory', 'url', 'htmlMethod',
                'longterm', 'htmlAction', 'htmlID', 'eula_accepted', 'hint_question_id']

def print_help():
    print(f'usage: {sys.argv[0]} [path to the "*.1pif" filename]')

def ts_to_datetime_str(ts):
    return datetime.datetime.fromtimestamp(int(str(ts)[:10])).strftime('%Y-%m-%d %H:%M:%S')

def read_1pif(filename):
    lines = []
    with open(filename, 'r') as f:
        for l in f.readlines():
            if l.startswith('***') or l.strip() == '':
                continue
            lines.append(json.loads(l))
    return lines

def parse_1pif_items(pass_items):
    logger.info(f'Found {len(pass_items)} items')
    logger.info(f'start parsing')
    for pitem in pass_items:
        title, vars = parse_1pid(pitem)
        print_item(title, vars)
    logger.info(f'finish parsing')

def parse_1pid(pitem):
    vars = []
    title = pitem['title']
    created_at = ts_to_datetime_str(pitem['createdAt'])
    updated_at = ts_to_datetime_str(pitem['updatedAt'])
    
    if 'location' in pitem:
        location = pitem['location']
    if 'secureContents' not in pitem:
        logger.warning(f'No secureContents in {title}')
        return title, vars
    
    secure_contents = pitem['secureContents']
    if 'username' in secure_contents:
        vars.append(('username', secure_contents['username']))
    if 'password' in secure_contents:
        vars.append(('password', secure_contents['password']))
    if 'fields' in secure_contents:
        vars += parse_fileds(secure_contents['fields'])
    if 'sections' in secure_contents:
        sections_vars = parse_sections(secure_contents['sections'])
    if 'URLs' in secure_contents:
        vars += parse_urls(secure_contents['URLs'])
    if 'notesPlain' in secure_contents:
        vars.append(('notes', secure_contents['notesPlain']))
    if 'passwordHistory' in secure_contents:
        vars += parse_password_history(secure_contents['passwordHistory']) 
    if 'url' in secure_contents:
        vars.append(('url', secure_contents['url']))
       
    # undefined
    undefinded_vars = []
    for k, v in secure_contents.items():
        if k not in SKIPED_ITEMS:
            undefinded_vars.append((k, v))
    if len(undefinded_vars) > 0:
        logger.warning(f'For "{title}" found undefined vars: {undefinded_vars}')
        vars += undefinded_vars
    # created and updated
    vars.append(('Created', created_at))
    vars.append(('Updated', updated_at))

    return title, vars

def parse_fileds(fields):
    vars = []
    for field in fields:
        if 'designation' in field:
            vars.append((field['designation'], field['value']))
        elif 'name' in field and len(field['name']) > 0:
            vars.append((field['name'], field['value']))
        elif 'v' in field:
            vars.append((field['n'], field['v']))        
        
    return vars

def parse_sections(sections):
    vars = []
    for section in sections:
        title_vars = []
        if 'title' in section and len(section['title']) > 0:
            title_vars.append(('##', section['title']))
        elif 'name' in section and len(section['name']) > 0:
            title_vars.append(('##', section['name']))
        if 'fields' in section:
            field_vars = parse_fileds(section['fields'])
            if len(field_vars) > 0:
                vars.append(title_vars)
                vars.append(field_vars)
        else:
            logger.warning(f'Undefined section "{section}"')
    return vars

def parse_password_history(history):
    vars = []
    for h in history:
        if 'value' in h and 'time' in h:
            ts = ts_to_datetime_str(h['time'])
            vars.append((ts, h['value']))
    return vars


def parse_urls(urls):
    vars = []
    for u in urls:
        if 'url' in u:
            vars.append(('url', u['url']))
    return vars

def convert_title(title):
    title = title.replace(' ', '_').lower()
    return title


def print_item(title, vars):
    print(f'## {title}')
    for v in vars:
        if len(v[1].strip()) > 0:
            if(v[0] == 'notes'):
                print(f'-------\n{v[1]}\n-------')
            else:
                print(f'{v[0]}: {v[1]}')
    print()

def main():
    if len(sys.argv) < 2:
        print_help()
        sys.exit(0)

    print(sys.argv[1])
    pass_items = read_1pif(sys.argv[1])
    parse_1pif_items(pass_items)
    
if __name__ == '__main__':
    main()