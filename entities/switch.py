import jieba
def Switch(inputstr):
    ##     功能定义
    func1=['点歌','播放','音乐','歌曲','放歌']   
    func2=['打开','点亮','开启','家具']
    ##     接收命令
    seg_str = inputstr
    flag = 0;
    str_ = ' '
    value = [flag,str_]
    key=jieba.lcut(seg_str)
    for c in func1:
        for d in key:
            if d == c:
                flag = 1
                str_= d
                value = [flag,str_]
                return  value
    for c in func2:
        for d in key:
            if d == c:
                flag = 2
                str_ = d
                value = [flag,str_]
                return value
    return value


