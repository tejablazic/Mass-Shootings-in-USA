import requests
import re
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim

# Funkcije ========================================================================================================================

def str_to_int(tabela):
    "Vzame tabelo in vsak element spremeni iz niza v število."
    nova_tabela = list()
    for element in tabela:
        nova_tabela.append(int(element))
    return nova_tabela


def str_to_float(tabela):
    "Vzame tabelo in vsak element spremeni iz celega v decimalno število."
    nova_tabela = list()
    for element in tabela:
        nova_tabela.append(float(element))
    return nova_tabela


def najdi_zvezno_drzavo(mesto):
    '''Za dano mesto vrne zvezno državo, v kateri se mesto nahaja.'''
    geolocator = Nominatim(user_agent = "PythonProjekt") # user_agent določa uporabniško ime za poizvedbo
    lokacija = geolocator.geocode(mesto + ", USA", country_codes="us", addressdetails = True) # poišče lokacijo
    if lokacija:  # če najde lokacijo, iz nje izlušči ime zvezne države, v kateri se nahaja mesto
        return lokacija.raw['display_name'].split(", ")[-2]
    else:
        return "/"


def zvezne_drzave(tabela):
    '''Vrne tabelo mest/držav, ki so zapisane za vejico.'''
    zvezne_drzave_incidentov = list()
    for lokacija in tabela: # element oblike 'mesto, država' oz. 'kraj, mesto'
        if ',' in lokacija:
            zvezne_drzave_incidentov.append(lokacija.split(',')[1].strip())
        else:
            zvezne_drzave_incidentov.append(lokacija)
    return zvezne_drzave_incidentov


def zvezne_drzave_v2(mesta):
    '''Vzame mesta in vrne tabelo zveznih držav. Funkcijo uporabimo v podatkih, kjer sta dve mesti, ločeni z "and". Pomagamo si s funkcijo najdi_zvezno_drzavo.'''
    zv_drzave_leto = list()
    for mesto in zvezne_drzave(mesta):
        zv_drzave_leto.append(najdi_zvezno_drzavo(mesto))
    return zv_drzave_leto


def streljanja_v_letu(leto):
    '''Število streljanj v izbranem letu.'''
    # toliko kot je datumov, toliko je streljanj v posameznem letu
    vsa_leta = {2010 : datumi_2010, 2011 : datumi_2011, 2012 : datumi_2012, 2013 : datumi_2013, 2014 : datumi_2014, 2015 : datumi_2015, 2016 : datumi_2016, 2017 : datumi_2017,
                2018 : datumi_2018, 2019 : datumi_2019, 2020 : datumi_2020, 2021 : datumi_2021, 2022 : datumi_2022, 2023 : datumi_2023, 2024 : datumi_2024}
    return len(vsa_leta[leto])
    
    
def ranjeni_v_letu(leto):
    '''Število ranjenih v izbranem letu.'''
    vsi_ranjeni = {2010 : sest_poskodovani_2010, 2011 : sest_poskodovani_2011, 2012 : sest_poskodovani_2012, 2013 : sest_poskodovani_2013, 2014 : sest_poskodovani_2014,
                   2015 : sest_poskodovani_2015, 2016 : sest_poskodovani_2016, 2017 : sest_poskodovani_2017, 2018 : sest_poskodovani_2018, 2019 : sest_poskodovani_2019,
                   2020 : sest_poskodovani_2020, 2021 : sest_poskodovani_2021, 2022 : sest_poskodovani_2022, 2023 : sest_poskodovani_2023, 2024 : sest_poskodovani_2024}
    return vsi_ranjeni[leto]


def mrtvi_v_letu(leto):
    '''Število smrtnih žrtev v izbranem letu.'''
    vsi_mrtvi = {2010 : sest_mrtvi_2010, 2011 : sest_mrtvi_2011, 2012 : sest_mrtvi_2012, 2013 : sest_mrtvi_2013, 2014 : sest_mrtvi_2014, 2015 : sest_mrtvi_2015,
           2016 : sest_mrtvi_2016, 2017 : sest_mrtvi_2017, 2018 : sest_mrtvi_2018, 2019 : sest_mrtvi_2019, 2020 : sest_mrtvi_2020, 2021 : sest_mrtvi_2021,
           2022 : sest_mrtvi_2022, 2023 : sest_mrtvi_2023, 2024 : sest_mrtvi_2024}
    return vsi_mrtvi[leto]


def zdruzi_podatke(od_leta, do_leta, vsi_podatki):
    '''Vrne slovar, ki vsebuje slovarje za leta od "od_leta" do "do_leta", v katerih so zvezne države, datumi incidentov, število ranjenih in število mrtvih.'''
    drzave = dict()
    for leto in range(od_leta, do_leta + 1): # range() ne vključuje do_leta, zato + 1
        leto_podatki = vsi_podatki[leto]  # pridobi podatke za dano leto
        for zvezna_drzava, incidenti, ranjeni, mrtvi in zip(leto_podatki['Zvezne države'], leto_podatki['Incidenti'], leto_podatki['Ranjeni'], leto_podatki['Mrtvi']): # združi elemente seznamov v terke
            if zvezna_drzava not in drzave: # zvezne države še ni v slovarju
                drzave[zvezna_drzava] = [0, 0, 0]
            # dodajanje števil incidentov, ranjenih in mrtvih za posamezno zvezno državo
            drzave[zvezna_drzava][0] += 1
            drzave[zvezna_drzava][1] += int(ranjeni)
            drzave[zvezna_drzava][2] += int(mrtvi)
    return drzave


# Opozorilo o počasnosti ===========================================================================================================
print('Prosimo počakajte, da se program izvede. Hvala za potrpežljivost.')


# Pridobivanje podatkov ============================================================================================================

# Zahteve mesta_drzave

mesta_drzave = requests.get('https://en.wikipedia.org/wiki/List_of_United_States_cities_by_area').text
tab_m_d = mesta_drzave.split('<th>(km<sup>2</sup>)')[3]
tab_m_d = tab_m_d.split('<td>8,399')[0]
vse_lokacije = set()

mes_drz1 = re.findall(r'<td><b><a href="/wiki/.*,_.*" title="(\w*, \w*)">.*</a>', tab_m_d)
for lokacija in mes_drz1:
    vse_lokacije.add(tuple(lokacija.split(', ')))  
mes_drz2 = re.findall(r'<td><a href="/wiki/.*" title=".*">(.*)</a></td>\n<td><a href="/wiki/(.*)" title=".*">.*</a></td>', tab_m_d, re.MULTILINE)
for lokacija in mes_drz2:
    vse_lokacije.add(lokacija)   
mes_drz3 = re.findall(r'<td><b><a href="/wiki/.*" title="(.*, .*)">.*</a></b> \*</td>', tab_m_d)
for lokacija in mes_drz3:
    vse_lokacije.add(tuple(lokacija.split(', ')))   
mes_drz4 = re.findall(r'<td><a href="/wiki/.*" title="(.*, .*)">.*</a><sup id=".*" class="reference"><a href=".*">.*;</a></sup>\*\*</td>', tab_m_d)
for lokacija in mes_drz4:
    vse_lokacije.add(tuple(lokacija.split(', ')))
