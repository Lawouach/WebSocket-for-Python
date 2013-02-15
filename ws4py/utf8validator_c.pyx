# coding=utf-8

###############################################################################
##
##  Copyright 2011 Tavendo GmbH
##
##  Note:
##
##  This code is a Python implementation of the algorithm
##
##            "Flexible and Economical UTF-8 Decoder"
##
##  by Bjoern Hoehrmann
##
##       bjoern@hoehrmann.de
##       http://bjoern.hoehrmann.de/utf-8/decoder/dfa/
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

## DFA transitions
cdef extern from "dfa.h":
    cdef char* UTF8VALIDATOR_DFA

cdef extern from "Python.h":
    int PyObject_AsReadBuffer(object, void**, Py_ssize_t*) except -1

DEF _UTF8_ACCEPT = 0
DEF _UTF8_REJECT = 1

cdef class Utf8Validator(object):
    """
    Incremental UTF-8 validator with constant memory consumption (minimal state).

    Implements the algorithm "Flexible and Economical UTF-8 Decoder" by
    Bjoern Hoehrmann (http://bjoern.hoehrmann.de/utf-8/decoder/dfa/).
    """

    UTF8_ACCEPT = 0
    UTF8_REJECT = 1

    cdef public int i
    cdef public int state
    cdef public int codepoint

    def __init__(self):
        self.reset()

    def decode(self, b):
        """
        Eat one UTF-8 octet, and validate on the fly.

        Returns UTF8_ACCEPT when enough octets have been consumed, in which case
        self.codepoint contains the decoded Unicode code point.

        Returns UTF8_REJECT when invalid UTF-8 was encountered.

        Returns some other positive integer when more octets need to be eaten.
        """
        cdef int type = UTF8VALIDATOR_DFA[b]
        if self.state != _UTF8_ACCEPT:
            self.codepoint = (b & 0x3f) | (self.codepoint << 6)
        else:
            self.codepoint = (0xff >> type) & b
        self.state = UTF8VALIDATOR_DFA[256 + self.state * 16 + type]
        return self.state

    def reset(self):
        """
        Reset validator to start new incremental UTF-8 decode/validation.
        """
        self.state = _UTF8_ACCEPT
        self.codepoint = 0
        self.i = 0

    def validate(self, ba):
        """
        Incrementally validate a chunk of bytes provided as bytearray.

        Will return a quad (valid?, endsOnCodePoint?, currentIndex, totalIndex).

        As soon as an octet is encountered which renders the octet sequence
        invalid, a quad with valid? == False is returned. currentIndex returns
        the index within the currently consumed chunk, and totalIndex the
        index within the total consumed sequence that was the point of bail out.
        When valid? == True, currentIndex will be len(ba) and totalIndex the
        total amount of consumed bytes.
        """
        cdef int state = self.state
        cdef int i=0, b
        cdef char* buf
        cdef Py_ssize_t buf_len
        PyObject_AsReadBuffer(ba, <void**>&buf, &buf_len)
        for i in range(buf_len):
            b = buf[i]
            ## optimized version of decode(), since we are not interested in actual code points
            state = UTF8VALIDATOR_DFA[256 + (state << 4) + UTF8VALIDATOR_DFA[b]]
            if state == _UTF8_REJECT:
                self.i += i
                self.state = state
                return False, False, i, self.i
        self.i += i
        self.state = state
        return True, state == _UTF8_ACCEPT, i, self.i
