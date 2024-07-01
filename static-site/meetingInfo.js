async function fetchSessionStatus() {
    try {
        const response = await fetch(`https://congress-rss.fly.dev/legislative/session-info`);

        if (!response.ok) {
            throw new Error(`Failed to fetch session status: ${response.status}`);
        }
        const data = await response.json();
        if (data.status !== 'success') {
            throw new Error(`Failed to fetch session status: ${data.message}`);
        }

        // jsonData[0] = Senate info, jsonData[1] = House info
        data.data.forEach(jsonData => {
            let sessionType = jsonData.chamber.toLowerCase();
            let elementId = `${sessionType}SessionStatus`;

            let result = document.createElement('div');
            result.textContent = `${sessionType.charAt(0).toUpperCase() + sessionType.slice(1)}: `;

            if (jsonData.in_session === 1) {
                const sessionStatusText = document.createElement('a');
                sessionStatusText.textContent = 'In Session';
                sessionStatusText.style.color = 'inherit';
                sessionStatusText.style.textDecoration = 'none';

                // Open link in a new tab
                sessionStatusText.target = '_blank';

                result.appendChild(sessionStatusText);
            } else {
                result.textContent += 'Adjourned';
            }

            if (jsonData.next_meeting) {
                const nextSessionDiv = document.createElement('div');
                nextSessionDiv.className = 'session-next-date';

                // Convert UTC time to the user's local time
                var pubDate = new Date(jsonData.next_meeting);
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

            document.getElementById(elementId).innerHTML = '';
            document.getElementById(elementId).appendChild(result);
        });
    } catch (error) {
        console.error(`Failed to fetch session status:`, error);
    }
}

fetchSessionStatus();