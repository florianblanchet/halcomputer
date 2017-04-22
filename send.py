# POUR GENERER DES PAYLOAD :
import wikipedia
from toolkit import recherche_similitude
from download import download_meteo, download_news


def send_classement_ligue1(sender, tableau):
    texte = ''
    for i in range(len(tableau)):
        texte+=str(i+1)+' '+tableau[i][0]+' '+tableau[i][1]+'pts, '+tableau[i][2]+'diff\n'
    payload = send_choix_multiple3(sender,texte,'Foot','Actu Sport','Menu')
    return payload
def send_classement_liga(sender, tableau):
    texte = ''
    for i in range(len(tableau)):
        texte+=str(i+1)+' '+tableau[i][0]+' '+tableau[i][1]+'pts\n'
    payload = send_choix_multiple3(sender,texte,'Foot','Actu Sport','Menu')
    return payload
def send_resultats_ligue1(sender,tableau):
    texte = ''
    for i in range(len(tableau)):
        texte+=tableau[i][0]+' '+tableau[i][2]+' '+tableau[i][1]+'\n'
    payload = send_choix_multiple3(sender,texte,'Foot','Actu Sport','Menu')
    return payload
def send_resultats_liga(sender,tableau):
    texte = ''
    for i in range(len(tableau)):
        texte+=tableau[i][0]+' '+tableau[i][2]+' '+tableau[i][1]+'\n'
    payload = send_choix_multiple3(sender,texte,'Foot','Actu Sport','Menu')
    return payload
def send_share(sender):
  texte = "Hal est un chatbot qui offre un certain nombre de services tels que donner l'actualité, la météo ou même faire des recherches sur wkipédia. Tu as simplement besoin de lui dire Bonjour pour commencer l'expérience!"
  return {"recipient":{"id":sender },
  "message":{
    "attachment":{
      "type":"template",
      "payload":{
        "template_type":"button",
        "text":'Click pour permettre à tes potes de discuter avec moi 🙏!',
        "buttons":[
            {
            "type": "element_share",
            "share_contents": { 
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": [{
                            "title": "Hal Chatbot",
                            "subtitle": texte,
                            "default_action": {"type": "web_url","url": 'https://m.me/halcomputer'},
                            "buttons": [{
                                  "type": "web_url",
                                  "url": 'http://m.me/halcomputer', 
                                  "title": 'Se lancer !'
                                }]
                            }]
                        }
                    }
                }
            }]
        }
    }}}
def send_msg_button1(sender,texte,nom_button,reponse_rapide):
  return {
  "recipient":{
    "id":sender
  },
  "message":{
    "attachment":{
      "type":"template",
      "payload":{
        "template_type":"button",
        "text":texte,
        "buttons":[
          {
            "type":"postback",
            "title":nom_button,
            "payload":reponse_rapide
          }
        ]
      }
    }
  }
 } 
def send_button2_postback_url(sender,texte,nom_button1,reponse_rapide1,nom_lien,link):
  return {"recipient":{"id":sender },
  "message":{
    "attachment":{
      "type":"template",
      "payload":{
        "template_type":"button",
        "text":texte,
        "buttons":[{
            "type":"web_url",
            "url": link,
            "title": nom_lien
            },
            {
            "type": "element_share",
            "share_contents": { 
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": [{
                            "title": "Actualité",
                            "subtitle": texte,
                            "default_action": {"type": "web_url","url": link},
                            "buttons": [{
                                  "type": "web_url",
                                  "url": link, 
                                  "title": nom_lien
                                }]
                            }]
                        }
                    }
                }
            },
            {
            "type":"postback",
            "title":nom_button1,
            "payload":reponse_rapide1
            }]
        }
    }}}
def location_quick_answer(sender):
  return {
        "recipient": {
            "id": sender
        },
        "message": {
            "text": "Share your location:",
            "quick_replies": [
                {
                    "content_type": "location",
                },
                {
                "content_type":"text",
                "title":'Météo Paris',
                "payload":"Météo Paris"
      }
            ]
        }
    }
