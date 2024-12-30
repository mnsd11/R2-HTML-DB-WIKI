// Constants and configurations
const CONSTANTS = {
    DEBOUNCE_DELAY: 300,
    DEFAULT_PER_PAGE: 25,
    FALLBACK_IMAGE: 'https://raw.githubusercontent.com/Aksel911/R2-HTML-DB/main/static/no_monster/no_monster_image.png',
    PAGINATION_RADIUS: 2,
    ERROR_DISPLAY_TIME: 5000
};

const MONSTER_CLASS_DESCRIPTIONS = {
    1: 'A класс',
    2: 'B класс',
    3: 'C класс',
    4: 'D класс',
    5: 'E класс',
    6: 'F класс',
    7: 'G класс',
    8: 'H класс',
    9: 'I класс',
    10: 'J класс',
    11: 'K класс',
    12: 'L класс',
    13: 'M класс',
    14: 'N класс',
    15: 'O класс',
    16: 'P класс',
    17: 'Q класс',
    18: 'R класс',
    19: 'S класс',
    20: 'T класс',
    21: 'U класс',
    22: 'V класс',
    23: 'NPC',
    24: 'W класс',
    25: 'X класс',
    26: 'Особый Монстр',
    27: 'Событие',
    28: 'Именной',
    29: 'Босс',
    31: 'S',
    32: 'Налетчики',
    33: 'Эпик Мобы (дем)',
    34: 'Эпик Боссы (дем)',
    35: 'Статуя',
    36: 'Последователи (ХТЖ Боссы)',
    37: 'Разъяренные Боссы',
    38: 'Падшие Боссы'
};

const MONSTER_TYPE_MAPPINGS = {
    '/monster_regular': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22],
    '/monster_boss': [29, 38, 37, 36, 34],
    '/monster_raidboss': [26],
    '/monster_imennoy': [28],
    '/monster_npc': [23],
    '/monster_event': [27]
};

const RACE_TYPES = {
    1: 'Человек',
    2: 'Нежить',
    3: 'Демон',
    4: 'Животное'
};

const ADVANCED_FILTERS = [{
        id: 'MHIT',
        label: 'Точность',
        icon: '🎯'
    },
    {
        id: 'MMinD',
        label: 'Мин. урон',
        icon: '⚔️'
    },
    {
        id: 'MMaxD',
        label: 'Макс. урон',
        icon: '⚔️'
    },
    {
        id: 'MHP',
        label: 'HP',
        icon: '❤️'
    },
    {
        id: 'MMP',
        label: 'MP',
        icon: '💧'
    },
    {
        id: 'MAttackRateOrg',
        label: 'Скорость атаки',
        icon: '⚡'
    },
    {
        id: 'MMoveRateOrg',
        label: 'Скорость передвижения',
        icon: '🏃'
    },
    {
        id: 'MMoveRange',
        label: 'Радиус преследования',
        icon: '📏'
    },
    {
        id: 'mSightRange',
        label: 'Радиус обзора',
        icon: '👁️'
    },
    {
        id: 'mAttackRange',
        label: 'Дальность атаки',
        icon: '🎯'
    },
    {
        id: 'mSkillRange',
        label: 'Дальность навыков',
        icon: '✨'
    },
    {
        id: 'mScale',
        label: 'Размер модели',
        icon: '📐'
    },
    {
        id: 'mHPRegen',
        label: 'Реген HP',
        icon: '♥️'
    },
    {
        id: 'mMPRegen',
        label: 'Реген MP',
        icon: '💫'
    },
    {
        id: 'mVolitionOfHonor',
        label: 'Очки чести',
        icon: '🏆'
    }
];

// State Management
class StateManager {
    constructor() {
        this._state = {
            currentPage: 1,
            cachedData: null,
            debounceTimer: null,
            isLoading: false,
            error: null
        };

        this._subscribers = new Set();
    }

    setState(key, value) {
        const oldValue = this._state[key];
        this._state[key] = value;

        if (oldValue !== value) {
            this._notifySubscribers(key, value, oldValue);
        }
    }

