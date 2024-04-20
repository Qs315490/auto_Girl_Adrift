from winsound import Beep
from win32.win32gui import (
    FindWindow,
    FindWindowEx,
    SendMessage,
    GetWindowRect,
)
from win32.win32api import MAKELONG
from win32con import WM_LBUTTONDOWN, WM_LBUTTONUP, MK_LBUTTON
from aircv import imread, find_all_template
from time import sleep, strftime, localtime
from threading import Thread, Event
from typing import Callable
from window_shot_background import window_shot


handle = FindWindow("PRDCMainWnd", None)
print("父窗口ID", handle)
handle = FindWindowEx(handle, None, "DISPLAY", None)
print("子窗口ID", handle)

left, top, right, bottom = GetWindowRect(handle)
window_width = right - left
window_height = bottom - top


def log(*msg: str):
    curr_time = strftime(r"%Y-%m-%d %H:%M:%S", localtime())
    print(curr_time, *msg)


def tap(x: int | float, y: int | float):
    if type(x) == float:
        x = int(x)
    if type(y) == float:
        y = int(y)
    long_position = MAKELONG(x, y)
    SendMessage(handle, WM_LBUTTONDOWN, MK_LBUTTON, long_position)
    SendMessage(handle, WM_LBUTTONUP, MK_LBUTTON, long_position)


class WhileTap(Thread):
    def __init__(self, x: int = 0, y: int = 0, wait_time: float = 0.15):
        super(WhileTap, self).__init__(daemon=True)
        self.x = x
        self.y = y
        self.flag = False
        self.wait_time = wait_time

    def wait(self, timeout: float = 0):
        time_flag: bool = False
        if timeout == 0:
            time_flag = True
        while time_flag or timeout >= 0 and not self.flag:
            if self.flag:
                break
            sleep(0.5)
            if not time_flag and timeout >= 0:
                timeout -= 0.5
        return True

    def run(self):
        while self.wait():
            tap(self.x, self.y)
            sleep(self.wait_time)

curr_img = None


def search_image(img_name: str, max_count=1, **kwargs):
    # curr_img = window_shot(handle, window_width, window_height)
    src_img = imread(f"png/{img_name}")
    if curr_img is None:
        return []
    result: list[dict[str]] = find_all_template(curr_img, src_img, maxcnt=max_count, **kwargs)  # type: ignore
    if result == []:
        return result
    if max_count == 1:
        x, y = result[0]["result"]
        return [x, y]
    return result


def tap_action(img_name: str, x: float, y: float):
    log(f"执行动作: {img_name}")
    tap(x, y)


def img2tap(
    img_name: str,
    func: Callable[[str, float, float], None] = tap_action,
    threshold: float = 0.8,
    **kwargs,
):
    result: tuple[float, float] = search_image(img_name, threshold=threshold, **kwargs)  # type: ignore
    if result:
        x, y = result
        func(img_name, x, y)
        return True
    return False


