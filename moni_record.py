# -*- coding: utf-8 -*-
import pyaudio
import wave
import numpy as np

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1    #WebRTC VAD only accepts 16-bit mono PCM audio,py_sdkXF需要单通道才能识别
RATE = 16000
RECORD_SECONDS = 1
class AudioRecorder:
    def __init__(self,flag):
        self.audio = pyaudio.PyAudio()
        self.flag = flag

    def start(self):
        self.stream = self.audio.open(format=FORMAT,
                                    channels=CHANNELS,
                                    rate=RATE,
                                    input=True,
                                    frames_per_buffer=CHUNK)
        self.frames = []
        print("开始缓存录音")

    def monitor(self):
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = self.stream.read(CHUNK)
            self.frames.append(data)
        audio_data = np.fromstring(data, dtype=np.short)
        large_sample_count = np.sum(audio_data > 800)
        temp = np.max(audio_data)  # 使用最大因音量来控制?
        return (temp)

    def record(self,temp):
        global flag_initial
        flag_initial = [x for x in range(1, 20)]

        if temp > 800:
            print("检测到信号，当前阈值", temp)
            print("开始录音")
            for i in range(0, int(RATE / CHUNK * RECORD_SECONDS * 30)):
                data = self.stream.read(CHUNK)
                self.frames.append(data)
            self.flag = flag_initial
            return (self.frames, self.flag)

        else:
            print("信号弱")
            if len(self.flag) > 0:
                print("flag length=",len(self.flag))
                self.flag.pop()
                self.frames = []
            return(self.frames, self.flag)

    def stop(self):
        self.stream.stop_stream()
        self.stream.close()
        # p.terminate()     #注释掉，使循环继续
        print("结束录音")

    def __del__(self):
        self.audio.terminate()

    def write_audio_to_wave(self,outWaveFile):
        wf = wave.open(outWaveFile, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(self.audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()


if __name__ == '__main__':
    flag = [x for x in range(1, 20)]
    rec = AudioRecorder(flag)
    while True:

        rec.start()
        tmp = rec.monitor()
        (frames, flag) = rec.record(tmp)
        if frames != [] and len(flag) > 0:
            rec.stop()
            rec.write_audio_to_wave("test.wav")
        elif frames == [] and len(flag) == 0:
            break


