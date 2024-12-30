// Immediate theme check before DOM loads
(function() {
    if (localStorage.getItem('theme') === 'dark') {
        document.documentElement.classList.add('dark-theme');
        document.body.classList.add('dark-theme');
    }
})();

// Utility functions
function highlightMatch(text, searchTerm) {
    if (!searchTerm) return text;
    const escapedSearchTerm = searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`(${escapedSearchTerm})`, 'gi');
    return text.replace(regex, '<span class="highlight">$1</span>');
}

// Initialize all functionality when document is ready
$(document).ready(function() {
    initializeKeyboardNavigation();
    initializeDropdownMenu();
    initializeTooltips();
    initializeSearch();
    initializeSpoilers();
    
    // Initialize image zoom if on monster page
    if ($('.monster-image').length) {
        initializeImageZoom();
    }
});

// Image zoom functionality
function initializeImageZoom() {
    $('.monster-image').each(function() {
        var $img = $(this);
        $img.off('mouseenter mouseleave');

        $img.hover(
            function() {
                $(this).css({
                    'transform': 'scale(2)',
                    'z-index': '1000',
                    'transition': 'transform 0.3s ease'
                });
            },
            function() {
                $(this).css({
                    'transform': 'scale(1)',
                    'z-index': '1',
                    'transition': 'transform 0.3s ease'
                });
            }
        );
    });
}

// Keyboard navigation
function initializeKeyboardNavigation() {
    $(document).keydown(function(e) {
        const isMonsterPage = $('#monsterSearch').length > 0;
        const searchId = isMonsterPage ? '#monsterSearch' : '#itemSearch';
        
        // Ctrl+F to focus search
        if (e.ctrlKey && e.keyCode === 70) {
            e.preventDefault();
            $(searchId).focus();
        }
        // Escape to clear search
        if (e.keyCode === 27) {
            $(searchId).val('').trigger('input');
            $('#searchSuggestions').hide();
        }
        // Left/Right arrows for pagination when not in search
        if (!$(searchId).is(':focus')) {
            if (e.keyCode === 37) { // Left arrow
                window.table.page('previous').draw('page');
            } else if (e.keyCode === 39) { // Right arrow
                window.table.page('next').draw('page');
            }
        }
    });
}

// Dropdown menu functionality
function initializeDropdownMenu() {
    let timeout;
    const DELAY = 300;

    $('.nav-item.dropdown').hover(
        function() {
            clearTimeout(timeout);
            const $dropdown = $(this);
            $('.nav-item.dropdown').not($dropdown).find('.dropdown-menu').hide();
            $dropdown.find('.dropdown-menu').show();
        },
        function() {
            const $dropdown = $(this);
            timeout = setTimeout(function() {
                if (!$dropdown.find('.dropdown-menu:hover').length) {
                    $dropdown.find('.dropdown-menu').hide();
                }
            }, DELAY);
        }
    );

    $('.dropdown-menu').hover(
        function() { clearTimeout(timeout); },
        function() {
            const $menu = $(this);
            timeout = setTimeout(function() {
                $menu.hide();
            }, DELAY);
        }
    );

    $('.dropdown-item').click(function(e) {
        const href = $(this).attr('href');
        if (href) {
            window.location.href = href;
        }
    });
}

// Initialize tooltips
function initializeTooltips() {
    $('[data-toggle="tooltip"]').tooltip();
}

// Search functionality
function initializeSearch() {
    const isMonsterPage = $('.monster-image').length > 0;
    const searchInput = document.getElementById(isMonsterPage ? 'monsterSearch' : 'itemSearch');
    const suggestionsContainer = document.getElementById('searchSuggestions');
    const clearButton = document.getElementById('clearSearch');
    let searchDebounceTimer;

    if (!searchInput || !suggestionsContainer || !clearButton) return;

    searchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.trim().toLowerCase();
        clearTimeout(searchDebounceTimer);

        if (searchTerm === '') {
            suggestionsContainer.style.display = 'none';
            app.applyFilters(1);
            return;
        }

        searchDebounceTimer = setTimeout(() => {
            const suggestions = findSuggestions(searchTerm, isMonsterPage);
            displaySuggestions(suggestions, searchTerm, isMonsterPage);
            app.applyFilters(1);
        }, 300);
    });

    clearButton.addEventListener('click', () => {
        searchInput.value = '';
        suggestionsContainer.style.display = 'none';
        app.applyFilters(1);
    });

    document.addEventListener('click', (e) => {
        if (!e.target.closest('.search-container')) {
            suggestionsContainer.style.display = 'none';
        }
    });
}

