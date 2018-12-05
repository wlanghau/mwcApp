import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# Authorize API credentials to use the Google Sheets API
scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name('./mwcApp/credentials/MWCapp-168978c46517.json', scope)
# gc = gspread.authorize(credentials)

# Retrieve the three Google Sheets "database" files
mainDatabaseKey = '19Rszi38ZKUsZqQ1UORV-a-rEORx1LpuFRgjyggEcFrE'
orderingToolKey = '109ngaK12BJS7u116vbBbrawjPxIxjNlqi8MjoecuRZI'
productionRecord = '160B7q0IdDYTzjRPemBwbCYVP3jLDhCt3BnD8Av3skAs'
# mainDatabaseSpreadsheet = gc.open_by_key(mainDatabaseKey)
# orderingToolSpreadsheet = gc.open_by_key(orderingToolKey)
# productionRecordSpreadsheet = gc.open_by_key(productionRecord)

# Return a dictionary contating all of the data from the menuCal table
# Iterate through the table retrieving the planned breakfast and lunch meal for each day
def getMenuCalData():
	gc = gspread.authorize(credentials)
	mainDatabaseSpreadsheet = gc.open_by_key(mainDatabaseKey)
	menuCalSheet = mainDatabaseSpreadsheet.worksheet("[Table] MenuCal")
	menuCalData = menuCalSheet.get_all_values()
	menuCalDict = {}

	for x in range(2,len(menuCalData)-1,2):
		menuCalDict[menuCalData[x][0]] = {"breakfast": menuCalData[x][2], "lunch":menuCalData[x+1][2]}

	return menuCalDict

# Return a dictionary contating all of the data from the EaterInfo table
# Iterate through the table retrieving the all of the neccessary information
# for every school in the BPS school district
def getSchoolData():
	gc = gspread.authorize(credentials)
	mainDatabaseSpreadsheet = gc.open_by_key(mainDatabaseKey)
	schoolsSheet = mainDatabaseSpreadsheet.worksheet("[Table] EaterInfo")
	schoolsData = schoolsSheet.get_all_values()
	schoolDict = {}

	for x in range(2,len(schoolsData)):
		schoolDict[schoolsData[x][2]] = {
        "name" : schoolsData[x][2],
        "live" : schoolsData[x][3],
        "age" : schoolsData[x][4],
        "population" : schoolsData[x][5],
        "attendance" : int(schoolsData[x][6]),
        "Breakfast" : int(schoolsData[x][7].strip('%'))/100,
        "Lunch" : int(schoolsData[x][8].strip('%'))/100,
        "expandedSalad" : schoolsData[x][9],
        "grabAndGo" : schoolsData[x][10]
        }

	return schoolDict

# Return a dictionary contating all of the data from the Menu table
# Iterate through the table retrieving the all of the components from
# each menu item that the BPS serves
def getMenuData():
	gc = gspread.authorize(credentials)
	mainDatabaseSpreadsheet = gc.open_by_key(mainDatabaseKey)
	menuSheet = mainDatabaseSpreadsheet.worksheet("[Table] Menu")
	menuData = menuSheet.get_all_values()
	menuSheetDict = {}

	for x in range(2,len(menuData)):
		menuSheetDict[menuData[x][0]] = {}
		menuSheetDict[menuData[x][0]]["components"] =  menuData[x][1].split(',')

	return menuSheetDict

# Return a dictionary contating all of the data from the menuCal table
# Iterate through the table retrieving the planned breakfast and lunch meal for each day
def getBaselineOptInData():
	gc = gspread.authorize(credentials)
	orderingToolSpreadsheet = gc.open_by_key(orderingToolKey)
	baselineOptInSheet = orderingToolSpreadsheet.worksheet("Baseline Opt In rates")
	baselineOptInData = baselineOptInSheet.get_all_values()
	baselineOptInDict = {}

	# Necessary?
	liveSchoolArray = getLiveSchools()
	for x in range(1,len(baselineOptInData)):
		baselineOptInDict[baselineOptInData[x][0]] = {}
		for y in range(1,len(baselineOptInData[x]) - 1):
			if len(baselineOptInData[x][y]) > 1:
				percentage = float(baselineOptInData[x][y].strip('%'))/100
				baselineOptInDict[baselineOptInData[x][0]][baselineOptInData[0][y]] = percentage

	return baselineOptInDict

# Return an array of all the current live schools that My Way Cafe is serving
def getLiveSchools():
	schoolDict = getSchoolData()
	returnArray = []
	for key in schoolDict:
		if schoolDict[key]["live"] == "TRUE":
			returnArray.append(key)
	return returnArray

# return the menuday for the given meal and date string
def getMenuDay(meal,dateStr):
    menuCalDict = getMenuCalData()

    if dateStr in menuCalDict.keys():
        if meal == 'Breakfast':
            return menuCalDict[dateStr]["breakfast"]
        else:
            return menuCalDict[dateStr]["lunch"]

