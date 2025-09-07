const { Inputs } = require("../enums");

class PlayerState {
    constructor(x = 320, y = 180) {
        this.x = x;
        this.y = y;
        this.vleocity = 0;
        this.state = Inputs.IDEL
    }
}

module.exports = PlayerState;