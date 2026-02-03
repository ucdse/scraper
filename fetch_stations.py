#!/usr/bin/env python3
"""
通过 JCDecaux API 请求 Dublin 的自行车站点数据。
"""

import json
import urllib.parse
import urllib.request

from config import BASE_URL, OUTPUT_JSON, PARAMS


def fetch_stations():
    """请求站点数据并返回 JSON 列表。"""
    url = f"{BASE_URL}?{urllib.parse.urlencode(PARAMS)}"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "dublin-bikes-scraper/1.0"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode())


if __name__ == "__main__":
    try:
        data = fetch_stations()
        print(f"共获取 {len(data)} 个站点")

        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"数据已保存到 {OUTPUT_JSON}")

        # 打印前几条作为示例
        for i, station in enumerate(data[:3]):
            print(f"\n--- 站点 {i + 1} ---")
            print(station)
        if len(data) > 3:
            print(f"\n... 还有 {len(data) - 3} 个站点")
    except urllib.error.URLError as e:
        print(f"请求失败: {e}")
