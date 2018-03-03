const path = require('path');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const ExtractTextPlugin = require('extract-text-webpack-plugin');

const commonConfig = {
    module: {},
};

const monacoEditorPath = './node_modules/monaco-editor-core/dev/vs';
const monacoConfig = Object.assign({}, commonConfig, {
    name: "monaco",
    entry: ['./js/tab-code.js', './css/main.scss'],
    output: {
        path: path.resolve(__dirname, "./js/dist"),
        filename: 'bundle-monaco.js'
    },
    module: {
        noParse: /vscode-languageserver-types/,
        rules: [
            {
                test: /\.css$/,
                loader: ExtractTextPlugin.extract(['css-loader']),
            },
            {
                test: /\.(sass|scss)$/,
                loader: ExtractTextPlugin.extract(['css-loader', 'sass-loader'])
            }
        ]
    },
    resolve: {
        extensions: ['.js'],
        alias: {
            'vs': path.resolve(__dirname, monacoEditorPath)
        }
    },
    devtool: 'source-map',
    target: 'web',
    node: {
        fs: 'empty',
        child_process: 'empty',
        net: 'empty',
        crypto: 'empty'
    },
    plugins: [
        new CopyWebpackPlugin([
            {
                from: monacoEditorPath,
                to: 'vs'
            }
        ]),
        new ExtractTextPlugin({
            filename: '../../css/[name].css',
            allChunks: true,
        })
    ]
});

const robotBlocksConfig = Object.assign({}, commonConfig, {
    name: "robot-blocks",
    entry: "./js/robot-blocks-loader.js",
    output: {
        path: path.resolve(__dirname, "./js/dist"),
        filename: "bundle-robot-blocks.js"
    },
});

module.exports = [
    monacoConfig, robotBlocksConfig
];
