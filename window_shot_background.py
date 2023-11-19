from cv2 import cvtColor, COLOR_RGB2BGR, imshow, waitKey
from numpy import asarray

from win32.win32gui import (
    FindWindow,
    FindWindowEx,
    GetWindowRect,
    GetWindowDC,
    DeleteObject,
    ReleaseDC,
)
from win32ui import CreateDCFromHandle, CreateBitmap
from win32con import SRCCOPY
from PIL import Image
from aircv import imread, find_template


def PIL2cv(image: Image.Image):
    return cvtColor(asarray(image), COLOR_RGB2BGR)


def window_shot(Window_handle: int, width: int, height: int):
    # 返回句柄窗口的设备环境，覆盖整个窗口，包过非工作区： 标题、菜单、边框
    hWndDC = GetWindowDC(Window_handle)
    # 创建设备描述表
    mfcDC = CreateDCFromHandle(hWndDC)
    # 创建内存设备描述表
    saveDC = mfcDC.CreateCompatibleDC()
    # 创建位图对象
    bitmap = CreateBitmap()
    # 为位图开辟空间
    bitmap.CreateCompatibleBitmap(mfcDC, width, height)
    # 保存到对象
    saveDC.SelectObject(bitmap)
    # 保存bitmap
    saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), SRCCOPY)
    # 获取位图信息
    bitmap_str = bitmap.GetBitmapBits(True)

    # 生成图像
    img_PIL = Image.frombuffer("RGB", (width, height), bitmap_str, "raw", "BGRX", 0, 1)

    # 释放内存
    DeleteObject(bitmap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    ReleaseDC(Window_handle, hWndDC)
    return PIL2cv(img_PIL)


def main():
    handle = FindWindow("PRDCMainWnd", None)
    print("父窗口ID", handle)
    handle = FindWindowEx(handle, None, "DISPLAY", None)
    print("子窗口ID", handle)
    left, top, right, bottom = GetWindowRect(handle)
    width = right - left
    height = bottom - top
    # 图像对比
    src_img = imread("png/fight.png")
    # curr_img = imread("raw/QQ_20231118212549.png")
    curr_img = window_shot(handle, width, height)
    # imshow("src", src_img)
    imshow("curr", curr_img)
    waitKey()
    position: dict[str, tuple] = find_template(curr_img, src_img, threshold=0.5)  # type: ignore
    if position:
        print(position)
        x, y = position["result"]
        print(x, y)


if __name__ == "__main__":
    main()