mes_drz5 = re.findall(r'<td><a href="/wiki/.*" title=".*">(.*)</a> \*\*</td>\n<td><a href="/wiki/.*" title="(.*)">.*</a></td>', tab_m_d, re.MULTILINE)
for lokacija in mes_drz5:
    vse_lokacije.add(lokacija)

lokacije = set()
for lokacija in vse_lokacije:
    lokacije.add((lokacija[0], lokacija[1].replace('" class="mw-redirect', '')))
    
    
# Zahteve za mesta
    # Shrani vse podatke držav, mest, lat, lng vsako v svojo tabelo, razporejeno tako, da se indeksi skladajo in sestavljajo podatke
    # Kasneje bo uporabno za risanje zemljevida

mesta = requests.get('https://lovro.fri.uni-lj.si/api/cities').json()
drzave = list()
list_vseh_mest = list()
lat = list()
lng = list()

for mesto in mesta:
    drzave.append(mesto['country'])
    list_vseh_mest.append(mesto['name'])
    lat.append(mesto['lat'])
    lng.append(mesto['lng'])

us_drzave = drzave.copy()
us_mesta = list_vseh_mest.copy()
us_lat = lat.copy()
us_lng = lng.copy()

for i in range(len(drzave)): # vsa mesta, ki niso v US, nas ne zanimajo, zato jih spremenimo v prazen niz, da jih kasneje odstranimo
    if drzave[i] != "US":
        us_drzave[i] = ''
        us_mesta[i] = ''
        us_lat[i] = ''
        us_lng[i] = ''


# Izolirana ameriška mesta z njihovimi koordinatami, uporabno za risanje zemljevida
    
us_drzave = [x for x in us_drzave if x != '']
us_mesta = [x for x in us_mesta if x != ''] # odstranimo vsa mesta, ki niso v US
us_lat = [x for x in us_lat if x != ''] # dobimo koordinate Ameriških mest
us_lng = [x for x in us_lng if x != '']

ameriska_mesta_koordinate = dict(mesta = us_mesta, lat = us_lat, lng = us_lng) #Slovar USA mest s točnimi koordinatami


# Analiza streljanj

url_streljanja_tabele = requests.get('https://en.wikipedia.org/wiki/List_of_mass_shootings_in_the_United_States').text # link do spletne strani, vir strani v obliko .text
tab_streljanj = url_streljanja_tabele.split('<th>Description') # dobimo tabelo iz wikipedije, kjer so naši podatki
incidenti_2024 = tab_streljanj[1].split('</td></tr></tbody></table>')


# 2024 ##################################################
    # Zbiranje podatkov za leto 2024
    
tabela_incidentov_2024 = list()
datumi_2024 = re.findall(r'<td>(.* .*), 2024', incidenti_2024[0]) # izluščimo datume
skupaj_mesta_2024 = re.findall(r'<td><a href="/wiki/\D*\W*\D*" title="(\D*\W*\D*)">\D*\W*\D*</a>\n', incidenti_2024[0]) # izluščimo mesta
mesta_2024 = list()
for mesto in skupaj_mesta_2024: # "mesto" oblike mesto, država
    mesto_drzava = mesto.split(',')
    novo_mesto = mesto_drzava[0] # dobimo samo mesto
    mesta_2024.append(novo_mesto)
st_mrtvih_ranjenih_2024 = re.findall(r'<td>(\d*).*\n</td>', incidenti_2024[0], re.MULTILINE)
st_mrtvih_ranjenih_2024 = [x for x in st_mrtvih_ranjenih_2024 if x != '']
mrtvi_2024 = st_mrtvih_ranjenih_2024[0::2] # št. mrtvih začne na prvem mestu, vzamemo vsako drugo
poskodovani_2024 = st_mrtvih_ranjenih_2024[1::2] # št. poškodovanih začne na drugem mestu, vzamemo vsako drugo

# naredimo slovar za določeno leto
leto_2024 = {'Zvezne države' : zvezne_drzave(skupaj_mesta_2024)[::-1], # v naš slovar zapišemo zvezne države, zato mesta pretvorimo z ustrezno funkcijo
             'Incidenti' : datumi_2024[::-1], # obrnemo tabele, da so incidenti zapisani od najstarejših do najmlajših
             'Ranjeni' : poskodovani_2024[::-1],
             'Mrtvi' : mrtvi_2024[::-1]}

mrtvi_2024 = str_to_int(mrtvi_2024)
sest_mrtvi_2024 = sum(mrtvi_2024) # seštevek vseh mrtvih v določenem letu
poskodovani_2024 = str_to_int(poskodovani_2024)
sest_poskodovani_2024 = sum(poskodovani_2024) # seštevek vseh poškodovanih v določenem letu


# 2023 ##################################################
    # Zbiranje podatkov za leto 2023
    
# postopek ponavljamo za vsa leta, po potrebi spremenimo
tab_incidenti_2023_1900 = url_streljanja_tabele.split('<th width="60%">Description')
incidenti_2023 = tab_incidenti_2023_1900[1] # tabela incidentov
datumi_2023 = re.findall(r'<td>(.* .*), 2023', incidenti_2023) # datume izluščimo iz tabele incidentov
dodatni_datum_2023 = re.findall(r'<td>(.* .*),  2023', incidenti_2023) # popravimo neustrezen datum
datumi_2023.insert(8, dodatni_datum_2023[0])
mesta_2023_1 = re.findall(r'<td><a href="/wiki/.*?" title=".*?">(.*?)</a>', incidenti_2023, re.MULTILINE)
mesta_2023 = mesta_2023_1[::2] # vzamemo vsak drugi element
st_mrtvih_ranjenih_2023 = re.findall(r'<td>(\d*).*\n</td>', incidenti_2023, re.MULTILINE)
st_mrtvih_ranjenih_2023 = [x for x in st_mrtvih_ranjenih_2023 if x != '']
mrtvi_2023 = st_mrtvih_ranjenih_2023[0::2]
poskodovani_2023 = st_mrtvih_ranjenih_2023[1::2]

zv_drzave_2023 = zvezne_drzave_v2(mesta_2023) # za vsa mesta zapišemo zvezne države, kar bomo potrebovali za analizo po državah
zv_drzave_2023[17] = 'Maine' # popravimo eno mesto
 
leto_2023 = {'Zvezne države' : zv_drzave_2023[::-1],
             'Incidenti' : datumi_2023[::-1],
             'Ranjeni' : poskodovani_2023[::-1],
             'Mrtvi' : mrtvi_2023[::-1]}

mrtvi_2023 = str_to_int(mrtvi_2023)
sest_mrtvi_2023 = sum(mrtvi_2023)
poskodovani_2023 = str_to_int(poskodovani_2023)
sest_poskodovani_2023 = sum(poskodovani_2023)


# 2022 ##################################################
    # Zbiranje podatkov za leto 2022

