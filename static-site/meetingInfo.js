async function fetchSessionStatus(sessionType, elementId) {
    try {
        const response = await fetch(`https://congress-rss.fly.dev/info/session/${sessionType}`);
        const data = await response.json();
        let result = document.createElement('div');

        result.textContent = `${sessionType.charAt(0).toUpperCase() + sessionType.slice(1)}: ${data.in_session === 0 ? 'Adjourned' : 'In Session'}`;

        if (data.next_meeting) {
            const nextSessionDiv = document.createElement('div');
            nextSessionDiv.className = 'session-next-date';
            var pubDate = new Date(data.next_meeting);
            const localOffset = pubDate.getTimezoneOffset();
            const localTime = new Date(pubDate.getTime() - localOffset * 60000);
            const localTimeString = localTime.toLocaleString('en-US', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                hour12: true,
                timeZoneName: 'short'
            });
            nextSessionDiv.textContent = `Meets ${localTimeString}`;
            result.appendChild(nextSessionDiv);
        }

        if (data.in_session === 1 && sessionType === 'senate' && data.live_link) {
            const link = document.createElement('a');
            link.href = data.live_link;
            link.target = '_blank';
            link.textContent = ' (Live)';
            link.style.color = 'inherit';
            link.style.textDecoration = 'none';
            result.appendChild(link);
        }

        document.getElementById(elementId).innerHTML = '';
        document.getElementById(elementId).appendChild(result);
    } catch (error) {
        console.error(`Failed to fetch ${sessionType} session status:`, error);
    }
}

fetchSessionStatus('house', 'houseSessionStatus');
fetchSessionStatus('senate', 'senateSessionStatus');
