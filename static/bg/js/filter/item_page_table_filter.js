// Constants and Configuration
const CONSTANTS = {
    DEBOUNCE_DELAY: 300,
    DEFAULT_PER_PAGE: 28,
    LOADING_FADE_DELAY: 500,
    ERROR_DISPLAY_TIME: 5000,
    PAGINATION_RADIUS: 2,
    FALLBACK_IMAGE: 'https://raw.githubusercontent.com/Aksel911/R2-HTML-DB/main/static/no_monster/no_monster_image.png',
    TABLE_FADE_DURATION: 300,
    BUTTON_ANIMATION_DURATION: 200,
    ANIMATION_CLASSES: {
        FADE_ENTER: 'table-fade-enter',
        FADE_ENTER_ACTIVE: 'table-fade-enter-active'
    },
    PER_PAGE_OPTIONS: [10, 25, 50, 75, 100, 150, 200],
    ATROPOS_OPTIONS: {
        activeOffset: 20,
        shadowScale: 1.05,
        rotateXMax: 10,
        rotateYMax: 10,
        duration: 400,
        shadow: true,
        shadowOffset: 30,
        highlight: true,
        onEnter(atropos) {
            atropos.el.classList.add('atropos-active');
        },
        onLeave(atropos) {
            atropos.el.classList.remove('atropos-active');
        }
    }
};

const TYPE_MAPPINGS = {
    '/weapon': [1, 18, 20],
    '/armor': [3],
    '/gloves': [7],
    '/boots': [6],
    '/helmet': [8],
    '/shield': [2],
    '/arrows': [19],
    '/cloak': [17],
    '/materials': [10, 16],
    '/ring': [4],
    '/belt': [9],
    '/necklace': [5],
    '/earrings': [42],
    '/books': [12],
    '/potions': [10],
    '/etc': [14, 16, 13, 11],
    '/sphere': [22, 23, 24, 25, 26, 27, 28, 29],
    '/quest': [15, 16]
};

const TYPE_DESCRIPTIONS = {
    1: 'Оружие Ближнего Боя',
    2: 'Щит, Браслет',
    3: 'Доспех',
    4: 'Кольцо',
    5: 'Ожерелье',
    6: 'Ботинки',
    7: 'Перчатки',
    8: 'Шлем',
    9: 'Ремень',
    10: 'Зелья',
    11: 'SpecificProcItem/Shop Item',
    12: 'Книга',
    13: 'Жезл, Фейерверк, Петарда',
    14: 'Предмет со Skill',
    15: 'Сундук',
    16: 'Пустышка, Печати, Квестовый',
    17: 'Плащ',
    18: 'Оружие Дальнего Боя',
    19: 'Патроны, стрелы, камни',
    20: 'Алебарда/Копье',
    22: 'Сфера Мастера',
    23: 'Сфера Души',
    24: 'Сфера Защиты',
    25: 'Сфера Разрушения',
    26: 'Сфера Жизни',
    27: 'Сфера 1 Слот',
    28: 'Сфера 2 Слот',
    29: 'Сфера 3 Слот',
    42: 'Серьги'
};

const CLASS_DESCRIPTIONS = {
    0: 'Нет класса',
    1: 'Рыцарь',
    2: 'Рейнджер',
    4: 'Маг',
    5: 'Рыцарь, Маг',
    7: 'Рыцарь, Рейнджер, Маг',
    8: 'Ассасин',
    15: 'Рыцарь, Рейнджер, Маг, Ассасин',
    16: 'Призыватель',
    18: 'Рейнджер, Призыватель',
    19: 'Рыцарь, Рейнджер, Призыватель',
    20: 'Маг, Призыватель',
    22: 'Рейнджер, Маг, Призыватель',
    23: 'Рыцарь, Рейнджер, Маг, Призыватель'
};


