# 📈 Stock Market Analytics & Sentiment Pipeline (Modern Data Stack)

Hệ thống xử lý và phân tích dữ liệu thị trường chứng khoán Hoa Kỳ (US Stock Market) kết hợp dữ liệu giá lịch sử (**OHLC**) và phân tích điểm tâm lý báo chí (**News Sentiment Analysis**). Dự án sử dụng mô hình **Modern Data Stack (MDS)** tiêu chuẩn công nghiệp nhằm tự động hóa quy trình thu thập, lưu trữ, biến đổi và trực quan hóa dữ liệu.

---

## 🏗️ Kiến Trúc Hệ Thống (System Architecture)

Dữ liệu di chuyển qua các tầng ETL/ELT khép kín từ các API thô đến giao diện phân tích cuối cùng của người dùng:

```mermaid
graph TD
    subgraph Data Sources & Ingestion
        A1[Grouped OHLC API - Massive]
        A2[News Sentiment API - Alpha Vantage]
        A3[(Local Postgres - Metadata)]
    end

    subgraph Step 1: Orchestration & Data Lake (Airflow & S3)
        B1[extract_ohlc.py] -->|Raw JSON| C1[(Raw Data Local)]
        B2[extract_news.py] -->|Raw JSON| C1
        
        C1 -->|Convert to Parquet| C2[(Parquet Data Local)]
        A3 -->|db_to_parquet| C2
        
        C2 -->|Upload via boto3| D[AWS S3 Bucket]
    end

    subgraph Step 2: Data Warehousing (Snowflake DWH)
        D -->|COPY INTO stg table| E[Snowflake Staging Tables]
        E -->|Idempotent MERGE| F[(Snowflake Core Tables)]
    end

    subgraph Step 3: Transformation & Analytics (dbt Core)
        F -->|dbt Run| G[dbt Staging Models]
        G -->|dbt Run| H[dbt Marts Analytics]
    end

    subgraph Step 4: Data Visualization (Streamlit)
        H -->|snowflake-connector-python| I[Streamlit Dashboard Web App]
    end

    classDef success fill:#e1f5fe,stroke:#0288d1,stroke-width:2px;
    classDef warning fill:#fff9c4,stroke:#fbc02d,stroke-width:2px;
    classDef primary fill:#e8f5e9,stroke:#388e3c,stroke-width:2px;
    
    class A1,A2,A3 warning;
    class B1,B2,C1,C2,D primary;
    class E,F,G,H success;
    class I primary;
```

---

## 🛠️ Công Nghệ Sử Dụng (Tech Stack)

* **Orchestration**: Apache Airflow (Astronomer CLI)
* **Storage & Lake**: AWS S3 (định dạng tối ưu cột **Parquet**)
* **Data Warehouse**: Snowflake Cloud DWH
* **Data Transformation**: dbt Core (phiên bản `1.8+`)
* **Visualization**: Streamlit Dashboard (Plotly, Pandas)
* **Metadata Database**: PostgreSQL
* **Containerization**: Docker & Docker Compose

---

## 📁 Cấu Trúc Thư Mục Dự Án (Project Directory Structure)

```text
stock_project/
├── .astro/                         # Cấu hình môi trường chạy Astronomer Airflow
├── dags/                           # Airflow DAGs & mã nguồn ELT
│   ├── backend/                    # Logic phụ trợ cho database
│   ├── dbt/                        # Thư mục chứa dbt project
│   │   └── stock_dbt/              # DBT Core configurations & models
│   │       ├── models/
│   │       │   ├── staging/        # Tầng làm sạch & làm mịn dữ liệu từ nguồn thô
│   │       │   └── marts/          # Tầng tổng hợp dữ liệu nghiệp vụ (Analytics Marts)
│   │       ├── seeds/              # Dữ liệu static đính kèm
│   │       └── dbt_project.yml
│   ├── elt/                        # Scripts xử lý dữ liệu chính
│   │   ├── extract/                # Crawl dữ liệu từ APIs (OHLC, News Sentiment)
│   │   ├── load/                   # Chuyển đổi sang Parquet & tải lên AWS S3
│   │   └── transform/              # Sao chép vào Snowflake Staging & MERGE
│   ├── scripts/                    # Định nghĩa các DAGs chạy trên Airflow UI
│   │   └── etl_to_dw.py            # DAG điều phối pipelines chính
│   └── dbt_dag.py                  # DAG điều phối chạy các models dbt qua cosmos
├── streamlit/                      # Ứng dụng giao diện người dùng
│   ├── app.py                      # File Streamlit Dashboard chính
│   ├── requirements.txt            # Thư viện cho Streamlit container
│   └── Dockerfile                  # Đóng gói ứng dụng Streamlit
├── docker-compose.override.yml     # Override các service chạy kèm Airflow (Streamlit, Postgres)
├── requirements.txt                # Thư viện Python chính của Airflow
├── packages.txt                    # System packages cho Airflow
└── .env                            # Quản lý tất cả các biến môi trường
```

---

## 📊 Mô Hình Dữ Liệu Phân Tích (Data Modeling in dbt)

Dữ liệu được dbt làm sạch từ lớp `staging` và tổng hợp lại tại tầng `marts` thành các bảng phân tích đa chiều phục vụ reporting:

