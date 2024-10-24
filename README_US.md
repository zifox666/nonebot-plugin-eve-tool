[简体中文](README.md) | English
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

_✨ NoneBot EVE Information Query Plugin ✨_


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/zifox666/nonebot-plugin-eve-tool" alt="license">
</a>
<a href="https://pypi.org/project/nonebot-plugin-eve-tool/">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-eve-tool.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">

</div>

This is an EVE ONLINE information query plugin written based on NoneBot2.

## 📖 Introduction

Specific functions: price check, kb information, translation, exchange rate, KM subscription and push notifications.</br>
This plugin is designed for querying real-time market prices, historical market prices, 
zkillboard information, wormhole information, 
EVE-specific term translations between Chinese and English, contract valuation, and custom killmail notifications. 
The aim of this plugin is to help Chinese players who face slow access to foreign websites 
and to allow them to quickly access EVE-related information, battle occurrences in the universe, 
and EVE content anytime and anywhere via QQ, a communication software widely used in China.

## 💿 Installation

<details open>
<summary>Install using nb-cli (recommended)</summary>
Open the command line in the root directory of the NoneBot2 project and enter the following command to install

    nb plugin install nonebot-plugin-eve-tool

</details>

<details>
<summary>Install using a package manager</summary>
In the plugin directory of the NoneBot2 project, open the command line and enter the corresponding installation command according to the package manager you use

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

    poetry add nonebot-plugin-eve-tool
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-eve-tool
</details>

Open the `pyproject.toml` file in the root directory of the NoneBot2 project and add the following in the `[tool.nonebot]` section

    plugins = ["nonebot_plugin_eve_tool"]

</details>

## ⚙️ Configuration

Add the mandatory configuration items in the table below to the `.env` file in the NoneBot2 project

```text
eve_mysql_password='your_password'
eve_proxy='http://127.0.0.1:7890' #Strongly recommended in China

# Important settings
eve_zkillboard_method='websocket'
eve_zkillboard_link='wss://zkillboard.com/websocket/'
# It will blocked by cloudflare when zkillboard upgrade their servers
# python websocket will block by cloudflare
```

### redisQ setting

```bash
# You can choose websocket if you not know how to use node.js
cd ./redis
yarn install
# Please remember check proxy and redis link
node app.js
```

<details>
<summary>All configuration items</summary>

| Configuration Item | Required | Default Value | Description |
|:-----:|:----:|:----:|:----:|
| eve_mysql_host | No | 'localhost' | MYSQL host address |
| eve_mysql_port | No | 3306 | MYSQL port number |
| eve_mysql_user | No | 'root' | MYSQL username |
| eve_mysql_password | Yes | None | MYSQL password |
| eve_mysql_db | No | 'eve_tool' | MYSQL database name |
| eve_redis_url | No | 'redis://localhost:6379/0' | Redis connection URL |
| eve_proxy | No | None | Proxy configuration |
| eve_market_preference | No | 'esi_cache' | Market preference setting |
| eve_janice_api_key | No | 'G9KwKq3465588VPd6747t95Zh94q3W2E' | Janice API key |
| eve_word_cut | No | 'jieba' | Word segmentation tool preference |
| eve_history_preference | No | 'follow' | History preference |
| eve_km_speed_limit | No | 0 | Kill Mail speed limit |
| eve_km_send_delay | No | 3 | Kill Mail send delay |
| eve_kb_info_background_url | No | 'https://www.loliapi.com/acg/' | KB information background URL |
| eve_sde_path | No | data_path / 'sde' | SDE storage location |
| eve_lagrange_preference | No | 'zh' | Language preference |
| eve_command_start | No | ["/", "", "！", ".", "!", "#"] | Command start characters |
</details>

Next, please install MySQL and Redis. It is recommended to use Docker.
```shell
docker run -itd --name mysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=123456 mysql
docker run -itd --name redis -p 6379:6379 redis/redis-stack-server:latest
```

## 🎉 Usage
### Command List
| Command | Permission |   Scope    |              Description              |
|:-------:|:----------:|:----------:|:-------------------------------------:|
| /ojita  |   Member   |    All     |            Qurry jita price           |
|  /help  |   Member   |    All     |                  None                 |
|  /zkb   |   Member   |    All     |        Qurry character zkb info       |
|  /rank  |   Member   |    All     | Show a corp member rank in last 7 days |
| /trans  |   Member   |    All     |       Trans eve items to chinese      |
| /更新sde  | SuperAdmin | SuperAdmin |              Update SDE               |

<br>

> All [EVE related materials](https://zkillboard.com/information/legal/) are property of [CCP Games](https://www.ccpgames.com/)