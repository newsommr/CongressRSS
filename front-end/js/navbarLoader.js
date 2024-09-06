document.addEventListener("DOMContentLoaded", function() {
    // Define a function to load the navbar
    function loadNavbar() {
        const navbarContainer = document.getElementById('navbar');

        // Check if the navbar container exists
        if (navbarContainer) {
            // Fetch the navbar HTML
            fetch('navbar.html')
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.text();
                })
                .then(html => {
                    navbarContainer.innerHTML = html;
                })
                .catch(error => {
                    console.error('Error loading the navbar:', error);
                });
        }
    }

    // Call the function to load the navbar
    loadNavbar();
});
