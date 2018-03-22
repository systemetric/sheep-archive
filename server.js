const express = require('express');
const bodyParser = require('body-parser');
const fs = require('fs');
const archiver = require('archiver');
const request = require('request');
const languageServer = require('./language-server/language-server');
const blocklyConfig = require('./robotsrc/blockly.config');

const app = express();

//TODO: Pretty bad for security, exposing server code, but meh (fix would probably involve having another package.json)
app.use(express.static(__dirname));
app.use(bodyParser.json());

app.get('/mainPath', (req, res) => {
  res.send(languageServer.MAIN_PATH);
});

const DEV = false;
const ROBOT_HOST = DEV ? 'localhost:8080' : 'robot.sr';
app.post('/upload/upload', (req, res) => {
  res.send();
});
app.post('/run/start', (req, res) => {
  res.send();
});
app.get('/run/output', (req, res) => {
  res.send('I\'m a log I\'m a log,\nlog log log\nlog log log');
});

app.get('/log', (req, res) => {
    request.get(`http://${ROBOT_HOST}/run/output`, (err, r) => {
      if(!err) {
        res.send(r.body);
      } else {
        res.send('ERROR!');
      }
    });
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

    for(let fileToCopy of blocklyConfig.copyFiles) {
      fs.copyFileSync('./robotsrc/' + fileToCopy, './data/files/' + fileToCopy);
    }

    let archive = archiver('zip');
    archive.pipe(fileOutput);
    // noinspection JSCheckFunctionSignatures
    archive.directory('data/files/', false);
    archive.on('error', err => { throw err; });
    // noinspection JSIgnoredPromiseFromCall
    archive.finalize();
  });
});

if(!fs.existsSync('./data')) {
  fs.mkdirSync('./data');
}
if(!fs.existsSync('./data/files')) {
  fs.mkdirSync('./data/files');
}

const server = app.listen(8080, () => console.log('Server listening on port 8080!'));
languageServer.init(server);