def send_news(sender,mot_suivant,number,actu_sport):
    #une,world,france,economie,science,culture,sport,sante = download_news()
    nom_lien = "Accéder à l'article"
    if mot_suivant in ['world','World','monde','Monde']:
        index_suivant = (int(number)+1)%len(world)
        if index_suivant != 0 :
            #payload = send_msg_button1(sender,world[int(number)][0]+'\n\nSource : '+world[int(number)][1],'Actu Monde suivante','reponse_actumon'+str(index_suivant)) #pour avoir reponse_actumon1 si premiere actu
            payload = send_button2_postback_url(sender,world[int(number)][0]+'\n\nSource : '+world[int(number)][2],'Actu Monde suivante' , 'reponse_actumon'+str(index_suivant) , nom_lien, world[int(number)][1])
        else:
            texte = world[int(number)][0] + '\n\nSource : '+ world[int(number)][2]
            payload = send_choix_multiple7(sender,texte,'Menu','Actu Une','Actu France','Actu Sport','Actu Business','Actu Culture','Actu Santé')
    elif mot_suivant in ['france','France']:
        index_suivant = (int(number)+1)%len(france)
        if index_suivant != 0 :
            payload = send_button2_postback_url(sender, france[int(number)][0]+'\n\nSource : '+france[int(number)][2],'Actu France suivante','reponse_actufr'+str(index_suivant),nom_lien, france[int(number)][1]) #pour avoir reponse_actumon1 si premiere actu
        else:
            texte = france[int(number)][0]+'\n\nSource : '+france[int(number)][2]
            payload = send_choix_multiple7(sender,texte,'Menu','Actu Une','Actu Monde','Actu Sport','Actu Business','Actu Culture','Actu Santé')
    elif mot_suivant in ['Economie','economie','économie','business','Business']:
        index_suivant = (int(number)+1)%len(economie)
        if index_suivant != 0 :
            payload = send_button2_postback_url(sender, economie[int(number)][0]+'\n\nSource : '+economie[int(number)][2],'Actu économique suivante','reponse_actuec'+str(index_suivant),nom_lien,economie[int(number)][1])
        else:
            texte = economie[int(number)][0]+'\n\nSource : '+economie[int(number)][2]
            payload = send_choix_multiple7(sender,texte,'Menu','Actu Une','Actu Monde','Actu Sport','Actu France','Actu Culture','Actu Santé')
    elif mot_suivant in ['Science','science']:
        index_suivant = (int(number)+1)%len(science)
        if index_suivant != 0 :
            payload = send_button2_postback_url(sender, science[int(number)][0]+'\n\nSource : '+science[int(number)][2],'Actu scientifique suivante','reponse_actusc'+str(index_suivant),nom_lien,science[int(number)][1])
        else:
            texte = science[int(number)][0]+'\n\nSource : '+science[int(number)][2]
            payload = send_choix_multiple7(sender,texte,'Menu','Actu Une','Actu Monde','Actu Sport','Actu Business','Actu Culture','Actu Santé')
    elif mot_suivant in ['culture','Culture']:
        index_suivant = (int(number)+1)%len(culture)
        if index_suivant != 0 :
            payload = send_button2_postback_url(sender, culture[int(number)][0]+'\n\nSource : '+culture[int(number)][2],'Actu culturelle suivante','reponse_actucu'+str(index_suivant),nom_lien,culture[int(number)][1])
        else:
            texte = culture[int(number)][0]+'\n\nSource : '+culture[int(number)][2]
            payload = send_choix_multiple7(sender,texte,'Menu','Actu Une','Actu Monde','Actu Sport','Actu Business','Actu Science','Actu Santé')
    elif mot_suivant in ['Sport','sport']:
        if actu_sport==1 : # Il veut vraiment l'actu
            index_suivant = (int(number)+1)%len(sport)
            if index_suivant != 0 :
                payload = send_button2_postback_url(sender, sport[int(number)][0]+'\n\nSource : '+sport[int(number)][2],'Actu Sport suivante','reponse_actusp'+str(index_suivant),nom_lien,sport[int(number)][1])
            else:
                texte = sport[int(number)][0]+'\n\nSource : '+sport[int(number)][2]
                payload = send_choix_multiple7(sender,texte,'Menu','Actu Une','Actu Monde','Actu France','Actu Business','Actu Culture','Actu Santé')
        else: # On lui demande quel sport ou actu
            texte = "Quel sport t'interesse ? "
            payload = send_choix_multiple3(sender,texte,'Tout sport','Foot','Rugby')

    elif mot_suivant in ['Santé','santé','sante','Sante']:
        index_suivant = (int(number)+1)%len(sante)
        if index_suivant != 0 :
            payload = send_button2_postback_url(sender, sante[int(number)][0]+'\n\nSource : '+sante[int(number)][2],'Actu santé suivante','reponse_actusa'+str(index_suivant),nom_lien,sante[int(number)][1])
        else:
            texte = sante[int(number)][0]+'\n\nSource : '+sante[int(number)][2]
            payload = send_choix_multiple7(sender,texte,'Menu','Actu Une','Actu Monde','Actu Sport','Actu Business','Actu Culture','Actu France')
    else :
        index_suivant = (int(number)+1)%len(une)
        if index_suivant != 0 :
            payload = send_button2_postback_url(sender, une[int(number)][0]+'\n\nSource : '+une[int(number)][2],'Actu suivante','reponse_actutop'+str(index_suivant),nom_lien,une[int(number)][1])
        else:
            texte = une[int(number)][0]+'\n\nSource : '+une[int(number)][2]
            payload = send_choix_multiple7(sender,texte,'Menu','Actu France','Actu Monde','Actu Sport','Actu Business','Actu Culture','Actu Santé')
    return payload