# Get Next Available Row
# Could potentially use sheet.row_count but does not look unfilled rows			
def next_available_row(worksheet):
	# str_list = list(filter(None, worksheet.col_values(1)))  # fastest
	# return str(len(str_list)+1)

	# Some blank rows giving bad errors so just getting entire length
	return len(worksheet.col_values(1))

# Take all data submitted from the application form, properly format it, then send it to the 
# Production records database. There are two separates tables in the PR relational database structure, 
# the individual entry needs to be sent to one table and all of the individual component information needs
# to be sent to the other table. In order to improve run time, all rows are added to an array and then batch
# uploaded to google sheets.
def sendToDatabase(formDict):
	schoolDict = getSchoolData()

	gc = gspread.authorize(credentials)
	productionRecordSpreadsheet = gc.open_by_key(productionRecord)
	PRMealsSpreadsheet = productionRecordSpreadsheet.worksheet("[Table] PRMeals")
	
	# Loading whole book seems like it is too much
	# allMealsValues = PRMealsSpreadsheet.get_all_values()
	# allMealsValuesLength = len(allMealsValues)
	allMealsValuesLength = next_available_row(PRMealsSpreadsheet)
	

	today = datetime.datetime.today().strftime('%D')
	mealDateSplit = formDict['date'].split("-")
	mealDate = mealDateSplit[1]+"/"+mealDateSplit[2]+"/"+mealDateSplit[0]

	meal = formDict['meal'].lower()
	menuDay = getMenuDay(meal,formDict['date'])
	school = formDict['school']

	# If we can assume no spaces at the end of the file sheet.append_row works
	# Insert row cant insert at end of file unless there are empty rows
	# Work on a check to know for sure but go for append row for now

	if schoolDict[formDict['school']]['age'] == "912":
		mealRow = [today,mealDate,'20172018',
		school,meal,"0",formDict['reimbursable-meals'],
		formDict['adult-meals'],formDict['adult-earned-meals'],"",formDict['daily-notes']]
		# PRMealsSpreadsheet.insert_row(mealRow, allMealsValuesLength+1)
	else:
		mealRow = [today,mealDate,'20172018',
		school,meal,formDict['reimbursable-meals'],"0",
		formDict['adult-meals'],formDict['adult-earned-meals'],"",formDict['daily-notes']]
		# PRMealsSpreadsheet.insert_row(mealRow, allMealsValuesLength+1)

	PRMealsSpreadsheet.append_row(mealRow)

		
	# WTF?
	# Reads Table
	prComponentsAcc = []
	# rowAcc = []
	# i = 1
	# for form in formDict:
		# if i > 10:
			# ind = i % 7

			# if ind == 4:
				# rowAcc.extend([today,mealDate,school,meal,menuDay,form[8:],formDict[form]])	
			# elif ind == 3:
				# rowAcc.append(formDict[form])
				# prComponentsAcc.append(rowAcc)
				# rowAcc = []
			# else:
				# rowAcc.append(formDict[form])			
		# i+=1
		
	# WBL Ideas:
	# Get all keys, Get unique after planned-, for each unique make row
	
	components = [x.split('-', 1)[1] for x in formDict.keys() if 'planned' in x]
	for comp in components:
		rowAcc = [today,mealDate,school,meal,menuDay,comp,formDict['planned-'+comp],formDict['prepared-'+comp],
		formDict['served-'+comp],formDict['leftover-'+comp],formDict['wasted-'+comp],formDict['extra-'+comp],formDict['notes-'+comp]]
		prComponentsAcc.append(rowAcc)

	sendToDatabaseHelper(prComponentsAcc)
	
# Helper function that uses an array of arrays, with each internal array representing one row in the
# database. It finds the last row of the database and then for each cell in the row, the value is updated.
# Makes one call via API to the google sheets database per row.
def sendToDatabaseHelper(prComponentsRow):
	gc = gspread.authorize(credentials)
	productionRecordSpreadsheet = gc.open_by_key(productionRecord)
	PRComponentsSpreadsheet = productionRecordSpreadsheet.worksheet("[Table] PRComponents")    
    
	# Too much to read in all data
	# allComponentValues = PRComponentsSpreadsheet.get_all_values()    
	# allComponentValuesLength = len(allComponentValues)
	allComponentValuesLength = next_available_row(PRComponentsSpreadsheet)
    
	cellRange = 'A'+str(allComponentValuesLength+1)+':M'+str(len(prComponentsRow)+allComponentValuesLength+1)

	# Need to resize spreadsheet before selecting new cells
	PRComponentsSpreadsheet.resize(len(prComponentsRow) + allComponentValuesLength + 1,
								   PRComponentsSpreadsheet.col_count)

	# Select a range
	cell_list = PRComponentsSpreadsheet.range(cellRange)

	for row in range(0,len(prComponentsRow)):
		for col in range(0,len(prComponentsRow[row])):
			ind = row * 13 + col
			val = prComponentsRow[row][col]
			cell = cell_list[ind]
			cell.value = val

	# Update in batch
	PRComponentsSpreadsheet.update_cells(cell_list)
