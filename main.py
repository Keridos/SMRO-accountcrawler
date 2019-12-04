import requests
import os
import re
import webbrowser
import shutil
import json


class Account:
    def __init__(self, username, password, count_zeny, char_slot):
        self.name = username
        self.pw = password
        self.count_zeny = count_zeny
        self.char_slot = char_slot


class Char:
    def __init__(self, username, name, zeny, count_zeny, char_slot, url):
        self.username = username
        self.name = name
        self.zeny = zeny
        self.count_zeny = count_zeny
        self.char_slot = char_slot
        self.url = url


total_zeny = 0
list_chars = []

# regex matching strings for different variables and stuff in the html
char_match_string = '</td>\n<td>\n.+?\\?module=character&action=view&id=(' \
                    '.+?)&preferred_server=Shining\\+Moon\\+RO'
head_match_string = '<link rel="stylesheet" .+?css/flux.css.+? />([\\s\\S]+?)\n</head>'
upper_block_match_string = '<body>([\\s\\S]+?)<h2>Viewing Character</h2>'
lower_block_match_string = '(</div> \n<div class="contentBottom">[\\s\\S]+?)</body>'
char_zeny_match_string = '<th>Zeny</th>\n<td colspan="2">(.+?)</td>'
char_name_match_string = '<title>Shining Moon: Viewing Character \\((.+?)\\)</title>'

# the actual code
new_path = os.getcwd() + '/output/'
if os.path.exists(new_path):
    shutil.rmtree(new_path, ignore_errors=True)
os.makedirs(new_path)


def get_accounts():
    accounts = []
    with open('accounts.json') as json_file:
        data = json.load(json_file)
        for p in data['accounts']:
            accounts.append(Account(p['name'], p['password'], bool(p['count_zeny']), p['char_slot']))

    return accounts


def parse_char(html):
    global total_zeny
    # remove outer stuff
    head = re.search(head_match_string, html)[1]
    upper_block = re.search(upper_block_match_string, html)[1]
    lower_block = re.search(lower_block_match_string, html)[1]

    html = html.replace(head, '').replace(upper_block, '').replace(lower_block, '')

    # replace relative urls with absolute urls
    html = html.replace('src="', 'src="https://www.shining-moon.com') \
        .replace('href="', 'href="https://www.shining-moon.com')

    char_zeny = re.search(char_zeny_match_string, html)[1]
    char_name = re.search(char_name_match_string, html)[1]

    # output to html file
    f = open('output/' + a.name + '-' + char_name + '.html', 'w')
    f.write(html)
    f.close()
    file = 'file:///' + os.getcwd() + '/output/' + a.name + '-' + char_name + '.html'

    if a.count_zeny:
        print(a.name + ' - ' + char_name + ':', char_zeny)
        total_zeny += int(char_zeny.replace(',', ''))

    list_chars.append(Char(a.name, char_name, char_zeny, a.count_zeny, a.char_slot, file))


def overview():
    global list_chars
    global total_zeny
    total_zeny = f'{total_zeny:,}'
    print('Total zeny: ' + total_zeny)

    html_start = \
        """<html>
        <head></head>
        <body><p>Character Overview:</p>"""
    html_end = \
        """</body>
        </html>"""
    html_content = '\n<br>Total Zeny: ' + total_zeny

    for c in list_chars:
        html_content += '\n<br>' + c.username + ' - <a href="' + c.url + '">' + c.name + '</a> - ' \
                        + 'Zeny: ' + c.zeny + ' (counted: ' + str(c.count_zeny).lower() + ')'

    html_overview = html_start + html_content + html_end

    f = open('output/index.html', 'w')
    f.write(html_overview)
    f.close()
    filename = 'file:///' + os.getcwd() + '/output/index.html'
    webbrowser.open_new_tab(filename)


# import account info
# TODO: potentially convert to API Tokens if implemented on server
list_accounts = get_accounts()

for a in list_accounts:
    payload = {'username': a.name,
               'password': a.pw,
               'server': 'Shining Moon RO'}

    with requests.session() as s:
        # Login
        s.post('https://www.shining-moon.com/?module=account&action=login&return_url=', data=payload)

        # get account page
        r = s.get('https://www.shining-moon.com/?module=account&action=view')

        char = ""

        if a.char_slot == 0:
            for i in range(1, 27):
                # search for char id
                char_matches = re.search(str(i) + char_match_string, r.text)
                if char_matches is None:
                    continue
                char_id = char_matches[1]
                # get character page for char with set id
                char = s.get('https://www.shining-moon.com/?module=character&action=view&id=' +
                             char_id + '&preferred_server=Shining+Moon+RO')
                parse_char(char.text)
        else:
            # search for char id
            char_matches = re.search(char_match_string, r.text)
            char_id = char_matches[a.char_slot]
            # get character page for char with set id
            char = s.get('https://www.shining-moon.com/?module=character&action=view&id=' +
                         char_id + '&preferred_server=Shining+Moon+RO')
            parse_char(char.text)

overview()
