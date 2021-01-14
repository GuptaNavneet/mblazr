from edgarapp.models import Filing, Company, Funds, Directors, Executives, Quarterly
from urllib.request import urlopen
from datetime import datetime
from time import perf_counter
from bs4 import BeautifulSoup
import textdistance
import httpx
import re


def get_time(st=perf_counter()):
    return perf_counter() - st

def is_report_tag(tag):
    if tag.name in ['p','b','font','span'] and 90 > len(tag.text) > 13:
        if len([word for word in ['for','quarterly','fiscal','period' 'the', 'ended'] if word in tag.text.lower()]) >= 3:
            return True
        else:
            return False
    else:
        return False

def find_report(filingpath):
    result = None
    url = f'https://mblazr.com/static/filings/{filingpath}'
    html = httpx.get(url).text
    soup = BeautifulSoup(html, 'lxml')
    date_tag = soup.find('ix:nonnumeric', format="ixt:datemonthdayyearen")
    
    if date_tag:
        result  = date_tag.text

    else:
        tag = soup.find(is_report_tag)
        if tag:
            result = tag.text

    if type(result) is str:
        result = result.replace('\\n', '').replace('\n', '').replace('\xa0','').replace('&nbsp;','')
        result = result.lower().split('ended')[-1]

    return (result, url)

def check_report(filing):
    report = Quarterly.objects.filter(filing=filing.filingpath).count()
    if report == 0:
        result, url = find_report(filing.filingpath)
        error = None
        if result == None:
            error = "couldn't find report date"
        try:
            Quarterly.objects.create(quarterly=result, url=url, cik=filing.cik, error=error, date=(datetime.now()).strftime("%Y-%m-%d %H:%M:%S"), filing=filing.filingpath)
        except Exception as e:
            print(e)

    # Uncomment to update filings too
    # else:
    #     result, url = find_report(filing.filingpath)
    #     error = None
    #     if result == None:
    #         error = "couldn't find report date"
    #     try:
    #         Quarterly.objects.filter(filing=filing.filingpath).update(quarterly=result, url=url, cik=filing.cik, error=error, date=(datetime.now()).strftime("%Y-%m-%d %H:%M:%S"), filing=filing.filingpath)
    #     except Exception as e:
    #         print(e)
    
def scrap_one_company(ticker):
    company = Company.objects.get(ticker=ticker)
    filings = Filing.objects.filter(company_id=company.id)

    [check_report(filing) for filing in filings if '.htm' in filing.filingpath]
    print(' Ended')


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