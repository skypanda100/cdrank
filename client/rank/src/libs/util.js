let util = {};

let SIGN_REGEXP = /([yMdhsm])(\1*)/g;
let DEFAULT_PATTERN = 'yyyy-MM-dd';

util.title = function (title) {
    title = title || 'rank';
    window.document.title = title;
};

util.inOf = function (arr, targetArr) {
    let res = true;
    arr.map(item => {
        if (targetArr.indexOf(item) < 0) {
            res = false;
        }
    });
    return res;
};

util.oneOf = function (ele, targetArr) {
    if (targetArr.indexOf(ele) >= 0) {
        return true;
    } else {
        return false;
    }
};

util.isNull = function (arg) {
    if (arg === undefined || arg === null) {
        return true;
    }
    return false;
};

util.floorMod = function (a, n) {
    return a - n * Math.floor(a / n);
};

util.rad2deg = function (ang) {
    return ang / (Math.PI / 180.0);
};

util.deg2rad = function (deg) {
    return deg / 180 * Math.PI;
};

util.isMobile = function () {
    return (/android|blackberry|iemobile|ipad|iphone|ipod|opera mini|webos/i.test(navigator.userAgent));
};

util.ionIcons = function (size, name, color) {
    if (this.isNull(color)) {
        return '<span style="font-size: ' + (size / 10.0) + 'rem"><i class="icon ion-' + name + '"></i></span>';
    }
    return '<span style="font-size: ' + (size / 10.0) + 'rem;color: ' + color + '"><i class="icon ion-' + name + '"></i></span>';
};

util.padding = function (s, len) {
    len = len - (s + '').length;
    for (let i = 0; i < len; i++) { s = '0' + s; }
    return s;
};

util.formatDate = function (date, pattern) {
    pattern = pattern || DEFAULT_PATTERN;
    return pattern.replace(SIGN_REGEXP, ($0) => {
        switch ($0.charAt(0)) {
            case 'y':
                return this.padding(date.getFullYear(), $0.length);
            case 'M':
                return this.padding(date.getMonth() + 1, $0.length);
            case 'd':
                return this.padding(date.getDate(), $0.length);
            case 'w':
                return date.getDay() + 1;
            case 'h':
                return this.padding(date.getHours(), $0.length);
            case 'm':
                return this.padding(date.getMinutes(), $0.length);
            case 's':
                return this.padding(date.getSeconds(), $0.length);
        }
    });
};

util.formatUTCDate = function (date, pattern) {
    pattern = pattern || DEFAULT_PATTERN;
    return pattern.replace(SIGN_REGEXP, ($0) => {
        switch ($0.charAt(0)) {
            case 'y':
                return this.padding(date.getUTCFullYear(), $0.length);
            case 'M':
                return this.padding(date.getUTCMonth() + 1, $0.length);
            case 'd':
                return this.padding(date.getUTCDate(), $0.length);
            case 'w':
                return date.getUTCDay() + 1;
            case 'h':
                return this.padding(date.getUTCHours(), $0.length);
            case 'm':
                return this.padding(date.getUTCMinutes(), $0.length);
            case 's':
                return this.padding(date.getUTCSeconds(), $0.length);
        }
    });
};

util.parseDate = function (dateString, pattern) {
    let matchs1 = pattern.match(SIGN_REGEXP);
    let matchs2 = dateString.match(/(\d)+/g);
    if (matchs1.length === matchs2.length) {
        let _date = new Date(1970, 0, 1);
        for (let i = 0; i < matchs1.length; i++) {
            let _int = parseInt(matchs2[i]);
            let sign = matchs1[i];
            switch (sign.charAt(0)) {
                case 'y':
                    _date.setFullYear(_int);
                    break;
                case 'M':
                    _date.setMonth(_int - 1);
                    break;
                case 'd':
                    _date.setDate(_int);
                    break;
                case 'h':
                    _date.setHours(_int);
                    break;
                case 'm':
                    _date.setMinutes(_int);
                    break;
                case 's':
                    _date.setSeconds(_int);
                    break;
            }
        }
        return _date;
    }
    return null;
};

util.parseUTCDate = function (dateString, pattern) {
    let matchs1 = pattern.match(SIGN_REGEXP);
    let matchs2 = dateString.match(/(\d)+/g);
    if (matchs1.length === matchs2.length) {
        let _date = new Date(1975, 1, 5); // 不能设置为1970 0 1,不然2月份的有bug
        for (let i = 0; i < matchs1.length; i++) {
            let _int = parseInt(matchs2[i], 10);
            let sign = matchs1[i];
            switch (sign.charAt(0)) {
                case 'y':
                    _date.setUTCFullYear(_int);
                    break;
                case 'M':
                    _date.setUTCMonth(_int - 1);
                    break;
                case 'd':
                    _date.setUTCDate(_int);
                    break;
                case 'h':
                    _date.setUTCHours(_int);
                    break;
                case 'm':
                    _date.setUTCMinutes(_int);
                    break;
                case 's':
                    _date.setUTCSeconds(_int);
                    break;
            }
        }
        return _date;
    }
    return null;
};

util.typeOf = function (obj) {
    let toString = Object.prototype.toString;
    let map = {
        '[object Boolean]': 'boolean',
        '[object Number]': 'number',
        '[object String]': 'string',
        '[object Function]': 'function',
        '[object Array]': 'array',
        '[object Date]': 'date',
        '[object RegExp]': 'regExp',
        '[object Undefined]': 'undefined',
        '[object Null]': 'null',
        '[object Object]': 'object'
    };
    return map[toString.call(obj)];
}

util.deepCopy = function (data) {
    let t = util.typeOf(data);
    let o = void 0;

    if (t === 'array') {
        o = [];
    } else if (t === 'object') {
        o = {};
    } else {
        return data;
    }

    if (t === 'array') {
        for (let i = 0; i < data.length; i++) {
            o.push(util.deepCopy(data[i]));
        }
    } else if (t === 'object') {
        for (let _i in data) {
            o[_i] = util.deepCopy(data[_i]);
        }
    }
    return o;
}

util.isNumber = function (data) {
    let re = /^\d+(?=\.{0,1}\d+$|$)/
    if (!re.test(data)) {
        return false;
    }
    return true;
}

export default util;