class LoopThread(Thread):
    def __init__(self, wait_time=0.5):
        super().__init__(daemon=True)
        self.wait_time = wait_time

    def refresh(self):
        while True:
            global curr_img
            curr_img = window_shot(handle, window_width, window_height)
            sleep(self.wait_time)

    def fight(self):
        result = search_image("fight.png", threshold=0.5)
        fight_flag = True if result else False
        if thread.flag != fight_flag:
            thread.flag = fight_flag
            if fight_flag:
                log("战斗开始")
            else:
                log("战斗结束")

    def port(self, x, y):
        log("执行动作：到达港口")
        tap(x, y)
        sleep(self.wait_time * 2)
        # 是否是黑市
        result = search_image("black_marketeer.png", threshold=0.8)
        if result == []:
            result = img2tap(
                "sale_all.png", lambda _, x, y: tap_action("卖出物品", x, y), 0.6, rgb=True
            )
            if result:
                log("点击全部卖出成功")
            tap(window_width // 2, window_height // 2)
            # img2tap("backpack.png", lambda _, x, y: tap(x, y))
            return
        Beep(1000, 1000)
        # TODO 选择一个物品卖出

    def setp_2(self, x, y, tip: str, img2_name: str):
        log("执行动作:", tip)
        tap(x, y)
        sleep(self.wait_time * 2)
        img2tap(img2_name, lambda _, x, y: tap(x, y))

    def rewards(self, x, y):
        log("执行动作：领取奖励")
        tap(x, y)
        sleep(self.wait_time * 2)
        img2tap("rewards1.png", lambda _, x, y: tap(x, y), rgb=True, bgremove=True)
        sleep(self.wait_time * 2)
        img2tap("close.png", lambda _, x, y: tap(x, y))

    def capture_vole_start(self, x, y):
        log("执行动作：捕获田鼠")
        tap(x, y)
        vole_list = [f"vole{i}.png" for i in range(1, 3)]
        time_flag = 0
        while time_flag < 25:
            for vole in vole_list:
                # img2tap(vole, lambda _, x, y: tap(x, y))
                results = search_image(vole, threshold=0.58, max_count=6, rgb=True)
                if results == []:
                    continue
                for result in results:
                    x, y = result["result"]
                    tap(x, y)
            result = search_image("capture_vole_end.png", threshold=0.8, rgb=True)
            if result:
                log("捕获完成")
                return
            sleep(self.wait_time * 2)
            time_flag += 1
        log("超时: 捕获田鼠, 已自动结束")

    def run(self):
        refresh_thread = Thread(target=self.refresh, daemon=True)
        refresh_thread.start()
        while True:
            # 战斗
            self.fight()

            # 到达港口
            img2tap("port.png", lambda _, x, y: self.port(x, y), 0.8)

            img2tap("turntable.png", lambda _, x, y: tap_action("转盘", x, y))
            img2tap("talent.png", lambda _, x, y: tap_action("炼金术 技能", x, y), rgb=True)
            img2tap(
                "capture_vole_start.png",
                lambda _, x, y: self.capture_vole_start(x, y),
                0.8,
                bgremove=True,
            )
            # 看广告加速升级
            img2tap(
                "ad_update.png",
                lambda _, x, y: tap_action("看广告加速升级", x, y),
                0.7,
                bgremove=True,
            )
            # 看广告获得物品
            img2tap(
                "ad_get_item.png",
                lambda _, x, y: tap_action("看广告获得物品", x, y),
                0.7,
                bgremove=True,
            )

            img2tap(
                "watch_ad_button2.png",
                lambda _, x, y: tap_action("确认看广告", x, y),
                0.7,
                rgb=True,
            )

            # 奖励
            img2tap(
                "rewards.png",
                lambda _, x, y: self.setp_2(x, y, "领取奖励", "rewards1.png"),
                0.6,
                rgb=True,
                bgremove=True,
            )
            # 邮箱
            img2tap(
                "email.png",
                lambda _, x, y: self.setp_2(x, y, "领取邮件奖励", "email2.png"),
                0.5,
                bgremove=True,
            )
            # 上线奖励
            img2tap(
                "online_reward.png",
                lambda _, x, y: self.setp_2(x, y, "领取在线奖励", "online_reward2.png"),
                0.8,
                bgremove=True,
            )

            img2tap(
                "watch_ad_button.png",
                lambda _, x, y: tap_action("观看广告按钮", x, y),
                rgb=True,
            )

            img2tap("close2.png", lambda _, x, y: tap_action("关闭弹窗", x, y))
            img2tap("close.png", lambda _, x, y: tap_action("关闭弹窗", x, y))

            img2tap(
                "relief.png",
                lambda _, x, y: tap_action("救济品", x, y),
                0.7,
                rgb=True,
            )

            ad_list = [f"ad{i}.png" for i in range(1, 6)]
            for ad in ad_list:
                img2tap(
                    ad,
                    lambda _, x, y: tap_action(f"关闭广告: {ad}", x, y),
                    0.8,
                    rgb=True,
                )
            
            sleep(self.wait_time)


def main():
    half_width: int = int(window_width / 2)
    half_height: int = int(window_height / 2)

    global thread
    thread = WhileTap(half_width, half_height, wait_time=0.25)
    thread.start()
    loop_thread = LoopThread()
    loop_thread.start()
    try:
        while True:
            thread.join(1)
    except KeyboardInterrupt:
        log("程序退出")
        exit()

if __name__ == "__main__":
    main()
