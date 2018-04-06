const INPUT_DISTANCE = "distance";
const INPUT_ANGLE = "angle";

const pinguBotConfig = {
    header: "from nicerobot import *\nimport time\n",
    footer: "",
    copyFiles: [ 'nicerobot.py' ],
    blocks: [
        {
            id: "robot_move",
            definition: ['Move', {name: INPUT_DISTANCE, type: 'number', initial: 1}, 'metre(s)'],
            generator: inputs => `move(${inputs[INPUT_DISTANCE]})`
        },
        {
            id: "robot_turn",
            definition: ['Turn', {name: INPUT_ANGLE, type: 'angle', initial: 90}],
            generator: inputs => `turn(${inputs[INPUT_ANGLE]})`
        },
        {
            id: "robot_pickup",
            definition: "Pickup cube",
            generator: () => `pickup_cube()`
        },
        {
            id: "robot_drop",
            definition: "Drop cube",
            generator: () => `drop()`
        },
        {
            id: "robot_find_go_cube",
            definition: "Find and go to a cube",
            generator: () => `find_cube()`
        },
        {
            id: "robot_find_go_bucket",
            definition: "Find and go to the bucket",
            generator: () => `find_bucket()`
        }
    ]
};

const testBotConfig = {
    header: "from testbot import *\n",
    footer: "",
    copyFiles: [ 'testbot.py' ],
    blocks: [
        {
            id: "robot_move",
            definition: ['Move', {name: INPUT_DISTANCE, type: 'number', initial: 1}, 'metres(s)'],
            generator: inputs => `move(${inputs[INPUT_DISTANCE]})`
        },
        {
            id: "robot_turn",
            definition: ['Turn', {name: INPUT_ANGLE, type: 'angle', initial: 90}],
            generator: inputs => `turn(${inputs[INPUT_ANGLE]})`
        }
    ]
};

const pacbotConfig = testBotConfig;
pacbotConfig.header = "from pacbot import *\n";
pacbotConfig.copyFiles = [ "pacbot.py" ];

module.exports = pinguBotConfig;