import json

def api_to_map(data):
    res = ""
    max_x = 0
    max_y = 0
    for entry in data['map']:
        tourn,id,x,y,w,h = entry
        res += """    <rect x="{x}" y="{y}" width="{w}" height="{h}" id="{tourn}-{id}"/>\n""".format(x=x, y=y, w=w-0.05, h=h-0.05, tourn=tourn, id=id)
        max_x = max(max_x, x+w)
        max_y = max(max_y, y+h)
        #res += """<text fill="#ffffff" x="{x}" y="{y}" dominant-baseline="middle" text-anchor="middle" font-size="0.4" id="{tourn}-{id}-text"></text>""".format(x=x+ 0.5*w, y=y+0.5*h, tourn=tourn, id=id)
    res += "</svg>\n"
    res = """<svg id="insalan_netmap" viewBox="0 0 {x} {y}" xmlns="http://www.w3.org/2000/svg">\n""".format(x=max_x, y=max_y) + res
    return res