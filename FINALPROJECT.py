requests = https://api.deezer.com/chart/0?&output=json


cur.execute("SELECT * FROM BILLBOARD_TOP")
artist_dict = {}
for row in cur:
    artist = row[1]
    artist_dict[artist] = artist_dict.get(artist, 0) + 1