incidenti_2022 = tab_incidenti_2023_1900[2]
datumi_2022 = re.findall(r'<td>(.* .*), 2022', incidenti_2022)
mesta_2022_1 = re.findall(r'<td><a href="/wiki/.*?" title=".*?">(.*?)</a>', incidenti_2022, re.MULTILINE)
mesta_2022 = mesta_2022_1[::2]
st_mrtvih_ranjenih_2022 = re.findall(r'<td>(\d*).*\n</td>', incidenti_2022, re.MULTILINE)
st_mrtvih_ranjenih_2022 = [x for x in st_mrtvih_ranjenih_2022 if x != '']
mrtvi_2022 = st_mrtvih_ranjenih_2022[0::2]
poskodovani_2022 = st_mrtvih_ranjenih_2022[1::2]   

leto_2022 = {'Zvezne države' : zvezne_drzave_v2(mesta_2022)[::-1],
             'Incidenti' : datumi_2022[::-1],
             'Ranjeni' : poskodovani_2022[::-1],
             'Mrtvi' : mrtvi_2022[::-1]}

mrtvi_2022 = str_to_int(mrtvi_2022)
sest_mrtvi_2022 = sum(mrtvi_2022)
poskodovani_2022 = str_to_int(poskodovani_2022)
sest_poskodovani_2022 = sum(poskodovani_2022)


# 2021 ##################################################
    # Zbiranje podatkov za leto 2021

incidenti_2021 = tab_incidenti_2023_1900[3]
datumi_2021 = re.findall(r'<td>(.* .*), 2021', incidenti_2021)
mesta_2021_1 = re.findall(r'<td><a href="/wiki/.*?" title=".*?">(.*?)</a>', incidenti_2021, re.MULTILINE)
mesta_2021 = mesta_2021_1[::2]
st_mrtvih_ranjenih_2021 = re.findall(r'<td>(\d*).*\n</td>', incidenti_2021, re.MULTILINE)
st_mrtvih_ranjenih_2021 = [x for x in st_mrtvih_ranjenih_2021 if x != '']
mrtvi_2021 = st_mrtvih_ranjenih_2021[0::2]
poskodovani_2021 = st_mrtvih_ranjenih_2021[1::2]

leto_2021 = {'Zvezne države' : zvezne_drzave_v2(mesta_2021)[::-1],
             'Incidenti' : datumi_2021[::-1],
             'Ranjeni' : poskodovani_2021[::-1],
             'Mrtvi' : mrtvi_2021[::-1]}

mrtvi_2021 = str_to_int(mrtvi_2021)
sest_mrtvi_2021 = sum(mrtvi_2021)
poskodovani_2021 = str_to_int(poskodovani_2021)
sest_poskodovani_2021 = sum(poskodovani_2021)


# 2020 ##################################################
    # Zbiranje podatkov za leto 2020

incidenti_2020 = tab_incidenti_2023_1900[4]
datumi_2020 = re.findall(r'<td>(.* .*), 2020', incidenti_2020)
mesta_2020_1 = re.findall(r'<td><a href="/wiki/.*?" title=".*?">(.*?)</a>', incidenti_2020, re.MULTILINE)
mesta_2020 = mesta_2020_1[::2]
st_mrtvih_ranjenih_2020 = re.findall(r'<td>(\d*).*\n</td>', incidenti_2020, re.MULTILINE)
st_mrtvih_ranjenih_2020 = [x for x in st_mrtvih_ranjenih_2020 if x != '']
mrtvi_2020 = st_mrtvih_ranjenih_2020[0::2]
poskodovani_2020 = st_mrtvih_ranjenih_2020[1::2]

leto_2020 = {'Zvezne države' : zvezne_drzave_v2(mesta_2020)[::-1],
             'Incidenti' : datumi_2020[::-1],
             'Ranjeni' : poskodovani_2020[::-1],
             'Mrtvi' : mrtvi_2020[::-1]}

mrtvi_2020 = str_to_int(mrtvi_2020)
sest_mrtvi_2020 = sum(mrtvi_2020)
poskodovani_2020 = str_to_int(poskodovani_2020)
sest_poskodovani_2020 = sum(poskodovani_2020)


# 2019 ##################################################
    # Zbiranje podatkov za leto 2019

incidenti_2019 = tab_incidenti_2023_1900[5]
datumi_2019 = re.findall(r'<td>(.* .*), 2019', incidenti_2019)
mesta_2019_1 = re.findall(r'<td><a href="/wiki/.*?" title=".*?">(.*?)</a>', incidenti_2019, re.MULTILINE)
mesta_2019 = mesta_2019_1[::2]
st_mrtvih_ranjenih_2019 = re.findall(r'<td>(\d*).*\n</td>', incidenti_2019, re.MULTILINE)
st_mrtvih_ranjenih_2019 = [x for x in st_mrtvih_ranjenih_2019 if x != '']
mrtvi_2019 = st_mrtvih_ranjenih_2019[0::2]
poskodovani_2019 = st_mrtvih_ranjenih_2019[1::2]

leto_2019 = {'Zvezne države' : zvezne_drzave_v2(mesta_2019)[::-1],
             'Incidenti' : datumi_2019[::-1],
             'Ranjeni' : poskodovani_2019[::-1],
             'Mrtvi' : mrtvi_2019[::-1]}

mrtvi_2019 = str_to_int(mrtvi_2019)
sest_mrtvi_2019 = sum(mrtvi_2019)
poskodovani_2019 = str_to_int(poskodovani_2019)
sest_poskodovani_2019 = sum(poskodovani_2019)


# 2018 ##################################################
    # Zbiranje podatkov za leto 2018

incidenti_2018 = tab_incidenti_2023_1900[6]
datumi_2018 = re.findall(r'<td><span data-sort-value=".*" style="white-space:nowrap">(.* .*), 2018</span>', incidenti_2018)
datum_2 = re.findall(r'<td><span data-sort-value=".*" style="white-space:nowrap">(.* .*)</span>(.*, .*)', incidenti_2018) # popravimo neustrezne datume
dat1, dat2 = datum_2[0]
datum_skupaj = str(dat1)+str(dat2)
tab_datuma = datum_skupaj.split(', ')
datumi_2018.insert(11, tab_datuma[0])
se_en_datum = re.findall(r'<td>(.* .*), 2018\n', incidenti_2018, re.MULTILINE)
dat_apr = se_en_datum[-1]
datumi_2018.insert(14, dat_apr)
mesta_2018_1 = re.findall(r'<td><a href="/wiki/.*?" title=".*?">(.*?)</a>', incidenti_2018, re.MULTILINE)
mesta_2018 = mesta_2018_1[::2]
st_mrtvih_ranjenih_2018 = re.findall(r'<td>(\d*).*\n</td>', incidenti_2018, re.MULTILINE)
st_mrtvih_ranjenih_2018 = [x for x in st_mrtvih_ranjenih_2018 if x != '']
mrtvi_2018 = st_mrtvih_ranjenih_2018[0::2]
poskodovani_2018 = st_mrtvih_ranjenih_2018[1::2]

leto_2018 = {'Zvezne države' : zvezne_drzave_v2(mesta_2018)[::-1],
             'Incidenti' : datumi_2018[::-1],
             'Ranjeni' : poskodovani_2018[::-1],
             'Mrtvi' : mrtvi_2018[::-1]}

