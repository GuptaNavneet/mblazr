from boto3 import client, resource
#from capitalrap.settings import AccesseyID,Secret,bucket_name
from .static.routine.config import AccesseyID,Secret,bucket_name
from bs4 import BeautifulSoup
client = client('s3')
s3 = resource('s3', aws_access_key_id=AccesseyID, aws_secret_access_key=Secret)


def readFiling(file):
    try:
        response = s3.Object(bucket_name, 'filings/files/'+file).get()['Body'].read()
    except:
        response = ''

    return response

def toc_exctract(file):
    html_soup = BeautifulSoup(str(file), 'html.parser')

    # print(file_recieved)
    toc = html_soup.find_all('a')

    unique_toc_items = []
    note_track = 0
    item_track = 0
    part_track = 0
    # searching through links
    for index, link in enumerate(toc):
        # print(link)
        if str(link).find('href="#') > -1 or str(link).find("href='#") > -1:  # only select links with #
            a = link  # .encode('utf-8', errors='ignore')
            if a in unique_toc_items:  # skip if already in list /prevent dupicates
                continue
            else:
                if str(a).find('TABLE') > -1 or str(a).find('Table') > -1 or str(a).find(
                        'table') > -1:  # skip table of content link
                    continue
                else:

                    href_val = a.attrs['href']

                    # Searching exhibits
                    if str(a.text).find('Exhibit') > -1 or str(a.text).find('EXHIBIT') > -1 or str(a.text).find(
                            'exhibit') > -1 or str(href_val).find('EXHIBIT') > -1 or str(href_val).find(
                        'ex') > -1 or str(href_val).find('EX') > -1 or str(href_val).find('Ex') > -1:
                        continue
                        #
                        # a = '<a href="' + href_val + '" class="exhibit-link">' + a.text + '</a>'  # attrs={"class": "exhibit-link"}
                        #
                        #
                        # unique_toc_items.append(a)
                        # print(a)
                    else:
                        # Check if item is a subpart/or a part item
                        try:
                            last_item_inserted = unique_toc_items[-1]
                        except:
                            last_item_inserted = ''

                        # last_item_inserted = unique_toc_items[-1]

                        ##Insert If its Part
                        if str(a.text).find('Part') > -1 or str(a.text).find('PART') > -1 or str(a.text).find(
                                'part') > -1 or str(href_val).find('Part') > -1 or str(href_val).find(
                            'PART') > -1 or str(href_val).find('part') > -1:
                            # Check if part is in text and if not add
                            if str(a.text).find('Part') > -1 or str(a.text).find('PART') > -1 or str(a.text).find(
                                    'part') > -1:
                                a = '<a href="' + href_val + '" class="part-link">' + a.text + '</a>'
                            else:

                                a = '<a href="' + href_val + '" class="part-link">Part ' + str(
                                    part_track + 1) + ' .' + a.text + '</a>'
                                part_track = part_track + 1
                            unique_toc_items.append(a)
                        ##Insert Item
                        elif str(a.text).find('ITEM') > -1 or str(a.text).find('Item') > -1 or str(a.text).find(
                                'item') > -1 or str(a.text).find('ITem') > -1 or str(href_val).find(
                            'Item') > -1 or str(href_val).find('item') > -1 or str(href_val).find(
                            'ITEM') > -1:  # This is a Part Link
                            if str(a.text).find('ITEM') > -1 or str(a.text).find('Item') > -1 or str(a.text).find(
                                    'item') > -1:
                                a = '<a href="' + href_val + '" class="item-link">' + a.text + '</a>'
                            else:

                                a = '<a href="' + href_val + '" class="item-link">Item ' + str(
                                    item_track + 1) + ' .' + a.text + '</a>'
                                item_track = item_track + 1
                            unique_toc_items.append(a)  # add to list of valid found links for toc
                        # Insert Note
                        else:
                            if (str(last_item_inserted).find('Item') > -1 or str(
                                    last_item_inserted).find('ITEM') > -1 or str(last_item_inserted).find(
                                'item') > -1 or str(last_item_inserted).find('note-link') > -1) and str(
                                last_item_inserted).find('exhibit-link') < 0:
                                # Last Inserted link is of type 'ITEM'
                                # if str(a.text).find('Note') > -1 or str(a.text).find('NOTE') > -1 or str(a.text).find(
                                #         'note') > -1 > -1:

                                if str(a.text).find('NOTE') > -1 or str(a.text).find('Note') > -1 or str(
                                        a.text).find(
                                    'note') > -1:
                                    a = '<a href="' + href_val + '" class="note-link">' + a.text + '</a>'
                                else:
                                    a = '<a href="' + href_val + '" class="note-link">Note -' + str(
                                        note_track + 1) + '. ' + a.text + '</a>'
                                    note_track = note_track + 1
                                unique_toc_items.append(a)

                        # if str(last_item_inserted).find('Item') > -1 or str(
                        #         last_item_inserted).find('ITEM') > -1 or str(last_item_inserted).find('item') > -1:
                        #     # Last Inserted link is of type 'ITEM'
                        #     if str(a.text).find('Note') > -1 or str(a.text).find('NOTE') > -1 or str(a.text).find(
                        #             'note') > -1 > -1:
                        #         a = '<a href="' + href_val + '" class="note-link">' + a.text + '</a>'
                        #         unique_toc_items.append(a)
                        # else:
                        #     if str(a.text).find('ITEM') > -1 or str(a.text).find('Item') > -1 or str(a.text).find(
                        #             'item') > -1 or str(a.text).find('ITem') > -1 or str(href_val).find(
                        #         'Item') > -1 or str(href_val).find('item') > -1 or str(href_val).find(
                        #         'ITEM') > -1:  # This is a Part Link
                        #         a = '<a href="' + href_val + '" class="item-link">Item .' + a.text + '</a>'
                        #         unique_toc_items.append(a)  # add to list of valid found links for toc
                        #         # print(a)
                        #     elif str(a.text).find('Part') > -1 or str(a.text).find('PART') > -1 or str(a.text).find(
                        #             'part') > -1 or str(href_val).find('Part') > -1 or str(href_val).find(
                        #         'PART') > -1 or str(href_val).find('part') > -1:
                        #         a = '<a href="' + href_val + '" class="part-link">' + a.text + '</a>'
                        #         unique_toc_items.append(a)  # add to list of valid found links for toc
                        #     else:
                        #         a = '<a class="norm-link" href="' + href_val + '"> ' + a.text + '</a>'
                        #         unique_toc_items.append(a)  # add to list of valid found links for toc

        else:
            continue

    # searching throughvdivs
    all_p = html_soup.find_all('p')

    # for f in all_p:
    # if str(f.attrs['id']).find('item')>-1 or str(f.attrs['id']).find('ITEM')>-1 or str(f.attrs['id']).find('part')>-1 or str(f.attrs['id']).find('note')>-1:
    # if str(f).find('item')>-1:
    # print(f)
    ##Search for Exhibits
    all_exhibits = '<h3 class="exhibit-header">Exhibits</h3>'
    # exhib = FilingsExhibits.objects.filter(company_cik =comp_searched[0].cik)
    # for l in exhib:
    #     link ='<a href="/exhibits/'+str(l.exhib_path).split('/')[-1]+'" class="exhibit-link">'+str(l.exhib_path).split('/')[-1]+'</a>'
    #     all_exhibits=all_exhibits+str(link)
    # print(file_recieved)

    html_of_toc = ''
    for itm in unique_toc_items:
        html_of_toc = html_of_toc + str(itm)
    #
    prep = html_of_toc + all_exhibits
    return prep;


