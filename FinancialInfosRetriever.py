__author__ = 'guillaume'

import requests as http
import re  # regular expression
import bs4 as BeautifulSoup
import json
import os
import unicodedata
import csv


symbols = {'COS'}
symbols = {'RY','CM','PWF','BNS','MFC','FTS','TRP','AGF.B','BMO','HSE','TD','ENB','TA','FCR','CU','ESI','MTL',
           'RCI.B','WN','PSI','CJR.B','TRI','CP','COS','LNF','ECA','TCL.A','CFW','BTE','FTT','SNC','CPG','BDT',
           'CTY','IMO','POT','EMA','BCE','MDI','BBD.B','TCK.B','NA','ENF','BDT','AI','FC','BDI','BNS','LB','ACD',
           'BMO','MIC','POW','CM','CPX','SDY'}

# *****************************************
# Definition of the class WineItem
# *****************************************
class FinancialInfos:
    def __init__(self):
        self.name = None
        self.code = None
        self.sector = None
        self.dividend = None
        self.dividendYield = None
        self.payout = None        
        self.dividendPeriod = None #A-Jan/Apr/Jul/Oct, B-Feb/May/Aug/Nov, C-Mar/Jun/Sep/Dec, S-Semi-annual, M-Montly
        self.priceEarningRatio = None
        self.earningPerShare = None        
        self.bookValuePerShare = None
        self.urlWSJ = None
        self.urlTMXquote = None
        self.urlTMXcmpy = None

    def to_json(self):
        seriazable_object = self.__dict__
        # other method : json.dumps(newWine, indent=4, default=jdefault) #default(obj) is a function that should return
        # a serializable version of obj or raise TypeError
        # where def jdefault(o) : return o.__dict__
        return json.dumps(seriazable_object, indent=4)

def jdefault(o):
    return o.__dict__


def writeToCsv(infos, filename):
    with open(filename, 'wb') as csvfile:
        fieldnames = ['name', 'code', 'sector', 'dividend', 'dividendYield', 'payout', 'dividendPeriod', \
            'priceEarningRatio', 'earningPerShare', 'bookValuePerShare', 'urlWSJ', 'urlTMXquote', 'urlTMXcmpy']
        #fieldnames = json.loads(infos[0].to_json()).keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for info in infos:
            data = json.loads(info.to_json())
            writer.writerow(data)


#def readFromCsv(filename):
#    with open('names.csv') as csvfile:
#        reader = csv.DictReader(csvfile)
#        for row in reader:
#            print(row['first_name'], row['last_name'])


