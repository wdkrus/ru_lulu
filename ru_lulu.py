import os, io, sys, time, threading, requests, subprocess, glob, traceback, ctypes, logging
from audio import start_recording_custom, detect_keyword_custom, play_file, stop_play
from PIL import Image
from pydub import AudioSegment
from pydub.effects import normalize, speedup
from xgolib import XGO
from picamera2 import Picamera2
from datetime import datetime
from lulu_llm_integrations import text_to_speech, generate_image, whisper_recognize, get_gpt_answer
import cv2

from uiutils import (
    dog, clear_bottom,clear_top,lcd_draw_string, display, splash, 
    line_break, scroll_text_on_lcd, draw_offline, draw, 
    font2, font3, font4, Button, get_font,la
)

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

logging.basicConfig(
    filename=os.path.join(current_dir, 'lulu.log'), 
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

SPLASH_COLOR = (15, 21, 46)

ui_current_message = "Загружаюсь..."
ui_current_message_left = 50
ui_current_message_override = None
ui_current_message_left_override = None
ui_current_expression = "sleep"
ui_current_message_color = (255, 255, 255)
ui_frame_index = 0

keyword_detected = False
keyword_thread = None
keyword_backgroud_thread = None

recognition_thread = None
recognized_speech = None

gpt_thread = None
gpt_answer = None

actions_script_thread = None
actions_script_done = False

generated_image_path = None   
generated_image_buffer = None

flow_state = -1

def scan_rider_expressions(base_path="/home/pi/xgoPictures/expression/rider"):
    if not os.path.exists(base_path):
        print(f"No folder {base_path}!")
        return {}
    
    expressions = {}
    
    for folder_name in os.listdir(base_path):
        folder_path = os.path.join(base_path, folder_name)
        if os.path.isdir(folder_path):
            png_files = sorted(glob.glob(os.path.join(folder_path, "*.png")))
            
            if png_files:
                clean_key = folder_name.lower().strip()
                frames = []
                
                for png_path in png_files:
                    try:
                        img = Image.open(png_path)
                        frames.append(img)
                    except Exception as e:
                        print(f"Error loading {png_path}: {e}")
                
                expressions[clean_key] = frames
                logging.info(f"Expression {folder_name} > '{clean_key}': {len(frames)} frames")
    
    return expressions

def reinit():
    global keyword_detected, keyword_thread, recognition_thread, recognized_speech, gpt_thread, gpt_answer, actions_script_thread, actions_script_done, flow_state, ui_current_message_override, ui_current_message_left_override
    
    keyword_detected = False
    keyword_thread = None

    recognition_thread = None
    recognized_speech = None
    
    gpt_thread = None
    gpt_answer = None
    
    actions_script_thread = None
    actions_script_done = False
    
    ui_current_message_override = None
    ui_current_message_left_override = None
    
    lulu_set_expression("sleep")
    
    flow_state = -1

def draw_ui():
    global ui_current_message, ui_current_message_left, ui_current_message_color, ui_frame_index, splash, generated_image_buffer
    
    if generated_image_buffer is not None:
        splash.paste(generated_image_buffer)
    else:
        draw.rectangle((0, 0, display.height, display.width), fill=SPLASH_COLOR)
        splash.paste(lulu_expressions[ui_current_expression][ui_frame_index],(0, -35))
                    
        ui_frame_index = ui_frame_index + 1
        if ui_frame_index >= len(lulu_expressions[ui_current_expression]) - 1:
            ui_frame_index = 0
            
        draw.text(
            (ui_current_message_left if ui_current_message_left_override is None else ui_current_message_left_override, 190),
            ui_current_message if ui_current_message_override is None else ui_current_message_override,
            fill=ui_current_message_color,
            font=font3
        )
                                      
    display.ShowImage(splash)
    
def detect_lulu_background():
    while True:
        logging.info("Start detect_lulu_background")
        if detect_keyword_custom(False):
            logging.info("Backgroud LULU detected")
            if (flow_state == 3):
                stop_play()
                force_stop_actions()
                time.sleep(0.5)
                xgo.reset()
            
            
        time.sleep(0.1)
    
def detect_lulu_internal():
    global keyword_detected
    
    keyword_detected = detect_keyword_custom()
    
def detect_lulu():
    global keyword_thread
    
    if keyword_detected:
        keyword_thread = None
        return True
    
    if keyword_thread is None:
        keyword_thread = threading.Thread(
            target=detect_lulu_internal
        )
        keyword_thread.start()
        
    return False

def record_and_recognize_internal():
    global recognized_speech
    
    start_recording_custom(filter_fan=True)
    recognized_speech = whisper_recognize("recorded_audio.wav")

def record_and_recognize():
    global recognition_thread
    
    if recognized_speech is not None:
        recognition_thread = None
        return recognized_speech
        
    if recognition_thread is None:
        recognition_thread = threading.Thread(
            target=record_and_recognize_internal
        )
        recognition_thread.start()
        
    return ""
        
def ask_lulu_internal(text):
    global gpt_answer
    cam_url = take_photo_and_upload()
    gpt_answer = get_gpt_answer(text, cam_url)
    
def ask_lulu(text):
    global gpt_thread
    
    if gpt_answer is not None:
        gpt_thread = None
        return gpt_answer
        
    if gpt_thread is None:
        gpt_thread = threading.Thread(
            target=ask_lulu_internal,
            args=(text,)
        )
        gpt_thread.start()
        
    return ""
    
def execute_actions_internal(script):
    global actions_script_done
    
    try:
        if script.startswith("Perplexity Client Error"):
            raise PerplexityAPIError(script)
            
        exec(script, globals(), locals())
    except SystemExit as e:
        logging.info(f"Script terminated by force_stop: {e}")
    except Exception as e:
        logging.error(f"Exception: {e}")
        logging.error(f"Traceback:\n{traceback.format_exc()}")
        
        lulu_set_expression("vertigo")
        lulu_say("Упс, не получилось выполнить команду, простите меня! Гав!")
        
    actions_script_done = True
    
def execute_actions(script):
    global actions_script_thread
    
    if actions_script_done:
        actions_script_thread = None
        return True
        
    if actions_script_thread is None:
        actions_script_thread = threading.Thread(
            target=execute_actions_internal,
            args=(script,)
        )
        actions_script_thread.start()
    
    return False
    
def terminate_thread(thread_id):
    if thread_id == 0:
        return False

    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(thread_id), ctypes.py_object(SystemExit)
    )
    
    if res == 0:
        return False
    elif res != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread_id), None)
        logging.warning("PyThreadState_SetAsyncExc affected multiple threads")
    
    return True
    
