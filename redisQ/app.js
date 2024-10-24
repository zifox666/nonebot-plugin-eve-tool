const Fastify = require('fastify');
const redisClient = require('./redis');
const { connectRemoteWs } = require('./websocket');
const killmailRoutes = require('./routes/killmail');

const fastify = Fastify({
    logger: false,
    http2: false
});

// 注册路由
fastify.register(killmailRoutes);

// 连接 Redis 和 WebSocket
(async () => {
    try {
        await redisClient.connect();
        console.log('Connected to Redis');
        connectRemoteWs(); // 连接到 WebSocket
    } catch (err) {
        console.error('Initialization Error', err);
        process.exit(1);
    }
})();

// 启动服务器
fastify.listen({ port: 18920, host: '0.0.0.0' }, (err, address) => {
    if (err) {
        fastify.log.error(err);
        process.exit(1);
    }
    console.log(`Fastify server is running at ${address}`);
});
