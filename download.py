import urllib.request
from bs4 import BeautifulSoup
import requests
import json
from toolkit import *

# TELECHARGER DES DATAS EXTERIEURES :
def download_news():
    req = urllib.request.Request('https://news.google.com/?edchanged=1&ned=fr&authuser=0')
    the_page = urllib.request.urlopen(req)
    page = the_page.read()
    soup = BeautifulSoup(page, 'html.parser')
    hello = []
    titre = soup.find_all("h2", attrs={"class" : "esc-lead-article-title"})
    journal = soup.find_all("span", attrs={"class" : "al-attribution-source"})
    image = soup.find_all("img", attrs={"class" : "esc-thumbnail-image"})
    print(len(image))
    if len(image) == len(titre):
        for i in range(len(titre)):
            if image[i].get('src')!=None:
                hello.append([titre[i].getText(),titre[i].a.get('href'),journal[i].getText(),'https:'+str(image[i].get('src'))])
            else : 
                hello.append([titre[i].getText(),titre[i].a.get('href'),journal[i].getText(),'https:'+str(image[i].get('imgsrc'))])
    if len(image) != len(titre):
        for i in range(len(titre)):
            hello.append([titre[i].getText(),titre[i].a.get('href'),journal[i].getText(),''])
    
    #news = 
    #cat={'sty':[],'w':[],'fr':[]}

    #photo = soup.find_all("td",attrs={"class":"esc-layout-thumbnail-cell"})
    #titre = soup.find_all("td",attrs={"class":"esc-layout-article-cell"})
    #contenu = soup.find_all("div",attrs={"class":"esc-lead-snippet-wrapper"})
    #journal = soup.find_all("span",attrs={"class":"al-attribution-source"})
    #for i in range(len(photo)):
    #    photoo = photo[i].div.div.div.a.div.img.get('imgsrc')
    #    if photoo!=None:
    #        hello.append([titre[i].div.getText(),titre[i].a.get('href'),journal[i],contenu[i].getText()[:14],'https:'+str(photoo)])
    #    else :
    #        hello.append([titre[i].div.getText(),titre[i].a.get('href'),journal[i],contenu[i].getText()[:14],'https:'+str(photo[i].div.div.div.a.div.img.get('src'))])
    une = hello[0:6]
    world = hello[6 : 10]
    france = hello[10 : 14]
    economie = hello[14 : 18]
    science = hello[18 : 22]
    culture = hello[22 : 26]
    sport = hello[26 : 30]
    sante = hello[30 : 34]
    return une,world,france,economie,science,culture,sport,sante 
def download_news2():
    req = urllib.request.Request('https://news.google.com/?edchanged=1&ned=fr&authuser=0')
    the_page = urllib.request.urlopen(req)
    page = the_page.read()
    soup = BeautifulSoup(page, 'html.parser')
    news ={}
    hello=[]
    articles = soup.find_all("div",attrs={"class":"esc-wrapper"})
    for i in range(len(articles)):
        articles[i] = BeautifulSoup(str(articles[i]),'html.parser')
        article={}
        photo = articles[i].find("img")
        if photo!=None:
            photo_url = photo.get('imgsrc')
            if photo_url!=None:
                article['image']='http:'+str(photo_url)
            else:
                article['image']='http:'+str(photo.get('src'))
        else:
            article['image']=''
        article['titre'] = str(articles[i].find("span",attrs={"class":"titletext"}).getText())
        article['lien'] = str(articles[i].find("a",attrs={"class":"article"}).get('url'))
        #contenu = articles[i].find_all("div",attrs={"class":"esc-lead-snippet-wrapper"})
        article['journal'] = str(articles[i].find("span",attrs={"class":"al-attribution-source"}).getText())
        hello.append(article)
    news['une'] = hello[0:6]
    news['world'] = hello[6:10]
    news['france'] = hello[10 : 14]
    news['economie'] = hello[14 : 18]
    news['science'] = hello[18 : 22]
    news['culture'] = hello[22 : 26]
    news['sport'] = hello[26 : 30]
    news['sante'] = hello[30 : 34]
    return news
def download_meteo(api_key_weather,latitude,longitude):
    url = 'http://api.openweathermap.org/data/2.5/weather?' \
               'lat={}&lon={}&appid={}&units={}&lang={}'.format(latitude,longitude,api_key_weather, 'metric', 'fr')
    r = requests.get(url)
    description = r.json()['weather'][0]['description'].title()
    icon = r.json()['weather'][0]['icon']
    weather = r.json()['main']
    return weather, description,icon
