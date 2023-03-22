var CryptoJS = require("crypto-js");

function b(a, b) {
    var c = CryptoJS.enc.Utf8.parse(b),
        d = CryptoJS.enc.Utf8.parse("0102030405060708"),
        e = CryptoJS.enc.Utf8.parse(a),
        f = CryptoJS.AES.encrypt(e, c, {
            iv: d,
            mode: CryptoJS.mode.CBC
        });
    return f.toString()
}

function d(d, e, f, g) {
    var h = {}, i = "GQF4N5tI0nNbhWVF"
    return h.encText = b(d, g),
        h.encText = b(h.encText, i),
        h.encSecKey = '5bff63591402fa3718ecb8c99241a4f2ef9c0868675cc5d4b0a015b1a5448bad6ee00dec4bd316fb4e05294f8d54dc12ce2de6e9ed078c20eaea7d25d876aefd6d407fdc0bde8c5db7f4b4f01180c9d64bfec69c3f65e14524f3f7be9b6516dfaa9100c943647a98f64af5daf82be01836945fdfe55a2db380710a1580368db4',
        h
}

function get_params_comment(song_id, pageNo, pageSize, cursor) {
    i7b = {
        "rid": "R_SO_4_" + song_id,
        "threadId": "R_SO_4_" + song_id,
        "pageNo": pageNo,
        "pageSize": pageSize,
        "cursor": cursor,
        "offset": "0",
        "orderType": "1",
        "csrf_token": ""
    }

    var bMr5w = d(JSON.stringify(i7b), '010001', '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7', '0CoJUm6Qyw8W8jud');
    var params = bMr5w.encText
    var encSecKey = bMr5w.encSecKey

    return { params: params, encSecKey: encSecKey }
}

function get_params_user(uid, type) {
    i7b = {
        "limit": "1000",
        "offset": "0",
        "total": "true",
        "uid": uid,
        "csrf_token": "",
        "type": type
    }

    var bMr5w = d(JSON.stringify(i7b), '010001', '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7', '0CoJUm6Qyw8W8jud');
    var params = bMr5w.encText
    var encSecKey = bMr5w.encSecKey

    return { params: params, encSecKey: encSecKey }
}