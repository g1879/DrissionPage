from click import command, option

from DrissionPage import ChromiumPage
from DrissionPage.easy_set import set_paths, configs_to_here as ch


@command()
@option("-p", "--set-browser-path", help="设置浏览器路径")
@option("-u", "--set-user-path", help="设置用户数据路径")
@option("-c", "--configs-to-here", is_flag=True, help="复制默认配置文件到当前路径")
@option("-l", "--launch-browser", default=-1, help="启动浏览器，传入端口号，0表示用配置文件中的值")
def main(set_browser_path, set_user_path, configs_to_here, launch_browser):
    if set_browser_path:
        set_paths(browser_path=set_browser_path)

    if set_user_path:
        set_paths(user_data_path=set_user_path)

    if configs_to_here:
        ch()

    if launch_browser >= 0:
        port = f'127.0.0.1:{launch_browser}' if launch_browser else None
        ChromiumPage(port)


if __name__ == '__main__':
    main()
