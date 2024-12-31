document.addEventListener('DOMContentLoaded', function() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    const dropdownToggles = document.querySelectorAll('.nav-link.dropdown-toggle');

    // Открытие/закрытие бургер-меню
    navbarToggler.addEventListener('click', function(e) {
        e.stopPropagation();
        navbarCollapse.classList.toggle('show');
    });

    // Обработка выпадающих меню
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const parentItem = this.closest('.nav-item');
            const currentMenu = parentItem.querySelector('.dropdown-menu');
            
            // Если меню уже открыто - закрываем его
            if (currentMenu.classList.contains('show')) {
                parentItem.classList.remove('show');
                currentMenu.classList.remove('show');
                return;
            }

            // Закрываем все другие открытые меню
            dropdownToggles.forEach(otherToggle => {
                const otherItem = otherToggle.closest('.nav-item');
                const otherMenu = otherItem.querySelector('.dropdown-menu');
                otherItem.classList.remove('show');
                otherMenu.classList.remove('show');
            });

            // Открываем текущее меню
            parentItem.classList.add('show');
            currentMenu.classList.add('show');
        });
    });

    // Закрытие при клике вне меню
    document.addEventListener('click', function(e) {
        if (!navbarCollapse.contains(e.target) && !navbarToggler.contains(e.target)) {
            navbarCollapse.classList.remove('show');
            dropdownToggles.forEach(toggle => {
                const parentItem = toggle.closest('.nav-item');
                const menu = parentItem.querySelector('.dropdown-menu');
                parentItem.classList.remove('show');
                menu.classList.remove('show');
            });
        }
    });
});