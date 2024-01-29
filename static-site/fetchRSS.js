(function() {
    const API_URL = "https://congress-rss.fly.dev/items/search/";
    const TITLE_MAX_LENGTH = 1000;
    const INDEX_PAGE_NAME = "mainPage";

    let items = [];
    let currentSortOrder = 'desc';
    let lastSearchTerm = '';

    const sourceNameMapping = {
        'white-house-legislation': 'White House',
        'white-house-presidential-actions': 'White House',
        'house-rules-committee': 'House Rules Committee',
        'senateppg-twitter': 'Senate Periodical Press Gallery',
        'housedailypress-twitter': 'House Press Gallery',
        'doj-olc-opinions': 'Department of Justice, Office of Legal Counsel',
        'gao-reports': 'Government Accountability Office',
        'dsca-major-arms-sales': 'Defense Security Cooperation Agency',
        'potus-schedule': 'Factbase'
    };

    const sourceLinkMapping = { 
        'white-house-legislation': "https://www.whitehouse.gov/briefing-room/legislation/",
        'white-house-presidential-actions': 'https://www.whitehouse.gov/briefing-room/presidential-actions/',
        'house-rules-committee': 'https://rules.house.gov/legislation',
        'senateppg-twitter': 'https://twitter.com/senateppg',
        'housedailypress-twitter': 'https://twitter.com/housedailypress',
        'doj-olc-opinions': 'https://www.justice.gov/olc/opinions',
        'gao-reports':  'https://www.gao.gov/reports-testimonies',
        'dsca-major-arms-sales': 'https://www.dsca.mil/press-media/major-arms-sales',
        'potus-schedule': 'https://factba.se/biden/calendar'
    }

    function truncateString(str, maxLength) {
        return str.length > maxLength ? `${str.substring(0, maxLength)}...` : str;
    }

    function formatDate(dateString) {
    const pubDate = new Date(dateString);
    const now = new Date();
    const localOffset = pubDate.getTimezoneOffset();
    const localTime = new Date(pubDate.getTime() - localOffset * 60000);
    const diffMs = now - localTime; // Difference in milliseconds

    let relativeTime = '';
    if (Math.abs(diffMs) < 24 * 60 * 60 * 1000) { // Within 24 hours
        if (Math.abs(diffMs) < 60 * 60 * 1000) { // Less than an hour
            const minutes = Math.floor(Math.abs(diffMs) / (60 * 1000));
            const minuteText = minutes === 1 ? 'minute' : 'minutes';
            relativeTime = ` (${minutes} ${minuteText} ${diffMs > 0 ? 'ago' : 'from now'})`;
        } else {
            const hours = Math.floor(Math.abs(diffMs) / (60 * 60 * 1000));
            const hourText = hours === 1 ? 'hour' : 'hours';
            relativeTime = ` (${hours} ${hourText} ${diffMs > 0 ? 'ago' : 'from now'})`;
        }
    }

    return localTime.toLocaleString('en-US', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true,
        timeZoneName: 'short'
    }) + relativeTime;
}


    async function fetchRSS(url, applySourceFilter = false) {
        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
            items = await response.json();
            applySourceFilter ? applyFilters() : displayItems();
        } catch (error) {
            console.error("Failed to fetch RSS:", error);
            document.getElementById('rss-content').textContent = 'No results.';
        }
    }

    function displayItems(sortOrder = currentSortOrder, filterSources = [], searchTerm = '') {
        let filteredItems = filterAndSortItems(items, filterSources, searchTerm, sortOrder);
        renderItems(filteredItems);
    }

    function filterAndSortItems(items, filterSources, searchTerm, sortOrder) {
        return items
            .filter(item => filterSources.length === 0 || filterSources.includes(item.source))
            .sort((a, b) => (sortOrder === 'asc' ? new Date(a.pubDate) - new Date(b.pubDate) : new Date(b.pubDate) - new Date(a.pubDate)));
    }

    function renderItems(items) {
        const listGroup = document.createElement('ul');
        listGroup.className = 'list-group';

        items.forEach(item => {
            const listItem = document.createElement('li');
            listItem.className = 'list-group-item';
            listItem.innerHTML = getItemHTML(item);
            listGroup.appendChild(listItem);
        });

        const contentContainer = document.getElementById('rss-content');
        contentContainer.innerHTML = '';
        contentContainer.appendChild(listGroup);
    }

    function getItemHTML(item) {
        const title = truncateString(item.title, TITLE_MAX_LENGTH);
        const pubDate = formatDate(item.pubDate);
        const sourceName = sourceNameMapping[item.source.trim()] || item.source.trim();
        const sourceLink = sourceLinkMapping[item.source.trim()] || item.source.trim();
        let timeOrPublished = "Published"
        if (sourceName == 'Factbase') {
            timeOrPublished = "Time";
        }

        // Check if item.link is available
        const titleElement = item.link ? `<a href='${item.link}' target="_blank">${title}</a>` : title;

        return `
            <div class='item-text'>
                ${titleElement}
                <p>${timeOrPublished}: ${pubDate}<br>
                Source: <a class='item-source' href='${sourceLink}' target="_blank">${sourceName}</a></p>
            </div>
        `;
    }


    function toggleSortOrder() {
        currentSortOrder = currentSortOrder === 'asc' ? 'desc' : 'asc';
        applyFilters();
    }

    function applyFilters() {
        const selectedSources = getSelectedSources();
        if (selectedSources.length === 0 && getPage() != INDEX_PAGE_NAME) {
            document.getElementById('rss-content').textContent = 'No sources selected.';
            return;
        }
        displayItems(currentSortOrder, selectedSources, lastSearchTerm);
    }

    function getSelectedSources() {
        return Array.from(document.querySelectorAll("input[name='source']:checked"))
            .map(input => input.value);
    }

    function handleSearchInput() {
        const searchTerm = document.getElementById('searchInput').value;
        if (searchTerm !== lastSearchTerm) {
            lastSearchTerm = searchTerm;
            fetchFilteredResults();
        }
    }

    function fetchFilteredResults() {
        const selectedSources = getSelectedSources();
        if (selectedSources.length === 0 && getPage() != INDEX_PAGE_NAME) {
            document.getElementById('rss-content').textContent = 'No sources selected.';
            return;
        }
    
        let url = `${API_URL}?search_term=${encodeURIComponent(lastSearchTerm)}`;
        if (getPage() != INDEX_PAGE_NAME) {
            url += `&sources=${encodeURIComponent(selectedSources.join(','))}`;
        }
        fetchRSS(url, true);
    }
    

    function getPage() {
        return document.body.id;
    }

    document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll("input[name='source']").forEach(checkbox => {
            checkbox.checked = true;
            checkbox.addEventListener('change', () => {
                fetchFilteredResults();
            });
        });
        

        document.getElementById('searchInput').addEventListener('keyup', handleSearchInput);
        document.getElementById('toggleSortButton').addEventListener('click', toggleSortOrder);

        window.addEventListener('scroll', handleInfiniteScroll);
        fetchFilteredResults();
    });

    function handleInfiniteScroll() {
        const scrollable = document.documentElement.scrollHeight - window.innerHeight;
        const scrolled = window.scrollY;
        const threshold = 100; // How close to the page bottom before loading more items

        if (scrollable - scrolled <= threshold) {
            // Avoid multiple requests
            window.removeEventListener('scroll', handleInfiniteScroll);

            loadMoreItems();
        }
    }

    async function loadMoreItems() {
        const offset = items.length; // Assuming 'items' array holds the currently displayed items
        let url = `${API_URL}?search_term=${encodeURIComponent(lastSearchTerm)}&offset=${offset}`;

        const selectedSources = getSelectedSources();
        if (selectedSources.length > 0 && getPage() != INDEX_PAGE_NAME) {
            url += `&sources=${encodeURIComponent(selectedSources.join(','))}`;
        }

        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
            const newItems = await response.json();
            items = items.concat(newItems); // Append new items to the existing list
            displayItems(currentSortOrder, selectedSources, lastSearchTerm);
            window.addEventListener('scroll', handleInfiniteScroll); // Re-attach scroll event listener
        } catch (error) {
            console.error("Failed to fetch more RSS items:", error);
        }
    }
})();
