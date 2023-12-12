var items = []; // Global variable to store all fetched items

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
function displayItems(sortOrder = 'desc', filterSources = []) {
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
      var timeZoneAbbreviation = pubDate.toLocaleTimeString("en-US", {
          timeZoneName: "short",
      }).split(" ")[2];

      var title = itemsToDisplay[i].title;
      if (title.length > 250) {
          title = title.substring(0, 252) + "...";
      }

      html += "<li class='list-group-item'>";
      html += "<div class='item-text'>";
      html += "<a href='" + itemsToDisplay[i].link + "'>" + title + "</a>";
      html += "<p> Published: " + pubDate.toLocaleDateString() + " " + pubDate.toLocaleTimeString() + " (" + timeZoneAbbreviation + ")<br>";
      html += "Source: " + itemsToDisplay[i].source + "</p>";
      html += "</div>";
      html += "</li>";
    }
          html += "</ul>";

          $("#rss-content").html(html);
  }
      
// Function to handle sort order change
function changeSortOrder(sortOrder) {
  var selectedSources = [];
  $("input[name='source']:checked").each(function() {
      selectedSources.push($(this).val());
  });

  displayItems(sortOrder, selectedSources);
}

// Function to apply filters based on selected checkboxes
function applyFilters() {
    var selectedSources = [];
    $("input[name='source']:checked").each(function() {
        selectedSources.push($(this).val());
    });

    displayItems('desc', selectedSources);
}

// Initial fetch with default sort order
$(document).ready(function() {
    fetchRSS("https://congress-rss.fly.dev/items");
});