import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import bs4
import requests
import html
import urllib
import time
from sklearn.preprocessing import MinMaxScaler
import math
from datetime import datetime

# contacts the senate.gov website
# and scrapes all the Senate votes
# which are saved in senate_votes_raw.csv
def scrape_votes():
    vote_no = 0
    correct_load = True
    vote_frame = pd.DataFrame() # initializing this just to try to fix an error
    while correct_load:
        
        vote_no += 1

        # build url
        if vote_no >= 1 and vote_no <= 9:
            getVars = {'congress': '117', 'session': "1", "vote" : ("0000" + str(vote_no))}
        elif vote_no >= 9 and vote_no <= 100:
            getVars = {'congress': '117', 'session': "1", "vote" : ("000" + str(vote_no))}
        elif vote_no > 100:
            getVars = {'congress': '117', 'session': "1", "vote" : ("00" + str(vote_no))}

        url = 'https://www.senate.gov/legislative/LIS/roll_call_lists/roll_call_vote_cfm.cfm?'

        # get site
        website = requests.get((url + urllib.parse.urlencode(getVars)))
        soup = BeautifulSoup(website.content, 'html.parser')

        # collect votes from site
        sen_votes = []
        votes = []

        try:
            # grab the vote report from html
            spans = soup.find_all('span', {'class' : 'contenttext'})
            span = spans[0]
            
            for x in span:
                if type(x) == bs4.NavigableString:
                    if x != "\n":
                        sen_votes.append(x.replace(', ', ''))

                elif type(x) == bs4.Tag:
                    if x.text != '':
                        votes.append(x.text)


            if vote_no == 1:
                    res = {sen_votes[i]: votes[i] for i in range(len(sen_votes))}
                    vote_frame = pd.DataFrame([res])
            else:
                res = {sen_votes[i]: votes[i] for i in range(len(sen_votes))}
                vote_frame = vote_frame.append(res, ignore_index = True)
        except:
            correct_load = False
            
        print("scraped vote " + str(vote_no))
        time.sleep(15) # prevents the site from blocking us via a timeout

    vote_frame.T.to_csv("senate_votes_raw.csv")

# a helper function that
# parses a senator's name of the format:
# LastName (Party-State)
# into individual pieces
def get_senator_info(sen_string):
    state = sen_string[-3:-1]
    party = sen_string[-5]
    name = sen_string.partition(" ")[0]
    
    return name, party, state

# takes the raw csv created by
# scrape_votes and processes it
# to get individual senator scores
def score_senators():

    # load the data
    votes = pd.read_csv("senate_votes_raw.csv")
    votes.index = votes["Unnamed: 0"]
    del votes["Unnamed: 0"]
    votes

    # map the data to numerical values
    for x in range(votes.shape[1]):
        votes[str(x)] = votes[str(x)].map({"Nay" : -1, "Yea" : 1, "Not Voting" : 0, np.nan : 0})

    # parse each senator's name into relevant pieces
    senator_details = []

    for x in range(len(votes)):
        name = votes.index[x]
        name, party, state = get_senator_info(name)
        senator_details.append([name, party, state])

    senator_details = pd.DataFrame(senator_details, index = votes.index, columns = ["Name", "Party", "State"])

    # a list for each vote result
    dem_yes_votes = []
    dem_no_votes = []
    gop_yes_votes = []
    gop_no_votes = []


    # count party affiliations for each vote
    for x in range(votes.shape[1]):
        # each senator
        
        # declare counts
        dem_yes = 0
        dem_no = 0
        gop_yes = 0
        gop_no = 0
        
        for y in range(votes.shape[0]):
            
            party = senator_details[senator_details.index == votes.index[y]].values[0][1]
            vote = votes.iloc[y,x]
            
            if party == "D":
                if vote == 1:
                    dem_yes += 1
                elif vote == -1:
                    dem_no += 1
                    
            elif party == "R":
                if vote == 1:
                    gop_yes += 1
                elif vote == -1:
                    gop_no += 1
        
        dem_yes_votes.append(dem_yes)
        dem_no_votes.append(dem_no)
        gop_yes_votes.append(dem_yes)
        gop_no_votes.append(gop_no)
        
    vote_summary = pd.DataFrame(data = [dem_yes_votes, dem_no_votes, gop_yes_votes, gop_no_votes], index = ["Dem Yes", "Dem No", "GOP Yes", "GOP No"])

    # score each senator
    sen_scores = []

    for x in range(votes.shape[0]):
        senator = senator_details.iloc[x,:]
        sen_score = 0
        for y in range(votes.shape[1]):
            
            vote = votes.iloc[x,y]
            
            dem_yes = vote_summary.iloc[0,y]
            dem_no = vote_summary.iloc[1,y]
            gop_yes = vote_summary.iloc[2,y]
            gop_no = vote_summary.iloc[3,y]
            
            increment_val = .0001
            
            if gop_yes == 0:
                gop_yes += increment_val
            if gop_no == 0:
                gop_no += increment_val
            if dem_yes == 0:
                dem_yes += increment_val
            if dem_no == 0:
                dem_no += increment_val
                
            if vote == 1:
                if gop_yes > dem_yes:
                    sen_score += math.log((gop_yes / dem_yes), 10)
                elif gop_yes < dem_yes:
                    sen_score += math.log((dem_yes / gop_yes), 10) * -1
            elif vote == -1:
                if gop_no > dem_no:
                    sen_score += math.log((gop_no / dem_no), 10)
                elif gop_no < dem_no:
                    sen_score += math.log((dem_no / gop_no), 10) * -1
        
        sen_scores.append(sen_score)

    # add scores to the data frame
    # and map scores to range 0,1
    senator_details["score"] = sen_scores
    minmax = MinMaxScaler().fit(senator_details["score"].values.reshape(-1,1))
    senator_details["score"] = minmax.transform(senator_details["score"].values.reshape(-1,1))
    senator_details.to_csv("senate_partisanship_scores.csv")

def main():
    scrape_votes()
    score_senators()

    # output completion to logs
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Script completed at: ", current_time)


if __name__ == "__main__":
    main()



    
