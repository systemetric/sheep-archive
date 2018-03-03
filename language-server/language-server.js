const ws = require("ws");
const url = require("url");
const path = require("path");
const rpc = require("vscode-ws-jsonrpc");
const server = require("vscode-ws-jsonrpc/lib/server");
const lsp = require("vscode-languageserver");

module.exports.MAIN_PATH = 'file://' + path.resolve(__dirname, 'src/main.py').substring(2).replace(/\\/g, '/');
const ROOT_PATH = path.resolve(__dirname, 'src');

function launch(socket) {
    const reader = new rpc.WebSocketMessageReader(socket);
    const writer = new rpc.WebSocketMessageWriter(socket);
    const serverPath = path.resolve(__dirname, 'env/Scripts/pyls');
    const socketConnection = server.createConnection(reader, writer, () => socket.dispose());
    const serverConnection = server.createServerProcess('PYTHON', serverPath/*, ['-vv']*/);
    server.forward(socketConnection, serverConnection, message => {
        if (rpc.isRequestMessage(message)) {
            // noinspection JSUnresolvedVariable
            if('rootPath' in message.params) {
                // noinspection JSUnresolvedVariable
                message.params.rootPath = ROOT_PATH;
                // noinspection JSUnresolvedVariable
                message.params.rootUri = 'file://' + ROOT_PATH.substring(2).replace(/\\/g, '/');
            }

            // noinspection JSUnresolvedVariable
            if (message.method === lsp.InitializeRequest.type.method) {
                // noinspection JSUnresolvedVariable
                message.params.processId = process.pid;
            }
        }
        return message;
    });
}

module.exports.init = function(server) {
    const webSocketServer = new ws.Server({
        noServer: true,
        perMessageDeflate: false
    });

    server.on('upgrade', (request, socket, head) => {
        // noinspection JSUnresolvedVariable
        const pathname = request.url ? url.parse(request.url).pathname : undefined;
        if (pathname === '/languageServer') {
            webSocketServer.handleUpgrade(request, socket, head, webSocket => {
                // noinspection JSUnusedGlobalSymbols
                const socket = {
                    send: content => webSocket.send(content, err => {
                        if (err) throw err;
                    }),
                    onMessage: callback => webSocket.on('message', callback),
                    onError: callback => webSocket.on('error', callback),
                    onClose: callback => webSocket.on('close', callback),
                    dispose: () => webSocket.close(),
                };

                if (webSocket.readyState === webSocket.OPEN) {
                    launch(socket);
                } else {
                    webSocket.on('open', () => launch(socket));
                }
            });
        }
    });
};