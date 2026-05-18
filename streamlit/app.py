import streamlit as st
import snowflake.connector
import pandas as pd
from pathlib import Path
import os
import logging
_APP_DIR= Path(__file__).resolve().parent
_DEFAULT_LOG_FILE = _APP_DIR / "logs" / "app.log"
log_dir = _APP_DIR / "logs"
log_dir.mkdir(parents=True,exist_ok=True)
VERBOSE = True
LOG_FILE = _DEFAULT_LOG_FILE


#set up log file
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename=LOG_FILE,
                    filemod="a"
)
logger = logging.getLogger("app")

class Background_colors:
    RED = "\033[41m"
    GREEN = "\033[42m"
    YELLOW = "\033[43m"
    BLUE = "\033[44m"
    MAGENTA = "\033[45m"
    CYAN = "\033[46m"
    END = "\033[0m"

def verbose_output(message: str) -> None:
    if VERBOSE:
        print(f"{message}{Background_colors.END}")
conn = snowflake.connector.connect(
    user="SNOWFLAKE_USER",
    password="SNOWFLAKE_PASSWORD",
    account="SNOWFLAKE_ACCOUNT",
    warehouse="SNOWFLAKE_WAREHOUSE",
    DATABASE="SNOWFLAKE_DATABASE",
    SCHEMA="SNOWFLAKE_SCHEMA"
)
st.set_page_config(page_title ="Stock Analysis Dashboard",layout="wide",page_icon="📈")

@st.cache_resource
def connection():
    try:
        return snowflake.connector.connect(
            user = os.getenv("SNOWFLAKE_USER"),
            password = os.getenv("SNOWFLAKE_PASSWORD"),
            account = os.getenv("SNOWFLAKE_ACCOUNT"),
            warehouse = os.getenv("SNOWFLAKE_WAREHOUSE"),
            DATABASE = os.getenv("SNOWFLAKE_DATABASE"),
            SCHEMA = os.getenv("SNOWFLAKE_SCHEMA"),
            client_session_keep_alive=True
        )
    except Exception as e:
        st.warning(f"Chua ket noi duoc voi database: {e}")
        return None
conn = connection()

def load_data(query: str):
    if conn is None:
        st.warning("Khong the ket noi duoc voi database")
        return pd.DataFrame()
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        df = cursor.fetch_pandas_all()
        df.columns = [col.lower() for col in df.columns]
        return df
    except Exception as e:
        st.error(f"Loi truy van:" {e})
        return pd.DataFrame()

st.title("Stock Data Analytics Dashboard")
st.markdown("Dashboard phân tích thị trường chứng khoán, tổng hợp từ các bảng dbt.")
menu = st.slidebar.selectbox(
    "Chọn Bảng Phân Tích (Select View)",
    [
        "Tổng quan (Overview)", 
        "Hiệu Suất Cổ Phiếu (Daily Performance)", 
        "Hiệu Suất Ngành (Industry Performance)", 
        "Tâm Lý Tin Tức (Company Sentiment)", 
        "Tác Động Tâm Lý Đến Giá (Sentiment Price Impact)" 
    ]
)
if menu == "Tổng quan (Overview)":
    st.write("### Chào mừng đến với trang tổng quan!")
    st.info("👈 Hãy chọn một chủ đề phân tích ở thanh bên trái (sidebar) để xem biểu đồ chi tiết.")
    st.markdown("""
        **Các bảng hiện có:**
        * **Hiệu Suất Cổ Phiếu:** Xem biến động giá và khối lượng giao dịch hằng ngày.
        * **Hiệu Suất Ngành:** Theo dõi dòng tiền và mức độ tăng trưởng của từng nhóm ngành.
        * **Tâm Lý Tin Tức:** Phân tích sentiment dư luận qua các bài báo tài chính.
        * **Tác Động Tâm Lý:** So sánh đối chiếu sự tương hợp giữa điểm sentiment và lợi nhuận thực tế.    
    """)
elif menu == "Hiệu Suất Cổ Phiếu (Daily Performance)":
    st.header("Hiệu Suất Cổ Phiếu Hằng Ngày")
    st.markdown("Dữ liệu từ bảng `daily_stock_performance`.")
    df = load_data("SELECT * FROM daily_stock_performance ORDER BY date_key DESC")

    if not df.empty:
        st.dataframe(df.head(10))
        st.subheader("Biến động Lợi Nhuận (Daily Return %)")
        tickers = df['ticker'],unique()
        selected_ticker = st.selectbox("Chọn Mã Cổ Phiếu (Ticker):", tickers)

        df_filtered = df[df['ticker']==selected_ticker].sort_values(by = 'date_key')

        fig = px.line(df_filtered,x='date_key',y='daily_return_percentage',
            title=f"Tỷ lệ Lợi Nhuận Hằng Ngày Của {selected_ticker}",
            markers=True,line_shape="spline")
        st.plotly_chart(fig,use_container_width=True)
    
        