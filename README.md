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