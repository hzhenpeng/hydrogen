# -*- coding: utf-8 -*-
# Created by restran on 2017/10/13
from __future__ import unicode_literals, absolute_import

import logging

from flask import request
from crypto import handlers
from utils import APIHandler

logger = logging.getLogger(__name__)


def do_decode(method, data, params):
    # 不能用 import string 的方式，否则打包成 exe 后会无法 import
    h = getattr(handlers, method, None)
    if h is not None:
        # data = force_text(converter.from_base64(data))

        decode = getattr(h, 'decode', None)
        decode_all = getattr(h, 'decode_all', None)
        if decode_all is not None:
            decode_func = decode_all
        elif decode is not None:
            decode_func = decode
        else:
            return '!!!error!!! no available decode for method %s' % method

        def _do_decode(d):
            if params is not None:
                _result = decode_func(d, *params, verbose=True)
            else:
                _result = decode_func(d, verbose=True)

            return _result

        if method in ('manchester',):
            index = 0
            last_index = 0
            data += ' '
            length = len(data)
            result = []
            # 输入的时候是以什么字符分隔，输出的时候保持一致
            while index < length:
                t = data[index]
                if t in (' ', '\n'):
                    text = data[last_index:index]
                    last_index = index + 1
                    if text != '':
                        r = _do_decode(text)
                        result.append(r)

                    result.append(t)
                index += 1

            result = ''.join(result)
            result = result.rstrip(' ')
        else:
            result = _do_decode(data)

    else:
        result = '!!!error!!! method %s not found' % method

    return result


def decode_data():
    if request.json is None:
        return APIHandler.fail()

    method = request.json.get('method')
    data = request.json.get('data')
    params = request.json.get('params')
    if method is None or data is None:
        return APIHandler.fail()

    try:
        result = do_decode(method, data, params)
    except Exception as e:
        logger.exception(e)
        result = '!!!error!!! %s' % e

    if result is None:
        result = '!!!error!!!'

    return APIHandler.success(result)
