document.addEventListener('DOMContentLoaded', (event) => {
    requestUserLocation();
});

function requestUserLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(fetchData, showError);
    } else {
        alert("Geolocation is not supported by this browser.");
    }
}

function showError(error) {
    console.log(error); // Log the error object for detailed debugging information
    let errorMessage = "An unknown error occurred.";
    switch(error.code) {
        case error.PERMISSION_DENIED:
        errorMessage = "User denied the request for Geolocation.";
        break;
        case error.POSITION_UNAVAILABLE:
        errorMessage = "Location information is unavailable.";
        break;
        case error.TIMEOUT:
        errorMessage = "The request to get user location timed out.";
        break;
    }
    alert(errorMessage);
}

async function fetchData(position) {
    const lat = position.coords.latitude; // Use user's latitude
    const lon = position.coords.longitude; // Use user's longitude
    const weatherApiKey = 'fe63cbf94273389383dc8f89963a50f8'; // Replace with your weather API key
    const airQualityApiKey = 'fe63cbf94273389383dc8f89963a50f8'; // Replace with your air quality API key
    const weatherUrl = `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&appid=${weatherApiKey}&units=metric`;
    const airQualityUrl = `https://api.openweathermap.org/data/2.5/air_pollution?lat=${lat}&lon=${lon}&appid=${airQualityApiKey}`;
    
    // Fetch weather and air quality data
    const weatherResponse = await fetch(weatherUrl);
    const airQualityResponse = await fetch(airQualityUrl);
    
    // Parse the response data
    const weatherData = await weatherResponse.json();
    const airQualityData = await airQualityResponse.json();
    
    // Process and display the weather and air quality data
    const weather = weatherData.weather[0].main;
    const temperature = weatherData.main.temp;
    const airQualityIndex = airQualityData.list[0].main.aqi;
    
    const dropdownContent = document.getElementById('dropdownContent');
    dropdownContent.innerHTML = `
        <h3 style="font-family: Arial, sans-serif;">
        <i class="fas fa-cloud-sun" style="font-family: 'Font Awesome 5 Free';"></i> Weather
        </h3>
        <p style="font-family: Arial, sans-serif;">Temperature: ${temperature}°C</p>
        <p style="font-family: Arial, sans-serif;">Condition: ${weather}</p>
    
        <h3 style="font-family: Arial, sans-serif;">
        <i class="fas fa-smog" style="font-family: 'Font Awesome 5 Free';"></i> Air Quality
        </h3>
        <p style="font-family: Arial, sans-serif;">Air Quality Index: ${airQualityIndex}</p>
`;
    
}


function toggleDropdown() {
    const dropdown = document.getElementById('dropdownContent');
    if (dropdown.style.display === 'none' || !dropdown.style.display) {
        dropdown.style.display = 'block';
        requestUserLocation(); // Request location and fetch data when the dropdown is shown
    } else {
        dropdown.style.display = 'none';
    }
}

// Initialize dropdown to be hidden on page load
document.getElementById('dropdownContent').style.display = 'none';
function driverRegistration() {
    window.location.href = "driver-registration.html";
}