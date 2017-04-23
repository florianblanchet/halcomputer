# coding: utf-8
import os
import requests
import traceback
import json
from flask import Flask, request
from datetime import datetime 
import urllib.request
from bs4 import BeautifulSoup #version à ajouter dans requirement.txt
from flask_sqlalchemy import SQLAlchemy
from send import *
from download import *
from toolkit import *

token = os.environ.get('FB_ACCESS_TOKEN')
FB_VERIFY_TOKEN = os.environ.get('FB_VERIFY_TOKEN')
api_key_weather = os.environ.get('WEATHER_API_KEY')

me = os.environ.get('MY_ID') #ID de l'app

app = Flask(__name__)  #instance de la classe FLask. premier argument est le nom
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
db = SQLAlchemy()
db.app=app
db.init_app(app)
start_time = time.time()

class BaseModel1(db.Model):
    """Base data model for all objects"""
    __abstract__ = True

    def __init__(self, *args):
        super().__init__(*args)

    def __repr__(self):
        """Define a base way to print models"""
        return '%s(%s)' % (self.__class__.__name__, {
            column: value
            for column, value in self._to_dict().items()
        })

    def json(self):
        """
                Define a base way to jsonify models, dealing with datetime objects
        """
        return {
            column: value if not isinstance(value, datetime.date) else value.strftime('%Y-%m-%d')
            for column, value in self._to_dict().items()
        }
class BaseModel2(db.Model):
    """Base data model for all objects"""
    __abstract__ = True

    def __init__(self, *args):
        super().__init__(*args)

    def __repr__(self):
        """Define a base way to print models"""
        return '%s(%s)' % (self.__class__.__name__, {
            column: value
            for column, value in self._to_dict().items()})

    def json(self):
        """
                Define a base way to jsonify models, dealing with datetime objects
        """
        return {
            column: value if not isinstance(value, datetime.date) else value.strftime('%Y-%m-%d')
            for column, value in self._to_dict().items()}
class User(BaseModel1,db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Numeric, unique=True)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    gender = db.Column(db.String(20))
    locale = db.Column(db.String(20))
    timezone = db.Column(db.Integer)

    def __init__(self, user_id,first_name,last_name,gender,locale,timezone):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.gender=gender
        self.locale=locale
        self.timezone=timezone
       

    def __repr__(self):
        return '<User %r>' %self.user_id
class News(BaseModel2,db.Model):
    __tablename__ = "news"
    id = db.Column(db.Integer, primary_key=True)
    categorie = db.Column(db.String(10))
    titre = db.Column(db.String(300))
    journal = db.Column(db.String(100))
    lien = db.Column(db.String(200))
    image = db.Column(db.String(200))

    def __init__(self, user_id,first_name,last_name,gender,locale,timezone):
        self.categorie = categorie
        self.titre = titre
        self.journal = journal
        self.lien = lien
        self.image = image
       
    def __repr__(self):
        return '<News %r>' %self.titre  

