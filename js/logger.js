let log = document.getElementById('log');

function getLog() {
    fetch('/log')
        .then(res => res.text())
        .then(res => {
            log.innerHTML = res;
            log.scrollTop = log.scrollHeight;
            setTimeout(getLog, 1000);
        });
}

getLog();