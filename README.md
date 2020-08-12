# interchange-tunes
A tool to move your music from itunes to spotify

## Setup

Go to itunes, and select the playlist you want to transfer to spotify

Do: ```File > Library > Export Playlist```

Make sure to export as XML

Head over to the [spotify developer console](https://developer.spotify.com/dashboard/login) and get credentials

Edit ```run.sh``` with your info

## Usage

Running it is as simple as using the script

```sh run.sh```

At the end it will tell you which tracks it couldn't add. With my playlists it was able to transfer around 95% of the tracks