@app.route('/', methods=['GET', 'POST']) #A decorator that is used to register a view function for a given URL rule. Ici rule = / et en option les methodes assignées à ce rule
def webhook():
    global start_time
    if request.method == 'POST':  # Toutes les requetes post passent par la ; dans les deux sens
        try:
            data = json.loads(request.data.decode())  #recupere le message envoye a notre chatbot
            sender = data['entry'][0]['messaging'][0]['sender']['id']   # Qui nous l a envoye
            depaquet = depaquetage(sender,data,me,ponct_liste)
            print(depaquet)
            type_msg_recu = depaquet[0]

            # Controle si l'user est dans la base de donnée
            # Dans l'avenir faire ça au moment du get started -> gagne du temps de traitement
            if db.session.query(User).filter(User.user_id==int(sender)).count()!=1 and (sender!=me):
                print(sender)
                first_name,last_name,gender,locale,timezone = download_info_user(sender,token)
                reg = User(int(sender),first_name,last_name,gender,locale,timezone)
                db.session.add(reg)
                db.session.commit()

            if type_msg_recu == 'text_msg' :
                type_msg_recu, texte, mots_du_msg=depaquet

                if similitudes(bonjour_liste,mots_du_msg)!=[]:
                    username = str(User.query.filter_by(user_id = sender).first().first_name)
                    texte = "Salut "+username+"!\n"+nouveaute+"Choisis :"
                    payload = send_choix_multiple4(sender,texte,'Actualité',actu_img,'Météo',meteo_img,'Fais croquer',pomme_img,'Wiki obama',wiki_img)
                    send_paquet(token,payload)
                    print('Reponse au bonjour envoyee')
                    return 'nothing'

                elif similitudes(news_liste,mots_du_msg)!=[]:
                    if (time.time() - start_time)>600:
                        r = requests.get('https://pure-tundra-75365.herokuapp.com/')
                        #print(r.text)
                        print("news actualisée")
                        start_time = time.time()
                    if len(mots_du_msg)>1: #Probleme si que le mot 'actualité' dans une phrase ou si 'monde' pas direct aprés
                        mot_suivant = mots_du_msg[recherche_similitude(news_liste,mots_du_msg)+1]
                        payload = send_news2(sender,mot_suivant)
                        send_paquet(token,payload)
                        if mot_suivant !='sport':
                            texte = "Si tu as encore faim voici la carte :"
                            payload = send_choix_multiple4(sender,texte,'Actualité',actu_img,'Météo',meteo_img,'Fais croquer',pomme_img,'Wiki obama',wiki_img)
                            send_paquet(token,payload)
                        print('News envoyées')
                        return 'nothing'
                    else:  #Cas ou on met juste message 'actualité'
                        texte = "Choisis ta catégorie :"
                        payload = send_choix_multiple7(sender,texte,'Actu Une','Actu Monde','Actu France','Actu Sport','Actu Business','Actu Culture','Actu Santé')
                        send_paquet(token,payload)
                        print('News envoyées')
                        return 'nothing'

                elif similitudes(meteo_liste,mots_du_msg)!=[]:
                    if len(mots_du_msg)>1:
                        if mots_du_msg[1] in ['paris']:
                            payload = send_meteo(sender,api_key_weather,'48.8534100','2.3488000')
                            send_paquet(token,payload)
                            texte = "Il fait beau n'est ce pas ? :"
                            payload = send_choix_multiple4(sender,texte,'Actualité',actu_img,'Météo',meteo_img,'Fais croquer',pomme_img,'Wiki obama',wiki_img)
                            send_paquet(token,payload)
                            print('Demande de meteo envoyee')
                            return 'nothing'
                    else :
                        payload = location_quick_answer(sender)
                        send_paquet(token,payload)
                        print('Demande de meteo envoyee')
                        return 'nothing'

                elif similitudes(partage_liste,mots_du_msg)!=[]:
                    payload = send_share(sender)
                    send_paquet(token,payload)
                    texte = "Aprés cet effort, le réconfort :"
                    payload = send_choix_multiple4(sender,texte,'Actualité',actu_img,'Météo',meteo_img,'Fais croquer',pomme_img,'Wiki obama',wiki_img)
                    send_paquet(token,payload)
                    print('Reponse à demande de partage')
                    return 'nothing'

                elif similitudes(['fais','fait'],mots_du_msg)!=[]:
                    if len(mots_du_msg)>1:
                        mot_suivant = mots_du_msg[1]
                        if mot_suivant in ['croquer','Croquer','croqué','Croqué']:
                            payload = send_share(sender)
                            send_paquet(token,payload)
                            texte = "Aprés cet effort, le réconfort :"
                            payload = send_choix_multiple4(sender,texte,'Actualité',actu_img,'Météo',meteo_img,'Fais croquer',pomme_img,'Wiki obama',wiki_img)
                            send_paquet(token,payload)
                            print('Reponse à demande de croquage')
                            return 'nothing'
                        else :
                            texte = "Voici la carte, choisis ce qu'il te plait :"
                            payload = send_choix_multiple4(sender,texte,'Actualité',actu_img,'Météo',meteo_img,'Wiki obama',wiki_img,'Date',date_img)
                            send_paquet(token,payload)
                            print('Reponse au retour menu')
                            return 'nothing'
                    else : 
                        texte = "Voici la carte de ce que je peux faire ;) :"
                        payload = send_choix_multiple4(sender,texte,'Actualité',actu_img,'Météo',meteo_img,'Wiki obama',wiki_img,'Date',date_img)
                        send_paquet(token,payload)
                        print('Reponse au retour menu')
                        return 'nothing'
                    
                elif similitudes(menu_liste,mots_du_msg)!=[]:
                    texte = "Voici la carte, choisis ce qu'il te plait :"
                    payload = send_choix_multiple4(sender,texte,'Actualité',actu_img,'Météo',meteo_img,'Fais croquer',pomme_img,'Wiki obama',wiki_img)
                    send_paquet(token,payload)
                    print('Reponse au retour menu')
                    return 'nothing'

                elif similitudes(vulgarite_liste,mots_du_msg)!=[]:
                    texte = "T'es pas cool avec moi, viens te détendre :"
                    payload = send_choix_multiple4(sender,texte,'Actualité',actu_img,'Météo',meteo_img,'Wiki obama',wiki_img,'Date',date_img)
                    send_paquet(token,payload)
                    print('Reponse à une vulgarité')
                    return 'nothing'

                elif similitudes(merci_liste,mots_du_msg)!=[]:
                    texte = "De rien, je suis à ton service!\n"+"N'hésites pas à faire croquer ;) :"
                    payload = send_choix_multiple4(sender,texte,'Actualité',actu_img,'Météo',meteo_img,'Fais croquer',pomme_img,'Wiki obama',wiki_img)
                    send_paquet(token,payload)
                    print('Reponse au merci envoyee')
                    return 'nothing'

                elif similitudes(lien_liste,mots_du_msg)!=[]:
                    subtitle1='hello'
                    image_url1=''
                    payload = send_webview(sender,'Twitter',subtitle1,image_url1,'http://www.twitter.com','payload_twitter')
                    send_paquet(token,payload)
                    print('Liens envoyes')
                    return 'nothing'

                elif similitudes(date_liste,mots_du_msg)!=[]:
                    d = datetime.now()
                    texte = 'Nous sommes le '+str(d.day)+'/'+str(d.month)+'/'+str(d.year)
                    payload = send_choix_multiple1(sender,texte,'Retour Menu')
                    send_paquet(token,payload)
                    texte = "Le jour pour découvrir de nouvelles choses :"
                    payload = send_choix_multiple4(sender,texte,'Actualité',actu_img,'Météo',meteo_img,'Fais croquer',pomme_img,'Wiki obama',wiki_img)
                    send_paquet(token,payload)
                    print('Date envoyée')
                    return 'nothing'

                elif similitudes(wiki_liste,mots_du_msg)!=[]:
                    payload = send_wiki(sender,mots_du_msg,wiki_liste)
                    send_paquet(token,payload)
                    texte = "Intéressant non? Découvres le reste :"
                    payload = send_choix_multiple4(sender,texte,'Actualité',actu_img,'Météo',meteo_img,'Fais croquer',pomme_img,'Wiki obama',wiki_img)
                    send_paquet(token,payload)
                    print('Recherche wiki envoyées')
                    return 'nothing'

                elif 'ligue1' in mots_du_msg:
                    if len(mots_du_msg)>1 :
                        mot_suivant = mots_du_msg[1]
                        mot_suivant[recherche_similitude(classement_liste,mots_du_msg)+1]

                        if mot_suivant in classement_liste:
                            classm = download_classement_ligue1()
                            payload = send_classement_ligue1(sender,classm)
                            send_paquet(token,payload)
                            print('Demande de quoi en ligue1 envoyé')
                            return 'nothing'
                        elif mot_suivant in resultat_liste:
                            result = download_resultats_ligue1()
                            payload = send_resultats_ligue1(sender,result)
                            send_paquet(token,payload)
                            print('resultats ligue1 envoyé')
                            return 'nothing'
                        else :
                            texte='Choisissez parmis :'
                            payload=send_choix_multiple2(sender,texte,'Ligue1 Classement','Ligue1 Résultats')
                            send_paquet(token,payload)
                            print('Demande de quoi en ligue1 envoyé')
                            return 'nothing'
                    else :
                        texte = 'Quoi en particulier en ligue1 ? '
                        payload = send_choix_multiple2(sender,texte,'Ligue1 Classement','Ligue1 Résultats')
                        send_paquet(token,payload)
                        print('Demande de quoi en ligue1 envoyé')
                        return 'nothing'
                elif 'liga' in mots_du_msg :
                    if len(mots_du_msg)>1 :
                        mot_suivant = mots_du_msg[1]
                        mot_suivant[recherche_similitude(classement_liste,mots_du_msg)+1]

                        if mot_suivant in classement_liste:
                            classm = download_classement_liga()
                            payload = send_classement_liga(sender,classm)
                            send_paquet(token,payload)
                            print('Demande de quoi en liga envoyé')
                            return 'nothing'
                        elif mot_suivant in resultat_liste:
                            result = download_resultats_liga()
                            payload = send_resultats_liga(sender,result)
                            send_paquet(token,payload)
                            print('resultats liga envoyé')
                            return 'nothing'
                        else :
                            texte='Choisissez parmis :'
                            payload=send_choix_multiple2(sender,texte,'Liga Classement','Liga Résultats')
                            send_paquet(token,payload)
                            print('Demande de quoi en liga envoyé')
                            return 'nothing'
                    else :
                        texte = 'Quoi en particulier en Liga ? '
                        payload = send_choix_multiple2(sender,texte,'Liga Classement','Liga Résultats')
                        send_paquet(token,payload)
                        print('Demande de quoi en liga envoyé')
                        return 'nothing'

                elif similitudes(['Tout','tout'],mots_du_msg):
                    if len(mots_du_msg)>1 : 
                        mot_suivant = mots_du_msg[1]
                        if mot_suivant in ['sport']:
                            actu_sport = 1 # On lui enverra l'actu
                            sport = extract_news('sport')
                            #payload = send_news(sender,mot_suivant,0,actu_sport)
                            payload = send_link4(sender,sport[0]['titre'],sport[0]['journal'],sport[0]['image'],sport[0]['lien'],sport[1]['titre'],sport[1]['journal'],sport[1]['image'],sport[1]['lien'],sport[2]['titre'],sport[2]['journal'],sport[2]['image'],sport[2]['lien'],sport[3]['titre'],sport[3]['journal'],sport[3]['image'],sport[3]['lien'])
                            send_paquet(sender,payload)
                            texte = "Si tu as encore faim voici la carte :"
                            payload = send_choix_multiple4(sender,texte,'Actualité',actu_img,'Météo',meteo_img,'Fais croquer',pomme_img,'Wiki obama',wiki_img)
                            send_paquet(token,payload)
                            print("Actu sport envoyée")
                            return 'nothing'
                        else : 
                            texte = "Voici tout ce que j'ai à te proposer : "
                            payload = send_choix_multiple4(sender,texte,'Actualité',actu_img,'Météo',meteo_img,'Wiki obama',wiki_img,'Date',date_img)
                            send_paquet(token,payload)
                            return 'nothing'
                    else : 
                        texte = "Tu veux tout ? Voici tout ce que j'ai à te proposer : "
                        payload = send_choix_multiple4(sender,texte,'Actualité',actu_img,'Météo',meteo_img,'Wiki obama',wiki_img,'Date',date_img)
                        send_paquet(token,payload)
                        return 'nothing'

                elif similitudes(['Foot','foot'],mots_du_msg):
                    texte = 'Quoi en particulier ?'
                    payload = send_choix_multiple2(sender,texte,'Ligue1','Liga')
                    send_paquet(sender,payload)
                    print('Demande championnat envoyée')
                    return 'nothing'

                #elif similitudes(['reglage'],mots_du_msg)!=[]:
                    #payload = reglage_menu()
                    #requests.post('https://graph.facebook.com/v2.6/me/messenger_profile?access_token=' + token1, json=payload)
                    #payload = description()
                    #requests.post('https://graph.facebook.com/v2.6/me/messenger_profile?access_token=' + token1, json=payload)
                    #print('Menu hal changé')
                    #payload = whitelist()
                    #requests.post('https://graph.facebook.com/v2.6/me/messenger_profile?access_token'+ token, json=payload)
                    #print('whitelisté')
                #elif similitudes(['réglagee'],mots_du_msg)!=[]:
                    #payload = get_started()
                    #requests.post('https://graph.facebook.com/v2.6/me/messenger_profile?access_token=' + token1, json=payload)
                    #print('Get started hal changé')
                    return 'nothing'

                else  : # Si reconnait pas la demande
                    texte = "Je n'ai pas de service à te proposer avec ce type de demande.. :( Essayes : "
                    payload = send_choix_multiple4(sender,texte,'Actualité',actu_img,'Météo',meteo_img,'Wiki obama',wiki_img,'Date',date_img)
                    send_paquet(token,payload)
                    print('Reponse a msg pas compris')
                    return 'nothing'

            elif type_msg_recu == 'read_msg':
                print('Message lu')
            elif type_msg_recu == 'delivery_msg':
                print('Message délivré')
            elif type_msg_recu == 'unknow_msg':
                print(data)
                print('Message inconnu')
            elif type_msg_recu == 'location_msg':
                type_msg_recu, latitude, longitude = depaquet
                payload = send_meteo(sender,api_key_weather,latitude,longitude)
                send_paquet(token,payload)
                return 'nothing'
            elif type_msg_recu == 'postback_msg':
                type_msg_recu, postback = depaquet
                if postback=='salut':
                    texte = "Salut!\n"+nouveaute+"Choisis :"
                    payload = send_choix_multiple4(sender,texte,'Actualité',actu_img,'Météo',meteo_img,'Fais croquer',pomme_img,'Wiki obama',wiki_img)
                    send_paquet(token,payload)
                    print('GET STARTED')
                    return 'nothing'
                elif postback=='menu':
                    texte = "Voici la carte, choisis ce qu'il te plait :"
                    payload = send_choix_multiple4(sender,texte,'Actualité',actu_img,'Météo',meteo_img,'Fais croquer',pomme_img,'Wiki obama',wiki_img)
                    send_paquet(token,payload)
                    print('Reponse au retour menu')
                    return 'nothing'
                elif postback[:4]=='actu':
                    #traitement_actu(postback,sender,1)
                    mot_suivant = postback[4:]
                    payload = send_news2(sender,mot_suivant)
                    send_paquet(token,payload)
                    if mot_suivant!='sport':
                        texte = "Voici la carte, fais toi plaisir :"
                        payload = send_choix_multiple4(sender,texte,'Actualité',actu_img,'Météo',meteo_img,'Fais croquer',pomme_img,'Wiki obama',wiki_img)
                        send_paquet(token,payload)
                        return 'nothing'
                elif postback=='partage':
                    payload = send_share(sender)
                    send_paquet(token,payload)
                    texte = "Aprés cet effort, le réconfort :"
                    payload = send_choix_multiple4(sender,texte,'Actualité',actu_img,'Météo',meteo_img,'Fais croquer',pomme_img,'Wiki obama',wiki_img)
                    send_paquet(token,payload)
                    print('Reponse à demande de partage')
                    return 'nothing'
                else :
                    print('postback inconnu :')
                    print(postback)
            elif type_msg_recu == 'image_msg':
                texte = "Je ne gére pas encore les images/GIFs, essayes plutôt :"
                payload = send_choix_multiple4(sender,texte,'Actualité',actu_img,'Météo',meteo_img,'Fais croquer',pomme_img,'Wiki obama',wiki_img)
                send_paquet(token,payload)
                print('Reponse à une image recue')
                return 'nothing'
        except Exception as e:
                    print(traceback.format_exc())
    elif request.method == 'GET':
        if request.args.get('hub.verify_token') == FB_VERIFY_TOKEN:
            return request.args.get('hub.challenge')
        return "Wrong Verify Token"
    return "Nothing"

