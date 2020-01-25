import json
import os
import re
import shutil
import webbrowser

import requests


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


# global variables
total_zeny = 0
list_chars = []

# regex matching strings for different values and stuff in the html
head_match_string = '<link rel=\"stylesheet\" .+?css/flux.css.+? />\n([\\s\\S]+?)\n</head>'
upper_block_match_string = '<body>([\\s\\S]+?)\n<h2>Viewing Character</h2>'
lower_block_match_string = '</div> \n(<div class=\"contentBottom\">[\\s\\S]+?)</body>'  # leave /div for padding
job_image_match_string = '<table class=\"vertical-table\">\n<tr>([\\s\\S]+?)\n<th>Character ID</th>'

char_id_match_string = '</td>\n<td>\n.+?\\?module=character&action=view&id=(' \
                       '.+?)&preferred_server=Shining\\+Moon\\+RO'
char_zeny_match_string = '<th>Zeny</th>\n<td colspan=\"2\">(.*?)</td>'
char_name_match_string = '<title>Shining Moon: Viewing Character \\((.+?)\\)</title>'

# replacement strings
head_match_replace_string = "<style>\ndiv {\npadding-right: 10px;\npadding-left: 10px;\n}\n </style>"
upper_block_replace_string = "\n<div>"


# the actual code
def get_lines_from_file(path):
    file = open(path, 'r')
    output = ''
    for line in file:
        output += line
    return output


# load account data from json
def get_accounts():
    accounts = []
    with open('accounts.json') as json_file:
        data = json.load(json_file)
        for p in data['accounts']:
            accounts.append(Account(p['name'], p['password'], bool(p['count_zeny']), p['char_slot']))

    return accounts


# here the char data is being extracted from the html and the output is cut down
def parse_char(html, a):
    global total_zeny

    # remove outer stuff
    head = re.search(head_match_string, html)[1]
    upper_block = re.search(upper_block_match_string, html)[1]
    lower_block = re.search(lower_block_match_string, html)[1]
    job_image = re.search(job_image_match_string, html)
    if job_image is not None:
        job_image = job_image[1]
    else:
        job_image = 'thisdoesnotexistorrathershouldnotexistinthehtml'

    html = html.replace(head, head_match_replace_string).replace(upper_block, upper_block_replace_string) \
        .replace(lower_block, '').replace(job_image, '')

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

    # print username, charname and zeny to terminal
    print(a.name + ' - ' + char_name + ':', char_zeny)

    if a.count_zeny:
        total_zeny += int(char_zeny.replace(',', ''))

    list_chars.append(Char(a.name, char_name, char_zeny, a.count_zeny, a.char_slot, file))


# creates the overview html
def overview():
    global list_chars
    global total_zeny
    total_zeny = f'{total_zeny:,}'
    print('Total zeny: ' + total_zeny)

    html_start = get_lines_from_file('data/overview_start.txt')
    html_end = get_lines_from_file('data/overview_end.txt')
    html_content = '\n<br><h3>Total Zeny: ' + total_zeny + \
                   '</h3>\n<br><table><tr><th>Account</th><th>Charname</th>' + \
                   '<th>Zeny</th><th>counted?</th></tr>'

    for c in list_chars:
        html_content += '\n<tr><td>' + c.username + '</td><td><a href="' + c.url + '">' \
                        + c.name + '</a></td><td  align="right">' + '<i>' + c.zeny + '</i></td><td align="right"><i>' \
                        + str(c.count_zeny).lower() + '</i></td></tr>'

    html_overview = html_start + html_content + html_end

    f = open('output/index.html', 'w')
    f.write(html_overview)
    f.close()
    filename = 'file:///' + os.getcwd() + '/output/index.html'
    webbrowser.open_new_tab(filename)


# main entry point
def main():
    # empty/create output folder
    new_path = os.getcwd() + '/output/'
    if os.path.exists(new_path):
        shutil.rmtree(new_path, ignore_errors=True)
    os.makedirs(new_path)

    # import account info
    list_accounts = get_accounts()

    # then loop over all the accounts
    for a in list_accounts:
        payload = {'username': a.name,
                   'password': a.pw,
                   'server': 'Shining Moon RO'}

        # start up a new session for each account
        with requests.session() as s:
            # Login to get some delicious cookies
            s.post('https://www.shining-moon.com/?module=account&action=login&return_url=', data=payload)

            # get account page
            r = s.get('https://www.shining-moon.com/?module=account&action=view')

            # determine which characters to scan, then get their page and parse it
            if a.char_slot == 0:
                for i in range(1, 27):
                    # search for char id
                    char_matches = re.search(str(i) + char_id_match_string, r.text)
                    if char_matches is None:
                        continue
                    char_id = char_matches[1]
                    # get character page for char with set id
                    char = s.get('https://www.shining-moon.com/?module=character&action=view&id=' +
                                 char_id + '&preferred_server=Shining+Moon+RO')
                    parse_char(char.text, a)
            else:
                # search for char id
                char_matches = re.search(char_id_match_string, r.text)
                char_id = char_matches[a.char_slot]
                # get character page for char with set id
                char = s.get('https://www.shining-moon.com/?module=character&action=view&id=' +
                             char_id + '&preferred_server=Shining+Moon+RO')
                parse_char(char.text, a)
    # after all that is done, create the overview
    overview()


main()
