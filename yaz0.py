

## Implementation of a yaz0 decoder/encoder in Python, by Yoshi2
## Using the specifications in http://www.amnoid.de/gc/yaz0.txt

import struct
import os
import re
import hashlib
import math

from timeit import default_timer as time
from io import BytesIO
from cStringIO import StringIO

class yaz0():
    def __init__(self, inputobj, outputobj = None, compress = False):
        
        self.compressFlag = compress
        self.fileobj = inputobj
        
        if outputobj == None:
            self.output = StringIO()
        else:
            self.output = outputobj
        
        # A way to discover the total size of the input data that
        # should be compatible with most file-like objects.
        self.fileobj.seek(0, 2)
        self.maxsize = self.fileobj.tell()
        self.fileobj.seek(0)
        
        
        if self.compressFlag == False:
            self.header = fileobj.read(4)
            if self.header != "Yaz0":
                raise RuntimeError("File is not Yaz0-compressed! Header: {0}".format(self.header))
            
            self.decompressedSize = struct.unpack(">I", fileobj.read(4))[0]
            nothing = fileobj.read(8) # Unused data
        
        else:
            self.output.write("Yaz0")
            
            self.output.write(struct.pack(">I", self.maxsize))
            self.output.write(chr(0x00)*8)
        
    def decompress(self):
        if self.compressFlag:
            raise RuntimeError("Compress flag is set, uncompress is not possible.")
        
        fileobj = self.fileobj
        output = self.output
        
        while output.tell() < self.decompressedSize:
            # The codebyte tells us what we need to do for the next 8 steps.
            codeByte = ord(fileobj.read(1))
            
            if fileobj.tell() >= self.maxsize:
                # We have reached the end of the compressed file, but the amount
                # of written data does not match the decompressed size.
                # This is generally a sign of the compressed file being invalid.
                raise RuntimeError("The end of file has been reached."
                                   "{0} bytes out of {1} written.".format(output.tell(), self.decompressedSize))
            
            for bit in self.__bit_iter__(codeByte):
                if bit:
                    ## The bit is set to 1, we do not need to decompress anything. 
                    ## Write the data to the output.
                    byte = fileobj.read(1)
                    if output.tell() < self.decompressedSize:
                        output.write(byte)
                    else:
                        print (
                               "Decompressed size already reached. "
                               "Disregarding Byte {0}, ascii: [{1}]".format(hex(ord(byte)), byte)
                               )
                    
                else:
                    ## Time to work some decompression magic. The next two bytes will tell us
                    ## where we find the data to be copied and how much data it is.
                    byte1 = ord(fileobj.read(1))
                    byte2 = ord(fileobj.read(1))
                    
                    byteCount = byte1 >> 4
                    byte1_lowerNibble = byte1 & 0xF
                    
                    if byteCount == 0:
                        # We need to read a third byte which tells us 
                        # how much data we have to read.
                        byte3 = ord(fileobj.read(1))
                       
                        byteCount = byte3 + 0x12
                    else:
                        byteCount += 2
                        
                    moveDistance = ((byte1_lowerNibble << 8) | byte2)
                    
                    normalPosition = output.tell()
                    moveTo = normalPosition-(moveDistance+1)
                    
                    if moveTo < 0: 
                        raise RuntimeError("Invalid Seek Position: Trying to move from "
                                           "{0} to {1} (MoveDistance: {2}".format(normalPosition, moveTo,
                                                                                  moveDistance+1))
                        
                    # We move back to a position that has the data we will copy to the front.
                    output.seek(moveTo)
                    toCopy = output.read(byteCount)
                    
                    
                    
                    if len(toCopy) < byteCount:
                        # The data we have read is less than what we should read, 
                        # so we will pad he rest with 0x00. 
                        # Hard to tell if this is the correct way to do it,
                        # but it seems to be working.
                        toCopy = toCopy.ljust(byteCount, chr(0x00))
                        
                    #print "Copying: '{0}', {1} bytes at position {2}".format(toCopy, byteCount, moveTo)
                    
                    
                    output.seek(normalPosition)
                    
                    if self.decompressedSize - normalPosition < byteCount:
                        diff = self.decompressedSize - normalPosition
                        oldCopy = map(hex, map(ord, toCopy))
                        print ("Difference between current position and "
                               "decompressed size is smaller than the length "
                               "of the current string to be copied.")
                        if diff < 0:
                            raise RuntimeError("We are already past the compressed size, "
                                               "this shouldn't happen! Uncompressed Size: {0}, "
                                               "current position: {1}.".format(self.decompressedSize,
                                                                               normalPosition))
                        elif diff == 0:
                            toCopy = ""
                            print ("toCopy string (content: '{0}') has been cleared because "
                                   "current position is close to decompressed size.".format(oldCopy))
                        else:
                            toCopy = toCopy[:diff]
                            print len(toCopy), diff
                            print ("toCopy string (content: '{0}') has been shortened to {1} byte/s "
                                   "because current position is close to decompressed size.".format(oldCopy,
                                                                                                    diff))
                        
                    
                    output.write(toCopy)
                       
                    
        print "Done!", codeByte
        print "Check the output position and uncompressed size (should be the same):"
        print "OutputPos: {0}, uncompressed Size: {1}".format(output.tell(), self.decompressedSize)
        
        return output
    
    
    # To do: 
    # 1) Optimization
    # 2) Better compression
    # 3) Testing under real conditions 
    #    (e.g. replace a file in a game with a file compressed with this method)
    def compress(self, compressLevel = 0, advanced = False):
        if not self.compressFlag:
            raise RuntimeError("Trying to compress, but compress flag is not set."
                               "Create yaz0 object with compress = True as one of its arguments.")
        
        if compressLevel >= 10 or compressLevel < 0:
            raise RuntimeError("CompressionLevel is limited to 0-9.")
        
        fileobj = self.fileobj
        output = self.output
        maxsize = self.maxsize
        
        # compressLevel can be one of the values from 0 to 9.
        # It will reduce the area in which the method will look
        # for matches and speed up compression slightly.
        compressRatio = (1/10.0) * (compressLevel+1)
        maxSearch = 2**12 - 1
        adjustedSearch = int(maxSearch*compressRatio)
        adjustedMaxBytes = int(math.ceil(15*compressRatio+2))
        
        # The advanced flag will allow the use of a third byte,
        # enabling the method to look for matches that are up to 
        # 256 bytes long. NOT IMPLEMENTED YET
        
        if advanced == False:
            while fileobj.tell() < maxsize:
                buffer = StringIO()
                codeByte = 0
                
                # Compressing data near the end can be troublesome, so we will just read the data
                # and write it uncompressed. Alternatively, checks can be added to
                # the code further down, but that requires more work and testing.
                #if maxsize - fileobj.tell() <= 17*8:
                #    print "Left: {0} bytes".format(maxsize - fileobj.tell())
                #    leftover = fileobj.read(8).ljust(8,chr(0x00))
                #    codeByte = 0xFF
                #    buffer.write(leftover) 
                    
                    
                #else:
                for i in range(8):
                    # 15 bytes can be stored in a nibble. The decompressor will
                    # read 15+2 bytes, possibly to account for the way compression works.
                    maxBytes = adjustedMaxBytes
                    
                    # Store the current file pointer for reference.
                    currentPos = fileobj.tell()
                    
                    # Adjust maxBytes if we are close to the end.
                    if maxsize - currentPos < maxBytes:
                        maxBytes = maxsize - currentPos
                        print "Maxbytes adjusted to", maxBytes
                    
                    # Calculate the starting position for the search
                    searchPos = currentPos-adjustedSearch
                    
                    # Should the starting position be negative, it will be set to 0.
                    # We will also adjust how much we need to read.
                    if searchPos < 0:
                        searchPos = 0
                        realSearch = currentPos
                    else:
                        realSearch = adjustedSearch
                    
                    # toSearch will be the string (up to 2**12 long) in which
                    # we will search for matches of the pattern.
                    pattern = fileobj.read(maxBytes)
                    fileobj.seek(searchPos)
                    toSearch = fileobj.read(realSearch)
                    fileobj.seek(currentPos + len(pattern))
                    
                    index = toSearch.rfind(pattern)
                    
                    # If a match hasn't been found, we will start a loop in which we
                    # will steadily reduce the length of the pattern, increasing the chance
                    # of finding a matching string. The pattern needs to be at least 3 bytes
                    # long, otherwise there is no point in trying to compress it.
                    # (The algorithm uses at least 2 bytes to represent such patterns)
                    while index == -1 and maxBytes > 3:
                        fileobj.seek(currentPos)
                        
                        maxBytes -= 1
                        pattern = fileobj.read(maxBytes)
                        
                        if len(pattern) < maxBytes:
                            maxBytes = len(pattern) 
                            print "adjusted pattern length"
                            
                        index = toSearch.rfind(pattern)
                    
                    if index == -1 or maxBytes <= 2:
                        # No match found. Read a byte and append it to the buffer directly.
                        fileobj.seek(currentPos)
                        byte = fileobj.read(1)
                        
                        # At the end of the file, read() will return an empty string.
                        # In that case we will set the byte to the 0 character.
                        # Hopefully, a decompressor will check the uncompressed size
                        # of the file and remove any padding bytes past this position.
                        if len(byte) == 0:
                            #print "Adding padding"
                            byte = chr(0x00)
                        
                        buffer.write(byte)
                        
                        # Mark the bit in the codebyte as 1.
                        codeByte = (1 << (7-i)) | codeByte
                        
                    else:
                        # A match has been found, we need to calculate its index relative to
                        # the current position. (RealSearch stores the total size of the search string,
                        # while the index variable holds the position of the pattern in the search string)
                        relativeIndex = realSearch - index 
                        
                        # Create the two descriptor bytes which hold the length of the pattern and
                        # its index relative to the current position.
                        # Marking the bit in the codebyte as 0 isn't necessary, it will be 0 by default.
                        byte1, byte2 = self.__build_byte__(maxBytes-2, relativeIndex-1)
                        
                        buffer.write(chr(byte1))
                        buffer.write(chr(byte2))
            
                # Now that everything is done, we will append the code byte and
                # our compressed data from the buffer to the output.
                output.write(chr(codeByte))
                output.write(buffer.getvalue())
        else:
            raise RuntimeError("Advanced compression not implemented yet.")
        
        return output
                    
    def __build_byte__(self, byteCount, position):
        if position >= 2**12:
            raise RuntimeError("{0} is outside of the range for 12 bits!".format(position))
        if byteCount > 0xF:
            raise RuntimeError("{0} is too much for 4 bits.".format(byteCount))
        
        positionNibble = position >> 8
        positionByte = position & 0xFF
        
        byte1 = (byteCount << 4) | positionNibble
        
        return byte1, positionByte
        
        
    # A simple iterator for iterating over the bits of a single byte
    def __bit_iter__(self, byte):
        for i in xrange(8):
            result = (byte << i) & 0x80
            yield result != 0
    

if __name__ == "__main__":
    compress = True
        
    if not compress:
        fileobj = open("compressed.dat", "rb")
        yazObj = yaz0(fileobj)
        output = yazObj.decompress()
        fileobj.close()
        
        writefile = open("decompressed.dat", "wb")
        writefile.write(output.getvalue())
        writefile.close()
        
    else:
        start = time()
        fileobj = open("decompressed.dat", "rb")
        yazObj = yaz0(fileobj, compress = True)
        output = yazObj.compress(compressLevel = 9)
        fileobj.close()
        
        writefile = open("compressed.dat", "wb")
        writefile.write(output.getvalue())
        writefile.close()
        
        print "Time taken: {0} seconds".format(time()-start)
        