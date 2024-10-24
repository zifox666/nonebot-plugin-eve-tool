const redisClient = require('../redis');

const KILLMAIL_QUEUE = 'global_killmail_queue';
const CLIENT_EXPIRATION = 1 * 60 * 60; // 1小时
const MAX_SENT_RECORDS = 200; // 每个客户端最多保留1000条已发送记录

async function killmailRoute(fastify, options) {
    fastify.get('/killmail', async (request, reply) => {
        const clientId = request.query.client_id;
        if (!clientId) {
            return reply.status(400).send({ error: 'client_id is required' });
        }

        const clientSentKey = `client_sent:${clientId}`;
        const killmailList = await redisClient.lRange(KILLMAIL_QUEUE, 0, -1);
        const sentRecords = await redisClient.hGetAll(clientSentKey);

        let unsentKillmails = killmailList;
        if (sentRecords) {
            unsentKillmails = killmailList.filter(killmail => {
                const killmailData = JSON.parse(killmail);
                return !sentRecords[killmailData.killmail_id];
            });
        }

        if (unsentKillmails.length === 0) {
            return reply.send({ package: null });
        }

        const nextKillmail = unsentKillmails[0];
        const killmailData = JSON.parse(nextKillmail);
        const killmailId = killmailData.killmail_id.toString();

        try {
            await redisClient.hSet(clientSentKey, killmailId, "true");
        } catch (err) {
            console.error('Failed to update client sent records:', err);
        }

        reply.send({ package: killmailData });
        console.info(`Send ${killmailId} to ${clientId}`);
    });
}

module.exports = killmailRoute;
