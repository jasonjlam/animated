import mdl
from display import *
from matrix import *
from draw import *

"""======== first_pass( commands ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)

  Should set num_frames and basename if the frames
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.
  ==================== """
def first_pass( commands ):

    name = ''
    num_frames = 1

    return (name, num_frames)

"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value.
  ===================="""
def second_pass( commands, num_frames ):
    frames = [ {} for i in range(num_frames) ]

    return frames


def run(filename):
    i = 0
    """
    This function runs an mdl script
    """
    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print("Parsing failed.")
        return

    view = [0,
            0,
            1];
    ambient = [50,
               50,
               50]
    light = [[0.5,
              0.75,
              1],
             [255,
              255,
              255]]

    color = [0, 0, 0]
    symbols['.white'] = ['constants',
                         {'red': [0.2, 0.5, 0.5],
                          'green': [0.2, 0.5, 0.5],
                          'blue': [0.2, 0.5, 0.5]}]
    reflect = '.white'

    tmp = new_matrix()
    ident( tmp )

    stack = [ [x[:] for x in tmp] ]
    screen = new_screen()
    zbuffer = new_zbuffer()
    tmp = []
    step_3d = 100
    consts = ''
    coords = []
    coords1 = []
    frames = 1
    basename = ''
    vary = 0
    knobs = []
    print("First passthrough:")
    for command in commands:
        print(command)
        c = command['op']
        args = command['args']
        if c == 'frames':
            frames = int(args[0])
        elif c == 'basename':
            basename = args[0]
        elif (c == 'vary'):
            vary = 1
    if (vary == 1 and frames == 1):
        print("No frames set! Please set a number of frames next time.")
        return
    elif (frames > 0 and basename == ""):
        print ("Setting default basename.")
        basename = "image"
    for frame in range(frames):
        knobs.append({})
    print ("Second passthrough:")
    for command in commands:
        print(command)
        c = command['op']
        args = command['args']
        if c == 'vary':
            knob = command['knob']
            print(args)
            value = args[2]
            # for frame in range(int(args[0])):
            #     knobs[frame][knob] = value
            for frame in range(int(args[0]), int(args[1]) + 1):
                i = 0
                increment = (args[3] - args[2]) / (args[1] - args[0] + 1)
                print("Increment:{}".format(increment))
                value += increment
                print("Value:{}".format(value))
                knobs[frame][knob] = value
                i+=1
            # for frame in range(int(args[1]) + 1, frames):
            #     knobs[frame][knob] = args[3]
    print(knobs)
    print ("Third passthrough:")
    for frame in range(frames):
        print("Generating frame{}".format(frame))
        for key, value in knobs[frame].items():
            symbols[key] = value
        for command in commands:
            print(command)
            print(i)
            i +=1
            c = command['op']
            args = command['args']
            knobValue = 1
            if 'knob' in command:
                knob = command['knob']
                if knob != None:
                    knobValue = symbols[knob]
            print ("knobValue{}".format(knobValue))
            print(args)
            if c == 'box':
                if command['constants']:
                    reflect = command['constants']
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'sphere':
                if command['constants']:
                    reflect = command['constants']
                add_sphere(tmp,
                           args[0], args[1], args[2], args[3], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'torus':
                if command['constants']:
                    reflect = command['constants']
                add_torus(tmp,
                          args[0], args[1], args[2], args[3], args[4], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'line':
                add_edge(tmp,
                         args[0], args[1], args[2], args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_lines(tmp, screen, zbuffer, color)
                tmp = []
            elif c == 'move':
                tmp = make_translate(args[0] * knobValue, args[1] * knobValue, args[2] * knobValue)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'scale':
                tmp = make_scale(args[0] * knobValue, args[1] * knobValue, args[2] * knobValue)
                print(tmp)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                theta = args[1] * knobValue * (math.pi/180)
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []

            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()

            elif c == 'display':
                display(screen)
            elif c == 'save':
                save_extension(screen, args[0])


        if frames > 1:
            save_extension(screen, "anim/" + basename + "%03d"%frame + ".png")
        tmp = new_matrix()
        ident( tmp )

        stack = [ [x[:] for x in tmp] ]
        screen = new_screen()
        zbuffer = new_zbuffer()
        tmp = []
        # end operation loop
    make_animation(basename)
