# git_multi_repo_updater
A tool that allows you to easily update multiple git repositories at once

可以方便的更新指定目录下的多项目及项目分支，当项目有未提交的信息时则直接跳过

## screen shot
![image](https://github.com/user-attachments/assets/9e40c37a-702b-43c7-9c52-9aa22194fd54)

## AI 核心提示词
```
# 背景
公司有很多项目使用git进行源代码管理

# 目标
使用Python脚本一键操作（编写脚本生成图形化界面程序），实现对多项目更新

# 要求
1、使用Python自带窗口界面库tk
2、界面布局：一个目录选择框、一个更新按钮、一个日志输出框
3、默认扫描目录选择框所在文件夹的一级目录即可
4、每个git项目需要遍历本地分支拉取最新代码
5、如果分支有未提交内容或者拉取存在冲突则跳过且有日志输出
6、如果当前目录已经是git项目则直接拉取不在遍历子目录
7、每个关键步骤均有日志输出，且日志开头需有时间记录精确到毫秒
8、程序需要多平台逻辑共用Windows、Linux、macOS。
```


