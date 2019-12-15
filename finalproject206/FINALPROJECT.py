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

    cur.execute('CREATE TABLE IF NOT EXISTS deezer_top(title TEXT UNIQUE, artist TEXT)')
    d = d["tracks"]["data"]

    num = cur.execute("SELECT COUNT (*) FROM deezer_top")
    info = num.fetchall()[0][0]
    for i in range(info,info+20):
        title = d[i]["title"]
        artist = d[i]["artist"]["name"]
        cur.execute("INSERT OR IGNORE INTO deezer_top (title, artist) VALUES (?, ?)", (title, artist))

    conn.commit()

def spotify_database(cur, conn):
# spotify:
    cid = "28678d88fa6b4267aaa4d49045c23920"
    secret = "bd63a7354a6a4285a7d46bfb737daadb"

    client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    cur.execute('CREATE TABLE IF NOT EXISTS Spotify_top(title TEXT UNIQUE, artist TEXT)')
    num = cur.execute("SELECT COUNT (*) FROM Spotify_top")
    info = num.fetchall()[0][0]
    for i in range(info,info+11):
        songs = sp.search(q='year:2019', type='track', offset=i)
        for i, t in enumerate(songs['tracks']['items']):    
            __title = t['name'] 
            __artist = t['artists'][0]['name']
            cur.execute("INSERT OR IGNORE INTO Spotify_top (title, artist) VALUES (?, ?)", (__title, __artist))
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

    x_values = new_dict.keys()
    y_values = new_dict.values() 
    index = np.arange(len(x_values))
    plt.bar(index, y_values, align='center', width =2.0, color = ["green"])
    plt.ylabel("Number of Songs on Spotify Top 100 by Artist")
    plt.xlabel("Artist")
    plt.title("Number of Hits on Spotify Top 100 by Artist") 
    plt.xticks(index, x_values, rotation=90, fontsize = 4) 
    plt.savefig("spotify_artists.png")
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
    cur.execute("CREATE TABLE IF NOT EXISTS Deezer_Artist_Count (count INTEGER, artist TEXT PRIMARY KEY UNIQUE)")
    for i in range(0, len(deezer)):
        try:
            cur.execute("INSERT OR REPLACE INTO Deezer_Artist_Count (count, artist) VALUES (?,?)",(deezer[i][1],deezer[i][0]))
        except:
            print("bad")
    conn.commit()

def spotify_artists_count(cur, conn):
    spotify = make_spotify_data(cur, conn)
    cur.execute("CREATE TABLE IF NOT EXISTS Spotify_Artist_Count (count INTEGER, artist TEXT PRIMARY KEY UNIQUE)")
    for i in range(0, len(spotify)):
        try:
            cur.execute("INSERT OR REPLACE INTO Spotify_Artist_Count (count, artist) VALUES (?,?)",(spotify[i][1],spotify[i][0]))
        except:
            print("bad")
    conn.commit()

def join_counts(cur, conn):
    cur.execute("SELECT Spotify_Artist_Count.count, Spotify_Artist_Count.artist, Deezer_Artist_Count.count, Deezer_Artist_Count.artist FROM Spotify_Artist_Count LEFT JOIN Deezer_Artist_Count ON Spotify_Artist_Count.artist=Deezer_Artist_Count.artist UNION ALL SELECT Deezer_Artist_Count.count, Deezer_Artist_Count.artist, Spotify_Artist_Count.count, Spotify_Artist_Count.artist FROM Deezer_Artist_Count LEFT JOIN Spotify_Artist_Count ON Deezer_Artist_Count.artist=Spotify_Artist_Count.artist")
    file = open("total_counts.txt", "w")
    file.write("Artists and their # hits total on Spotify and Deezer's top 100 combined\n")
    for row in cur.fetchall():
        if not (row[0] and row[2]):
            if (row[0]):
                sentence = (str(row[1]) + " is only in one of the top 100 lists, with " + str(row[0]) + " hits.")
                file.write("{} \n".format(sentence))
        else:
            total_hits = row[0] + row[2]
            sentence = (str(row[1]) + " has " + str(total_hits) + " total hits on Spotify and Deezer's top 100 hits combined.")
            file.write("{} \n".format(sentence))

def make_graph_deezer(cur, conn):
#deezer graph
    deezer_dict = make_deezer_data(cur, conn)
    new_dict = {}
    for item in deezer_dict:
        new_dict[item[0]] = item[1]
    x_values = new_dict.keys()
    y_values = new_dict.values() 
    index = np.arange(len(x_values))
    plt.bar(index, y_values, align='center', width =2.0, color = ["magenta"])
    plt.xlabel("Artist")
    plt.ylabel("Number of Songs on Deezer Top 100 by Artist")
    plt.title("Number of Hits on Deezer Top 100 by Artist") 
    plt.xticks(index, x_values, rotation=90, fontsize = 4) 
    plt.savefig("deezer_artists.png")
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

    deezer_database(deezer_data, cur, conn)
    spotify_database(cur, conn)

    deezer_artists_count(cur, conn)
    spotify_artists_count(cur, conn)
    join_counts(cur, conn)

    make_graph_spotify(cur, conn)
    make_graph_deezer(cur, conn)

    word_cloud_deezer(cur, conn)
    word_cloud_spotify(cur, conn)

if __name__ == "__main__":
    main()
    unittest.main(verbosity = 2)
