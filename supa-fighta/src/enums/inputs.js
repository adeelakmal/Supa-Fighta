class Inputs {
    static IDEL = 'idel';
    static MOVE_LEFT = 'move_left';
    static MOVE_RIGHT = 'move_right';
    static ATTACK = 'attack';
    static DASH = 'dash';
    static PARRY = 'parry';

    static isValid(input) {
        return Object.values(Inputs).includes(input);
        
    }
}
module.exports = Inputs;