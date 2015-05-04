#!/usr/bin/env python

import cgi
import re
import time
import gpio
import json


def notfound ( env, start_response ):
    start_response( '404 Not Found', [('Content-type', 'text/plain')] )
    return [b'Not Found']

def badrequest ( env, start_response ):
    start_response ( '400 Bad Request', [('Content-type', 'text/plain')] )
    return [b'Bad Request']


def localtime ( env, start_response ):
    t = time.localtime()
    lt = { 'time': { 'year': t.tm_year,
                     'month': t.tm_mon,
                     'day': t.tm_mday,
                     'hour': t.tm_hour,
                     'minute': t.tm_min,
                     'second': t.tm_sec
                   }
         }
    jlt = json.dumps(lt)
    resp = jlt.encode('utf-8')
    start_response( '200 OK', [('Content-type', 'application/json')] )
    return [resp]


def flags2list(flags):
    lists = []

    if (flags & gpio.PIN_INPUT):
        lists.append('INPUT')
    if (flags & gpio.PIN_OUTPUT):
        lists.append('OUTPUT')
    if (flags & gpio.PIN_OPENDRAIN):
        lists.append('OPENDRAIN')
    if (flags & gpio.PIN_PUSHPULL):
        lists.append('PUSHPULL')
    if (flags & gpio.PIN_TRISTATE):
        lists.append('TRISTATE')
    if (flags & gpio.PIN_PULLUP):
        lists.append('PULLUP')
    if (flags & gpio.PIN_PULLDOWN):
        lists.append('PULLDOWN')
    if (flags & gpio.PIN_INVIN):
        lists.append('INVIN')
    if (flags & gpio.PIN_INVOUT):
        lists.append('INVOUT')
    if (flags & gpio.PIN_PULSATE):
        lists.append('PULSATE')

    return lists


def flags2str(flags):
    return ','.join(flags2list(flags))


def gpioapi ( env, start_response ):
    configs = { 'INPUT' : gpio.PIN_INPUT,
                'OUTPUT' : gpio.PIN_OUTPUT,
		'OPENDRAIN' : gpio.PIN_OPENDRAIN,
		'PUSHPULL' : gpio.PIN_PUSHPULL,
		'TRISTATE' : gpio.PIN_TRISTATE,
		'PULLUP' : gpio.PIN_PULLUP,
		'PULLDOWN' : gpio.PIN_PULLDOWN,
		'INVIN' : gpio.PIN_INVIN,
		'INVOUT' : gpio.PIN_INVOUT,
		'PULSATE' : gpio.PIN_PULSATE }

    gpioc = gpio.controller()
    max_pin = gpioc.max_pin

    request = env['REQUEST_METHOD']
    uri = re.split('/',re.sub('/api/','',env['PATH_INFO']))

    if ( (len(uri) == 1) or ((len(uri) == 2) and (uri[1] == '')) ):
        if ( request != 'GET' ):
            badrequest( env, start_response )
        else:
            gpiol = {}
            for p in range(0, max_pin + 1):
                 pin = gpioc.pin(p)
                 try:
                     value = pin.value
                 except gpio.GpioError as e:
                     # pin with this number is unknown
                     continue
                 gpiol[p] = { 'name': pin.name, 'value': value, 'config': flags2str(pin.config), 'caps': flags2list(pin.caps) }
            jgpiol = json.dumps(gpiol)
            resp = jgpiol.encode('utf-8')
            start_response( '200 OK', [('Content-type', 'application/json')] )
            return [resp]

    if ( (len(uri) == 2) or ((len(uri) == 3) and (uri[2] == '')) ):
        gpiol = {}
        p = uri[1]
        pin = gpioc.pin(int(p))
        try:
            value = pin.value
        except gpio.GpioError as e:
            notfound ( env, start_response )
        if ( request == 'PUT' ):
            query=re.split('=',env['QUERY_STRING'])
            if ( len(query) == 2 ):
                op = query[0]
                val = query[1]
                if ( op == 'value' ):
                    if ( int(val) == 1 ):
                        pin.value = gpio.HIGH
                    else:
                        pin.value = gpio.LOW
                elif ( op == 'config' ):
                    if ( val.upper() in configs ):
                        pin.config = configs[ val.upper() ]
        if ( (request == 'PUT') or (request == 'GET') ):
            gpiol[p] = { 'name': pin.name, 'value': pin.value, 'config': flags2str(pin.config), 'caps': flags2list(pin.caps) }
            jgpiol = json.dumps(gpiol)
            resp = jgpiol.encode('utf-8')
            start_response( '200 OK', [('Content-type', 'application/json')] )
            return [resp]
           

    if ( len(uri) > 2 ):
        p = uri[1]
        pin = gpioc.pin(int(p))
        try:
            value = pin.value
        except gpio.GpioError as e:
            notfound ( env, start_response )
        op = uri[2].lower()
        if ( request == 'GET' ):
            if ( op == 'name' ):
                gpiol = { 'name': pin.name }
                jgpiol = json.dumps(gpiol)
                resp = jgpiol.encode('utf-8')
                start_response( '200 OK', [('Content-type', 'application/json')] )
                return [resp]
            elif ( op == 'value' ):
                gpiol = { 'value': value }
                jgpiol = json.dumps(gpiol)
                resp = jgpiol.encode('utf-8')
                start_response( '200 OK', [('Content-type', 'application/json')] )
                return [resp]
            elif ( op == 'config' ):
                gpiol = { 'config': flags2str(pin.config) }
                jgpiol = json.dumps(gpiol)
                resp = jgpiol.encode('utf-8')
                start_response( '200 OK', [('Content-type', 'application/json')] )
                return [resp]
            elif ( op == 'caps' ):
                gpiol = { 'caps': flags2list(pin.caps) }
                jgpiol = json.dumps(gpiol)
                resp = jgpiol.encode('utf-8')
                start_response( '200 OK', [('Content-type', 'application/json')] )
                return [resp]

    badrequest( env, start_response )


pathmap = { 'gpio': gpioapi,
            'localtime': localtime,
          }


def application ( env, start_response ):
    path = re.split('/',re.sub('/api/','',env['PATH_INFO']))[0]
    handler = pathmap.get( path, notfound )
    return handler( env, start_response )

