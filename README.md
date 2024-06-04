# Homomorphic-encryption
Homomorphic encryption through BFV and CKKS.

BFV是一种支持全同态加密的同态加密方案，支持整数计算。

CKKS也是一种支持全同态加密的同态加密方案，支持浮点数计算，但在同态乘法上相对较弱，只支持有限次乘法的运算。

对于计算效率，由于CKKS方案只实现了有限的乘法同态，而BFV是无限制乘法同态的全同态，所以认为CKKS方案计算效率会高于BFV。

选择使用serialize函数将向量对象转换为二进制流，存为txt文件。可以同样以二进制流的方式读取文件，再使用ts.lazy_bfv_vector_from函数将二进制流转换为bfv（或ckks）加密向量。需要注意的是，context参数每次生成的密钥不一样，所以context和图片加密向量一样需要存储和读取，分别用serialize和context_from函数实现。从二进制流文件恢复图片加密向量时需要读取的context作为参数。文件夹中的图片都是较大的。实际上为了方便使用，在代码中设置了一个函数resize_image来将任意形状大小的图片规整成64×64。在读取图片规整形状时，用“RGBA”的模式读取，可以最大程度保留原图像png的信息。

在浮点数运算的CKKS方案中，可以通过内积算得加密向量夹角的余弦值，将之视作匹配度，通过匹配度判断明文是否一致。若两张图片一样，则所得的匹配度应该趋近100%，设阈值为99.999%，即认为匹配度大于99.999%时两图相同。这样可以得知任意两张图片的匹配度，这样只用解密三个内积值出来，也能避免解密向量导致的泄露数据，同时也能实现图片查询。要查询一张图片是否在一个图片库中，则将该图像加密，得到一个加密向量，求它和各个图片的加密向量的匹配度，若有满足匹配度趋近100%的图片即为匹配图片。

但在BFV方案中并不适用，因为BFV方案的计算会取模，内积运算的结果不再能表示长度。可以通过直接点乘两个加密向量得到新向量，解密新向量出来自行累加求得真实内积值。但这样就解密了加密向量，暴露的数据量较大，可能导致图片库的数据泄露，被攻击者获取，因此没有这么做。
