#!/usr/bin/python3
import hashlib
import re


def hashText(password):
    hash_object = hashlib.sha256(password.encode())
    return hash_object.hexdigest()

def matchExpression(user_input,regex):
	m = re.search(regex,user_input)
	if m is None:
		return False
	return True