nouveaute = "Nouveauté : Refonte de l'affichage de l'actualité\n"

# LISTE DE MOTS CLES 
ponct_liste = ['.',',','!','?',';',':']
resultat_liste = ['resultat','resultats']
classement_liste = ['classement','tableau']
partage_liste = ['partage','partager','ami','amis']
vulgarite_liste = ['tg','moche','nul','fdp','tagueule','connard','pd','idiot','encule','salop','ntm','nique','fuck'] 
menu_liste = ['Menu','menu','start','Start']
meteo_liste = ["meteo",'temps','temperature']
bonjour_liste = ['hey','bonsoir','bonjour','salut','coucou','hi','hello']
lien_liste = ['lien','Lien','link','Link']
date_liste = ['Date','date','jour','Jour','Mois','mois','année']
wiki_liste = ['wikipedia','wiki']
news_liste = ['actualites','actualite','news','actu','actus','journal','newspaper']
merci_liste = ['merci','thanks','thank','gracias']

meteo_img = 'http://ian.umces.edu/imagelibrary/albums/userpics/12865/normal_ian-symbol-weather-solar-radiation.png'
actu_img = 'http://icons.iconarchive.com/icons/zerode/plump/256/Network-Earth-icon.png'
wiki_img = 'http://www.icone-png.com/png/25/24983.png'
date_img = 'https://cdn2.iconfinder.com/data/icons/perfect-flat-icons-2/512/Date_calendar_event_month_time_day_vector.png'
pomme_img = 'https://s2.qwant.com/thumbr/0x0/5/8/3078a9585992fbea80e57c386326b7/b_1_q_0_p_0.jpg?u=http%3A%2F%2Fwww.free-icons-download.net%2Fimages%2Fred-apple-icon-54633.png&q=0&b=1&p=0&a=1' 

