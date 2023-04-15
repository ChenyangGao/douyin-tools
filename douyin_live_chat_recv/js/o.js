// https://lf-cdn-tos.bytescm.com/obj/static/webcast/douyin_live/6654.834775e1.js
let u = function(ws, tl) {
    for (var n = [...ws], l = 8 * tl, s = 1732584193, c = -271733879, f = -1732584194, d = 271733878, p = 0; p < n.length; p++)
        n[p] = 16711935 & (n[p] << 8 | n[p] >>> 24) | 4278255360 & (n[p] << 24 | n[p] >>> 8);
        n[l >>> 5] |= 128 << l % 32,
        n[14 + (l + 64 >>> 9 << 4)] = l;
    var h = u._ff
        , v = u._gg
        , m = u._hh
        , y = u._ii;
    for (p = 0; p < n.length; p += 16) {
        var g = s
            , b = c
            , _ = f
            , w = d;
        s = h(s, c, f, d, n[p + 0], 7, -680876936),
        d = h(d, s, c, f, n[p + 1], 12, -389564586),
        f = h(f, d, s, c, n[p + 2], 17, 606105819),
        c = h(c, f, d, s, n[p + 3], 22, -1044525330),
        s = h(s, c, f, d, n[p + 4], 7, -176418897),
        d = h(d, s, c, f, n[p + 5], 12, 1200080426),
        f = h(f, d, s, c, n[p + 6], 17, -1473231341),
        c = h(c, f, d, s, n[p + 7], 22, -45705983),
        s = h(s, c, f, d, n[p + 8], 7, 1770035416),
        d = h(d, s, c, f, n[p + 9], 12, -1958414417),
        f = h(f, d, s, c, n[p + 10], 17, -42063),
        c = h(c, f, d, s, n[p + 11], 22, -1990404162),
        s = h(s, c, f, d, n[p + 12], 7, 1804603682),
        d = h(d, s, c, f, n[p + 13], 12, -40341101),
        f = h(f, d, s, c, n[p + 14], 17, -1502002290),
        s = v(s, c = h(c, f, d, s, n[p + 15], 22, 1236535329), f, d, n[p + 1], 5, -165796510),
        d = v(d, s, c, f, n[p + 6], 9, -1069501632),
        f = v(f, d, s, c, n[p + 11], 14, 643717713),
        c = v(c, f, d, s, n[p + 0], 20, -373897302),
        s = v(s, c, f, d, n[p + 5], 5, -701558691),
        d = v(d, s, c, f, n[p + 10], 9, 38016083),
        f = v(f, d, s, c, n[p + 15], 14, -660478335),
        c = v(c, f, d, s, n[p + 4], 20, -405537848),
        s = v(s, c, f, d, n[p + 9], 5, 568446438),
        d = v(d, s, c, f, n[p + 14], 9, -1019803690),
        f = v(f, d, s, c, n[p + 3], 14, -187363961),
        c = v(c, f, d, s, n[p + 8], 20, 1163531501),
        s = v(s, c, f, d, n[p + 13], 5, -1444681467),
        d = v(d, s, c, f, n[p + 2], 9, -51403784),
        f = v(f, d, s, c, n[p + 7], 14, 1735328473),
        s = m(s, c = v(c, f, d, s, n[p + 12], 20, -1926607734), f, d, n[p + 5], 4, -378558),
        d = m(d, s, c, f, n[p + 8], 11, -2022574463),
        f = m(f, d, s, c, n[p + 11], 16, 1839030562),
        c = m(c, f, d, s, n[p + 14], 23, -35309556),
        s = m(s, c, f, d, n[p + 1], 4, -1530992060),
        d = m(d, s, c, f, n[p + 4], 11, 1272893353),
        f = m(f, d, s, c, n[p + 7], 16, -155497632),
        c = m(c, f, d, s, n[p + 10], 23, -1094730640),
        s = m(s, c, f, d, n[p + 13], 4, 681279174),
        d = m(d, s, c, f, n[p + 0], 11, -358537222),
        f = m(f, d, s, c, n[p + 3], 16, -722521979),
        c = m(c, f, d, s, n[p + 6], 23, 76029189),
        s = m(s, c, f, d, n[p + 9], 4, -640364487),
        d = m(d, s, c, f, n[p + 12], 11, -421815835),
        f = m(f, d, s, c, n[p + 15], 16, 530742520),
        s = y(s, c = m(c, f, d, s, n[p + 2], 23, -995338651), f, d, n[p + 0], 6, -198630844),
        d = y(d, s, c, f, n[p + 7], 10, 1126891415),
        f = y(f, d, s, c, n[p + 14], 15, -1416354905),
        c = y(c, f, d, s, n[p + 5], 21, -57434055),
        s = y(s, c, f, d, n[p + 12], 6, 1700485571),
        d = y(d, s, c, f, n[p + 3], 10, -1894986606),
        f = y(f, d, s, c, n[p + 10], 15, -1051523),
        c = y(c, f, d, s, n[p + 1], 21, -2054922799),
        s = y(s, c, f, d, n[p + 8], 6, 1873313359),
        d = y(d, s, c, f, n[p + 15], 10, -30611744),
        f = y(f, d, s, c, n[p + 6], 15, -1560198380),
        c = y(c, f, d, s, n[p + 13], 21, 1309151649),
        s = y(s, c, f, d, n[p + 4], 6, -145523070),
        d = y(d, s, c, f, n[p + 11], 10, -1120210379),
        f = y(f, d, s, c, n[p + 2], 15, 718787259),
        c = y(c, f, d, s, n[p + 9], 21, -343485551),
        s = s + g >>> 0,
        c = c + b >>> 0,
        f = f + _ >>> 0,
        d = d + w >>> 0
    }
    return [s, c, f, d]
}
u._ff = function(e, t, n, r, i, o, a) {
    var u = e + (t & n | ~t & r) + (i >>> 0) + a;
    return (u << o | u >>> 32 - o) + t
}
u._gg = function(e, t, n, r, i, o, a) {
    var u = e + (t & r | n & ~r) + (i >>> 0) + a;
    return (u << o | u >>> 32 - o) + t
}
u._hh = function(e, t, n, r, i, o, a) {
    var u = e + (t ^ n ^ r) + (i >>> 0) + a;
    return (u << o | u >>> 32 - o) + t
}
u._ii = function(e, t, n, r, i, o, a) {
    var u = e + (n ^ (t | ~r)) + (i >>> 0) + a;
    return (u << o | u >>> 32 - o) + t
}
u._blocksize = 16;
u._digestsize = 16;
exports.o = u;