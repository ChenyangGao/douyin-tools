require('./douyin-source');

function parseMessage(event, payload) {
    let method = proto.webcast.im[event];
    if (method == undefined && event.startsWith("Webcast"))
        method = proto.webcast.im[event.slice(7)];
    if (method == undefined)
        return null
    let res = method.deserializeBinary(payload);
    return res.toObject();
}

function parseResponse(payload) {
    const res = proto.webcast.im.Response.deserializeBinary(payload);
    const resObj = res.toObject();
    resObj['messagesList'] = res.getMessagesList()
        .map(msg => parseMessage(msg.getMethod(), msg.getPayload()));
    return resObj;
}

module.exports = { parseMessage, parseResponse };
