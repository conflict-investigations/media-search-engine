# OSINT Geolocation Databases Search

Check whether a (social) media post already exists and has been geolocated in
several databases (e.g. Belllingcat's, Cen4InfoRes, GeoConfirmed).

---

Use it **live:** [Geolocation Databases Search](https://t.co/jnGTOLEuaG)

---

*Now with visualization on a map via [leaflet.js](https://leafletjs.com/)*

Has both a **simple web UI** as well as an **API** and a **command-line client**.

### Installation

Requires Python, `pip` and the `flask` package (the CLI can be used without
`flask`).
For data extraction, the
[osint-geo-extractor](https://pypi.org/project/osint-geo-extractor/) library is
used.

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

# Print URLs as JSON
media_search -j
# Seach for a specific URL
media_search <url>
```

### Obtaining data
The `Belllingcat` database is from their
[Civilian Harm in Ukraine](https://ukraine.bellingcat.com/) project.
There's an "Export to JSON" button.

The `Cen4InfoRes` database is from the Center for Information Resilience's
[Eyes on Russia map](https://eyesonrussia.org/).

The `GeoConfirmed` database is from the
[GeoConfirmed map](https://geoconfirmed.org/ukraine).
*Note: Currently not working due to data format change*

The `Reukraine` database is from [reukraine.shtab.net](https://reukraine.shtab.net).
*Note: Beta status, currently not publicly available.*

The `Texty` database is from
[Texty.org.ua](https://texty.org.ua/projects/107577/under-attack-what-and-when-russia-shelled-ukraine/).
with kind permission from the authors.

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
- `/api/v1.1/export` - `GET` - Export all URLs as JSON
- `/api/v1.1/query` - `GET`/`POST` - Check if URL is in a database  
  **params**:
  - `urls`: List of urls to search (as `POST` JSON body array of strings or
    comma-separated `GET` argument)
  - `format`: `text`, `json` or `csv` - Show results in web UI (`text`) or force
    downloading as `results.json` or `results.csv` file

  **response:**
  ```json
  {
    "dataset": {
      "t.me/truexanewsua/57093": [
        {
          "desc": "2022-08-15 - A naval mine exploded...",
          "id": "UW11823",
          "location": {
            "latitude": "46.0552",
            "longitude": "30.443433",
            "place_desc": "Ukraine - Odessa Oblast - Zatoka"
          },
          "source": "CENINFORES",
          "unsanitized_url": "https://t.me/truexanewsua/57093"
        }
      ],
      "twitter.com/foo/bar": ["..."],
      "baz/bar": ["..."],
    },
    "message": "Success! Url found in database",
    "success": true
  }
  ```
  If the entry as not found, `success` is `false`.
- `/api/v1.1/query/csv` - `POST` - Check all links in uploaded `.csv` file  
  **params:** File as `POST` form data named `file`

**curl example:**  
```
# POST
curl 'http://localhost:8000/api/v1.1/query' \
    -X POST \
    -H 'Content-Type: application/json' \
    --data-raw '{"urls":["https://twitter.com/RALee85/status/1497853526881546241"]}'
# GET
curl 'http://localhost:8000/api/v1.1/query?\
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

# Prior Art

See also
[atlos.org](https://atlos.notion.site/Platform-Overview-46d4723f22ef420fb5ad0e07feba8d79),
which tries to do something quite similar, but it seems it's mostly used for
closed investigations.

The Centre for Information Resilience has also recently intensified efforts to
integrate other sources into their [map](https://eyesonrussia.org/), so the
utility of this tool, which was always intended to be transitional, is shrinking
further.

# LICENSE
Copyright 2022-2023 conflict-investigations Team.
Licensed under [MIT License](https://mit-license.org/)

[autosize](https://www.jacklmoore.com/autosize/) library by Jack Moore, MIT.

[leaflet](https://leafletjs.com/) for maps, licensed 2-clause BSD:

> Copyright (c) 2010-2023, Volodymyr Agafonkin  
> Copyright (c) 2010-2011, CloudMade

Marker favicon by [Leaflet project](https://leafletjs.com/), Copyright (c) 2010-2022, Vladimir Agafonkin
