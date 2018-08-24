# -*- coding: utf-8 -*-
import pyaudio
import wave
import numpy as np

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1 #WebRTC VAD only accepts 16-bit mono PCM audio,py_sdkXF需要单通道才能识别
RATE = 16000
RECORD_SECONDS = 3

p = pyaudio.PyAudio()

def monitor(path):
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    print("开始缓存录音")
    frames = []
    count = 0

    while (True):
        count +=1
        print("开始第" + str(count) +"次检测")

        for i in range(0, int(RATE/CHUNK*RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
        audio_data = np.fromstring(data, dtype=np.short)
        large_sample_count = np.sum( audio_data > 800 )
        temp = np.max(audio_data)   # 使用最大因音量来控制?
        if temp > 800:
            print("检测到信号")
            print('当前阈值：',temp)
            print("开始录音")
            break
        else:
            frames = []
            continue
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS*10)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("结束录音")
    stream.stop_stream()
    stream.close()
    # p.terminate()     #注释掉，使循环继续

    wf = wave.open(path, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

if __name__ == '__main__':
        monitor("test.wav")
