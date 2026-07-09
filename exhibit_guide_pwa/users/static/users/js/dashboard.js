// This script powers the dashboard filter pills.
// It hides and shows cards on the page instead of doing a full page reload.

const filterButtons = document.querySelectorAll('.filter-pill');
const cards = document.querySelectorAll('.artwork-card');
const emptyState = document.querySelector('[data-filter-empty]');

const emptyMessages = {
    all: 'No paintings to display yet.',
    scanned: 'No newly scanned painting yet. Scan a QR code to add one here.',
    watching: 'Nothing in your watchlist yet. Add a scanned painting to start watching.',
    enquired: 'No inquiries sent yet.',
    acquired: 'No acquired works yet.',
};

function applyFilter(filterValue) {
    // Count visible cards so we can show a friendly empty-state message when needed.
    let visibleCount = 0;

    cards.forEach((card) => {
        const status = card.getAttribute('data-status') || 'watching';
        const shouldShow = filterValue === 'all' || filterValue === status;
        card.classList.toggle('is-hidden', !shouldShow);
        if (shouldShow) {
            visibleCount += 1;
        }
    });

    if (emptyState) {
        const message = emptyMessages[filterValue] || emptyMessages.all;
        emptyState.textContent = message;
        emptyState.classList.toggle('is-hidden', visibleCount > 0);
    }
}

filterButtons.forEach((button) => {
    button.addEventListener('click', () => {
        // Only one pill should look active at a time.
        filterButtons.forEach((item) => item.classList.remove('is-active'));
        button.classList.add('is-active');
        applyFilter(button.getAttribute('data-filter') || 'all');
    });
});

const activeButton = document.querySelector('.filter-pill.is-active');
const initialFilter = (activeButton && activeButton.getAttribute('data-filter')) || 'scanned';

// Sync the first rendered screen with whichever pill the template marked as active.
applyFilter(initialFilter);
