from bs4 import BeautifulSoup
import urllib2
import icalendar as IC
import datetime as DT
import os

def printTeamGames(schedule):
    print "Schedule:"
    for game in schedule:
        date = game["date"]
        hour = game["hour"]
        homeTeam = game["homeTeam"]
        awayTeam = game["awayTeam"]
        location = game["location"]
        print "%s %s: %s - %s\t(%s)" % (date,hour,homeTeam,awayTeam,location)

def getGameDict(gameRow):
    res = {}
    rowElements = gameRow.find_all_next("td")
    location = rowElements[0].find("img").get("title")[17:]
    date = rowElements[1].get_text()
    hour = rowElements[2].get_text()
    homeTeam = rowElements[3].get_text()
    awayTeam = rowElements[4].get_text()

    res["location"] = location
    res["date"] = date
    res["hour"] = hour
    res["homeTeam"] = homeTeam
    res["awayTeam"] = awayTeam

    return res

def getTeamSchedule(teamURL):
    res = []

    #download the link
    print "Downloading information from website"
    response = urllib2.urlopen(teamURL)
    html = response.read()

    soup = BeautifulSoup(html)
    wedstrijdTable = soup.find("div", id="wedstrijden")
    children = wedstrijdTable.children

    print "Processing data"
    firstTableRow = wedstrijdTable.find("tr")
    res.append(getGameDict(firstTableRow))

    for sibling in firstTableRow.next_siblings:
        res.append(getGameDict(sibling))

    return res

def createIcal(schedule, savePath):
    cal = IC.Calendar()

    for game in schedule:
        #find out if team plays home
        playsHome = False
        if game["location"][9:19] == "De Lichten":
            playsHome = True

        #get opponent
        opponent = game["homeTeam"]
        if playsHome:
            opponent = game["awayTeam"]

        #get start time
        dateArray = game["date"].split("-")
        timeArray = game["hour"].split(":")
        startTime = DT.datetime(int(dateArray[2]), int(dateArray[1]), int(dateArray[0]), int(timeArray[0]), int(timeArray[1]))

        event = IC.Event()
        event.add("summary", opponent)
        event.add("location", game["location"])
        event.add("dtstart", startTime)
        event.add("dtend", startTime + DT.timedelta(seconds=7200))

        cal.add_component(event)

    #print cal.to_ical()
    f = open(savePath, 'wb')
    f.write(cal.to_ical())
    f.close()

def getKeyValue(team):
    teamName = None
    url = None

    if team.name == "a":
        url = team.get("href")
        splittedUrl = url.split("/")
        teamName = splittedUrl[-1]

    return teamName, url

def getTeamList():
    res = {}
    url = "http://www.mendo.be/v2/4/"
    response = urllib2.urlopen(url)
    html = response.read()

    soup = BeautifulSoup(html)
    teamsDiv = soup.find("div", id="defaultBox")
    firstTeam = teamsDiv.find("a")
    key, value = getKeyValue(firstTeam)
    res[key] = value

    for sibling in firstTeam.next_siblings:
        key, value = getKeyValue(sibling)
        if key and value:
            res[key] = value

    return res


teams = getTeamList()
for k in teams:
    print "%s" % (k)
team = raw_input("Geef je team op: ")
schedule = getTeamSchedule(teams[team])
printTeamGames(schedule)
createIcal(schedule, "./"+ str(team) +".ics")