def force_stop_actions():
    global actions_script_thread, actions_script_done
    
    if actions_script_thread is None:
        return False
    
    if terminate_thread(actions_script_thread.ident):
        logging.info(f"Force stopping thread {actions_script_thread.ident}")
        actions_script_thread = None
        actions_script_done = True
        return True
    
    return False
    
def take_photo():
    picam2 = Picamera2()
    picam2.configure(
        picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
    )
    picam2.start()
    
    image = picam2.capture_array() 
    cv2.imwrite(os.path.join(current_dir, 'lulu_camera.jpg'), image)
    image = cv2.resize(image, (320, 240))
    b, g, r = cv2.split(image)
    image = cv2.merge((r, g, b))
    image = cv2.flip(image, 1)
    picam2.stop()
    picam2.close()
    cv2.destroyAllWindows()
    
def upload_temp_private_image(image_path, timeout=3600):
    with open(image_path, "rb") as f:
        files = {"file": f}
        response = requests.post(
            "https://tmpfiles.org/api/v1/upload",
            files=files,
            timeout=30
        )
    
    if response.status_code == 200:
        data = response.json()
        url = data["data"]["url"]
        direct_url = url.replace("tmpfiles.org/", "tmpfiles.org/dl/")
        logging.info(f"Camera snapshot url: {direct_url}")
        return direct_url
    else:
        return None
        
def take_photo_and_upload():
    take_photo()
    return upload_temp_private_image(os.path.join(current_dir, 'lulu_camera.jpg'))

#lulu actions

from lulu_physical_actions import *

def lulu_delete_history():
    filename = os.path.join(current_dir, "lulu_default_history.json")

    if os.path.exists(filename):
        try:
            os.remove(filename)
            logging.info(f"{filename} removed")
        except OSError as e:
            logging.error(f"Error removing {filename}: {e}")
    else:
        ogging.error(f"{filename} not found")

