"""
Utilite for convert 1password item to pass item
"""
import os
import sys
import json
import datetime
import argparse
import subprocess
from loguru import logger

__author__ = 'Sergey Poterianski'

SKIPED_ITEMS = ['password', 'fields', 'sections', 'URLs', 'notesPlain', 'passwordHistory',
                'url', 'htmlMethod', 'longterm', 'htmlAction', 'htmlID', 'eula_accepted',
                'hint_question_id', 'order_date_dd', 'order_date_mm', 'search_app',
                'search_url', 'search_user', 'search_pass', 'search_name', 'field_1',
                'field_2', 'field_3', 'field_4', 'field_5', 'field_6', 'field_7',
                'field_8', 'agree_tos', 'agree_privacy', 'agree_marketing',
                'agree_marketing_email', 'agree_marketing_sms', 'ips_password',
                'ips_username', 'ips_email', 'ips_phone', 'ips_first_name', 'ips_last_name',
                'signOn[passwd]', 'signOn[username]', 'signOn[usernameField]',
                'signOn[passwordField]', 'option1', 'option2', 'option3', 'option4', 'option5',
                'option6', 'option7', 'option8', 'agree'
                ]

def ts_to_datetime_str(timestamp):
    """Convert timestamp to datetime string"""
    return datetime.datetime.fromtimestamp(int(str(timestamp)[:10])).strftime('%Y-%m-%d %H:%M:%S')

def read_1pif(filename):
    """Read 1pif file"""
    lines = []
    with open(filename, 'r') as fstream:
        for line in fstream.readlines():
            if line.startswith('***') or line.strip() == '':
                continue
            lines.append(json.loads(line))
    return lines

def parse_1pif_items(pass_items, folder_name, print_only=False, force=False,
                     pass_in_first_line=False):
    """Parse 1pif items"""
    logger.info(f'Found {len(pass_items)} items')
    logger.info('start parsing')

    result = []
    for pitem in pass_items:
        result.append(parse_1pid(pitem))
    logger.info('finish parsing')

    if print_only:
        for title, vals in result:
            print_item(title, vals)
        return
    store_items(result, folder_name, force, pass_in_first_line)

def parse_1pid(pitem):
    """Parse 1pif item"""
    vals = []
    title = pitem['title']
    created_at = ts_to_datetime_str(pitem['createdAt'])
    updated_at = ts_to_datetime_str(pitem['updatedAt'])

    if 'location' in pitem:
        vals.append(('Location', pitem['location']))
    if 'secureContents' in pitem:
        secure_contents = pitem['secureContents']
        if 'username' in secure_contents:
            vals.append(('Username', secure_contents['username']))
        if 'password' in secure_contents:
            vals.append(('Password', secure_contents['password']))
        if 'fields' in secure_contents:
            vals += parse_fileds(secure_contents['fields'])
        if 'sections' in secure_contents:
            vals += parse_sections(secure_contents['sections'])
        if 'URLs' in secure_contents:
            vals += parse_urls(secure_contents['URLs'])
        if 'notesPlain' in secure_contents:
            vals.append(('Notes', f'\n-------\n{secure_contents["notesPlain"]}\n-------'))
        if 'passwordHistory' in secure_contents:
            vals += parse_password_history(secure_contents['passwordHistory'])
        if 'url' in secure_contents:
            vals.append(('url', secure_contents['url']))

    # Process undefined vars
    undefinded_vars = []
    for key, val in secure_contents.items():
        if key not in SKIPED_ITEMS:
            undefinded_vars.append((key, val))
    if len(undefinded_vars) > 0:
        logger.debug(f'For "{title}" found undefined vars: {undefinded_vars}')
        vals += undefinded_vars

    vals.append(('\nCreated', created_at))
    vals.append(('Updated', updated_at))

    # Make result dict
    result_dict = dict()
    for var in vals:
        key = var[0].strip().capitalize()
        val = var[1]
        if key not in result_dict and val.strip() != '':
            result_dict[key] = val

    return title, result_dict

