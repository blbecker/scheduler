// logger.js

import pino from 'pino';

const log = pino({
    level: process.env.LOG_LEVEL || 'debug',
    // transport: {
    //     target: 'pino-pretty'
    // },
})

export default  log