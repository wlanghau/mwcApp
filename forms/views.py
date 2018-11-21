from django.shortcuts import render, redirect
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

def enter_pr_data(req):
	context = {}
	context['schools'] = getLiveSchools()
	context['fruits'] = getMenuData()['am: fruit']['components']
	context['numFruits'] = ['Fruit 1','Fruit 2','Fruit 3']
	return render(req, 'home.html', context)
	
def generate_table(req):

	context = {}
	context['msg'] = ''
	context['err'] = ''

	menuSheetDict = getMenuData()
	
	# Need to get all schools? Add optional arg for school name
	schoolDict = getSchoolData()
	menuCalDict = getMenuCalData()
	baselineOptInDict = getBaselineOptInData()
	
	if req.method == 'POST':
		meal=req.POST['meal']
		date = req.POST['date']
		
		menuDay = getMenuDay(mean, date)
		
		try:
			menuCalDict[date]
		except Exception as e:
			context['err'] += 'Not a valid menu day: '+date
			redirect('', context)
			
		try:
			menuSheetDict[menuDay]['components']
		except Exception as e:
			context['err'] += 'Cannot find menu day components'
			return redirect('', context)
				
	
	
		context['school'] = req.POST['school']
		context['fruits'] = [req.POST[x] for x in ['Fruit 1', 'Fruit 2', 'Fruit 3'] if req.POST[x] is not None]
		context['menuDayComponents'] = menuSheetDict[menuDay]['components']
		context['saladComponents'] = menuSheetDict['al: salad bar']['components']
		context['isLunch'] = meal == 'Lunch'
		context['isGrab'] = schoolDict[school]['grabAndGo'] == 'True'
		context['isExpanded'] = schoolDict[school]['expandedSalad'] == 'True'
		context['isHs'] = schoolDict[school]['age'] == "912"
		context['expandedComponents'] = menuSheetDict['hsl: salad bar add-ons']['components']
		context['grabAndGoBreakComponents'] = menuSheetDict['hsb: grab n go']['components']
		context['grabAndGoLunchComponents'] = getGrabAndGo(school, menuDay, meal)
	
		return render(req, 'result.html', context)
	else:
		return redirect('')