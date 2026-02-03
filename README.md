# scraper

独立运行的 Dublin Bikes 抓取程序（不依赖原 Flask 项目）。

## 1) 准备环境变量

在仓库根目录放置 `.env`，至少包含：

```env
DATABASE_URL=mysql+pymysql://user:password@host:3306/dublinbikes
JCDECAUX_API_KEY=your_api_key
JCDECAUX_CONTRACT=dublin
```

可选：

```env
SCRAPE_INTERVAL_SECONDS=300
RETRY_INTERVAL_SECONDS=60
OUTPUT_JSON=stations.json
JCDECAUX_BASE_URL=https://api.jcdecaux.com/vls/v1/stations
```

## 2) 安装依赖

```bash
pip install -r requirements.txt
```

## 3) 运行

- 单次抓取并保存 JSON：
  ```bash
  python fetch_stations.py
  ```
- 持续抓取并写入数据库：
  ```bash
  python main_scraper.py
  ```