const ADVANCED_FILTERS = [{
        id: 'IDHIT',
        label: 'Точность в ближнем бою',
        icon: '🎯'
    },
    {
        id: 'IDDD',
        label: 'Урон в ближнем бою',
        icon: '⚔️'
    },
    {
        id: 'IRHIT',
        label: 'Точность в дальнем бою',
        icon: '🏹'
    },
    {
        id: 'IRDD',
        label: 'Урон в дальнем бою',
        icon: '🎯'
    },
    {
        id: 'IMHIT',
        label: 'Магическая точность',
        icon: '✨'
    },
    {
        id: 'IMDD',
        label: 'Магический урон',
        icon: '🔮'
    },
    {
        id: 'IHPPlus',
        label: 'Доп. HP',
        icon: '❤️'
    },
    {
        id: 'IMPPlus',
        label: 'Доп. MP',
        icon: '💧'
    },
    {
        id: 'ISTR',
        label: 'Сила',
        icon: '💪'
    },
    {
        id: 'IDEX',
        label: 'Ловкость',
        icon: '🏃'
    },
    {
        id: 'IINT',
        label: 'Интеллект',
        icon: '🧠'
    },
    {
        id: 'IHPRegen',
        label: 'Реген HP',
        icon: '♥️'
    },
    {
        id: 'IMPRegen',
        label: 'Реген MP',
        icon: '💫'
    },
    {
        id: 'IAttackRate',
        label: 'Скорость атаки',
        icon: '⚡'
    },
    {
        id: 'IMoveRate',
        label: 'Скорость передвижения',
        icon: '🏃'
    },
    {
        id: 'ICritical',
        label: 'Шанс крита',
        icon: '🎯'
    }
];

// Utilities
class EventEmitter {
    constructor() {
        this.events = {};
    }

    on(event, callback) {
        if (!this.events[event]) {
            this.events[event] = [];
        }
        this.events[event].push(callback);
        return () => this.off(event, callback);
    }

    off(event, callback) {
        if (!this.events[event]) return;
        this.events[event] = this.events[event].filter(cb => cb !== callback);
    }

    emit(event, data) {
        if (!this.events[event]) return;
        this.events[event].forEach(callback => callback(data));
    }
}

// State Management
class StateManager extends EventEmitter {
    constructor() {
        super();
        this._state = {
            currentPage: 1,
            cachedData: null,
            debounceTimer: null,
            isLoading: false,
            error: null,
            filters: {},
            perPage: CONSTANTS.DEFAULT_PER_PAGE
        };
    }

    setState(key, value) {
        const oldValue = this._state[key];
        this._state[key] = value;

        if (oldValue !== value) {
            this.emit('stateChange', {
                key,
                value,
                oldValue
            });
        }
    }

    getState(key) {
        return this._state[key];
    }

    resetState() {
        Object.keys(this._state).forEach(key => {
            if (key !== 'cachedData') {
                this.setState(key, null);
            }
        });
    }
}

// Data Service
class ItemDataService {
    constructor(stateManager) {
        this.stateManager = stateManager;
    }

    async fetchData(forceReload = false) {
        if (this.stateManager.getState('cachedData') && !forceReload) {
            return this.stateManager.getState('cachedData');
        }

        this.stateManager.setState('isLoading', true);

        try {
            const data = await this._fetchAllPages();
            this.stateManager.setState('cachedData', data);
            return data;
        } catch (error) {
            this.stateManager.setState('error', error.message);
            return null;
        } finally {
            this.stateManager.setState('isLoading', false);
        }
    }

    async _fetchAllPages() {
        const firstPageResponse = await this._fetchPage(1);
        let allItems = [...firstPageResponse.items];

        const totalPages = firstPageResponse.pages;
        const remainingPages = Array.from({
                length: totalPages - 1
            },
            (_, i) => i + 2
        );

        const pageResponses = await Promise.all(
            remainingPages.map(page => this._fetchPage(page))
        );

        pageResponses.forEach(response => {
            if (response.items) {
                allItems = allItems.concat(response.items);
            }
        });

        return {
            ...firstPageResponse,
            items: allItems
        };
    }

