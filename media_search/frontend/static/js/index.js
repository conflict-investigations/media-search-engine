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
      return `<a href=${CENINFORES_LINK}>Center for Information Resilience</a>`
      break;
    default:
      return src
      break;
  }
}
const getLocation = (e) => {
  return '';
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
    loc.textContent = `Location: ${getLocation(entry)}`;
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
    header.textContent = url;
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
const submitData = (event) => {
  event.preventDefault();
  const url = document.getElementById('url').value;
  const formdata = new FormData();
  if (!url) {
    const csvfile = document.getElementById('file').files[0];
    formdata.append('file', csvfile);
  }
  const requestOptions = {
    method: 'POST', headers: url ? { 'Content-Type': 'application/json' } : {},
    body: url ? JSON.stringify({'url': url}) : formdata,
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
    .catch((error) => console.log(error));
}
document.getElementById('query').onsubmit = submitData;
