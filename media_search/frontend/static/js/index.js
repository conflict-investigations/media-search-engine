const API_QUERY = '/api/v1.1/query';
const API_CSV = '/api/v1.1/query/csv';
const BELLINGCAT_LINK = 'https://ukraine.bellingcat.com/';
const CENINFORES_LINK = 'https://eyesonrussia.org/'
const GEOCONFIRMED_LINK = 'https://geoconfirmed.org/ukraine'
const REUKRAINE_LINK = 'https://reukraine.shtab.net/'
const TEXTY_LINK = 'https://texty.org.ua/projects/107577/under-attack-what-and-when-russia-shelled-ukraine/'

const results_area = document.getElementById('results');
const create = ((elm) => document.createElement(elm));
const mapToSourceLink = (src) => {
  switch (src) {
    case 'BELLINGCAT':
      return `<a href=${BELLINGCAT_LINK}>Bellingcat</a>`
      break;
    case 'CEN4INFORES':
      return `<a href=${CENINFORES_LINK}>Centre for Information Resilience</a>`
      break;
    case 'GEOCONFIRMED':
      return `<a href=${GEOCONFIRMED_LINK}>@GeoConfirmed</a>`
      break;
    case 'REUKRAINE':
      return `<a href=${REUKRAINE_LINK}>reukraine.shtab.net</a>`
      break;
    case 'TEXTY':
      return `<a href=${TEXTY_LINK}>texty.org.ua</a>`
      break;
    default:
      return src
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
const insertResults = (results) => {
  // Clear any previous results
  results_area.textContent = '';

  const formatEntry = (entry) => {
    let innerContainer = create('div');
    innerContainer.classList.add('result');
    let header = create('span');
    header.innerHTML =
      `Found entry in database of <b>${mapToSourceLink(entry.source)}</b>, `
      + `Identifier = <b>${entry.id}</b>`;
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
    results_area.appendChild(container);
  };
  Object.entries(results).forEach(([url, entries]) => {
    insertContainer(url, entries);
  });
}
const insertFailure = () => {
  results_area.textContent = 'URL not found in database';
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
  results_area.textContent = 'loading...';
  const resultFormat = document.querySelector('input[name=result_format]:checked').value;
  const url = document.getElementById('url').value;
  submitData(API_QUERY, JSON.stringify({'urls': [url,], 'format': resultFormat}), true, resultFormat);
}
const submitMultipleURLs = (event) => {
  event.preventDefault();
  results_area.textContent = 'loading...';
  const resultFormat = document.querySelector('input[name=result_format]:checked').value;
  const input = document.getElementById('urls').value;
  const urls = input.split(/[ ,\\\n'"]+/);
  submitData(API_QUERY, JSON.stringify({'urls': urls, 'format': resultFormat}), true, resultFormat);
}
const submitCSV = (event) => {
  event.preventDefault();
  results_area.textContent = 'loading...';
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
        results_area.textContent = '';
        downloadAsFile(`results.${resultFormat}`, response);
      })
      .catch((error) => {
        console.log(error)
        results_area.textContent = `Something went wrong. Technical information: ${error}`
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
        results_area.textContent = `Something went wrong. Technical information: ${error}`
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
