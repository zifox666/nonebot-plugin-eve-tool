const WebSocket = require('ws');
const redisClient = require('./redis');
const agent = require("./proxy");

let remoteWs;
const reconnectInterval = 5000; // 5秒重连间隔
const messageCheckInterval = 60000; // 每60秒检查一次
const messageTimeoutDuration = 2 * 60 * 1000; // 2分钟消息超时时间
let lastMessageTime;
let messageCheckIntervalId;

const KILLMAIL_QUEUE = 'global_killmail_queue';
const MAX_QUEUE_LENGTH = 200; // 设置 Redis 队列的最大长度

function connectRemoteWs() {
    console.log('正在连接到 zkillboard WebSocket...');
    remoteWs = new WebSocket('wss://zkillboard.com/websocket/', { agent });

    remoteWs.on('open', () => {
        console.log('已连接到 zkillboard WebSocket');
        lastMessageTime = Date.now();

        const channels = ["killstream", "public"];
        channels.forEach(channel => {
            const message = JSON.stringify({
                action: "sub",
                channel: channel
            });
            remoteWs.send(message);
        });

        startMessageCheck();
    });

    remoteWs.on('message', async (data) => {
        const parsedData = JSON.parse(data);
        lastMessageTime = Date.now();

        if (parsedData.killmail_id) {
            console.log('killmail_id:', parsedData.killmail_id);
            try {
                // 推送数据到 KILLMAIL_QUEUE
                await redisClient.lPush(KILLMAIL_QUEUE, JSON.stringify(parsedData));
                // 修剪队列长度，保留最新的 MAX_QUEUE_LENGTH 条记录
                await redisClient.lTrim(KILLMAIL_QUEUE, 0, MAX_QUEUE_LENGTH - 1);
            } catch (err) {
                console.error('Failed to push killmail to global queue:', err);
            }
        }
    });

    remoteWs.on('close', () => {
        console.log('与 zkillboard WebSocket 连接已断开，正在重连...');
        stopMessageCheck();
        setTimeout(connectRemoteWs, reconnectInterval);
    });

    remoteWs.on('error', (error) => {
        console.error('zkillboard WebSocket 错误:', error);
        if (remoteWs.readyState !== WebSocket.CLOSED) {
            remoteWs.close();
        }
    });
}

function startMessageCheck() {
    stopMessageCheck(); // 确保没有重复的检查器
    messageCheckIntervalId = setInterval(() => {
        if (Date.now() - lastMessageTime > messageTimeoutDuration) {
            console.log('2分钟内未收到任何消息，断开并重新连接...');
            if (remoteWs.readyState !== WebSocket.CLOSED) {
                remoteWs.close();
            }
        }
    }, messageCheckInterval);
}

function stopMessageCheck() {
    if (messageCheckIntervalId) {
        clearInterval(messageCheckIntervalId);
        messageCheckIntervalId = null;
    }
}

module.exports = { connectRemoteWs };
