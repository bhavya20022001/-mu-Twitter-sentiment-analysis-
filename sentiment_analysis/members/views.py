from django.shortcuts import render,HttpResponse, redirect
import matplotlib.pyplot as plt
import matplotlib
from textblob import TextBlob
import sys,tweepy,csv,re
from django.views import View
import io, urllib.parse
import urllib, base64

matplotlib.use('Agg')
 
def index(req):
    args = {'image':False}
    return render(req, "index.html",args) 

def sentimentAnalysis(request):
    tweets=[]
    tweetText=[]
    
    if request.method=='POST':
        inputtext=request.POST['title']
        inputnumber=request.POST['record']

        return downloadData(request, inputnumber, inputtext, tweets, tweetText)

    
    return HttpResponse(request, "get method not allowed...")

def downloadData(request, inputnumber, inputtext, tweets, tweetText):
    
    consumerKey = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    consumerSecret = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    accessToken =  'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    accessTokenSecret = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
    auth.set_access_token(accessToken, accessTokenSecret)
    api = tweepy.API(auth)

    # input for term to be searched and how many tweets to search
    searchTerm = str(inputtext)
    NoOfTerms = int(inputnumber)

    # searching for tweets
    tweets = tweepy.Cursor(api.search_tweets, q=searchTerm, lang = "en").items(NoOfTerms)

    # Open/create a file to append data to
    csvFile = open('result.csv', 'a')

    # Use csv writer
    csvWriter = csv.writer(csvFile)

    # creating some variables to store info
    polarity = 0
    positive = 0
    wpositive = 0
    spositive = 0
    negative = 0
    wnegative = 0
    snegative = 0
    neutral = 0

    # iterating through tweets fetched
    for tweet in tweets:
            #Append to temp so that we can store in csv later. I use encode UTF-8
            tweetText.append(cleanTweet(tweet.text).encode('utf-8'))
            # print (tweet.text.translate(non_bmp_map))    #print tweet's text
            analysis = TextBlob(tweet.text)
            # print(analysis.sentiment)  # print tweet's polarity
            polarity += analysis.sentiment.polarity  # adding up polarities to find the average later      
            if (analysis.sentiment.polarity == 0):  # adding reaction of how people are reacting to find average later
                neutral += 1
            elif (analysis.sentiment.polarity > 0 and analysis.sentiment.polarity <= 0.3):
                wpositive += 1
            elif (analysis.sentiment.polarity > 0.3 and analysis.sentiment.polarity <= 0.6):
                positive += 1
            elif (analysis.sentiment.polarity > 0.6 and analysis.sentiment.polarity <= 1):
                spositive += 1
            elif (analysis.sentiment.polarity > -0.3 and analysis.sentiment.polarity <= 0):
                wnegative += 1
            elif (analysis.sentiment.polarity > -0.6 and analysis.sentiment.polarity <= -0.3):
                negative += 1
            elif (analysis.sentiment.polarity > -1 and analysis.sentiment.polarity <= -0.6):
                snegative += 1 

    # Write to csv and close csv file
    csvWriter.writerow(tweetText)
    csvFile.close()

    # finding average of how people are reacting
    positive = percentage(positive, NoOfTerms)
    wpositive = percentage(wpositive, NoOfTerms)
    spositive = percentage(spositive, NoOfTerms)
    negative = percentage(negative, NoOfTerms)
    wnegative = percentage(wnegative, NoOfTerms)
    snegative = percentage(snegative, NoOfTerms)
    neutral = percentage(neutral, NoOfTerms)

    # finding average reaction
    polarity = polarity / NoOfTerms

    # printing out data
    print("How people are reacting on " + searchTerm + " by analyzing " + str(NoOfTerms) + " tweets.")
    print()
    print("General Report: ")

    if (polarity == 0):
        print("Neutral")
    elif (polarity > 0 and polarity <= 0.3):
        print("Weakly Positive")
    elif (polarity > 0.3 and polarity <= 0.6):
        print("Positive")
    elif (polarity > 0.6 and polarity <= 1):
        print("Strongly Positive")
    elif (polarity > -0.3 and polarity <= 0):
        print("Weakly Negative")
    elif (polarity > -0.6 and polarity <= -0.3):
        print("Negative")
    elif (polarity > -1 and polarity <= -0.6):
        print("Strongly Negative")

    print()
    print("Detailed Report: ")
    print(str(positive) + "% people thought it was positive")
    print(str(wpositive) + "% people thought it was weakly positive")
    print(str(spositive) + "% people thought it was strongly positive")
    print(str(negative) + "% people thought it was negative")
    print(str(wnegative) + "% people thought it was weakly negative")
    print(str(snegative) + "% people thought it was strongly negative")
    print(str(neutral) + "% people thought it was neutral")

    return plotPieChart(request, positive, wpositive, spositive, negative, wnegative, snegative, neutral, searchTerm, NoOfTerms)

def cleanTweet(tweet):
    # Remove Links, Special Characters etc from tweet
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) | (\w +:\ / \ / \S +)", " ", tweet).split())

# function to calculate percentage
def percentage(part, whole):
    temp = 100 * float(part) / float(whole)
    return format(temp, '.2f')

def plotPieChart(request, positive, wpositive, spositive, negative, wnegative, snegative, neutral, searchTerm, noOfSearchTerms):
    labels = ['Positive [' + str(positive) + '%]', 'Weakly Positive [' + str(wpositive) + '%]','Strongly Positive [' + str(spositive) + '%]', 'Neutral [' + str(neutral) + '%]',
            'Negative [' + str(negative) + '%]', 'Weakly Negative [' + str(wnegative) + '%]', 'Strongly Negative [' + str(snegative) + '%]']
    sizes = [positive, wpositive, spositive, neutral, negative, wnegative, snegative]
    colors = ['yellowgreen','lightgreen','darkgreen', 'gold', 'red','lightsalmon','darkred']
    patches, texts = plt.pie(sizes, colors=colors, startangle=90)
    plt.legend(patches, labels, loc="best")
    plt.title('How people are reacting on ' + searchTerm + ' by analyzing ' + str(noOfSearchTerms) + ' Tweets.')
    plt.axis('equal') 

    # image process :

    buf=io.BytesIO()
    plt.savefig(buf,format='png' ) 
    buf.seek(0)
    string=base64.b64encode(buf.read())
    uri='data:image/png;base64,' + urllib.parse.quote(string)
    # breakpoint()
    # plt.show()
    plt.close()
    args = {'image':uri}
    return render(request, "index.html",args)


