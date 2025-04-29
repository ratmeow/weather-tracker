// main.js

// Глобальные переменные для состояния авторизации
let isAuthenticated = localStorage.getItem('isAuthenticated') === 'true' || false;
let cachedUserName = localStorage.getItem('userName') || null;

// Константы для API и селекторов
const API_USER = '/api/user';
const API_LOCATIONS = '/api/locations';
const API_SEARCH = '/api/search';
const API_LOGOUT = '/api/logout';
const SEARCH_INPUT = '.location-search-input-group input';
const NAV_SECTION = 'nav-auth-section';
const USER_NAME_ELEMENT = 'user-name';

function showError(message) {
    const errorContainer = document.querySelector('#error-container');
    errorContainer.innerHTML = ''; // Очищаем предыдущие ошибки

    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger alert-dismissible fade show';
    errorDiv.role = 'alert';
    errorDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" aria-label="Close"></button>
    `;
    errorContainer.appendChild(errorDiv);

    // Ручное закрытие
    const closeButton = errorDiv.querySelector('.btn-close');
    closeButton.addEventListener('click', () => {
        errorDiv.classList.remove('show');
        setTimeout(() => errorDiv.remove(), 150);
    });
}

// Функция для обработки выхода или неавторизованного состояния
function resetAuthState() {
    isAuthenticated = false;
    cachedUserName = null;
    localStorage.removeItem('isAuthenticated');
    localStorage.removeItem('userName');
    updateNavMenu();
}

// Функция для обновления навигационного меню
function updateNavMenu() {
    const navSection = document.getElementById(NAV_SECTION);
    if (isAuthenticated && cachedUserName) {
        navSection.innerHTML = `
            <span class="navbar-text me-3" id="${USER_NAME_ELEMENT}">${cachedUserName}</span>
            <button class="btn btn-outline-danger" id="sign-out-btn">Sign out</button>
        `;
        document.getElementById('sign-out-btn').addEventListener('click', async () => {
            try {
                const response = await fetch(API_LOGOUT, { method: 'POST', credentials: 'include' });
                if (response.ok) {
                    resetAuthState();
                    window.location.href = '/';
                }
            } catch (error) {
                console.error('Logout error:', error);
                showError('Failed to sign out. Please try again.');
            }
        });
    } else {
        navSection.innerHTML = `
            <a href="/login" class="btn btn-outline-primary me-2">Sign In</a>
            <a href="/register" class="btn btn-outline-success">Sign Up</a>
        `;
    }
}

async function loadWeatherData() {
    try {
        const response = await fetch('/api/locations', { credentials: 'include' });
        if (!response.ok) {
            if (response.status === 401) {
                resetAuthState();
                return;
            }
            throw new Error(`Failed to fetch data: ${response.status}`);
        }
        isAuthenticated = true;
        localStorage.setItem('isAuthenticated', 'true');

        const data = await response.json();
        const container = document.querySelector('#page-content .container .row');
        container.innerHTML = '';

        data.forEach(location => {
            const card = createWeatherCard(location);
            container.appendChild(card);
        });
    } catch (error) {
        console.error('Error loading weather data:', error);
        if (!error.message.includes('401')) {
            showError('Failed to load weather data. Please try again later.');
        }
    }
}

// Функция для поиска локаций
async function searchLocations() {
    const input = document.querySelector(SEARCH_INPUT);
    const locationName = input.value.trim();

    if (!locationName) {
        showError('Please enter a location name.');
        return;
    }

    try {
        const response = await fetch(`${API_SEARCH}?location_name=${encodeURIComponent(locationName)}`, { credentials: 'include' });
        if (!response.ok) {
            if (response.status === 401) {
                resetAuthState();
                return;
            }
            throw new Error(`Failed to fetch data: ${response.status}`);
        }

        const data = await response.json();
        const container = document.querySelector('#page-content .row');
        const errorContainer = document.querySelector('#error-container');

        // Очищаем ошибку перед отображением результата
        errorContainer.innerHTML = '';
        container.innerHTML = ''; // Очищаем карточки

        if (data.length === 0) {
            container.innerHTML = '<p class="text-center">No locations found.</p>';
        } else {
            data.forEach(location => {
                const card = createLocationCard(location);
                container.appendChild(card);
            });
        }
        const newUrl = `/search?location_name=${encodeURIComponent(locationName)}`;
        window.history.pushState({ locationName }, '', newUrl);
    } catch (error) {
        console.error('Error searching for locations:', error);
        if (!error.message.includes('401')) {
            showError('Failed to search for locations. Please try again later.');
        }
    }
}

// Вспомогательная функция для поиска по значению
async function searchLocationsWithValue(locationName) {
    try {
        const response = await fetch(`${API_SEARCH}?location_name=${encodeURIComponent(locationName)}`, { credentials: 'include' });
        if (!response.ok) {
            if (response.status === 401) {
                resetAuthState();
                return;
            }
            throw new Error(`Failed to fetch data: ${response.status}`);
        }

        const data = await response.json();
        const container = document.querySelector('#page-content .row');
        container.innerHTML = '';

        if (data.length === 0) {
            container.innerHTML = '<p class="text-center">No locations found.</p>';
        } else {
            data.forEach(location => {
                const card = createLocationCard(location);
                container.appendChild(card);
            });
        }
    } catch (error) {
        console.error('Error searching for locations:', error);
    }
}

// Функция для отправки POST-запроса на добавление локации
async function addLocation(name, lat, lon) {
    const locationData = { name, latitude: lat, longitude: lon };

    try {
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(locationData),
            credentials: 'include'
        });

        if (!response.ok) {
            if (response.status === 401) {
                resetAuthState();
                showError('To add locations, you need to log in.');
                return;
            }
                    if (response.status === 400) {
                const errorData = await response.json();
                const errorMessage = errorData.message
                showError(errorMessage);
                return;
            }
            throw new Error(`Failed to add location: ${response.status}`);
        }

        window.location.href = '/';
    } catch (error) {
        console.error('Error adding location:', error);
        if (!error.message.includes('401')) {
            showError('Failed to add location. Please try again later.');
        }
    }
}

async function deleteLocation(name, lat, lon) {
    const locationData = { name, latitude: lat, longitude: lon };
    const queryString = new URLSearchParams(locationData).toString();
    const url = `/api/?${queryString}`;
    try {
        const response = await fetch(url, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include'
        });

        if (!response.ok) {
            if (response.status === 401) {
                resetAuthState();
                return;
            }
            throw new Error(`Failed to add location: ${response.status}`);
        }

        window.location.href = '/';
    } catch (error) {
        console.error('Error deleting location:', error);
        if (!error.message.includes('401')) {
            showError('Failed to delete location. Please try again later.');
        }
    }
}

// Обработчик события popstate
window.addEventListener('popstate', (event) => {
    const urlParams = new URLSearchParams(window.location.search);
    const locationName = urlParams.get('location_name');

    if (locationName) {
        searchLocationsWithValue(locationName);
    } else {
        loadWeatherData();
    }
});

// Обработчик кнопки поиска
document.querySelector('.btn-outline-success').addEventListener('click', searchLocations);

// Обработчик загрузки страницы
document.addEventListener('DOMContentLoaded', async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const locationName = urlParams.get('location_name');
    const input = document.querySelector(SEARCH_INPUT);

    if (locationName) {
        input.value = locationName;
        searchLocationsWithValue(locationName);
    } else {
        loadWeatherData();
    }
    updateNavMenu();
});