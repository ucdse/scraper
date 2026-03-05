import datetime
import requests
from sqlalchemy import delete

from config import OPENWEATHER_API_KEY, WEATHER_CITY, OPENWEATHER_GEOCODING_URL, OPENWEATHER_ONECALL_URL, OPENWEATHER_FORECAST_URL
from database import SessionLocal
from models_weather import WeatherForecast


class WeatherScraperError(Exception):
    pass


def get_lat_lon_for_city(city: str) -> tuple[float, float]:
    """
    通过 Geocoding API 根据城市名获取经纬度
    """
    url = OPENWEATHER_GEOCODING_URL
    params = {
        "q": city,
        "limit": 1,
        "appid": OPENWEATHER_API_KEY,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data:
            raise WeatherScraperError(f"Geocoding API returned empty data for city: {city}")
        
        return data[0]["lat"], data[0]["lon"]
    except requests.exceptions.RequestException as e:
        raise WeatherScraperError(f"Failed to fetch geocoding data: {e}")


def fetch_weather_and_store():
    """
    抓取目标城市的预报天气并存储入库 (更新未来2天，即48小时)。
    """
    if not OPENWEATHER_API_KEY:
        print("未配置 OPENWEATHER_API_KEY，跳过天气抓取。")
        return

    started_at = datetime.datetime.now()
    print(f"[{started_at.strftime('%Y-%m-%d %H:%M:%S')}] 开始抓取天气 ({WEATHER_CITY})...")

    try:
        # 1. 动态获取城市经纬度
        lat, lon = get_lat_lon_for_city(WEATHER_CITY)
        
        # 2. 调用 OpenWeatherMap One Call API (如果支持 3.0) 或 free forecast API
        # 这里尝试使用标准的 Onecall API 获取 hourly 数据
        url = OPENWEATHER_ONECALL_URL
        params = {
            "lat": lat,
            "lon": lon,
            "exclude": "current,minutely,daily,alerts",
            "appid": OPENWEATHER_API_KEY,
            "units": "metric" # 返回摄氏度
        }
        
        req = requests.get(url, params=params, timeout=10)
        # 兼容性处理：如果 OneCall 3.0 未订阅（返回 401），退回使用 2.5/forecast 等 API
        if req.status_code == 401:
            url = OPENWEATHER_FORECAST_URL
            params = {
                 "lat": lat,
                 "lon": lon,
                 "appid": OPENWEATHER_API_KEY,
                 "units": "metric"
            }
            req = requests.get(url, params=params, timeout=10)
            
        req.raise_for_status()
        data = req.json()

        # 3. 整理需要写入数据库的小时列表
        forecast_list = []
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        
        # 处理 OneCall 返回的 hourly (48 小时)
        if "hourly" in data:
            for item in data["hourly"]:
                dt = datetime.datetime.fromtimestamp(item["dt"], tz=datetime.timezone.utc)
                weather_info = item["weather"][0] if "weather" in item and item["weather"] else {}
                forecast_list.append({
                    "forecast_time": dt.replace(tzinfo=None), # SQLAlchemy DateTime usually assumes naive local or UTC depending on engine
                    "temperature": item.get("temp", 0),
                    "weather_code": weather_info.get("id", 800),
                    "description": weather_info.get("description", ""),
                    "icon": weather_info.get("icon", ""),
                    "feels_like": item.get("feels_like"),
                    "pressure": item.get("pressure"),
                    "humidity": item.get("humidity"),
                    "uvi": item.get("uvi"),
                    "clouds": item.get("clouds"),
                    "visibility": item.get("visibility"),
                    "wind_speed": item.get("wind_speed"),
                    "wind_deg": item.get("wind_deg"),
                    "pop": item.get("pop"),
                })
        # 处理 2.5/forecast 返回的 3-hour list (通常 5天 40条记录)
        elif "list" in data:
            for item in data["list"]:
                 dt = datetime.datetime.fromtimestamp(item["dt"], tz=datetime.timezone.utc)
                 weather_info = item["weather"][0] if "weather" in item and item["weather"] else {}
                 forecast_list.append({
                    "forecast_time": dt.replace(tzinfo=None),
                    "temperature": item["main"].get("temp", 0),
                    "weather_code": weather_info.get("id", 800),
                    "description": weather_info.get("description", ""),
                    "icon": weather_info.get("icon", ""),
                    "feels_like": item["main"].get("feels_like"),
                    "pressure": item["main"].get("pressure"),
                    "humidity": item["main"].get("humidity"),
                    "uvi": None, # Forecast API rarely provides UVI
                    "clouds": item.get("clouds", {}).get("all"),
                    "visibility": item.get("visibility"),
                    "wind_speed": item.get("wind", {}).get("speed"),
                    "wind_deg": item.get("wind", {}).get("deg"),
                    "pop": item.get("pop"),
                })
        
        if not forecast_list:
            print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 天气 API 没有返回小时数据。")
            return

        # 4. Upsert 逻辑 + 删除旧数据
        session = SessionLocal()
        try:
            # 清理过期的预报（小于当前 UTC 小时）
            # 当前时间的整点
            current_hour = now_utc.replace(minute=0, second=0, microsecond=0, tzinfo=None)
            session.execute(delete(WeatherForecast).where(WeatherForecast.forecast_time < current_hour))
            
            inserted = 0
            updated = 0
            
            for item in forecast_list:
                # 只保留未来最多 48 小时的数据。
                if (item["forecast_time"] - current_hour).total_seconds() > 48 * 3600:
                    continue
                    
                existing = session.query(WeatherForecast).filter_by(forecast_time=item["forecast_time"]).first()
                if existing:
                    # Update
                    existing.temperature = item["temperature"]
                    existing.weather_code = item["weather_code"]
                    existing.description = item["description"]
                    existing.icon = item["icon"]
                    existing.feels_like = item["feels_like"]
                    existing.pressure = item["pressure"]
                    existing.humidity = item["humidity"]
                    existing.uvi = item["uvi"]
                    existing.clouds = item["clouds"]
                    existing.visibility = item["visibility"]
                    existing.wind_speed = item["wind_speed"]
                    existing.wind_deg = item["wind_deg"]
                    existing.pop = item["pop"]
                    existing.fetched_at = datetime.datetime.utcnow()
                    updated += 1
                else:
                    # Insert
                    new_forecast = WeatherForecast(
                        forecast_time=item["forecast_time"],
                        temperature=item["temperature"],
                        weather_code=item["weather_code"],
                        description=item["description"],
                        icon=item["icon"],
                        feels_like=item["feels_like"],
                        pressure=item["pressure"],
                        humidity=item["humidity"],
                        uvi=item["uvi"],
                        clouds=item["clouds"],
                        visibility=item["visibility"],
                        wind_speed=item["wind_speed"],
                        wind_deg=item["wind_deg"],
                        pop=item["pop"],
                        fetched_at=datetime.datetime.utcnow()
                    )
                    session.add(new_forecast)
                    inserted += 1
            
            session.commit()
            
            finished_at = datetime.datetime.now()
            duration_sec = (finished_at - started_at).total_seconds()
            print(
                f"[{finished_at.strftime('%Y-%m-%d %H:%M:%S')}] 天气抓取完成 | "
                f"Insert: {inserted}, Update: {updated} | "
                f"耗时 {duration_sec:.2f} 秒"
            )

        except Exception as e:
            session.rollback()
            raise WeatherScraperError(f"Database operation failed: {e}")
        finally:
            session.close()

    except Exception as e:
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 抓取天气报错了: {e}")

if __name__ == "__main__":
    fetch_weather_and_store()
