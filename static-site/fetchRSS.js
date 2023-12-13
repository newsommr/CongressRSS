var items = []; // Global variable to store all fetched items
var currentSortOrder = 'desc'; // Default sorting order
var sourceNameMapping = {
    'white-house-legislation': 'White House',
    'white-house-presidential-actions': 'White House',
    'house-rules-committee': 'House Rules Committee',
    'senateppg-twitter': 'Senate Periodical Press Gallery'
};

// Function to fetch RSS data once and store it
function fetchRSS(url) {
    $.ajax({
        url: url,
        method: "GET",
        success: function (data) {
            items = data; // Store the fetched data
            displayItems(); // Display items initially
        },
    });
}

// Function to display items with current filters and sorting
function displayItems(sortOrder = currentSortOrder, filterSources = []) {
    var itemsToDisplay = items;

    // Filter itemsToDisplay by source if filterSources is not empty
    if (filterSources.length > 0) {
        itemsToDisplay = itemsToDisplay.filter(item => filterSources.includes(item.source));
    }

    // Sort the itemsToDisplay based on pubDate and sortOrder
    itemsToDisplay.sort((a, b) => {
        var dateA = new Date(a.pubDate), dateB = new Date(b.pubDate);
        return sortOrder === 'asc' ? dateA - dateB : dateB - dateA;
    });

// Generate and display HTML for the itemsToDisplay
var html = "<ul class='list-group'>";
for (var i = 0; i < itemsToDisplay.length; i++) {
    var pubDate = new Date(itemsToDisplay[i].pubDate);
    const localOffset = pubDate.getTimezoneOffset();
    const localTime = new Date(pubDate.getTime() - localOffset * 60000);
    
    // Modified line: Format the date and time
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

    var title = itemsToDisplay[i].title;
    if (title.length > 250) {
        title = title.substring(0, 252) + "...";
    }

    html += "<li class='list-group-item'>";
    html += "<div class='item-text'>";
    html += "<a href='" + itemsToDisplay[i].link + "'>" + title + "</a>";
    html += "<p> Published: " + localTimeString + "<br>"; // Adjusted line
    var sourceDisplayName = sourceNameMapping[itemsToDisplay[i].source.trim()] || itemsToDisplay[i].source.trim();
    html += "Source: " + sourceDisplayName + "</p>";
    html += "</div>";
    html += "</li>";
}
html += "</ul>";

$("#rss-content").html(html);

}

// Function to toggle sort order
function toggleSortOrder() {
    currentSortOrder = currentSortOrder === 'asc' ? 'desc' : 'asc';
    applyFilters();
}

// Function to apply filters based on selected checkboxes
function applyFilters() {
  var selectedSources = [];
  $("input[name='source']:checked").each(function() {
      selectedSources.push($(this).val());
  });

  // Check if no checkboxes are selected
  if (selectedSources.length === 0) {
      // Clear the displayed items
      $("#rss-content").html("");
      return; // Exit the function
  }

  // Call displayItems with the selected sources
  displayItems(currentSortOrder, selectedSources);
}

// Initial fetch with default sort order
$(document).ready(function() {
    fetchRSS("https://congress-rss.fly.dev/items/?limit=500");

    // Uncheck all checkboxes on page refresh
    $("input[name='source']").prop('checked', true);

    // Attach a change event listener to checkboxes
    $("input[name='source']").change(applyFilters);
});
