# coding:utf-8

# 遍历path路径下的*.md文件，进行如下操作
# 1. 获取对应的文件名，创建对应的文件夹
# 2. 获取文件中的图片标签，获取图片名称，将img路径下的图片名称copy到上一步的创建的文件夹中

import os,sys,time,re,shutil

IMG_NAME = 'img'
# markdown文件中图片
IMG_RE = '!\[\]\((.*)\)'

def start():
    # get file path which extension is ".md"
    path = os.getcwd()
    md_files = list_file(path)
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' 文件扫描完成，开始处理')
    for md_file in md_files:
        copy_img(md_file)
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' 处理完成')

def copy_img(file):
    '''
        创建以文件名命名的文件夹，然后拷贝文件中存在的图片到文件夹中
    '''
    
    file_name = os.path.splitext(file)[0].split(os.sep)[-1]
    path = file[0:file.rindex(os.sep)]
    img_path = os.path.join(path,IMG_NAME)
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' 开始处理文件'+file_name+'中的图片')
    imgs = extract_img(file)
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' 图片路径提取完成，开始拷贝到目的文件夹')
    # 创建目标文件夹
    if not os.path.exists(os.path.join(path,file_name)):
        os.mkdir(os.path.join(path,file_name))
    try:
        for img in imgs:
            img_name = img[img.rindex('/')+1:]
            src = os.path.join(img_path,img_name)
            des = os.path.join(path,file_name)
            if os.path.exists(src):
                shutil.copy(src,des)
    except Exception as e:
        print("文件拷贝异常，",e)
    print(imgs)



def extract_img(file):
    '''
    读取文件，然后返回文件中包含的图片
    '''
    imgs = []
    try:
        stream = open(file,'r',encoding="utf-8")
        for line in stream:
            img = re.findall(IMG_RE,line)
            if img:
                imgs.extend(img)
        return imgs
    except Exception as e:
        print("读取文件异常,",e)
    finally:
        stream.close()


  



def list_file(path):
    '''
    获取path路径下所有的以md结尾的文件
    '''
    result = []
    # func listdir returns name of files in the directory
    files = os.listdir(path)
    for file in files:
        if os.path.splitext(file)[-1] == '.md':
            result.append(os.path.join(path,file))

    return result



if __name__ == "__main__":
    start()