from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from urllib.error import HTTPError
from forms.googleSheetsData import *


# import logging
# import datetime
# from googleSheetsData import getMenuCalData,getSchoolData,getMenuData,getBaselineOptInData,sendToDatabase,getLiveSchools,getMenuDay
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
# import datetime


# Create your views here.
# scope = ['https://spreadsheets.google.com/feeds']
# credentials = ServiceAccountCredentials.from_json_keyfile_name('./MWCapp-6ea127e5c10a.json', scope)
# gc = gspread.authorize(credentials)


def getGrabAndGo(school, menu, meal, menuSheetDict):
    # Necessary to call again? Going to add to args
    # menuSheetDict = getMenuData()
    if meal == "Lunch":
        if school == "East Boston HS":
            return menuSheetDict["gg-ebhs-" + menu]['components']
        elif school == "Mckay K-8" or school == "Umana/Mario Academy K-8":
            return menuSheetDict["gg-mk&um-" + menu]['components']
        else:
            return []
    else:
        return []


def plannedDictBuilder(menuDayComponents, school, meal, baselineOptInDict, schoolDict):
    returnDict = {}
    attendance = schoolDict[school]['attendance']
    mealOptIn = schoolDict[school][meal]
    for component in menuDayComponents:
        try:
            componentOptIn = baselineOptInDict[component][school]
            planned = attendance * mealOptIn * componentOptIn
            returnDict[component] = int(planned)
        except Exception as e:
            returnDict[component] = 0
    return returnDict


# @login_required
def enter_pr_data(req):
    context = {}
    context['schools'] = getLiveSchools()
    context['fruits'] = get_fruit_list()
    context['numFruits'] = ['Fruit 1', 'Fruit 2', 'Fruit 3']
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

        meal = req.POST['meal']
        date = req.POST['date']

        menuDay = getMenuDay(meal, date)

        try:
            menuCalDict[date]
        except Exception as e:
            context['err'] += 'Not a valid menu day: ' + date
            redirect('/', context)

        try:
            menuSheetDict[menuDay]['components']
        except Exception as e:
            context['err'] += 'Cannot find menu day components'
            return redirect('/', context)

        menuDayComponents = menuSheetDict[menuDay]['components']
        fruits = [req.POST[x] for x in ['Fruit 1', 'Fruit 2', 'Fruit 3'] if req.POST[x] != 'None']
        saladComponents = menuSheetDict['al: salad bar']['components']
        grabAndGoBreakComponents = menuSheetDict['hsb: grab n go']['components']
        grabAndGoLunchComponents = getGrabAndGo(req.POST['school'], menuDay, meal, menuSheetDict)
        expandedComponents = menuSheetDict['hsl: salad bar add-ons']['components']
        school = req.POST['school']

        context['school'] = school
        context['meal_date'] = date
        context['meal'] = meal
        context['daily_notes'] = req.POST['daily-notes']
        context['isLunch'] = meal == 'Lunch'
        context['isGrab'] = schoolDict[school]['grabAndGo'] == 'True'
        context['isExpanded'] = schoolDict[school]['expandedSalad'] == 'True'
        context['isHs'] = schoolDict[school]['age'] == "912"

        del req.POST['Fruit 1']
        del req.POST['Fruit 2']
        del req.POST['Fruit 3']
        context['result'] = req.POST
        context['menuDay'] = menuDay

        context['component_list'] = get_component_list()
        context['fruits_list'] = get_fruit_list()

        context['fruits'] = plannedDictBuilder(fruits, school, meal, baselineOptInDict, schoolDict)
        context['components'] = plannedDictBuilder(menuDayComponents, school, meal, baselineOptInDict, schoolDict)
        context['saladComponents'] = plannedDictBuilder(saladComponents, school, meal, baselineOptInDict, schoolDict)
        context['expandedComponents'] = plannedDictBuilder(expandedComponents, school, meal, baselineOptInDict,
                                                           schoolDict)
        context['grabAndGoBreakComponents'] = plannedDictBuilder(grabAndGoBreakComponents, school, meal,
                                                                 baselineOptInDict, schoolDict)
        context['grabAndGoLunchComponents'] = plannedDictBuilder(grabAndGoLunchComponents, school, meal,
                                                                 baselineOptInDict, schoolDict)
        context['drinks'] = plannedDictBuilder(menuSheetDict["am: drinks"]['components'], school, meal,
                                               baselineOptInDict, schoolDict)

        # print(sdsd)

        return render(req, 'result.html', context)
    else:
        return redirect('/')


def send_to_database(req):
    if req.method == 'POST':
        try:
            sendToDatabase(req.POST)
            return redirect('/')
        except HTTPError as e:
            if e.code == 502:
                return HttpResponseRedirect(req.META.get('HTTP_REFERER'))
    else:
        return redirect('/')


def return_comp_planned(req, school, meal, comp):
    schoolDict = getSchoolData()
    baselineOptInDict = getBaselineOptInData()
    response_val = plannedDictBuilder([comp], school, meal, baselineOptInDict, schoolDict)[comp]
    return HttpResponse(response_val, content_type="text/plain")


def enter_inventory_data(req):
    context = {}
    context['schools'] = getLiveSchools()
    context['inventory_items'] = [
        {'type': 'Ambient',
         'items': [
            "olive oil",
            "all purpose seasoning",
            "taco mix",
            "quick oats",
            "ketchup - pc",
            "whole wheat spaghetti",
            "whole wheat penne pasta",
            "brown rice",
            "jerk marinade",
            "ground black pepper",
            "salt"
         ]},
        {'type': 'Freezer',
         'items': [
             "plain bagel",
             "frozen blueberries"
         ]},
        {'type': 'Fridge',
         'items': [
             "cream cheese - pc",
             "pulled chicken",
             "frozen corn kernels",
             "liquid eggs",
             "ranch dressing",
             "honey mustard",
             "plain yogurt",
             "shredded cheddar cheese"
         ]}
    ]

    return render(req, 'inventory.html', context)


def inventory_submit(req):
    if req.method == 'POST':
        try:
            send_to_inventory(req.POST)
            return redirect('/')
        except HTTPError as e:
            if e.code == 502:
                return HttpResponseRedirect(req.META.get('HTTP_REFERER'))
    else:
        return redirect('/')

