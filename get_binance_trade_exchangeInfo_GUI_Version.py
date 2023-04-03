import sys
import time 
import requests
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
from get_binance_trade_exchangeInfo import write_txt
from PyQt5.QtWidgets import QApplication, QDialog, QFormLayout
from PyQt5.QtWidgets import (QPushButton, QLineEdit, QLabel)

def time2number(input):
    timeString = "2022-02-06 15:33:00" # 時間格式為字串
    struct_time = time.strptime(input, "%Y-%m-%d %H:%M:%S") # 轉成時間元組
    time_stamp = int(time.mktime(struct_time)) # 轉成時間戳
    return time_stamp

def number2time(input):
    time_stamp = 1644132840 # 設定timeStamp
    struct_time = time.localtime(input) # 轉成時間元組
    timeString = time.strftime("%Y-%m-%d %H:%M:%S", struct_time) # 轉成字串
    return timeString
#https://api3.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&startTime=1644132840000&endTime=1644132900000&limit=1

def get_data(symbol, startTime, endTime):
    my_params = {'symbol': symbol, 'interval': '1m', 'startTime': startTime, 'endTime': endTime, 'limit': '1'}
    r = requests.get("https://api3.binance.com/api/v3/klines", params = my_params)
    #print(len(r.text))
    if len(r.text) > 2:
        #print(r.url)
        #print(r.text)        
        get_result = r.json()
        Start_at = number2time(get_result[0][0] / 1000)
        Open = float(get_result[0][1])
        High = float(get_result[0][2])
        Low = float(get_result[0][3])
        Close = float(get_result[0][4])
        Vol = float(get_result[0][7])
        if Vol<5000:
            return [0, 0 , 0, 0, 0, 0]
        else:
            return [Start_at, Open , High, Low, Close, Vol]
    else:
        return [0, 0 , 0, 0, 0, 0]

def get_percent_list(start_time, end_time):
        
        trade_pair_1 = []
        trade_pair_2 = [] 
        if time2number(end_time) > time2number(start_time):
            start_time_result = get_data("BTCUSDT", time2number(start_time)*1000, time2number(start_time)*1000 + 60000)
            end_time_result = get_data("BTCUSDT", time2number(end_time)*1000, time2number(end_time)*1000 + 60000)
        else:
            print("時間錯誤")
        persent = (end_time_result[4] - start_time_result[4]) / start_time_result[4]
        trade_pair_1.append("BTCUSDT") #trading pair string
        trade_pair_2.append(persent*100) #trading pair persent
        count = write_txt()
        f = open('output.txt')
        for line in tqdm(f.readlines()):
            start_time_result = get_data(str(line.strip()), time2number(start_time)*1000, time2number(start_time)*1000 + 60000)
            end_time_result = get_data(str(line.strip()), time2number(end_time)*1000, time2number(end_time)*1000 + 60000)
            if start_time_result[0] == 0 or end_time_result[0] == 0:
                continue
            else:
                persent = (end_time_result[4] - start_time_result[4]) / start_time_result[4]
                trade_pair_1.append(line.strip()) #trading pair string
                trade_pair_2.append(persent*100)  #trading pair persent
                time.sleep(0.15)       
        f.close
        return trade_pair_1, trade_pair_2   

class Form(QDialog):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        self.le = QLineEdit()
        self.le.setObjectName("LineEdit_start")

        self.le_2 = QLineEdit()
        self.le_2.setObjectName("LineEdit_end")

        self.pb = QPushButton()
        self.pb.setObjectName("Start_Button")
        self.pb.setText("Start")
        self.pb.clicked.connect(self.button_click)

        self.lb = QLabel()
        self.lb.setText("輸入起始時間(2022-02-06 15:33:00):")

        self.lb_2 = QLabel()
        self.lb_2.setText("輸入結束時間(2022-02-06 18:33:00):") 

        layout = QFormLayout()
        layout.addWidget(self.le)
        layout.addWidget(self.lb)
        layout.addWidget(self.le_2)
        layout.addWidget(self.lb_2)
        layout.addWidget(self.pb)
        self.setLayout(layout)

        self.setWindowTitle("Binance API Beta V1.0")
        self.resize(500, 200)

    def button_click(self):
        start = time.time()
        # shost is a QString object
        start_time = self.le.text()
        end_time = self.le_2.text()


        trade_pair_1, trade_pair_2 = get_percent_list(start_time, end_time)
        list_index = np.argsort(trade_pair_2)[::-1]
        trade_pair_1_sort = np.array(trade_pair_1)[list_index]
        trade_pair_2_sort = np.array(trade_pair_2)[list_index]
        end = time.time()
        print("cost time:", end - start)
        for i in range(len(trade_pair_1_sort)):
            print(trade_pair_1_sort[i], trade_pair_2_sort[i])

        btc_index = trade_pair_1_sort.tolist().index("BTCUSDT")
        eth_index = trade_pair_1_sort.tolist().index("ETHUSDT")
        color = ['blue']*len(trade_pair_1_sort)
        color[btc_index] = 'red'
        color[eth_index] = 'green'
        plt.barh(range(len(trade_pair_1_sort)), trade_pair_2_sort, tick_label=trade_pair_1_sort, color = color)
        plt.show()

app = QApplication(sys.argv)
form = Form()
form.show()

app.exec_()