import pdfplumber, re, csv

pdf = pdfplumber.open('WinsorNewtonOilPaintChart.pdf')
p = pdf.pages[1]
words = p.extract_words()
codes = [w for w in words if re.fullmatch(r'\d{3}', w['text']) and w['top'] < 660]

row_tops_code = [114.41, 246.87, 379.33, 511.79, 644.0]
col_xs = sorted(set(round(w['x0'],1) for w in codes if abs(w['top']-114.41)<1))

def nearest(val, arr):
    return min(range(len(arr)), key=lambda i: abs(arr[i]-val))

grid_code = {}
for w in codes:
    r = nearest(w['top'], row_tops_code)
    c = nearest(w['x0'], col_xs)
    grid_code[(r,c)] = w['text']
print("codes placed", len(grid_code))

cand = [r for r in p.rects if r.get('fill') and 36<round(r['width'],1)<38 and 86<round(r['height'],1)<88]
row_tops_rect = sorted(set(round(r['top'],1) for r in cand))
# cluster row tops (should be ~5 distinct clusters)
row_tops_rect_clustered = []
for t in row_tops_rect:
    if not row_tops_rect_clustered or abs(t-row_tops_rect_clustered[-1])>10:
        row_tops_rect_clustered.append(t)
print("rect row tops", row_tops_rect_clustered)

grid_color = {}
for r in cand:
    ri = nearest(r['top'], row_tops_rect_clustered)
    ci = nearest(r['x0'], col_xs)
    grid_color[(ri,ci)] = r['non_stroking_color']
print("colors placed", len(grid_color))

missing = set(grid_code.keys()) - set(grid_color.keys())
print("missing color for code cells:", missing)

names = {
"111":"Cadmium Yellow Deep","891":"Cadmium-Free Yellow Deep","089":"Cadmium Orange","899":"Cadmium-Free Orange",
"650":"Transparent Orange","416":"Orange Lake Mineral","724":"Winsor Orange","106":"Cadmium Scarlet",
"903":"Cadmium-Free Scarlet","603":"Scarlet Lake","094":"Cadmium Red","901":"Cadmium-Free Red",
"726":"Winsor Red","725":"Winsor Red Deep","347":"Lemon Yellow Hue","025":"Bismuth Yellow",
"722":"Winsor Lemon","086":"Cadmium Lemon","898":"Cadmium-Free Lemon","730":"Winsor Yellow",
"653":"Transparent Yellow","149":"Chrome Yellow Hue","118":"Cadmium Yellow Pale","907":"Cadmium-Free Yellow Pale",
"108":"Cadmium Yellow","890":"Cadmium-Free Yellow","319":"Indian Yellow","731":"Winsor Yellow Deep",
"097":"Cadmium Red Deep","895":"Cadmium-Free Red Deep","257":"Pale Rose Blush","587":"Rose Madder Genuine",
"576":"Rose Dore","042":"Bright Red","548":"Quinacridone Red","004":"Alizarin Crimson",
"479":"Permanent Carmine","468":"Permanent Alizarin Crimson","502":"Permanent Rose","411":"Ruby Madder Alizarin",
"545":"Quinacridone Magenta","380":"Magenta","242":"Flake White Hue","748":"Zinc White",
"674":"Underpainting White (Fast Drying)","644":"Titanium White","429":"Warm White","058":"Bronze",
"214":"Copper","573":"Renaissance Gold","283":"Gold","511":"Pewter",
"617":"Silver","330":"Iridescent White","646":"Transparent Gold Ochre","059":"Brown Ochre",
"074":"Burnt Sienna","647":"Transparent Red Ochre","362":"Light Red","678":"Venetian Red",
"635":"Terra Rosa","657":"Transparent Maroon","317":"Indian Red","395":"Mars Violet Deep",
"413":"Warm Brown Pink","056":"Brown Madder","648":"Transparent Brown Oxide","076":"Burnt Umber",
"489":"Permanent Magenta","669":"Ultramarine Pink","543":"Purple Madder","544":"Purple Lake",
"192":"Cobalt Violet","491":"Permanent Mauve","400":"Mauve Blue Shade","733":"Winsor Violet (Dioxazine)",
"672":"Ultramarine Violet","263":"French Ultramarine","710":"Smalt (Dumont's Blue)","045":"Royal Blue",
"180":"Cobalt Blue Deep","667":"Ultramarine (Green Shade)","178":"Cobalt Blue","321":"Indanthrene Blue",
"414":"Oriental Blue","706":"Winsor Blue (Red Shade)","707":"Winsor Blue (Green Shade)","538":"Prussian Blue",
"137":"Cerulean Blue","379":"Manganese Blue Hue","526":"Phthalo Turquoise","190":"Cobalt Turquoise",
"191":"Cobalt Turquoise Light","184":"Cobalt Green","412":"Mineral Green Deep","183":"Cobalt Chromite Green",
"897":"Cadmium-Free Green Pale","294":"Green Gold","447":"Olive Green","426":"Naples Yellow Light",
"422":"Naples Yellow","333":"Brilliant Yellow","425":"Naples Yellow Deep","745":"Yellow Ochre Light",
"746":"Yellow Ochre Pale","320":"Indian Yellow Deep","285":"Gold Ochre","744":"Yellow Ochre",
"557":"Raw Umber Light","552":"Raw Sienna","147":"Chrome Green Deep Hue","696":"Viridian Hue",
"720":"Winsor Green (Phthalo)","721":"Winsor Green (Yellow Shade)","482":"Permanent Green Deep","481":"Permanent Green",
"708":"Winsor Emerald","483":"Permanent Green Light","637":"Terre Verte","459":"Oxide of Chromium",
"540":"Prussian Green","599":"Sap Green","420":"Cinnabar Green","084":"Cadmium Green Pale",
"676":"Vandyke Brown","554":"Raw Umber","558":"Raw Umber (Green Shade)","217":"Davy's Gray",
"427":"Mineral Grey","424":"Ultramarine Ash","465":"Payne's Gray","034":"Blue Black",
"322":"Indigo","142":"Charcoal Grey","386":"Mars Black","331":"Ivory Black",
"337":"Lamp Black","505":"Perylene Black",
}

rows_out = []
for (r,c), code in grid_code.items():
    cmyk = grid_color.get((r,c))
    name = names.get(code, "UNKNOWN")
    if cmyk is None:
        rows_out.append({'Code':code,'Name':name,'C':'','M':'','Y':'','K':''})
        continue
    C,M,Y,K = cmyk
    rows_out.append({'Code':code,'Name':name,
                      'C': round(C*100,1),'M': round(M*100,1),
                      'Y': round(Y*100,1),'K': round(K*100,1)})

rows_out.sort(key=lambda r: r['Code'])

with open('./paint_cmyk_values.csv','w',newline='') as f:
    w = csv.DictWriter(f, fieldnames=['Code','Name','C','M','Y','K'])
    w.writeheader()
    for r in rows_out:
        w.writerow(r)

print("total rows written", len(rows_out))
for r in rows_out[:8]:
    print(r)