mrtvi_2018 = str_to_int(mrtvi_2018)
sest_mrtvi_2018 = sum(mrtvi_2018)
poskodovani_2018 = str_to_int(poskodovani_2018)
sest_poskodovani_2018 = sum(poskodovani_2018)


# 2017 ##################################################
    # Zbiranje podatkov za leto 2017

incidenti_2017 = tab_incidenti_2023_1900[7]
datumi_2017 = re.findall(r'<td><span data-sort-value=".*" style="white-space:nowrap">(.* .*), 2017</span>', incidenti_2017)
datum_2 = re.findall(r'<td><span data-sort-value=".*" style="white-space:nowrap">(.* .*)</span>(.*, .*)', incidenti_2017)
mesta_2017_1 = re.findall(r'<td><a href="/wiki/.*?" title=".*?">(.*?)</a>', incidenti_2017, re.MULTILINE)
mesta_2017 = mesta_2017_1[::2]
st_mrtvih_ranjenih_2017 = re.findall(r'<td>(\d*).*\n</td>', incidenti_2017, re.MULTILINE)
st_mrtvih_ranjenih_2017 = [x for x in st_mrtvih_ranjenih_2017 if x != '']
mrtvi_2017 = st_mrtvih_ranjenih_2017[0::2]
poskodovani_2017 = st_mrtvih_ranjenih_2017[1::2]

leto_2017 = {'Zvezne države' : zvezne_drzave_v2(mesta_2017)[::-1],
             'Incidenti' : datumi_2017[::-1],
             'Ranjeni' : poskodovani_2017[::-1],
             'Mrtvi' : mrtvi_2017[::-1]}

mrtvi_2017 = str_to_int(mrtvi_2017)
sest_mrtvi_2017 = sum(mrtvi_2017)
poskodovani_2017 = str_to_int(poskodovani_2017)
sest_poskodovani_2017 = sum(poskodovani_2017)


# 2016 ##################################################
    # Zbiranje podatkov za leto 2016
    
incidenti_2016 = tab_incidenti_2023_1900[8]
datumi_2016 = re.findall(r'<td><span data-sort-value=".*" style="white-space:nowrap">(.* .*), 2016</span>', incidenti_2016)
march7_8 = re.findall(r'<td>(.* .*), 2016\n', incidenti_2016, re.MULTILINE) # popravimo neustrezne datume
datumi_2016.insert(9, march7_8[0])
mesta_2016_1 = re.findall(r'<td><a href="/wiki/.*?" title=".*?">(.*?)</a>', incidenti_2016, re.MULTILINE)
mesta_2016 = mesta_2016_1[::2]
st_mrtvih_ranjenih_2016 = re.findall(r'<td>(\d*).*\n</td>', incidenti_2016, re.MULTILINE)
st_mrtvih_ranjenih_2016 = [x for x in st_mrtvih_ranjenih_2016 if x != '']
mrtvi_2016 = st_mrtvih_ranjenih_2016[0::2]
poskodovani_2016 = st_mrtvih_ranjenih_2016[1::2]

zv_drzave_2016 = zvezne_drzave(mesta_2016)
zv_drzave_2016[10] = 'Kansas' # popravimo neustrezno drzavo

leto_2016 = {'Zvezne države' : zv_drzave_2016[::-1],
             'Incidenti' : datumi_2016[::-1],
             'Ranjeni' : poskodovani_2016[::-1],
             'Mrtvi' : mrtvi_2016[::-1]}

mrtvi_2016 = str_to_int(mrtvi_2016)
sest_mrtvi_2016 = sum(mrtvi_2016)
poskodovani_2016 = str_to_int(poskodovani_2016)
sest_poskodovani_2016 = sum(poskodovani_2016)


# 2015 ##################################################
    #Zbiranje podatkov za leto 2015

incidenti_2015 = tab_incidenti_2023_1900[9]
datumi_2015 = re.findall(r'<td><span data-sort-value=".*" style="white-space:nowrap">(.* .*), 2015</span>', incidenti_2015)
november23 = re.findall(r'<td>(.* .*), 2015\n', incidenti_2015, re.MULTILINE) # popravimo neustrezen datum
datumi_2015.insert(2, november23[0])
mesta_2015_1 = re.findall(r'<td><a href="/wiki/.*?" title=".*?">(.*?)</a>', incidenti_2015, re.MULTILINE)
mesta_2015 = mesta_2015_1[::2]
st_mrtvih_ranjenih_2015 = re.findall(r'<td>(\d*).*\n</td>', incidenti_2015, re.MULTILINE)
st_mrtvih_ranjenih_2015 = [x for x in st_mrtvih_ranjenih_2015 if x != '']
mrtvi_2015 = st_mrtvih_ranjenih_2015[0::2]
poskodovani_2015 = st_mrtvih_ranjenih_2015[1::2]

leto_2015 = {'Zvezne države' : zvezne_drzave_v2(mesta_2015)[::-1],
             'Incidenti' : datumi_2015[::-1],
             'Ranjeni' : poskodovani_2015[::-1],
             'Mrtvi' : mrtvi_2015[::-1]}

mrtvi_2015 = str_to_int(mrtvi_2015)
sest_mrtvi_2015 = sum(mrtvi_2015)
poskodovani_2015 = str_to_int(poskodovani_2015)
sest_poskodovani_2015 = sum(poskodovani_2015)


# 2014 ##################################################
    # Zbiranje podatkov za leto 2014
    
incidenti_2014 = tab_incidenti_2023_1900[10]
datumi_2014 = re.findall(r'<td><span data-sort-value=".*" style="white-space:nowrap">(.* .*), 2014</span>', incidenti_2014)
mesta_2014_1 = re.findall(r'<td><a href="/wiki/.*?" title=".*?">(.*?)</a>', incidenti_2014, re.MULTILINE)
mesta_2014 = mesta_2014_1[::2]
st_mrtvih_ranjenih_2014 = re.findall(r'<td>(\d*).*\n</td>', incidenti_2014, re.MULTILINE)
st_mrtvih_ranjenih_2014 = [x for x in st_mrtvih_ranjenih_2014 if x != '']
mrtvi_2014 = st_mrtvih_ranjenih_2014[0::2]
poskodovani_2014 = st_mrtvih_ranjenih_2014[1::2]

leto_2014 = {'Zvezne države' : zvezne_drzave(mesta_2014)[::-1],
             'Incidenti' : datumi_2014[::-1],
             'Ranjeni' : poskodovani_2014[::-1],
             'Mrtvi' : mrtvi_2014[::-1]}

mrtvi_2014 = str_to_int(mrtvi_2014)
sest_mrtvi_2014 = sum(mrtvi_2014)
poskodovani_2014 = str_to_int(poskodovani_2014)
sest_poskodovani_2014 = sum(poskodovani_2014)


# 2013 ##################################################
    # Zbiranje podatkov za leto 2013
    
