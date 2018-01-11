# coding: utf-8

import requests
import os
import time
import threading


HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}

def download_file(url, path):
    global chunk_count  # 声明全局变量，以便在线程间传递
    chunk_count = 0
    with requests.get(url, headers=HEADERS, stream=True) as req:
        chunk_size = 1024 * 10
        content_size = int(req.headers['content-length'])
        print('开始下载')
        p = ProgressData(size=content_size, unit='Kb', block=chunk_size,
                 filename=path)
        # 将进度条的打印放到线程中
        t = threading.Thread(target=p.output, name='progress_bar')
        with open(path, 'wb') as f:
            t.start()   # 线程启动
            for chunk in req.iter_content(chunk_size=chunk_size):
                chunk_count += 1
                f.write(chunk)
                f.flush()
                os.fsync(f.fileno())
                


class ProgressData:
    def __init__(self, block, size, unit, filename=''):
        self.block = block / 1024
        self.size = size / 1024
        self.unit = unit    
        self.filename = filename
        self.start = time.time()
        self._previous = 0  # 记录上次的数据大小，用于计算瞬时网速

    def output(self):
        while True:
            self.end = time.time()
            burning_time = self.end - self.start
            loaded = chunk_count * self.block
            speed = (loaded-self._previous) / burning_time if burning_time > 0 else 0
            self._previous = loaded
            progress = round(loaded / self.size, 4)
            if loaded >= self.size:
                print('\n下载完成')
                break
            else:
                bar = '|'+'=' * int(40*progress) + ' '*(40-int(40*progress)) + '|'
                print(('\r{0} ({1:.1f}{2}) {3:3.2%}'+bar+'{4}{5} 速度:{6:4.2f}{7}/s')\
                      .format(self.filename, self.size, self.unit, progress, loaded,\
                              self.unit, speed, self.unit),
                      end='')
            self.start = time.time()
            time.sleep(0.5)


def main():
    url = 'http://v11-tt.ixigua.com/d9b88ca165aa60c6695509c6bbf2ee8a/5a579610/video/m/22020c38f4b307943d2bb97aac38a6448911153029200005eb3618bb4a2/'
    path = './video.mp4'
    download_file(url, path)


if __name__ == '__main__':
    main()
