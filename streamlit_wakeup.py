import os
import sys
from playwright.sync_api import sync_playwright

# 优先读取环境变量中的 URL，未设置则使用默认链接
APP_URL = os.getenv("STREAMLIT_APP_URL", "https://yesgoo.streamlit.app/")

def run():
    print(f"正在启动浏览器，目标地址: {APP_URL}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        try:
            # 访问应用
            page.goto(APP_URL, timeout=60000, wait_until="domcontentloaded")
            page.wait_for_timeout(5000)
            
            # 定位复活按钮 (支持匹配多种常见唤醒文本)
            wake_button = page.locator('button:has-text("Yes, get this app back up!"), button:has-text("Wake app")')
            
            if wake_button.is_visible(timeout=5000):
                print("检测到应用处于休眠状态，正在点击唤醒按钮...")
                wake_button.click()
                print("已点击唤醒按钮，等待应用拉起...")
                page.wait_for_timeout(15000)
                print("唤醒指令发送成功！")
            else:
                print("应用正常在线运行中，无需唤醒。")

        except Exception as e:
            print(f"执行过程中出现异常: {e}", file=sys.stderr)
            sys.exit(1)
        finally:
            browser.close()

if __name__ == "__main__":
    run()