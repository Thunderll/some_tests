# coding: utf-8

import requests
import os
import time


HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}

def download_file(url, path):
    with requests.get(url, headers=HEADERS, stream=True) as req:
        chunk_size = 1024 * 10
        content_size = int(req.headers['content-length'])
        print('开始下载')
        with open(path, 'wb') as f:
            p = ProgressData(size=content_size, unit='Kb', block=chunk_size, filename=path)
            for chunk in req.iter_content(chunk_size=chunk_size):
                f.write(chunk)
                f.flush()
                os.fsync(f.fileno())
                p.output()

class ProgressData:
    def __init__(self, block, size, unit, filename=''):
        self.block = block / 1024
        self.size = size / 1024
        self.unit = unit
        self.filename = filename
        self.count = 0
        self.start = time.time()

    def output(self):
        self.end = time.time()
        self.count += 1
        burning_time = self.end - self.start
        speed = self.block / burning_time if burning_time > 0 else 0
        loaded = self.count * self.block
        progress = round(loaded / self.size, 4)
        if loaded >= self.size:
            print('\n下载完成')
        else:
            bar = '|'+'=' * int(40*progress) + ' '*(40-int(40*progress)) + '|'
            print(('\r{0} ({1:.1f}{2}) {3:.2%}'+bar+'{4}{5} 速度:{6:4.2f}{7}/s').\
                  format(self.filename, self.size, self.unit, progress, loaded, self.unit, speed, self.unit),
                  end='')
        self.start = time.time()


if __name__ == '__main__':
    url = 'http://v11-tt.ixigua.com/3215feec567fcdc10df072130ede6485/5a575256/video/m/2208e380f7c24764de2b6d316b90fc72b411152e7af0000fed0cc25e23a/'
    path = './video.mp4'
    download_file(url, path)
