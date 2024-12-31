function toggleItems(button, event) {
    // Предотвращаем всплытие события
    event.preventDefault();
    event.stopPropagation();

    const header = button.closest('.chest-header');
    const itemsList = header.nextElementSibling;
    const card = header.closest('.chest-card');
    
    // Если кликнули по уже активной карточке
    if (button.classList.contains('active')) {
        button.classList.remove('active');
        itemsList.classList.remove('active');
        return;
    }

    // Закрываем все остальные
    document.querySelectorAll('.toggle-button.active').forEach(btn => {
        if (btn !== button) {
            btn.classList.remove('active');
            btn.closest('.chest-card').querySelector('.items-list').classList.remove('active');
        }
    });

    // Открываем текущую
    button.classList.add('active');
    itemsList.classList.add('active');
    
    // Инициализируем цвета для шансов
    initializeRarityClasses(itemsList);
    initializeImageZoom();
}

function initializeRarityClasses(container) {
    container.querySelectorAll('.item-row').forEach(row => {
        const fill = row.querySelector('.chance-fill');
        const chance = parseInt(fill.dataset.chance);
        const badge = row.querySelector('.rarity-badge');
        const container = row.querySelector('.chance-container');
        
        let rarityClass, rarityText;
        if (chance >= 1000) {
            rarityClass = 'rarity-common';
            rarityText = 'Обычный';
        } else if (chance >= 500) {
            rarityClass = 'rarity-rare';
            rarityText = 'Редкий';
        } else if (chance >= 100) {
            rarityClass = 'rarity-epic';
            rarityText = 'Эпический';
        } else {
            rarityClass = 'rarity-legendary';
            rarityText = 'Легендарный';
        }
        
        container.className = 'chance-container ' + rarityClass;
        badge.textContent = rarityText;
        badge.className = 'rarity-badge ' + rarityClass;
    });
}


let currentItems = [];
let currentMonsterName = '';

function openEditor(mid) {
    const modal = document.getElementById('chestEditor');
    
    fetch(`/api/chest-loot/${mid}`)
        .then(response => response.json())
        .then(data => {
            currentItems = data.items;

            if (currentItems && currentItems.length > 0) {
                const firstItem = currentItems[0];
                currentMonsterName = firstItem.MName;
                currentMonsterPic = firstItem.MID_pic;
            } else {
                currentMonsterName = 'Неизвестно';
                currentMonsterPic = 'https://raw.githubusercontent.com/Aksel911/R2-HTML-DB/main/static/no_monster/no_monster_image.png';
            }

            const currentMIDElement = document.getElementById('currentMID');
            currentMIDElement.innerHTML = `
                <h1><img src="${currentMonsterPic}" 
                        class="monster-pic" 
                        alt="${currentMonsterName}" 
                        onerror="this.onerror=null; this.src='https://raw.githubusercontent.com/Aksel911/R2-HTML-DB/main/static/no_monster/no_monster_image.png';" /></h1>
                [${mid}] <a href="/monster/${mid}" class="item-name">${currentMonsterName}</a>
            `;
            
            renderItems();
            modal.style.display = 'block';
        })
        .catch(error => console.error('Ошибка загрузки данных:', error));
    
    if (document.body.classList.contains('dark-theme')) {
        modal.classList.add('dark-theme');
    }
}


function closeEditor() {
    const modal = document.getElementById('chestEditor');
    modal.style.display = 'none';
    currentItems = [];
    document.getElementById('itemsList').innerHTML = '';
}

// Обновляем HTML структуру field-labels
document.querySelector('.field-labels').innerHTML = `
    <div class="field-label"></div>
    <div class="field-label">ID предмета</div>
    <div class="field-label">Название предмета</div>
    <div class="field-label">Количество</div>
    <div class="field-label">Шанс (%)</div>
    <div class="field-label">Тип предмета</div>
    <div class="field-label"></div>
    `;

