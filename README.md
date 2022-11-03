![quick n' dirty cool plane alert logo](assets/cool_plane_alert.jpg)
# cool-plane-alert
Small tool to voice an alert when a cool plane is nearby, 

Cool-plane-alert exists to solve a single problem: by the time I hear a neat plane overhead, grab my camera, and slip outside, the plane has typically already passed me by. I've been trying to check off planes off my planespotting list, so this doesn't do-- I needed something to let me know if a neat plane was nearby, so that I could have my camera ready to make the spot and snap a pic.

Cool-plane-alert vocally alerts you to nearby planes. It can filter for civilian or military aircraft within any distance <25nm. 

## Requirements
* x86 Linux
* ADS-B paid or X-Plane API key.
* Python 3.7 -> 3.9
* System installation of Larynx

___ 
## Installation:

1. Install [Larynx](https://github.com/rhasspy/larynx). Use pre-built Debian package.
2. Clone this repo
3. Download latest 'aircraft-database-complete-yyyy-mm.csv' from OpenSky. Extract into /assets.
4. Make venv from requirements.txt
5. Insert your, location & API key, aircraft database filename, and other params into config-sample.yml. Save as config.yml.
6. Run main.py.
7. cool-plane-alert will announce when a cool plane is nearby! Ready your camera..

## Known issues:
- [ ] Some aircraft model pronunciations are incorrect-- ex. "Boeing seven hundred and thirty-seven" rather than "Boeing seven-thirty-seven"
- [ ] You may have trouble decoding OpenSky database, depending on your host environment. I'm working on something more reliable. Until then, opening the CSV with a tabular data app (e.g. [Tad](https://www.tadviewer.com/)) and exporting the table back out ameliorates the issue.

## Future:

- [ ] Pre-packaged docker installation
- [ ] Automatic location detection
- [ ] Raspberry Pi support 
- [ ] Trajectory prediction, so that you can only receive alerts for planes which will pass overhead.
- [ ] More filtering options: airframe age, airframe types, etc. Open an issue to suggest more.
- [ ] More complete aircraft database. Many military airframes cannot be found in OpenSky via ICAO or registration no., but are still identified on ADS-B Exchange.