import re
import time
from datetime import datetime
import urllib
import mechanicalsoup
import getpass
from bs4 import BeautifulSoup

# Conver Time Function
def convertTime(time):
    try:
        time = time.replace(",","").replace("@","").replace("."," ").replace(":"," ") 
        t2 = datetime.strptime(time[3:], "%A %B %d %Y %I %M%p")
        return (t2-datetime(1970,1,1)).total_seconds()
    except Exception:
        print ("Error while converting time to seconds")
        return 1

url = 'https://slashdot.org/'

# List Variables
outputList = []
article_headline_list = []
writer_list = []
time_posted_list = []
response = []

# Count Variables
totalRecords=0
totalRecordsOut=0
page=-1
timestamp=0
browser = mechanicalsoup.StatefulBrowser()

On_This_Page = False
logged_in = False

# Loop until logged in
browser.open(url)

while not logged_in:
    nick = input("Enter your nickname for slashdot.org: ") #Chazzio1
    passw = getpass.getpass("Enter your password: ")        #vBm5HbkA
    
    while(timestamp<1):
        try:
            timestamp = int(input("Enter timestamp in seconds since 1970: ")) # 1535241600
        except Exception:
            "Not a valid number"
    
    browser.select_form(nr=1)      
    browser['unickname'] = nick
    browser['upasswd'] = passw
    result = browser.submit_selected()
    response = result.content
 
    soup_0 = BeautifulSoup(response, "lxml")
    user = str(soup_0.find_all(class_="user-access"))

    if user.find(nick)>0:
        logged_in=True
        print ("Logged in")
    else:
        print ("Try Again\n")
    time.sleep(5)

# Loop until date found
while not(On_This_Page):
    page+=1
    try:
        browser.open(url)
    except Exception:
        print ("Error cannot open next page ")
        print ("Page " + url + " may not exist")
        browser.close()
        break
        #release resources
    
# HTML to BeautifulSoup
    response = ""
    response=result.content
    soup = ""
    soup = BeautifulSoup(response, "lxml")

# Find all Headlines
    article_headline = soup.find_all('span',class_="story-title")
    poster = soup.find_all('span', class_="story-byline")
    time_posted = soup.find_all('time')    

# Store all required info
    for headline in article_headline:
        title = '\"'+headline.a.get_text()+'\"'
        article_headline_list.append(title) #Get Text headline
        totalRecords+=1
    for t in time_posted:
        time_posted_list.append(convertTime(t.get("datetime"))) 
    for val in poster:
        writer = val.find(text=True)
        writer = " ".join(re.split("\s+", writer, flags=re.UNICODE))
        writer = writer.replace(' ', '')
        writer = writer.replace('Posted','')
        writer = writer.replace('by','')
        writer_list.append(writer)
        
# Make output List as per format required    
    for j in range(totalRecords):
        if (int(time_posted_list[j]) < timestamp):
            On_This_Page = True
            break
        else:
            outputList.append(str(
                "{" "\n" "\"headline\": ") + str(article_headline_list[j]) +
                "\n\"author\": \"" + str(writer_list[j]) + 
                "\"\n\"date\": " + str(int(time_posted_list[j])) + "\n},\n"
                )
            totalRecordsOut+=1;
    # All records on page within timeframe, open next page
    if totalRecordsOut%totalRecords == 0:
        totalRecordsOut=0
        url = str('https://slashdot.org/?page=')  + str(page+1)
        
        # Display this message while loading other pages
        print ("Opening next page " + url) 

for headline in outputList:
    print (headline)

print ("Total headlines returned: " + str(totalRecordsOut))
browser.close()    