def send_wiki(sender,mots_du_msg,wiki_liste):
    wikipedia.set_lang("fr")
    search = wikipedia.summary(str(mots_du_msg[recherche_similitude(wiki_liste,mots_du_msg)+1]), sentences=1)
    return {'recipient': {'id': sender}, 'message': {'text': search}}   
def send_meteo(sender,api_key_weather,latitude,longitude):
    weather, description,icon = download_meteo(api_key_weather,latitude,longitude)
    texte = '{}\n' \
       'Temperature: {}\n' \
       'Pression: {}\n' \
       'Humidité: {}\n' \
       'Max: {}\n' \
       'Min: {}'.format(description, weather['temp'], weather['pressure'], weather['humidity'], weather['temp_max'], weather['temp_min'])
    payload = send_text(sender,texte)
    return payload
def send_link6 (sender,title1,subtitle1,image_url1,link1,title2,subtitle2,image_url2,link2,title3,subtitle3,image_url3,link3,title4,subtitle4,image_url4,link4,title5,subtitle5,image_url5,link5,title6,subtitle6,image_url6,link6):
    return {
    "recipient": {
      "id": sender
    },
    "message": {
      "attachment": {
        "type": "template",
        "payload": {
          "template_type": "generic",
          "image_aspect_ratio":'square',
          "elements": [{
            "title": title1,
            "subtitle": subtitle1,              
            "image_url": image_url1,
            "default_action":{"type":"web_url","url":link1},
            "buttons": [{
              "type": "web_url",
              "url": link1,
              "title": "Accéder à l'article"
            }, {
            "type": "element_share",
            "share_contents": { 
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": [{
                            "title": title1,
                            "subtitle": subtitle1,
                            "item_url": link1,               
                            "image_url": image_url1,
                            "buttons": [{
                              "type": "web_url",
                              "url": link1,
                              "title": "Accéder à l'article",
                                }]
                            }]
                        }
                    }
                }
            }]
          }, {
            "title": title2,
            "subtitle": subtitle2,              
            "image_url": image_url2,
            "default_action":{"type":"web_url","url":link2},
            "buttons": [{
              "type": "web_url",
              "url": link2,
              "title": "Accéder à l'article"
            }, {
            "type": "element_share",
            "share_contents": { 
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": [{
                            "title": title2,
                            "subtitle": subtitle2,
                            "item_url": link2,               
                            "image_url": image_url2,
                            "buttons": [{
                              "type": "web_url",
                              "url": link2,
                              "title": "Accéder à l'article"
                                }]
                            }]
                        }
                    }
                }
            }]
          }, {
            "title": title3,
            "subtitle": subtitle3,         
            "image_url": image_url3,
            "default_action":{"type":"web_url","url":link3},
            "buttons": [{
              "type": "web_url",
              "url": link3,
              "title": "Accéder à l'article"
            }, {
            "type": "element_share",
            "share_contents": { 
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": [{
                            "title": title3,
                            "subtitle": subtitle3,
                            "item_url": link3,               
                            "image_url": image_url3,
                            "buttons": [{
                              "type": "web_url",
                              "url": link3,
                              "title": "Accéder à l'article"
                                }]
                            }]
                        }
                    }
                }
            }]
          }, {
            "title": title4,
            "subtitle": subtitle4,         
            "image_url": image_url4,
            "default_action":{"type":"web_url","url":link4},
            "buttons": [{
              "type": "web_url",
              "url": link4,
              "title": "Accéder à l'article"
            }, {
            "type": "element_share",
            "share_contents": { 
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": [{
                            "title": title4,
                            "subtitle": subtitle4,
                            "item_url": link4,               
                            "image_url": image_url4,
                            "buttons": [{
                              "type": "web_url",
                              "url": link4,
                              "title": "Accéder à l'article"
                                }]
                            }]
                        }
                    }
                }
            }]
          }, {
            "title": title5,
            "subtitle": subtitle5,          
            "image_url": image_url5,
            "default_action":{"type":"web_url","url":link5},
            "buttons": [{
              "type": "web_url",
              "url": link5,
              "title": "Accéder à l'article"
            }, {
            "type": "element_share",
            "share_contents": { 
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": [{
                            "title": title5,
                            "subtitle": subtitle5,
                            "item_url": link5,               
                            "image_url": image_url5,
                            "buttons": [{
                              "type": "web_url",
                              "url": link5,
                              "title": "Accéder à l'article"
                                }]
                            }]
                        }
                    }
                }
            }]
          }, {
            "title": title6,
            "subtitle": subtitle6,        
            "image_url": image_url6,
            "default_action":{"type":"web_url","url":link6},
            "buttons": [{
              "type": "web_url",
              "url": link6,
              "title": "Accéder à l'article"
            }, {
            "type": "element_share",
            "share_contents": { 
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": [{
                            "title": title6,
                            "subtitle": subtitle6,
                            "item_url": link6,               
                            "image_url": image_url6,
                            "buttons": [{
                              "type": "web_url",
                              "url": link6,
                              "title": "Accéder à l'article"
                                }]
                            }]
                        }
                    }
                }
            }]
          }]
        }
      }
    }
    } 