# ENVOYER UN PAYLOAD
def send_paquet(sender,payload):
    r = requests.post('https://graph.facebook.com/v2.6/me/messages/?access_token=' + token, json=payload)
    print(r.text) # affiche la reponse à l'envoit; pratique si veut l'ID ou voir si bien envoyé
    pass
def send_news2(sender,mot_suivant):
  if mot_suivant in ['sport']:
    texte = "Quel sport t'interesse ? "
    payload = send_choix_multiple3(sender,texte,'Tout sport','Foot','Rugby')
    return payload
  if mot_suivant in ['world','monde']:
    world = extract_news('world')
    payload = send_link4(sender,world[0]['titre'],world[0]['journal'],world[0]['image'],world[0]['lien'],world[1]['titre'],world[1]['journal'],world[1]['image'],world[1]['lien'],world[2]['titre'],world[2]['journal'],world[2]['image'],world[2]['lien'],world[3]['titre'],world[3]['journal'],world[3]['image'],world[3]['lien'])
  elif mot_suivant in ['france']:
    france = extract_news('france')
    payload = send_link4(sender,france[0]['titre'],france[0]['journal'],france[0]['image'],france[0]['lien'],france[1]['titre'],france[1]['journal'],france[1]['image'],france[1]['lien'],france[2]['titre'],france[2]['journal'],france[2]['image'],france[2]['lien'],france[3]['titre'],france[3]['journal'],france[3]['image'],france[3]['lien'])
  elif mot_suivant in ['economie','business']:
    economie = extract_news('economie')
    payload = send_link4(sender,economie[0]['titre'],economie[0]['journal'],economie[0]['image'],economie[0]['lien'],economie[1]['titre'],economie[1]['journal'],economie[1]['image'],economie[1]['lien'],economie[2]['titre'],economie[2]['journal'],economie[2]['image'],economie[2]['lien'],economie[3]['titre'],economie[3]['journal'],economie[3]['image'],economie[3]['lien'])
  elif mot_suivant in ['sante']:
    sante = extract_news('sante')
    payload = send_link4(sender,sante[0]['titre'],sante[0]['journal'],sante[0]['image'],sante[0]['lien'],sante[1]['titre'],sante[1]['journal'],sante[1]['image'],sante[1]['lien'],sante[2]['titre'],sante[2]['journal'],sante[2]['image'],sante[2]['lien'],sante[3]['titre'],sante[3]['journal'],sante[3]['image'],sante[3]['lien'])
  elif mot_suivant in ['culture']:
    culture = extract_news('culture')
    payload = send_link4(sender,culture[0]['titre'],culture[0]['journal'],culture[0]['image'],culture[0]['lien'],culture[1]['titre'],culture[1]['journal'],culture[1]['image'],culture[1]['lien'],culture[2]['titre'],culture[2]['journal'],culture[2]['image'],culture[2]['lien'],culture[3]['titre'],culture[3]['journal'],culture[3]['image'],culture[3]['lien'])
  elif mot_suivant in ['science']:
    science = extract_news('science')
    payload = send_link4(sender,science[0]['titre'],science[0]['journal'],science[0]['image'],science[0]['lien'],science[1]['titre'],science[1]['journal'],science[1]['image'],science[1]['lien'],science[2]['titre'],science[2]['journal'],science[2]['image'],science[2]['lien'],science[3]['titre'],science[3]['journal'],science[3]['image'],science[3]['lien'])
  else :
    une = extract_news('une')
    payload = send_link6(sender,une[0]['titre'],une[0]['journal'],une[0]['image'],une[0]['lien'],une[1]['titre'],une[1]['journal'],une[1]['image'],une[1]['lien'],une[2]['titre'],une[2]['journal'],une[2]['image'],une[2]['lien'],une[3]['titre'],une[3]['journal'],une[3]['image'],une[3]['lien'],une[4]['titre'],une[4]['journal'],une[4]['image'],une[4]['lien'],une[5]['titre'],une[5]['journal'],une[5]['image'],une[5]['lien'])
  return payload
def extract_news(categorie):
    articles = []
    for newss in db.session.query(News).filter_by(categorie=categorie):
        article = {}
        article['titre'] = newss.titre
        article['journal'] = newss.journal
        article['lien'] = newss.lien
        article['image'] = newss.image
        articles.append(article)
    return articles

if __name__ == '__main__':
    #db.create_all()
    app.run(debug=True)