def download_classement_ligue1():
    clubs_abreviation = ['Olympique Lyonnais','Olympique de Marseille','Girondins de Bordeaux','Paris Saint-Germain','Montpellier Hérault SC','AS Nancy Lorraine','Stade Rennais FC','AS Saint-Etienne']
    abreviation = ['OL','OM','Girondins','PSG','Montpellier','AS Nancy','Stade Rennais','Saint-Etienne']
    req = urllib.request.Request('http://www.lfp.fr/ligue1/classement')
    the_page = urllib.request.urlopen(req)
    page = the_page.read()
    soup = BeautifulSoup(page, 'html.parser')
    hello = []
    club = soup.find_all("td", attrs={"class" : "club"})
    points = soup.find_all("td", attrs={"class" : "points"})
    diff = soup.find_all("td", attrs={"class" : "diff"})
    for i in range(len(club)):
        nom_club = club[i].getText()[23:-37]
        nb_points = points[i].getText()
        nb_diff = diff[i].getText()
        if nom_club in clubs_abreviation : 
            hello.append([abreviation[recherche_similitude([nom_club],clubs_abreviation)],nb_points,nb_diff])
        else :
            hello.append([nom_club,nb_points,nb_diff])
    return hello
def download_resultats_ligue1():
    clubs_abreviation = ['Olympique Lyonnais','Olympique de Marseille','Girondins de Bordeaux','Paris Saint-Germain','Montpellier Hérault SC','AS Nancy Lorraine','Stade Rennais FC','AS Saint-Etienne']
    abreviation = ['OL','OM','Girondins','PSG','Montpellier','AS Nancy','Stade Rennais','Saint-Etienne']
    req = urllib.request.Request('http://www.lfp.fr/ligue1')
    the_page = urllib.request.urlopen(req)
    page = the_page.read()
    soup = BeautifulSoup(page, 'html.parser')
    hello = []
    domicile = soup.find_all("td", attrs={"class" : "domicile"})
    exterieur = soup.find_all("td", attrs={"class" : "exterieur"})
    stats = soup.find_all("td", attrs={"class" : "stats"})
    for i in range(len(domicile)):
        nom_domicile = domicile[i].getText()[24:-21]
        nom_exterieur = exterieur[i].getText()[24:-21]
        if nom_domicile in clubs_abreviation:
            nom_domicile = abreviation[recherche_similitude([nom_domicile],clubs_abreviation)]
        if nom_exterieur in clubs_abreviation:
            nom_exterieur = abreviation[recherche_similitude([nom_exterieur],clubs_abreviation)]
        nb_result = stats[i].getText()[1:]
        hello.append([nom_domicile,nom_exterieur,nb_result])
    return hello
def download_classement_liga():
    clubs_abreviation =[]
    abreviation = []
    req = urllib.request.Request('http://www.eurosport.fr/football/liga/standing.shtml')
    the_page = urllib.request.urlopen(req)
    page = the_page.read()
    soup = BeautifulSoup(page, 'html.parser')
    hello = []
    club = soup.find_all("a", attrs={"class" : "standing-table__team-link"})
    points = soup.find_all("span", attrs={"class" : "standing-table__cell-value"})
    #diff = soup.find_all("td", attrs={"class" : "diff"})
    for i in range(len(club)):
        nom_club = club[i].getText()
        nb_points = points[i].getText()
        #nb_diff = diff[i].getText()
        if nom_club in clubs_abreviation : 
            hello.append([abreviation[recherche_similitude([nom_club],clubs_abreviation)],nb_points])
        else :
            hello.append([nom_club,nb_points])
    return hello
def download_resultats_liga():
    clubs_abreviation = []
    abreviation = []
    req = urllib.request.Request('http://www.lequipe.fr/Football/championnat-d-espagne-resultats.html')
    the_page = urllib.request.urlopen(req)
    page = the_page.read()
    soup = BeautifulSoup(page, 'html.parser')
    hello = []
    domicile = soup.find_all("div", attrs={"class" : "equipeDom"})
    exterieur = soup.find_all("div", attrs={"class" : "equipeExt"})
    stats = soup.find_all("div", attrs={"class" : "score"})
    for i in range(len(domicile)):
        nom_domicile = str(domicile[i].getText())[:-4]
        nom_exterieur = str(exterieur[i].getText())[:-4]
        if nom_domicile[:-3] in clubs_abreviation:
            nom_domicile = abreviation[recherche_similitude([nom_domicile],clubs_abreviation)]
        if nom_exterieur[:-3] in clubs_abreviation:
            nom_exterieur = abreviation[recherche_similitude([nom_exterieur],clubs_abreviation)]
        nb_result = stats[i].getText()
        hello.append([nom_domicile,nom_exterieur,nb_result])
    return hello
def download_info_user(user_id,token):
    #r = requests.get('https://graph.facebook.com/v2.6/'+user_id+'?fields=first_name,last_name,profile_pic,locale,timezone,gender&access_token=' + token)
    r = requests.get('https://graph.facebook.com/v2.6/'+user_id+'?fields=last_name,profile_pic,locale,timezone,gender&access_token=' + token)
    data = json.loads(r.text)
    print(data)
    first_name = data["first_name"]
    last_name = data["last_name"]
    timezone = data['timezone']
    locale = data['locale']
    gender = data['gender']
    return first_name,last_name,gender,locale,timezone 