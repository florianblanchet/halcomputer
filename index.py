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
#from models import *

token = os.environ.get('FB_ACCESS_TOKEN')
FB_VERIFY_TOKEN = os.environ.get('FB_VERIFY_TOKEN')
api_key_weather = os.environ.get('WEATHER_API_KEY')

me = os.environ.get('MY_ID') #ID de l'app

app = Flask(__name__)  #instance de la classe FLask. premier argument est le nom
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
db = SQLAlchemy()
db.app=app
db.init_app(app)

class BaseModel(db.Model):
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

class User(BaseModel,db.Model):
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

@app.route('/', methods=['GET', 'POST']) #A decorator that is used to register a view function for a given URL rule. Ici rule = / et en option les methodes assignées à ce rule
def webhook():
    if request.method == 'POST':  # Toutes les requetes post passent par la ; dans les deux sens
        try:
            data = json.loads(request.data.decode())  #recupere le message envoye a notre chatbot
            sender = data['entry'][0]['messaging'][0]['sender']['id']   # Qui nous l a envoye
            depaquet = depaquetage(sender,data,me,ponct_liste)
            print(depaquet)
            type_msg_recu = depaquet[0]

            # Controle si l'user est dans la base de donnée
            # Dans l'avenir faire ça au moment du get started -> gagne du temps de traitement
            if not db.session.query(User).filter(User.user_id==int(sender)).count() and (sender!=me):
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
                            une,world,france,economie,science,culture,sport,sante = download_news()
                            #payload = send_news(sender,mot_suivant,0,actu_sport)
                            payload = send_link4(sender,sport[0][2],sport[0][0],sport[0][3],sport[0][1],sport[1][2],sport[1][0],sport[1][3],sport[1][1],sport[2][2],sport[2][0],sport[2][3],sport[2][1],sport[3][2],sport[3][0],sport[3][3],sport[3][1])
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

                elif similitudes(['reglage'],mots_du_msg)!=[]:
                    payload = reglage_menu()
                    requests.post('https://graph.facebook.com/v2.6/me/messenger_profile?access_token=' + token1, json=payload)
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

def traitement_actu(postback,sender,actu_sport):
    if postback[:-1]=='reponse_actufr':
        payload = send_news(sender,'france',postback[-1],actu_sport)
        send_paquet(token,payload)
        print('News france '+str(postback[-1]),'envoyées')
    elif postback[:-1]=='reponse_actumon':
        payload = send_news(sender,'monde',postback[-1],actu_sport)
        send_paquet(token,payload)
        print('News monde '+str(postback[-1]),'envoyées')
    elif postback[:-1]=='reponse_actuec':
        payload = send_news(sender,'economie',postback[-1],actu_sport)
        send_paquet(token,payload)
        print('News economie '+str(postback[-1]),'envoyées')
    elif postback[:-1]=='reponse_actucu':
        payload = send_news(sender,'culture',postback[-1],actu_sport)
        send_paquet(token,payload)
        print('News culture '+str(postback[-1]),'envoyées')
    elif postback[:-1]=='reponse_actusa':
        payload = send_news(sender,'sante',postback[-1],actu_sport)
        send_paquet(token,payload)
        print('News sante '+str(postback[-1]),'envoyées')
    elif postback[:-1]=='reponse_actusp':
        payload = send_news(sender,'sport',postback[-1],actu_sport)
        send_paquet(token,payload)
        print('News sport '+str(postback[-1]),'envoyées')
    elif postback[:-1]=='reponse_actutop':
        payload = send_news(sender,'top',postback[-1],actu_sport)
        send_paquet(token,payload)
        print('News top '+str(postback[-1]),'envoyées')

# ENVOYER UN PAYLOAD
def send_paquet(sender,payload):
    requests.post('https://graph.facebook.com/v2.6/me/messages/?access_token=' + token, json=payload)
    pass

# INTERACTION UTILISATEUR PAS ENCORE UTILISE
def msg_seen(sender):
    payload = {
        "recipient":{
            "id":sender
            },
        "sender_action":"mark_seen"
    }
    send_paquet(sender,payload)
def typing_on(sender):
    payload = {
        "recipient":{
            "id":sender
            },
        "sender_action":"typing_on"
    }
    send_paquet(sender,payload)
def typing_off(sender):
    payload = {
        "recipient":{
            "id":sender
            },
        "sender_action":"typing_off"
    }
    send_paquet(sender,payload)

# CONFIGURATION DE LA PAGE HAL
def reglage_menu():
    payload = {
  "persistent_menu":[
    {
      "locale":"default",
      "call_to_actions":[
        {
          "type":"postback",
          "title":"Menu",
          "payload":"menu"
        },
        {
          "title":"Actualités",
          "type":"nested",
          "call_to_actions":[
            {
              "title":"A la une",
              "type":"postback",
              "payload":"actuune"
            },
            {
              "title":"Actu Monde",
              "type":"postback",
              "payload":"actumonde"
            },
            {
              "title":"Actu Sport",
              "type":"postback",
              "payload":"actusport"
            }
          ]
        },
        {
          "type":"postback",
          "title":"Fais croquer !",
          "payload":"partage"
        }
      ]
    },
    {
      "locale":"zh_CN",
      "composer_input_disabled":"false"
    }
  ]
 }
    return payload
def get_started():
    payload = { 
  "get_started":{
    "payload":"salut"
  }
 }
    return payload
def description():
    payload = {
  "greeting":[
    {
      "locale":"default",
      "text":"Salut {{user_first_name}}, commençons à discuter !"
    }, {
      "locale":"en_US",
      "text":"Hi {{user_first_name}}, let's start!"
    }
  ] 
 }
    return payload

if __name__ == '__main__':
    #db.create_all()
    app.run(debug=True)
