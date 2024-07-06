from flask import Flask, request
import requests

app = Flask(__name__)

# Replace with your actual API key
IPINFO_API_KEY = '2d9ec0c3be1ce0'
OPENWEATHERMAP_API_KEY = '912267f3e1bca4f497d32101815d6b62'

from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app)  # Trust X-Forwarded-For (if applicable)

def get_geolocation(ip):
    try:
        response = requests.get(f'https://ipinfo.io/{ip}?token=2d9ec0c3be1ce0')
        response.raise_for_status()  # Raise an error for unsuccessful requests (4xx, 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting geolocation data for {ip}: {e}")
        return None

def get_weather(lat, lon):
    response = requests.get(f'http://api.openweathermap.org/data/2.5/weather?lat=44.34&lon=10.99&appid=912267f3e1bca4f497d32101815d6b62&units=metric')
    if response.status_code == 200:
        return response.json()
    else:
        return None


@app.route('/api')
def hello_world():
    visitor_name = request.args.get('visitor_name', default='Michael')

    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)

    if client_ip == '127.0.0.1':
        location = "Local Network"  # Generic message for local IP
    else:
        location_data = get_geolocation(client_ip)
        if location_data:
            location = location_data.get('city', 'Unknown')
        else:
            location = "Unknown"

    location_data = get_geolocation(client_ip)
    if not location_data:
        return {
            "error": "Failed to get geolocation data"
        }, 500

    city = location_data.get('city', 'Unknown')
    loc = location_data.get('loc', '0,0').split(',')
    lat, lon = loc[0], loc[1]
    
    weather_data = get_weather(lat, lon)
    if not weather_data or 'main' not in weather_data:
        return {
            "error": "Failed to get weather data"
        }, 500
    
    temperature = weather_data['main']['temp']
    
    message = f"Hello, {visitor_name}! The temperature is {temperature} degrees Celsius in {city}."
    
    return {
        "client_ip": client_ip,
        "location": city,
        "greeting": message
    }

if __name__ == '__main__':
    app.run(debug=True)


