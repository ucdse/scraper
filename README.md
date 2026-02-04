# scraper

独立运行的 Dublin Bikes 抓取程序（不依赖 Flask 应用进程即可运行）。

**与 flask-app 共用同一套数据库表结构**：表 `station`、`availability` 由 flask-app 的迁移维护，scraper 只负责写入数据，不维护表结构。

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

## 2) 数据库与迁移

表结构由 **flask-app** 的迁移维护。首次使用或迁移变更后，请在 flask-app 目录执行：

```bash
cd ../flask-app && flask --app app.py db upgrade
```

完成后再启动 scraper（任选下面一种方式）。

## 3) 运行方式（二选一）

### 方式 A：本地运行

安装依赖：

```bash
pip install -r requirements.txt
```

- 单次抓取并保存 JSON：`python fetch_stations.py`
- 持续抓取并写入数据库：`python main_scraper.py`

### 方式 B：Docker 部署

在 `scraper` 目录下构建镜像：

```bash
docker build -t kaiwenyao/scraper:latest .
```

运行容器时通过 `--env-file` 传入环境变量（内容同「准备环境变量」）。若与 flask-app 在同一 Docker 网络中，可加入该网络以便共用数据库：

```bash
# 创建网络（若尚未创建）
docker network create flask-app

# 运行 scraper 容器
docker run -d \
  --name scraper \
  --restart unless-stopped \
  --network flask-app \
  --env-file /path/to/.env \
  kaiwenyao/scraper:latest
```

- `--restart unless-stopped`：宿主机重启后自动拉起容器。
- `--network flask-app`：与 flask-app 同网段时使用，便于 `DATABASE_URL` 指向同一数据库（如用服务名/容器名作 host）。
- 镜像默认执行 `python main_scraper.py`（持续抓取并写入数据库）。

CI 流程见 `scraper/Jenkinsfile`：构建镜像、推送到 registry，main 分支时部署到 EC2（使用相同镜像名、容器名与 env 路径）。
