(function() {
    const API_URL = "https://congress-rss.fly.dev/items/";
    const TITLE_MAX_LENGTH = 1000;

    // State Variables
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
        'gao-reports': 'Government Accountability Office'
    };

    const sourceLinkMapping = { 
        'white-house-legislation': "https://www.whitehouse.gov/briefing-room/legislation/",
        'white-house-presidential-actions': 'https://www.whitehouse.gov/briefing-room/presidential-actions/',
        'house-rules-committee': 'https://rules.house.gov/legislation',
        'senateppg-twitter': 'https://twitter.com/senateppg',
        'housedailypress-twitter': 'https://twitter.com/housedailypress',
        'doj-olc-opinions': 'https://www.justice.gov/olc/opinions',
        'gao-reports':  'https://www.gao.gov/reports-testimonies'
    }



    // Fetch from API with/without filtering
    async function fetchRSS(url, applySourceFilter = false) {
        try {
            const response = await fetch(url);
            items = await response.json();
            applySourceFilter ? applyFilters() : displayItems();
        } catch (error) {
            console.error("Failed to fetch RSS:", error);
            document.getElementById('rss-content').innerHTML = 'No results.';
        }
    }

    // Display items with optional sorting and filtering
    function displayItems(sortOrder = currentSortOrder, filterSources = [], searchTerm = '') {
        let filteredItems = filterAndSortItems(items, filterSources, searchTerm, sortOrder);
        renderItems(filteredItems);
    }

    // Filter and sort items
    function filterAndSortItems(items, filterSources, searchTerm, sortOrder) {
        try {
            return items
            .filter(item => filterSources.length === 0 || filterSources.includes(item.source))
            .sort((a, b) => (sortOrder === 'asc' ? new Date(a.pubDate) - new Date(b.pubDate) : new Date(b.pubDate) - new Date(a.pubDate)));
        } catch (error) {
            console.log(error)
        }
    }

    // Render items to the DOM
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

    // Generate the HTML for each item to be displayed.
    function getItemHTML(item) {
        const title = item.title.length > TITLE_MAX_LENGTH ? `${item.title.substring(0, TITLE_MAX_LENGTH)}...` : item.title;
        // Modified line: Format the date and time
        var pubDate = new Date(item.pubDate);
        const localOffset = pubDate.getTimezoneOffset();
        const localTime = new Date(pubDate.getTime() - localOffset * 60000);
        const localTimeString = localTime.toLocaleString('en-US', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: true,
            timeZoneName: 'short'
        });
        const sourceName = sourceNameMapping[item.source.trim()] || item.source.trim();
        const sourceLink = sourceLinkMapping[item.source.trim()] || item.source.trim();

        return `
            <div class='item-text'>
                <a href='${item.link}'target="_blank">${title}</a>
                <p> Published: ${localTimeString}<br>
                Source: <a class='item-source' href='${sourceLink}'target="_blank">${sourceName}</a></p>
            </div>
        `;
    }

    // Formats the pubdate to display to the user's local time
    function getFormattedLocalTime(pubDate) {
        const localTime = new Date(pubDate);
        return localTime.toLocaleString('en-US', {
            year: 'numeric', month: '2-digit', day: '2-digit',
            hour: '2-digit', minute: '2-digit', second: '2-digit',
            hour12: true, timeZoneName: 'short'
        });
    }

    function toggleSortOrder() {
        currentSortOrder = currentSortOrder === 'asc' ? 'desc' : 'asc';
        applyFilters();
    }

    function applyFilters() {
        const selectedSources = getSelectedSources();
        if (selectedSources.length === 0) {
            document.getElementById('rss-content').innerHTML = 'No sources selected.';
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
        lastSearchTerm = searchTerm;

        if (lastSearchTerm !== "") {
            fetchFilteredResults();
        } else {
            fetchRSS(`${API_URL}?limit=500`, true);
        }
    }

    function fetchFilteredResults() {
        const selectedSources = getSelectedSources();
        let url = `${API_URL}search/${encodeURIComponent(lastSearchTerm)}`;

        if (selectedSources.length === 0) return;

        url += `?sources=${encodeURIComponent(selectedSources.join(','))}`;
        fetchRSS(url, true);
    }


    // Initialization
    document.addEventListener('DOMContentLoaded', () => {
        fetchRSS(`${API_URL}?limit=500`, true);

        // Event listener for source filter checkboxes
        document.querySelectorAll("input[name='source']").forEach(checkbox => {
            checkbox.checked = true;
            checkbox.addEventListener('change', applyFilters);
            checkbox.addEventListener('change', handleSearchInput);
        });

        // Event listener for search input
        document.getElementById('searchInput').addEventListener('keyup', handleSearchInput);

        // Event listener for sort order toggle button
        document.getElementById('toggleSortButton').addEventListener('click', toggleSortOrder);
    });
})();