incidenti_2013 = tab_incidenti_2023_1900[11]
datumi_2013 = re.findall(r'<td><span data-sort-value=".*" style="white-space:nowrap">(.* .*), 2013</span>', incidenti_2013)
march13 = re.findall(r'<td>(.* .*), 2013\n', incidenti_2013, re.MULTILINE) # popravimo neustrezen datum
datumi_2013.insert(4, 'march13')
mesta_2013_1 = re.findall(r'<td><a href="/wiki/.*?" title=".*?">(.*?)</a>', incidenti_2013, re.MULTILINE)
mesta_2013 = mesta_2013_1[::2]
st_mrtvih_ranjenih_2013 = re.findall(r'<td>(\d*).*\n</td>', incidenti_2013, re.MULTILINE)
st_mrtvih_ranjenih_2013 = [x for x in st_mrtvih_ranjenih_2013 if x != '']
mrtvi_2013 = st_mrtvih_ranjenih_2013[0::2]
poskodovani_2013 = st_mrtvih_ranjenih_2013[1::2]

zv_drzave_2013 = zvezne_drzave(mesta_2013)
zv_drzave_2013[1] = 'Washington' # popravimo neustrezni zvezni državi
zv_drzave_2013[4] = 'New York'

leto_2013 = {'Zvezne države' : zv_drzave_2013[::-1],
             'Incidenti' : datumi_2013[::-1],
             'Ranjeni' : poskodovani_2013[::-1],
             'Mrtvi' : mrtvi_2013[::-1]}

mrtvi_2013 = str_to_int(mrtvi_2013)
sest_mrtvi_2013 = sum(mrtvi_2013)
poskodovani_2013 = str_to_int(poskodovani_2013)
sest_poskodovani_2013 = sum(poskodovani_2013)


# 2012 ##################################################
    # Zbiranje podatkov za leto 2012
    
incidenti_2012 = tab_incidenti_2023_1900[12]
datumi_2012 = re.findall(r'<td>(.* .*), 2012', incidenti_2012)
mesta_2012_1 = re.findall(r'<td><a href="/wiki/.*?" title=".*?">(.*?)</a>', incidenti_2012, re.MULTILINE)
mesta_2012 = mesta_2012_1[::2]
st_mrtvih_ranjenih_2012 = re.findall(r'<td>(\d*).*\n</td>', incidenti_2012, re.MULTILINE)
st_mrtvih_ranjenih_2012 = [x for x in st_mrtvih_ranjenih_2012 if x != '']
mrtvi_2012 = st_mrtvih_ranjenih_2012[0::2]
poskodovani_2012 = st_mrtvih_ranjenih_2012[1::2]

leto_2012 = {'Zvezne države' : zvezne_drzave(mesta_2012)[::-1],
             'Incidenti' : datumi_2012[::-1],
             'Ranjeni' : poskodovani_2012[::-1],
             'Mrtvi' : mrtvi_2012[::-1]}

mrtvi_2012 = str_to_int(mrtvi_2012)
sest_mrtvi_2012 = sum(mrtvi_2012)
poskodovani_2012 = str_to_int(poskodovani_2012)
sest_poskodovani_2012 = sum(poskodovani_2012)


# 2011 ##################################################
    # Zbiranje podatkov za leto 2011

incidenti_2011 = tab_incidenti_2023_1900[13]
datumi_2011 = re.findall(r'<td>(.* .*), 2011', incidenti_2011)
mesta_2011_1 = re.findall(r'<td><a href="/wiki/.*?" title=".*?">(.*?)</a>', incidenti_2011, re.MULTILINE)
mesta_2011 = mesta_2011_1[::2]
st_mrtvih_ranjenih_2011 = re.findall(r'<td>(\d*).*\n</td>', incidenti_2011, re.MULTILINE)
st_mrtvih_ranjenih_2011 = [x for x in st_mrtvih_ranjenih_2011 if x != '']
mrtvi_2011 = st_mrtvih_ranjenih_2011[0::2]
poskodovani_2011 = st_mrtvih_ranjenih_2011[1::2]

leto_2011 = {'Zvezne države' : zvezne_drzave(mesta_2011)[::-1],
             'Incidenti' : datumi_2011[::-1],
             'Ranjeni' : poskodovani_2011[::-1],
             'Mrtvi' : mrtvi_2011[::-1]}

mrtvi_2011 = str_to_int(mrtvi_2011)
sest_mrtvi_2011 = sum(mrtvi_2011)
poskodovani_2011 = str_to_int(poskodovani_2011)
sest_poskodovani_2011 = sum(poskodovani_2011)


# 2010 ##################################################
    # Zbiranje podatkov za leto 2010
    
incidenti_2010 = tab_incidenti_2023_1900[14]
datumi_2010 = re.findall(r'<td>(.* .*), 2010', incidenti_2010)
mesta_2010_1 = re.findall(r'<td><a href="/wiki/.*?" title=".*?">(.*?)</a>', incidenti_2010, re.MULTILINE)
mesta_2010 = mesta_2010_1[::2]
st_mrtvih_ranjenih_2010 = re.findall(r'<td>(\d*).*\n</td>', incidenti_2010, re.MULTILINE)
st_mrtvih_ranjenih_2010 = [x for x in st_mrtvih_ranjenih_2010 if x != '']
mrtvi_2010 = st_mrtvih_ranjenih_2010[0::2]
poskodovani_2010 = st_mrtvih_ranjenih_2010[1::2]

leto_2010 = {'Zvezne države' : zvezne_drzave_v2(mesta_2010)[::-1],
             'Incidenti' : datumi_2010[::-1],
             'Ranjeni' : poskodovani_2010[::-1],
             'Mrtvi' : mrtvi_2010[::-1]}

mrtvi_2010 = str_to_int(mrtvi_2010)
sest_mrtvi_2010 = sum(mrtvi_2010)
poskodovani_2010 = str_to_int(poskodovani_2010)
sest_poskodovani_2010 = sum(poskodovani_2010)


# Analiza podatkov =================================================================================================================

# vse slovarje let združimo v skupen slovar
vsa_leta = {2010 : leto_2010, 2011 : leto_2011, 2012 : leto_2012, 2013 : leto_2013, 2014 : leto_2014, 2015 : leto_2015, 2016 : leto_2016, 2017 : leto_2017,
            2018 : leto_2018, 2019 : leto_2019, 2020 : leto_2020, 2021 : leto_2021, 2022 : leto_2022, 2023 : leto_2023, 2024 : leto_2024} # vse slovarje let združimo v skupen slovar


# Priprava podatkov za zemljevid Amerike

vsa_mesta = mesta_2010 + mesta_2011 + mesta_2012 + mesta_2013 + mesta_2014 + mesta_2015 + mesta_2016 + mesta_2017 + mesta_2018 + mesta_2019 + mesta_2020 + mesta_2021 + mesta_2022 + mesta_2023 + mesta_2024
vsa_mesta_kopija = vsa_mesta.copy()
samo_vsa_mesta = list()
for elt in vsa_mesta_kopija:
    element = elt.split(',') # mesta v tabeli vsa_mesta imajo poleg zabeleženega še državo, tega ne potrebujemo, zato jih odstranimo
    samo_vsa_mesta.append(element[0])
vsa_mesta_kopija = samo_vsa_mesta
vsa_mesta = set(vsa_mesta) # odstranimo vse morebitne ponovitve mest
tab_2 = list()

