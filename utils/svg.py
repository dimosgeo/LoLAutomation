import io
import lxml.etree as ET
from matplotlib import use as mplot_use
mplot_use('svg')
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Polygon, Ellipse


class SVG:
    def __init__(self, tree):
        self.tree = ET.fromstring(tree)
        self.viewbox = [0, 0, 0, 0]
        self.paths = []
        self.make_paths()

    def parse_path_tag(self, data, fill='#000000', border='None'):
        codes = []
        vertices = []
        d = ''
        last_pos = [(0, 0)]
        last_bezier = None

        if 'fill' in data:
            fill = data['fill']
        elif 'style' in data:
            style = data['style'].split(';')
            style.remove('')
            for s in style:
                if 'fill' in s:
                    fill = s.split(':')[-1]
                    break

        if 'stroke' in data:
            border = 'none' if data['stroke'] == 'transparent' else data['stroke']
        paths = data['d']

        for c in paths:
            if c.isalpha():
                d = d.replace(',', ' ')
                d = d.replace('#-', '-')
                d = d.replace('-', ' -')
                d = d.replace('#', ' ').strip()
                d = d.split()
                if len(d) == 0:
                    d = c + '#'
                    continue
                if d[0] == 'M':
                    codes.append(Path.MOVETO)
                    v = [(float(i), -float(j)) for i, j in zip(d[1::2], d[2::2])]
                    vertices += v
                    last_pos = v[-1]
                elif d[0] == 'm':
                    codes.append(Path.MOVETO)
                    v = [(last_pos[0] + float(i), last_pos[1] - float(j)) for i, j in zip(d[1::2], d[2::2])]
                    vertices += v
                    last_pos = v[-1]
                elif d[0] == 'c':
                    codes += [Path.CURVE4] * 3
                    v = [(float(i) + last_pos[0], -float(j) + last_pos[1]) for i, j in zip(d[1::2], d[2::2])]
                    vertices += v
                    last_pos = v[-1]
                    last_bezier = v[1]
                elif d[0] == 'q':
                    codes += [Path.CURVE3] * 2
                    v = [(float(i) + last_pos[0], -float(j) + last_pos[1]) for i, j in zip(d[1::2], d[2::2])]
                    vertices += v
                    last_pos = v[-1]
                    last_bezier = v[1]
                elif d[0] == 'Q':
                    codes += [Path.CURVE3] * 2
                    v = [(float(i), -float(j)) for i, j in zip(d[1::2], d[2::2])]
                    vertices += v
                    last_pos = v[-1]
                    last_bezier = v[1]
                elif d[0] == 'C':
                    codes += [Path.CURVE4] * 3
                    v = [(float(i), -float(j)) for i, j in zip(d[1::2], d[2::2])]
                    vertices += v
                    last_pos = v[-1]
                    last_bezier = v[1]
                elif d[0] == 'z' or d[0] == 'Z':
                    codes += [Path.CLOSEPOLY]
                    vertices += [last_pos]
                elif d[0] == 'L':
                    codes += [Path.LINETO]
                    v = [(float(i), -float(j)) for i, j in zip(d[1::2], d[2::2])]
                    vertices += v
                    last_pos = v[0]
                elif d[0] == 'l':
                    codes += [Path.LINETO]
                    v = [(last_pos[0] + float(i), last_pos[1] - float(j)) for i, j in zip(d[1::2], d[2::2])]
                    vertices += v
                    last_pos = v[0]
                elif d[0] == 'v':
                    codes += [Path.LINETO]
                    v = [(last_pos[0], last_pos[1] - float(d[1]))]
                    vertices += v
                    last_pos = v[0]
                elif d[0] == 'h':
                    codes += [Path.LINETO]
                    v = [(last_pos[0] + float(d[1]), last_pos[1])]
                    vertices += v
                    last_pos = v[0]
                elif d[0] == 'H':
                    codes += [Path.LINETO]
                    v = [(float(d[1]), last_pos[1])]
                    vertices += v
                    last_pos = v[0]
                elif d[0] == 'V':
                    codes += [Path.LINETO]
                    v = [(last_pos[0], -float(d[1]))]
                    vertices += v
                    last_pos = v[0]
                elif d[0] == 'S':
                    codes += [Path.CURVE4] * 3
                    v = [(float(i), -float(j)) for i, j in zip(d[1::2], d[2::2])]
                    v = [(2 * last_pos[0] - last_bezier[0], 2 * last_pos[1] - last_bezier[1])] + v
                    vertices += v
                    last_pos = v[-1]
                    last_bezier = v[1]
                elif d[0] == 's':
                    codes += [Path.CURVE4] * 3
                    v = [(last_pos[0] + float(i), last_pos[1] - float(j)) for i, j in zip(d[1::2], d[2::2])]
                    v = [(2 * last_pos[0] - last_bezier[0], 2 * last_pos[1] - last_bezier[1])] + v
                    vertices += v
                    last_pos = v[-1]
                    last_bezier = v[1]
                elif d[0] == 't':
                    codes += [Path.CURVE3] * 2
                    v = [(last_pos[0] + float(i), last_pos[1] - float(j)) for i, j in zip(d[1::2], d[2::2])]
                    v = [(2 * last_pos[0] - last_bezier[0], 2 * last_pos[1] - last_bezier[1])] + v
                    vertices += v
                    last_pos = v[-1]
                    last_bezier = v[1]
                elif d[0] == 'Τ':
                    codes += [Path.CURVE3] * 2
                    v = [(float(i), -float(j)) for i, j in zip(d[1::2], d[2::2])]
                    v = [(2 * last_pos[0] - last_bezier[0], 2 * last_pos[1] - last_bezier[1])] + v
                    vertices += v
                    last_pos = v[-1]
                    last_bezier = v[1]

                elif d[0] == 'A':
                    codes += [Path.MOVETO]
                    v = [float(i) for i in d[1:]]
                    v[-1] = -v[-1]
                    # NOT IMPLEMENTED
                    last_pos = (v[-2], v[-1])
                    vertices += [last_pos]
                else:
                    print(d[0])
                d = c + '#'
            else:
                d += c

        patch = PathPatch(Path(codes=codes, vertices=vertices), facecolor=fill, edgecolor=border)
        if 'stroke-width' in data:
            patch.set_linewidth(float(data['stroke-width']))
        self.paths.append(patch)

    def parse_poly(self, data, fill='#000000', border='#000000'):
        if 'fill' in data:
            fill = data['fill']
        elif 'style' in data:
            style = data['style'].split(';')
            style.remove('')
            for s in style:
                if 'fill' in s:
                    fill = s.split(':')[-1]
                    break

        if 'stroke' in data:
            border = 'none' if data['stroke'] == 'transparent' else data['stroke']

        data = data['points'].replace(' ', ',').split(',')
        self.paths.append(Polygon([(float(i), -float(j)) for i, j in zip(data[0::2], data[1::2])], closed=True, facecolor=fill, edgecolor=border))

    def parse_ellipse(self, data, fill='#000000', border='#000000'):
        cx = float(data['cx'])
        cy = -float(data['cy'])
        rx = float(data['rx'])
        ry = float(data['ry'])

        if 'fill' in data:
            fill = data['fill']

        if 'stroke' in data:
            border = 'none' if data['stroke'] == 'transparent' else data['stroke']

        self.paths.append(Ellipse((cx, cy), 2 * ry, 2 * rx, angle=-90, fill=True, facecolor=fill, edgecolor=border))

    def make_paths(self):
        data = list(self.tree)

        fill = '#000000'
        if 'fill' in self.tree.attrib:
            fill = self.tree.attrib['fill']

        for element in data:
            if element.tag == f'{{{self.tree.nsmap[None]}}}path':
                self.parse_path_tag(element.attrib, fill)
            if element.tag == f'{{{self.tree.nsmap[None]}}}polygon':
                self.parse_poly(element.attrib, fill)

            if element.tag == f'{{{self.tree.nsmap[None]}}}ellipse':
                self.parse_ellipse(element.attrib, fill)

        if 'viewBox' in self.tree.attrib:
            self.viewbox = [float(i) for i in self.tree.attrib.get('viewBox').split()]
        elif 'width' in self.tree.attrib and 'height' in self.tree.attrib:
            self.viewbox[2] = float(self.tree.attrib['width'])
            self.viewbox[3] = float(self.tree.attrib['height'])
    
    def set(self, **args):
        for path in self.paths:
            path.set(**args)

    @property
    def buffer(self, transparent=True, image_format='png'):
        fig, ax = plt.subplots()
        for path in self.paths:
            ax.add_patch(path)
        ax.set_aspect('equal')

        plt.xlim([self.viewbox[0], self.viewbox[2]])
        plt.ylim([-self.viewbox[3], self.viewbox[1]])
        plt.axis('off')
        img_buf = io.BytesIO()
        plt.savefig(img_buf, bbox_inches='tight', transparent=transparent, format=image_format)

        return img_buf
