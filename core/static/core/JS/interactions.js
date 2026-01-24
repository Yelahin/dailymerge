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

document.addEventListener('DOMContentLoaded', function () {
    const sourceTypeSelect = document.getElementById('id_source_type');
    const paramsField = document.getElementById('id_params');

    if (sourceTypeSelect && paramsField) {
        // Find the parent form-group to hide the whole row
        const paramsGroup = paramsField.closest('.form-group');

        function toggleParamsField() {
            if (sourceTypeSelect.value === 'API') {
                paramsGroup.style.display = 'flex';
            } else {
                paramsGroup.style.display = 'none';
            }
        }

        // Initial check
        toggleParamsField();

        // Listen for changes
        sourceTypeSelect.addEventListener('change', toggleParamsField);
    }
});