    getState(key) {
        return this._state[key];
    }

    subscribe(callback) {
        this._subscribers.add(callback);
        return () => this._subscribers.delete(callback);
    }

    _notifySubscribers(key, newValue, oldValue) {
        this._subscribers.forEach(callback =>
            callback(key, newValue, oldValue));
    }
}

// Data Service
class DataService {
    constructor(stateManager) {
        this.stateManager = stateManager;
    }

    async fetchData(forceReload = false) {
        const cachedData = this.stateManager.getState('cachedData');
        if (cachedData && !forceReload) {
            return cachedData;
        }

        this.stateManager.setState('isLoading', true);

        try {
            const response = await fetch(`${window.location.pathname}?all=1`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            if (data.error) {
                throw new Error(data.error);
            }

            this.stateManager.setState('cachedData', data);
            return data;

        } catch (error) {
            this.stateManager.setState('error', error.message);
            return null;
        } finally {
            this.stateManager.setState('isLoading', false);
        }
    }
}

// Filter Logic
class FilterManager {
    static collectFilters() {
        const filters = {};

        document.querySelectorAll('.form-control, .custom-control-input').forEach(input => {
            if (input.id === 'perPageSelect') return;

            let value = input.type === 'checkbox' ? input.checked : input.value.trim();

            if (value !== '' && value !== false) {
                if (input.type === 'checkbox' && value === true) {
                    value = '1';
                }

                // Map input IDs to correct field names
                switch (input.id) {
                    case 'levelMin':
                        filters['mLevelMin'] = value;
                        break;
                    case 'levelMax':
                        filters['mLevelMax'] = value;
                        break;
                    case 'expMin':
                        filters['MExpMin'] = value;
                        break;
                    case 'expMax':
                        filters['MExpMax'] = value;
                        break;
                    case 'tickMin':
                        filters['mTickMin'] = value;
                        break;
                    case 'tickMax':
                        filters['mTickMax'] = value;
                        break;
                    default:
                        filters[input.id] = value;
                }
            }
        });

        // Debug log
        //console.log('Collected filters:', filters);
        return filters;
    }


    static filterData(monsters, filters) {
        return monsters.filter(monster =>
            this._applyAllFilters(monster, filters));
    }

    static _applyAllFilters(monster, filters) {
        return Object.entries(filters).every(([key, value]) => {
            if (!value || value === '') return true;

            // Let server handle tick filtering
            if (key === 'mTickMin' || key === 'mTickMax') return true;

            if (key.endsWith('Min') || key.endsWith('Max')) {
                return this._applyRangeFilter(monster, key, value);
            }
            return this._applyBasicFilter(monster, key, value);
        });
    }

    static _applyRangeFilter(monster, key, value) {
        // Map filter keys to monster properties
        let baseKey = key.replace(/(Min|Max)$/, '');
        const isMin = key.endsWith('Min');
        let monsterValue;

        switch (baseKey) {
            case 'mLevel':
                monsterValue = monster.mLevel;
                break;
            case 'MExp':
                monsterValue = monster.MExp;
                break;
            default:
                monsterValue = monster[baseKey];
        }

        monsterValue = Number(monsterValue) || 0;
        const filterValue = Number(value);

        if (isNaN(filterValue)) return true;
        return isMin ? monsterValue >= filterValue : monsterValue <= filterValue;
    }

    static _applyBasicFilter(monster, key, value) {
        switch (key) {
            case 'classFilter':
                return monster.MClass === Number(value);
            case 'raceFilter':
                return monster.MRaceType === Number(value);
            case 'attackTypeFilter':
                return monster.mAttackType === Number(value);
            case 'eventMonsterFilter':
                return Boolean(monster.mIsEvent);
            case 'testMonsterFilter':
                return Boolean(monster.mIsTest);
            case 'showHpFilter':
                return Boolean(monster.mIsShowHp);
            default:
                return true;
        }
    }
}

// UI Management
class UIManager {
    constructor(stateManager) {
        this.stateManager = stateManager;
        this.setupStateSubscriptions();
    }

