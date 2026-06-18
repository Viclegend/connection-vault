# 🛡️ 客戶連線資訊管理系統

這是一個輕量級的容器化 Web 應用程式，專為系統整合 (SI) 與維運團隊設計。專門用來集中管理與記錄各客戶旗下設備的連線資訊（IP、連線方式、帳號密碼），確保團隊資訊同步與存取安全。

## 🌟 系統功能

* **分層式架構管理：** 依據客戶名稱進行分類，採用手風琴折疊介面，畫面清爽直覺。
* **強大檢索能力：** 支援關鍵字全域搜尋，可快速篩選客戶名稱、設備名稱、IP 或帳號。
* **權限與防呆防護：** 全站登入驗證，並具備管理員密碼防護與「防呆刪除」機制。
* **高安全性展示：** 敏感密碼預設遮罩，支援點擊「👁️」一鍵顯示/隱藏。
* **現代化 UI 體驗：** 內建日/夜間主題切換，自動適應使用者的視覺需求。

---

## 🐳 環境準備 (Docker 安裝指南)

本系統依賴 Docker 容器環境運行。若您的伺服器尚未安裝 Docker 與 Docker Compose，請依據您的作業系統執行以下指令：

### ▶ Ubuntu / Debian 系統
```bash
sudo apt update
sudo apt install docker.io docker-compose-v2 -y
sudo systemctl enable --now docker
▶ Rocky Linux / CentOS / RHEL 系統
Bash
sudo dnf install -y yum-utils
sudo dnf config-manager --add-repo=[https://download.docker.com/linux/centos/docker-ce.repo](https://download.docker.com/linux/centos/docker-ce.repo)
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo systemctl enable --now docker
🚀 快速部署指南
取得專案與設定檔
將本專案目錄下載至您的伺服器中。

建立環境變數
複製範本檔並重新命名為 .env：

Bash
cp .env.example .env
設定客製化參數
打開 .env 檔案，設定好您的對外通訊埠與管理員帳密：

程式碼片段
HOST_PORT=9000
ADMIN_USER=您的帳號
ADMIN_PASS=您的密碼
一鍵啟動服務
執行以下指令，系統會自動從雲端拉取最新版本的映像檔並於背景運行：

Bash
docker compose up -d
🎉 開始使用： 開啟瀏覽器，前往 http://<您的伺服器IP>:<您設定的Port>，輸入帳號密碼即可登入！

💾 資料備份與遷移說明
資料持久化： 系統所有的客戶與設備資料皆儲存於伺服器本機的 ./data/system_v4.db 檔案中。

備份方式： 進行日常備份或伺服器遷移時，您僅需將專案目錄下的 data 資料夾完整打包複製即可。只要 data 資料夾存在，重新啟動容器時資料就會無縫還原。