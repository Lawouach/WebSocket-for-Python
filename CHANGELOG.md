# Change Log

## Unreleased
[Full Changelog](https://github.com/Lawouach/WebSocket-for-Python/compare/0.5.1...master)

**Changes:**

 * Upgrade Python support to include 3.6, 3.7, 3.8 and 3.9
 * Drop support for Python 3.* < 3.6 (Python 2.7 remains)

## [0.5.1](https://github.com/Lawouach/WebSocket-for-Python/tree/0.5.1) (2018-02-28)
[Full Changelog](https://github.com/Lawouach/WebSocket-for-Python/compare/0.5.0...0.5.1)
**Merged pull requests:**

- Rudimentary fix and testcase for Issue #179 [\#219](https://github.com/Lawouach/WebSocket-for-Python/pull/219) ([medington](https://github.com/medington))

## [0.5.0](https://github.com/Lawouach/WebSocket-for-Python/tree/0.5.0) (2018-02-27)
[Full Changelog](https://github.com/Lawouach/WebSocket-for-Python/compare/0.4.3...0.5.0)
**Merged pull requests:**

- proper fix for #230: on secure, only pass the requested number of bytes to the parsers [\#239](https://github.com/Lawouach/WebSocket-for-Python/pull/239) ([jmichiel](https://github.com/jmichiel))
- fixed runtime error: Set changed size during iteration [\#233](https://github.com/Lawouach/WebSocket-for-Python/pull/233) ([kamwoh](https://github.com/kamwoh))
- Adds argument to set block value on gevent get command in WebSocketClient.receive() [\#221](https://github.com/Lawouach/WebSocket-for-Python/pull/221) ([thaffenden](https://github.com/thaffenden))

**Changes:**

- Clarifies this project is on hiatus in README

## [0.4.3](https://github.com/Lawouach/WebSocket-for-Python/tree/0.4.3) (2017-12-19)
[Full Changelog](https://github.com/Lawouach/WebSocket-for-Python/compare/0.4.3...0.4.3)
**Merged pull requests:**

- Change threaded client test to test ssl socket [\#213](https://github.com/Lawouach/WebSocket-for-Python/pull/213) ([awelkie](https://github.com/awelkie))
- Create MANIFEST.in with LICENSE [\#215](https://github.com/Lawouach/WebSocket-for-Python/pull/215) ([pmlandwehr](https://github.com/pmlandwehr))
- exclude certain headers when requested [\#217](https://github.com/Lawouach/WebSocket-for-Python/pull/217) ([klattimer](https://github.com/klattimer))
- change from type() to isinstance() [\#236](https://github.com/Lawouach/WebSocket-for-Python/pull/236) ([noam-graetz](https://github.com/noam-graetz))

**Changes:**

- Various test cleanups
- Disable build for Python 3.4 as running into https://github.com/pypa/setuptools/issues/951 (Thinking of dropping official support for it too)

## [0.4.2](https://github.com/Lawouach/WebSocket-for-Python/tree/0.4.2) (2017-03-29)
[Full Changelog](https://github.com/Lawouach/WebSocket-for-Python/compare/0.4.1...0.4.2)

**Merged pull requests:**

- Block on receiving from SSL socket [\#212](https://github.com/Lawouach/WebSocket-for-Python/pull/212) ([awelkie](https://github.com/awelkie))

## [0.4.1](https://github.com/Lawouach/WebSocket-for-Python/tree/0.4.1) (2017-03-26)
[Full Changelog](https://github.com/Lawouach/WebSocket-for-Python/compare/0.4.0...0.4.1)

**Merged pull requests:**

- fixes parsed hostname [\#210](https://github.com/Lawouach/WebSocket-for-Python/pull/210) ([isubas](https://github.com/isubas))

## [0.4.0](https://github.com/Lawouach/WebSocket-for-Python/tree/0.4.0) (2017-03-24)
[Full Changelog](https://github.com/Lawouach/WebSocket-for-Python/compare/0.3.5...0.4.0)

**Implemented enhancements:**

- exception not catch in websocket.py always [\#70](https://github.com/Lawouach/WebSocket-for-Python/issues/70)

**Fixed bugs:**

- Last send never happens [\#167](https://github.com/Lawouach/WebSocket-for-Python/issues/167)

**Closed issues:**

- PyPI latest release 0.3.5 does not include \#205 and therefore breaks with cherrypy [\#209](https://github.com/Lawouach/WebSocket-for-Python/issues/209)
- Unable to reconnect [\#207](https://github.com/Lawouach/WebSocket-for-Python/issues/207)
- CherryPy does not use its own wsgiserver anymore, which ws4py depended on [\#205](https://github.com/Lawouach/WebSocket-for-Python/issues/205)
- py2exe / python2.7 / syntax error in "yield from" lines [\#202](https://github.com/Lawouach/WebSocket-for-Python/issues/202)
- Missing 0.3.5 changelog and tag [\#192](https://github.com/Lawouach/WebSocket-for-Python/issues/192)
- ws4py 0.3.5 doesn't receive all messages over wss [\#191](https://github.com/Lawouach/WebSocket-for-Python/issues/191)
- SSL: received\_message not getting called [\#183](https://github.com/Lawouach/WebSocket-for-Python/issues/183)
- Python 2.6 support [\#182](https://github.com/Lawouach/WebSocket-for-Python/issues/182)
- Overridden close\(\) not called under windows [\#178](https://github.com/Lawouach/WebSocket-for-Python/issues/178)
- Enabling cpstats causes ws4py to crash [\#177](https://github.com/Lawouach/WebSocket-for-Python/issues/177)
- Only support Python 3.0+ ? [\#175](https://github.com/Lawouach/WebSocket-for-Python/issues/175)
- IOError\(interrupted system call\) on dropping privilages [\#172](https://github.com/Lawouach/WebSocket-for-Python/issues/172)
- error: configure\_logger\(stdout=False, filepath="ws4py.log"\) [\#171](https://github.com/Lawouach/WebSocket-for-Python/issues/171)
- Python 3.4 and gevent 1.1 [\#170](https://github.com/Lawouach/WebSocket-for-Python/issues/170)
- Is it possible to extract headers from WebSocketProtocol using asyncio [\#169](https://github.com/Lawouach/WebSocket-for-Python/issues/169)
- server, opened\(\) is called each time a message is send [\#162](https://github.com/Lawouach/WebSocket-for-Python/issues/162)
- tlm [\#160](https://github.com/Lawouach/WebSocket-for-Python/issues/160)
- In opened\(\), closing connection would crash the server [\#159](https://github.com/Lawouach/WebSocket-for-Python/issues/159)
- Server crashes with broken pipe if client disconnects ungracefully? [\#150](https://github.com/Lawouach/WebSocket-for-Python/issues/150)
- Client connection hangs when using Cherrypy [\#146](https://github.com/Lawouach/WebSocket-for-Python/issues/146)
- low priority: wsgiref example doesn't work [\#145](https://github.com/Lawouach/WebSocket-for-Python/issues/145)
- CherryPy: simple example of an echo server [\#140](https://github.com/Lawouach/WebSocket-for-Python/issues/140)
- WebSocketClient.closed\(\) always returns code 1006 if reason string empty. [\#137](https://github.com/Lawouach/WebSocket-for-Python/issues/137)
- Server Side Connection Drops Immediately [\#134](https://github.com/Lawouach/WebSocket-for-Python/issues/134)
- Calling WebSocketClient.terminate\(\) results in AttributeError [\#131](https://github.com/Lawouach/WebSocket-for-Python/issues/131)
- ConnectionRefusedError: \[WinError 10061\] No connection could be made because the target machine actively refused it [\#130](https://github.com/Lawouach/WebSocket-for-Python/issues/130)
- AttributeError: 'NoneType' object has no attribute 'fileno' [\#129](https://github.com/Lawouach/WebSocket-for-Python/issues/129)
- wss is always one message behind [\#128](https://github.com/Lawouach/WebSocket-for-Python/issues/128)
- Asyncio Issues [\#125](https://github.com/Lawouach/WebSocket-for-Python/issues/125)

**Merged pull requests:**

- change cherrypy.wsgiserver to cheroot.server [\#206](https://github.com/Lawouach/WebSocket-for-Python/pull/206) ([raven38](https://github.com/raven38))
- This change is to address the issue with run\_forever\(\) terminating too early. [\#201](https://github.com/Lawouach/WebSocket-for-Python/pull/201) ([steowens](https://github.com/steowens))
- Don't crash with broken pipe when trying to close a connection [\#198](https://github.com/Lawouach/WebSocket-for-Python/pull/198) ([cristi8](https://github.com/cristi8))
- adding heartbeat for gevent\_client [\#195](https://github.com/Lawouach/WebSocket-for-Python/pull/195) ([alexmnt](https://github.com/alexmnt))
- minor - typo [\#193](https://github.com/Lawouach/WebSocket-for-Python/pull/193) ([johnwheeler](https://github.com/johnwheeler))
- Eliminate a protocol error when first chunk is last too. [\#186](https://github.com/Lawouach/WebSocket-for-Python/pull/186) ([plu9in](https://github.com/plu9in))
- Allow WebSocketWSGIHandler to work even in presence of a middleware [\#185](https://github.com/Lawouach/WebSocket-for-Python/pull/185) ([bozzzzo](https://github.com/bozzzzo))
- Give application status code 1005 when no good status code is parsed/received [\#181](https://github.com/Lawouach/WebSocket-for-Python/pull/181) ([isonmad](https://github.com/isonmad))
- Fix server "Bad file descriptor" error under gevent 1.1, \#170 [\#180](https://github.com/Lawouach/WebSocket-for-Python/pull/180) ([hyt-hz](https://github.com/hyt-hz))
- Version of example that doesn't need jquery, fix IOError on resume, f… [\#173](https://github.com/Lawouach/WebSocket-for-Python/pull/173) ([EternityForest](https://github.com/EternityForest))
- Fix typo [\#161](https://github.com/Lawouach/WebSocket-for-Python/pull/161) ([hexchain](https://github.com/hexchain))
- added a word [\#157](https://github.com/Lawouach/WebSocket-for-Python/pull/157) ([Mrmaxmeier](https://github.com/Mrmaxmeier))
- Removed unnecessary try/except and cleaned for some PEP8 [\#155](https://github.com/Lawouach/WebSocket-for-Python/pull/155) ([warvariuc](https://github.com/warvariuc))
- Improve Origin handling in Client [\#154](https://github.com/Lawouach/WebSocket-for-Python/pull/154) ([rdbhost](https://github.com/rdbhost))
- Fix: closing handshake does not work correctly when reason is empty [\#149](https://github.com/Lawouach/WebSocket-for-Python/pull/149) ([schiermike](https://github.com/schiermike))
- pass ssl\_options to SSLIOStream\(\) to ensure certificate validation works [\#147](https://github.com/Lawouach/WebSocket-for-Python/pull/147) ([szweep](https://github.com/szweep))
- Explained why wsgiref not for produciton [\#144](https://github.com/Lawouach/WebSocket-for-Python/pull/144) ([Seanny123](https://github.com/Seanny123))
- Added Port to Host in handshake header. [\#139](https://github.com/Lawouach/WebSocket-for-Python/pull/139) ([thiagorcdl](https://github.com/thiagorcdl))
- Don't fail when websocket was not inited. [\#135](https://github.com/Lawouach/WebSocket-for-Python/pull/135) ([eraviart](https://github.com/eraviart))
- ws4py/\_\_init\_\_.py: fix configure\_logger by importing loging.handlers as handlers [\#133](https://github.com/Lawouach/WebSocket-for-Python/pull/133) ([andrew-canaday](https://github.com/andrew-canaday))

## [0.3.5](https://github.com/Lawouach/WebSocket-for-Python/tree/0.3.5) (2014-04-01)
[Full Changelog](https://github.com/Lawouach/WebSocket-for-Python/compare/v0.3.4...0.3.5)

**Closed issues:**

- No longer working on Chome 34.0.1847.76 [\#124](https://github.com/Lawouach/WebSocket-for-Python/issues/124)

## [v0.3.4](https://github.com/Lawouach/WebSocket-for-Python/tree/v0.3.4) (2014-03-30)
[Full Changelog](https://github.com/Lawouach/WebSocket-for-Python/compare/v0.3.3...v0.3.4)

**Fixed bugs:**

- ws4py 0.3.3 installation broken [\#123](https://github.com/Lawouach/WebSocket-for-Python/issues/123)

## [v0.3.3](https://github.com/Lawouach/WebSocket-for-Python/tree/v0.3.3) (2014-03-29)
[Full Changelog](https://github.com/Lawouach/WebSocket-for-Python/compare/v0.3.2...v0.3.3)

**Implemented enhancements:**

- Upload releases to PyPI for compatibility with new pip versions [\#99](https://github.com/Lawouach/WebSocket-for-Python/issues/99)
- Gradually drop support for Python \<2.7 and \<3.3.2 [\#91](https://github.com/Lawouach/WebSocket-for-Python/issues/91)

**Fixed bugs:**

- Catch MemoryError when uploading a music file\(size: 16M\) [\#113](https://github.com/Lawouach/WebSocket-for-Python/issues/113)
- ws4py 0.2.2 no longer working on Chrome version 30 [\#108](https://github.com/Lawouach/WebSocket-for-Python/issues/108)

**Closed issues:**

- Exception in thread WebSocketClient during unit testing [\#122](https://github.com/Lawouach/WebSocket-for-Python/issues/122)
- TypeError: \_\_str\_\_ returned non-string \(type bytes\) [\#121](https://github.com/Lawouach/WebSocket-for-Python/issues/121)
- While using the Gevent WebSocket client an os error, OSError: \[Errno 24\] Too many open files, occurs [\#120](https://github.com/Lawouach/WebSocket-for-Python/issues/120)
- AttributeError: 'MyClient' object has no attribute '\_cleanup' [\#119](https://github.com/Lawouach/WebSocket-for-Python/issues/119)
- Message string representation does not work in Python 3 [\#117](https://github.com/Lawouach/WebSocket-for-Python/issues/117)
- Not able to install a specific version of an unsecure package [\#115](https://github.com/Lawouach/WebSocket-for-Python/issues/115)
- How to use WebSocketManager with server? [\#111](https://github.com/Lawouach/WebSocket-for-Python/issues/111)
- client: KeyboardInterrupt silently catched [\#109](https://github.com/Lawouach/WebSocket-for-Python/issues/109)
- unittests2 shouldn't be needed with python \>= 2.7 and \>= 3.2 [\#106](https://github.com/Lawouach/WebSocket-for-Python/issues/106)

**Merged pull requests:**

- base example documentation fix [\#118](https://github.com/Lawouach/WebSocket-for-Python/pull/118) ([husio](https://github.com/husio))
- fix: changed gevent server to use a real gevent.pool.Pool [\#114](https://github.com/Lawouach/WebSocket-for-Python/pull/114) ([fischerq](https://github.com/fischerq))
- Tutorial should import TornadoWebSocketClient. [\#112](https://github.com/Lawouach/WebSocket-for-Python/pull/112) ([ajdavis](https://github.com/ajdavis))
- Fix cherrypy logging [\#107](https://github.com/Lawouach/WebSocket-for-Python/pull/107) ([UncleRus](https://github.com/UncleRus))

## [v0.3.2](https://github.com/Lawouach/WebSocket-for-Python/tree/v0.3.2) (2013-09-12)
[Full Changelog](https://github.com/Lawouach/WebSocket-for-Python/compare/v0.3.0-beta...v0.3.2)

**Implemented enhancements:**

- Move back to unicode and byte litterals [\#100](https://github.com/Lawouach/WebSocket-for-Python/issues/100)
- remove implicit gevent monkey patching in the gevent client [\#90](https://github.com/Lawouach/WebSocket-for-Python/issues/90)
- Busy loop in SelectPoller that is consuming a lot of CPU [\#87](https://github.com/Lawouach/WebSocket-for-Python/issues/87)
- tornado expects bytes but TornadoWebSocketClient gives strings [\#71](https://github.com/Lawouach/WebSocket-for-Python/issues/71)

**Fixed bugs:**

- AssertionError: Header values must be strings [\#103](https://github.com/Lawouach/WebSocket-for-Python/issues/103)
- remove implicit gevent monkey patching in the gevent client [\#90](https://github.com/Lawouach/WebSocket-for-Python/issues/90)
- ws4py.server.wsgiutils.py got some error in python 3.3 [\#88](https://github.com/Lawouach/WebSocket-for-Python/issues/88)
- Busy loop in SelectPoller that is consuming a lot of CPU [\#87](https://github.com/Lawouach/WebSocket-for-Python/issues/87)
- Socket not properly closed in Win7 [\#69](https://github.com/Lawouach/WebSocket-for-Python/issues/69)

**Closed issues:**

- NameError: global name 'dec' is not defined \(in Python 2.7.5\) [\#102](https://github.com/Lawouach/WebSocket-for-Python/issues/102)
- Allow cherrypy users to pass in a custom poller to the manager [\#95](https://github.com/Lawouach/WebSocket-for-Python/issues/95)
- IPv6 sockets not supported [\#86](https://github.com/Lawouach/WebSocket-for-Python/issues/86)
- Support `ws+unix` scheme [\#76](https://github.com/Lawouach/WebSocket-for-Python/issues/76)
- Strange traceback with WebSocket.send [\#73](https://github.com/Lawouach/WebSocket-for-Python/issues/73)

**Merged pull requests:**

- fixed some old references to removed functions enc\(\) and dec\(\) [\#101](https://github.com/Lawouach/WebSocket-for-Python/pull/101) ([flaviogrossi](https://github.com/flaviogrossi))
- ws4py.client classes should support client certificates [\#98](https://github.com/Lawouach/WebSocket-for-Python/pull/98) ([EliAndrewC](https://github.com/EliAndrewC))
- Code correction in built-in client tutorial [\#96](https://github.com/Lawouach/WebSocket-for-Python/pull/96) ([elmiko](https://github.com/elmiko))
- Fixed a couple of typos in the docs [\#92](https://github.com/Lawouach/WebSocket-for-Python/pull/92) ([rakiru](https://github.com/rakiru))
- Fix typo in 'ws4y.websocket' [\#89](https://github.com/Lawouach/WebSocket-for-Python/pull/89) ([jodal](https://github.com/jodal))
- Fix for bytestrings in Tornado client. [\#85](https://github.com/Lawouach/WebSocket-for-Python/pull/85) ([lbolla](https://github.com/lbolla))

## [v0.3.0-beta](https://github.com/Lawouach/WebSocket-for-Python/tree/v0.3.0-beta) (2013-03-16)
[Full Changelog](https://github.com/Lawouach/WebSocket-for-Python/compare/v0.2.4...v0.3.0-beta)

**Closed issues:**

- Threaded WebSocket client always exits randomly [\#78](https://github.com/Lawouach/WebSocket-for-Python/issues/78)
- test\_cherrypy.py fails with py3 [\#72](https://github.com/Lawouach/WebSocket-for-Python/issues/72)
- A simpler gevent server example? [\#66](https://github.com/Lawouach/WebSocket-for-Python/issues/66)

**Merged pull requests:**

- select.select\(\) on Windows does not allow empty rlist. [\#83](https://github.com/Lawouach/WebSocket-for-Python/pull/83) ([Who8MyLunch](https://github.com/Who8MyLunch))
- DOC: add omitted default value for closed\(\) in Client example [\#80](https://github.com/Lawouach/WebSocket-for-Python/pull/80) ([y-p](https://github.com/y-p))
- README: Mention to wsaccel [\#79](https://github.com/Lawouach/WebSocket-for-Python/pull/79) ([methane](https://github.com/methane))
- Faster utf8validate. [\#75](https://github.com/Lawouach/WebSocket-for-Python/pull/75) ([methane](https://github.com/methane))
- Cleanup indent and trailing spaces. [\#74](https://github.com/Lawouach/WebSocket-for-Python/pull/74) ([methane](https://github.com/methane))

## [v0.2.4](https://github.com/Lawouach/WebSocket-for-Python/tree/v0.2.4) (2012-12-13)
[Full Changelog](https://github.com/Lawouach/WebSocket-for-Python/compare/v0.2.3...v0.2.4)

**Closed issues:**

- echo\_cherrypy\_server with Python 3.2 fails on client connection [\#62](https://github.com/Lawouach/WebSocket-for-Python/issues/62)

**Merged pull requests:**

- Doc build improvements [\#65](https://github.com/Lawouach/WebSocket-for-Python/pull/65) ([jodal](https://github.com/jodal))
- Don't broadcast messages to terminated WebSockets [\#64](https://github.com/Lawouach/WebSocket-for-Python/pull/64) ([jodal](https://github.com/jodal))
- Fixup/readme [\#63](https://github.com/Lawouach/WebSocket-for-Python/pull/63) ([richo](https://github.com/richo))

## [v0.2.3](https://github.com/Lawouach/WebSocket-for-Python/tree/v0.2.3) (2012-10-27)
[Full Changelog](https://github.com/Lawouach/WebSocket-for-Python/compare/v0.2.2...v0.2.3)

**Closed issues:**

- urlsplit in Python 2.6.1 and earlier doesn't parse ws or wss properly. [\#59](https://github.com/Lawouach/WebSocket-for-Python/issues/59)
- Inconsistent tabs/spaces [\#58](https://github.com/Lawouach/WebSocket-for-Python/issues/58)
- Bug in documentation [\#55](https://github.com/Lawouach/WebSocket-for-Python/issues/55)
- wss server support [\#40](https://github.com/Lawouach/WebSocket-for-Python/issues/40)
- Port to Python 3 [\#29](https://github.com/Lawouach/WebSocket-for-Python/issues/29)

**Merged pull requests:**

- Work around Python 2.6.X bug in urlparse.urlsplit\(\) [\#60](https://github.com/Lawouach/WebSocket-for-Python/pull/60) ([dsully](https://github.com/dsully))
- Bug fix in WebSocketPlugin.broadcast\(\) [\#54](https://github.com/Lawouach/WebSocket-for-Python/pull/54) ([ralhei](https://github.com/ralhei))
- Minor fix which turns an unintentional and confusing error message into the intended error message [\#53](https://github.com/Lawouach/WebSocket-for-Python/pull/53) ([EliAndrewC](https://github.com/EliAndrewC))

## [v0.2.2](https://github.com/Lawouach/WebSocket-for-Python/tree/v0.2.2) (2012-06-21)
[Full Changelog](https://github.com/Lawouach/WebSocket-for-Python/compare/v0.2.1...v0.2.2)

**Closed issues:**

- memory leak in streaming.Stream [\#51](https://github.com/Lawouach/WebSocket-for-Python/issues/51)
- ws4py shouldn't send a masked message to the client [\#50](https://github.com/Lawouach/WebSocket-for-Python/issues/50)
- In client/\_\_init\_\_.py: remaining 'body' bytes ignored [\#46](https://github.com/Lawouach/WebSocket-for-Python/issues/46)
- ws4py.client.threadedclient is not compatible with ws4py.server.cherrypyserver [\#44](https://github.com/Lawouach/WebSocket-for-Python/issues/44)
- infinite loop in threadedclient.py when server closes websocket [\#23](https://github.com/Lawouach/WebSocket-for-Python/issues/23)

**Merged pull requests:**

- Change Sec-WebSocket-Origin header to Origin as per RFC [\#49](https://github.com/Lawouach/WebSocket-for-Python/pull/49) ([jtakkala](https://github.com/jtakkala))
- Testing: Add support for `python setup.py test`, tox, and Travis CI [\#47](https://github.com/Lawouach/WebSocket-for-Python/pull/47) ([msabramo](https://github.com/msabramo))
- Fixed geventclient.WebSocketClient.receive\(\) blocking forever [\#45](https://github.com/Lawouach/WebSocket-for-Python/pull/45) ([aluzzardi](https://github.com/aluzzardi))
- Doctest fixed at ws4py.framing in Frame [\#43](https://github.com/Lawouach/WebSocket-for-Python/pull/43) ([stuntgoat](https://github.com/stuntgoat))
- Delete greenlet start\(\) [\#42](https://github.com/Lawouach/WebSocket-for-Python/pull/42) ([yrttyr](https://github.com/yrttyr))

## [v0.2.1](https://github.com/Lawouach/WebSocket-for-Python/tree/v0.2.1) (2012-03-28)
[Full Changelog](https://github.com/Lawouach/WebSocket-for-Python/compare/v0.2.0...v0.2.1)

**Closed issues:**

- wsgi.input \_sock not working [\#41](https://github.com/Lawouach/WebSocket-for-Python/issues/41)
- ImportError: No module named gevent [\#39](https://github.com/Lawouach/WebSocket-for-Python/issues/39)
- HandshakeError: WebSocket version required [\#36](https://github.com/Lawouach/WebSocket-for-Python/issues/36)
- tools.websocket.version should allow more than one version [\#34](https://github.com/Lawouach/WebSocket-for-Python/issues/34)
- TornadoWebSocketClient doesn't support SSL [\#32](https://github.com/Lawouach/WebSocket-for-Python/issues/32)
- Problem creating a websocket [\#31](https://github.com/Lawouach/WebSocket-for-Python/issues/31)
- KeyboardInterrupt ignored in WebSocketClient [\#30](https://github.com/Lawouach/WebSocket-for-Python/issues/30)

**Merged pull requests:**

- Delete start\(\) [\#38](https://github.com/Lawouach/WebSocket-for-Python/pull/38) ([yrttyr](https://github.com/yrttyr))
- Tornado implementation fix [\#37](https://github.com/Lawouach/WebSocket-for-Python/pull/37) ([protoss-player](https://github.com/protoss-player))
- Fix SSL support in TornadoWebSocketClient and add missing import [\#33](https://github.com/Lawouach/WebSocket-for-Python/pull/33) ([patrickod](https://github.com/patrickod))
- Fix SSL Clients [\#27](https://github.com/Lawouach/WebSocket-for-Python/pull/27) ([chadselph](https://github.com/chadselph))
- send\(\) really shouldn't fail silently when getting an unknown data type [\#26](https://github.com/Lawouach/WebSocket-for-Python/pull/26) ([chadselph](https://github.com/chadselph))

## [v0.2.0](https://github.com/Lawouach/WebSocket-for-Python/tree/v0.2.0) (2012-02-23)
[Full Changelog](https://github.com/Lawouach/WebSocket-for-Python/compare/v0.1.5...v0.2.0)

**Closed issues:**

- Incorrect args in TornadoWebSocketClient constructor [\#25](https://github.com/Lawouach/WebSocket-for-Python/issues/25)
- Typo in echo\_client example [\#24](https://github.com/Lawouach/WebSocket-for-Python/issues/24)
- Typos following recent code changes... [\#22](https://github.com/Lawouach/WebSocket-for-Python/issues/22)
- ThreadedHandler still referenced [\#21](https://github.com/Lawouach/WebSocket-for-Python/issues/21)
- memory leak [\#20](https://github.com/Lawouach/WebSocket-for-Python/issues/20)
- Please store the close code and reason in WebSocketBaseClient [\#19](https://github.com/Lawouach/WebSocket-for-Python/issues/19)
- Exception when running with gevent 1.0 [\#18](https://github.com/Lawouach/WebSocket-for-Python/issues/18)
- Version 0.1.5 is not installable [\#17](https://github.com/Lawouach/WebSocket-for-Python/issues/17)
- TypeError: list indices must be integers, not str [\#16](https://github.com/Lawouach/WebSocket-for-Python/issues/16)
- All frames from the client should be masked [\#15](https://github.com/Lawouach/WebSocket-for-Python/issues/15)
- chrome 16.0.912.41 beta return code 400 [\#11](https://github.com/Lawouach/WebSocket-for-Python/issues/11)

## [v0.1.5](https://github.com/Lawouach/WebSocket-for-Python/tree/v0.1.5) (2011-12-15)
[Full Changelog](https://github.com/Lawouach/WebSocket-for-Python/compare/v0.1.4...v0.1.5)

**Closed issues:**

- Bad code for binary send in client/\_\_init\_\_.py ?? [\#14](https://github.com/Lawouach/WebSocket-for-Python/issues/14)
- Server not handling "Upgrade" header case-insensitively, as it should [\#13](https://github.com/Lawouach/WebSocket-for-Python/issues/13)

**Merged pull requests:**

- support for wss:// connections using ssl.wrap\_socket [\#12](https://github.com/Lawouach/WebSocket-for-Python/pull/12) ([EliAndrewC](https://github.com/EliAndrewC))

## [v0.1.4](https://github.com/Lawouach/WebSocket-for-Python/tree/v0.1.4) (2011-11-12)
[Full Changelog](https://github.com/Lawouach/WebSocket-for-Python/compare/v0.1.3...v0.1.4)

**Closed issues:**

- Handle Connection: keep-alive, Upgrade header from Firefox 7.0 [\#3](https://github.com/Lawouach/WebSocket-for-Python/issues/3)

**Merged pull requests:**

- Hello, I had to make some minor changes to get the echo server to work for me. Thank for the excellent work. I am looking forward to incorporating it into my site :\). Regards, Derrick [\#10](https://github.com/Lawouach/WebSocket-for-Python/pull/10) ([dpetzold](https://github.com/dpetzold))
- Added io\_loop parameter to TornadoWebSocketClient constructor [\#9](https://github.com/Lawouach/WebSocket-for-Python/pull/9) ([swax](https://github.com/swax))
- Websocket threading client ignores initial data send by the server [\#7](https://github.com/Lawouach/WebSocket-for-Python/pull/7) ([majek](https://github.com/majek))
- Fixed hangup in Tornado implementation [\#6](https://github.com/Lawouach/WebSocket-for-Python/pull/6) ([protoss-player](https://github.com/protoss-player))
- Added a gevent client and fixed a major flaw in the gevent/"wsgi" server handler [\#5](https://github.com/Lawouach/WebSocket-for-Python/pull/5) ([progrium](https://github.com/progrium))
- Some JSON functionality [\#4](https://github.com/Lawouach/WebSocket-for-Python/pull/4) ([protoss-player](https://github.com/protoss-player))

## [v0.1.3](https://github.com/Lawouach/WebSocket-for-Python/tree/v0.1.3) (2011-09-07)
[Full Changelog](https://github.com/Lawouach/WebSocket-for-Python/compare/v0.1.2...v0.1.3)

**Merged pull requests:**

- Made it more generic, fixed some bugs, cleaned things up [\#2](https://github.com/Lawouach/WebSocket-for-Python/pull/2) ([progrium](https://github.com/progrium))

## [v0.1.2](https://github.com/Lawouach/WebSocket-for-Python/tree/v0.1.2) (2011-08-23)
[Full Changelog](https://github.com/Lawouach/WebSocket-for-Python/compare/v0.1.1...v0.1.2)

**Merged pull requests:**

- gevent server implementation [\#1](https://github.com/Lawouach/WebSocket-for-Python/pull/1) ([progrium](https://github.com/progrium))

## [v0.1.1](https://github.com/Lawouach/WebSocket-for-Python/tree/v0.1.1) (2011-08-21)


\* *This Change Log was automatically generated by [github_changelog_generator](https://github.com/skywinder/Github-Changelog-Generator)*