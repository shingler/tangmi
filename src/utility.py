import requests
import base64
from PIL import Image
from io import BytesIO


# 从url读取图片，并生成缩略图（最大不超过1080P），返回base64
# @param url string 图片url地址
# @param origin_output bool 是否原图转码base64。设置为False则会以最大分辨率1080P转码base64
# @exception url无法访问、图片格式非jpg、png都会返回False
def imageUrl2Base64(url, origin_output=False):
    # 从url下载图片到内存
    ret = requests.get(url)
    # print(url, ret.status_code)
    if ret.status_code != 200:
        return False

    # 将图片转换成Image对象做处理
    try:
        img = Image.open(BytesIO(ret.content))
        # 图片格式检查
        # print(img.format.lower())
        # img.show()
        if img.format.lower() not in ["jpeg", "png"]:
            return False
        # 非原图输出缩放成最高1080P
        if not origin_output:
            w, h = img.size
            short_side = min(w, h)
            if short_side > 1080 and w > h:
                # 宽图
                img.thumbnail((1920, 1080), Image.ANTIALIAS)
            elif short_side > 1080:
                # 长图
                img.thumbnail((1080, 1920), Image.ANTIALIAS)

        # 将图片数据读入字节缓冲区以编码base64
        # img.show()
        img_buffer = BytesIO()
        img.save(img_buffer, img.format)
        # print("save")
        bstring = base64.b64encode(img_buffer.getvalue())
        # 解码base64显示图像用于调试
        # img_dec = Image.open(BytesIO(base64.b64decode(bstring)))
        # img_dec.show()
        return bstring
    except Exception as ex:
        print("exception:")
        print(repr(ex))
        return False



