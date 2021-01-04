# # -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
import requests
import re
from argparse import Namespace
# from urllib.request import urlopen

import unicodedata

'''
Table of Contents Extractor


This class takes a filing html file as input and return the table of contents
'''

# used in finding pages for 3 buttons to keep page titles search results
tree_buttons = {}
class TOCAlternativeExtractor(object):
    exhibit_end = -1

    html = ''

    def extract(self, url):
        # For test mode
        # url = url.replace('/mnt/filings-static/capitalrap/edgarapp', 'https://mblazr.com')
        # html = str(urlopen(url).read())
        
        with open(url) as file:
            html = file.read()

        html = html.replace('\\n','') 
        html = html.replace('\\t','')
        html = html.replace('\t','')
        html = html.replace('\n','')

        # remove  previous tag ids for 3 page titles
        html = html.replace('id="Cons_Balance_Sheets"','')
        html = html.replace('id="Cons_Statmnts_of_Cmprehnsve_Loss"','')
        html = html.replace('id="Cons_Statements_of_Cash_Flows"','')

        self.html = html

        self.url = url

        links = self._get_alternative_links(html)

        links += self._get_exhibits(self.html)

        data = Namespace(table=links)

        self.save_html(self.html)

        return data

    def _get_exhibits(self, html):

        exhibit_end = html.find('exhibits="true"')

        if exhibit_end == -1:
            exhibit_end = html.find("exhibits='true'")

        if exhibit_end == -1: return ""

        html = html.replace(html[:exhibit_end], '')

        soup = BeautifulSoup(html, features='lxml')

        exhibits = ""

        distinct_exhibits = []

        exhibit_counter = 1

        for link in soup.find_all('a'):

            link_text = link.get_text()

            if not link_text: continue

            if 'table of content' in link_text.lower(): continue

            href = link.get('href')

            if href and href not in distinct_exhibits:
                href_text = href.split('/')[-1]

                # exhibits += f"<a href='{href}' class='exhibit-link' target='_blank'>EX-{exhibit_counter} {href_text}</a>"
                # This line changed to show the discription.
                exhibits += f"<a href='{href}' class='exhibit-link' target='_blank'>EX-{exhibit_counter} {link_text}</a>"
                
                distinct_exhibits.append(href)

                exhibit_counter += 1

        if not exhibits:
            return ''

        heading = "<h3 class='exhibit-header'>Exhibits</h3>"

        return heading + exhibits

    def _get_alternative_links(self, html):

        default_table = self._get_toc(html)
        # before manipulating html remove all past ids of page titles for 3 buttons
        default_table.replace('Cons_Statements_of_Cash_Flows', '')
        default_table.replace('Cons_Statmnts_of_Cmprehnsve_Loss', '')
        default_table.replace('Cons_Balance_Sheets', '')

        html = self.html
        # if default_table:
        #     html = html.replace(default_table, '[[REMOVED_TABLE]]')

        modified_soup = BeautifulSoup(html, 'lxml')

        new_soup = ''

        def is_bold(tag):

            tag_text = tag.get_text().lower().strip()

            if not tag_text:
                return False

            if tag.name == 'a':
                return False

             # check if the tag have id and it's one of list below
            if 'id' in tag.attrs and tag.attrs['id'] in ['Cons_Statements_of_Cash_Flows', 'Cons_Statmnts_of_Cmprehnsve_Loss', 'Cons_Balance_Sheets']:
                tag.attrs['id'] = ''


            # check if tag have text inside, check if tag is one of tag list below 
            # and check if text lenght is betwen 100 and 25
            # check if tag have only one content inside (which should be the text)
            if len(tree_buttons) < 3 and tag.name in ['p','b','font','span'] and 90 > len(tag.text) > 25:
                
                # tag shouldn't have parent a or td. Only content table tags have td and a as parents 
                if not [e for e in tag.parents if e.name in ['td','tr','a']]:
                    # check tag text to consist words from list below
                    if not 'balance' in tree_buttons and len([word for word in ['consolidated', 'balance', 'sheet'] if word in tag.text.lower()]) == 3:
                        tag['id'] = 'Cons_Balance_Sheets'
                        tree_buttons['balance'] = True

                    # If there is not 'consolidated balance sheet' check for 'consolidated financial position'
                    if not 'balance' in tree_buttons and not 'financial' in tree_buttons and len([word for word in ['consolidated', 'financial', 'position'] if word in tag.text.lower()]) == 3:
                        tag['id'] = 'Cons_Balance_Sheets'
                        tree_buttons['financial'] = True

                    if len([word for word in ['consolidated', 'statement'] if word in tag.text.lower()]) == 2:
                        
                        if not 'loss' in tree_buttons and 'loss' in tag.text.lower() or 'income' in tag.text.lower():
                            tag['id'] = 'Cons_Statmnts_of_Cmprehnsve_Loss'
                            tree_buttons['loss'] = True

                        if not 'cash' in tree_buttons and 'cash' in tag.text.lower() or 'flow' in tag.text.lower():
                            tag['id'] = 'Cons_Statements_of_Cash_Flows'
                            tree_buttons['cash'] = True


            if not tag.has_attr('style') and tag.name != 'b':
                return False

            style_text = tag.get('style')

            if tag.name != 'b' and not (
                    'font-weight:700' in style_text or 'font-weight:bold' in style_text or 'font-weight:800' in style_text or 'font-weight:900' in style_text or 'font-weight: 700' in style_text or 'font-weight: bold' in style_text or 'font-weight: 800' in style_text or 'font-weight: 900' in style_text):
                return False

            split_text = tag_text.split()

            if len(split_text) <= 1:
                return False

            if split_text and split_text[0] not in ('item', 'items', 'note', 'part'):
                return False

            if split_text[1] not in ('i', 'i.', 'ii', 'ii.', 'iii', 'iii.', 'iv', 'v', 'vi', 'vii',) and not \
            split_text[1][0].isdigit():
                return False

            return True

        id_counter = 0

        global tree_buttons
        tree_buttons = {}
        headings = modified_soup.find_all(is_bold)

        num_of_headings = len(list(headings))

        tag_dict = {
            'part': 1,
            'item': 1,
            'note': 1,
        }

        headings_list = []

        for tag in headings:

            tag_text = tag.get_text().strip().replace('&nbsp;', ' ').replace('\n', '').replace('\\n', '')

            tag_text_lower = tag_text.lower()

            split_text = tag_text_lower.split()

            if split_text[0] == 'item' and split_text[1][-1] == '.':

                for t in tag.parents:

                    if t.name == 'tr':
                        tag_text = t.get_text().strip().replace('&nbsp;', ' ').replace('\n', '').replace('\\n', '')
                        tag_text_lower = tag_text.lower()
                        break
                    elif t.name == 'body':
                        break

            if tag_text_lower in headings_list:
                continue

            link_found = False

            for link in headings_list:
                if link.startswith(tag_text_lower) and link != 'part i' and link != 'part ii':
                    link_found = True

            if link_found:
                continue

            headings_list.append(tag_text_lower)

            tag_first_word = tag_text_lower.split()[0]
            tag_class = tag_first_word if tag_first_word != 'items' else 'item'

            tag_id = tag_class + str(tag_dict[tag_class])
            tag['id'] = tag_id

            tag_dict[tag_class] += 1

            if tag_first_word == 'part':
                tag_text = tag_text.upper()
            else:
                tag_text = tag_text.title()

            tag_text = tag_text.replace('.', '. ').replace('  ', ' ').strip(' . ')

            exhbit_text = tag_text_lower.replace('.', ' - ').replace('  ', ' ').strip(' - ')

            if 'exhibit' in exhbit_text and self.exhibit_end == -1:
                tag['exhibits'] = 'true'
                self.exhibit_end = 1

            id_counter += 1

            if id_counter == num_of_headings and self.exhibit_end == -1:
                tag['exhibits'] = 'true'

            tag['data-print-type'] = tag_class

            new_soup += f"<a href='#{tag_id}' class='{tag_class}-link' data-print-type='{tag_class}'>{tag_text}</a>"

        self.html = modified_soup.body.prettify(formatter='html').replace('[[REMOVED_TABLE]]', default_table)

        return new_soup

    def _get_toc(self, html):

        text = html

        start = text.find("SECURITIES AND EXCHANGE COMMISSION")

        if start != -1:
            text = text[start:]

        pattern = re.compile(r'<a.+href="([\S]+)".*>Table of Contents*</a>', re.IGNORECASE)

        # links = re.findall(pattern, text)
        links = ['#TOC']

        pos = -1

        if links:
            links = links[0]

            link = links[links.find('#') + 1:]

            pos = text.find(f'id="{link}"')

            if pos == -1:
                pos = text.find(f'name="{link}"')

        if pos == -1:
            pos = text.lower().find("table of contents")

        if pos == -1:
            pos = text.lower().find("index")

        # if pos == -1:
        #     pos = text.lower().find('<hr style="page-break-after:always"')


        if pos == -1:
            return ''

        text = text[pos:]

        end_pos = text.lower().find('</table>')


        if pos != -1 and end_pos != -1:
            text = text[:end_pos + 8]

        else:
            return ''

        return text


    def save_html(self, html):
        # For test mode
        import os 
        from capitalrap.settings import STATICFILES_DIRS
        new_url = self.url.replace('https://mblazr.com/static/filings', STATICFILES_DIRS[0][1])

        if not new_url.split('/')[7] in os.listdir(STATICFILES_DIRS[0][1]):
            os.mkdir(STATICFILES_DIRS[0][1] + '/' + new_url.split('/')[-2])
        with open(new_url, 'w') as file:

        # with open(self.url, 'w') as file:
            file.write(html)


class Printer(object):

    def generate(self, url, content_type):
        with open(url) as file:
            html = file.read()

        soup = BeautifulSoup(html, 'lxml')

        res = soup.find(attrs={'id': content_type})

        start_tag_str = str(res)

        del soup
        del res

        start = html.find(start_tag_str)

        html = html[start:]

        end_word = re.sub('\d+', '', content_type)
        end_word = end_word.lower()

        html = html.replace(f'data-print-type="{end_word}"', '', 1)

        end = html.find(f'data-print-type="{end_word}"')

        html = html[:end]

        return html
