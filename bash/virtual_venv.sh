VENV_PATH = "$HOME/stock_project/.venv/bin/activate"

if test -f "$VENV_PATH"; then
    source $VENV_PATH
else
    echo "Virtual environment not found at $VENV_PATH"
fi