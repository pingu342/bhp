# -*- coding: utf-8 -*-

import re
import zlib
import cv2
import argparse

from scapy.all import *

def parse_options():
    parser = argparse.ArgumentParser()
    parser.add_argument('pcap_file')
    parser.add_argument('mac_addr')
    args = parser.parse_args()
    return (args.pcap_file, args.mac_addr)

pictures_directory = "pictures"
faces_directory = "faces"
pcap_file, mac_addr = parse_options()

def hexdump(src, length=16):
    result = []
    digits = 4 if isinstance(src, unicode) else 2

    for i in xrange(0, len(src), length):
        s = src[i:i+length]
        hexa = b' '.join(["%0*X" % (digits, ord(x)) for x in s])
        text = b''.join([x if 0x20 <= ord(x) < 0x7f else b'.' for x in s])
        result.append( b"%04X   %-*s   %s" % (i, length*(digits + 1), hexa, text) )

    print b'\n'.join(result)

def get_http_headers(http_payload):
    try:
        # HTTPのヘッダーを抽出
        headers_raw = http_payload[:http_payload.index("\r\n\r\n")+2]

        # ヘッダーの各要素を辞書化
        headers = dict(re.findall(r"(?P<name>.*?): (?P<value>.*?)\r\n",
            headers_raw))

    except:
        return None

    if "Content-Type" not in headers:
        return None

    return headers

def extract_image(headers, http_payload):
    image = None
    image_type = None

    content_len = 0
    if 'Content-Length' in headers:
        content_len = int(headers['Content-Length'])

    try:
        if "image" in headers['Content-Type']:

            # 画像種別と画像本体の取得
            image_type = headers['Content-Type'].split("/")[1]

            image = http_payload[http_payload.index("\r\n\r\n")+4:]

            # Content-Lengthヘッダがある場合はサイズを確認
            if content_len != 0:
                if len(image) != content_len:
                    return None, None

            # 画像が圧縮されている場合は解答
            try:
                if "Content-Encoding" in headers.keys():
                    if headers['Content-Encoding'] == "gzip":
                        image = zlib.decompress(image, 16+zlib.MAX_WBITS)
                    elif headers['Content-Encoding'] == "deflate":
                        image = zlib.decompress(image)
            except:
                pass

    except:
        return None, None

    return image, image_type

def face_detect(path, file_name):
    img = cv2.imread(path)
    cascade = cv2.CascadeClassifier("haarcascade_frontalface_alt.xml")
    rects = cascade.detectMultiScale(img, 1.3, 4,
            cv2.cv.CV_HAAR_SCALE_IMAGE, (20,20))

    if len(rects) == 0:
        return False

    rects[:, 2:] += rects[:, :2]

    # 画像中のすべての顔をハイライト
    for x1,y1,x2,y2 in rects:
        cv2.rectangle(img, (x1,y1), (x2,y2), (127,255,0), 2)

    cv2.imwrite("%s/%s-%s" % (faces_directory, pcap_file, file_name), img)

    return True

def http_assembler(pcap_file):
    carved_images = 0
    faces_detected = 0

    # type(a) = <class 'scapy.plist.PacketList'>
    a = rdpcap(pcap_file)

    # type(sessions) = <type 'dict'>
    sessions = a.sessions()

    for session in sessions:
        # session = "TCP 192.168.0.12:52488 > 183.79.249.124:80"
        # session = "TCP 192.168.0.12:52498 > 183.79.249.124:80"
        #  ...

        # if session != "TCP 183.79.249.124:80 > 192.168.0.12:52490":
        #     continue

        http_payloads = [];

        for packet in sessions[session]:

            try:

                # サーバーからのレスポンスのみを取り出す
                if packet[TCP].sport == 80:

                    # `python arper-jp.py` が出力したpcapファイルには、
                    # 下図(1)(2)両方のパケットがキャプチャされている。
                    #   サーバー <-(1)-> 中継 <-(2)-> ターゲット
                    # 
                    # つまりサーバーからターゲットへのレスポンスパケットは、
                    # (1)(2)の2箇所でキャプチャされている。
                    # そこで(2)の箇所でキャプチャされたパケットだけを取り出す。
                    #  mac_addr: パケット中継するホストのインターフェース

                    if packet[Ether].src == mac_addr:

                        # ストリームの再構築
                        payload = str(packet[TCP].payload)
                        if re.match('^HTTP/\d\.\d 200 OK\r\n', payload):
                            http_payloads.append(payload)
                        else:
                            if http_payloads[-1] is not None:
                                http_payloads[-1] += str(payload)

            except Exception as e:
                pass

        for http_payload in http_payloads:

            headers = get_http_headers(http_payload)

            # Content-Typeヘッダがない場合はcontinue
            if headers is None:
                continue

            image, image_type = extract_image(headers, http_payload)

            if image is not None and image_type is not None:

                # 画像の保存
                file_name = "%s-pic_carver_%d.%s" % (
                        pcap_file, carved_images, image_type)

                fd = open("%s/%s" % (pictures_directory, file_name), "wb")

                fd.write(image)
                fd.close()

                carved_images += 1

                # 顔検出
                try:
                    result = face_detect("%s/%s" %
                            (pictures_directory, file_name), file_name)

                    if result is True:
                        faces_detected += 1

                except:
                    pass

    return carved_images, faces_detected

carved_images, faces_detected = http_assembler(pcap_file)

print "Extracted: %d images" % carved_images
print "Detected: %d faces" % faces_detected

