import praw
import config
import requests
import json
from datetime import date, timedelta
import bs4
import re


#reddit authentication
reddit = praw.Reddit(username = config.username, 
                    password = config.password,
                    client_id = config.client_id, 
                    client_secret = config.client_secret,
                    user_agent = "script:test for r/sixfeetunder:v1.0 (by /u/f1uk3r)")

#amazon season url list
amazonContainer=["https://www.amazon.com/Six-Feet-Under-Season-1/dp/B006GLLR4A", 
                "https://www.amazon.com/Six-Feet-Under-Season-2/dp/B0190TKA2Y", 
                "https://www.amazon.com/Six-Feet-Under-Season-3/dp/B00KGS1RAS", 
                "https://www.amazon.com/Six-Feet-Under-Season-4/dp/B0078YWTJQ", 
                "https://www.amazon.com/Six-Feet-Under-Season-5/dp/B0078YWR5M"]


def soupMaker(url):
  res = requests.get(url)
  soup = bs4.BeautifulSoup(res.text, 'html.parser')
  return soup

#Input season and episode number
season = int(input("Enter season number without preceding 0's:" ))
episode = int(input("Enter episode number without preceding 0's:" ))

if episode<10:
  episodeFinal = "0{0}".format(str(episode))
else:
  episodeFinal = str(episode)

#extracting informations and urls from hbo website
hboBaseUrl = "https://www.hbo.com"
hboMain = soupMaker("https://www.hbo.com/six-feet-under/season-0" + str(season))
allEpisodes = hboMain.findAll('div', {'class':'serialepisodeband'})
for eachEpisode in allEpisodes:
  if episode < 10:
    if str(eachEpisode.find('p', {'class':'modules/Episode--textLabel'}).text)[-9:]=="Episode "+str(episode):
      requiredEpisodeSpan = eachEpisode.find('span', {'class':'modules/Episode--title'})
      hboEpisodeUrl = hboBaseUrl + str(requiredEpisodeSpan.find('a')['href'])
  else:
    if str(eachEpisode.find('p', {'class':'modules/Episode--textLabel'}).text)[-2:]==str(episode):
      requiredEpisodeSpan = eachEpisode.find('span', {'class':'modules/Episode--title'})
      hboEpisodeUrl = hboBaseUrl + str(requiredEpisodeSpan.find('a')['href'])
hboSynopsis = soupMaker(hboEpisodeUrl + "/synopsis")
creditSynopsisContainer = hboSynopsis.find('div', {'class':'modules/Article--externalHtmlContainer'})
synopsisAllPContainer = creditSynopsisContainer.findAll('p')
credit = str(synopsisAllPContainer[0].text)
credit = re.sub(r'Written', r'\nWritten', credit)
if len(synopsisAllPContainer)==2:
  synopsis = str(synopsisAllPContainer[1].text)
else:
  synopsis = ''
  for i in range(1,len(synopsisAllPContainer)):
    synopsis += str(synopsisAllPContainer[i].text) + "  \n"

#extracting informations and urls from imdb website
baseImdbUrl = "https://www.imdb.com/title/tt0248654/episodes?season="
imdbEpisodeListContainer = soupMaker(baseImdbUrl + str(season))
allImdbEpisodes = imdbEpisodeListContainer.findAll('div', {'class':'list_item'})
for eachEpisode in allImdbEpisodes:
  episodeNumberContainer = eachEpisode.find('div',{'class': 'hover-over-image'})
  if episode < 10:
    if str(episodeNumberContainer.find('div').text)[-3:]=="Ep" + str(episode):
      episodeName = str(eachEpisode.find('a')['title'])
      imdbEpisodeUrl ="https://www.imdb.com" + str(eachEpisode.find('a')['href'])
      airDate = eachEpisode.find('div', {'class':'airdate'}).text
  else:
    if str(episodeNumberContainer.find('div').text)[-2:]==str(episode):
      episodeName = str(eachEpisode.find('a')['title'])
      imdbEpisodeUrl ="https://www.imdb.com" + str(eachEpisode.find('a')['href'])
      airDate = eachEpisode.find('div', {'class':'airdate'}).text

#extracting informations and urls from trakt website
traktEpisodeUrl = "https://trakt.tv/shows/six-feet-under/seasons/{0}/episodes/{1}".format(str(season), str(episode))
traktEpisodeContainer = soupMaker(traktEpisodeUrl)
obituaryDivContainer = traktEpisodeContainer.find('div', {'class':'overview'})
obituaryRaw = str(obituaryDivContainer.find('p').text)
if re.match(r"^([\w \,\.\"]+, \d{4} ?- ?\w+ \d+, ?\d{4})", obituaryRaw) is not None:
  obituary = re.match(r"^([\w \,\.\"]+, \d{4} ?- ?\w+ \d+, ?\d{4})", obituaryRaw).group(0)
