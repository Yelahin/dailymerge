function toggleFavorite(event, articleId) {
    event.preventDefault(); // Prevent opening the link
    event.stopPropagation(); // Stop bubbling

    const icon = event.currentTarget;
    const url = `/favorite/toggle/${articleId}/`;

    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Check if we are on the favorite page
                const isFavoritePage = window.location.pathname.includes('/favorite/');

                if (isFavoritePage && !data.is_favorite) {
                    // Remove the article card specifically
                    const articleCard = document.getElementById(`article-${articleId}`);
                    if (articleCard) {
                        articleCard.style.transition = "opacity 0.05s, transform 0.05s";
                        articleCard.style.opacity = "0";
                        articleCard.style.transform = "scale(0.9)";

                        setTimeout(() => {
                            articleCard.remove();
                            // Update count
                            const countSpan = document.getElementById('fav-count');
                            if (countSpan) {
                                let count = parseInt(countSpan.innerText);
                                count = Math.max(0, count - 1);
                                countSpan.innerText = count;

                                // Show empty message if count is 0
                                if (count === 0) {
                                    const container = document.getElementById('favorites-container');
                                    if (container) {
                                        container.innerHTML = '<p id="no-favorites-msg">No favorite articles yet.</p>';
                                    }
                                }
                            }
                        }, 50);
                    }
                } else {
                    // Normal toggle behavior
                    if (data.is_favorite) {
                        icon.classList.add('active');
                    } else {
                        icon.classList.remove('active');
                    }
                }
            } else {
                console.error('Error toggling favorite:', data.message);
            }
        })
        .catch(error => console.error('Error:', error));
}

// Helper to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