    async _fetchPage(page) {
        const response = await fetch(
            `${window.location.pathname}?all=1&page=${page}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            }
        );

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        if (data.error) {
            throw new Error(data.error);
        }

        return data;
    }
}

// Filter Logic
class ItemFilterManager {
    
    static collectFilters() {
        const filters = {};
        document.querySelectorAll('.form-control, .custom-control-input').forEach(input => {
            if (input.id === 'perPageSelect' || input.id === 'itemSearch') return;

            const value = input.type === 'checkbox' ? input.checked : input.value;
            
            if (value !== '') {
                filters[input.id] = value;
            }
        });

        //console.log('Collected filters:', filters);
        return filters;
    }

    static filterData(items, filters) {
        // Проверяем структуру первого предмета
        // if (items.length > 0) {
        //     console.log('First item structure:', items[0]);
        // }
        // Сначала применяем поиск
        const searchTerm = document.getElementById('itemSearch')?.value.trim().toLowerCase();
        let filteredData = items;

        if (searchTerm) {
            filteredData = items.filter(item => {
                const matchesId = item.IID.toString().toLowerCase().includes(searchTerm);
                const matchesName = item.IName.toLowerCase().includes(searchTerm);
                return matchesId || matchesName;
            });
        }

        // Затем применяем остальные фильтры
        return filteredData.filter(item => this._applyAllFilters(item, filters));
    }

    static _applyAllFilters(item, filters) {
        return Object.entries(filters).every(([key, value]) => {
            // Фильтр стакаемости
            if (key === 'stackableFilter') {
                if (!value) return true;
                return value === '1' ? item.IMaxStack > 0 : item.IMaxStack <= 0;
            }

            // Остальные фильтры...
            if (key === 'typeFilter') {
                return item.IType === Number(value);
            }

            if (key === 'typeClassFilter') {
                const filterClass = Number(value);
                if (!value || filterClass === 0 || filterClass === 255) return true;
                const classNumber = item.IUseClass ? 
                    Number(item.IUseClass.split('/').pop().replace('.png', '')) : 
                    0;
                return classNumber === filterClass;
            }

            if (key === 'questNoFilter') {
                if (!value) return true;
                return item.IQuestNo === Number(value);
            }

            if (key.endsWith('Min') || key.endsWith('Max')) {
                return this._applyRangeFilter(item, key, value);
            }

            if (this._isBooleanFilter(key)) {
                return this._applyBooleanFilter(item, key);
            }

            return true;
        });
    }

    static _applyRangeFilter(item, key, value) {
        const baseKey = key.replace(/(Min|Max)$/, '');
        const isMin = key.endsWith('Min');
        const itemValue = this._getItemValue(item, baseKey);
        const filterValue = Number(value);

        return isMin ?
            itemValue >= filterValue :
            itemValue <= filterValue;
    }

    static _isBooleanFilter(key) {
        return [
            'eventItemFilter',
            'testItemFilter',
            'indictFilter',
            'chargeFilter',
            'partyDropFilter'
        ].includes(key);
    }

    static _applyBooleanFilter(item, key) {
        const mappings = {
            eventItemFilter: 'IIsEvent',
            testItemFilter: 'IIsTest',
            indictFilter: 'IIsIndict',
            chargeFilter: 'IIsCharge',
            partyDropFilter: 'IIsPartyDrop'
        };

        return item[mappings[key]] === true;
    }

    static _getItemValue(item, baseKey) {
        const mappings = {
            level: 'ILevel',
            weight: 'IWeight',
            validityDays: 'ITermOfValidity',
            validityMinutes: 'ITermOfValidityMi'
        };

        return item[mappings[baseKey] || baseKey] || 0;
    }
}

// UI Management
class ItemUIManager {
    constructor(stateManager) {
        this.stateManager = stateManager;
        this.setupStateSubscriptions();
        this.initializeAtropos();
        this.setupThemeChangeListener();
    }


    
    initializeAtropos() {
        const script = document.createElement('script');
        script.src = 'https://unpkg.com/atropos@2.0.2/atropos.js';
        script.onload = () => {
            //console.log('Atropos loaded successfully');
            this.atroposLoaded = true;
        };
        document.head.appendChild(script);

        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'https://unpkg.com/atropos@2.0.2/atropos.css';
        document.head.appendChild(link);
    }

    reinitializeCards() {
        // Сначала уничтожаем все существующие экземпляры
        document.querySelectorAll('.atropos').forEach(el => {
            if (el.atroposInstance) {
                el.atroposInstance.destroy();
            }
        });
    
        // Затем реинициализируем карточки
        requestAnimationFrame(() => {
            this._initializeAtroposCards();
        });
    }

    setupThemeChangeListener() {
        const themeToggle = document.querySelector('.theme-toggle'); // или ваш селектор для переключателя темы
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                // Даем небольшую задержку, чтобы тема успела переключиться
                setTimeout(() => {
                    this.reinitializeCards();
                }, 50);
            });
        }
    }

    setupStateSubscriptions() {
        this.stateManager.on('stateChange', ({
            key,
            value
        }) => {
            switch (key) {
                case 'isLoading':
                    this.toggleLoadingState(value);
                    break;
                case 'error':
                    if (value) this.showError(value);
                    break;
            }
        });
    }

    setupAnimations() {
        this.setupTableAnimations();
        this.setupPaginationAnimations();
    }

    setupTableAnimations() {
        const style = document.createElement('style');
        style.textContent = `
                .table-fade-enter {
                    opacity: 0;
                    transform: translateY(-10px);
                }
                .table-fade-enter-active {
                    opacity: 1;
                    transform: translateY(0);
                    transition: opacity 300ms ease-in-out, transform 300ms ease-out;
                }
                .pagination-fade {
                    transition: opacity 200ms ease-in-out;
                }
                .pagination-button-active {
                    transform: scale(0.95);
                    transition: transform 200ms ease-out;
                }
            `;
        document.head.appendChild(style);
    }

    setupPaginationAnimations() {
        document.addEventListener('click', e => {
            if (e.target.matches('.pagination-container button')) {
                e.target.classList.add('pagination-button-active');
                setTimeout(() => {
                    e.target.classList.remove('pagination-button-active');
                }, CONSTANTS.BUTTON_ANIMATION_DURATION);
            }
        });
    }

    initializeUI() {
        this.initializeFilters();
        this.setupEventListeners();
    }

    initializeFilters() {
        this.initializeTypeFilter(); // Инициализация типа предметов
        this.initializeClassFilter(); // Инициализация класс предметов
        this.initializeAdvancedFilters();
        this.initializePerPageSelect();
    }

    // Инициализация типа предметов
    initializeTypeFilter() {
        const typeFilter = document.getElementById('typeFilter');
        if (!typeFilter) return;

        const allowedTypes = this._getAllowedTypes();

        typeFilter.innerHTML = this._createTypeFilterOptions(allowedTypes);
    }
    
    _getAllowedTypes() {
        return TYPE_MAPPINGS[window.location.pathname] ||
            Object.keys(TYPE_DESCRIPTIONS);
    }

    _createTypeFilterOptions(types) {
        const options = ['<option value="">Все</option>'];

        types.forEach(type => {
            options.push(`
                    <option value="${type}">
                        ${TYPE_DESCRIPTIONS[type] || `Тип ${type}`}
                    </option>
                `);
        });

        return options.join('');
    }


    // Инициализация класс предметов
    initializeClassFilter() {
        const classFilter = document.getElementById('typeClassFilter');
        if (!classFilter) return;

        classFilter.innerHTML = this._createClassFilterOptions();
    }

    _createClassFilterOptions() {
        const options = ['<option value="255">Все классы</option>'];
        
        Object.entries(CLASS_DESCRIPTIONS).forEach(([value, label]) => {
            options.push(`
                <option value="${value}">
                    ${label}
                </option>
            `);
        });

        return options.join('');
    }





    initializeAdvancedFilters() {
        const container = document.querySelector('.advanced-filters-grid');
        if (!container) return;

        container.innerHTML = ADVANCED_FILTERS
            .map(this._createFilterCard)
            .join('');
    }

    _createFilterCard(filter) {
        return `
                <div class="filter-card" data-filter="${filter.id}">
                    <div class="filter-card-header">
                        <span class="filter-icon">${filter.icon}</span>
                        <span class="filter-label">${filter.label}</span>
                    </div>
                    <div class="filter-inputs">
                        <div class="input-group">
                            <input type="number" 
                                   class="form-control" 
                                   id="${filter.id}Min" 
                                   placeholder="Мин" 
                                   step="any">
                            <div class="input-group-text">-</div>
                            <input type="number" 
                                   class="form-control" 
                                   id="${filter.id}Max" 
                                   placeholder="Макс" 
                                   step="any">
                        </div>
                    </div>
                </div>
            `;
    }

    initializePerPageSelect() {
        const perPageSelect = document.getElementById('perPageSelect');
        if (!perPageSelect) return;

        perPageSelect.innerHTML = CONSTANTS.PER_PAGE_OPTIONS
            .map(n => `<option value="${n}">${n} на странице</option>`)
            .join('');

        perPageSelect.value = this.stateManager.getState('perPage').toString();
    }

    setupEventListeners() {
        this._setupFilterContainerListener();
        this._setupResetButton();
        this._setupPerPageSelect();
    }

    _setupFilterContainerListener() {
        const container = document.querySelector('.filters-container');
        if (!container) return;

        container.addEventListener('input', event => {
            if (this._isFilterInput(event.target)) {
                this._handleFilterInput();
            }
        });
    }

    _isFilterInput(element) {
        return element.classList.contains('form-control') ||
            element.classList.contains('custom-control-input');
    }

    _handleFilterInput() {
        clearTimeout(this.stateManager.getState('debounceTimer'));

        const timer = setTimeout(
            () => this._triggerFiltersUpdate(),
            CONSTANTS.DEBOUNCE_DELAY
        );

        this.stateManager.setState('debounceTimer', timer);
    }

    _setupResetButton() {
        const resetButton = document.getElementById('resetFilters');
        if (!resetButton) return;

        resetButton.addEventListener('click', () => {
            this._resetAllFilters();
            this._triggerFiltersUpdate();
        });
    }

    _setupCardInteractions() {
        document.querySelectorAll('.item-card').forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.classList.add('is-hovered');
            });
            
            card.addEventListener('mouseleave', () => {
                card.classList.remove('is-hovered');
            });
        });
    }

    _resetAllFilters() {
        document.querySelectorAll('.form-control, .custom-control-input')
            .forEach(input => {
                if (input.id === 'perPageSelect') return;

                if (input.type === 'checkbox') {
                    input.checked = false;
                } else {
                    input.value = '';
                }
            });
    }

    _setupPerPageSelect() {
        const perPageSelect = document.getElementById('perPageSelect');
        if (!perPageSelect) return;

        perPageSelect.addEventListener('change', () => {
            this.stateManager.setState('currentPage', 1);
            this.stateManager.setState('perPage',
                Number(perPageSelect.value));
            this._triggerFiltersUpdate();
        });
    }

    _triggerFiltersUpdate() {
        document.dispatchEvent(new CustomEvent('filtersUpdated'));
    }

    renderItems(items, resources) {
        const tableWrapper = document.querySelector('.table-wrapper');
        if (!tableWrapper) return;
    
        this._animateTableUpdate(tableWrapper, () => {
            const oldTable = tableWrapper.querySelector('table');
            if (oldTable) {
                oldTable.remove();
            }
    
            const gridHtml = items.map((item, index) => {
                // Безопасное извлечение значения класса из пути к изображению
                const classValue = item.IUseClass ? 
                    item.IUseClass.split('/').pop()?.replace('.png', '') || '0' : '0';
    
                return `
                    <div class="atropos" data-index="${index}">
                        <div class="atropos-scale">
                            <div class="atropos-rotate">
                                <div class="atropos-inner" data-class="${classValue}">
                                    <div class="item-card-id" data-atropos-offset="5">
                                        #${item.IID}
                                    </div>
    
                                    <div class="item-card-image" data-atropos-offset="8" data-class="${classValue}">
                                        <img src="${resources[item.IID] || CONSTANTS.FALLBACK_IMAGE}"
                                            alt="${item.IName}"
                                            loading="lazy"
                                            onerror="this.src='${CONSTANTS.FALLBACK_IMAGE}';">
                                    </div>
                                    <div class="item-card-title" data-atropos-offset="8">
                                        <span><img src="${item.IUseClass}" alt="Image description"></span>
                                    </div>
    
                                    <div class="item-card-title" data-atropos-offset="6">
                                        <a href="/item/${item.IID}" class="item-link">${item.IName}</a>
                                    </div>
    
                                    <div class="stat-badges" data-atropos-offset="4">
                                        ${this._generateStatBadges(item)}
                                    </div>
    
                                    <div class="item-card-description" data-atropos-offset="2">
                                        ${item.IDesc || 'Нет описания'}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
    
            tableWrapper.innerHTML = `<div class="items-grid">${gridHtml}</div>`;
            
            requestAnimationFrame(() => {
                this._initializeAtroposCards();
            });
        });
    }












    _initializeAtroposCards() {
        if (!window.Atropos) {
            console.warn('Waiting for Atropos...');
            setTimeout(() => this._initializeAtroposCards(), 100);
            return;
        }
    
        document.querySelectorAll('.atropos').forEach((el, index) => {
            if (el.atroposInstance) {
                el.atroposInstance.destroy();
            }
    
            // Установка индекса для анимации
            el.style.setProperty('--index', index);
    
            // Улучшенная обработка эффекта свечения
            const handleMouseMove = (e) => {
                const rect = el.getBoundingClientRect();
                const x = ((e.clientX - rect.left) / rect.width) * 100;
                const y = ((e.clientY - rect.top) / rect.height) * 100;
                el.style.setProperty('--x', `${x}%`);
                el.style.setProperty('--y', `${y}%`);
            };
    
            el.addEventListener('mousemove', handleMouseMove);
    
            // Улучшенная обработка кликабельности
            const title = el.querySelector('.item-card-title');
            const link = title?.querySelector('a');
            
            if (title && link) {
                // Расширяем область клика
                title.style.cursor = 'pointer';
                
                // Обработка наведения
                title.addEventListener('mouseenter', (e) => {
                    e.stopPropagation();
                    link.style.color = '#3182ce';
                    const beforeElement = window.getComputedStyle(link, '::before');
                    if (beforeElement) {
                        link.classList.add('hover-active');
                    }
                });
    
                title.addEventListener('mouseleave', (e) => {
                    e.stopPropagation();
                    link.style.color = '';
                    link.classList.remove('hover-active');
                });
    
                // Обработка клика
                title.addEventListener('click', (e) => {
                    e.stopPropagation();
                    link.click();
                });
            }
    
            const atroposInstance = Atropos({
                el: el,
                activeOffset: 20,
                shadowScale: 1.05,
                rotateXMax: 8,
                rotateYMax: 8,
                duration: 800,
                shadow: true,
                shadowOffset: 30,
                highlight: true,
                onEnter() {
                    el.classList.add('atropos-active');
                },
                onLeave() {
                    el.classList.remove('atropos-active');
                    // Сброс стилей при уходе мыши
                    el.style.removeProperty('--x');
                    el.style.removeProperty('--y');
                },
                onRotate(e) {
                    // Плавное движение для названия
                    const title = el.querySelector('.item-card-title');
                    if (title) {
                        const slowFactor = 0.3;
                        const x = e.rotateX * slowFactor;
                        const y = e.rotateY * slowFactor;
                        title.style.transform = `translate3d(${y/2}px, ${-x/2}px, 40px)`;
                    }
    
                    // Плавное движение для описания
                    const description = el.querySelector('.item-card-description');
                    if (description) {
                        const ultraSlowFactor = 0.1;
                        const dx = e.rotateX * ultraSlowFactor;
                        const dy = e.rotateY * ultraSlowFactor;
                        description.style.transform = `translate3d(${dy/2}px, ${-dx/2}px, 20px)`;
                    }
                }
            });
    
            el.atroposInstance = atroposInstance;
        });
    }

    destroy() {
        document.querySelectorAll('.atropos').forEach(el => {
            if (el.atroposInstance) {
                el.atroposInstance.destroy();
            }
        });
    }

    _animateTableUpdate(tableBody, updateFn) {
        tableBody.classList.add(CONSTANTS.ANIMATION_CLASSES.FADE_ENTER);

        requestAnimationFrame(() => {
            updateFn();

            tableBody.classList.remove(CONSTANTS.ANIMATION_CLASSES.FADE_ENTER);
            tableBody.classList.add(CONSTANTS.ANIMATION_CLASSES.FADE_ENTER_ACTIVE);

            setTimeout(() => {
                tableBody.classList.remove(
                    CONSTANTS.ANIMATION_CLASSES.FADE_ENTER_ACTIVE
                );
            }, CONSTANTS.TABLE_FADE_DURATION);
        });
    }



    
    _generateStatBadges(item) {
        const badges = [];
        
        // // Класс предмета
        // if (item.IUseClass) {
        //     badges.push(`
        //         <div class="stat-badge" data-atropos-offset="3">
        //             <i class="fas fa-star"></i>
        //             <span><img src="${item.IUseClass}" alt="Image description"></span>
        //         </div>
        //     `);
        // }

        // Уровень предмета
        if (item.ILevel) {
            badges.push(`
                <div class="stat-badge" data-atropos-offset="3">
                    <i class="fas fa-star"></i>
                    <span>Ур. ${item.ILevel}</span>
                </div>
            `);
        }
        
        // Вес предмета
        if (item.IWeight) {
            badges.push(`
                <div class="stat-badge" data-atropos-offset="3">
                    <i class="fas fa-weight-hanging"></i>
                    <span>${item.IWeight}</span>
                </div>
            `);
        }
        
        // Характеристики атаки/защиты
        if (item.IDHIT) {
            badges.push(`
                <div class="stat-badge" data-atropos-offset="3">
                    <i class="fas fa-fist-raised"></i>
                    <span>ATK ${item.IDHIT}</span>
                </div>
            `);
        }
        
        if (item.IDDD) {
            badges.push(`
                <div class="stat-badge" data-atropos-offset="3">
                    <i class="fas fa-shield-alt"></i>
                    <span>DEF ${item.IDDD}</span>
                </div>
            `);
        }
        
        return badges.join('');
    }


    _generateTableHeaders() {
        return `
                    <th>🖼️</th>
                    <th>Название</th>
                    <th>Описание</th>
                    <th>Вес</th>
                    <th>Класс</th>
            `;
    }

    _generateItemRow(item, resources) {
        return `
                <tr>
                    <td>
                        <div class="hover-text-wrapper">
                            <a href="/item/${item.IID}">
                                <img src="${resources[item.IID] || CONSTANTS.FALLBACK_IMAGE}"
                                    alt="${item.IName}"
                                    title="${item.IName}"
                                    width="48"
                                    height="48"
                                    loading="lazy"
                                    class="item-image"
                                    onerror="this.src='${CONSTANTS.FALLBACK_IMAGE}';">
                            </a>
                            <div class="hover-text">[${item.IID}] ${item.IName}</div>
                        </div>
                    </td>
                    <td>
                        <div class="item-name">
                            <a href="/item/${item.IID}">${item.IName}</a>
                        </div>
                    </td>
                    <td class="item-desc">${item.IDesc || 'Нет описания'}</td>
                    <td>${item.IWeight || 'N/A'}</td>
                    <td><img src="${item.IUseClass || 'N/A'}" alt="${item.IName}"></td>
                </tr>
            `;
    }

    createPagination(total, currentPage, perPage) {
        const paginationContainer = document.querySelector('.pagination-container');
        if (!paginationContainer) return;

        const totalPages = Math.ceil(total / perPage);

        paginationContainer.style.opacity = '0';
        paginationContainer.innerHTML = this._generatePaginationHTML(
            totalPages, currentPage
        );

        requestAnimationFrame(() => {
            paginationContainer.style.opacity = '1';
        });
    }

    _generatePaginationHTML(totalPages, currentPage) {
        const buttons = [];

        // Previous button
        buttons.push(this._createPaginationButton(
            'Предыдущая',
            currentPage - 1,
            currentPage === 1
        ));

        // Page numbers
        for (let i = 1; i <= totalPages; i++) {
            if (this._shouldShowPageNumber(i, currentPage, totalPages)) {
                buttons.push(this._createPaginationButton(
                    i.toString(),
                    i,
                    false,
                    i === currentPage
                ));
            } else if (i === currentPage - 3 || i === currentPage + 3) {
                buttons.push('<span class="pagination-ellipsis">...</span>');
            }
        }

        // Next button
        buttons.push(this._createPaginationButton(
            'Следующая',
            currentPage + 1,
            currentPage === totalPages
        ));

        return buttons.join('');
    }

    _shouldShowPageNumber(pageNum, currentPage, totalPages) {
        return pageNum === 1 ||
            pageNum === totalPages ||
            (pageNum >= currentPage - CONSTANTS.PAGINATION_RADIUS &&
                pageNum <= currentPage + CONSTANTS.PAGINATION_RADIUS);
    }

    _createPaginationButton(text, pageNum, isDisabled, isActive = false) {
        const className = isActive ? 'btn-primary' : 'btn-secondary';
        const disabled = isDisabled ? 'disabled' : '';
        return `
                <button class="btn ${className} ${disabled}"
                        onclick="app.applyFilters(${pageNum})"
                        ${disabled}>
                    ${text}
                </button>
            `;
    }

    updateTotalCount(count) {
        const totalCount = document.getElementById('totalCount');
        if (totalCount) {
            totalCount.textContent = `Найдено предметов: ${count}`;
        }
    }

    updateURL(params) {
        const url = new URL(window.location.href);
        url.search = new URLSearchParams(params).toString();
        history.pushState({}, '', url);
    }

    toggleLoadingState(isLoading) {
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (!loadingOverlay) return;

        if (isLoading) {
            loadingOverlay.classList.add('show');
        } else {
            setTimeout(() => {
                loadingOverlay.classList.remove('show');
            }, CONSTANTS.LOADING_FADE_DELAY);
        }
    }

    showError(message) {
        const errorMessage = document.getElementById('errorMessage');
        if (!errorMessage) return;

        errorMessage.textContent = `Произошла ошибка: ${message}`;
        errorMessage.classList.add('show');

        setTimeout(() => {
            errorMessage.classList.remove('show');
        }, CONSTANTS.ERROR_DISPLAY_TIME);
    }
}