for elt in vsa_mesta: # iz množice nazaj formiramo tabelo mest
    element = elt.split(',')
    tab_2.append(element[0])

x_os = list()
y_os = list()
mesta_streljanja = list()
for mesto in tab_2: # pridobimo koordinate mest, v katerih so se zgodila streljanja
    if mesto in us_mesta:
        indeks = us_mesta.index(mesto)
        x_os.append(us_lng[indeks])
        y_os.append(us_lat[indeks])
        mesta_streljanja.append(us_mesta[indeks])

x_os = str_to_float(x_os)
y_os = str_to_float(y_os)


# Poišči mesta z največ strelskimi pohodi
    # Iz vseh shranjenih mest v Ameriki najde tista v katerih so se zgodili strelski pohodi
    # To je priprava za risanje stolpičnega diagrama vseh incidentov po državah

vsa_mesta_slovar = dict()
for mesto in vsa_mesta_kopija:
    if mesto not in vsa_mesta_slovar:
        vsa_mesta_slovar[mesto] = 1
    else:
        vsa_mesta_slovar[mesto] += 1
        
mesta_drzave = requests.get('https://www.britannica.com/topic/list-of-cities-and-towns-in-the-United-States-2023068').text
mesta_drzave2 = mesta_drzave.split('<!--[BEFORE-ARTICLE]--><span class="marker before-article"></span><section id="ref1" data-level="1"><p class="topic-paragraph"> This is a list of selected cities, towns, and other populated places in the <a href="https://www.britannica.com/place/United-States" class="md-crosslink" data-show-preview="true">United States</a>, ordered alphabetically by state. (<em>See also</em> <a href="https://www.britannica.com/topic/city" class="md-crosslink" data-show-preview="true">city</a> and <a href="https://www.britannica.com/topic/urban-planning" class="md-crosslink" data-show-preview="true">urban planning</a>.)</p><!--[P1]--><span class="marker p1"></span><!--[AM1]--><span class="marker AM1 am-inline"></span><!--[MOD1]--><span class="marker MOD1 mod-inline"></span></section>')[1]
mesta_drzave3 = mesta_drzave2.split('<span class="md-signature">This article was most recently revised and updated by <a href="/editor/Richard-Pallardy/6744">Richard Pallardy</a>.</span><!--[END-OF-CONTENT]--><span class="marker end-of-content"></span><!--[AFTER-ARTICLE]--><span class="marker after-article"></span></div>')[0]

drz = re.findall(r'<a href="https://www.britannica.com/place/.*" class="md-crosslink" data-show-preview="true">(.*)</a></h2', mesta_drzave3)

po_drzavah = mesta_drzave3.split(']--><span class="marker h')
tab_mest = list()
for drzava in po_drzavah: # zanka vsaki državi priredi tabelo mest
    mesta = re.findall(r'<a href="https://www.britannica.com/place/.*?" class="md-crosslink" data-show-preview="true">(.*?)</a>', drzava, re.MULTILINE)
    if len(mesta) != 0:
        mesta.pop(0)
    tab_mest.append(mesta)

tab_mest.append(mesta)
tab_mest.pop(51)
tab_mest.pop(0)

mesta_v_drzavah = dict()
for i in range(len(drz)): # vsaki državi priredi seznam mest v katero spadajo
    mesta_v_drzavah[drz[i]] = tab_mest[i]
    
slovar_incidentov_po_drzavah = dict()
for key1 in mesta_v_drzavah.keys():
    slovar_incidentov_po_drzavah[key1] = 0

for key1, value1 in mesta_v_drzavah.items(): # vse incidente v vseh mestih zabeležimo za primerne države
    for key2, value2 in vsa_mesta_slovar.items():
        if key2 in value1:
            slovar_incidentov_po_drzavah[key1] += value2

slovar_incidentov_po_drzavah2 = slovar_incidentov_po_drzavah.copy() # države brez incidentov nas ne zanimajo, zato jih odstranimo iz slovarja
for key1, value1 in slovar_incidentov_po_drzavah.items():
    if slovar_incidentov_po_drzavah[key1] == 0:
        slovar_incidentov_po_drzavah2.pop(key1)
 
 
# tabela vseh zveznih držav
vse_zvezne_drzave_us = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois',
                        'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana',
                        'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania',
                        'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming']

# Izpis ============================================================================================================================

print(' ')
print('Pozdravljeni!\n' +
      'V projektni nalogi sva analizirala strelske pohode v Združenih državah Amerike v obdobju od leta 2010 do leta 2024. Pripravila sva nekaj analiz in grafov.\n' +
      'Za ogled analiz izberite ustrezno številko in nato vpišite leto ali obdobje, ki vas zanima, za ogled grafa pa si pri določenih številkah preberite opis in izberite, katerega si želite ogledati.\n' +
      '1: Število streljanj v izbranem letu.\n' +
      '2: Število ranjenih v izbranem letu.\n' +
      '3: Štvilo smrtnih žrtev v izbranem letu.\n' +
      '4: Število streljanj v izbrani državi v izbranem obdobju.\n' +
      '5: Število ranjenih v izbrani državi v izbranem obdobju.\n' +
      '6: Število smrtnih žrtev v izbrani državi v izbranem obdobju.\n' +
      '7: Grafični prikaz števila ranjenih in števila smrtnih žrtev po datumu.\n' +
      '8: Grafični prikaz števila množičnih streljanj po državah.\n' +
      '9: Izris mest, v katerih so se strelski pohodi zgodili, na zemljevid ameriških mest.\n' +
      '10: Konec pregleda analiz in grafov.\n')
print('Dodatno navodilo: Če izberete število 4, 5 ali 6, morate vpisati ime izbrane zvezne države v angleščini!\n' +
      'Zvezne države: Alabama, Alaska, Arizona, Arkansas, California, Colorado, Connecticut, Delaware, Florida, Georgia, Hawaii, Idaho, Illinois, Indiana, Iowa, Kansas, Kentucky, Louisiana, Maine, Maryland, Massachusetts, Michigan, Minnesota, Mississippi, Missouri, Montana, Nebraska, Nevada, New Hampshire, New Jersey, New Mexico, New York, North Carolina, North Dakota, Ohio, Oklahoma, Oregon, Pennsylvania, Rhode Island, South Carolina, South Dakota, Tennessee, Texas, Utah, Vermont, Virginia, Washington, West Virginia, Wisconsin, Wyoming'
      )
print(' ')

