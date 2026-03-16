import os, logging, json
from openai import OpenAI
from perplexity import ask_perplexity
from api_keys import OPENAI_KEY

def gpt_load_chat_history(space_id="lulu_default"):
    history_file = os.path.join(current_dir, f"{space_id}_history.json")
    messages = []
    
    if os.path.exists(history_file):
        logging.info(f"File {history_file} found")
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                messages = data.get("history", [])
                logging.info(f"Loaded {len(messages)} from {history_file}")
        except json.JSONDecodeError:
            logging.error(f"Error reading {history_file}")
    
    return messages, history_file
    

def gpt_save_chat_history(messages, history_file):
    data = {
        "space_id": history_file.replace(".json", ""),
        "system_prompt": lulu_system_promt,
        "history": messages,
        "last_updated": os.path.getctime(history_file) if os.path.exists(history_file) else None
    }
    
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    logging.info(f"Saved GPT history to {history_file}")
    
def text_to_speech(text, output_file):
    response = openai_client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="shimmer",
        input=text,
        response_format="wav"
    )
    
    response.stream_to_file(output_file)

def load_system_prompt(filename="lulu_prompt.txt"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read().strip()
        return {"role": "system", "content": content}
    except FileNotFoundError:
        logging.error(f"Error loading {filename}!")
        return None
        
def generate_image(promt):
    global ui_current_message_override, ui_current_message_left_override, generated_image_path, generated_image_buffer
    
    ui_current_message_override = "Создаю картинку!"
    ui_current_message_left_override = 30
    
    response = openai_client.images.generate(
        model="dall-e-3",
        prompt=promt,
        size="1792x1024",
        quality="standard",
        n=1,
    )
    
    image_url = response.data[0].url
    
    return image_url
    
def whisper_recognize(audio_path):
    with open(audio_path, "rb") as audio_file:
        transcription = openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="ru",
            response_format="text", 
            temperature=0.0
        )
        
    return transcription
    
def get_gpt_answer(text, cam_url, max_history=18):  
    chat_history, history_file = gpt_load_chat_history()
    
    messages = [lulu_system_promt]
    messages += chat_history[-max_history:]
    messages.append({"role": "user", "content": [ {"type": "text", "text": text}, {"type": "image_url", "image_url": {"url": cam_url}} ]})
    
    logging.info(f"Asking GPT: {text}")
       
    #gpt 5-2 variant  
    '''messages = [lulu_system_promt, {"role": "user", "content": text}]
    
    response = openai_client.chat.completions.create(
        model="gpt-5.2",
        messages=messages,
        temperature=0.7
    )
    return response.choices[0].message.content'''
    
    #perplexity sonar variant
    
    gpt_response = ask_perplexity(messages)
    
    logging.info(f"GPT Response: {gpt_response}")
    
    if gpt_response.startswith("Perplexity Client Error"):
        return gpt_response
        #raise RuntimeError(gpt_response)
    
    chat_history.append({"role": "user", "content": text})
    chat_history.append({"role": "assistant", "content": gpt_response})
    
    gpt_save_chat_history(chat_history[-200:], history_file)
    
    return gpt_response

current_dir = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(
    filename=os.path.join(current_dir, 'lulu.log'), 
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

openai_client = OpenAI(api_key=OPENAI_KEY)
lulu_system_promt = load_system_prompt(os.path.join(current_dir, "lulu_system_promt.txt"))
