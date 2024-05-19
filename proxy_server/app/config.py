import logging
import os

from dotenv import load_dotenv


load_dotenv()

RABBIT_MQ_URL = os.getenv("RABBIT_MQ_URL", "amqp://guest:guest@localhost/")


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(pathname)s:%(lineno)d - %(message)s",
    datefmt="%H:%M:%S %d.%m.%Y",
)
