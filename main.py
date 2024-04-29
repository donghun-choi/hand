import cv2
import mediapipe as mp
import math
import pyautogui
from pynput.mouse import Controller, Button

mouse = Controller()
size = [pyautogui.size().width, pyautogui.size().height]
cap = cv2.VideoCapture(0)
hands = mp.solutions.hands.Hands()
scrollY = 0

# 전역병신들
preMouseLBcondition = mouseLBcondition = scroll = 0
mousePosition = None
smooth_factor = 0.5
scroll_smooth_factor = 1

# 함수 정의
def smooth_position(current_pos, previous_pos, factor):
    if previous_pos is None:
        return current_pos
    else:
        return (int(previous_pos[0] * (1 - factor) + current_pos[0] * factor),
                int(previous_pos[1] * (1 - factor) + current_pos[1] * factor))

def smooth_scroll(current_scroll, target_scroll, factor):
    return current_scroll + (target_scroll - current_scroll) * factor

def cd(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def cal_distance(x1, y1, x2, y2, x3, y3):
    a = cd(x1, y1, x2, y2)
    b = cd(x2, y2, x3, y3)
    c = cd(x3, y3, x1, y1)
    s = (a + b + c) / 3
    return s

while 1:
    success, img = cap.read()
    imgrgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgrgb)

    if results.multi_hand_landmarks:
        for handlms in results.multi_hand_landmarks:
            
            lm4 = handlms.landmark[4]
            lm8 = handlms.landmark[8]
            lm5 = handlms.landmark[5]
            lm9 = handlms.landmark[9]
            lm7 = handlms.landmark[7]
            lm12 = handlms.landmark[12]
            
            distance_rel     = (math.sqrt((lm5.x -lm9.x) ** 2 + (lm5.y - lm9.y) ** 2)) * 1.2
            distance_lm4_lm8 = (math.sqrt((lm4.x - lm8.x) ** 2 + (lm4.y - lm8.y) ** 2))
            dis_lm4_lm8_lm12 = (cal_distance(lm4.x, lm4.y, lm8.x, lm8.y, lm12.x, lm12.y))
            
            x_ctr = ((lm4.x - 0.5) * 2) ** 2 + 1
            y_ctr = ((lm4.y - 0.5) * 2) ** 2 + 1
            # corrected_coords = [ size[0] * lm4.x * x_ctr, size[1] * lm4.y * y_ctr]
            corrected_coords = [ size[0] * lm4.x, size[1] * lm4.y-500]

            mousePosition = smooth_position((size[0] - corrected_coords[0], corrected_coords[1]), mousePosition, smooth_factor)
            
            if mousePosition is not None:
                scrollY = -(mousePosition[1] - corrected_coords[1]) / 10

            if dis_lm4_lm8_lm12 < distance_rel and distance_lm4_lm8 < distance_rel or dis_lm4_lm8_lm12 < distance_rel:
                mouseLBcondition = 0
                scroll = 1
                continue

            if distance_lm4_lm8 < distance_rel:
                mouseLBcondition = 1
                scroll = 0
            else:
                scroll = 0
                mouseLBcondition = 0
                
        if not scroll:
            mouse.position = mousePosition
        if scroll:
            scrollY = smooth_scroll(0, scrollY, scroll_smooth_factor)
            mouse.scroll(0, scrollY)
            continue

        # if mouseLBcondition == preMouseLBcondition:
        #     continue
        
        if mouseLBcondition == 1 and preMouseLBcondition != mouseLBcondition:
            mouse.click(Button.left)
            # continue
        
        if mouseLBcondition == 1 and preMouseLBcondition == mouseLBcondition:
            # mouse.press(Button.left)
            continue
        
        # 마우스 왼쪽 버튼이 떨어진 상태이면 이전 상태와 다르면 릴리즈
        if mouseLBcondition == 0 and preMouseLBcondition != mouseLBcondition:
            mouse.release(Button.left)
        
        preMouseLBcondition = mouseLBcondition
        
        