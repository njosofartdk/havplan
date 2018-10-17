import arcpy, os

ru = "ru"
eu = "eu"
ik = "ng"
worksp = os.path.join(r"C:\havplan\havplan_data", "kategorier")

if not os.path.exists(os.path.join(worksp, ru, "identity" )):
    os.makedirs(os.path.join(worksp, ru, "identity"))
identitydir = os.path.join(worksp, ru, "identity")


throw = "intermediate"
final = "final"

rudirlist = []
for root, dirs, files in os.walk(os.path.join(worksp, ru, throw)):
    for file in files:
        if file.endswith(".shp"):
            rudirlist.append((os.path.join(root, file)))

eungdirlist = []
for i in [eu, ik]:
    for root, dirs, files in os.walk(os.path.join(worksp, i, final)):
        for file in files:
            if file.endswith(".shp"):
                eungdirlist.append((os.path.join(root, file)))

for x in rudirlist:
    tmp =  "in_memory/tmpfileid"
    arcpy.Identity_analysis(x, eungdirlist[0], tmp)
    arcpy.Identity_analysis(tmp, eungdirlist[1], os.path.join(identitydir, "id_"+os.path.basename(x)))
    arcpy.Delete_management(tmp)