// Main Application Class
class ItemFilterApp {
    constructor() {
        this.stateManager = new StateManager();
        this.dataService = new ItemDataService(this.stateManager);
        this.uiManager = new ItemUIManager(this.stateManager);
    }

    async initialize() {
        await this.dataService.fetchData();
        this.uiManager.initializeUI();
        this.setupEventListeners();
        this.applyFilters(1);
        initializeSearch();
    }

    setupEventListeners() {
        document.addEventListener('filtersUpdated', () => {
            this.applyFilters(1);
        });
    }

    async applyFilters(page = 1) {
        const cachedData = this.stateManager.getState('cachedData');
        if (!cachedData) return;

        const filters = ItemFilterManager.collectFilters();
        const filteredData = ItemFilterManager.filterData(cachedData.items, filters);

        const perPage = this.stateManager.getState('perPage');
        const paginatedData = this._paginateData(filteredData, page, perPage);

        this.stateManager.setState('currentPage', page);
        this.uiManager.updateTotalCount(filteredData.length);
        this.uiManager.renderItems(paginatedData, cachedData.resources);
        this.uiManager.createPagination(filteredData.length, page, perPage);
        this.uiManager.updateURL(filters);
    }

    _paginateData(data, page, perPage) {
        const start = (page - 1) * perPage;
        return data.slice(start, start + perPage);
    }
}

// Initialize application
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new ItemFilterApp();
    app.initialize();
});