function fetchRSS(url, sortOrder = 'desc') {
    $.ajax({
        url: url,
        method: "GET",
        success: function (data) {
            // Sort the items based on pubDate and sortOrder
            var items = data.sort((a, b) => {
                var dateA = new Date(a.pubDate), dateB = new Date(b.pubDate);
                return sortOrder === 'asc' ? dateA - dateB : dateB - dateA;
            });
  
            // Generate the HTML for the sorted items
            var html = "<ul>";
            for (var i = 0; i < items.length; i++) {
                var pubDate = new Date(items[i].pubDate);
                var timeZoneAbbreviation = pubDate.toLocaleTimeString("en-US", {
                    timeZoneName: "short",
                }).split(" ")[2];
  
                var title = items[i].title;
                if (title.length > 250) {
                    title = title.substring(0, 252) + "...";
                }
  
                html += "<li>";
                html += "<div class='item-text'>";
                html += "<a href='" + items[i].link + "'>" + title + "</a>";
                html += "<p> Published: " + pubDate.toLocaleDateString() + " " + pubDate.toLocaleTimeString() + " (" + timeZoneAbbreviation + ") </p>";
                html += "</div>";
                html += "</li>";
            }
            html += "</ul>";
  
            $("#rss-content").html(html);
        },
    });
  }
  
  // Function to handle sort order change and re-fetch RSS data
  function changeSortOrder(sortOrder) {
    $('#rss-content').empty(); // Clear existing RSS items
    fetchRSS("https://back-end.fly.dev/items", sortOrder);
  }
  
  // Initial fetch with default sort order
  $(document).ready(function() {
    fetchRSS("https://back-end.fly.dev/items");
  });
  