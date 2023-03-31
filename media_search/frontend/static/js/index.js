const API_QUERY = '/api/v1.1/query';
const API_CSV = '/api/v1.1/query/csv';
const BELLINGCAT_LINK = 'https://ukraine.bellingcat.com/';
const CENINFORES_LINK = 'https://eyesonrussia.org/'
const GEOCONFIRMED_LINK = 'https://geoconfirmed.org/ukraine'
const REUKRAINE_LINK = 'https://reukraine.shtab.net/'
const TEXTY_LINK = 'https://texty.org.ua/projects/107577/under-attack-what-and-when-russia-shelled-ukraine/'

const UKRAINE_CENTER = [48.356, 33.662];
const ZOOM_LEVEL = 5;

const resultsArea = document.getElementById('results');
const create = ((elm) => document.createElement(elm));
const insertFirst = ((parent, elm) => parent.insertBefore(elm, parent.children[0]));
const mapToSourceLink = (src) => {
  switch (src) {
    case 'BELLINGCAT':
      return `<a href="${BELLINGCAT_LINK}">Bellingcat</a>`
      break;
    case 'CENINFORES':
      return `<a href="${CENINFORES_LINK}">Centre for Information Resilience</a>`
      break;
    case 'GEOCONFIRMED':
      return `<a href="${GEOCONFIRMED_LINK}">@GeoConfirmed</a>`
      break;
    case 'REUKRAINE':
      return `<a href="${REUKRAINE_LINK}">reukraine.shtab.net</a>`
      break;
    case 'TEXTY':
      return `<a href="${TEXTY_LINK}">texty.org.ua</a>`
      break;
    default:
      return src
      break;
  }
}
const linkToIdentifier = (src, id) => {
  switch (src) {
    case 'BELLINGCAT':
      return `<a href="${BELLINGCAT_LINK}/?id=${id}">${id}</a>`
      break;
    case 'CENINFORES':
      return `${id}`
      break;
    case 'GEOCONFIRMED':
      return `<a href="${GEOCONFIRMED_LINK}/${id}">${id}</a>`
      break;
    case 'REUKRAINE':
      return `<a href="${REUKRAINE_LINK}detail/${id.replace('reukraine-', '')}">${id}</a>`
      break;
    case 'TEXTY':
      return `(no id)`
      break;
    default:
      return id
      break;
  }
}
const formatOSM = (loc) => {
  return `https://www.openstreetmap.org/?mlat=${loc.latitude}&mlon=${loc.longitude}#map=8/${loc.latitude}/${loc.longitude}`
}
const getLocation = (e) => {
  if (e.location) {
    return [
      `<a title="OpenStreetMaps link" href="${formatOSM(e.location)}">`,
      `[${e.location.latitude.slice(0, 10)}, ${e.location.longitude.slice(0, 10)}]</a>`,
      ` <button id="copy-button-${e.id}" title="Copy coordinates to clipboard" onClick="`,
      `navigator.clipboard.writeText('${e.location.latitude}, ${e.location.longitude}');`,
      ` this.textContent = 'copied!';`,
      `">copy coordinates</button>`,
      `${e.location.place_desc ? ' - ' + e.location.place_desc : ''}`,
    ].join('');
  }
  return 'n/a (or perhaps in description below)'
}

const visualizeMap = (results) => {
  let map = L.map('leaflet-map').setView(UKRAINE_CENTER, ZOOM_LEVEL);
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
  }).addTo(map);
  //console.log(results);
  // Collect all markers into a group in order to compute outer bounds
  var grp = new L.FeatureGroup();
  for (let url in results) {
    let entries = results[url];
    for (let key in entries) {
      let entry = entries[key];
      //console.log('entry');
      //console.log(entry);
      let lat = entry.location.latitude;
      let lng = entry.location.longitude;
      //let marker = L.marker([lat, lng]).addTo(map);
      let marker = L.marker([lat, lng]);
      grp.addLayer(marker);
      let popup = (
        `<b>DB: ${mapToSourceLink(entry.source)}</b>, ` +
        `ID: ${linkToIdentifier(entry.source, entry.id)} - ` +
        `${url}<br>` +
        `<b>Location:</b> ${getLocation(entry)}` +
        `${entry.location.place_desc ? ' - ' + entry.location.place_desc : ''}<br>` +
        `${entry.desc}`
      )
      marker.bindPopup(popup);
    }
  }
  grp.addTo(map);
  // Center and zoom the map on added markers
  map.fitBounds(grp.getBounds());
  // Zoom level should be at most the initial zoom level, i. e., not zoom in on objects too much
  map.setZoom(Math.min(map.getBoundsZoom(grp.getBounds()), ZOOM_LEVEL));
}

