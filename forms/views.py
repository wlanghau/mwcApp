from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from forms.googleSheetsData import getMenuCalData,getSchoolData,getMenuData,getBaselineOptInData,sendToDatabase,getLiveSchools,getMenuDay


#import logging
#import datetime
#from googleSheetsData import getMenuCalData,getSchoolData,getMenuData,getBaselineOptInData,sendToDatabase,getLiveSchools,getMenuDay
#import gspread
#from oauth2client.service_account import ServiceAccountCredentials
#import datetime


# Create your views here.
#scope = ['https://spreadsheets.google.com/feeds']
#credentials = ServiceAccountCredentials.from_json_keyfile_name('./MWCapp-6ea127e5c10a.json', scope)
#gc = gspread.authorize(credentials)


def getGrabAndGo(school,menu,meal, menuSheetDict):

	# Necessary to call again? Going to add to args
    # menuSheetDict = getMenuData()
    if meal == "Lunch":
        if school == "East Boston HS":
            return menuSheetDict["gg-ebhs-"+menu]['components']
        elif school == "Mckay K-8" or school == "Umana/Mario Academy K-8":
            return menuSheetDict["gg-mk&um-"+menu]['components']
        else:
            return []
    else:
        return []


def plannedDictBuilder(menuDayComponents,school,meal,baselineOptInDict,schoolDict):
	returnDict = {}
	attendance = schoolDict[school]['attendance']
	mealOptIn = schoolDict[school][meal]
	for component in menuDayComponents:
		try:
			componentOptIn = baselineOptInDict[component][school]
			planned = attendance*mealOptIn*componentOptIn
			returnDict[component] = int(planned)
		except Exception as e:
			returnDict[component] = 0
	return returnDict


@login_required
def enter_pr_data(req):
	context = {}
	context['schools'] = getLiveSchools()
	context['fruits'] = getMenuData()['am: fruit']['components']
	context['numFruits'] = ['Fruit 1','Fruit 2','Fruit 3']
	return render(req, 'home.html', context)


def generate_table(req):

	if req.method == 'POST':
		context = {}
		context['msg'] = ''
		context['err'] = ''
		req.POST = req.POST.copy()
		
		del req.POST['csrfmiddlewaretoken']
		context['result'] = req.POST

		menuSheetDict = getMenuData()
		
		# Need to get all schools? Add optional arg for school name
		schoolDict = getSchoolData()
		menuCalDict = getMenuCalData()
		baselineOptInDict = getBaselineOptInData()
	
		meal=req.POST['meal']
		date = req.POST['date']
		
		menuDay = getMenuDay(meal, date)
		
		try:
			menuCalDict[date]
		except Exception as e:
			context['err'] += 'Not a valid menu day: '+date
			redirect('/', context)
			
		try:
			menuSheetDict[menuDay]['components']
		except Exception as e:
			context['err'] += 'Cannot find menu day components'
			return redirect('/', context)
				
	
		menuDayComponents = menuSheetDict[menuDay]['components']
		fruits = [req.POST[x] for x in ['Fruit 1', 'Fruit 2', 'Fruit 3'] if req.POST[x] is not None]
		saladComponents = menuSheetDict['al: salad bar']['components']
		grabAndGoBreakComponents = menuSheetDict['hsb: grab n go']['components']
		grabAndGoLunchComponents = getGrabAndGo(req.POST['school'], menuDay, meal, menuSheetDict)
		expandedComponents = menuSheetDict['hsl: salad bar add-ons']['components']
		school = req.POST['school']
	
		context['school'] = school
		context['isLunch'] = meal == 'Lunch'
		context['isGrab'] = schoolDict[school]['grabAndGo'] == 'True'
		context['isExpanded'] = schoolDict[school]['expandedSalad'] == 'True'
		context['isHs'] = schoolDict[school]['age'] == "912"
		context['result'] = req.POST		

		context['fruits'] = plannedDictBuilder(fruits,school,meal,baselineOptInDict,schoolDict)
		context['components'] = plannedDictBuilder(menuDayComponents,school,meal,baselineOptInDict,schoolDict)
		context['saladComponents'] = plannedDictBuilder(saladComponents,school,meal,baselineOptInDict,schoolDict)
		context['expandedComponents'] = plannedDictBuilder(expandedComponents,school,meal,baselineOptInDict,schoolDict)
		context['grabAndGoBreakComponents'] = plannedDictBuilder(grabAndGoBreakComponents,school,meal,baselineOptInDict,schoolDict)
		context['grabAndGoLunchComponents'] = plannedDictBuilder(grabAndGoLunchComponents,school,meal,baselineOptInDict,schoolDict)
		context['drinks'] = plannedDictBuilder(menuSheetDict["am: drinks"]['components'],school,meal,baselineOptInDict,schoolDict)
		
	
		# print(sdsd)
		
		return render(req, 'result.html', context)
	else:
		return redirect('/')


def send_to_database(req):
	if req.method == 'POST':
		sendToDatabase(req.POST)
		return redirect('/')
	else:
		return redirect('/')
	