def send_link4 (sender,title1,subtitle1,image_url1,link1,title2,subtitle2,image_url2,link2,title3,subtitle3,image_url3,link3,title4,subtitle4,image_url4,link4):
    return {
    "recipient": {
      "id": sender
    },
    "message": {
      "attachment": {
        "type": "template",
        "payload": {
          "template_type": "generic",
          "image_aspect_ratio":'square',
          "elements": [{
            "title": title1,
            "subtitle": subtitle1,             
            "image_url": image_url1,
            "default_action":{"type":"web_url","url":link1},
            "buttons": [{
              "type": "web_url",
              "url": link1,
              "title": "Accéder à l'article"
            }, {
            "type": "element_share",
            "share_contents": { 
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": [{
                            "title": title1,
                            "subtitle": subtitle1,
                            "item_url": link1,               
                            "image_url": image_url1,
                            "buttons": [{
                              "type": "web_url",
                              "url": link1,
                              "title": "Accéder à l'article"
                                }]
                            }]
                        }
                    }
                }
            }]
          }, {
            "title": title2,
            "subtitle": subtitle2,            
            "image_url": image_url2,
            "default_action":{"type":"web_url","url":link2},
            "buttons": [{
              "type": "web_url",
              "url": link2,
              "title": "Accéder à l'article"
            }, {
            "type": "element_share",
            "share_contents": { 
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": [{
                            "title": title2,
                            "subtitle": subtitle2,
                            "item_url": link2,               
                            "image_url": image_url2,
                            "buttons": [{
                              "type": "web_url",
                              "url": link2,
                              "title": "Accéder à l'article"
                                }]
                            }]
                        }
                    }
                }
            }]
          }, {
            "title": title3,
            "subtitle": subtitle3,             
            "image_url": image_url3,
            "default_action":{"type":"web_url","url":link3},
            "buttons": [{
              "type": "web_url",
              "url": link3,
              "title": "Accéder à l'article"
            }, {
            "type": "element_share",
            "share_contents": { 
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": [{
                            "title": title3,
                            "subtitle": subtitle3,
                            "item_url": link3,               
                            "image_url": image_url3,
                            "buttons": [{
                              "type": "web_url",
                              "url": link3,
                              "title": "Accéder à l'article"
                                }]
                            }]
                        }
                    }
                }
            }]
          }, {
            "title": title4,
            "subtitle": subtitle4,          
            "image_url": image_url4,
            "default_action":{"type":"web_url","url":link4},
            "buttons": [{
              "type": "web_url",
              "url": link4,
              "title": "Accéder à l'article"
            }, {
            "type": "element_share",
            "share_contents": { 
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": [{
                            "title": title4,
                            "subtitle": subtitle4,
                            "item_url": link4,               
                            "image_url": image_url4,
                            "buttons": [{
                              "type": "web_url",
                              "url": link4,
                              "title": "Accéder à l'article"
                                }]
                            }]
                        }
                    }
                }
            }]
          }]
        }
      }
    }
    }
