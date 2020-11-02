# # -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
import requests
import re
from argparse import Namespace

import unicodedata


'''
Table of Contents Extractor


This class takes a filing html file as input and return the table of contents
'''


class TOCAlternativeExtractor(object):
    
    exhibit_end = -1

    html = ''

    def extract(self, url):

        with open(url,encoding="utf-8",errors="ignore",newline=None,mode='r') as file:
            html = file.read()
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
            
        html = html.replace( html[:exhibit_end], '')

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

                exhibits += f"<a href='{href}' class='exhibit-link' target='_blank'>EX-{exhibit_counter} {href_text}</a>"
                distinct_exhibits.append(href)

                exhibit_counter += 1

        if not exhibits:
            return ''

        heading = "<h3 class='exhibit-header'>Exhibits</h3>"

        return heading + exhibits

    def _get_alternative_links(self, html):

        default_table = self._get_toc(html)

        
        if default_table:
            html = html.replace(default_table, '[[REMOVED_TABLE]]')
        
        modified_soup = BeautifulSoup(html, 'lxml')

        new_soup = ''

        def is_bold(tag):
            
            tag_text = tag.get_text().lower().strip()
            
            if not tag_text:
                return False

            if tag.name == 'a':
                return False

            if not tag.has_attr('style') and tag.name != 'b':
                return False

            style_text = tag.get('style')

            if tag.name != 'b' and not ('font-weight:700' in style_text or 'font-weight:bold' in style_text or 'font-weight:800' in style_text or 'font-weight:900' in style_text or 'font-weight: 700' in style_text or 'font-weight: bold' in style_text or 'font-weight: 800' in style_text or 'font-weight: 900' in style_text):
                return False
                        
            split_text = tag_text.split()

            if len(split_text) <= 1:
                return False

            if split_text and split_text[0] not in ('item', 'items', 'note', 'part'):
                return False

            if split_text[1] not in ('i', 'i.', 'ii', 'ii.', 'iii', 'iii.', 'iv', 'v', 'vi', 'vii',) and not split_text[1][0].isdigit():
                return False

            return True

        id_counter = 0

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

        pattern = re.compile(
            r'<a.+href="([\S]+)".*>Table of Contents.*</a>', re.IGNORECASE)

        links = re.findall(pattern, text)

        pos = -1

        if links:
            links = links[0]

            link = links[links.find('#')+1:]

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
            text = text[:end_pos+8]
        
        else:
            return ''

        return text

    def save_html(self, html):

        with open(self.url, 'w') as file:
            file.write(html)


class Printer(object):

    def generate(self, url, content_type):

        with open(url,encoding='utf-8',errors='ignore',newline=None,mode='r') as file:
            html = file.read()
        if content_type == 'Full':
            return html
        else:
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
