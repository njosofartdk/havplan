import csv, os
#scriptet her laver en liste over datasættene der findes på computeren, kategoriseret ift. zone (EU, RU og NG)

def categorizer(csvfilen, dirlists, filelist, anvendelsesklasse):
    countc = 0
    countf = 0
    sektordict = {}
#   #aflæser .csv filen der indeholder informationer omkring hvordan hvert enkelt datasæt skal håndteres
    with open(csvfilen) as csvfile:
        readCSV = csv.DictReader(csvfile, delimiter=';')
        
        for row in readCSV:
            brugbar = row["brugbart ift. havplan laget?"]
    
            if brugbar.lower() == "ja": #hvis datasættet er brugbar, sæt en masse variabler
                filnavn = row["filnavn(wfs, dl, shp)"]
                category = row["CATEGORY"]
                sektor = row["sektor"]
                tema = row["tema"]
                #hvis anvendelseskoden, f.eks "eu/ru" er længere end 2, dvs. den indeholder flere anveldeskoder, så bruges den første anvendelseskode
                if len(category) > 2:
                    category = category.split("/")[0].lower()
                else: 
                    category = category.lower()
                    
                if category == anvendelsesklasse.lower() and filnavn not in ["", " "]: 
                    countc += 1
                    if filnavn.lower() in filelist:
                        countf += 1
                        if sektordict.get(sektor) == None: 
                            sektordict[sektor] = [tema]
                        else: 
                            sektordict[sektor].append(tema)

                    else:
                            print (filnavn, " is missing")
    print (countc - countf, " are missing")
    return sektordict


#input der skal ændres på
inputworksp = r"C:\havplan\projekter\havplans_temalag_7_arbjgrpmode_11_okt\data\input\havplans_data_til_7arbjdsmode"

#r"C:\Users\B039723\Documents\Filkassen\havplan\projekter\havplans_temalag_7_arbjgrpmode_11_okt\data\intermediate"

liste = os.path.join(r"C:\Users\B039723\Documents\Filkassen\havplan\BaseData\lists","oversigt_data_24_sep_7_internPC.csv")

##laver to lister (lidt ineffektivt), 1) dirlist nideholder hele path'en til filen, 2) filelist indeholder filenavnet (samt extensionen ".shp")
filelist_UK = []
dirlist = []

#for root, dirs, files in os.walk(os.path.join(inputworksp, dataspace)):
for root, dirs, files in os.walk(inputworksp):
    for file in files:
        if file.endswith(".shp"):
            dirlist.append((os.path.join(root, file)))
            filelist_UK.append(file.lower().replace("ø", "oe")
            .replace("æ", "ae").replace("å", "aa").replace(".shp", ""))

anvendelseskoder = ["ru", "eu", "ng"]
#outputname = "reserverede_udviklingszone"
for anvendelseskode in anvendelseskoder:
    print (anvendelseskode)    
    sektordict = categorizer(liste, dirlist, filelist_UK, anvendelseskode)
    for key, value in sektordict.items() :
        print (key, value)








