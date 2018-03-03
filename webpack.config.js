const path = require('path');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const ExtractTextPlugin = require('extract-text-webpack-plugin');

const jsSrcRoot = path.resolve(__dirname, "./js");
const jsDistRoot = path.resolve(__dirname, "./js/monaco");
const monacoEditorPath = './node_modules/monaco-editor-core/dev/vs';

module.exports = {
    entry: ['./js/tab-code.js', './css/main.scss'],
    output: {
        filename: 'bundle.js',
        path: jsDistRoot
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
            'vs': path.resolve(jsSrcRoot, monacoEditorPath)
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
};