const express = require('express');
const bodyParser = require('body-parser');
const fs = require('fs');
const archiver = require('archiver');
const request = require('request');
const languageServer = require('./language-server/language-server');

const app = express();

//TODO: Pretty bad for security, exposing server code, but meh (fix would probably involve having another package.json)
app.use(express.static(__dirname));
app.use(bodyParser.json());

app.get('/mainPath', (req, res) => {
  res.send(languageServer.MAIN_PATH);
});

const ROBOT_HOST = 'localhost:8080';
app.post('/upload/upload', (req, res) => {
  res.send();
});
app.post('/run/start', (req, res) => {
  res.send();
});

app.post('/run', (req, res) => {
  console.log('Received code');
  console.log(req.body.code);

  fs.writeFile('data/files/main.py', req.body.code, err => {
    if(err) throw err;
    console.log('Written code');

    let fileOutput = fs.createWriteStream('./data/code.zip');
    fileOutput.on('close', () => {
      console.log('Written archive');

      let formData = {
        uploaded_file: fs.createReadStream('./data/code.zip')
      };
      request.post({
        url: `http://${ROBOT_HOST}/upload/upload`,
        formData: formData
      }, (err) => {
        if(err) throw err;        
        console.log('Uploaded archive');

        formData = {
          zone: '0',
          mode: 'development'
        };
        request.post({
          url: `http://${ROBOT_HOST}/run/start`,
          formData: formData
        }, (err) => {
          if(err) throw err;
          console.log('Ran program');

          res.send();
        });
      });
    });

    let archive = archiver('zip');
    archive.pipe(fileOutput);
    // noinspection JSCheckFunctionSignatures
    archive.directory('data/files/', false);
    archive.on('error', err => { throw err; });
    // noinspection JSIgnoredPromiseFromCall
    archive.finalize();
  });
});

const server = app.listen(8080, () => console.log('Server listening on port 8080!'));
languageServer.init(server);