import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests
import sqlite3
import json
import numpy as np
import matplotlib.pyplot as plt


# deezer
def get_deezer():
    r = requests.get("https://api.deezer.com/chart/0?&output=json")
    data = r.text
    deezer = json.loads(data)
    return deezer


# spotify:
cid = "28678d88fa6b4267aaa4d49045c23920"
secret = "bd63a7354a6a4285a7d46bfb737daadb"

client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


# cur.execute("SELECT * FROM BILLBOARD_TOP")
# artist_dict = {}
# for row in cur:
#     artist = row[1]
#     artist_dict[artist] = artist_dict.get(artist, 0) + 1


conn = sqlite3.connect('Spotify_top.sqlite')
cur = conn.cursor()
cur.execute('DROP TABLE IF EXISTS Spotify_top')
cur.execute('CREATE TABLE Spotify_top(title TEXT, artist TEXT)')
for i in range(0,100,20):
    track_results = sp.search(q='year:2019', type='track', limit=20, offset=i)
    for i, t in enumerate(track_results['tracks']['items']):    
        __title = t['name'] 
        __artist = t['artists'][0]['name']
        cur.execute("INSERT INTO Spotify_top (title, artist) VALUES (?, ?)", (__title, __artist))
conn.commit()


# seperate doc?
conn = sqlite3.connect("Spotify_top.sqlite")
cur = conn.cursor()

cur.execute("SELECT * FROM Spotify_top")
spotify_artist_dict = {}
for row in cur:
    spotify_artist = row[1]
    spotify_artist_dict[spotify_artist] = spotify_artist_dict.get(spotify_artist, 0) + 1

with open('spotify_data.text', 'w') as outfile:
    json.dump(spotify_artist_dict, outfile) 

#Assign the x values to the keys of the dictionary and the y values to the values that correspond to those keys
y_values = spotify_artist_dict.keys()
x_values = spotify_artist_dict.values() 

#Plot the bar chart with xvals and yvals. Align the bars in center and assign a color to each bar.
index = np.arange(len(x_values))
plt.bar(index, x_values, align='center', width =1.0, color = ["green"])

#Give ylabel to the plot
plt.xlabel("Number of Songs on Spotify Top 100 by Artist")

#Give xlabel to the plot
plt.ylabel("Artist")

#Give the title to the plot
plt.title("Number of Hits on Spotify Top 100 by Artist") 

#Adjust the placement of the x-axis labels 
plt.xticks(index, y_values, rotation=90, fontsize = 4) 

#Save the plot as a .png file
plt.savefig("spotify_artists.png")

#Show the plot
plt.show()