elif re.match(r"^([\w \,\.]+ ?- ?\d{4})", obituaryRaw) is not None:
  obituarySecondary = re.match(r"^([\w \,\.]+ ?- ?\d{4})", obituaryRaw).group(0)
  timeline = "  \n" + re.search(r'(\d{4} ?- ?\d{4})', obituarySecondary).group(0)
  obituary = re.sub(r'(\d{4} ?- ?\d{4})', timeline, obituarySecondary)
elif season == 1 and episode == 7:
  obituary = '''Chloe Margaret Bryant Yorkin  
January 7, 1959 - April 2001'''
elif season == 5 and episode == 12:
  obituary = "No one died"

#urls that is going to be added in body
wikipediaSeasonUrl = "https://en.wikipedia.org/wiki/List_of_Six_Feet_Under_episodes#Season_{0}_(200{0})".format(str(season))
hboGoUrl = hboBaseUrl + "/six-feet-under"
amazonUrl = amazonContainer[season-1]
fishercastContainerUrl = "https://drive.google.com/drive/folders/1fQ-02ZDam7CHIuhzZJxAtZyhTPKzD7pD"

#extracting url from avclub website
avclubEpisodeContainer = soupMaker("https://www.avclub.com/c/tv-review/six-feet-under/season-{0}".format(str(season)))
avclubEpisodeH1Container = avclubEpisodeContainer.findAll('h1', {'class':'headline entry-title'})
for thisEpisode in avclubEpisodeH1Container:
  avclubEpisodeUrl = str(thisEpisode.find('a')['href'])
  avclubEpisodeNameRaw = str(thisEpisode.find('div').text)
  if avclubEpisodeNameRaw[17:-1].lower()==episodeName.lower():
    break
if season == 5:
  avclubEpisodeUrl = "https://www.avclub.com/c/tv-review/six-feet-under"

#extracting url from playerfm website
playerfmBaseUrl = "https://player.fm"
diggingSfuEpisodeContainer = soupMaker("https://player.fm/series/digging-six-feet-under-podcast-2035002/episodes?active=true&limit=100&order=newest&query=&style=list&container=false&offset=")
diggingSfuAllEpisodes = diggingSfuEpisodeContainer.findAll('div', {'class':'info-top'})
for thisEpisode in diggingSfuAllEpisodes:
  diggingSfuLinkContainer = thisEpisode.find('a')
  if str(diggingSfuLinkContainer.text)[:6]=="S0{0}E{1}".format(str(season), episodeFinal):
    diggingSfuEpisodeUrl = playerfmBaseUrl + str(diggingSfuLinkContainer['href'])
    break

#body starts here
body = '''>[Discussion] Six Feet Under - "{2}" (S0{0}E{1})

###Details
______________________

{3}

Originally Aired: {14}

###Obituary
________________________________________________________________

>!{5}!<


###Synopsis
________________________________________________
>!{4}!<

###Expansion
_____________________________________________

- [AVClub/John Teti]({10}) (Dissection)
- [FisherCast]({15}) (Podcast)
- [Digging SFU]({11}) (Podcast)

###Relevant Links
_______________________________________________________________________

- [trakt.tv]({9})
- [IMDb]({7})
- [Wikipedia]({8})
- [HBO.com]({6})

###Where to watch
_______________________________________

- [HBO GO/HBO NOW]({12})
- [Amazon]({13})

#[All Discussion Threads Index (Google Docs)](https://docs.google.com/spreadsheets/d/1YPx-qMpIVkpZktaMosTkNICgxG9wiWby_YhPBYhEp0w/edit?usp=sharing)

||
|:-:|
|^bot-script ^by ^/u/f1uk3r|'''.format(str(season), episodeFinal, episodeName,credit, synopsis, obituary,hboEpisodeUrl, imdbEpisodeUrl,wikipediaSeasonUrl,traktEpisodeUrl,avclubEpisodeUrl,diggingSfuEpisodeUrl,hboGoUrl,amazonUrl,airDate,fishercastContainerUrl)

#print(body)
#title of the post
title = "[Discussion] Six Feet Under - \"{2}\" (S0{0}E{1})".format(str(season), episodeFinal, episodeName)

#posting it on concerned subreddit
response = reddit.subreddit('nonaestheticthings').submit(title, selftext=body, send_replies=False)
#making post distinguishable
response.mod.distinguish(how="yes")
#making post sticky
response.mod.sticky()