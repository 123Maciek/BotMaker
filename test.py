import pyautogui
import time
import keyboard
import sys

time.sleep(5)
end_loop = False

def play_actions(act):
    start = time.time()

    for action in act:
        action_type, *params, timestamp = action

        elapsed_time = time.time() - start
        delay = timestamp - elapsed_time

        pyautogui.PAUSE = max(0, delay)

        if action_type == "mouse_move":
            x, y = params
            pyautogui.moveTo(x, y)
        elif action_type == "mouse_press":
            x, y, button = params
            pyautogui.mouseDown(x, y, button)
        elif action_type == "mouse_release":
            x, y, button = params
            pyautogui.mouseUp(x, y, button)
        elif action_type == "key_press":
            key = params[0]
            pyautogui.keyDown(key)
        elif action_type == "key_release":
            key = params[0]
            pyautogui.keyUp(key)
def text_to_action(text):
    lines = text.split("\n")
    act = []
    for line in lines:
        if line != "":
            line = line[:-1]
            line = line[1:]
            line = line.replace(" ", "")
            args = line.split(",")
            arr = []
            for arg in args:
                if arg[0] == "'" and arg[len(arg)-1] == "'":
                    arg = arg[1:]
                    arg = arg[:-1]
                else:
                    try:
                        arg = int(arg)
                    except:
                        arg = float(arg)
                arr.append(arg)
            act.append(arr)
    return act



macroLoc = r"C:/Users/Admin/Documents\BotMaker/Notepad-Bot/Macros/"
with open(macroLoc + 'Open-Notepad.txt', 'r') as file:
        play_actions(text_to_action(file.read()))
if keyboard.is_pressed('m'):
        sys.exit()
for i in range(3):
        if keyboard.is_pressed('m'):
                sys.exit()
        with open(macroLoc + 'Write-Text.txt', 'r') as file:
                play_actions(text_to_action(file.read()))
        if keyboard.is_pressed('m'):
                sys.exit()
        with open(macroLoc + 'DeleteText.txt', 'r') as file:
                play_actions(text_to_action(file.read()))
        if keyboard.is_pressed('m'):
                sys.exit()
if keyboard.is_pressed('m'):
        sys.exit()