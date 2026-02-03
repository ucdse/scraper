"""
独立 scraper 配置：只依赖环境变量，不依赖 Flask 项目。
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

BASE_URL = os.environ.get("JCDECAUX_BASE_URL", "https://api.jcdecaux.com/vls/v1/stations")
PARAMS = {
    "contract": os.environ.get("JCDECAUX_CONTRACT", "dublin"),
    "apiKey": os.environ.get("JCDECAUX_API_KEY", ""),
}

OUTPUT_JSON = os.environ.get("OUTPUT_JSON", "stations.json")

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL 环境变量未设置，请在 .env 文件中配置")

SCRAPE_INTERVAL_SECONDS = int(os.environ.get("SCRAPE_INTERVAL_SECONDS", "300"))
RETRY_INTERVAL_SECONDS = int(os.environ.get("RETRY_INTERVAL_SECONDS", "60"))
