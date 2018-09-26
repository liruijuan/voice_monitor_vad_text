import pyaudio
import wave
import struct
import numpy as np

import collections
import contextlib
import sys
import time
from datetime import datetime
import os
import shutil

import webrtcvad

def read_wave(path):
    with contextlib.closing(wave.open(path, 'rb')) as wf:   #创建上下文管理器，在执行过程离开with语句体时自动执行object.close()
        num_channels = wf.getnchannels()  # 通道数
        assert num_channels == 1        # assert断言，在出现错误条件时就崩溃。即如果发生异常就说明表达示为假
        sample_width = wf.getsampwidth()    # 采样位数2字节，
        assert sample_width == 2
        sample_rate = wf.getframerate() # 采样频率
        assert sample_rate in (8000, 16000, 32000)
        pcm_data = wf.readframes(wf.getnframes())   # readframes返回的是二进制数据(一大堆bytes)
        # print(type(pcm_data))
        return pcm_data, sample_rate


def write_wave(path, audio, sample_rate):
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)


class Frame(object):
    def __init__(self, bytes, timestamp, duration):     # （比特，时间戳，持续时间）
        self.bytes = bytes
        self.timestamp = timestamp
        self.duration = duration


def frame_generator(frame_duration_ms, audio, sample_rate):
    n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)     # 采样率* 时间 * 双音频 = 比特率；1毫秒(ms)=0.001秒(s)
    offset = 0
    timestamp = 0.0
    duration = (float(n) / sample_rate) / 2.0   # 即音频时长，单位：s
    while offset + n < len(audio):
        yield Frame(audio[offset:offset + n], timestamp, duration)  # yield使用生成器就不需要返回整个列表，每次都只是返回一个数据，避免了内存的限制问题。
        timestamp += duration
        offset += n


def vad_collector(sample_rate, frame_duration_ms,
                  padding_duration_ms, vad, frames):
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)   # 帧数？？
    ring_buffer = collections.deque(maxlen=num_padding_frames)      # 双队列Double-Ended Queue，适合于在两端添加和删除，类似与序列的容器。
    triggered = False

    voiced_frames = []
    for frame in frames:
        sys.stdout.write(
            '1' if vad.is_speech(frame.bytes, sample_rate) else '0')
        if not triggered:
            ring_buffer.append(frame)   # 在ring_buffer的右边(末尾)添加项目frame
            num_voiced = len([f for f in ring_buffer
                              if vad.is_speech(f.bytes, sample_rate)])
            if num_voiced > 0.9 * ring_buffer.maxlen:
                sys.stdout.write('+(%s)' % (ring_buffer[0].timestamp,))
                triggered = True
                voiced_frames.extend(ring_buffer)
                ring_buffer.clear()
        else:
            voiced_frames.append(frame)
            ring_buffer.append(frame)
            num_unvoiced = len([f for f in ring_buffer
                                if not vad.is_speech(f.bytes, sample_rate)])
            if num_unvoiced > 0.9 * ring_buffer.maxlen:
                sys.stdout.write('-(%s)' % (frame.timestamp + frame.duration))
                triggered = False
                yield b''.join([f.bytes for f in voiced_frames])
                ring_buffer.clear()
                voiced_frames = []
    if triggered:
        sys.stdout.write('-(%s)' % (frame.timestamp + frame.duration))
    sys.stdout.write('\n')
    if voiced_frames:
        yield b''.join([f.bytes for f in voiced_frames])


def main(audio_path):
    audio, sample_rate = read_wave(audio_path)
    vad = webrtcvad.Vad(int(2))
    frames = frame_generator(30, audio, sample_rate)
    frames = list(frames)
    segments = vad_collector(sample_rate, 30, 300, vad, frames)
    vad_filepath = "D:\\pycharm_project\\voice_monitor_vad_text\\audio_vad_file\\"

    for i, segment in enumerate(segments):
        dt = datetime.now()
        nowtime = dt.strftime("%Y%m%d%H%M%S%f")
        path = vad_filepath + nowtime +'-chunk-%002d.wav' % (i,)
        print(' Writing %s' % (path,))

        write_wave(path, segment, sample_rate)

if __name__ == '__main__':
    main("test.wav")