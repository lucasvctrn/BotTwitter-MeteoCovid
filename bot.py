import tweepy
import requests
import datetime
import json
import emoji

client = tweepy.Client(consumer_key='aMuKdG5RVbgH7tGzWknPQMPJ1',
                       consumer_secret='PMQ0qAzn8z4vxyDQ9oWiGT5CEqWJbE21nrZcKPZiuvkTOZy3pa',
                       access_token='1482981962688122881-Gka8KbxCtP3tbEMCUFrkukMfSV2YX9',
                       access_token_secret='OnxaPhyFCeYnBxIE50UTvQPFuMfHs6OXSNNCXPccoDaSH')

# Récupération de la date de l'avant veille
before_yesterday = datetime.date.today() - datetime.timedelta(days=2)
before_yesterday_date = before_yesterday.strftime("%d-%m-%Y")

# Récupération des données de Meurthe et Moselle de l'avant veille
before_yesterday_response = requests.get("https://coronavirusapifr.herokuapp.com/data/france-by-date/" + before_yesterday_date).content
before_yesterday_data = json.loads(before_yesterday_response)

# Récupération de la date de la veille
yesterday = datetime.date.today() - datetime.timedelta(days=1)
yesterday_date = yesterday.strftime("%d-%m-%Y")

# Récupération des données de Meurthe et Moselle de la veille
yesterday_response = requests.get("https://coronavirusapifr.herokuapp.com/data/france-by-date/" + yesterday_date).content
yesterday_data = json.loads(yesterday_response)

# Tweet l'évolution probable des contaminations à l'échelle nationale
for before_yesterday_value in before_yesterday_data:
   for yesterday_value in yesterday_data:
      if yesterday_value["conf_j1"] + (yesterday_value["conf_j1"] - before_yesterday_value["conf_j1"]) > 0:
         new_contaminations = yesterday_value["conf_j1"] + (yesterday_value["conf_j1"] - before_yesterday_value["conf_j1"]) * 1.5
         client.create_tweet(text="En vu des chiffres des contaminations du Covid19 de ces derniers jours, nous estimons que le nombre de nouveaux infectés le " + datetime.date.today().strftime('%d-%m-%Y') + " s'élèvera à " + str(new_contaminations) + " personnes.")
      else:
         client.create_tweet(text="Hier, le " + yesterday_date + " s'élèvera à " + str(new_contaminations) + " personnes.")

# Récupération des données les plus récentes des départements
yesterday_deps_response = requests.get("https://coronavirusapifr.herokuapp.com/data/live/departements").content
yesterday_deps_data = json.loads(yesterday_deps_response)

# Création du tableau réprésentatif de la carte de France avec les numéros de départements. Les 0 réprésentent des espaces
franceMapTable = [0, 0, 0, 0, 0, 62, 59, "\n", 0, 0, 0, 0, 80, 60, 2, 8, "\n", 0, 0, 14, 27, 76, 95, 93, 51, 55, 57, "\n", 29, 22, 35, 50, 61, 75, 94, 10, 52, 54, 88, 67, "\n", 0, 56, 53, 72, 78, 92, 91, 77, 21, 70, 90, 68, "\n", 0, 44, 85, 49, 28, 41, 45, 89, 71, 39, 25, "\n", 0, "  ", 79, 86, 37, 36, 18, 58, 69, 1, 74, "\n", 0, 0, 17, 16, 23, 3, 42, 38, 73, "\n", 0, "  ", 33, 24, 87, 19, 63, 7, 26, 5, "\n", 0, 40, 47, 46, 15, 43, 48, 84, 4, "\n", 0, 64, 32, 82, 12, 34, 30, 13, 83, 6, "\n", 0, 0, 65, 31, 81, 11, "\n", 0, 0, 0, 9, 66]

# Remplacement des numéros de départements du tableau par un smiley décrivant le taux d'occupation hospitalier du département
for yesterday_deps_value in yesterday_deps_data:
   emojiDep = ""

   if yesterday_deps_value["TO"] > 1 :
      emojiDep = emoji.emojize(':fire:')
   elif yesterday_deps_value["TO"] > 0.8 :
      emojiDep = emoji.emojize(':warning:')
   elif yesterday_deps_value["TO"] > 0.6 :
      emojiDep = emoji.emojize(':hot_face:')
   elif yesterday_deps_value["TO"] > 0.4 :
      emojiDep = emoji.emojize(':face_with_head-bandage:')
   elif yesterday_deps_value["TO"] > 0.2 :
      emojiDep = emoji.emojize(':sneezing_face:')
   else:
      emojiDep = emoji.emojize(':grinning_face:')

   for i in range(len(franceMapTable)):
      if(franceMapTable[i] == yesterday_deps_value["dep"]):
         franceMapTable[i] = emojiDep

# Remplacement des 0 du tableau par des emojis vague, permettant de faire un espace plus important que le caractère espace (nécessaire car Twitter limite les caractères)
for i in range(len(franceMapTable)):
   if(franceMapTable[i] == 0):
      franceMapTable[i] = emoji.emojize(':water_wave:')

# Création d'une string à partir du tableau et publication du tweet
franceMap = "".join(franceMapTable)
tweetText = emoji.emojize(':face_with_medical_mask:') + " Météo Covid du jour :\n\n" + franceMap
response = client.create_tweet(text=tweetText)

# Réponse au tweet contenant la légende de la carte
legende = "Cette carte représente le 'TO' (taux d'occupation : tension hospitalière sur la capacité en réanimation) par département, en pourcentage.\n\nLégende :\n" + emoji.emojize(':fire:') + " TO > 100%\n" + emoji.emojize(':warning:') + " TO > 80%\n" + emoji.emojize(':hot_face:') + " TO > 60%\n" + emoji.emojize(':face_with_head-bandage:') + " TO > 40%\n" + emoji.emojize(':sneezing_face:') + " TO > 20%\n" + emoji.emojize(':grinning_face:') + " TO < 20%"
client.create_tweet(text=legende, in_reply_to_tweet_id=response[0]["id"])