# OSINT Geolocation Databases Search

Check whether a (social) media post already exists and has been geolocated in
several databases (e.g. Belllingcat's, Cen4InfoRes, GeoConfirmed).

Has both a **simple web UI** as well as an **API** and a **command-line client**.

### Installation

Requires Python, `pip` and the `flask` package (the CLI can be used without
`flask`).

```console
virtualenv .venv
.venv/bin/activate
pip install -e .
```

### Usage

**Command line**
```console
# Before first run: Download necessary files
media_search -o
# Dump data into pre-formatted database so the web API can use it.
media_search -d

# Print all URLs in all databases
media_search -p
# Print URLs as JSON
media_search -j
# Seach for a specific URL
media_search <url>
# Load data from pre-formatted database on disk instead of loading the huge
# database files themselves
media_search -l
```

### Obtaining data
The `Belllingcat` database is from their
[Civilian Harm in Ukraine](https://ukraine.bellingcat.com/) project.
There's an "Export to JSON" button.

The `Cen4InfoRes` database is from the Center for Information Resilience's
[Eyes on Russia map](https://maphub.net/Cen4infoRes/russian-ukraine-monitor).

The `GeoConfirmed` database is from the
[GeoConfirmed map](https://geoconfirmed.azurewebsites.net/).

The `media_search -o` command will download the data on your behalf and put it
into a `data/` folder.

### API & Web UI
There's a simple `flask` application with a plain HTML+JS frontend.

The API part requires you to do a dump of the pre-formatted database beforehand.
Run `media_search -d` before you start the API server.

Run the server:
```console
$ flask --app 'media_search.web' run --port 8000
```

By default, the server will run on `http://localhost:8000/`. It is not
recommended to run a `flask` development server in production.

Use e.g. [gunicorn](https://flask.palletsprojects.com/en/2.2.x/deploying/gunicorn/):
```console
$ gunicorn -w 2 media_search.web:app'
```

**Available routes**

- `/`: Web UI
- `/api/v1/export` - `GET` - Export all URLs as JSON
- `/api/v1/query` - `GET`/`POST` - Check if URL is in a database  
  **params**: `urls`: List of urls to search (as `POST` JSON body or
  comma-separated `GET` argument)  
  **response:**
  ```json
  {
    "dataset": [
      {
        "desc": "ENTRY: UW[...]", 
        "id": "UW13293", 
        "source": "CEN4INFORES"
      }
    ], 
    "message": "Success! Url found in database", 
    "success": true
  }
  ```
  If the entry as not found, `success` is `false`.

**curl example:**  
```
# POST
curl 'http://localhost:8000/api/v1/query' \
    -X POST \
    -H 'Content-Type: application/json' \
    --data-raw '{"urls":["https://twitter.com/RALee85/status/1497853526881546241"]}'
# GET
curl 'http://localhost:8000/api/v1/query?\
    urls=https://twitter.com/RALee85/status/1497853526881546241,\
         https://twitter.com/GeoConfirmed/status/1508518239567065090'
```

**Web UI screenshot:**

![webui](./webui.png)


### Example
```console
$ media_search 'https://twitter.com/RedIntelPanda/status/1488569554028707847'

Found URL https://twitter.com/RedIntelPanda/status/1488569554028707847 in 'CEN4INFORES' dataset
Id: UW0067
Description:

DATE:  01/01/2022
LINK: https://twitter.com/GirkinGirkin/status/1488544876908187650
GEOLOCATION: https://twitter.com/RedIntelPanda/status/1488569554028707847
BRIEF DESCRIPTION: Russian military equipment moving in Belarus
COUNTRY: Belarus
PROVINCE: 
DISTRICT: 
TOWN/CITY: Petrishki
COORDINATES: 54.069385, 27.211645
ARMS/MUNITION: 
VIOLENCE LEVEL: 1
ENTRY: UW0067
```

# LICENSE
Copyright 2022 conflict-investigations Team.
Licensed under [MIT License](https://mit-license.org/)

[autosize](https://www.jacklmoore.com/autosize/) library by Jack Moore, MIT.

Marker favicon by [Leaflet project](https://leafletjs.com/), Copyright (c) 2010-2022, Vladimir Agafonkin
