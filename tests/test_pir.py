import time
from gpiozero import MotionSensor
from signal import pause

# Cảm biến PIR HW-416A cắm OUT -> GPIO 17 (Pin 11)
pir = MotionSensor(17)

print("=" * 45)
print("  KIỂM THỬ CẢM BIẾN HỒNG NGOẠI PIR (HW-416A)")
print("  Hãy vẫy tay trước cảm biến (Bấm Ctrl + C để dừng)")
print("=" * 45)

def on_motion():
    print(">>> [CẢNH BÁO] Phát hiện có người đến gần thùng rác!")

def on_no_motion():
    print("--- Không có chuyển động.")

pir.when_motion = on_motion
pir.when_no_motion = on_no_motion

try:
    pause()
except KeyboardInterrupt:
    print("\nĐã dừng kiểm thử PIR.")
