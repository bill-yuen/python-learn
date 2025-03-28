import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from functools import wraps

# 防抖装饰器（避免多次触发）
def debounce(wait_time):
    """
    防抖装饰器
    @param wait_time: 等待时间（秒）
    @return: 装饰器函数
    """
    def decorator(func):
        last_called = 0
        
        @wraps(func)
        def wrapped(*args, **kwargs):
            nonlocal last_called
            current_time = time.time()
            
            if current_time - last_called >= wait_time:
                last_called = current_time
                return func(*args, **kwargs)
            return None  # 在冷却时间内返回None
            
        return wrapped
    return decorator

class MainFileHandler(FileSystemEventHandler):
    @debounce(1)  # 1秒内仅触发一次
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('main.py'):
            print("\n检测到 main.py 已修改，开始执行...")
            try:
                # 终止之前的进程（避免重复运行）
                subprocess.run(["pkill", "-f", "python3 main.py"], timeout=5)
            except subprocess.TimeoutExpired:
                print("终止旧进程超时，可能未运行")
            # 启动新进程
            result = subprocess.run(
                ["python3", "main.py"], 
                capture_output=True,
                text=True
            )
            print(f"执行结果:\n{result.stdout}")
            if result.stderr:
                print(f"错误信息:\n{result.stderr}")

if __name__ == "__main__":
    path = "."  # 监控当前目录
    event_handler = MainFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    print(f"监控已启动，正在监听 {path}/main.py 的改动...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()