| Bảng Phân Tích (dbt Marts) | Mô tả chi tiết | Các chỉ số chính |
| :--- | :--- | :--- |
| **`daily_stock_performance`** | Phân tích biến động giá cổ phiếu hàng ngày | Giá đóng/mở cửa, khối lượng giao dịch, tỷ lệ lợi nhuận ngày (`daily_return_percentage`). |
| **`industry_performance`** | Phân tích sức mạnh và dòng tiền theo từng nhóm ngành | Tổng khối lượng giao dịch ngành, số lượng mã tăng/giảm giá. |
| **`company_sentiment`** | Tổng hợp điểm tâm lý báo chí hàng ngày của doanh nghiệp | Điểm sentiment trung bình (`avg_sentiment_score`), số bài báo tích cực/tiêu cực/trung lập. |
| **`sentiment_price_impact`** | Đối chiếu mức độ ảnh hưởng của tâm lý truyền thông lên giá cổ phiếu | Sự tương đồng giữa tín hiệu tin tức và biến động giá thực tế (`sentiment_price_alignment`). |

---

## 🚀 Hướng Dẫn Cài Đặt & Khởi Chạy (Installation & Quick Start)

### 1. Chuẩn Bị File Cấu Hình Môi Trường (`.env`)
Tạo file `.env` ở thư mục gốc của dự án với đầy đủ các cấu hình sau:

```env
# API Keys
API_NEWS=your_alpha_vantage_api_key
API_OHLC=your_massive_api_key

# PostgreSQL (Metadata)
POSTGRES_HOST=my_new_postgres
POSTGRES_DB=stock_db
POSTGRES_USER=phongthanh
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_PORT=5432

# AWS Credentials (S3 Data Lake)
ACCESS_KEY=your_aws_access_key
SECRET_KEY=your_aws_secret_key
REGION=ap-southeast-1

# Snowflake Data Warehouse
SNOWFLAKE_USER=your_snowflake_user
SNOWFLAKE_PASSWORD=your_snowflake_password
SNOWFLAKE_ACCOUNT=your_snowflake_account_id
SNOWFLAKE_WAREHOUSE=dbt_wh
SNOWFLAKE_DATABASE=stock_database
SNOWFLAKE_SCHEMA=stock_schema
SNOWFLAKE_ROLE=dbt_role
```

---

### 2. Khởi Chạy Hệ Thống Bằng Astronomer CLI (Airflow & Services)

Dự án sử dụng **Astro CLI** để quản lý vòng đời chạy Airflow. Đảm bảo bạn đã cài đặt Docker và Astro CLI trên máy cá nhân.

```bash
# Di chuyển vào thư mục dự án
cd /path/to/stock_project

# Khởi động cụm dịch vụ (Airflow Webserver, Scheduler, Postgres, Streamlit)
astro dev start
```

* Sau khi chạy thành công, bạn truy cập vào các cổng sau:
  * **Airflow UI**: `http://localhost:8080` (Tài khoản mặc định: `admin` / `admin`).
  * **Streamlit Dashboard**: `http://localhost:8501` để xem dashboard trực quan.

---

### 3. Cấu hình và Chạy dbt Core

Để khởi chạy thủ công dbt hoặc kiểm tra mô hình dữ liệu:

```bash
# Kích hoạt virtual environment của dbt
source .venv/bin/activate

# Di chuyển đến thư mục dbt
cd dags/dbt/stock_dbt

# Kiểm tra kết nối đến Snowflake Data Warehouse
dbt debug

# Tải seed data (danh sách công ty, ngành nghề...) vào Snowflake
dbt seed

# Khởi chạy và build toàn bộ bảng dữ liệu phân tích
dbt run

# Chạy kiểm thử chất lượng dữ liệu (Data Quality Tests)
dbt test
```

---

## 🔄 Luồng Vận Hành Tự Động (Orchestration Workflow)

1. **DAG 1: `Extracing_API_and_load_data_data_warehouse`**
   * **Tần suất**: Chạy định kỳ hàng ngày (`@daily`).
   * **Nhiệm vụ**:
     * `extract_phase`: Trích xuất dữ liệu OHLC và News từ API, lưu dạng JSON.
     * `load_phase`: Trích xuất metadata từ Postgres local, gộp tất cả thành file Parquet và upload lên AWS S3.
     * `transform_phase`: Gọi Snowflake STG tạo bảng ảo, copy dữ liệu từ S3 và chạy lệnh `MERGE` cập nhật dữ liệu mới vào bảng lõi.

2. **DAG 2: `dbt_dag`**
   * **Tần suất**: Chạy tự động ngay sau khi DAG 1 hoàn tất thành công.
   * **Nhiệm vụ**: Điều phối dbt để dọn dẹp tầng `staging` và tổng hợp dữ liệu mới lên tầng `marts` phục vụ trực quan hóa trên Streamlit.

---

## 📈 Streamlit Dashboard Preview

Ứng dụng Streamlit của dự án cung cấp 5 trang phân tích chuyên sâu:
1. **Tổng quan (Overview)**: Giới thiệu hệ thống, hướng dẫn người dùng và xem danh mục dữ liệu.
2. **Hiệu Suất Cổ Phiếu (Daily Performance)**: Xem biểu đồ tỷ lệ sinh lời hàng ngày của từng mã cổ phiếu.
3. **Hiệu Suất Ngành (Industry Performance)**: Thống kê tổng quan khối lượng giao dịch và xu thế dịch chuyển dòng tiền theo ngành nghề.
4. **Tâm Lý Tin Tức (Company Sentiment)**: Phân bố điểm tâm lý trung bình dư luận để phát hiện rủi ro doanh nghiệp qua tin tức.
5. **Tác Động Tâm Lý Đến Giá (Sentiment Price Impact)**: Biểu đồ phân tán (Scatter Plot) phân tích mức độ tương quan thực tế giữa tin tức báo chí và sự biến động giá cổ phiếu.

---

## 👨‍💻 Tác giả & Đóng góp
Dự án được phát triển và duy trì bởi nhóm Kỹ sư Dữ liệu (**Data Engineers**). Mọi đóng góp, sửa lỗi hoặc đề xuất tính năng mới vui lòng gửi Pull Request hoặc tạo Issue trên kho lưu trữ của dự án.
