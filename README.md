<h1 align='center'>Codeforces 命令行小工具</h1>

![](https://img.shields.io/badge/status-updating-green)

**本项目在疯狂迭代与测试中**   
配合 cf 全题目页面，实现无需点击浏览器完成操作，使用更香哦（比如进入的比赛为 https://codeforces.com/contest/666，那么全题目页面仅需要在网址后加上 `/problems`）  

## 配置方法

1.进入本目录内运行 `pip install -e .`  
  
2.修改 `info.json` 内的 `username` 和 `password`  （想多次更换账号的同学每次更换时需要将本目录下的 `cookie.pkl` 删掉
  
然后就可以使用了  

> 运行的时候可能会出现 `werkzeug` 的路径识别问题，只需要进入它报错的文件里面添加一句 `from werkzeug.utils import cached_property` 即可  
> 别的了话就最多是缺一些包，用 `pip` 手动安装即可  

## 使用方法
  
### 交题测题

- 可手动添加删除样例
- 可自动拉取 cf 对应题目样例
- 可手动拉取 cf 对应比赛所有题目的所有样例
- 可一次测试解题文件夹下所有样例
- 可一次测试解题文件夹下的单个样例
- 交题测题文件语种暂时只支持 `.cpp`、`.java`、`.py`

在任意一个文件夹下面编写一个解 CF 题目的文件（这里假设为 `hello.cpp`，解 CF1843A）    

那么我们写好后就执行命令   
`acforces hello.cpp 1843 A t`  
进行测试   

![20230626202922](https://raw.githubusercontent.com/Tequila-Avage/PicGoBeds/master/20230626202922.png)
  
测试完毕后想要交题就执行  
`acforces hello.cpp 1843 A s`
进行交题  

![20230626203131](https://raw.githubusercontent.com/Tequila-Avage/PicGoBeds/master/20230626203131.png)

![20230626203036](https://raw.githubusercontent.com/Tequila-Avage/PicGoBeds/master/20230626203036.png)
  
其中测试命令会在本目录下根据题目的样例生成一个 `1843/A/sample1.in` 和 `1843/A/sample1.out`  
对于子目录 `1843/A/` 下面的样例也可以手动添加，但注意要输入输出同名，比如 `1843/A/0.in` 与 `1843/A/0.out`   
默认测试会测试 1843/A/ 下的所有样例，当然也可以手动决定测试哪一项： `acforces hello.cpp 1843 A t 0`  

> 在工作目录下如果没有存在测试题目的样例会进行拉取一次，如果有的话直接测试
> 如果想要省去第一次测试登录的时间，可使用 `race 1843` 拉取比赛号为 1843 下的所有题目的所有样例

### 展示区

- 支持比赛首页每道题过题人数展示
- 支持比赛好友榜单区展示
- 支持自己提交列表的展示
- 支持通过编号输出自己对应提交代码

**首页过题人数展示**（其中绿色的是自己过了的题）  
`acforces p 1843`
![20230626203332](https://raw.githubusercontent.com/Tequila-Avage/PicGoBeds/master/20230626203332.png)

**比赛好友区榜单展示**（其中绿色的是自己）
`acforces r 1843`  
![82c030efa6a3601d14697174ecbc71da_0](https://raw.githubusercontent.com/Tequila-Avage/PicGoBeds/master/82c030efa6a3601d14697174ecbc71da_0.png)
  
**自己的提交列表展示**（其中绿色的是自己的 AC 提交）  
![20230626204052](https://raw.githubusercontent.com/Tequila-Avage/PicGoBeds/master/20230626204052.png)  

可以通过上面显示的编号来显示对应的提交代码  
**通过编号输出自己对应提交代码**  
![c8a1b85c13fb26c65a2598af70bb618e_0](https://raw.githubusercontent.com/Tequila-Avage/PicGoBeds/master/c8a1b85c13fb26c65a2598af70bb618e_0.png)