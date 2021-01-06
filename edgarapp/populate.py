from edgarapp.models import Filing, Company, Funds, Directors, Executives
import textdistance
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re


def check_for_quarterly():
    for company in Company.objects.all():
        for filing in company.filings.all():

            url = f'https://mblazr.com/static/filings/{filing.filingpath}'
            html = str(urlopen(url).read())

            soup = BeautifulSoup(html, 'lxml')
            date_tag = soup.find('ix:nonnumeric', format="ixt:datemonthdayyearen")

            if date_tag:
                text  = date_tag.text.replace('\\n', '').replace('\n', '')
                print(f'company T: {company.ticker} filing id: {filing.id} date: {text}')

            else:
                # expresion = re.compile(r'for the ([A-Za-z]*) ended (\S*) ', re.IGNORECASE)
                expresion = re.compile(r'For the quarterly ([A-Za-z]*) ([A-Za-z]*) ended', re.IGNORECASE)
                text = expresion.search(html)
                print(text)

def check_filing(filing=None):
    url = f'https://mblazr.com/static/filings/{filing.filingpath}'
    html = str(urlopen(url).read())
    if filing is None:
        filing = Filing.objects.get(filingdate='2020-08-05', cik=715957)

    soup = BeautifulSoup(html, 'lxml')
    date_tag = soup.find('ix:nonnumeric', format="ixt:datemonthdayyearen")

    if date_tag:
        text  = date_tag.text.replace('\\n', '').replace('\n', '')
        return(text)
    else:
        return('There is no tag ix:nonnumeric')

def populate_filings():

    for company in Company.objects.all():

        Filing.objects.filter(cik=company.cik, name=company.name, company=None).update(company=company)
        
        # company = Company.objects.filter(cik=filing.cik).first()
        
        # filing.company = company
        # filing.save()

    print('DOne with Filings')

def populate_funds():

    for company in Company.objects.all():
            
        name = company.name
        name = name.upper()
        name = name.replace('INTERNATIONAL', 'INTL')
        name = name.replace(' /DE', '')
        name = name.replace('/DE', '')
        name = name.replace('INC.', 'INC')
        name = name.replace(',', '')
        
        Funds.objects.filter(company=name, company_rep=None).update(company_rep=company)
    

    print('Done with Funds')

def populate_executives():

    for company in Company.objects.all():
        
        Executives.objects.filter(company=company.name, company_rep=None).update(company_rep=company)
        
    
    print('Done with Exectuives')

def populate_directors():

    for company in Company.objects.all():
        Directors.objects.filter(company=company.name, company_rep=None).update(company_rep=company)
    
    print('Done with Directors')

def populate_other_companies():

    for company in Company.objects.all():

        directors = Directors.objects.filter(company=company.name)

        allDirectors = Directors.objects.all()

        for person in directors:
            if person:
                personA = person.director.replace("Mr.", '')
                personA = person.director.replace("Dr.", '')
                personA = person.director.replace("Ms.", '')
                a = set([s for s in personA if s != "," and s != "." and s != " "])
                aLast = personA.split(' ')[-1]
                if (len(personA.split(' ')) == 1):
                    aLast = personA.split('.')[-1]
            
            comps = []
            
            for check in allDirectors:
            
                if person:
            
                    personB = check.director.replace("Mr.", '')
                    personB = check.director.replace("Dr.", '')
                    personB = check.director.replace("Ms.", '')
                    bLast = personB.split(' ')[-1]
            
                    if (len(personB.split(' ')) == 1):
                        bLast = personB.split('.')[-1]
                    # print(personA, aLast, person.company, personB, bLast, check.company)
            
                    if aLast == bLast:
                        # first check jaccard index to speed up algo, threshold of .65
                        b = set([s for s in personB if s !=
                                "," and s != "." and s != " "])
                        if (len(a.union(b)) != 0):
                            jaccard = float(
                                len(a.intersection(b)) / len(a.union(b)))
            
                        else:
                            jaccard = 1
                        # print(personA, personB, jaccard)
            
                        if (jaccard > 0.65):
                            # run Ratcliff-Obershel for further matching, threshold of .75 and prevent self-match
                            sequence = textdistance.ratcliff_obershelp(
                                personA, personB)
                            # print(sequence)
                            if sequence > 0.75 and company.name != check.company:
                                # comps.append(check.company)
                                other_companies = Company.objects.filter(name=check.company)
                                person.other_companies.add(*other_companies)
                                
            # if not comps:
                # comps.append('Director is not on the board of any other companies')
        # filing.save()

    print('Done with other companies')


def populate_all():

    # for company in Company.objects.all():

        # Filing.objects.filter(cik=company.cik).update(company=company)
            
        # name = company.name
        # name = name.upper()
        # name = name.replace('INTERNATIONAL', 'INTL')
        # name = name.replace(' /DE', '')
        # name = name.replace('/DE', '')
        # name = name.replace('INC.', 'INC')
        # name = name.replace(',', '')

        # Funds.objects.filter(company=name).update(company_rep=company)

        # Executives.objects.filter(company=company.name).update(company_rep=company)
        # Directors.objects.filter(company=company.name).update(company_rep=company)

    populate_other_companies()
    # print('Done with all')
    # populate_filings()
    # populate_funds()
    # populate_executives()
    # populate_directors()