def RetrieveInfos(symbols):

    listOfCompagnies = []

    for symbol in symbols:
        financialInfos = FinancialInfos()
        financialInfos.code = symbol

        # Ouverture de la page web
        financialInfos.urlWSJ = u'http://quotes.wsj.com/CA/XTSE/' + re.sub('\.','',symbol) + '/financials'
        financialInfos.urlTMXquote = u'http://web.tmxmoney.com/quote.php?qm_symbol=' + symbol
        financialInfos.urlTMXcmpy = u'http://web.tmxmoney.com/company.php?qm_symbol=' + symbol

        requestWSJ = http.get(financialInfos.urlWSJ)
        htmlWSJ = requestWSJ.text  # .decode('utf-8')
        htmlWSJ = unicodedata.normalize('NFKD', htmlWSJ).encode('ASCII', 'ignore')
        source_site_codeWSJ = BeautifulSoup.BeautifulSoup(htmlWSJ, "html.parser")

        requestTMXquote = http.get(financialInfos.urlTMXquote)
        htmlTMXquote = requestTMXquote.text  # .decode('utf-8')
        htmlTMXquote = unicodedata.normalize('NFKD', htmlTMXquote).encode('ASCII', 'ignore')
        source_site_codeTMXquote = BeautifulSoup.BeautifulSoup(htmlTMXquote, "html.parser")

        requestTMXcmpy = http.get(financialInfos.urlTMXcmpy)
        htmlTMXcmpy = requestTMXcmpy.text  # .decode('utf-8')
        htmlTMXcmpy = unicodedata.normalize('NFKD', htmlTMXcmpy).encode('ASCII', 'ignore')
        source_site_codeTMXcmpy = BeautifulSoup.BeautifulSoup(htmlTMXcmpy, "html.parser")
        
        # Stock name
        div = source_site_codeTMXquote.find('div', class_='quote-name')
        if div is not None:
            financialInfos.name = div.h2.text

        print ''
        print '************************************************'
        print '{0} - {1}'.format(financialInfos.name, financialInfos.code)
        print '************************************************'
        
        for result in source_site_codeWSJ.find_all('table'):        
            # Book Value Per Share
            bvps = result.find('td', text='Book Value Per Share')                    
            if bvps is not None:
                financialInfos.bookValuePerShare = bvps.findNext('td').text
                if financialInfos.bookValuePerShare != 'N/A':
                    financialInfos.bookValuePerShare = float(financialInfos.bookValuePerShare)
                print 'Book Value Per Share: {0}'.format(financialInfos.bookValuePerShare)


        dfreq = None
        month = None
        for result in source_site_codeTMXquote.find_all('table', class_='detailed-quote-table'):
            # Dividend
            div = result.find('td', text='Dividend:')   
            if div is not None:
                financialInfos.dividend = div.findNext('td').text;
                if financialInfos.dividend != 'N/A':
                    m = re.search('((\d+\.\d*))', financialInfos.dividend)
                    financialInfos.dividend = float(m.group(1))
                else:
                    financialInfos.dividend = None
                print 'Dividend: {0}'.format(financialInfos.dividend)
            # Div. Frequency
            freq = result.find('td', text='Div. Frequency:')                    
            if freq is not None:  
                dfreq = freq.findNext('td').text;          
                print 'Dividend Frequency: {0}'.format(dfreq)
            # Yield
            divYield = result.find('td', text='Yield:')    
            if divYield is not None:  
                financialInfos.dividendYield = divYield.findNext('td').text
                if financialInfos.dividendYield != 'N/A':
                    financialInfos.dividendYield = float(financialInfos.dividendYield )
                print 'Dividend Yield: {0}'.format(financialInfos.dividendYield)
            #Ex-Div Date
            date = result.find('td', text='Ex-Div Date:')        
            if date is not None:  
                month = date.findNext('td').text;
                if month != 'N/A':
                    m = re.search('((\d+)/(\d+)/(\d+))', month)
                    month = int(m.group(2))
                print 'Month: {0}'.format(month)            

            # P/E ratio
            per = result.find('td', text='P/E Ratio:')    
            if per is not None:
                financialInfos.priceEarningRatio = per.findNext('td').text
                if financialInfos.priceEarningRatio != 'N/A':
                    financialInfos.priceEarningRatio = float(financialInfos.priceEarningRatio)
                print 'PER: {0}'.format(financialInfos.priceEarningRatio)
            # EPS
            eps = result.find('td', text='EPS:')                
            if eps is not None:
                financialInfos.earningPerShare = eps.findNext('td').text;
                if financialInfos.earningPerShare != 'N/A':
                    financialInfos.earningPerShare = float(financialInfos.earningPerShare)
                print 'EPS: {0}'.format(financialInfos.earningPerShare)

        factor = 1
        if dfreq is not None and dfreq != 'N/A':
            if dfreq == 'Monthly':
                financialInfos.dividendPeriod = 'Monthly'
                factor = 12
            elif dfreq == 'Semi-Annual':
                financialInfos.dividendPeriod = 'Semi-Annual'
                factor = 2
            elif dfreq == 'Quarterly' and month is not None:#A-Jan/Apr/Jul/Oct, B-Feb/May/Aug/Nov, C-Mar/Jun/Sep/Dec, S-Semi-Annual, M-Montly
                factor = 4
                if month == 1 or month == 4 or month == 7  or month == 10:
                    financialInfos.dividendPeriod = u'Jan/Apr/Jul/Oct'
                elif month == 2 or month == 5 or month == 8  or month == 11:
                    financialInfos.dividendPeriod = u'Feb/May/Aug/Nov'
                elif month == 3 or month == 6 or month == 9  or month == 12:
                    financialInfos.dividendPeriod = u'Mar/Jun/Sep/Dec'
        else:
            financialInfos.dividendPeriod = 'N/A'
        print 'Dividend Period: {0}'.format(financialInfos.dividendPeriod)
        
        financialInfos.sector = 'N/A'
        for result in source_site_codeTMXcmpy.find_all('table'):
            # Sector
            sec = result.find('td', text='Sector:')    
            if sec is not None:
                financialInfos.sector = sec.findNext('td').text;
                print 'Sector: {0}'.format(financialInfos.sector)

        if financialInfos.dividend is not None and financialInfos.earningPerShare is not None:
            financialInfos.payout = financialInfos.dividend * factor / financialInfos.earningPerShare
        else:
            if financialInfos.dividend is None:
                financialInfos.dividend = 'N/A'
            if financialInfos.earningPerShare is None:
                financialInfos.earningPerShare = 'N/A'
            financialInfos.payout = 'N/A'

        listOfCompagnies.append(financialInfos)

    with open('High yield stocks.json', mode='w') as outfile:
        json.dump(listOfCompagnies, outfile, default=jdefault, indent=4)

    writeToCsv(listOfCompagnies, 'Financial Infos.csv')

# *****************************************
# Main called function
# *****************************************
if __name__ == '__main__':
    RetrieveInfos(symbols)
    print "Finished!"