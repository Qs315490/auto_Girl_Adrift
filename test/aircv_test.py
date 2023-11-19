from aircv import imread, find_all_template
from cv2 import imshow, waitKey, rectangle, imdecode
from numpy import fromfile, uint8

src_img = imread("png/vole1.png")
curr_img = imdecode(fromfile("raw/捕获田鼠3.png", dtype=uint8), -1)
positions = find_all_template(curr_img, src_img, threshold=0.5, rgb=True)
if positions:
    print(positions)
    for position in positions:
        (x_start, y_start), _, _, (x_end, y_end) = position["rectangle"]
        rectangle(curr_img, (x_start, y_start), (x_end, y_end), (0, 0, 255), 2)
    imshow("result", curr_img)
    waitKey()
