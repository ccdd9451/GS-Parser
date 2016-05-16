from bs4 import BeautifulSoup
import re


RE_AMOUNT = r'About ([0-9|,]+) results'
RE_ID = r'cites=([0-9]+)'
RE_CITED_NUM = r'Cited by ([0-9]+)'
RE_REFINFO = r'q=related:(.*?):scholar'

def Parsing(obj):
    content = obj.source
    soup = BeautifulSoup(content, 'html.parser')
    amounttext = soup.find('div', id='gs_ab_md').text
    amount = int(re.search(REAMOUNT, amounttext).group(1).replace(',',''))
    results = soup.findAll('div', class_='gs_ri')
    r = []
    for result in results:
        fl = list(result.find('div', class_='gs_fl').findAll('a'))
        rd = {}
        rd['name'] = result.h3.a.text
        rd['link'] = result.h3.a['href']
        rd['id'] = int(re.search(RE_ID, fl[0]['href']).group(1))
        rd['cnum'] = int(re.search(RE_CITED_NUM, fl[0].text))
        rd['refurl'] = re.search(RE_REFINFO, fl[1]['href'])
        r.append(rd)
    return r, amount





