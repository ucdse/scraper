# 🚀 Dublin Bikes Scraper

**Dublin Bikes Scraper** is a ✨ standalone data collection service ✨ designed to continuously scrape Dublin's shared bike station availability and local weather forecasts, then persist them to a MySQL database. Whether you're building a real-time dashboard, training a demand-forecasting model, or just love open data — this scraper has you covered! 🎉

> **Shared Database**: Table schemas (`station`, `availability`, `weather_forecast`) are maintained by the companion [flask-app](https://github.com/ucdse/flask-app). This scraper only writes data — it does **not** own or run migrations.

---

## 📋 Table of Contents
- [✨ Features](#-features)
- [🏗️ Architecture](#️-architecture)
- [🚀 Getting Started](#-getting-started)
  - [🔧 Prerequisites](#-prerequisites)
  - [🗄️ Database and Migrations](#️-database-and-migrations)
  - [⚙️ Installation (Local)](#️-installation-local)
  - [🐳 Installation (Docker)](#-installation-docker)
  - [🔧 Configuration](#-configuration)
- [🧬 Testing](#-testing)
- [💻 Usage](#-usage)
- [📁 Project Structure](#-project-structure)
- [🔄 CI/CD](#-cicd)
- [🤝 Contributing](#-contributing)
- [📝 License](#-license)
- [📧 Contact](#-contact)

---

## ✨ Features
- **🚲 Bike Station Scraping**: Fetches real-time station data (availability, status, location) from the JCDecaux API every 5 minutes. 🌟
- **🌤️ Weather Forecast Scraping**: Collects hourly weather forecasts (temperature, humidity, wind, UV index, etc.) from OpenWeatherMap every hour.
- **🔄 Dual-Thread Architecture**: Station and weather scraping run concurrently in separate threads with independent intervals and retry logic. 🔥
- **🐳 Docker-First Deployment**: Ships with a production-ready `Dockerfile` (Python 3.12-slim, non-root user). 🐳
- **⚡ Auto-Retry on Failure**: Both scrapers catch errors and retry after a configurable interval — no manual intervention needed. ⚡
- **🧹 Smart Data Cleanup**: Weather scraper automatically purges expired forecasts, keeping only the next 48 hours. 🧹
- **🗄️ Upsert Logic**: Station data is inserted or updated intelligently; weather forecasts are upserted to avoid duplicates. 🗄️

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────┐
│                 main_scraper.py                   │
│  ┌─────────────────────┐ ┌─────────────────────┐ │
│  │  Station Thread     │ │  Weather Thread      │ │
│  │  (every 5 min)      │ │  (every 1 hour)      │ │
│  │  ┌───────────────┐  │ │  ┌───────────────┐  │ │
│  │  │ JCDecaux API  │  │ │  │ OpenWeatherMap │  │ │
│  │  └───────┬───────┘  │ │  └───────┬───────┘  │ │
│  │          │           │ │          │           │ │
│  │          ▼           │ │          ▼           │ │
│  │  ┌───────────────┐  │ │  ┌───────────────┐  │ │
│  │  │  MySQL DB     │  │ │  │  MySQL DB      │  │ │
│  │  │ (station,     │  │ │  │ (weather_     │  │ │
│  │  │  availability)│  │ │  │  forecast)    │  │ │
│  │  └───────────────┘  │ │  └───────────────┘  │ │
│  └─────────────────────┘ └─────────────────────┘ │
└──────────────────────────────────────────────────┘
```

---