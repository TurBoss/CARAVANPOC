from util import *


def basicDecompression(self, rom, source, addr):
    
    done = False
    reader = addr
    pixels = ""
    raw_bytes = ""
    commands = {}
    
    if type(source) == type(""):
        func = lambda pos, num: source[pos*2:pos*2+num*2]
    else:
        func = rom.getBytes
    
    shown = False
    
    while not done:
        
        raw_barrel = func(reader, 2)
        raw_bytes += raw_barrel + ": "
        barrel = "".join([bin(int(c, 16), 4) for c in raw_barrel])
        reader += 2
        
        for com in barrel:
            
            operand = func(reader, 2)
                
            raw_bytes += operand + " "
            
            reader += 2
            
            if com == "1":
                
                if operand == "0000":
                    done = True
                    break
                
                else:
                    
                    repeat = int(operand, 16) & 0x1F
                    offset = (int(operand, 16) - repeat) / 16
                    repeat = 33 - repeat
                    
                    commands[len(pixels)] = [len(pixels) - (offset*2), repeat]
                    
                    if repeat % 2:
                        
                        idx = -offset*2
                        if idx == -4:
                            pixels += pixels[idx:]
                        else:
                            pixels += pixels[idx:idx+4]
                    
                    repeat /= 2
                    
                    start = len(pixels)
                    
                    for iter in range(repeat):
                        idx = -offset*2
                        if idx == -4:
                            pixels += pixels[idx:]*2
                            
                        elif idx == -8:
                            pixels += pixels[idx:]
                        else:
                            pixels += pixels[idx:idx+8]
                    
                    #print "%i, %i->%i: %s" % (repeat, start, len(pixels), pixels[start:])
                    
                    if not shown and len(pixels) > (24*24):
                        ##print "\n".join(pixels[p:p+24] for p in range(0, 24*24, 24))
                        #raw_input()
                        shown = True
                            
            else:
                #print "add, %i->%i: %s" % (len(pixels), len(pixels)+4, operand)
                pixels += operand
    
        raw_bytes += "\n"
        
    #print `24*24*2`
    
    return pixels, raw_bytes
    
# ----------------------------

