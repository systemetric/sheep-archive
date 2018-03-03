let tabBlocks = document.getElementById('tab-blocks');

let blocklyArea = document.getElementById('blockly-area');
let blocklyDiv = document.getElementById('blockly-div');

let blocklyCodeArea = document.getElementById('code-area');

let blocklyRobotToolbox = document.getElementById('blockly-toolbox-robot-category');
blocklyRobotToolbox.innerHTML = window.blocklyRobotToolbox;

let blocklyWorkspace = Blockly.inject(blocklyDiv,
    {toolbox: document.getElementById('toolbox')});
let onResize = function() {
    let element = blocklyArea;
    let x = 0;
    let y = 0;
    do {
        x += element.offsetLeft;
        y += element.offsetTop;
        element = element.offsetParent;
    } while (element);
    blocklyDiv.style.left = x + 'px';
    blocklyDiv.style.top = y + 'px';
    blocklyDiv.style.width = blocklyArea.offsetWidth + 'px';
    blocklyDiv.style.height = blocklyArea.offsetHeight + 'px';
};

window.addEventListener('resize', onResize, false);
onResize();
Blockly.svgResize(blocklyWorkspace);

function getBlocklyCode(header=window.blocklyHeader, footer=window.blocklyFooter) {
    return header + Blockly.Python.workspaceToCode(blocklyWorkspace) + footer;
}

function saveBlockly() {
    let xml = Blockly.Xml.workspaceToDom(blocklyWorkspace);
    return Blockly.Xml.domToText(xml);
}

function loadBlockly(text) {
    let xml = Blockly.Xml.textToDom(text);
    Blockly.Xml.domToWorkspace(xml, blocklyWorkspace);
}

blocklyWorkspace.addChangeListener(function() {
    blocklyCodeArea.innerHTML = getBlocklyCode('', '');
    Prism.highlightElement(blocklyCodeArea, true);
});
blocklyCodeArea.innerHTML = getBlocklyCode('', '');
Prism.highlightElement(blocklyCodeArea, true);
