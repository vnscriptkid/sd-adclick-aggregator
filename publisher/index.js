const {Kafka, logLevel} = require('kafkajs')

const kafka = new Kafka({
    brokers: ['cool-civet-11505-us1-kafka.upstash.io:9092'],
    ssl: true,
    sasl: {
        mechanism: 'scram-sha-256',
        username: 'Y29vbC1jaXZldC0xMTUwNSTbNyM_hWBk0p3kL8MhEX_G3sCn82k8A2H1END-GFs',
        password: 'ZTM0ZTg0ZDEtNTgxNS00MGQ4LTliODctYTIwYTc4MTFjZTAw'
    },
    logLevel: logLevel.ERROR,
});

const producer = kafka.producer();

const adsIds = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
const randomAdsId = () => adsIds[Math.floor(Math.random() * adsIds.length)]
const randomInterval = (min, max) => Math.floor(Math.random() * (max - min + 1) + min) * 1000

const publish = async () => {
    const adsId = randomAdsId()
    const createdAt = new Date().toISOString()
    const message = { adsId, createdAt }
    await producer.send({
        topic: 'clicks',
        messages: [
            { value: JSON.stringify(message) },
        ],
    });
    return message
}


const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const run = async () => {
    await producer.connect();

    while (true) {
        const message = await publish()
        console.log("Message sent", message)
        waitTime = randomInterval(1, 5)
        console.log("Waiting for next publish in", waitTime, "ms")
        await sleep(waitTime)
    }


    console.log("Message sent successfully");
    await producer.disconnect();
};

run().catch(e => console.error('[example/producer] e.message', e));