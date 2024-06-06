from datetime import datetime, timedelta 
import gradio as gr
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
import logging
import sys
import io
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"), server_api=ServerApi('1'))
db = client[os.getenv("DB_NAME")]
collection = db[os.getenv("COLLECTION_NAME_C")]

task = "The function 'time_to_seconds', which should take a string time as an input parameter. The string specifies a participant's finishing time in an event (e.g., holding their breath for as long as possible) and will have the following format: min:sec.hundredths. The function should convert this string into a floating-point number in the format seconds.hundredths and return this floating-point number."

def store_submission(user_id, code_input, submit_type):
    if not hasattr(store_submission, "input_number"):
        store_submission.input_number = 0
    store_submission.input_number += 1

    document = {
        "user_id": user_id,
        "input_number": store_submission.input_number,
        "submit_type": submit_type,
        "time": datetime.utcnow() + timedelta(hours=1),
        "code_input": code_input
    }
    collection.insert_one(document)
    print(f"Stored {submit_type} submission for user {user_id} with input number {store_submission.input_number}")

def execute_code(code, user_id):
    output_io = io.StringIO()
    try:
        sys.stdout = output_io
        exec(code, {})
    except Exception as e:
        return f"Error: {e}"
    finally:
        sys.stdout = sys.__stdout__ 

    store_submission(user_id, code, "execute")
    return output_io.getvalue()

def submit_code(code, user_id):
    store_submission(user_id, code, "submit")
    
with gr.Blocks(css="footer {visibility: hidden}") as demo:
    code_input_var = gr.State()
    gr.Label(task)
    user_id_input = gr.Textbox(label="User ID", placeholder="Enter your user ID")
    with gr.Row():
        code_field1 = gr.Code(language="python")
        code_output_area = gr.TextArea(label="Code Output")
    execute_button = gr.Button("Execute Code")
    submit_button = gr.Button("Submit Code")

    execute_button.click(
        execute_code,
        inputs=[code_field1, user_id_input],
        outputs=code_output_area
    )

    submit_button.click(
        submit_code,
        inputs=[code_field1, user_id_input],
        outputs=code_output_area
    )
    

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    demo.queue().launch()
