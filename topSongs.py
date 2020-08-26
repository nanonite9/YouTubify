import json
import requests
import os
import youtube_dl
import google_auth_oauthlib.flow
import googleapiclient.discovery
from secrets import spotify_user_id
from secrets import spotify_token

class TopSongs:
    def __init__(self):
        self.user_id = spotify_user_id
        self.youtube_client = self.ytClient()
        self.spotify_token = spotify_token
        self.data_track = {}

    def ytClient(self):
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1'"

        api_service_name = "youtube"
        api_version = "v3"
        client_secret = "config/client_secret.json"

        scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secret(client_secret, scopes)
        credentials = flow.run_console()

        youtube_client = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)

        return youtube_client
        
    def spotifyUri(self, track, artist):
        query = "https://api.spotify.com/v1/artists/1vCWHaC5f2uS3yhpwWbIA6/albums?album_type=SINGLE&offset=20&limit=10".format(track,artist)
        response = requests.get(
            query,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer{}".format(self.spotify_token)
            }
        )

        response_json = response.json()
        tracks = response_json["tracks"]["items"]
        uri = tracks[0]["uri"]
        return uri

    def newPlaylist(self):
        info_request = json.dumps({
            "name": "MisbehavedRabbit",
            "description": "My fave Bad Bunny tracks!",
            "public": False
        })

        query = "https://api.spotify.com/v1/users/{}/playlists".format(spotify_user_id)
        response = requests.post(
             query,
             data=info_request,
             headers={
                 "Content-Type": "application/json",
                 "Authorization": "Bearer{}".format(spotify_token)
             } 
         )
        response_json = response.json()
        return response_json["id"]

    def likedFromArtist(self):
        request = self.youtube_client.videos().list(part="snippet,contentDetails,statistics", myRating="like"   )
        response = request.execute()

        for item in response["items"]:
            video_title = item["snippet"]["title"]
            youtube_url = "https://youtube.com/watch?v={}".format(item["id"])

            video = youtube_dl.YoutubeDL({}).extract_data(youtube_url, download=False)
            track=video["track"]
            artist=video["Bad Bunny"]

            self.data_track[video_title] = {
                "youtube_url": youtube_url,
                "track": track,
                "artist": artist,
                "spotify_uri":self.spotifyUri(track,artist)

            }

    def newEntry(self):
        self.likedFromArtist()
        uris = []
        for track, data in self.data_track.items():
            uris.append(data["spotify_uri"])

        playlist_id = self.newPlaylist()
        data_request = json.dumps(uris)
        query = "https://api.spotify.com/v1/playlists/{}/playlists".format(playlist_id)

        response = requests.post(
            query,
            data=data_request,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(self.spotify_token)
            }
        )

        response_json = response.json()
        return response_json

    if __name__ == '__main__':
        np = newPlaylist()
        np.newEntry()