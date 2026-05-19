#!/bin/bash
# Lấy đường dẫn tuyệt đối của thư mục gốc dự án
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Starting the Streamlit application..."

# Kích hoạt virtual environment nếu tồn tại
if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
else
    echo "Warning: .venv not found at $PROJECT_ROOT/.venv. Running without activating virtual environment."
fi

# Chạy Streamlit
export PYTHONPATH="$PROJECT_ROOT"
streamlit run "$PROJECT_ROOT/streamlit/app.py"