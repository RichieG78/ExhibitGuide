const readButton = document.getElementById('read-button');
const readingPanel = document.getElementById('reading-panel');
const viewButton = document.getElementById('view-button');
const viewPanel = document.getElementById('view-panel');
const listenButton = document.getElementById('listen-button');
const listenPanel = document.getElementById('listen-panel');

if (readButton && readingPanel) {
    readButton.addEventListener('click', () => {
        const isVisible = readingPanel.classList.toggle('is-visible');
        readButton.setAttribute('aria-expanded', String(isVisible));
    });
}

if (viewButton && viewPanel) {
    viewButton.addEventListener('click', () => {
        const isVisible = viewPanel.classList.toggle('is-visible');
        viewButton.setAttribute('aria-expanded', String(isVisible));
    });
}

if (listenButton && listenPanel) {
    listenButton.addEventListener('click', () => {
        const isVisible = listenPanel.classList.toggle('is-visible');
        listenButton.setAttribute('aria-expanded', String(isVisible));
    });
}
