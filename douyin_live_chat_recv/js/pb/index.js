let { createServer } = require('net');
let { parseResponse, parseMessage } = require('./parse.js');

function createHeader(data) {
    let n = data.length;
    let a = n < 0x7fffffff ? [0, 0, 0, 0] : [0xff, 0xff, 0xff, 0xff, 0, 0, 0, 0, 0, 0, 0, 0];
    let i = a.length;
    while ( n > 0 ) {
        a[--i] = n & 0xff;
        n >>= 8;
    }
    return Buffer.from(a);
}

function buf2int(b) {
    let s = 0n;
    for (let c of b)
        s = (s << 8n) + BigInt(c);
    return s;
}

function processMultipartData(process) {
    let bigdata = false;
    let lastover = true;
    let datasize = 0n;
    let takesize = 0n;
    let collection = [];

    return data => {
        if ( lastover ) {
            if ( bigdata) {
                if ( data.length !== 8 )
                    throw new Error("Invalid pack size");
                lastover = false;
                datasize = buf2int(data);
            } else if ( data.length === 4 ) {
                if ( data.every(v => v === 0xff) ) {
                    bigdata = true;
                } else {
                    lastover = false;
                    datasize = buf2int(data);
                }
            } else {
                datasize = buf2int(data.slice(0, 4));
                takesize = BigInt(data.length-4);
                if ( datasize === takesize ) {
                    process(data.slice(4));
                    datasize = 0n;
                    takesize = 0n;
                } else if ( datasize > takesize ) {
                    lastover = false;
                    collection.push(data.slice(4));
                } else
                    throw new Error("Invalid pack size");
            }
        } else {
            takesize += BigInt(data.length);
            collection.push(data);
            if ( datasize === takesize ) {
                data = Buffer.concat(collection);
                process(data);
                bigdata = false;
                lastover = true;
                datasize = 0n;
                takesize = 0n;
                collection = [];
            } else if ( datasize < takesize ) {
                throw new Error("Invalid pack size");
            }
        }
    }
}

// TODO: 后续需要 gzip 压缩
function parseResponseServer(address) {
    if ( address === undefined ) {
        if ( process.platform === 'win32' )
            address = "\\\\.\\pipe\\douyin-chat.pipe"
        else
            address = "douyin-chat.sock"
    }
    const server = createServer(function(socket) {
        socket.on('data', processMultipartData(data => {
            let result;
            try {
                result = parseResponse(data);
            } catch(e) {
                result = {error: true, stack: e.stack, exception: e.toString()};
            }
            const ret = Buffer.from(JSON.stringify(result));
            socket.write(createHeader(ret));
            socket.write(ret);
        }));
    });
    server.listen(address);
    return server;
}

function parseMessageServer(address) {
    if ( address === undefined ) {
        if ( process.platform === 'win32' )
            address = "\\\\.\\pipe\\douyin-chat.pipe"
        else
            address = "douyin-chat.sock"
    }
    const server = createServer(function(socket) {
        socket.on('data', processMultipartData(data => {
            let result;
            try {
                const sepIndex = data.indexOf(0x7c);
                const event = data.slice(0, sepIndex).toString();
                const payload = data.slice(sepIndex + 1);
                result = parseMessage(event, payload);
            } catch(e) {
                result = {error: true, stack: e.stack, exception: e.toString()};
            }
            const ret = Buffer.from(JSON.stringify(result));
            socket.write(createHeader(ret));
            socket.write(ret);
        }));
    });
    server.listen(address);
    return server;
}

module.exports = { parseResponseServer, parseMessageServer };
