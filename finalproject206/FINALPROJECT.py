import unittest
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests
import sqlite3
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import os
from wordcloud import WordCloud, STOPWORDS

# deezer
def get_deezer():
    r = requests.get("https://api.deezer.com/playlist/1313621735?&output=json")
    data = r.text
    deezer = json.loads(data)
    return deezer

def deezer_database(d, cur, conn):
    # conn = sqlite3.connect('deezer_top.sqlite')
    # cur = conn.cursor()
    # cur.execute('DROP TABLE IF EXISTS deezer_top')
    cur.execute('CREATE TABLE IF NOT EXISTS deezer_top(title TEXT UNIQUE, artist TEXT)')
    d = d["tracks"]["data"]
    deezer_artist_ids = []

    num = cur.execute("SELECT COUNT (*) FROM deezer_top")
    info = num.fetchall()[0][0]
    for i in range(info,info+20):
        title = d[i]["title"]
        artist = d[i]["artist"]["name"]
        if artist not in deezer_artist_ids:
            deezer_artist_ids.append(artist)
        cur.execute("INSERT OR IGNORE INTO deezer_top (title, artist) VALUES (?, ?)", (title, artist))

    cur.execute("CREATE TABLE IF NOT EXISTS Deezer_Artist_ids (id INTEGER PRIMARY KEY, artist TEXT, UNIQUE(id, artist))")
    num2 = cur.execute("SELECT COUNT (*) FROM Deezer_Artist_ids")
    info2 = num2.fetchall()[0][0]
    for i in range(info2, len(deezer_artist_ids)+info2):
        cur.execute("INSERT OR IGNORE INTO Deezer_Artist_ids (id,artist) VALUES (?,?)",(i,deezer_artist_ids[i-info2]))

    conn.commit()
    return deezer_artist_ids

def spotify_database(deezer_artist_ids, cur, conn):
# spotify:
    cid = "28678d88fa6b4267aaa4d49045c23920"
    secret = "bd63a7354a6a4285a7d46bfb737daadb"

    client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # conn = sqlite3.connect('Spotify_top.sqlite')
    # cur = conn.cursor()
    # cur.execute('DROP TABLE IF EXISTS Spotify_top')
    cur.execute('CREATE TABLE IF NOT EXISTS Spotify_top(title TEXT UNIQUE, artist TEXT)')
    num = cur.execute("SELECT COUNT (*) FROM Spotify_top")
    info = num.fetchall()[0][0]
    for i in range(info,info+11):
        songs = sp.search(q='year:2019', type='track', offset=i)
        for i, t in enumerate(songs['tracks']['items']):    
            __title = t['name'] 
            __artist = t['artists'][0]['name']
            cur.execute("INSERT OR IGNORE INTO Spotify_top (title, artist) VALUES (?, ?)", (__title, __artist))
            if __artist not in deezer_artist_ids:
                deezer_artist_ids.append(__artist)
    cur.execute("CREATE TABLE IF NOT EXISTS Spotify_Artist_ids (id INTEGER PRIMARY KEY, artist TEXT, UNIQUE(id, artist))")
    num2 = cur.execute("SELECT COUNT (*) FROM Spotify_Artist_ids")
    info2 = num2.fetchall()[0][0]
    for i in range(info2,len(deezer_artist_ids)+info2):
        cur.execute("INSERT OR IGNORE INTO Spotify_Artist_ids (id,artist) VALUES (?,?)",(i,deezer_artist_ids[i-info2]))

    conn.commit()

def make_spotify_data(cur, conn):
    
    cur.execute("SELECT * FROM Spotify_top")
    spotify_artist_dict = {}
    for row in cur:
        spotify_artist = row[1]
        spotify_artist_dict[spotify_artist] = spotify_artist_dict.get(spotify_artist, 0) + 1
    
    spotify_artist_dict = sorted(spotify_artist_dict.items(), key=lambda item:item[1], reverse=True)

    with open('spotify_data.text', 'w') as outfile:
        json.dump(spotify_artist_dict, outfile)
    
    return spotify_artist_dict

def make_graph_spotify(cur, conn):

    spotify_artist_dict = make_spotify_data(cur, conn)
    new_dict = {}
    for item in spotify_artist_dict:
        new_dict[item[0]] = item[1]

#Assign the x values to the keys of the dictionary and the y values to the values that correspond to those keys
    x_values = new_dict.keys()
    y_values = new_dict.values() 

#Plot the bar chart with xvals and yvals. Align the bars in center and assign a color to each bar.
    index = np.arange(len(x_values))
    plt.bar(index, y_values, align='center', width =2.0, color = ["green"])

