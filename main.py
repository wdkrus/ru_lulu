from demos.uiutils import la, Button, get_language, show_button, show_button_custom, display, show_battery, load_language, draw, DogTypeChecker, lcd_draw_string, color_white, font1, font2, show_button_template, show_button_template_custom, splash,dog
from PIL import Image
import socket, os, time
from xgolib import XGO

current_selection = 1

# Initialize the button
button = Button()
la = load_language()

last_battery_check_time = time.time()
last_network_check_time = time.time()
is_online = False

frame_index = 0

def run_program_custom(selection):
    show_button_custom(0, 320, 90, "OPENING")
    display.ShowImage(splash)
    
    def action_1():
        os.system('python3 ./app/app_dogzilla.py')
               
    def action_2():
        os.system("python3 demos/RuLulu/ru_lulu.py")
        
    def action_3():
        os.system("python3 demoen.py")

    actions = {
        1: action_1,
        2: action_2,
        3: action_3
    }

    if selection in actions:
        actions[selection]()
    
def main():    
    global key_state_left, key_state_right, key_state_down, current_selection, frame_index
    splash.paste(frames[frame_index],(0, -35))
    update_status()
    key_state_left = key_state_right = key_state_down = 0

    if button.press_a():
        key_state_down = 1
    elif button.press_c():
        key_state_left = 1
    elif button.press_d():
        key_state_right = 1
    elif button.press_b():
        print("b button, but nothing to quit")

    if key_state_left == 1:
        current_selection = current_selection - 1 if current_selection > 1 else 3
    elif key_state_right == 1:
        current_selection = current_selection + 1 if current_selection < 3 else 1
   
    button_ranges = [(0, 110), (110, 210), (210, 320)]
    button_texts = [
        ("WIFIAPP", "GPT", "TRYDEMO"),
        ("WIFIAPP", "GPT", "TRYDEMO"),
        ("WIFIAPP", "GPT", "TRYDEMO")
    ]
    
    left, right = button_ranges[current_selection - 1]
    text1, text2, text3 = button_texts[current_selection - 1]
    show_button_template_custom(left, right, text1, text2, text3)
 
    if key_state_down == 1:
        show_battery()
        run_program_custom(current_selection)
        print(f"{current_selection} select")
      
    frame_index = frame_index + 1
    if frame_index >= 75:
        frame_index = 0
        
    display.ShowImage(splash)

def is_connected(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print(f"network err: {ex}")
        return False
        
def update_status():
    global last_battery_check_time, last_network_check_time, is_online
    now = time.time()

    if now - last_battery_check_time > 3:
        show_battery()
        last_battery_check_time = now
    else:
        show_battery(False)

    if now - last_network_check_time > 3:
        is_online = is_connected()
        last_network_check_time = now

    if is_online:
        draw.bitmap((10, 0), wifiy)

current_dir = os.path.dirname(os.path.abspath(__file__))
logo = Image.open(os.path.join(current_dir, "pics", "luwu@3x.png"))
wifiy = Image.open(os.path.join(current_dir, "pics", "wifi@2x.png"))
bat = Image.open(os.path.join(current_dir, "pics", "battery.png"))

if is_connected():
    draw.bitmap((10, 0), wifiy)
    draw.bitmap((74, 49), logo)
else:
    draw.bitmap((74, 49), logo)
    print("Wifi,Unconnection")

show_battery()

current_selection = 1

last_check_time = time.time()

BASE_EMO_DIR = "/home/pi/xgoPictures/expression/rider/cute"
frames = []

for i in range(1, 76):
    path = os.path.join(BASE_EMO_DIR, f"cute{i:02}.png")
    img = Image.open(path)
    frames.append(img)

while True:
    main()   

