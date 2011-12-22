#!/usr/bin/env python
# -*- coding: utf-8 -*-
import struct

TYPE_BYTE = "\x00"			#unsigned byte
TYPE_BYTE_MINUS = "\x01"		#unsigned byte
TYPE_SHORT = "\x10"			#unsigned short
TYPE_SHORT_MINUS = "\x11"	#unsigned short
TYPE_INT = "\x20"			#unsigned int
TYPE_INT_MINUS = "\x21"		#unsigned int
TYPE_LONG = "\x30"			#signed long
TYPE_FLOAT = "\x31"			#signed double
TYPE_STRING = "\x40"		#string
TYPE_UNICODE = "\x41"		#string
TYPE_DICT = "\x50"			#dict
TYPE_LIST = "\x51"			#list
TYPE_TUPLE = "\x52"			#tuple
TYPE_BOOL = "\x53"			#bool

def _str(s):
	if type(s) == str:			return s
	elif type(s) == unicode:	return s.encode("utf-8")
	else:					return str(s)

def _unicode(s):
	if type(s) == unicode:		return s
	elif type(s) == str:		return s.decode("utf-8")
	else:					return str(s).decode("utf-8")

def get_type_name(type_id):
	for key, value in globals().iteritems():
		if not key.startswith("TYPE"):
			continue
		if type_id == value:
			return key

def pack_dict(d):
	s = ""
	for key, value in d.iteritems():
		#print key, value
		s += pack_obj(key)
		s += pack_obj(value)
	return TYPE_DICT + pack_obj(len(s)) + s

def unpack_dict(s, i=0):
	llen, vlen = unpack_obj(s, i+1)
	i_max = i+1+llen+vlen-1
	i += 1+llen
	d = {}
	while i <= i_max:
		key_length, key = unpack_obj(s, i)
		i += key_length
		#print get_type_name(s[i]), "\t",
		value_length, value = unpack_obj(s, i)
		i += value_length
		#print key, value, "\t", key_length, value_length
		d[key] = value
	return (1+llen+vlen, d) #type+length_len+length, d

def pack_list(l, pack_tuple=False):
	s = ""
	for obj in l:
		s += pack_obj(obj)
	if not pack_tuple:
		return TYPE_LIST + pack_obj(len(s)) + s
	else:
		return TYPE_TUPLE + pack_obj(len(s)) + s

def unpack_list(s, i=0, unpack_tuple=False):
	llen, vlen = unpack_obj(s, i+1)
	i_max = i+1+llen+vlen-1
	i += 1+llen
	l = []
	while i <= i_max:
		obj_length, obj = unpack_obj(s, i)
		i += obj_length
		l.append(obj)
	if not unpack_tuple:
		return (1+llen+vlen, l)
	else:
		return (1+llen+vlen, tuple(l))

def pack_obj(obj):
	obj_type = type(obj)
	if obj_type == int:
		if 0 > obj >= -255:	return TYPE_BYTE_MINUS + struct.pack(">B", 0-obj)
		elif 0 > obj >= -65535:	return TYPE_SHORT_MINUS + struct.pack(">H", 0-obj)
		elif 0 > obj:			return TYPE_INT_MINUS + struct.pack(">I", 0-obj)
		elif obj < 255:		return TYPE_BYTE + struct.pack(">B", obj)
		elif obj < 65535:		return TYPE_SHORT + struct.pack(">H", obj)
		else:				return TYPE_INT + struct.pack(">I", obj)
	elif obj_type == long:		return TYPE_LONG + struct.pack(">q", obj)
	elif obj_type == float:		return TYPE_FLOAT + struct.pack(">d", obj)
	elif obj_type == dict:		return pack_dict(obj)
	elif obj_type == list:		return pack_list(obj)
	elif obj_type == tuple:		return pack_list(obj, True)
	elif obj_type == bool:
		return TYPE_BOOL + struct.pack(">B", (obj and 1 or 0))
	elif obj_type == unicode:
		obj = _str(obj)
		return TYPE_UNICODE + pack_obj(len(obj)) + obj
	else:
		obj = _str(obj)
		return TYPE_STRING + pack_obj(len(obj)) + obj
	#else:
	#	raise TypeError("unsupport type: %s"%_str(obj_type))
def unpack_obj(s, i=0):
	"""unpack from s[i], return (unpack_length, obj)"""
	obj_type = s[i]
	if obj_type == TYPE_BYTE: 		return (2, struct.unpack(">B", s[i+1])[0])
	elif obj_type == TYPE_SHORT:		return (3, struct.unpack(">H", s[i+1:i+3])[0])
	elif obj_type == TYPE_INT:		return (5, struct.unpack(">I", s[i+1:i+5])[0])
	elif obj_type == TYPE_BYTE_MINUS:	return (2, 0-struct.unpack(">B", s[i+1])[0])
	elif obj_type == TYPE_SHORT_MINUS:return (3, 0-struct.unpack(">H", s[i+1:i+3])[0])
	elif obj_type == TYPE_INT_MINUS:	return (5, 0-struct.unpack(">I", s[i+1:i+5])[0])
	elif obj_type == TYPE_LONG:	return (9, long(struct.unpack(">q", s[i+1:i+9])[0]))
	elif obj_type == TYPE_FLOAT:		return (9, struct.unpack(">d", s[i+1:i+9])[0])
	elif obj_type == TYPE_DICT:		return unpack_dict(s, i)
	elif obj_type == TYPE_LIST:		return unpack_list(s, i)
	elif obj_type == TYPE_TUPLE:		return unpack_list(s, i, True)
	elif obj_type == TYPE_BOOL:
		return (2, (struct.unpack(">B", s[i+1])[0] and True or False))
	elif obj_type == TYPE_UNICODE:
		llen, vlen = unpack_obj(s, i+1)
		return (1+llen+vlen, _unicode(s[i+1+llen:i+1+llen+vlen]))
	elif obj_type == TYPE_STRING:
		llen, vlen = unpack_obj(s, i+1)
		return (1+llen+vlen, s[i+1+llen:i+1+llen+vlen])
	else:
		raise TypeError("unknow type: %s"%obj_type.encode("hex"))

if __name__ == "__main__":
	s = pack_obj({"string": "abc",
				"int": 123,
				"long": -123L,
				"float": 1.01,
				"unicode": u"abcde",
				"dict": {"dict_int": -123,
						"dict_string": "zzz",
						},
				"list": [10, 100, (101, True)],
				})
	print s.encode("hex")
	print unpack_obj(s)[1]
