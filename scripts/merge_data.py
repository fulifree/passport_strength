import json
import pandas as pd
import pycountry

''' This script merge several datasets
# Visa exemption data, scrapped from visaindex.com
# Population data, downloaded from data.worldbank.org
# Income group data, downloaded from data.worldbank.org
# ISO2 codes, from pycountry
'''
# Load visa data
f = open('../data/visa_data.json')
data = json.load(f)

# Creat visa dataframe
df_visa = {'Country Name':[],
           'Visa free access':[],
           'Visa on arrival':[],
           'eTA':[],
           'Visa free to':[],
           'Visa on arrival to':[],
           'eTA to':[]}

for d in data:
    df_visa['Country Name'].append(d['name'])
    df_visa['Visa free access'].append(len(d['Visa free access']))
    df_visa['Visa on arrival'].append(len(d['Visa on arrival']))
    df_visa['eTA'].append(len(d['eTA']))
    
    to1 = 0
    to2 = 0
    to3 = 0
    for j in data:
        to1 += int(d['name'] in j['Visa free access'])
        to2 += int(d['name'] in j['Visa on arrival'])
        to3 += int(d['name'] in j['eTA'])
    
    df_visa['Visa free to'].append(to1)
    df_visa['Visa on arrival to'].append(to2)
    df_visa['eTA to'].append(to3)

df_visa = pd.DataFrame.from_dict(df_visa)

# Visa free access = visa free + visa on arrival + eTA
df_visa['total access'] = df_visa['Visa free access'] + df_visa['Visa on arrival'] + df_visa['eTA']
# Visa free treaty given out
df_visa['total to'] = df_visa['Visa free to'] + df_visa['Visa on arrival to'] + df_visa['eTA to']
# Sort by country name for easy inspection
df_visa = df_visa.sort_values(by=['Country Name'])

# Population data from World Bank
df_population = pd.read_csv('../data/API_SP/API_SP.POP.TOTL_DS2_en_csv_v2_5454896.csv',
                            skiprows=3,
                            usecols=['Country Name','Country Code','2021'])
# Income group data from World Bank
df_income = pd.read_csv('../data/API_SP/Metadata_Country_API_SP.POP.TOTL_DS2_en_csv_v2_5454896.csv',
                        usecols=['Country Code','Region','IncomeGroup'])

# Merge population and income group data
df_merge = pd.merge(df_population,df_income,how="left",on=['Country Code'])
df_merge = df_merge.sort_values(by=['Country Name'])

# Mannually change some country names to match the visa data
df_merge.at[96,'Country Name'] = 'Hong Kong'
df_merge.at[146,'Country Name'] = 'Macao'
df_merge.at[251,'Country Name'] = 'United States of America'
df_merge.at[44,'Country Name'] = 'Congo'
df_merge.at[43,'Country Name'] = 'Congo (Dem. Rep.)'
df_merge.at[41,'Country Name'] = 'Cote d’Ivoire (Ivory Coast)'
df_merge.at[125,'Country Name'] = 'Saint Kitts and Nevis'
df_merge.at[133,'Country Name'] = 'Saint Lucia'
df_merge.at[126,'Country Name'] = 'South Korea'
df_merge.at[262,'Country Name'] = 'Yemen'
df_merge.at[23,'Country Name'] = 'Bahamas'
df_merge.at[31,'Country Name'] = 'Brunei'
df_merge.at[47,'Country Name'] = 'Cape Verde'
df_merge.at[54,'Country Name'] = 'Czech Republic'
df_merge.at[67,'Country Name'] = 'Egypt'
df_merge.at[86,'Country Name'] = 'Gambia'
df_merge.at[112,'Country Name'] = 'Iran'
df_merge.at[122,'Country Name'] = 'Kyrgyzstan'
df_merge.at[129,'Country Name'] = 'Laos'
df_merge.at[79,'Country Name'] = 'Micronesia'
df_merge.at[193,'Country Name'] = 'North Korea'
df_merge.at[202,'Country Name'] = 'Russia'
df_merge.at[221,'Country Name'] = 'Slovakia'
df_merge.at[227,'Country Name'] = 'Syria'
df_merge.at[244,'Country Name'] = 'Turkey'
df_merge.at[254,'Country Name'] = 'Venezuela'

# Merge visa data and population-income data
df = pd.merge(df_visa,df_merge,how="left",on=['Country Name'])

# Mannual input of missing data from World Bank
# Taiwan
df.at[173,'2021'] = 23.57*1000000
df.at[173,'Region'] = 'East Asia & Pacific'
df.at[173,'IncomeGroup'] = 'High income'

# Vatican City
df.at[193,'2021'] = 825
df.at[193,'Region'] = 'Europe & Central Asia'
df.at[193,'IncomeGroup'] = 'High income'

# Palestinian Territories
df.at[135,'2021'] = 4.923*1000000
df.at[135,'Region'] = 'Europe & Central Asia'
df.at[135,'IncomeGroup'] = 'Lower middle income'

# Add iso2 codes 
def name_to_iso2(name):
    if name == 'Cape Verde': name = 'Cabo Verde'
    if name == 'Cote d’Ivoire (Ivory Coast)': name = 'cote'
    if name == 'Laos': name = 'lao'
    if name == 'Palestinian Territories': name = 'palestine'
    if name == 'St. Vincent and the Grenadines': name = 'vincent'
    if name == 'Congo (Dem. Rep.)':
        return 'CD'
    else:
        country = pycountry.countries.search_fuzzy(name)
        return country[0].alpha_2

df['iso2'] = df.apply(lambda row: name_to_iso2(row['Country Name']),axis=1)

# Save data to csv
df.to_csv('../data/visa_population_income.csv',index=False)