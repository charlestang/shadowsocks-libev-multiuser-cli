# shadowsocks-libev-multiuser-cli
A very simple multi-user manager of shadowsocks-libev.

## 初始化项目

### 安装 pipx

```shell
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

`pipx` 是专门管理 cli 命令的包管理器，上面的命令可以处理好 PATH 环境变量。

### 安装 pipenv

```shell
pipx install pipenv
# 安装项目的依赖
pipenv install
# 如果要修改代码的话，需要安装开发环境的依赖
pipenv install --dev
```



