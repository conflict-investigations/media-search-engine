const API_QUERY = '/api/v1/query';
const BELLINGCAT_LINK = 'https://ukraine.bellingcat.com/';
const CENINFORES_LINK = 'https://maphub.net/Cen4infoRes/russian-ukraine-monitor'

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
      `[${e.location.latitude}, ${e.location.longitude}]</a>`,
      ` <button title="Copy coordinates to clipboard" onClick="`
      + `navigator.clipboard.writeText('${e.location.latitude}, ${e.location.longitude}')`,
      `">copy</button>`,
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

const submitSingleURL = (event) => {
  event.preventDefault();
  results_area.textContent = 'loading...';
  const url = document.getElementById('url').value;
  submitData(JSON.stringify({'urls': [url,]}), true);
}
const submitMultipleURLs = (event) => {
  event.preventDefault();
  results_area.textContent = 'loading...';
  const input = document.getElementById('urls').value;
  const urls = input.split(/[ ,\\\n'"]+/);
  submitData(JSON.stringify({'urls': urls}), true);
}
const submitCSV = (event) => {
  event.preventDefault();
  results_area.textContent = 'loading...';
  const formdata = new FormData();
  const csvfile = document.getElementById('file').files[0];
  formdata.append('file', csvfile);
  submitData(formdata, false);
}
const submitData = (payload, json) => {
  const requestOptions = {
    method: 'POST', headers: json ? { 'Content-Type': 'application/json' } : {},
    body: payload
  };
  fetch(API_QUERY, requestOptions)
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

const exampleQuery = (event) => {
  const urlElm = document.getElementById('url')
  const EXAMPLE_URL = 'https://twitter.com/RALee85/status/1497853526881546241';
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