    setupStateSubscriptions() {
        this.stateManager.subscribe((key, value) => {
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

    initializeUI() {
        this.initializeAdvancedFilters();
        this.initializePerPageSelect();
        this.setupEventListeners();
        this.initializeTypeFilter();
    }

    initializeAdvancedFilters() {
        const container = document.querySelector('.advanced-filters-grid');
        if (!container) return;

        container.innerHTML = ADVANCED_FILTERS
            .map(this.createFilterCard)
            .join('');
    }

    createFilterCard(filter) {
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

    setupEventListeners() {
        const filtersContainer = document.querySelector('.filters-container');
        if (filtersContainer) {
            filtersContainer.addEventListener('input', this._handleFilterInput.bind(this));
        }

        const resetButton = document.getElementById('resetFilters');
        if (resetButton) {
            resetButton.addEventListener('click', this._handleResetFilters.bind(this));
        }

        const perPageSelect = document.getElementById('perPageSelect');
        if (perPageSelect) {
            perPageSelect.addEventListener('change', () => {
                this.stateManager.setState('currentPage', 1);
                this._triggerFiltersUpdate();
            });
        }
    }

    _handleFilterInput(event) {
        if (event.target.classList.contains('form-control') ||
            event.target.classList.contains('custom-control-input')) {

            clearTimeout(this.stateManager.getState('debounceTimer'));

            const timer = setTimeout(
                () => this._triggerFiltersUpdate(),
                CONSTANTS.DEBOUNCE_DELAY
            );

            this.stateManager.setState('debounceTimer', timer);
        }
    }

    _handleResetFilters() {
        document.querySelectorAll('.form-control, .custom-control-input')
            .forEach(input => {
                if (input.type === 'checkbox') {
                    input.checked = false;
                } else if (input.id !== 'perPageSelect') {
                    input.value = '';
                }
            });

        this._triggerFiltersUpdate();
    }

    _triggerFiltersUpdate() {
        const event = new CustomEvent('filtersUpdated');
        document.dispatchEvent(event);
    }

    initializeTypeFilter() {
        const typeFilter = document.getElementById('classFilter');
        if (!typeFilter) return;

        const allowedTypes = this._getAllowedTypes();
        typeFilter.innerHTML = '<option value="">Все</option>';

        (allowedTypes.length ? allowedTypes : Object.keys(MONSTER_CLASS_DESCRIPTIONS))
        .forEach(type => {
            const option = document.createElement('option');
            option.value = type;
            option.textContent = MONSTER_CLASS_DESCRIPTIONS[type] || `Класс ${type}`;
            typeFilter.appendChild(option);
        });
    }

    _getAllowedTypes() {
        return MONSTER_TYPE_MAPPINGS[window.location.pathname] || [];
    }

    initializePerPageSelect() {
        const perPageSelect = document.getElementById('perPageSelect');
        if (!perPageSelect) return;

        const options = [10, 25, 50, 75, 100];
        perPageSelect.innerHTML = options
            .map(n => `<option value="${n}">${n} на странице</option>`)
            .join('');

        perPageSelect.value = CONSTANTS.DEFAULT_PER_PAGE.toString();
    }

    renderMonsters(monsters) {
        const tableBody = document.querySelector('table tbody');
        if (!tableBody) return;
        const cachedData = this.stateManager.getState('cachedData');

        const monstersHTML_table_headers = '<th>🖼️</th>\n\t<th>Название</th>\n\t<th>Уровень</th>\n\t<th>Класс</th>\n\t<th>MExp</th>\n\t<th>MHP</th>\n\t<th>MRaceType</th>';

        const monstersHTML = monsters
            .map(monster => this._createMonsterRow(monster, cachedData.resources))
            .join('');

        tableBody.innerHTML = monstersHTML_table_headers + monstersHTML;
    }

    _createMonsterRow(monster, resources) {
        return `
                <tr>
                    <td>
                        <div class="hover-text-wrapper">
                            <a href="/monster/${monster.MID}">
                                <img src="${resources[monster.MID] || CONSTANTS.FALLBACK_IMAGE}"
                                    alt="${monster.MName}"
                                    title="${monster.MName}"
                                    width="48"
                                    height="48"
                                    loading="lazy"
                                    class="monster-image"
                                    onerror="this.src='${CONSTANTS.FALLBACK_IMAGE}';">
                            </a>
                            <div class="hover-text">[${monster.MID}] ${monster.MName}</div>
                        </div>
                    </td>
                    <td>
                        <div class="monster-name">
                            <a href="/monster/${monster.MID}">${monster.MName}</a>
                        </div>
                    </td>
                    <td>${monster.mLevel || '0'}</td>
                    <td>${MONSTER_CLASS_DESCRIPTIONS[monster.MClass] || 'N/A'}</td>
                    <td>${monster.MExp || '0'}</td>
                    <td>${monster.MHP || 'N/A'}</td>
                    <td>${RACE_TYPES[monster.MRaceType] || 'N/A'}</td>
                </tr>
            `;
    }

    createPagination(total, currentPage, perPage) {
        const paginationContainer = document.querySelector('.pagination-container');
        if (!paginationContainer) return;

        const totalPages = Math.ceil(total / perPage);
        const paginationHTML = [];

        // Previous button
        paginationHTML.push(this._createPaginationButton(
            'Предыдущая',
            currentPage - 1,
            currentPage === 1
        ));

        // Page numbers
        for (let i = 1; i <= totalPages; i++) {
            if (this._shouldShowPageNumber(i, currentPage, totalPages)) {
                paginationHTML.push(this._createPaginationButton(
                    i.toString(),
                    i,
                    false,
                    i === currentPage
                ));
            } else if (i === currentPage - 3 || i === currentPage + 3) {
                paginationHTML.push('<span class="pagination-ellipsis">...</span>');
            }
        }

        // Next button
        paginationHTML.push(this._createPaginationButton(
            'Следующая',
            currentPage + 1,
            currentPage === totalPages
        ));

        paginationContainer.innerHTML = paginationHTML.join('');
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
            totalCount.textContent = `Найдено монстров: ${count}`;
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
            }, 500);
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
class MonsterFilterApp {
    constructor() {
        this.stateManager = new StateManager();
        this.dataService = new DataService(this.stateManager);
        this.uiManager = new UIManager(this.stateManager);
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

        const filters = FilterManager.collectFilters();
        const filteredData = FilterManager.filterData(cachedData.monsters, filters);
        const perPage = this._getPerPage();

        this.stateManager.setState('currentPage', page);

        const paginatedData = this._paginateData(filteredData, page, perPage);

        this.uiManager.updateTotalCount(filteredData.length);
        this.uiManager.renderMonsters(paginatedData);
        this.uiManager.createPagination(filteredData.length, page, perPage);
        this.uiManager.updateURL(filters);
    }

    _getPerPage() {
        return Number(document.getElementById('perPageSelect')?.value) ||
            CONSTANTS.DEFAULT_PER_PAGE;
    }

    _paginateData(data, page, perPage) {
        const start = (page - 1) * perPage;
        return data.slice(start, start + perPage);
    }
}


// Filter Manager with search support
FilterManager.filterData = function(data, filters) {
    const isMonsterPage = $('.monster-image').length > 0;
    const searchId = isMonsterPage ? '#monsterSearch' : '#itemSearch';
    const searchTerm = document.querySelector(searchId)?.value.trim().toLowerCase();

    // Apply search filter before other filters
    let filteredData = data;
    if (searchTerm) {
        filteredData = data.filter(item => {
            const id = isMonsterPage ? item.MID : item.IID;
            const name = isMonsterPage ? item.MName : item.IName;
            const matchesId = id.toString().toLowerCase().includes(searchTerm);
            const matchesName = name.toLowerCase().includes(searchTerm);
            return matchesId || matchesName;
        });
    }

    // Apply remaining filters
    return filteredData.filter(item => 
        FilterManager._applyAllFilters(item, filters));
};




// Initialize application
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new MonsterFilterApp();
    app.initialize();
});