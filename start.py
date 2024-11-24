from elasticsearch import Elasticsearch
from flask import Flask

# 连接信息
cloud_id = "My_deployment:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvJDZlODAxZjQ5YzAwNDQ5MGRhNDFlOGM3Y2U0MmFmYmQxJGQ2ZTE2YjQ1OWNjMTRhNmZiNDE0ZGZmNmJmN2JjMjll"  # 从 Elastic Cloud 控制台获取
api_key = "TzVkMldKTUJDVjk5bTVXZVFFeGg6LVpiZk04UFZUUE95QXpjbE9VZUttdw=="

# 创建 Elasticsearch 客户端
client = Elasticsearch(
    cloud_id=cloud_id,
    api_key=api_key
)
app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>Welcome to my Flask server!</h1>"

@app.route("/start")
def elastic_search():
    # 测试连接
    try:
        info = client.info()
        print("Connected to Elasticsearch:", info)
    except Exception as e:
        print("Error connecting to Elasticsearch:", e)
    return f"{info}"

if __name__ == "__main__":
    app.run(port=8000)