def send_link3 (sender,title1,subtitle1,image_url1,link1,title2,subtitle2,image_url2,link2,title3,subtitle3,image_url3,link3):
    return {
    "recipient": {
      "id": sender
    },
    "message": {
      "attachment": {
        "type": "template",
        "payload": {
          "template_type": "generic",
          "elements": [{
            "title": title1,
            "subtitle": subtitle1,            
            "image_url": image_url1,
            "default_action":{"type":"web_url","url":link1},
            "buttons": [{
              "type": "web_url",
              "url": link1,
              "title": "Accéder à l'article"
            }, {
            "type": "element_share",
            "share_contents": { 
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": [{
                            "title": title1,
                            "subtitle": subtitle1,
                            "item_url": link1,               
                            "image_url": image_url1,
                            "buttons": [{
                              "type": "web_url",
                              "url": link1,
                              "title": "Accéder à l'article"
                                }]
                            }]
                        }
                    }
                }
            }]
          }, {
            "title": title2,
            "subtitle": subtitle2,             
            "image_url": image_url2,
            "default_action":{"type":"web_url","url":link2},
            "buttons": [{
              "type": "web_url",
              "url": link2,
              "title": "Accéder à l'article"
            }, {
            "type": "element_share",
            "share_contents": { 
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": [{
                            "title": title2,
                            "subtitle": subtitle2,
                            "item_url": link2,               
                            "image_url": image_url2,
                            "buttons": [{
                              "type": "web_url",
                              "url": link2,
                              "title": "Accéder à l'article"
                                }]
                            }]
                        }
                    }
                }
            }]
          }, {
            "title": title3,
            "subtitle": subtitle3,            
            "image_url": image_url3,
            "default_action":{"type":"web_url","url":link3},
            "buttons": [{
              "type": "web_url",
              "url": link3,
              "title": "Accéder à l'article"
            }, {
            "type": "element_share",
            "share_contents": { 
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": [{
                            "title": title3,
                            "subtitle": subtitle3,
                            "item_url": link3,               
                            "image_url": image_url3,
                            "buttons": [{
                              "type": "web_url",
                              "url": link3,
                              "title": "Accéder à l'article"
                                }]
                            }]
                        }
                    }
                }
            }]
          }]
        }
      }
    }
    }
