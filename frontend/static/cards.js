// cards.js

// Функция для создания карточки погоды
function createWeatherCard(location) {
    const card = document.createElement('div');
    card.className = 'col-12 col-lg-3 col-md-6 mb-4';

    const weatherIconClass = getWeatherIconClass(location.mainState);
    const flagEmoji = getCountryFlagEmoji(location.country);
    const tempDifference = Math.round(location.temperatureFeels - location.temperature);

    // Определяем знак разницы температур для отображения
    const tempDiffSign = tempDifference > 0 ? '+' : '';
    const tempDiffText = tempDifference !== 0 ? `${tempDiffSign}${tempDifference}°` : '';

    card.innerHTML = `
        <div class="card h-100 weather-card">
            <div class="position-absolute" style="top: 12px; right: 12px;">
                <button class="btn-close" onclick="deleteLocation('${location.name}', ${location.latitude}, ${location.longitude})" aria-label="Delete">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="card-body">
                <h2 class="weather-temp">${location.temperature}°</h2>

<div class="d-flex justify-content-between align-items-center mb-1">
  <h3 class="location-name mb-0">${location.name} <span class="flag-emoji">${flagEmoji}</span></h3>
  <div class="weather-icon ms-2">
    <i class="${weatherIconClass}"></i>
  </div>
</div>
                <div class="info-section">
                    <div class="info-row">
                        <span class="info-label">Feels like</span>
                        <span>${location.temperatureFeels}°</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Humidity</span>
                        <span>${location.humidity}%</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Wind</span>
                        <span>${location.windSpeed} m/s</span>
                    </div>
                </div>
            </div>
        </div>
    `;

    return card;
}


// Функция для определения иконки погоды
function getWeatherIconClass(mainWeather) {
    const icons = {
        'Clear': 'wi wi-day-sunny',
        'Clouds': 'wi wi-cloudy',
        'Snow': 'wi wi-snow',
        'Rain': 'wi wi-rain',
        'Drizzle': 'wi wi-sprinkle',
        'Thunderstorm': 'wi wi-thunderstorm',
        'Mist': 'wi wi-fog',
        'default': 'wi wi-day-sunny'
    };

    return icons[mainWeather] || icons['default'];
}

function createLocationCard(location) {
  const card = document.createElement('div');
  card.className = 'col-12 col-lg-3 col-md-6 mb-4';

  const countryCode = location.country || '';
  const flagEmoji = getCountryFlagEmoji(countryCode);

  card.innerHTML = `
    <div class="card h-100 location-card">
      <div class="card-body d-flex flex-column">
        <h5 class="location-name">${location.name} <span class="flag-emoji">${flagEmoji}</span></h5>

        <div class="info-section">
          <div class="info-row">
            <span class="info-label">Latitude</span>
            <span>${location.latitude}</span>
          </div>
          <div class="info-row">
            <span class="info-label">Longitude</span>
            <span>${location.longitude}</span>
          </div>
          <div class="info-row">
            <span class="info-label">Country</span>
            <span>${location.country || 'N/A'}</span>
          </div>
          <div class="info-row">
            <span class="info-label">State</span>
            <span>${location.state || 'N/A'}</span>
          </div>
        </div>

        <div class="mt-auto pt-4">
          <button class="btn w-100" onclick="addLocation('${location.name}', ${location.latitude}, ${location.longitude})">Add</button>
        </div>
      </div>
    </div>
  `;

  return card;
}

function getCountryFlagEmoji(countryCode) {
  if (!countryCode || countryCode.length !== 2) return '🌐';

  try {
    const codePoints = countryCode
      .toUpperCase()
      .split('')
      .map(char => 127397 + char.charCodeAt(0));

    const emoji = String.fromCodePoint(...codePoints);

    return emoji;
  } catch (e) {
    console.warn('Error creating flag emoji:', e);
    return countryCode;
  }
}

