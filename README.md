简体中文 | [English](README_US.md)
```text
                                                                           .-'''-.        .-'''-.          
                                                                          '   _    \     '   _    \  .---. 
       __.....__   .----.     .----.   __.....__                        /   /` '.   \  /   /` '.   \ |   | 
   .-''         '.  \    \   /    /.-''         '.                     .   |     \  ' .   |     \  ' |   | 
  /     .-''"'-.  `. '   '. /'   //     .-''"'-.  `.                .| |   '      |  '|   '      |  '|   | 
 /     /________\   \|    |'    //     /________\   \             .' |_\    \     / / \    \     / / |   | 
 |                  ||    ||    ||                  |           .'     |`.   ` ..' /   `.   ` ..' /  |   | 
 \    .-------------''.   `'   .'\    .-------------'          '--.  .-'   '-...-'`       '-...-'`   |   | 
  \    '-.____...---. \        /  \    '-.____...---.             |  |                               |   | 
   `.             .'   \      /    `.             .'              |  |                               |   | 
     `''-...... -'      '----'       `''-...... -'                |  '.'                             '---' 
                                                                  |   /                                    
                                                                  `'-'                                     
```

<div align="center">

# nonebot-plugin-eve-tool

_✨ NoneBot EVE信息查询插件 ✨_


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/zifox666/nonebot-plugin-eve-tool" alt="license">
</a>
<a href="https://pypi.org/project/nonebot-plugin-eve-tool/">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-eve-tool.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">

</div>

这是一个基于 nonebot2 编写的EVE ONLINE信息查询插件。


## 📖 介绍

懒，具体功能：查价，kb信息，翻译，汇率，KM订阅及推送</br>
数据库将会在第一次使用的时候导入，不用管，后续可以通过指令更新SDE

## 💿 安装

<details open>
<summary>使用 nb-cli 安装 (推荐)</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-eve-tool

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-eve-tool
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-eve-tool
</details>
<details>
<summary>poetry</summary>

    poetry nonebot-plugin-eve-tool
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-eve-tool
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot-plugin-eve-tool"]

</details>

## ⚙️ 配置

在 nonebot2 项目的`.env`文件中添加下表中的必填配置

```text
eve_mysql_password='你的密码'
eve_proxy='http://127.0.0.1:7890' #国内强烈推荐

# 关键配置项 - 可选 websocket 或者 redisQ
eve_zkillboard_method='websocket'
eve_zkillboard_link='wss://zkillboard.com/websocket/'
# 在zkillboard加强cloudflare盾之后强烈建议自搭redisQ作为中转服务器
# websocket极容易被cf盾拦截
```

### redisQ配置

```bash
# 此部分没有教程，请自行领悟，不会可以选择websocket
cd ./redisQ
yarn install
# 记得更改redis地址以及proxy地址
node app.js
```

<details>
<summary>全部配置项</summary>

| 配置项 | 必填 | 默认值 |      说明       |
|:-----:|:--:|:----:|:-------------:|
| eve_mysql_host | 否  | 'localhost' |   MYSQL主机地址   |
| eve_mysql_port | 否  | 3306 |   MYSQL端口号    |
| eve_mysql_user | 否  | 'root' |   MYSQL用户名    |
| eve_mysql_password | 是  | 无 |    MYSQL密码    |
| eve_mysql_db | 否  | 'eve_tool' |   MYSQL数据库名   |
| eve_redis_url | 否  | 'redis://localhost:6379/0' |  Redis连接URL   |
| eve_proxy | 否  | None |     代理配置      |
| eve_market_preference | 否  | 'esi_cache' |    市场设置偏好     |
| eve_janice_api_key | 否  | 'G9KwKq3465588VPd6747t95Zh94q3W2E' | Janice API密钥  |
| eve_word_cut | 否  | 'jieba' |    分词工具偏好     |
| eve_history_preference | 否  | 'follow' |    历史记录偏好     |
| eve_km_speed_limit | 否  | 0 | Kill Mail速度限制 |
| eve_km_send_delay | 否  | 3 | Kill Mail发送延迟 |
| eve_kb_info_background_url | 否  | 'https://www.loliapi.com/acg/' |   KB信息背景URL   |
| eve_sde_path | 否  | data_path / 'sde' |    SDE存放位置    |
| eve_lagrange_preference | 否  | 'zh' |     语言偏好      |
| eve_zkillboard_link  | 否  | wss://zkillboard.com/websocket/ |    监听km的连接    |
|eve_zkillboard_method| 否  |websocket|    监听km方式     |
| eve_command_start | 否  | ["/", "", "！", ".", "!", "#"] |    命令起始字符     |

</details>


接下来请安装mysql和redis，推荐使用docker
```shell
docker run -itd --name mysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=123456 mysql
docker run -itd --name redis -p 6379:6379 redis/redis-stack-server:latest
```

## 🎉 使用
### 指令表
|  指令   |  权限   | 需要@ | 范围 |  说明   |
|:-----:|:-----:|:---:|:--:|:-----:|
| /help |  群员   |  否  | 全部 |   无   |
|   /更新sde    | 超级管理员 |  否  |  超级管理员  | 更新SDE |

<br>

> All [EVE related materials](https://zkillboard.com/information/legal/) are property of [CCP Games](https://www.ccpgames.com/)
