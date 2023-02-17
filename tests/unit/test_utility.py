from src.utility import imageUrl2Base64


def test_image_url2base64():
    url = "https://ask.qcloudimg.com/http-save/yehe-1269631/5eaa0702cc5b5433fbf2fbb4460e7f1b.png?imageView2/2/w/1620"
    imgb64_ori = imageUrl2Base64(url, True)
    imgb64_thu = imageUrl2Base64(url, False)
    assert imgb64_ori is not False
    assert imgb64_thu is not False
    # assert imgb64_ori != imgb64_thu
