import requests
import schedule
import time
from datetime import datetime

# Placeholder for API Key. Replace 'YOUR_API_KEY' with your actual OpenWeatherMap API key.
API_KEY = '7738e487e1c6f8eeeeee873882624ed8'
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

def get_weather(city):
    """
    Fetches weather data for a given city and prints it.
    """
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'metric'  # Use 'imperial' for Fahrenheit
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status() # Raise an exception for bad status codes
        
        data = response.json()
        
        # Extracting relevant information
        temp = data['main']['temp']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        weather_desc = data['weather'][0]['description']
        
        # Coordinates for AQI
        lat = data['coord']['lat']
        lon = data['coord']['lon']

        # Start AQI Fetching
        aqi_url = "http://api.openweathermap.org/data/2.5/air_pollution"
        aqi_params = {
            'lat': lat,
            'lon': lon,
            'appid': API_KEY
        }
        aqi_response = requests.get(aqi_url, params=aqi_params)
        aqi_response.raise_for_status()
        aqi_data = aqi_response.json()
        aqi_level = aqi_data['list'][0]['main']['aqi']
        
        aqi_dict = {
            1: "Good",
            2: "Fair",
            3: "Moderate",
            4: "Poor",
            5: "Very Poor"
        }
        aqi_text = aqi_dict.get(aqi_level, "Unknown")
        # End AQI Fetching
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"[{timestamp}] Weather in {city}:")
        print(f"  Temperature: {temp}°C")
        print(f"  Humidity: {humidity}%")
        print(f"  Wind Speed: {wind_speed} m/s")
        print(f"  Condition: {weather_desc.capitalize()}")
        print(f"  AQI: {aqi_level} ({aqi_text})")
        print("-" * 30)

    except requests.exceptions.HTTPError as errh:
        print(f"Http Error: {errh}")
        if response.status_code == 404:
            print("City not found. Please check the city name.")
        elif response.status_code == 401:
            print("Invalid API Key. Please check your API key.")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"OOps: Something Else: {err}")

def job():
    get_weather(city_name)

if __name__ == "__main__":
    print("Welcome to the Weather Notification Bot!")
    city_name = input("Enter City Name: ").strip()
    
    while True:
        try:
            frequency = float(input("Enter Frequency (in minutes): "))
            if frequency <= 0:
                print("Frequency must be positive.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a number.")

    print(f"\nStarting weather monitoring for {city_name} every {frequency} minutes...")
    
    # Run once immediately
    job()
    
    # Schedule the job
    schedule.every(frequency).minutes.do(job)
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nWeather Bot stopped by user.")