function findSuggestions(searchTerm, isMonsterPage) {
    const cachedData = app?.stateManager?.getState('cachedData');
    const items = isMonsterPage ? cachedData?.monsters : cachedData?.items;
    
    if (!items) return [];

    return items
        .filter(item => {
            const id = isMonsterPage ? item.MID : item.IID;
            const name = isMonsterPage ? item.MName : item.IName;
            const matchesId = id.toString().toLowerCase().includes(searchTerm);
            const matchesName = name.toLowerCase().includes(searchTerm);
            return matchesId || matchesName;
        })
        .slice(0, 8);
}

function displaySuggestions(suggestions, searchTerm, isMonsterPage) {
    const suggestionsContainer = document.getElementById('searchSuggestions');
    if (!suggestionsContainer) return;

    if (!suggestions.length) {
        suggestionsContainer.style.display = 'none';
        return;
    }

    const resources = app?.stateManager?.getState('cachedData')?.resources || {};
    
    const suggestionsHtml = suggestions.map(item => {
        const id = isMonsterPage ? item.MID : item.IID;
        const name = isMonsterPage ? item.MName : item.IName;
        const itemName = highlightMatch(name, searchTerm);
        const itemId = highlightMatch(id.toString(), searchTerm);
        const imageUrl = resources[id] || CONSTANTS.FALLBACK_IMAGE;
        const type = isMonsterPage ? 'monster' : 'item';
        
        return `
            <a href="/${type}/${id}" class="search-suggestion" data-id="${id}">
                <img src="${imageUrl}" alt="${name}" onerror="this.src='${CONSTANTS.FALLBACK_IMAGE}';">
                <span>[${itemId}] ${itemName}</span>
            </a>
        `;
    }).join('');

    suggestionsContainer.innerHTML = suggestionsHtml;
    suggestionsContainer.style.display = 'block';
}

// Spoiler functionality
function initializeSpoilers() {
    document.querySelectorAll('.skill-section').forEach(section => {
        const title = section.querySelector('.section-title');
        const content = section.querySelector('.skill-content');
        
        if (title && content) {
            // Create wrapper for content
            const contentWrapper = document.createElement('div');
            contentWrapper.className = 'skill-content-wrapper';
            content.parentNode.insertBefore(contentWrapper, content);
            contentWrapper.appendChild(content);
            
            // Create header structure
            const header = document.createElement('div');
            header.className = 'skill-header';
            
            const titleWrapper = document.createElement('div');
            titleWrapper.className = 'skill-title-wrapper';
            
            const toggle = document.createElement('div');
            toggle.className = 'skill-toggle';
            
            // Move the title into the new structure
            title.parentNode.removeChild(title);
            titleWrapper.appendChild(title);
            header.appendChild(titleWrapper);
            header.appendChild(toggle);
            
            // Insert the header before the content wrapper
            contentWrapper.parentNode.insertBefore(header, contentWrapper);
            
            // Set initial height
            contentWrapper.style.height = content.offsetHeight + 'px';
            
            // Add click handler
            header.addEventListener('click', function() {
                const isCollapsed = section.classList.contains('collapsed');
                
                if (isCollapsed) {
                    contentWrapper.style.height = content.offsetHeight + 'px';
                    section.classList.remove('collapsed');
                } else {
                    contentWrapper.style.height = content.offsetHeight + 'px';
                    contentWrapper.offsetHeight; // Force reflow
                    section.classList.add('collapsed');
                }
            });
            
            // Add resize observer to handle content changes
            const resizeObserver = new ResizeObserver(entries => {
                if (!section.classList.contains('collapsed')) {
                    contentWrapper.style.height = content.offsetHeight + 'px';
                }
            });
            
            resizeObserver.observe(content);
        }
    });
}

// Theme toggle functionality
const toggleButton = document.getElementById('theme-toggle');

// Adding sound effect on click
const soundEffect = new Audio('https://www.soundjay.com/buttons/sounds/button-30.mp3');

toggleButton.addEventListener('click', () => {
    document.documentElement.classList.toggle('dark-theme');
    document.body.classList.toggle('dark-theme');
    localStorage.setItem(
        'theme',
        document.documentElement.classList.contains('dark-theme') ? 'dark' : 'light'
    );

    // Play sound effect
    soundEffect.play();

    // Toggle bounce effect for fun
    toggleButton.classList.toggle('bouncing');
    setTimeout(() => toggleButton.classList.remove('bouncing'), 1000);
});

// Restore theme on page load
const savedTheme = localStorage.getItem('theme');
if (savedTheme === 'dark') {
    document.documentElement.classList.add('dark-theme');
    document.body.classList.add('dark-theme');
}