const insertResults = (results) => {
  // Clear any previous results
  resultsArea.textContent = '';

  const mapButton = () => {
    let _mapButton = create('button');
    _mapButton.id = 'map-button';
    _mapButton.textContent = 'Visualize results on map';
    _mapButton.addEventListener('click',
      (event) => {
        insertFirst(resultsArea, mapArea());
        visualizeMap(results);
        document.getElementById('map-button').remove();
      },
      false,
      // Remove button
    )
    return _mapButton;
  }

  const mapArea = () => {
    let mapDiv = create('div');
    mapDiv.id = 'leaflet-map';
    return mapDiv;
  }

  const formatEntry = (entry) => {
    let innerContainer = create('div');
    innerContainer.classList.add('result');
    let header = create('span');
    header.innerHTML =
      `Found entry in database of <b>${mapToSourceLink(entry.source)}</b>, `
      + `Identifier = <b>${linkToIdentifier(entry.source, entry.id)}</b>`;
    innerContainer.appendChild(header);
    let loc = create('div');
    loc.innerHTML = `<b>Location:</b> ${getLocation(entry)}`;
    innerContainer.appendChild(loc);
    let content = create('div');
    // Replace newlines with HTML linebreak tags
    let desc = entry.desc.replace(/\n/g, '<br>');
    content.innerHTML = desc;
    innerContainer.appendChild(content);
    return innerContainer;
  }
  const insertContainer = (url, entries) => {
    let container = create('div');
    container.classList.add('result-container');
    let header = create('h3');
    header.innerHTML = `<a href="https://${url}">${url}</a>`;
    container.appendChild(header);
    entries.forEach((entry) => {
      container.appendChild(formatEntry(entry));
    });
    resultsArea.appendChild(container);
  };

  resultsArea.appendChild(mapButton());

  Object.entries(results).forEach(([url, entries]) => {
    insertContainer(url, entries);
  });
}
const insertFailure = () => {
  resultsArea.textContent = 'URL not found in database';
}

// Adapted from:
// https://github.com/bellingcat/ukraine-timemap/blob/ad1ccc4fd3cf6f53c6fc36eb0a57ab04524b37da/src/common/utilities.js#L564-L578
const downloadAsFile = (filename, content) => {
  let elm = document.createElement('a');
  elm.setAttribute(
    'href',
    `data:application/octet-stream;charset=utf-8,${encodeURIComponent(content)}`
  );
  elm.setAttribute('download', filename);
  elm.style.display = "none";
  document.body.appendChild(elm);
  elm.click();
  document.body.removeChild(elm);
}

const submitSingleURL = (event) => {
  event.preventDefault();
  resultsArea.textContent = 'loading...';
  const resultFormat = document.querySelector('input[name=result_format]:checked').value;
  const url = document.getElementById('url').value;
  submitData(API_QUERY, JSON.stringify({'urls': [url,], 'format': resultFormat}), true, resultFormat);
}
const submitMultipleURLs = (event) => {
  event.preventDefault();
  resultsArea.textContent = 'loading...';
  const resultFormat = document.querySelector('input[name=result_format]:checked').value;
  const input = document.getElementById('urls').value;
  const urls = input.split(/[ ,\\\n'"]+/);
  submitData(API_QUERY, JSON.stringify({'urls': urls, 'format': resultFormat}), true, resultFormat);
}
const submitCSV = (event) => {
  event.preventDefault();
  resultsArea.textContent = 'loading...';
  const resultFormat = document.querySelector('input[name=result_format]:checked').value;
  const formdata = new FormData();
  const csvfile = document.getElementById('file').files[0];
  formdata.append('file', csvfile);
  formdata.append('format', resultFormat);
  submitData(API_CSV, formdata, false, resultFormat);
}
const submitData = (url, payload, json, resultFormat) => {
  const requestOptions = {
    method: 'POST', headers: json ? { 'Content-Type': 'application/json' } : {},
    body: payload
  };
  if (['json', 'csv'].includes(resultFormat)) {
    fetch(url, requestOptions)
      .then((resp) => resp.text())
      .then((response) => {
        resultsArea.textContent = '';
        downloadAsFile(`results.${resultFormat}`, response);
      })
      .catch((error) => {
        console.log(error)
        resultsArea.textContent = `Something went wrong. Technical information: ${error}`
      });
  } else {
    fetch(url, requestOptions)
      .then((resp) => resp.json())
      .then((response) => {
        if (response.success) {
          insertResults(response.dataset);
        } else {
          insertFailure();
        }
      })
      .catch((error) => {
        console.log(error)
        resultsArea.textContent = `Something went wrong. Technical information: ${error}`
      });
  }
}

const exampleQuery = (event) => {
  const urlElm = document.getElementById('url')
  const EXAMPLE_URL = 'https://t.me/truexanewsua/57093';
  urlElm.value = EXAMPLE_URL;
  submitSingleURL(event);
  // Remove sample text
  const elm = document.getElementById('example')
  elm.parentElement.removeChild(elm);
}

document.getElementById('url-field').onsubmit = submitSingleURL;
document.getElementById('textarea-field').onsubmit = submitMultipleURLs;
document.getElementById('file-field').onsubmit = submitCSV;

document.getElementById('example-query').addEventListener('click', exampleQuery, {once: true});

autosize(document.querySelector('textarea'));
