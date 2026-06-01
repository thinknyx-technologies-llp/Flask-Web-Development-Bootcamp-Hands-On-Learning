from flask import Flask
import logging

app = Flask(__name__)

logging.basicConfig(
    filename="app.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

@app.route('/')
def home():
    app.logger.info("Application started")
    return "Logged into the terminal"

if __name__ == "__main__":
    app.run(debug=False)