import tenseal as ts
import numpy as np
from PIL import Image
import time
image_num = 6

def context():# 定义context并存为txt文件
    context = ts.context(
        ts.SCHEME_TYPE.CKKS,
        poly_modulus_degree=32768,
        coeff_mod_bit_sizes=[60, 40, 40, 60]
    )
    context.generate_galois_keys()
    context.global_scale = 2 ** 40
    cot = context.serialize(save_secret_key=True)
    with open('context.txt', 'wb') as f:
        f.write(cot)
    return context

def read_context():#读取存储的context，保证密钥的一致性
    # 读取序列化数据context.txt
    with open('context.txt', 'rb') as f:
        cot_new = f.read()
        con = ts.context_from(cot_new)
        return con

def encrypt(context):#根据context加密库中的图片，存为txt文件
    for i in range(image_num):
        v1 = resize_image(str(i) + '.png', '64_' + str(i) + '.png')
        enc_v1 = ts.ckks_vector(context, v1)
        # 序列化以方便存取数据（数据以二进制形式存储）
        buff = enc_v1.serialize()
        # 保存数据
        with open(str(i) + '.txt', 'wb') as f:
            f.write(buff)

def resize_image(input_path, output_path, target_size=(64, 64)):
    try:
        #打开图像文件
        with Image.open(input_path).convert('RGBA') as img:
            # 调整图像大小为四通道64*64，图像过大会不能计算，假设比较的都是调整大小后的图片
            resized_img = img.resize(target_size)
            #可以保存调整大小后的图像
            #resized_img.save(output_path)
            img = np.array(resized_img)
            return img.flatten()
    except Exception as e:
        print(f"出现错误: {e}")

def testimg(imgname, context):#根据context检测库中是否存在imgname.png图片
    test = resize_image(imgname + '.png', '64_' + imgname + '.png')
    enc_test = ts.ckks_vector(context, test)
    tip = -1
    for i in range(image_num):
        # 读取序列化数据
        with open(str(i) + '.txt', 'rb') as f:
            buff_new = f.read()
        # 将序列化数据转化为密文
        enc_v1 = ts.lazy_ckks_vector_from(buff_new)
        # 将密文和对应密钥绑定
        enc_v1.link_context(context)
        result = enc_v1 - enc_test
        differ = result.dot(result)
        # 比较相减结果的内积是否为0，是则匹配
        if (differ.decrypt()[0] < 0.01):
            tip = i
            break
    if(tip != -1):
        print("test-image matches:"+str(tip))
    else:
        print("no object matches test image " + imgname)

if __name__ == '__main__':
    t1 = time.time()
    #加密图片至文件库中
    context = context()
    encrypt(context)
    #查询图片在库中是否存在
    read_context = read_context()
    testimg('test1', read_context)
    testimg('test2', read_context)
    testimg('test3', read_context)
    runtime = time.time() - t1
    print(runtime)