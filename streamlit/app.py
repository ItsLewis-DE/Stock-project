import streamlit as st
import snowflake.connector
import pandas as pd
from pathlib import Path
import plotly.express as px
import os
import logging
from dotenv import load_dotenv
load_dotenv('/usr/local/.env')
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
                    filemode="a"
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
st.set_page_config(page_title ="Stock Analysis Dashboard",layout="wide",page_icon="📈")

@st.cache_resource
def connection():
    try:
        return snowflake.connector.connect(
            user = os.getenv("SNOWFLAKE_USER"),
            password = os.getenv("SNOWFLAKE_PASSWORD"),
            account = os.getenv("SNOWFLAKE_ACCOUNT"),
            warehouse = os.getenv("SNOWFLAKE_WAREHOUSE"),
            database = os.getenv("SNOWFLAKE_DATABASE"),
            schema = os.getenv("SNOWFLAKE_SCHEMA"),
            role = os.getenv("SNOWFLAKE_ROLE"),
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
        st.error(f"Loi truy van: {e}")
        return pd.DataFrame()

st.title("Stock Data Analytics Dashboard")
st.markdown("Dashboard phân tích thị trường chứng khoán, tổng hợp từ các bảng dbt.")
menu = st.sidebar.selectbox(
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
        tickers = df['ticker'].unique()
        selected_ticker = st.selectbox("Chọn Mã Cổ Phiếu (Ticker):", tickers)

        df_filtered = df[df['ticker']==selected_ticker].sort_values(by = 'date_key')

        fig = px.line(df_filtered,x='date_key',y='daily_return_percentage',
            title=f"Tỷ lệ Lợi Nhuận Hằng Ngày Của {selected_ticker}",
            markers=True,line_shape="spline")
        st.plotly_chart(fig,use_container_width=True)
    else:
        st.error("Không có dữ liệu hoặc kết nối DB thất bại.")
elif menu == "Hiệu Suất Ngành (Industry Performance)":
    st.header("Hiệu Suất Theo Ngành")
    st.markdown("Dữ liệu từ bảng `industry_performance`.")
    df = load_data("SELECT * FROM industry_performance")
    
    if not df.empty:
        st.dataframe(df.head(10))

        st.subheader("Tổng khối lượng giao dịch theo ngành")
        df_group = df.groupby('industry_name')['total_trading_volume'].sum().reset_index()
        df_group = df_group.sort_values(by='total_trading_volume',ascending=False)
        fig = px.bar(df_group,x= 'industry_name',y='total_trading_volume',title="Total Trading Volume by Industry",color='total_trading_volume')
        st.plotly_chart(fig,use_container_width=True)
    else:
        st.error("Không có dữ liệu hoặc kết nối DB thất bại.")
elif menu == "Tâm Lý Tin Tức (Company Sentiment)":
    st.header("Phân Tích Tâm Lý Dư Luận")
    st.markdown("Dữ liệu từ bảng `company_sentiment`.")
    df = load_data("SELECT * FROM company_sentiment ORDER BY date_key DESC;")
    
    if not df.empty:
        st.dataframe(df.head(10))
        
        st.subheader("Phân Phối Điểm Tâm Lý (Sentiment Score)")
        fig = px.box(df, x="ticker", y="avg_sentiment_score", 
                     title="Phân Bố Điểm Tâm Lý Trung Bình Giữa Các Cổ Phiếu", color="ticker")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Không có dữ liệu hoặc kết nối DB thất bại.")

elif menu == "Tác Động Tâm Lý Đến Giá (Sentiment Price Impact)":
    st.header("Tác Động Của Tâm Lý Tin Tức Lên Giá Cổ Phiếu")
    st.markdown("Dữ liệu từ bảng `sentiment_price_impact`.")
    df = load_data("SELECT * FROM sentiment_price_impact ORDER BY date_key DESC;")

    if not df.empty:
        st.dataframe(df.head(10))
        st.subheader("Mức Độ Tương Hợp: Sentiment Score vs Daily Return (%)")
        fig=px.scatter(df,x='avg_sentiment_score',y='daily_return_percentage',
                        color = 'sentiment_price_alignment',
                        title="Biểu Đồ Phân Tán: Sự Tương Quan Giữa Tin Tức Và Giá",
                        labels={"avg_sentiment_score": "Điểm Tâm Lý (Sentiment)", "daily_return_percentage": "Tỷ Lệ Lợi Nhuận (%)"},
                        hover_data=["ticker", "date_key"])
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        fig.add_vline(x=0, line_dash="dash", line_color="gray")
        st.plotly_chart(fig,use_container_width=True)
    else:
        st.error("Không có dữ liệu hoặc kết nối DB thất bại.")
    

        