def stackDecompression(self, rom, source, addr=0):
    
    done = False
    reader = addr
    pixels = ""
    raw_bytes = ""
    offset_strings = []
    
    cmd_str = ""
    
    barrel = ""
    
    if type(source) == type(""):
        func = lambda pos, num: source[pos*2:pos*2+num*2]
    else:
        func = rom.getBytes
    
    pixel_stack = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f"]
    
    tile_ctr = 0
    
    #print "------------------------"
    #print "AT " + hex(addr)
    #print "------------------------"

    tile_command = ""
    pixel_barrel = ""
        
    pixels = ""
    raw_pixels = ""
    
    while not done:
        
        command = ""
        cmd_ctr = 4
        
        tile_barrel = ""
        
        while cmd_ctr > 0:
            
            if not barrel:
                
                raw_barrel = func(reader, 2)
                raw_bytes += raw_barrel + " "
                barrel = "".join([bin(int(c, 16), 4) for c in raw_barrel])
                reader += 2
            
                #print "New barrel: " + hex(reader) + " - " + raw_barrel + " - (" + command + ")" + barrel
            
            for bit in barrel:
                
                command += bit
                barrel = barrel[1:]
                
                if command == "0":
                    tile_barrel += "0"
                
                elif command.startswith("10") and len(command) == 3:
                    tile_barrel += str(int(command[2]) + 1)
                    command = command[:2] + " " + command[2:]
                
                elif command == "110":
                    tile_barrel += "4"
                
                elif command == "1110":
                    tile_barrel += "8"
                
                elif command.startswith("1111") and len(command) == 8:
                    tile_barrel += hex(int(command[4:], 2))[2:]
                    command = command[:4] + " " + command[4:]
                
                else:
                    continue
                    
                cmd_str += tile_barrel[-1] + ": " + command + "\n"
                cmd_ctr -= 1
                #print command
                command = ""
                
                if cmd_ctr == 0:
                    cmd_str += "TILE: " + tile_barrel + "\n\n"
                    break
        
        tile_barrel = "".join([bin(int(c, 16), 4) for c in tile_barrel])
        
        for tile_bit in tile_barrel:
            
            cmd_ctr = 4
            pixel_barrel = ""
            
            if tile_bit == "0":
                
                #print "Literal pixels:"
                
                while cmd_ctr > 0:
                    
                    if not barrel:
                        
                        raw_barrel = func(reader, 2)
                        raw_bytes += raw_barrel + " "
                        barrel = "".join([bin(int(c, 16), 4) for c in raw_barrel])
                        reader += 2
                        
                        #print "New barrel: " + hex(reader) + " - " + raw_barrel + " - (" + command + ")" + barrel
                    
                    for bit in barrel:
                        
                        command += bit
                        barrel = barrel[1:]
                        
                        if command == "00":
                            pass
                        
                        elif command == "01":
                            pixel_stack.insert(0, pixel_stack.pop(1))
                            
                        elif command == "100":
                            pixel_stack.insert(0, pixel_stack.pop(2))
                            
                        elif command == "101":
                            pixel_stack.insert(0, pixel_stack.pop(3))
                        
                        elif command == "110":
                            pixel_stack.insert(0, pixel_stack.pop(4))
                        
                        elif command.startswith("111") and (len(command) == 10 or (len(command)%2 == 1 and command.find("0") != -1)):
                            offset = "".join([command[s] for s in range(len(command)-1, 2, -1)]).zfill(7)
                            val = 0
                            tog = 0
                            for i in offset[1:]:
                                val += int(i) * (tog+1)
                                tog ^= 1
                            val += 5
                            val += int(offset[0])
                            #print "BAK: " + offset + ",   VAL: " + `val`
                            pixel_stack.insert(0, pixel_stack.pop(val))
                            command = command[:3] + " " + command[3:]
                        
                        else:
                            continue
                            
                        pixel_barrel += pixel_stack[0]
                        cmd_str += pixel_barrel[-1] + ": " + command + "\n"
                        cmd_ctr -= 1
                        #print command
                        command = ""
                        
                        if cmd_ctr == 0:
                            #print "THESE: " + pixel_barrel
                            #print "STACK: " + `pixel_stack`
                            cmd_str += "PIXELS: " + pixel_barrel + "\n\n"
                            break                    
                
                pixels += pixel_barrel
                raw_pixels += pixel_barrel
                
            else:
                
                #print "Copy section:"

                ctr = 11
                offset = ""
                
                while ctr > 0:
                    
                    if not barrel:
                        
                        raw_barrel = func(reader, 2)
                        
                        #print "New barrel: " + hex(reader) + " - " + raw_barrel + " - " + barrel
                        
                        raw_bytes += raw_barrel + " "
                        barrel = "".join([bin(int(c, 16), 4) for c in raw_barrel])
                        reader += 2
                        
                    offset += barrel[0]
                    barrel = barrel[1:]
                    ctr -= 1
                
                real_offset = int(offset, 2)*4
                total = 0
                bit = "0"
                
                #print "  Offset: " + offset + ", go back " + `real_offset` + " pixels"
                
                if real_offset == 0:
                    
                    #print "!!! THIS MEANS WE'RE DONE !!!"
                    done = True
                    #raw_input()
                    break
                
                start = len(raw_pixels)
                
                while bit == "0":

                    if not barrel:
                        
                        raw_barrel = func(reader, 2)
                        raw_bytes += raw_barrel + " "
                        barrel = "".join([bin(int(c, 16), 4) for c in raw_barrel])
                        reader += 2
                        
                        #print "New barrel: " + hex(reader) + " - " + raw_barrel + " - " + barrel
                    
                    if real_offset == 4:
                        pixels += raw_pixels[-real_offset:]
                        raw_pixels += raw_pixels[-real_offset:]
                    else:
                        pixels += raw_pixels[-real_offset:-real_offset+4]
                        raw_pixels += raw_pixels[-real_offset:-real_offset+4]
                    
                    total += 1
                    bit = barrel[0]
                    barrel = barrel[1:]
                    
                if real_offset == 4:
                    pixels += raw_pixels[-real_offset:]
                    raw_pixels += raw_pixels[-real_offset:]
                else:
                    pixels += raw_pixels[-real_offset:-real_offset+4]
                    raw_pixels += raw_pixels[-real_offset:-real_offset+4]
                
                offset_strings.append((real_offset/2, total+1, " ".join([raw_pixels[i:i+4] for i in range(start, len(raw_pixels), 4)])+" ", offset))
                #print "  Copied 4-pixel chunk " + `total+1` + " times."
            
            #print "PIXELS:\n" + "\n".join([pixels[i:i+8] for i in range(0, len(pixels), 8)])
            
            #print ""
            
            #print `len(pixels)`
            """for p in range(len(pixels)/64):
                #print "Making tile %i... (%s)" % (tile_ctr, hex(0x3000 + tile_ctr*0x20))
                tile = data.Tile(name="Tile %i" % tile_ctr)
                tile.init([pixels[i:i+8] for i in range(0, 64, 8)])
                tile.raw_pixels = pixels[:64]
                pixels = pixels[64:]
                tileset.tiles.append(tile)
                tile_ctr += 1"""
                
                #raw_input()
            
            #raw_input()

        #print "Tile barrel over, getting a new one."
        
    #print "PIXELS:\n" + "\n".join([pixels[i:i+8] for i in range(0, len(pixels), 8)])
    
    #print ""
    
    return pixels, raw_bytes