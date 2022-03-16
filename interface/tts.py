import os
import time
import pyttsx3

class tts:
    def __init__(self):
        pass

    def sound(self, words='哈哈哈'):
							engine = pyttsx3.init() # 创建对象
							rate = engine.getProperty('rate')   # 获取当前语速（默认值）
							#print (rate)                        # 打印当前语速（默认值）
							engine.setProperty('rate', 135)     # 设置一个新的语速
							volume = engine.getProperty('volume')   # 获取当前的音量 （默认值）(min=0 and max=1)
							#print (volume)                          # 打印当前音量（默认值）
							engine.setProperty('volume',1.0)    # 设置一个新的音量（0 < volume < 1）
							voices = engine.getProperty('voices')       # 获取当前的音色信息
							engine.setProperty('voice', voices[0].id)  # 改变中括号中的值,0为男性,1为女性
							engine.setProperty('voice','zh')             #将音色中修改音色的语句替换
							engine.say(words)     
							engine.runAndWait()


if __name__ == '__main__':
	vo = tts()
	vo.sound('我是河浩林')
	
