# Media search engine

Check whether a (social) media post already exists in several databases (e.g.
Belllingcat's, Cen4InfoRes).

### Usage

```sh
# Print all URLs in all databases
python check.py -p
# Seach for a specific URL
python check.py <url>
```

### Example
```sh
$ python check.py 'https://twitter.com/RedIntelPanda/status/1488569554028707847'

Found URL https://twitter.com/RedIntelPanda/status/1488569554028707847 in 'CEN4INFORES' dataset
Id: None
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
