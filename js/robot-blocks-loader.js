const config = require('../robotsrc/blockly.config');

window.blocklyHeader = config.header;
window.blocklyFooter = config.footer;
window.blocklyRobotToolbox = '';

function isArray(val) {
    return Array.isArray(val);
}

function isObject(val) {
    if (val === null) { return false;}
    return ( (typeof val === 'function') || (typeof val === 'object') );
}

function getField(type, initial) {
    switch(type) {
        case 'number':
            return new Blockly.FieldNumber(initial);
        case 'boolean':
            return new Blockly.FieldCheckbox(initial);
        case 'angle':
            return new Blockly.FieldAngle(initial);
        case 'text':
            return new Blockly.FieldTextInput(initial);
        default:
            console.error("Unknown field type: " + type);
            return new Blockly.FieldTextInput(initial);
    }
}

for(let block of config.blocks) {
    window.blocklyRobotToolbox += `<block type="${block.id}"></block>`;

    Blockly.Blocks[block.id] = {
        init: function() {
            let dummy = this.appendDummyInput();

            function addText(text) {
                dummy.appendField(text);
            }

            if(isArray(block.definition)) {
                for(let field of block.definition) {
                    if(isObject(field)) {
                        dummy.appendField(getField(field.type, field.initial), field.name);
                    } else {
                        addText(field);
                    }
                }
            } else {
                addText(block.definition);
            }

            this.setInputsInline(true);
            this.setPreviousStatement(true, null);
            this.setNextStatement(true, null);
            this.setColour(65);
            this.setTooltip("");
            this.setHelpUrl("");
        }
    };

    let fields = [];
    if(isArray(block.definition)) {
        for(let field of block.definition) {
            if(isObject(field)) {
                fields.push(field.name);
            }
        }
    }

    Blockly.Python[block.id] = function(item) {
        let inputs = {};
        for(let field of fields) {
            inputs[field] = item.getFieldValue(field);
        }
        return block.generator(inputs) + "\n";
    };
}
