let switchButton = document.getElementById('switch-button');
let buildButton = document.getElementById('build-button');

let usingBlockly = true;
switchButton.addEventListener('click', function() {
   usingBlockly = !usingBlockly;
   tabBlocks.style.display = usingBlockly ? "block" : "none";
   tabCode.style.display = usingBlockly ? "none" : "block";
   if(!usingBlockly) monacoEditor.layout();
});

let running = false;
buildButton.addEventListener('click', function() {
    if(running) return;

    running = true;
    buildButton.innerHTML = "Running...";
    buildButton.classList.add("selected");

    let code = usingBlockly ? getBlocklyCode() : getMonacoCode();

    fetch('/run', {
        body: JSON.stringify({
            code: code
        }),
        headers: { 'content-type': 'application/json' },
        method: "POST"
    }).then(() => {
        running = false;
        buildButton.innerHTML = "Run on Robot";
        buildButton.classList.remove("selected");
    });
});