#Give ylabel to the plot
    plt.ylabel("Number of Songs on Spotify Top 100 by Artist")

#Give xlabel to the plot
    plt.xlabel("Artist")

#Give the title to the plot
    plt.title("Number of Hits on Spotify Top 100 by Artist") 

#Adjust the placement of the x-axis labels 
    plt.xticks(index, x_values, rotation=90, fontsize = 4) 


#Save the plot as a .png file
    plt.savefig("spotify_artists.png")

# Show the plot
    plt.show()

def make_deezer_data(cur, conn):

    cur.execute("SELECT * FROM deezer_top")
    deezer_dict = {}
    for row in cur:
        deezer_artist = row[1]
        deezer_dict[deezer_artist] = deezer_dict.get(deezer_artist, 0) + 1
    deezer_dict = sorted(deezer_dict.items(), key=lambda item:item[1], reverse=True)

    with open('deezer_data.text', 'w') as outfile:
        json.dump(deezer_dict, outfile) 

    return deezer_dict

def deezer_artists_count(cur, conn):
    deezer = make_deezer_data(cur, conn)
    print(deezer)
    cur.execute("CREATE TABLE IF NOT EXISTS Deezer_Artist_Count (count INTEGER PRIMARY KEY, artist TEXT UNIQUE)")
    #why is this not adding anything to the database? everything is in deezer, but it doesn't add to table.
    for i in range(0, len(deezer)):
        cur.execute("INSERT OR REPLACE INTO Deezer_Artist_Count (count, artist) VALUES (?,?)",(deezer[i][1],deezer[i][0]))

def make_graph_deezer(cur, conn):
#deezer graph
    deezer_dict = make_deezer_data(cur, conn)
    new_dict = {}
    for item in deezer_dict:
        new_dict[item[0]] = item[1]
#Assign the x values to the values of the dictionary and the y values to the keys that correspond
    x_values = new_dict.keys()
    y_values = new_dict.values() 

#Plot the bar chart with x & y. Align the bars in center and make bars green.
    index = np.arange(len(x_values))
    plt.bar(index, y_values, align='center', width =2.0, color = ["magenta"])

#Give ylabel to the plot
    plt.xlabel("Artist")

#Give xlabel to the plot
    plt.ylabel("Number of Songs on Deezer Top 100 by Artist")

#Give the title to the plot
    plt.title("Number of Hits on Deezer Top 100 by Artist") 

#Adjust the placement of the x-axis labels 
    plt.xticks(index, x_values, rotation=90, fontsize = 4) 

#Save the plot as a .png file
    plt.savefig("deezer_artists.png")

# Show the plot
    plt.show()

def word_cloud_deezer(cur, conn):

    #turn list of tuples into list of artists without whitespace
    deezer_dict = make_deezer_data(cur, conn)
    new_list_deezer = []
    for item in deezer_dict:
        newname = item[0].replace(" ", "")
        new_list_deezer.append(newname)

    #create wordcloud & show & save
    wc = WordCloud(max_words=1000, margin=10, background_color='white', scale=3, relative_scaling = 0.5, width=500, height=400, random_state=1).generate(' '.join(new_list_deezer))
    plt.figure(figsize=(20,10))
    plt.imshow(wc)
    plt.axis("off")
    plt.show()
    path = os.path.dirname(os.path.abspath(__file__))
    wc.to_file(path+"/wordcloud_deezer.png")

def word_cloud_spotify(cur, conn):

    #turn list of tuples into list of artists without whitespace
    spotify_dict = make_spotify_data(cur, conn)
    new_list_spotify = []
    for item in spotify_dict:
        newname = item[0].replace(" ", "")
        new_list_spotify.append(newname)

    #create wordcloud & show & save
    wc = WordCloud(max_words=1000, margin=10, background_color='white', scale=3, relative_scaling = 0.5, width=500, height=400, random_state=1).generate(' '.join(new_list_spotify))
    plt.figure(figsize=(20,10))
    plt.imshow(wc)
    plt.axis("off")
    plt.show()
    path = os.path.dirname(os.path.abspath(__file__))
    wc.to_file(path+"/wordcloud_spotify.png")

def main():

    deezer_data = get_deezer()
    conn = sqlite3.connect("data.sqlite")
    cur = conn.cursor()

    db = deezer_database(deezer_data, cur, conn)
    spotify_database(db, cur, conn)

    make_graph_spotify(cur, conn)
    make_graph_deezer(cur, conn)

    word_cloud_deezer(cur, conn)
    word_cloud_spotify(cur, conn)
    deezer_artists_count(cur, conn)

if __name__ == "__main__":
    main()
    unittest.main(verbosity = 2)
