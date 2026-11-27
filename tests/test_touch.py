from gpiozero import Button
from datetime import datetime
from signal import pause

# Cảm biến chạm WH-139 (TTP223) cắm SIG -> GPIO 27 (Pin 13)
touch = Button(27, pull_up=False)

print("=" * 45)
print("  KIỂM THỬ CẢM BIẾN CHẠM WH-139 (TTP223)")
print("  Hãy chạm vào cảm biến để xác nhận thu gom rác!")
print("=" * 45)

def on_touch():
    ts = datetime.now().strftime("%H:%M:%S - %d/%m/%Y")
    print(f">>> [ĐÃ THU GOM RÁC] Thời gian ghi nhận: {ts}")

touch.when_pressed = on_touch

try:
    pause()
except KeyboardInterrupt:
    print("\nĐã dừng kiểm thử WH-139.")
