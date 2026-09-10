import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

MODEL_NAME = os.environ.get("LLM_MODEL", "")

model = init_chat_model(MODEL_NAME)
