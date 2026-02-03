#!/usr/bin/env python3
import datetime
import time

from config import RETRY_INTERVAL_SECONDS, SCRAPE_INTERVAL_SECONDS
from database import SessionLocal
from fetch_stations import fetch_stations
from models import Availability, Station


def scrape_stations():
    """
    抓取站点数据。期望 API 返回格式与样例一致，例如：
    {
      "number": 42,
      "contract_name": "dublin",
      "name": "SMITHFIELD NORTH",
      "address": "Smithfield North",
      "position": {"lat": 53.349562, "lng": -6.278198},
      "banking": false,
      "bonus": false,
      "bike_stands": 30,
      "available_bike_stands": 2,
      "available_bikes": 28,
      "status": "OPEN",
      "last_update": 1770053684000
    }
    """
    started_at = datetime.datetime.now()
    print(f"[{started_at.strftime('%Y-%m-%d %H:%M:%S')}] 开始抓取...")

    raw = fetch_stations()
    # 兼容：直接返回数组，或包在 {"stations": [...]} 等键里
    if isinstance(raw, list):
        data = raw
    elif isinstance(raw, dict):
        data = raw.get("stations", raw.get("data", []))
    else:
        data = []
    total = len(data)

    session = SessionLocal()
    try:
        new_stations = 0
        for item in data:
            # --- 第一步：处理 Station (静态数据) ---
            station = session.get(Station, item["number"])

            if not station:
                new_stations += 1
                station = Station(
                    number=item["number"],
                    contract_name=item["contract_name"],
                    name=item["name"],
                    address=item["address"],
                    latitude=item["position"]["lat"],
                    longitude=item["position"]["lng"],
                    banking=item["banking"],
                    bonus=item["bonus"],
                    bike_stands=item["bike_stands"],
                )
                session.add(station)

            # --- 第二步：处理 Availability (动态数据) ---
            dt_object = datetime.datetime.fromtimestamp(item["last_update"] / 1000.0)
            availability = Availability(
                number=item["number"],
                available_bikes=item["available_bikes"],
                available_bike_stands=item["available_bike_stands"],
                status=item["status"],
                last_update=item["last_update"],
                timestamp=dt_object,
            )
            session.add(availability)

        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    finished_at = datetime.datetime.now()
    duration_sec = (finished_at - started_at).total_seconds()
    print(
        f"[{finished_at.strftime('%Y-%m-%d %H:%M:%S')}] 完成 | "
        f"本次获得 {total} 条站点数据，新增站点 {new_stations} 条，写入 {total} 条可用性记录 | "
        f"耗时 {duration_sec:.2f} 秒"
    )


# 主循环（表结构由 flask-app 的迁移维护，请先执行 flask db upgrade）
if __name__ == "__main__":
    while True:
        try:
            scrape_stations()
            # 默认休息 5 分钟，可通过 .env 覆盖
            time.sleep(SCRAPE_INTERVAL_SECONDS)
        except Exception as e:
            ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{ts}] 报错了: {e}")
            time.sleep(RETRY_INTERVAL_SECONDS)
