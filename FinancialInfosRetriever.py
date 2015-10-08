__author__ = 'guillaume'

import requests as http
import re  # regular expression
import bs4 as BeautifulSoup
import json
import os
import unicodedata

# *****************************************
# Definition of the class WineItem
# *****************************************
class FinancialInfos:
    def __init__(self):
        self.urlWSJ = None
        self.urlTMX = None
        self.earningPerShare = None
        self.priceEarningRatio = None
        self.bookValuePerShare = None
        self.sector = None
        self.payout = None
        self.dividend = None
        self.dividendYield = None
        self.dividendPeriod = None #A-Jan/Apr/Jul/Oct, B-Feb/May/Aug/Nov, C-Mar/Jun/Sep/Dec, S-Semi-annual, M-Montly

    def to_json(self):
        seriazable_object = self.__dict__
        # other method : json.dumps(newWine, indent=4, default=jdefault) #default(obj) is a function that should return
        # a serializable version of obj or raise TypeError
        # where def jdefault(o) : return o.__dict__
        return json.dumps(seriazable_object, indent=4)

def RetrieveInfos():
    symbols = {'RY','CM','PWF','BNS','MFC','FTS','TRP','AGF.B','BMO','HSE','TD','ENB','TA','FCR','CU','ESI','MTL',
               'RCI.B','WN','PSI','CJR.B','TRI','CP','COS','LNF','ECA','TCL.A','CFW','BTE','FTT','SNC','CPG','BDT',
               'CTY','IMO','POT','EMA','BCE','MDI','BBD.B','TCK.B'}

    for symbol in symbols:
        # Ouverture de la page web
        urlWSJ = u'http://quotes.wsj.com/CA/XTSE/' + symbol + '/financials'
        urlTMXquote = u'http://web.tmxmoney.com/quote.php?qm_symbol=' + symbol
        urlTMXcmpy = u'http://web.tmxmoney.com/company.php?qm_symbol=' + symbol

        requestWSJ = http.get(urlWSJ)
        htmlWSJ = requestWSJ.text  # .decode('utf-8')
        htmlWSJ = unicodedata.normalize('NFKD', htmlWSJ).encode('ASCII', 'ignore')
        source_site_codeWSJ = BeautifulSoup.BeautifulSoup(htmlWSJ, "html.parser")

        requestTMXquote = http.get(urlTMXquote)
        htmlTMXquote = requestTMXquote.text  # .decode('utf-8')
        htmlTMXquote = unicodedata.normalize('NFKD', htmlTMXquote).encode('ASCII', 'ignore')
        source_site_codeTMXquote = BeautifulSoup.BeautifulSoup(htmlTMXquote, "html.parser")

        requestTMXcmpy = http.get(urlTMXcmpy)
        htmlTMXcmpy = requestTMXcmpy.text  # .decode('utf-8')
        htmlTMXcmpy = unicodedata.normalize('NFKD', htmlTMXcmpy).encode('ASCII', 'ignore')
        source_site_codeTMXcmpy = BeautifulSoup.BeautifulSoup(htmlTMXcmpy, "html.parser")
        #with open('QuoteRY.html', mode='w') as file:
        #        file.write(html)
     
        # re.compile pour utiliser une expression reguliere avec la methode
        # 'match'.
        # Ici on cherche tous les div dont l'id contient 'result'
        resultsWSJ = source_site_codeWSJ.find_all('table')
        resultsTMXquote = source_site_codeTMXquote.find_all('table')
        resultsTMXcmpy = source_site_codeTMXcmpy.find_all('table')
        financialInfos = FinancialInfos()

        for result in resultsWSJ:        
            # Book Value Per Share
            bvps = result.find('td', text='Book Value Per Share')        
            if bvps is not None:
                financialInfos.bookValuePerShare = bvps.findNext('td').text;
                print 'Book Value Per Share: {0}'.format(financialInfos.bookValuePerShare)        

        for result in resultsTMXquote:
            # Dividend
            div = result.find('td', text='Dividend:')                
            if div is not None:
                financialInfos.dividend = div.findNext('td').text;
                m = re.search('((\d+\.\d*))', financialInfos.dividend)
                financialInfos.dividend = m.group(1)
                print 'Dividend: {0}'.format(financialInfos.dividend)
            # Div. Frequency
            freq = result.find('td', text='Div. Frequency:')        
            if freq is not None:  
                dfreq = freq.findNext('td').text;          
                print 'Dividend Frequency: {0}'.format(dfreq)
            # Yield
            divYield = result.find('td', text='Yield:')        
            if divYield is not None:  
                financialInfos.dividendYield = divYield.findNext('td').text;          
                print 'Dividend Yield: {0}'.format(financialInfos.dividendYield)
            #Ex-Div Date
            date = result.find('td', text='Ex-Div Date:')        
            if date is not None:  
                financialInfos.dividendPeriod = date.findNext('td').text;          
                print 'Date: {0}'.format(financialInfos.dividendPeriod)
            # P/E ratio
            per = result.find('td', text='P/E Ratio:')        
            if per is not None:
                financialInfos.priceEarningRatio = per.findNext('td').text;
                print 'PER: {0}'.format(financialInfos.priceEarningRatio)
            # EPS
            eps = result.find('td', text='EPS:')                
            if eps is not None:
                financialInfos.eps = eps.findNext('td').text;
                print 'EPS: {0}'.format(financialInfos.eps)

        for result in resultsTMXcmpy:
            # Sector
            sec = result.find('td', text='Sector:')                
            if sec is not None:
                financialInfos.sector = sec.findNext('td').text;
                print 'Sector: {0}'.format(financialInfos.sector)

# *****************************************
# Main called function
# *****************************************
if __name__ == '__main__':
    RetrieveInfos()
    print "Finished!"