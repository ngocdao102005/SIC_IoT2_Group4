import time
from gpiozero import DistanceSensor

# Khởi tạo HC-SR04: Echo GPIO 24 (Pin 18 qua trở 4.7kΩ), Trig GPIO 23 (Pin 16)
sensor = DistanceSensor(echo=24, trigger=23, max_distance=2.0)

print("=" * 45)
print("  KIỂM THỬ CẢM BIẾN SIÊU ÂM HC-SR04")
print("  (Bấm Ctrl + C để dừng)")
print("=" * 45)

try:
    while True:
        dist_cm = sensor.distance * 100.0
        print(f"Khoảng cách đo được: {dist_cm:.1f} cm")
        time.sleep(0.5)
except KeyboardInterrupt:
    print("\nĐã dừng kiểm thử HC-SR04.")