def lulu_say(text):
    text_to_speech(text, os.path.join(current_dir, "lulu_tts.wav"))
    audio = AudioSegment.from_wav(os.path.join(current_dir, "lulu_tts.wav"))
    audio = normalize(audio) + 15 
    #audio = audio.high_pass_filter(200).low_pass_filter(4000)
    audio.export(os.path.join(current_dir, "lulu_tts_processed.wav"), format="wav")
    play_file(os.path.join(current_dir, "lulu_tts_processed.wav"))
    
def lulu_set_expression(name):
    global ui_current_expression, ui_frame_index
    
    if ui_current_expression != name:
        ui_current_expression = name
        ui_frame_index = 0
   
def lulu_generate_image(promt):
    global ui_current_message_override, ui_current_message_left_override, generated_image_path, generated_image_buffer
    
    ui_current_message_override = "Создаю картинку!"
    ui_current_message_left_override = 30
       
    image_url = generate_image(promt)
    
    os.makedirs(os.path.join(current_dir, "generated_images"), exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(current_dir, f"generated_images/{timestamp}.jpg")
    
    response = requests.get(image_url, timeout=30)
    response.raise_for_status()
            
    img = Image.open(io.BytesIO(response.content))
    
    img.save(filename, "JPEG", quality=95)
            
    logging.info(f"Saved generated image to {filename}")
    
    generated_image_path = filename
    canvas = Image.new('RGB', (320, 240), color=(0, 0, 0))
        
    big_img = Image.open(generated_image_path)
    big_img.thumbnail((320, 240), Image.Resampling.LANCZOS)
    paste_x = (320 - big_img.width) // 2
    paste_y = (240 - big_img.height) // 2
    
    canvas.paste(big_img, (paste_x, paste_y))
        
    generated_image_buffer = canvas
    
    ui_current_message_override = None
    ui_current_message_left_override = None
    
    while generated_image_buffer != None:
        time.sleep(0.1)

#end lulu actions

def show_message(text, color=(255, 255, 255)):
    draw.rectangle((0, 0, display.height, display.width), fill=SPLASH_COLOR)
    draw.text((80, 100), text, fill=color, font=font2)
    display.ShowImage(splash)
    
def button_listener():
    global generated_image_buffer
    
    while True:
        if button.press_b():
            if flow_state != 3:
                logging.info("Button B pressed, exiting")
                os._exit(0)
            else:
                if generated_image_buffer is not None:
                    logging.info("Exiting generated image")
                    generated_image_buffer = None
                else:
                    stop_play()
                    force_stop_actions()
                    time.sleep(0.5)
                    xgo.reset()
        time.sleep(0.1)

show_message("Загружаемся...", color=(255, 255, 255))

lulu_expressions = scan_rider_expressions()
   
#define base fuctions
button=Button()

#Button listening thread
button_thread = threading.Thread(target=button_listener)
button_thread.daemon = True  
button_thread.start()

'''
- experimental force stop by saying LULU during performing
- works bad due to motors noise

keyword_backgroud_thread = threading.Thread(
    target=detect_lulu_background
)
keyword_backgroud_thread.daemon = True
keyword_backgroud_thread.start()
'''

while True:
    draw_ui()
    
    #initial state
    if flow_state == -1:
        logging.info("Waiting for LULU")
        flow_state = 0
        continue
    
    #detect LULU keyword
    if flow_state == 0:
        ui_current_message = "Скажи ЛУЛУ!"
        ui_current_message_left = 60
        
        if detect_lulu():            
            logging.info("LULU recognized")
            
            flow_state = 1
            
        continue
            
    #speech recognition        
    if flow_state == 1:
        lulu_set_expression("cute")
        ui_current_message = "Я слушаю!"
        ui_current_message_left = 80
            
        if record_and_recognize() != "":
            logging.info("Recognized speech: " + recognized_speech)
            
            flow_state = 2
        continue
    
    #gpt
    if flow_state == 2:
        lulu_set_expression("doubt")
        ui_current_message = "Думаю..."
        ui_current_message_left = 100
        
        if ask_lulu(recognized_speech) != "":
            #logging.info("GPT answer: " + gpt_answer)
            
            lulu_set_expression("cute")
            
            flow_state = 3
        continue
    
    #performing
    if flow_state == 3:
        ui_current_message = "Исполняю!"
        ui_current_message_left = 80
        
        if execute_actions(gpt_answer):        
            flow_state = 1000
            continue
    
    #loop end
    if flow_state == 1000:
        time.sleep(1)
        reinit()
        
        continue

    time.sleep(0.05)  
