Blockly.Python['robot_move'] = function(block) {
  var number_distance = block.getFieldValue('DISTANCE');
  var code = 'move(' + number_distance + ')\n';
  return code;
};

Blockly.Python['robot_turn'] = function(block) {
  var number_angle = block.getFieldValue('ANGLE');
  var code = 'turn(' + number_angle + ')\n';
  return code;
};

Blockly.Python['robot_pickup'] = function(block) {
  var code = 'pickup_cube()\n';
  return code;
};

Blockly.Python['robot_drop'] = function(block) {
  var code = 'drop()\n';
  return code;
};

Blockly.Python['robot_find_go_cube'] = function(block) {
  var code = 'find_cube()\n';
  return code;
};

Blockly.Python['robot_find_go_bucket'] = function(block) {
  var code = 'find_bucket()\n';
  return code;
};