// Обновляем функцию renderItems
function renderItems() {
    const itemsList = document.getElementById('itemsList');
    
    itemsList.innerHTML = currentItems.map((item, index) => `
        <div class="item-edit-row" data-status="${item.status}">
            <img src="${item.itemPic}"
                    class="item-pic"
                    alt="${item.itemName}"
                    onerror="this.onerror=null; this.src='https://raw.githubusercontent.com/Aksel911/R2-HTML-DB/main/static/no_monster/no_monster_image.png';">
            <input type="text" value="${item.itemId}" required>
            <input type="text" value="${item.itemName || ''}">
            <input type="number" value="${item.count}" min="1" required>
            <input type="number" value="${item.dropChance}" min="0" max="100" required>
            <select onchange="updateRowStatus(this)">
                <option value="0" ${item.status === 0 ? 'selected' : ''}>Проклятый</option>
                <option value="1" ${item.status === 1 ? 'selected' : ''}>Обычный</option>
                <option value="2" ${item.status === 2 ? 'selected' : ''}>Благословенный</option>
            </select>
            <button type="button" onclick="removeItem(${index})" class="remove-item">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `).join('');
}


function updateRowStatus(selectElement) {
    const row = selectElement.closest('.item-edit-row');
    row.dataset.status = selectElement.value;
}

async function addNewItem() {
    const newItemId = document.getElementById('newItemId').value;
    const newItemStatus = document.getElementById('newItemStatus');
    
    if (!newItemId) {
        alert('Пожалуйста, введите ID предмета');
        return;
    }

    try {
        // Загружаем информацию о предмете с сервера
        const response = await fetch(`/api/item-info/${newItemId}`);
        const itemInfo = await response.json();

        const newItem = {
            itemId: newItemId,
            itemName: document.getElementById('newItemName').value || itemInfo.itemName,
            itemPic: itemInfo.itemPic,
            count: parseInt(document.getElementById('newItemCount').value) || 1,
            dropChance: parseInt(document.getElementById('newItemChance').value),
            status: parseInt(newItemStatus.value)
        };
        
        if (!newItem.count || isNaN(newItem.dropChance)) {
            alert('Пожалуйста, заполните все обязательные поля');
            return;
        }
        
        currentItems.push(newItem);
        renderItems();
        
        // Очистка полей
        document.getElementById('newItemId').value = '';
        document.getElementById('newItemName').value = '';
        document.getElementById('newItemCount').value = '1';
        document.getElementById('newItemChance').value = '';
        newItemStatus.value = '1';
    } catch (error) {
        console.error('Error fetching item info:', error);
        alert('Ошибка при получении информации о предмете');
    }
}

function removeItem(index) {
    if (confirm('Вы уверены, что хотите удалить этот предмет?')) {
        currentItems.splice(index, 1);
        renderItems();
    }
}

async function saveChestLoot(event) {
    event.preventDefault();
    const mid = document.getElementById('currentMID').textContent;
    
    // Собираем данные из всех строк с предметами
    const itemRows = document.querySelectorAll('.item-edit-row');
    const currentItems = Array.from(itemRows).map(row => ({
        itemId: row.querySelector('input[type="text"]:nth-child(1)').value,
        itemName: row.querySelector('input[type="text"]:nth-child(2)').value,
        count: parseInt(row.querySelector('input[type="number"]:nth-child(3)').value),
        dropChance: parseInt(row.querySelector('input[type="number"]:nth-child(4)').value),
        status: parseInt(row.querySelector('select').value)
    }));

    try {
        const response = await fetch('/api/save-chest-loot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                mid: parseInt(mid),
                items: currentItems
            }),
        });
        
        if (response.ok) {
            alert('Изменения сохранены успешно!');
            closeEditor();
            location.reload();
        } else {
            const error = await response.json();
            alert(`Ошибка: ${error.message || 'Не удалось сохранить изменения'}`);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Ошибка сохранения. Пожалуйста, попробуйте снова.');
    }
}

// Закрытие модального окна при клике вне его
window.onclick = function(event) {
    const modal = document.getElementById('chestEditor');
    if (event.target === modal) {
        closeEditor();
    }
}



