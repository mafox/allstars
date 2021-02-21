
import pandas as pd

url = 'https://en.wikipedia.org/wiki/NBA_All-Star_Game#All-Star_Game_results'

resultTable = pd.read_html(url)
#print("resultTable: ", resultTable)

# Remove sections before table
resultTable.remove(resultTable[0])
#print("resultTable:\n", resultTable)

resultTable.remove(resultTable[0])
#print("resultTable:\n", resultTable)

#print("resultTable[0].shape:\n ", resultTable[0].shape)
# Just need the 75 rows of the table
resultTable = resultTable[0][0:74]
print("columns:\n", resultTable.columns)

resultTable.drop(labels="Game MVP", axis="columns", inplace=True)
resultTable.drop(labels="Host arena", axis="columns", inplace=True)
print("describe resultTable:\n", resultTable.describe(), "\n")

resultTable["City"] = resultTable["Host city"].str.split(pat=",", n=1, expand=True).get(0)
resultTable.drop(labels="Host city", axis="columns", inplace=True)
# get the scores from the composition Result column
res = resultTable["Result"].str.split(pat=r"\s|,", expand=True)
# lots of irrelevant columns produced
cols = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
res.drop(res.columns[cols], axis=1, inplace=True)
# get rid of rrelevant columns and name relrevant ones
res.rename(columns={0: "LocEast", 1: "East", 2: 'blank', 3: "LocWest", 4: "West"}, inplace=True)

for i in range(0, len(res)):
	row = res.loc[i]
	try:  # convert scores to integers
		row[1] = int(row[1])
		row[4] = int(row[4])
	except:
		continue
	if (row[0] == 'West'): # score in wrong column
		temp = res.loc[i][1]
		res.loc[i][1] = res.loc[i][4]
		res.loc[i][4] = temp

cols1 = [0, 2, 3]  # nolonger needed
res.drop(res.columns[cols1], axis=1, inplace=True)

resultTable.drop(labels="Result", axis="columns", inplace=True)

# make new table to include integer scores
final = pd.concat([resultTable[['Year']], res[['East', 'West']], resultTable[['City']]], axis=1)

#print("final:\n", final)

# Now get differences between East and West scores
exclude = []
excludeLoc = []
diff = []
yearDiff = []
for i in range(0, len(final)):
	try:
		tmp = int(final.iloc[i].East) - int(final.iloc[i].West)
		if tmp < 0:
			tmp = - tmp
		diff.append(tmp)
		yearDiff.append(final.iloc[i].Year)
	except:
		exclude.append(final.loc[i])
		excludeLoc.append(i)
# have a look at what the non integer scores mean by printing under
#print("excludeLoc:\n", excludeLoc)
#print("exclude:\n", exclude)
final.drop(excludeLoc, inplace=True)
final = final.assign(dif = diff) # add the deference column
print("final length: ", len(final), "\n final table sorted by differences\n", final.sort_values(by = ['dif']))
diff.sort()
print("sorted differencres:\n", diff)
# now for mean of scores for cities hosting more than one game

grpc = final.groupby('City')

# I'm going top construct a new data framed from scratch looks like
# scoreData = {'Host City':  HC, 'East': ES, 'West': WS, 'Count': CT }

HC = []
ES = []
WS = []
CT = []

# now to fill the lists

oldKey = ""
for k, gp in grpc:
	# print('key=' + str(k))
	if len(gp['City']) > 1: #  only want to traverse oncve per city
		if k == oldKey:
			continue
		oldKey = k
		#print('key=' + str(k), " ", len(gp['City']), " City: ", gp['City'])
		#print("mean: ", gp['East'].mean(), ' ', gp['West'].mean())
		HC.append(str(k)) # must use key as gp['city'] has repeat values
		ES.append(gp['East'].mean())
		WS.append(gp['West'].mean())
		CT.append(len(gp['City']))
		# print("East mean")
		# print(ES)

scoreData = {'Host City': HC, 'East': ES, 'West': WS, 'Count': CT}

# Convert the dictionary into DataFrame
dfsc = pd.DataFrame(scoreData)
dfsc.set_index('Host City')
# This produces final table
print('new table sorted by count\n', dfsc.sort_values( by = ['Count']))
