import pyaudio,wave,random, subprocess
import wave
import numpy as np
from scipy import fftpack
import os,time
from datetime import datetime
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from auto_platform import AudiostreamSource, play_command
from libnyumaya import AudioRecognition, FeatureExtractor
from uiutils import Button,mic_logo,mic_purple,splash_theme_color,clear_top,draw,splash,display,la,lcd_draw_string,get_font

from PIL import Image, ImageDraw, ImageFont

font1=get_font(17)
button=Button()

SAVE_FILE = "recorded_audio.wav"




# 关键词检测参数 Keyword detection parameters
KEYWORD_MODEL_PATH = "./demos/src/lulu_v3.1.907.premium"
KEYWORD_THRESHOLD = 0.6
PLAY_COMMAND = "aplay"
aplay_process = None

def calculate_volume(data):

    rt_data = np.frombuffer(data, dtype=np.int16)
    fft_temp_data = fftpack.fft(rt_data, rt_data.size, overwrite_x=True)
    fft_data = np.abs(fft_temp_data)[0: fft_temp_data.size // 2 + 1]
    return sum(fft_data) // len(fft_data)

def draw_cir(ch):
    if ch > 15:
        ch = 15
    clear_top()
    draw.bitmap((145, 40), mic_logo, mic_purple)
    radius = 4
    cy = 60
    centers = [(62, cy), (87, cy), (112, cy), (210, cy), (235, cy), (260, cy)]
    for center in centers:
        random_offset = random.randint(0, ch)
        new_y = center[1] + random_offset
        new_y2 = center[1] - random_offset

        draw.line([center[0], new_y2, center[0], new_y], fill=mic_purple, width=11)

        top_left = (center[0] - radius, new_y - radius)
        bottom_right = (center[0] + radius, new_y + radius)
        draw.ellipse([top_left, bottom_right], fill=mic_purple)
        top_left = (center[0] - radius, new_y2 - radius)
        bottom_right = (center[0] + radius, new_y2 + radius)
        draw.ellipse([top_left, bottom_right], fill=mic_purple)



def draw_wave(ch):
    ch = min(ch, 10)
    clear_top()
    draw.bitmap((145, 40), mic_logo, mic_purple)
    
    wave_params = [
        {"start_x": 40, "start_y": 32, "width": 80, "height": 50},
        {"start_x": 210, "start_y": 32, "width": 80, "height": 50}
    ]
    
    for params in wave_params:
        draw_single_wave(
            params["start_x"], 
            params["start_y"], 
            params["width"], 
            params["height"], 
            ch
        )

def draw_single_wave(start_x, start_y, width, height, ch):
    y_center = height // 2
    current_y = y_center
    previous_point = (start_x, y_center + start_y)
    
    if start_x > 200: 
        draw.rectangle(
            [(start_x - 1, start_y), (start_x + width, start_y + height)],
            fill=splash_theme_color,
        )
    
    x = 0
    while x < width:
        seg_len = random.randint(7, 25)
        gap_len = random.randint(4, 20)
        
        for _ in range(seg_len):
            if x >= width: break
            current_y = max(0, min(height - 1, current_y + random.randint(-ch, ch)))
            current_point = (x + start_x, current_y + start_y)
            draw.line([previous_point, current_point], fill=mic_purple)
            previous_point, x = current_point, x + 1
        
        for _ in range(gap_len):
            if x >= width: break
            current_point = (x + start_x, y_center + start_y)
            draw.line([previous_point, current_point], fill=mic_purple, width=2)
            previous_point, x = current_point, x + 1

 
def visual(content):
    gray_color = (128, 128, 128)
    rectangle_x = (display.width - 120) // 2 
    rectangle_y = 110  
    rectangle_width = 200
    rectangle_height = 80
    draw.rectangle((rectangle_x, rectangle_y, rectangle_x + rectangle_width, rectangle_y + rectangle_height),
                   fill=gray_color)
    def lcd_draw_string(
            splash,
            x,
            y,
            text,
            color=(255, 255, 255),
            font_size=16,
            max_width=220,
            max_lines=5,
            clear_area=False
    ):
        font = ImageFont.truetype("/home/pi/model/msyh.ttc", font_size)
        line_height = font_size + 2
        total_height = max_lines * line_height
        if clear_area:
            draw.rectangle((x, y, x + max_width, y + total_height), fill=(15, 21, 46))
        lines = []
        current_line = ""
        for char in text:
            test_line = current_line + char
            if font.getlength(test_line) <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = char
        if current_line:
            lines.append(current_line)
        if max_lines:
            lines = lines[:max_lines]

        for i, line in enumerate(lines):
            splash.text((x, y + i * line_height), line, fill=color, font=font)

    lcd_draw_string(
        draw,
        x=70,
        y=115,
        text=content,
        color=(255, 255, 255),
        font_size=16,
        max_width=190,
        max_lines=5,
        clear_area=False
    )



            
from Fan_noise import FanNoiseFilter
fan_filter = FanNoiseFilter(noise_file="/home/pi/RaspberryPi-CM5/fannoise.wav") 


import threading

import subprocess
def is_mplayer_running():
    # 检查mplayer进程
    result = subprocess.run(['pgrep', 'mplayer'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.returncode == 0

button_flag = 0
#按键处理事件
def Button_Thread():
    global button_flag
    while True:
        if button.press_c():
            button_flag = 1
            print("lulu detected ok")
            break
            
def detect_keyword_custom(play_ding=True):
    global button_flag
    audio_stream = AudiostreamSource()
    libpath = "./demos/src/libnyumaya_premium.so.3.1.0"
    extractor = FeatureExtractor(libpath)
    detector = AudioRecognition(libpath)
    extractor_gain = 1.0
    keyword_id = detector.addModel(KEYWORD_MODEL_PATH, KEYWORD_THRESHOLD)
    bufsize = detector.getInputDataSize()
    audio_stream.start()
 
    print("Waiting for keyword...")
    
    
    while True:       
        frame = audio_stream.read(bufsize * 2, bufsize * 2)
        if not frame:
            continue
        
        if is_mplayer_running()==0:
            rt_data = np.frombuffer(frame, dtype=np.int16)
            fft_temp_data = fftpack.fft(rt_data, rt_data.size, overwrite_x=True)
            fft_data = np.abs(fft_temp_data)[0:fft_temp_data.size // 2 + 1]
            vol = sum(fft_data) // len(fft_data)
                       
        denoised_data = fan_filter.filter_fan_noise(frame)

        features = extractor.signalToMel(denoised_data, extractor_gain)
        prediction = detector.runDetection(features)

        if prediction == keyword_id:
            now = datetime.now().strftime("%d.%b %Y %H:%M:%S")
            print(f"Keyword detected: {now}")
            if play_ding:
                os.system(f"{PLAY_COMMAND} ./demos/src/ding.wav")
            return True
            
def detect_keyword():
    global button_flag
    # 初始化关键词检测 Initialize keyword detection
    audio_stream = AudiostreamSource()
    libpath = "./demos/src/libnyumaya_premium.so.3.1.0"
    extractor = FeatureExtractor(libpath)
    detector = AudioRecognition(libpath)
    extractor_gain = 1.0
    keyword_id = detector.addModel(KEYWORD_MODEL_PATH, KEYWORD_THRESHOLD)
    bufsize = detector.getInputDataSize()
    audio_stream.start()
 
    print("Waiting for keyword...")
    
    tts_thread = threading.Thread(target=Button_Thread)
    tts_thread.daemon = True  
    tts_thread.start()
    
    while True:
        #这里添加个手动唤醒，自动唤醒不好触发
        if button_flag == 1:
            button_flag =0
            os.system("sudo pkill mplayer") 
            time.sleep(.1)
            os.system(play_command + " /home/pi/RaspberryPi-CM5/ding.wav")
            return True
        
        # 读取音频数据 Read audio data
        frame = audio_stream.read(bufsize * 2, bufsize * 2)
        if not frame:
            continue
        
        #无东西播放的情况才显示录音
        if is_mplayer_running()==0:
             # 绘制波形（直接使用当前帧） Draw waveform (using the current frame directly)
            rt_data = np.frombuffer(frame, dtype=np.int16)
            fft_temp_data = fftpack.fft(rt_data, rt_data.size, overwrite_x=True)
            fft_data = np.abs(fft_temp_data)[0:fft_temp_data.size // 2 + 1]
            vol = sum(fft_data) // len(fft_data)
            # if la=="cn": #这种案例不需要这样显示
            #     visual(content='请说:“lulu”,或者按下左上方按键 唤醒机器人')
            # else:
            #     visual(content="Please say: 'lulu' Or press the upper left button to wake up the robot.")
                
            draw_wave(int(vol / 10000))
            display.ShowImage(splash)
        
        
        # 使用风扇噪声过滤器处理音频数据
        denoised_data = fan_filter.filter_fan_noise(frame)

        # 关键词检测 keyword spotting
        features = extractor.signalToMel(denoised_data, extractor_gain)
        prediction = detector.runDetection(features)

        if prediction == keyword_id:
            now = datetime.now().strftime("%d.%b %Y %H:%M:%S")
            print(f"Keyword detected: {now}")
            os.system(f"{PLAY_COMMAND} ./demos/src/ding.wav")
            return True

quitmark = 0
automark = True 
def start_recording(timel = 3,save_file=SAVE_FILE,filter_fan=False):
    global automark,quitmark
    start_threshold = 220000 #30000
    end_threshold = 40000 #20000
    endlast = 15
    max_record_time = 5 
    
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    WAVE_OUTPUT_FILENAME = save_file 

    
    if automark:
        p = pyaudio.PyAudio()       
        stream_a = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
        frames = []
        start_luyin = False
        break_luyin = False
        data_list =[0]*endlast
        sum_vol=0
        start_time = None

        while not break_luyin:
            if not automark or quitmark == 1:
                break

            data = stream_a.read(CHUNK, exception_on_overflow=False)
            rt_data = np.frombuffer(data, dtype=np.int16)
            fft_temp_data = fftpack.fft(rt_data, rt_data.size, overwrite_x=True)
            fft_data = np.abs(fft_temp_data)[0 : fft_temp_data.size // 2 + 1]
            vol = sum(fft_data) // len(fft_data)
            
            data_list.pop(0)
            data_list.append(vol)
            
            print(f"Current volume: {vol}, boot threshold: {start_threshold}, End threshold: {end_threshold}")
            
            if vol > start_threshold:
                sum_vol += 1
                if sum_vol == 1:
                    print("start recording")
                    start_luyin = True
                    start_time = time.time()
            
            if start_luyin:
                elapsed_time = time.time() - start_time
                
                if all(float(i) < end_threshold for i in data_list) or elapsed_time > max_record_time:
                    print("Recording ends: Low volume or recording time exceeds the limit")
                    break_luyin = True
                    frames = frames[:-5]
            
            if start_luyin:
                frames.append(data)
            print(start_threshold, vol)
            draw_cir(int(vol / 10000))
            display.ShowImage(splash)
        print("auto end")
        


    if quitmark==0:
        try:
            stream_a.stop_stream()
            stream_a.close()
        except:
            pass
        p.terminate()
        
        if filter_fan:
            frames = fan_filter.filter_fan_noise(frames)

        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')  
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        print(f"The recording has been saved as: {WAVE_OUTPUT_FILENAME}")

def start_recording_custom(timel = 3,save_file=SAVE_FILE,filter_fan=False):
    global automark,quitmark
    start_threshold = 220000 #30000
    end_threshold = 40000 #20000
    endlast = 15
    max_record_time = 5 
    
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    WAVE_OUTPUT_FILENAME = save_file 

    
    if automark:
        p = pyaudio.PyAudio()       
        stream_a = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
        frames = []
        start_luyin = False
        break_luyin = False
        data_list =[0]*endlast
        sum_vol=0
        start_time = None

        while not break_luyin:
            if not automark or quitmark == 1:
                break

            data = stream_a.read(CHUNK, exception_on_overflow=False)
            rt_data = np.frombuffer(data, dtype=np.int16)
            fft_temp_data = fftpack.fft(rt_data, rt_data.size, overwrite_x=True)
            fft_data = np.abs(fft_temp_data)[0 : fft_temp_data.size // 2 + 1]
            vol = sum(fft_data) // len(fft_data)
            
            data_list.pop(0)
            data_list.append(vol)
            
            print(f"Current volume: {vol}, boot threshold: {start_threshold}, End threshold: {end_threshold}")
            
            if vol > start_threshold:
                sum_vol += 1
                if sum_vol == 1:
                    print("start recording")
                    start_luyin = True
                    start_time = time.time()
            
            if start_luyin:
                elapsed_time = time.time() - start_time
                
                if all(float(i) < end_threshold for i in data_list) or elapsed_time > max_record_time:
                    print("Recording ends: Low volume or recording time exceeds the limit")
                    break_luyin = True
                    frames = frames[:-5]
            
            if start_luyin:
                frames.append(data)
            print(start_threshold, vol)
        print("auto end")
        


    if quitmark==0:
        try:
            stream_a.stop_stream()
            stream_a.close()
        except:
            pass
        p.terminate()
        
        if filter_fan:
            frames = fan_filter.filter_fan_noise(frames)

        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')  
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        print(f"The recording has been saved as: {WAVE_OUTPUT_FILENAME}")
        
def play_file(file_path):
    os.system(f"{PLAY_COMMAND} {file_path}")
    #aplay_process = subprocess.Popen(["aplay", file_path])
    #aplay_process.wait()
    #aplay_process = None
    
def stop_play():
    try:
        subprocess.run(["pkill", "-9", "aplay"], check=True)
        print("aplay killed")
    except subprocess.CalledProcessError:
        print("aplay not found")
