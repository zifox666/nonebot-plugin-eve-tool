const { HttpsProxyAgent } = require('https-proxy-agent');

const proxy = 'http://127.0.0.1:7890';
const agent = new HttpsProxyAgent(proxy);

module.exports = agent;