stevilo = int(input('Katero število ste izbrali? '))
while stevilo != 10:
    if 1 <= stevilo <= 3:
        leto = int(input('Katero leto želite analizirati? '))
        if leto not in [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]:
            print('Podatki obstajajo le za leta 2010-2024.')
        elif stevilo == 1:
            print(streljanja_v_letu(leto))
        elif stevilo == 2:
            print(ranjeni_v_letu(leto))
        elif stevilo == 3:
            print(mrtvi_v_letu(leto))
    elif 4 <= stevilo <= 6:
        k = True # ulovimo napake pri vnosu
        while k == True:
            drzava = input('Katera država vas zanima? ')
            if drzava not in vse_zvezne_drzave_us:
                print('Država ni ustrezna!')
            elif drzava in ('Delaware', 'Hawaii', 'Idaho', 'Massachusetts', 'Montana', 'Nebraska', 'New Hampshire', 'Rhode Island', 'South Dakota', 'Vermont', 'Wyoming'):
                print('V tej zvezni državi ni bilo streljanj oziroma ni podatka.')
            else:    
                l = True # ulovimo napake pri vnosu
                while l == True:
                    i = True # ulovimo napako, če uporabnik vpiše neustrezno začetno leto
                    while i == True:
                        zacetek = int(input('Od katerega leta dalje želite analizirati podatke? '))
                        if zacetek not in [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]:
                            print('Neustrezno leto!')
                        else:
                            i = False
                    j = True # ulovimo napako, če uporabnik vpiše neustrezno končno leto
                    while j == True:
                        konec = int(input('Do katerega leta želite analizirati podatke? '))
                        if konec not in [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]:
                            print('Neustrezno leto!')
                        else:
                            j = False
                    drzave = zdruzi_podatke(zacetek, konec, vsa_leta)
                    urejene_drzave = dict(sorted(drzave.items(), key=lambda x: x[0]))  # slovar vseh držav oblike drzave = {drzava : [streljanja, ranjeni, mrtvi]}, podatki za vsa leta
                    if konec < zacetek:
                        print('Napačno izbran interval.')
                    elif drzava not in urejene_drzave.keys():
                        print('V tem obdobju v tej državi ni bilo nobenih incidentov.')
                        l = False
                    elif stevilo == 4:
                        print(urejene_drzave[drzava][0])
                        l = False
                    elif stevilo == 5:
                        print(urejene_drzave[drzava][1])
                        l = False
                    elif stevilo == 6:
                        print(urejene_drzave[drzava][2])
                        l = False
                k = False
    elif stevilo == 7:
        t = True
        while t == True:
            vprasanje = input('Katero leto vas zanima? Na voljo so leta od 2010 do 2024, če pa želite vsa leta, napišite "vsa". Če hočete končati pregled, vpišite ukaz "continue": ')
            if vprasanje == '2010':
                print(f'Št incidentov: {len(poskodovani_2010)}, ranjeni: {sest_poskodovani_2010}, mrtvi: {sest_mrtvi_2010}')
                plt.plot(datumi_2010, mrtvi_2010, c = 'r') # izrišemo graf za izbrano leto
                plt.plot(datumi_2010, poskodovani_2010, c = 'g')
                plt.title("Incidenti leta 2010")
                plt.xlabel('Datumi incidentov v izbranem letu')
                plt.xticks(rotation=45, fontsize = 7)
                plt.legend(["Mrtvi", "Ranjeni"], loc="upper right")
                plt.show()
            elif vprasanje == '2011':
                print(f'Št incidentov: {len(poskodovani_2011)}, ranjeni: {sest_poskodovani_2011}, mrtvi: {sest_mrtvi_2011}')
                plt.plot(datumi_2011, mrtvi_2011, c = 'r')
                plt.plot(datumi_2011, poskodovani_2011, c = 'g')
                plt.title("Incidenti leta 2011")
                plt.xlabel('Datumi incidentov v izbranem letu')
                plt.xticks(rotation=45, fontsize = 7)
                plt.legend(["Mrtvi", "Ranjeni"], loc="upper right")
                plt.show()
            elif vprasanje == '2012':
                print(f'Št incidentov: {len(poskodovani_2012)}, ranjeni: {sest_poskodovani_2012}, mrtvi: {sest_mrtvi_2012}')
                plt.plot(datumi_2012, mrtvi_2012, c = 'r')
                plt.plot(datumi_2012, poskodovani_2012, c = 'g')
                plt.title("Incidenti leta 2012")
                plt.xlabel('Datumi incidentov v izbranem letu')
                plt.xticks(rotation=45, fontsize = 7)
                plt.legend(["Mrtvi", "Ranjeni"], loc="upper right")
                plt.show()
            elif vprasanje == '2013':
                print(f'Št incidentov: {len(poskodovani_2013)}, ranjeni: {sest_poskodovani_2013}, mrtvi: {sest_mrtvi_2013}')
                plt.plot(datumi_2013, mrtvi_2013, c = 'r')
                plt.plot(datumi_2013, poskodovani_2013, c = 'g')
                plt.title("Incidenti leta 2013")
                plt.xlabel('Datumi incidentov v izbranem letu')
                plt.xticks(rotation=45, fontsize = 7)
                plt.legend(["Mrtvi", "Ranjeni"], loc="upper right")
                plt.show()
            elif vprasanje == '2014':
                print(f'Št incidentov: {len(poskodovani_2014)}, ranjeni: {sest_poskodovani_2014}, mrtvi: {sest_mrtvi_2014}')
                plt.plot(datumi_2014, mrtvi_2014, c = 'r')
                plt.plot(datumi_2014, poskodovani_2014, c = 'g')
                plt.title("Incidenti leta 2014")
                plt.xlabel('Datumi incidentov v izbranem letu')
                plt.xticks(rotation=45, fontsize = 7)
                plt.legend(["Mrtvi", "Ranjeni"], loc="upper right")
                plt.show()
            elif vprasanje == '2015':
                print(f'Št incidentov: {len(poskodovani_2015)}, ranjeni: {sest_poskodovani_2015}, mrtvi: {sest_mrtvi_2015}')
                plt.plot(datumi_2015, mrtvi_2015, c = 'r')
                plt.plot(datumi_2015, poskodovani_2015, c = 'g')
                plt.title("Incidenti leta 2015")
                plt.xlabel('Datumi incidentov v izbranem letu')
                plt.xticks(rotation=45, fontsize = 7)
                plt.legend(["Mrtvi", "Ranjeni"], loc="upper right")
                plt.show()
            elif vprasanje == '2016':
                print(f'Št incidentov: {len(poskodovani_2016)}, ranjeni: {sest_poskodovani_2016}, mrtvi: {sest_mrtvi_2016}')
                plt.plot(datumi_2016, mrtvi_2016, c = 'r')
                plt.plot(datumi_2016, poskodovani_2016, c = 'g')
                plt.title("Incidenti leta 2016")
                plt.xlabel('Datumi incidentov v izbranem letu')
                plt.xticks(rotation=45, fontsize = 7)
                plt.legend(["Mrtvi", "Ranjeni"], loc="upper right")
                plt.show()
            elif vprasanje == '2017':
                print(f'Št incidentov: {len(poskodovani_2017)}, ranjeni: {sest_poskodovani_2017}, mrtvi: {sest_mrtvi_2017}')
                plt.plot(datumi_2017, mrtvi_2017, c = 'r')
                plt.plot(datumi_2017, poskodovani_2017, c = 'g')
                plt.title("Incidenti leta 2017")
                plt.xlabel('Datumi incidentov v izbranem letu')
                plt.xticks(rotation=45, fontsize = 7)
                plt.legend(["Mrtvi", "Ranjeni"], loc="upper right")
                plt.show()
            elif vprasanje == '2018':
                print(f'Št incidentov: {len(poskodovani_2018)}, ranjeni: {sest_poskodovani_2018}, mrtvi: {sest_mrtvi_2018}')
                plt.plot(datumi_2018, mrtvi_2018, c = 'r')
                plt.plot(datumi_2018, poskodovani_2018, c = 'g')
                plt.title("Incidenti leta 2018")
                plt.xlabel('Datumi incidentov v izbranem letu')
                plt.xticks(rotation=45, fontsize = 7)
                plt.legend(["Mrtvi", "Ranjeni"], loc="upper right")
                plt.show()
            elif vprasanje == '2019':
                print(f'Št incidentov: {len(poskodovani_2019)}, ranjeni: {sest_poskodovani_2019}, mrtvi: {sest_mrtvi_2019}')
                plt.plot(datumi_2019, mrtvi_2019, c = 'r')
                plt.plot(datumi_2019, poskodovani_2019, c = 'g')
                plt.title("Incidenti leta 2019")
                plt.xlabel('Datumi incidentov v izbranem letu')
                plt.xticks(rotation=45, fontsize = 7)
                plt.legend(["Mrtvi", "Ranjeni"], loc="upper right")
                plt.show()
            elif vprasanje == '2020':
                print(f'Št incidentov: {len(poskodovani_2020)}, ranjeni: {sest_poskodovani_2020}, mrtvi: {sest_mrtvi_2020}')
                plt.plot(datumi_2020, mrtvi_2020, c = 'r')
                plt.plot(datumi_2020, poskodovani_2020, c = 'g')
                plt.title("Incidenti leta 2020")
                plt.xlabel('Datumi incidentov v izbranem letu')
                plt.xticks(rotation=45, fontsize = 7)
                plt.legend(["Mrtvi", "Ranjeni"], loc="upper right")
                plt.show()
            elif vprasanje == '2021':
                print(f'Št incidentov: {len(poskodovani_2021)}, ranjeni: {sest_poskodovani_2021}, mrtvi: {sest_mrtvi_2021}')
                plt.plot(datumi_2021, mrtvi_2021, c = 'r')
                plt.plot(datumi_2021, poskodovani_2021, c = 'g')
                plt.title("Incidenti leta 2021")
                plt.xlabel('Datumi incidentov v izbranem letu')
                plt.xticks(rotation=45, fontsize = 7)
                plt.legend(["Mrtvi", "Ranjeni"], loc="upper right")
                plt.show()
            elif vprasanje == '2022':
                print(f'Št incidentov: {len(poskodovani_2022)}, ranjeni: {sest_poskodovani_2022}, mrtvi: {sest_mrtvi_2022}')
                plt.plot(datumi_2022, mrtvi_2022, c = 'r')
                plt.plot(datumi_2022, poskodovani_2022, c = 'g')
                plt.title("Incidenti leta 2022")
                plt.xlabel('Datumi incidentov v izbranem letu')
                plt.xticks(rotation=45, fontsize = 7)
                plt.legend(["Mrtvi", "Ranjeni"], loc="upper right")
                plt.show()
            elif vprasanje == '2023':
                print(f'Št incidentov: {len(poskodovani_2023)}, ranjeni: {sest_poskodovani_2023}, mrtvi: {sest_mrtvi_2023}')
                plt.plot(datumi_2023, mrtvi_2023, c = 'r')
                plt.plot(datumi_2023, poskodovani_2023, c = 'g')
                plt.title("Incidenti leta 2023")
                plt.xlabel('Datumi incidentov v izbranem letu')
                plt.xticks(rotation=45, fontsize = 7)
                plt.legend(["Mrtvi", "Ranjeni"], loc="upper right")
                plt.show()
            elif vprasanje == '2024':
                print(f'Št incidentov: {len(poskodovani_2024)}, ranjeni: {sest_poskodovani_2024}, mrtvi: {sest_mrtvi_2024}')
                plt.plot(datumi_2024, mrtvi_2024, c = 'r')
                plt.plot(datumi_2024, poskodovani_2024, c = 'g')
                plt.title("Incidenti leta 2024")
                plt.xlabel('Datumi incidentov v izbranem letu')
                plt.xticks(rotation=45, fontsize = 7)
                plt.legend(["Mrtvi", "Ranjeni"], loc="upper right")
                plt.show()
            elif vprasanje == 'vsa':
                mrtvi_vsa_leta = [sest_mrtvi_2010,sest_mrtvi_2011,sest_mrtvi_2012,sest_mrtvi_2013,sest_mrtvi_2014,sest_mrtvi_2015,sest_mrtvi_2016,sest_mrtvi_2017,sest_mrtvi_2018,sest_mrtvi_2019,sest_mrtvi_2020,sest_mrtvi_2021,sest_mrtvi_2022,sest_mrtvi_2023,sest_mrtvi_2024]
                ranjeni_vsa_leta = [sest_poskodovani_2010,sest_poskodovani_2011,sest_poskodovani_2012,sest_poskodovani_2013,sest_poskodovani_2014,sest_poskodovani_2015,sest_poskodovani_2016,sest_poskodovani_2017,sest_poskodovani_2018,sest_poskodovani_2019,sest_poskodovani_2020,sest_poskodovani_2021,sest_poskodovani_2022,sest_poskodovani_2023,sest_poskodovani_2024]
                x = [x + 2010 for x in range(15)]
                y = mrtvi_vsa_leta
                z = ranjeni_vsa_leta
                plt.plot(x,y, c = 'r')
                plt.plot(x,z, c = 'g')
                plt.xlabel('Leta')
                plt.ylabel('Žrtve')
                plt.title('Graf mrtvih in ranjenih skozi leta')
                plt.legend(["Mrtvi", "Ranjeni"], loc="upper right")
                plt.show()
            elif vprasanje == 'continue':
                t = False
            else:
                print('Ni podatka/Neveljaven ukaz')    
    elif stevilo == 8:
        tab_incidentov = []
        for value in urejene_drzave.values():
            tab_incidentov.append(value[0])
        plt.title("Št. Strelskih pohodov po zveznih državah slozi vsa leta") # izrišemo stolpični diagram vseh incidentov skozi leta
        plt.bar(range(len(urejene_drzave)), tab_incidentov, align='center')
        plt.xticks(range(len(urejene_drzave.keys())), list(urejene_drzave.keys()), rotation=45, fontsize = 7)
        plt.ylabel('št. incidentov')
        plt.show()
    elif stevilo == 9:
        us_lng = str_to_float(us_lng) # koodrinate US mest
        us_lat = str_to_float(us_lat)
        slika = plt.figure()
        plt.scatter(us_lng, us_lat,  c = 'k', s = 1) # izrišemo piko za vsako ameriško mesto
        plt.axis('off')
        plt.savefig('Ameriska_mesta.png')
        plt.scatter(x_os, y_os,  c = 'r', s = 1) # izrišemo rdečo piko za vsako mesto, v katerem se je zgodil strelski pohod
        plt.axis('off')
        plt.title('Lokacije strelskih pohodov po celotni Ameriki')
        plt.savefig('Streljanja.png')
        plt.show()    
    elif stevilo > 10:
        print('Neustrezno število!')
    stevilo = int(input('Katero število ste izbrali? '))
print('Hvala za sodelovanje! :)')
    