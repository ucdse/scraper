# scraper

独立运行的 Dublin Bikes 抓取程序（不依赖 Flask 应用进程即可运行）。

**与 flask-app 共用同一套数据库表结构**：表 `station`、`availability` 由 flask-app 的迁移维护，scraper 只负责写入数据，不维护表结构。

## 1) 数据库与迁移

表结构由 **flask-app** 的迁移维护。首次使用或迁移变更后，请在 flask-app 目录执行：

```bash
cd ../flask-app && flask --app app.py db upgrade
```

完成后再启动 scraper（任选下面一种方式）。

## 2) 运行方式（二选一）

### 方式 A：本地运行

#### 步骤 1：克隆仓库

```bash
git clone https://github.com/your-org/scraper.git
cd scraper
```

#### 步骤 2：创建并激活虚拟环境（推荐）

```bash
# 创建 Conda 环境
conda create -n scraper python=3.11 -y

# 激活环境
conda activate scraper
```

#### 步骤 3：安装依赖

```bash
pip install -r requirements.txt
```

#### 步骤 4：配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入实际配置：

| 变量 | 必填 | 说明 |
|------|------|------|
| `DATABASE_URL` | ✅ | 数据库连接字符串，如 `mysql+pymysql://user:password@host:3306/dublinbikes` |
| `JCDECAUX_API_KEY` | ✅ | JCDecaux API 密钥 |
| `JCDECAUX_CONTRACT` | ✅ | 合约名称，如 `dublin` |
| `SCRAPE_INTERVAL_SECONDS` | | 抓取间隔（默认 300） |
| `RETRY_INTERVAL_SECONDS` | | 失败重试间隔（默认 60） |

#### 步骤 5：确保数据库已就绪

运行前请确认：
- 数据库服务已启动且可连接
- flask-app 的迁移已执行（参考「1) 数据库与迁移」章节）

#### 步骤 6：运行脚本

| 命令 | 说明 |
|------|------|
| `python fetch_stations.py` | 单次抓取，结果保存到 JSON 文件 |
| `python main_scraper.py` | 持续抓取，定时写入数据库 |

### 方式 B：Docker 部署

在 `scraper` 目录下构建镜像：

```bash
docker build -t kaiwenyao/scraper:latest .
```

运行容器时通过 `--env-file` 传入环境变量（参考 `.env.example`）。若与 flask-app 在同一 Docker 网络中，可加入该网络以便共用数据库：

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
