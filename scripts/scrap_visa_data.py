from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import json

''' This script scraps data from visaindex.com '''

# Get the list for all passports on visaindex.com
# Comments of text treatments included
url = 'https://visaindex.com/'
req = Request(
    url=url, 
    headers={'User-Agent': 'Mozilla/5.0'}
)
page = urlopen(req).read()
html = page.decode("utf-8")
soup = BeautifulSoup(html, "html.parser") # use BeautifulSoup to get rid of non-text contents
txt = soup.get_text()
txt = txt.replace("\n","") # remove unnecessary new lines

index0 = txt.find('View all passports') # where to locate the passports
index1 = txt.find('Do I need a visa?')
c_list = txt[index0:index1]
index0 = c_list.find('Singapore') # the list is ordered in visaindex rank, Singapore is No. 1 atm
c_list = c_list[index0:]
c_list = c_list.replace("Rank: ",";") # change some text to a spliter
for i in range(20):
    c_list = c_list.replace("  "," ") # remove redundant spaces
c_list = c_list.split(" ;")

c_list0 = [] # the passport list to use later
for c in c_list:
    new_c = ''.join((x for x in c if not x.isdigit())) # remove the rank number from the texts
    new_c = new_c.strip()
    c_list0.append(new_c)
c_list0.remove('') # remove the empty item

# Download the passport visa info
special = ['.', '(', ')','’'] # identified special symbols to be replaced in urls

# 5 types of visa requirements
classification = ['Visa free access',
                  'Visa on arrival',
                  'eTA',
                  'Visa online',
                  'Visa required'] 

def load_page(c):
    ''' Given a country c, scrap its page text '''
    c_new = c
    for i in special:
        c_new = c_new.replace(i,"") # remove special character
    c_new = c_new.replace(" ","-") # replace space with -
    if c == 'Myanmar': 
        ''' Myanmar has a special url
        # https://visaindex.com/country/myanmar-burma-passport-ranking/
        '''
        c_new += '-burma'
    url = "https://visaindex.com/country/"+c_new+"-passport-ranking/" # visaindex.com url format
    
    req = Request(
        url=url, 
        headers={'User-Agent': 'Mozilla/5.0'}
        )
    page = urlopen(req).read()
    html = page.decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    txt = soup.get_text()
    txt = txt.replace("\n","")
    
    return txt

def visa_req(c,txt,visa_type):
    ''' From the page text, identify visa requiremnts
    # txt: page text
    # visa_type: int, index for the visa requiment classification
    '''
    
    if txt.find('and 0 eTA') != -1 and visa_type == 2:
        # Some countires don't have eTA exemption, return eTA data as []
        return 0, []
    else:
        index0 = txt.find(classification[visa_type])
        if visa_type == 4:
            # txtend: used to locate the ending index if visa_type is 'Visa required'
            txt_end = c+' Passport RankingThe '+c+' passport ranking relative to other global passports'
            index1 = txt.find(txt_end)
        elif txt.find('and 0 eTA') != -1 and visa_type == 1:
            # If eTA is empty, relocated ending index
            index1 = txt.find(classification[visa_type+2])
        else:
            index1 = txt.find(classification[visa_type+1])
        txt_tmp = txt[index0:index1]
        txt_tmp = txt_tmp.replace("\t","$")
        for i in range(20):
            txt_tmp = txt_tmp.replace("$$","$")
        txt_tmp = txt_tmp.split("$")
        txt_tmp.remove(classification[visa_type])
        txt_tmp.remove('Destinations')
        if '' in txt_tmp:
            txt_tmp.remove('')
    
        if int(txt_tmp[0])+1 != len(txt_tmp):
            # Check if the data length matches the number on visaindex.com
            print(int(txt_tmp[0]),len(txt_tmp))
            raise Exception("Error: visa free access list length")
        
        # return data length, data
        return int(txt_tmp[0]), txt_tmp[1:]

# Download the data as a list of dictionary
data = []
denominator = len(c_list0) # total number of passports
counter = 1 # counter to show progress 
for c in c_list0:
    print(counter,'/',denominator,': working on ',c)
    counter += 1
    txt = load_page(c)
    
    out =  []
    # Only scrap the first 3 classifications that involve visa exemption
    for i in range(3): 
        a,b = visa_req(c,txt,i)
        out.append(b)
    data.append({'name':c,
                 'Visa free access':out[0],
                 'Visa on arrival':out[1],
                 'eTA':out[2]})

# Save the data to json
with open('../data/visa_data.json', 'w') as file:
    json.dump(data,file)