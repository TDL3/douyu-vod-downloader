#!/bin/env python3
import os
import re
import argparse
import requests
import subprocess

class DouYuVODDownloader():
    def __init__(self, url, d_path="./vods",  fname="mergedfile"):
        super().__init__()
        self.url = url
        self.d_path = d_path
        self.fname = fname
        self.index = 0
        self.ffmpeg = f"ffmpeg -f concat -safe 0 -i files.txt -c copy \"{self.fname}.mp4\""

    def makedir(self):
        if self.d_path == "./vods" and not os.path.isdir(self.d_path):
            print("Default download folder dose not extists, auto created")
            os.mkdir(self.d_path)

    def download_vod(self):
        # {index:0>7} makes sure index has 7 digits
        link = re.sub(r"\d{7}\.ts", r"{index:0>7}.ts", self.url)

        while True:
            vod = requests.get(link.format(index=self.index))
            # data length in bytes
            length = vod.headers["Content-Length"]
            # convert to MiB
            length = int(length) / 1024 ** 2
            print(f"GET VOD index:{self.index} size:{length:.2f}MB")
            if vod.status_code != 200:
                print(f"No Vod to Download at index:{self.index}")
                break
            with open(f"{self.d_path}/{self.index:0>7}.ts", "wb") as fp:
                fp.write(vod.content)
            self.index += 1

    def generate_ffmpeg_file_list(self):
        # Generate FFmpeg merge file list
        with open(f"{self.d_path}/files.txt", "w") as fp:
            for x in range(0, self.index, 1):
                fp.write(fr"file '{x:0>7}.ts'" + "\n")

    def merge_vod(self, del_files=True):
        os.chdir(self.d_path)
        proc = subprocess.run(self.ffmpeg)
        if proc.returncode != 0:
            print("视频合失败")
            return -1
        if proc.returncode == 0 and del_files == True:
            files = os.listdir()
            for f in files:
                if f != f"{self.fname}.mp4":
                    os.remove(f)

    def get(self):
        self.makedir()
        self.download_vod()
        self.generate_ffmpeg_file_list()
        self.merge_vod()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='笨笨的斗鱼录播下载助手')
    parser.add_argument('--path', dest="download_path", type=str,
                        action='store', help='VOD 下载路径', default="./vods")
    parser.add_argument('--name', dest="file_name", type=str,
                        action='store', help='录播视频名字', default="mergedfile")
    parser.add_argument('url', type=str, help='斗鱼视频vod链接，任意一个即可')
    args = parser.parse_args()
    DouYuVODDownloader(args.url, d_path=args.download_path,
                       fname=args.file_name).get()
