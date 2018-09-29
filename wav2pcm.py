import os

def wav_to_pcm(wav_file):
    #假设wav_file = "音频文件.wav"
    #wav_file.spilr(".")得到["音频文件","wav"]拿出第一个结果"音频文件"与".pcm"拼接，得到结果"音频文件.pcm"
    [dirname, filename] = os.path.split(wav_file)
    pcm_file = "%s.pcm"%("D:\\pycharm_project\\voice_monitor_vad_text\\audio_vad_file_pcm\\" + filename.split(".")[0])

    #就是此前在cmd窗口中输入命令，这里面就是让Python帮我们在cmd中执行命令
    os.system("D:/ffmpeg/bin/ffmpeg -loglevel quiet -y  -i %s  -acodec pcm_s16le -f s16le -ac 1 -ar 16000 %s" %(wav_file,pcm_file))

    return pcm_file

def play_mp3(file_name):
    os.system("D:/ffmpeg/bin/ffplay  %s"%(file_name))

NOISE_TOLERANCE = 90

def removes_silence(silence_file):
    [dirname, filename] = os.path.split(silence_file)
    silence_out = "%s.wav"%("D:\\pycharm_project\\voice_monitor_vad_text\\audio_silence\\"+ filename.split(".")[0])
    os.system("D:/ffmpeg/bin/ffmpeg -loglevel quiet -i %s -af silenceremove=0:0:0:-1:1:-40dB -ac 1 -y %s" %(silence_file, silence_out))

    return silence_out

if __name__ == '__main__':
    filename = "20180928221747.wav"
    removes_silence(filename)