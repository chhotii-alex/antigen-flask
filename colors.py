
def convertToRGB(hexstr):
    r = int(hexstr[1:3], 16)
    g = int(hexstr[3:5], 16)
    b = int(hexstr[5:7], 16)
    return "rgb(%d,%d,%d)" % (r, g, b)

def convertColors(d):
    pos = convertToRGB(d["positives"])
    neg = convertToRGB(d["negatives"])
    med = convertToRGB(d["medium"])
    return {
        "positives" : [pos, pos],
        "negatives" : [neg, neg],
        "count" : [neg, med],
    }

colorPairs = [
    {"negatives": '#6a3d9a', #dark purple
     "positives": '#cab2d6', #light purple
     "medium": "#8B6FB0",
     },
    {"negatives": '#1f78b4', #dark blue
     "positives": '#a6cee3', #light blue
     "medium": "#6D99C3",
     },
    {"negatives": '#33a02c', #dark green
    "positives": '#b2df8a', #light green
     "medium": "#7FB66F",
     },
    {"negatives": '#d8ac60', #dark yellow
     "positives": '#ffff99', #light yellow
     "medium": "#DDC291",
     },
    {"negatives": '#ff7f00', #dark orange
     "positives": '#fdbf6f', #light orange
     "medium": "#FF9F40",
    },
    {"negatives": '#e31a1c', #dark red
     "positives": '#fb9a99', #light red
     "medium": "#EA5455",
     },
]

colorPairs = [convertColors(p) for p in colorPairs[::-1]]

def getColorSchema(index):
    return colorPairs[index % len(colorPairs)]

black = "rgb(0,0,0)"

def getPlainColors():
    return {"positives" : [black, black],
            "negatives" : [black, black],
            }



