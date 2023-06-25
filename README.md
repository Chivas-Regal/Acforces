![](https://img.shields.io/badge/status-updating-green)

<h1 align='center'>Codeforces 命令行小工具</h1>

**本项目在疯狂迭代与测试中**

使用案例（视频）：  
[![](https://img.youtube.com/vi/onIQwtgDd_M/0.jpg)](https://youtu.be/onIQwtgDd_M)

## 配置方法

1.进入本目录内运行 `pip install -e .`  
  
2.修改 `info.json` 内的 `username` 和 `password`
  
然后就可以使用了  

> 运行的时候可能会出现 `werkzeug` 的路径识别问题，只需要进入它报错的文件里面添加一句 `from werkzeug.utils import cached_property` 即可  
> 别的了话就最多是缺一些包，用 `pip` 手动安装即可  

## 使用方法

在任意一个文件夹下面编写一个解 CF 题目的文件（这里假设为 `hello.cpp`，解 CF1843A）    
  
那么我们写好后就执行命令   
`acforces hello.cpp 1843 A t`  
进行测试  
  
测试完毕后想要交题就执行  
`acforces hello.cpp 1843 A s`
进行交题  
  
其中测试命令会在本目录下根据题目的样例生成一个 `1843/A/sample1.in` 和 `1843/A/sample1.out`  
对于子目录 `1843/A/` 下面的样例也可以手动添加，但注意要输入输出同名，比如 `1843/A/0.in` 与 `1843/A/0.out`  

## 支持

- 在任意目录下测试自己的解题代码
- 手动添加样例删除样例
- 支持 `cpp`，`python`，`java` 的解题代码测试与提交