def parse_fileds(fields):
    """Parse fields"""
    vals = []
    for field in fields:
        if 'designation' in field:
            vals.append((field['designation'], field['value']))
        elif 'name' in field and len(field['name']) > 0:
            vals.append((field['name'], field['value']))
        elif 'v' in field:
            vals.append((field['n'], field['v']))
    return vals

def parse_sections(sections):
    """Parse sections"""
    vals = []
    for section in sections:
        title_vars = []
        if 'title' in section and len(section['title']) > 0:
            title_vars.append(('\n##', section['title']))
        elif 'name' in section and len(section['name']) > 0:
            title_vars.append(('\n##', section['name']))
        if 'fields' in section:
            field_vars = parse_fileds(section['fields'])
            if len(field_vars) > 0:
                vals += title_vars
                vals += field_vars
        else:
            logger.warning(f'Undefined section "{section}"')
    return vals

def parse_password_history(history):
    """Parse password history"""
    vals = []
    if len(history) > 0:
        vars.append(('\n## Password history', ''))
    for hist in history:
        if 'value' in hist and 'time' in hist:
            timestamp = ts_to_datetime_str(hist['time'])
            vals.append((timestamp, hist['value']))
    return vals

def parse_urls(urls):
    """fstream"""
    vals = []
    for url in urls:
        if 'url' in url:
            vals.append(('url', url['url']))
    return vals

def convert_title(title):
    """Convert title to filename"""
    title = title.replace(' ', '_').lower()
    if title.startswith('http://'):
        title = title[7:]
    elif title.startswith('https://'):
        title = title[8:]
    return title

def convert_folder_name(folder_name):
    """Convert folder name to filename"""
    if folder_name == '':
        return 'Import'
    result = ''
    for fname in folder_name.split('/'):
        result += fname.capitalize() + '/'
    return result[:-1]

def print_item(title, vals):
    """Print item"""
    print(f'# {title}')
    for key, val in vals.items():
        print(f'{key}: {val}')
    print()

def store_items(items, folder_name, first_line=False, force=False):
    """Store items"""
    logger.info('start storing')
    for item in items:
        title, vals = item
        folder_name = convert_folder_name(folder_name)
        fname = convert_title(title)
        logger.info(f'store: "{title} -> {fname}"')
        cmd = 'pass insert '
        if force:
            cmd += '-f '
        cmd += f'-m {folder_name}/{fname}'
        with subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, encoding='utf-8') as proc:
            if first_line and 'Password' in vals:
                proc.stdin.write(f'{vals["Password"]}\n')
            proc.stdin.write(f'# {title}\n')
            for key, val in vals.items():
                proc.stdin.write(f'{key}: {val}\n')

            lines = proc.communicate()[0]
            for line in lines.split('\n'):
                logger.debug(line)
    logger.info('finish storing')

def main():
    """Main function"""
    parser = argparse.ArgumentParser(prog='1pass2pass',
                                     description='Utility for converting ' + \
                                                 '1password data to pass format',
                                     epilog = 'written by @spoterianski')
    parser.add_argument("pif_filename", metavar="<1pif filename>",
                        help="Path to *.1pif file for processing",
                        type=str)
    parser.add_argument("folder", metavar="<folder>",
                        help="Folder name for store passwords",
                        type=str)
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-p", "--print-only",
                        help="print data into console, without saving into password store",
                        action="store_true")
    parser.add_argument("-f", "--force", help="force overwrite existing passwords (default=False)",
                        action="store_true", default=False)
    parser.add_argument("-fl", "--first-line",  help="Put password in first line (default=False)",
                        action="store_true", default=False)
    args = parser.parse_args()
    if not os.path.isfile(args.pif_filename):
        logger.error(f'File "{args.pif_filename}" not found')
        return

    logger.remove()
    logger.add(sys.stderr, level='DEBUG' if args.verbose else 'INFO')
    pass_items = read_1pif(args.pif_filename)
    parse_1pif_items(pass_items, args.folder, args.print_only, args.force, args.first_line)

if __name__ == '__main__':
    main()
