async function fetchSessionStatus(sessionType, elementId) {
    try {
        const response = await fetch(`https://congress-rss.fly.dev/info/session/${sessionType}`);
        const data = await response.json();
        let result;

        if (data.in_session === 0) {
            result = `${sessionType.charAt(0).toUpperCase() + sessionType.slice(1)}: Adjourned`;
        } else if (data.in_session === 1) {
            result = `${sessionType.charAt(0).toUpperCase() + sessionType.slice(1)}: `;
            if (sessionType === 'senate' && data.live_link) {
                const link = document.createElement('a');
                link.href = data.live_link;
                link.target = '_blank';
                link.textContent = 'In Session';
                link.style.color = 'inherit'; // Apply the CSS rule inline
                link.style.textDecoration = 'none'; // Optional: if you want to remove the underline
                result += link.outerHTML;
            } else {
                result += 'In Session';
            }
        }

        document.getElementById(elementId).innerHTML = result;
    } catch (error) {
        console.error(`Failed to fetch ${sessionType} session status:`, error);
    }
}

fetchSessionStatus('house', 'houseSessionStatus');
fetchSessionStatus('senate', 'senateSessionStatus');
