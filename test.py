from DrissionPage import WebPage, ChromiumOptions

co = ChromiumOptions(read_file=False)
co.set_local_port(9222)
co.set_paths(browser_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe")
co.set_proxy("http://xxxxxxx")
co.set_proxy_auth("代理账号", "代理密码")
page = WebPage(chromium_options=co, session_or_options=False)
page.get("https://ipapi.co/json/")

input("回车结束...")