def send_link (sender,title1,subtitle1,image_url1,link1,payload1,title2,subtitle2,image_url2,link2,payload2):
    return {
    "recipient": {
      "id": sender
    },
    "message": {
      "attachment": {
        "type": "template",
        "payload": {
          "template_type": "generic",
          "elements": [{
            "title": title1,
            "subtitle": subtitle1,
            "item_url": link1,               
            "image_url": image_url1,
            "buttons": [{
              "type": "web_url",
              "url": link1,
              "title": "Ouvre le lien"
            }, {
              "type": "postback",
              "title": "T'en veux plus ?",
              "payload": payload1,
            }],
          }, {
            "title": title2,
            "subtitle": subtitle2,
            "item_url": link2,               
            "image_url": image_url2,
            "buttons": [{
              "type": "web_url",
              "url": link2,
              "title": "Ouvre le lien"
            }, {
              "type": "postback",
              "title": "T'en veux plus ? ",
              "payload": payload2,
            }]
          }]
        }
      }
    }
    }

def send_text (sender,texte):

    return {'recipient': {'id': sender}, 'message': {'text': texte}}
def send_choix_multiple1(sender,texte,choix1):
  return {
  "recipient":{
    "id":sender
  },
  "message":{
    "text":texte,
    "quick_replies":[
      {
        "content_type":"text",
        "title":choix1,
        "payload":choix1
      }
    ]
  }
 } 
def send_choix_multiple2(sender,texte,choix1,choix2):
  return {
  "recipient":{
    "id":sender
  },
  "message":{
    "text":texte,
    "quick_replies":[
      {
        "content_type":"text",
        "title":choix1,
        "payload":choix1
      },
      {
        "content_type":"text",
        "title":choix2,
        "payload":choix2
      }
    ]
  }
 } 

def send_choix_multiple3(sender,texte,choix1,choix2,choix3):
  return {
  "recipient":{
    "id":sender
  },
  "message":{
    "text":texte,
    "quick_replies":[
      {
        "content_type":"text",
        "title":choix1,
        "payload":choix1
      },
      {
        "content_type":"text",
        "title":choix2,
        "payload":choix2
      },
      {
        "content_type":"text",
        "title":choix3,
        "payload":choix3
      }
    ]
  }
 } 
def send_choix_multiple4(sender,texte,choix1,img_url1,choix2,img_url2,choix3,img_url3,choix4,img_url4):
  return {
  "recipient":{
    "id":sender
  },
  "message":{
    "text":texte,
    "quick_replies":[
      {
        "content_type":"text",
        "title":choix1,
        "payload":choix1,
        "image_url" : img_url1
      },
      {
        "content_type":"text",
        "title":choix2,
        "payload":choix2,
        "image_url" : img_url2
      },
      {
        "content_type":"text",
        "title":choix3,
        "payload":choix3,
        "image_url" : img_url3
      },
      {
        "content_type":"text",
        "title":choix4,
        "payload":choix4,
        "image_url" : img_url4
      }
    ]
  }
 }
def send_choix_multiple7(sender,texte,choix1,choix2,choix3,choix4,choix5,choix6,choix7):
  return {
  "recipient":{
    "id":sender
  },
  "message":{
    "text":texte,
    "quick_replies":[
      {
        "content_type":"text",
        "title":choix1,
        "payload":choix1
      },
      {
        "content_type":"text",
        "title":choix2,
        "payload":choix2
      },
      {
        "content_type":"text",
        "title":choix3,
        "payload":choix3
      },
      {
        "content_type":"text",
        "title":choix4,
        "payload":choix4
      },
      {
        "content_type":"text",
        "title":choix5,
        "payload":choix5
      },
      {
        "content_type":"text",
        "title":choix6,
        "payload":choix6
      },
      {
        "content_type":"text",
        "title":choix7,
        "payload":choix7
      }
    ]
  }
 } 