import time
import os
import threading
from datetime import datetime
from flask import Flask, render_template, jsonify
from gpiozero import DigitalOutputDevice, DigitalInputDevice, Button

app = Flask(__name__)

# --- CẤU HÌNH GPIO (RASPBERRY PI 5) ---
PIN_TRIG = 23      # Physical Pin 16
PIN_ECHO = 24      # Physical Pin 18 (Qua 1 điện trở bảo vệ 4.7kΩ)
PIN_PIR = 17       # Physical Pin 11 (HW-416A / HC-SR501)
PIN_TOUCH = 27     # Physical Pin 13 (WH-139 / TTP223)
BIN_HEIGHT_CM = 35.0  # Chiều cao lòng thùng rác (cm)

# Đường dẫn đọc DHT11 từ Linux Kernel IIO Driver (dtoverlay=dht11,gpiopin=4)
TEMP_PATH = "/sys/bus/iio/devices/iio:device0/in_temp_input"
HUM_PATH = "/sys/bus/iio/devices/iio:device0/in_humidityrelative_input"

# Khởi tạo các cảm biến
trig = DigitalOutputDevice(PIN_TRIG)
echo = DigitalInputDevice(PIN_ECHO, pull_up=False)
pir = DigitalInputDevice(PIN_PIR, pull_up=False)
touch = Button(PIN_TOUCH, pull_up=False)

# Trạng thái dữ liệu thời gian thực
state = {
    "distance": 0.0,
    "fill_pct": 0.0,
    "temperature": 0.0,
    "humidity": 0.0,
    "person_detected": False,
    "usage_count": 0,
    "last_cleaned": "Chưa có",
    "alert": "Bình thường"
}


def measure_distance():
    """Đo khoảng cách (cm) bằng cảm biến siêu âm HC-SR04 theo nguyên lý Time-of-Flight."""
    try:
        trig.off()
        time.sleep(0.02)
        trig.on()
        time.sleep(0.00001)
        trig.off()

        t0 = time.time()
        pulse_start = time.time()
        while echo.value == 0:
            pulse_start = time.time()
            if pulse_start - t0 > 0.04:
                return None

        t1 = time.time()
        pulse_end = time.time()
        while echo.value == 1:
            pulse_end = time.time()
            if pulse_end - t1 > 0.04:
                return None

        duration = pulse_end - pulse_start
        return (duration * 34300) / 2
    except Exception:
        return None


def loop_sensors():
    """Luồng nền đọc liên tục HC-SR04, PIR HW-416A và cảm biến chạm WH-139."""
    prev_pir = False
    while True:
        try:
            # 1. Đo mức rác
            dist = measure_distance()
            if dist is not None:
                dist = min(dist, BIN_HEIGHT_CM)
                pct = ((BIN_HEIGHT_CM - dist) / BIN_HEIGHT_CM) * 100.0
                state["distance"] = round(dist, 1)
                state["fill_pct"] = round(max(0.0, min(100.0, pct)), 1)

            # 2. Phát hiện người & đếm lượt bỏ rác (Sườn xung lên L-mode)
            current_pir = (pir.value == 1)
            state["person_detected"] = current_pir
            if current_pir and not prev_pir:
                state["usage_count"] += 1
            prev_pir = current_pir

            # 3. Cảm biến chạm WH-139 (Xác nhận thu gom rác)
            if touch.is_pressed:
                state["last_cleaned"] = datetime.now().strftime("%H:%M:%S - %d/%m/%Y")
                time.sleep(0.5)

            # 4. Đánh giá trạng thái cảnh báo
            if state["fill_pct"] >= 90:
                state["alert"] = "CẢNH BÁO: Thùng rác đã đầy! Vui lòng thu gom."
            elif state["temperature"] > 45:
                state["alert"] = "NGUY HIỂM: Nhiệt độ trong thùng cao bất thường!"
            else:
                state["alert"] = "Bình thường"

        except Exception:
            pass

        time.sleep(0.3)


def loop_dht():
    """Luồng nền đọc nhiệt độ & độ ẩm từ Linux Kernel IIO Driver (DHT11)."""
    while True:
        try:
            if os.path.exists(TEMP_PATH) and os.path.exists(HUM_PATH):
                with open(TEMP_PATH, "r") as f:
                    state["temperature"] = round(float(f.read().strip()) / 1000.0, 1)
                with open(HUM_PATH, "r") as f:
                    state["humidity"] = round(float(f.read().strip()) / 1000.0, 1)
        except Exception:
            pass
        time.sleep(2.5)


# Chạy ngầm các luồng đọc cảm biến
threading.Thread(target=loop_sensors, daemon=True).start()
threading.Thread(target=loop_dht, daemon=True).start()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/data")
def api():
    return jsonify(state)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
