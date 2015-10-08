﻿__author__ = 'guillaume'

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
        self.industry = None
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
    # Ouverture de la page web
    urlWSJ = u'http://quotes.wsj.com/CA/XTSE/RY/financials'
    urlTMXquote = u'http://web.tmxmoney.com/quote.php?qm_symbol=RY'
    urlTMXcmpy = u'http://web.tmxmoney.com/company.php?qm_symbol=RY'

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
    financialInfos = FinancialInfos()

    for result in results:
        # EPS
        eps = result.find('span', text='Earnings Per Share')                
        if eps is not None:
            financialInfos.eps = eps.findNext('span').text;
            m = re.search('((\d+\.\d*))', financialInfos.eps)
            financialInfos.eps = m.group(1)
            print 'EPS: {0}'.format(financialInfos.eps)
        # Book Value Per Share
        bvps = result.find('td', text='Book Value Per Share')        
        if bvps is not None:
            financialInfos.bookValuePerShare = bvps.findNext('td').text;
            print 'Book Value Per Share: {0}'.format(financialInfos.bookValuePerShare)
        # P/E ratio

    #Dans WSJ, on cherche
    #* EPS
    #<td> <span class="data_lbl">Earnings Per Share</span> <span class="data_data"> <span class="marketDelta deltaType-positive">+6.03</span> </span> </td>
    #* Book to value per share
    #<tr class="cr_financials_row"> <td class="data_lbl">Book Value Per Share</td> <td class="data_data">38.23</td> <td class="data_smallgraph"> <span class="data_data">-</span> </td> </tr>
    #* P/E ratio
    #<tr> <td> <span class="data_lbl updated-intraday">P/E Ratio <small class="data_meta">(TTM)</small></span> <span class="data_data"> <span class="marketDelta noChange">11.16</span> </span> </td> </tr>

    #Dans TMX quote
    #* Dividende 
    #* Yield
    #* Calcul du payout ratio
    #* Date du dividende
    #* Frequence du dividende
    #http://web.tmxmoney.com/quote.php?qm_symbol=RY
    #<tr>
    #   <td class="">Dividend:</td>
	#   <td class="">0.790&nbsp;CAD</td>
	#</tr>
    #<tr class="alt">
	#	<td class="">Div. Frequency:</td>
	#	<td class="">Quaterly</td>
	#</tr>
    #<tr class="">
	#	<td class="">Yield:</td>
	#	<td class="">4,316</td>
	#</tr>
	#<tr class="alt">
	#	<td class="">Ex-Div Date:</td>
	#	<td class="">10/22/2015</td>	
	#</tr>

    # Dans TMX compagny
    #http://web.tmxmoney.com/company.php?qm_symbol=RY
    # * Secteur 
    #<td class="label">Sector:</td>
    #<td class="data">Financial Services</td>)

# *****************************************
# Main called function
# *****************************************
if __name__ == '__main__':
    RetrieveInfos()
    print "Finished!"