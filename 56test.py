import time
import random
import subprocess
import os
import sys
import base64
from threading import Thread

# ================= 1. 基础工具箱 =================

def get_adb_path():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    adb_path = os.path.join(base_path, "adb.exe")
    if not os.path.exists(adb_path): return "adb"
    return f'"{adb_path}"'

ADB_EXE = get_adb_path()

class DouyinBot:
    def __init__(self, sn, name):
        self.sn = sn
        self.name = name
        self.W = 720
        self.H = 1280
        self.update_size()
        self._cmd("shell ime set com.android.adbkeyboard/.AdbIME")

    def _cmd(self, command):
        full_cmd = f'{ADB_EXE} -s {self.sn} {command}'
        return subprocess.run(full_cmd, shell=True, capture_output=True, text=True)

    def update_size(self):
        res = self._cmd("shell wm size")
        if res and res.stdout:
            try:
                val = res.stdout.split(":")[-1].strip()
                self.W, self.H = map(int, val.split("x"))
            except:
                pass

    # === 动作积木 ===

    def restart_app(self):
        print(f"[{self.name}] 🔄 重启 App...")
        self._cmd("shell am force-stop com.ss.android.ugc.aweme.lite")
        time.sleep(2)
        self._cmd("shell am start -n com.ss.android.ugc.aweme.lite/com.ss.android.ugc.aweme.splash.SplashActivity")
        time.sleep(12) 

    def click_percent(self, x_pct, y_pct):
        real_x = int(self.W * x_pct) + random.randint(-3, 3)
        real_y = int(self.H * y_pct) + random.randint(-3, 3)
        self._cmd(f"shell input tap {real_x} {real_y}")

    def swipe_random(self):
        sx = int(self.W / 2) + random.randint(-20, 20)
        sy = int(self.H * 0.8) + random.randint(-50, 50)
        ey = int(self.H * 0.2) + random.randint(-50, 50)
        dur = random.randint(700, 1200) 
        self._cmd(f"shell input swipe {sx} {sy} {sx} {ey} {dur}")

    def clear_input_safe(self):
        # 1. 点击左侧 (0.25)
        self.click_percent(0.25, 0.06)
        time.sleep(1)
        # 2. 移到末尾
        self._cmd("shell input keyevent 123")
        time.sleep(0.5)
        # 3. 分批删除
        for _ in range(3):
            self._cmd("shell input keyevent " + "67 " * 10)
            time.sleep(0.2)
        # 4. 再次激活
        self.click_percent(0.25, 0.06)
        time.sleep(1)

    def search_and_enter(self, keyword):
        print(f"[{self.name}] 🔍 搜索: {keyword}")
        self.click_percent(0.92, 0.06) # 进搜索页
        time.sleep(3)
        self.clear_input_safe() 

        print(f"[{self.name}] ⌨️ 输入关键词...")
        b64_str = base64.b64encode(keyword.encode('utf-8')).decode('utf-8')
        self._cmd(f"shell am broadcast -a ADB_INPUT_B64 --es msg '{b64_str}'")
        time.sleep(2)
        
        self.click_percent(0.92, 0.06) # 搜索按钮
        time.sleep(6) 
        
        print(f"[{self.name}] 👆 点击结果...")
        self.click_percent(0.50, 0.28) 
        time.sleep(8)

# ================= 2. 业务逻辑 (回归版) =================

def run_task_flow(sn, name):
    bot = DouyinBot(sn, name)
    
    print(f"[{name}] 🚀 任务开始！阶段一：12轮 混合双打")
    
    # === 阶段一：12轮循环 ===
    for i in range(12):
        print(f"\n[{name}] >>> 第 {i+1}/12 轮 <<<")
        try:
            # --- 步骤 A: 看广告 ---
            bot.restart_app()
            bot.search_and_enter("打卡领大奖")
            
            print(f"[{name}] [A] 唤起弹窗...")
            bot.click_percent(0.50, 0.92) 
            time.sleep(4)
            
            print(f"[{name}] [A] 看广告 (0.73)...")
            bot.click_percent(0.80, 0.73) 
            time.sleep(40)
            
            print(f"[{name}] [A] 关广告...")
            bot.click_percent(0.91, 0.05)
            time.sleep(3)

            # --- 步骤 B: 刷时长 (恢复旧坐标 + 确认弹窗) ---
            bot.restart_app()
            bot.search_and_enter("打卡领大奖")
            
            print(f"[{name}] [B] 唤起弹窗...")
            bot.click_percent(0.50, 0.92)
            time.sleep(4)
            
            # 1. 点击去观看 (使用你确认过的旧坐标)
            print(f"[{name}] [B] 点击去观看 (0.78, 0.88)...")
            bot.click_percent(0.78, 0.88)
            time.sleep(3)

            # 2. 点击温馨提示确认 (防止被弹窗挡住)
            print(f"[{name}] [B] 确认温馨提示 (0.50, 0.60)...")
            bot.click_percent(0.50, 0.60)
            time.sleep(3)
            
            # 刷 5 分钟
            print(f"[{name}] [B] 刷视频 5 分钟...")
            start_swipe = time.time()
            while (time.time() - start_swipe) < 300:
                bot.swipe_random()
                time.sleep(random.uniform(8, 15))
            
            print(f"[{name}] ✅ 第 {i+1} 轮完成！")

        except Exception as e:
            print(f"[{name}] ⚠️ 错误: {e}，跳过...")

    # === 阶段二：补齐时长 ===
    print(f"\n[{name}] 🚀 阶段二：挂机补时长 (4小时)...")
    target_time = 4 * 3600 
    start_phase2 = time.time()
    
    while (time.time() - start_phase2) < target_time:
        try:
            print(f"[{name}] 🎬 新一轮 40分钟挂机...")
            bot.restart_app()
            bot.search_and_enter("打卡领大奖")
            
            bot.click_percent(0.50, 0.92) # 唤起
            time.sleep(4)
            
            # 同样应用：旧坐标 + 确认弹窗
            bot.click_percent(0.78, 0.88)
            time.sleep(3)
            bot.click_percent(0.50, 0.60)
            time.sleep(5)
            
            # 刷 40 分钟
            cycle_start = time.time()
            while (time.time() - cycle_start) < 2400:
                bot.swipe_random()
                time.sleep(random.uniform(8, 15))
                
        except Exception as e:
            print(f"[{name}] 挂机重试: {e}")
            time.sleep(10)

    print(f"[{name}] 🎉 任务全部结束")

# ================= 3. 启动 =================

if __name__ == "__main__":
    devices = {
        # 格式："手机名称"，"序列号"
       "56号机": "AADE9X3518W02061",
    }
    
    print(f"🚀 启动中... ADB: {ADB_EXE}")
    
    # ...后面代码不用动
    
    threads = []
    for name, sn in devices.items():
        t = Thread(target=run_task_flow, args=(sn, name))
        threads.append(t)
        t.start()
        time.sleep(1)
    
    for t in threads:
        t.join()