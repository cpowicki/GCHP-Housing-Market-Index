from dotenv import load_dotenv
import os
import requests
import pandas as pd
import numpy as np
import json

load_dotenv(dotenv_path='.env')

apikey = os.getenv("API_KEY")
