from .models import Filing, Company, Funds, Directors, Executives

import textdistance


def populate_filings():

    for company in Company.objects.all():

        Filing.objects.filter(cik=company.cik, name=company.name).update(company=company)
        
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
        
        Funds.objects.filter(company=name).update(company_rep=company)
    

    print('Done with Funds')

def populate_executives():

    for company in Company.objects.all():

        name = company.name
        
        Executives.objects.filter(company=name).update(company_rep=company)
        
    
    print('Done with Exectuives')

def populate_directors():

    for company in Company.objects.all():

    # company = Company.objects.filter(cik=1318605).first()

        Directors.objects.filter(company=company.name).update(company_rep=company)
    # directors = Directors.objects.filter(company=company.name)

    # allDirectors = list(Directors.objects.all())
    # allDirectorsCount = len(allDirectors)

    # for person in directors:
    #     if person:
    #         personA = person.director.replace("Mr.", '')
    #         personA = person.director.replace("Dr.", '')
    #         personA = person.director.replace("Ms.", '')
    #         a = set([s for s in personA if s != "," and s != "." and s != " "])
    #         aLast = personA.split(' ')[-1]
    #         if (len(personA.split(' ')) == 1):
    #             aLast = personA.split('.')[-1]
        
    #     comps = []
        
    #     for check in range(allDirectorsCount):

    #         check = allDirectors[check]
        
    #         if person:
        
    #             personB = check.director.replace("Mr.", '')
    #             personB = check.director.replace("Dr.", '')
    #             personB = check.director.replace("Ms.", '')
    #             bLast = personB.split(' ')[-1]
        
    #             if (len(personB.split(' ')) == 1):
    #                 bLast = personB.split('.')[-1]
    #             # print(personA, aLast, person.company, personB, bLast, check.company)
        
    #             if aLast == bLast:
    #                 # first check jaccard index to speed up algo, threshold of .65
    #                 b = set([s for s in personB if s !=
    #                          "," and s != "." and s != " "])
    #                 if (len(a.union(b)) != 0):
    #                     jaccard = float(
    #                         len(a.intersection(b)) / len(a.union(b)))
        
    #                 else:
    #                     jaccard = 1
    #                 # print(personA, personB, jaccard)
        
    #                 if (jaccard > 0.65):
    #                     # run Ratcliff-Obershel for further matching, threshold of .75 and prevent self-match
    #                     sequence = textdistance.ratcliff_obershelp(
    #                         personA, personB)
    #                     # print(sequence)
    #                     if sequence > 0.75 and company.name != check.company:
    #                         # comps.append(check.company)
    #                         other_company = Company.objects.get(name=check.name)
    #                         person.other_companies.add(other_company)
                            
    #     if not comps:
    #          comps.append('Director is not on the board of any other companies')
    # # filing.save()

    print('Done with Directors')


def populate_all():
    populate_filings()
    populate_funds()
    populate_executives()
    populate_directors()