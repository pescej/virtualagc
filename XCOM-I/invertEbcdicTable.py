#!/usr/bin/env python3
# This is a throwaway program that creates the inverse of the `asciiToEbcdic`
# array found in the file runtimeC.c.

asciiToEbcdic = [
  0x00, 0x01, 0x02, 0x03, 0x37, 0x2d, 0x2e, 0x2f,
  0x16, 0x05, 0x25, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f,
  0x10, 0x11, 0x12, 0x13, 0x3c, 0x3d, 0x32, 0x26, #              */
  0x18, 0x19, 0x3f, 0x27, 0x1c, 0x1d, 0x1e, 0x1f, #              */
  0x40, 0x5A, 0x7F, 0x7B, 0x5B, 0x6C, 0x50, 0x7D, #  !"#$%&'     */
  0x4D, 0x5D, 0x5C, 0x4E, 0x6B, 0x60, 0x4B, 0x61, # ()*+,-./     */
  0xF0, 0xF1, 0xF2, 0xF3, 0xF4, 0xF5, 0xF6, 0xF7, # 01234567     */
  0xF8, 0xF9, 0x7A, 0x5E, 0x4C, 0x7E, 0x6E, 0x6F, # 89:;<=>?     */
  0x7C, 0xC1, 0xC2, 0xC3, 0xC4, 0xC5, 0xC6, 0xC7, # @ABCDEFG     */
  0xC8, 0xC9, 0xD1, 0xD2, 0xD3, 0xD4, 0xD5, 0xD6, # HIJKLMNO     */
  0xD7, 0xD8, 0xD9, 0xE2, 0xE3, 0xE4, 0xE5, 0xE6, # PQRSTUVW     */
  0xE7, 0xE8, 0xE9, 0xBA, 0xE0, 0xBB, 0x5F, 0x6D, # XYZ[\]^_     */
  0x4A, 0x81, 0x82, 0x83, 0x84, 0x85, 0x86, 0x87, # `abcdefg     */
  0x88, 0x89, 0x91, 0x92, 0x93, 0x94, 0x95, 0x96, # hijklmno     */
  0x97, 0x98, 0x99, 0xA2, 0xA3, 0xA4, 0xA5, 0xA6, # pqrstuvw     */
  0xA7, 0xA8, 0xA9, 0xC0, 0x4F, 0xD0, 0x5F, 0x07  # xyz{|}~      */
    ]

ebcdicToAscii = [" "] * 256

for i in range(len(asciiToEbcdic)):
    ebcdic = asciiToEbcdic[i]
    if False and chr(i) == "'":
        ebcdicToAscii[ebcdic] = "\\'"
    elif False and chr(i) == '\\':
        ebcdicToAscii[ebcdic] = '\\\\'
    elif False and chr(i).isprintable():
        ebcdicToAscii[ebcdic] = chr(i)
    else:
        if ebcdicToAscii[ebcdic] != " ":
            print("Reused EBCDIC code %02X: %02X %s" % (ebcdic, i, ebcdicToAscii[ebcdic]))
        ebcdicToAscii[ebcdic] = "\\x%02X" % i

print("static char ebcdicToAscii[256] = {\n  ", end="")
for i in range(len(ebcdicToAscii)):
    if i > 0 and i % 8 == 0:
        print("\n  ", end='')
    print("%-6s" % ("'" + ebcdicToAscii[i] + "'"), end="")
    if i != 255:
        print(", ", end="")
print("\n};")

'''
for i in range(256):
    char = ebcdicToAscii[asciiToEbcdic[i]]
    if i != int(char[2:], 16):
        print("Mismatch: %02X %s" % (i, char))
0x20, 0x21, 0x22, 0x23, 0x24, 0x15, 0x06, 0x17, 0x28, 0x29, 0x2a, 0x2b, 0x2c, 0x09, 0x0a, 0x1b,
0x30, 0x31, 0x1a, 0x33, 0x34, 0x35, 0x36, 0x08, 0x38, 0x39, 0x3a, 0x3b, 0x04, 0x14, 0x3e, 0xff,
0x41, 0xaa, 0x4a, 0xb1, 0x9f, 0xb2, 0x6a, 0xb5, 0xbd, 0xb4, 0x9a, 0x8a, 0xb0, 0xca, 0xaf, 0xbc,
0x90, 0x8f, 0xea, 0xfa, 0xbe, 0xa0, 0xb6, 0xb3, 0x9d, 0xda, 0x9b, 0x8b, 0xb7, 0xb8, 0xb9, 0xab,
0x64, 0x65, 0x62, 0x66, 0x63, 0x67, 0x9e, 0x68, 0x74, 0x71, 0x72, 0x73, 0x78, 0x75, 0x76, 0x77,
0xac, 0x69, 0xed, 0xee, 0xeb, 0xef, 0xec, 0xbf, 0x80, 0xfd, 0xfe, 0xfb, 0xfc, 0xad, 0xae, 0x59,
0x44, 0x45, 0x42, 0x46, 0x43, 0x47, 0x9c, 0x48, 0x54, 0x51, 0x52, 0x53, 0x58, 0x55, 0x56, 0x57,
0x8c, 0x49, 0xcd, 0xce, 0xcb, 0xcf, 0xcc, 0xe1, 0x70, 0xdd, 0xde, 0xdb, 0xdc, 0x8d, 0x8e, 0xdf
'''