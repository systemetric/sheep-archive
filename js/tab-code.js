import { listen } from 'vscode-ws-jsonrpc';
import {
    BaseLanguageClient, CloseAction, ErrorAction,
    createMonacoServices, createConnection
} from 'monaco-languageclient';
const ReconnectingWebSocket = require('reconnecting-websocket');
const pythonLanguage = require("./python");

let tabCode = window.tabCode = document.getElementById('tab-code');
let monacoEditor;

window.amdRequire.config({ paths: { 'vs': 'js/monaco/vs' }});
window.amdRequire(['vs/editor/editor.main'], () => {
    fetch('/mainPath').then(res => res.text()).then(mainPath => {
        monaco.languages.register({
            id: 'python',
            extensions: ['.py'],
            aliases: ['PYTHON', 'python'],
        });
        // noinspection JSCheckFunctionSignatures
        monaco.languages.setMonarchTokensProvider("python", pythonLanguage.tokens);

        let codeEditor = document.getElementById('code-editor');
        // noinspection AmdModulesDependencies
        monacoEditor = window.monacoEditor = monaco.editor.create(codeEditor, {
            model: monaco.editor.createModel('import nicerobot\n', 'python', monaco.Uri.parse(mainPath)),
            theme: 'vs-dark'
        });
        tabCode.style.display = 'none';

        window.addEventListener("resize", function() {
            monacoEditor.layout()
        });

        // create the web socket
        const url = createUrl('/languageServer');
        const webSocket = createWebSocket(url);
        // listen when the web socket is opened
        listen({
            webSocket,
            onConnection: connection => {
                // create and start the language client
                const languageClient = createLanguageClient(connection);
                const disposable = languageClient.start();
                connection.onClose(() => disposable.dispose());
            }
        });

        const services = createMonacoServices(monacoEditor);
        function createLanguageClient(connection) {
            return new BaseLanguageClient({
                name: "Python Language Client",
                clientOptions: {
                    documentSelector: ['python'],
                    errorHandler: {
                        error: () => ErrorAction.Continue,
                        closed: () => CloseAction.DoNotRestart
                    }
                },
                services,
                connectionProvider: {
                    get: (errorHandler, closeHandler) => {
                        return Promise.resolve(createConnection(connection, errorHandler, closeHandler))
                    }
                }
            })
        }

        function createUrl(path) {
            const protocol = location.protocol === 'https:' ? 'wss' : 'ws';
            return `${protocol}://${location.host}${path}`;
        }

        function createWebSocket(url) {
            const socketOptions = {
                maxReconnectionDelay: 10000,
                minReconnectionDelay: 1000,
                reconnectionDelayGrowFactor: 1.3,
                connectionTimeout: 10000,
                maxRetries: Infinity,
                debug: false
            };
            // noinspection JSUnresolvedVariable
            return new ReconnectingWebSocket(url, undefined, socketOptions);
        }
    });
});

window.saveMonaco = window.getMonacoCode = function() {
    return monacoEditor.getValue();
};

window.loadMonaco = function(text) {
    monacoEditor.setValue(text);
};