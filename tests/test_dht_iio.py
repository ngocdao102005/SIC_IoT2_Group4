import os
import time

# Đường dẫn sysfs của Linux Kernel IIO Driver (dtoverlay=dht11,gpiopin=4)
TEMP_PATH = "/sys/bus/iio/devices/iio:device0/in_temp_input"
HUM_PATH = "/sys/bus/iio/devices/iio:device0/in_humidityrelative_input"

print("=" * 45)
print("  KIỂM THỬ DHT11 QUA LINUX KERNEL IIO DRIVER")
print("  (Bấm Ctrl + C để dừng)")
print("=" * 45)

try:
    while True:
        if os.path.exists(TEMP_PATH) and os.path.exists(HUM_PATH):
            try:
                with open(TEMP_PATH, "r") as f:
                    temp = float(f.read().strip()) / 1000.0
                with open(HUM_PATH, "r") as f:
                    hum = float(f.read().strip()) / 1000.0
                print(f"Nhiệt độ: {temp:.1f} °C  |  Độ ẩm: {hum:.1f} %")
            except OSError as e:
                print(f"Chờ đồng bộ xung từ Kernel IIO... ({e})")
        else:
            print("Chưa tìm thấy /sys/bus/iio/devices/iio:device0. Kiểm tra dtoverlay=dht11,gpiopin=4!")
        time.sleep(2.5)
except KeyboardInterrupt:
    print("\nĐã dừng kiểm thử DHT11.")
