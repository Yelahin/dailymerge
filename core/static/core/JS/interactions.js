document.addEventListener('DOMContentLoaded', () => {
    // Staggered animation for news items
    const newsItems = document.querySelectorAll('.news-item');

    newsItems.forEach((item, index) => {
        // Add a delay based on the index to create a stagger effect
        // We cap the index at 20 to avoid waiting too long for items further down
        const delay = Math.min(index * 100, 2000);
        item.style.animationDelay = `${delay}ms`;
    });

});
