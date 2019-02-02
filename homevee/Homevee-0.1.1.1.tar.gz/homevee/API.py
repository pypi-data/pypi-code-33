#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import traceback
from thread import start_new_thread

from DeviceAPI import dimmer, energy_data
from DeviceAPI.blind_control import set_blinds, get_all_blinds, set_room_blinds
from DeviceAPI.heating import get_thermostats, control_room_heating
from DeviceAPI.rfid_control import get_rfid_tags, add_edit_rfid_tag, run_rfid_action
from DeviceAPI.rgb_control import rgb_control
#from Functions import people_classifier, ar_control
#from Functions.people_classifier import *
from Functions import room_data, weather, events, chat, shopping_list, media_center, gps_data, nutrition_data
from DeviceAPI.get_modes import *
from DeviceAPI.wake_on_lan import *
from Functions.condition_actions.actions import run_scene
from Functions.home_budget import get_home_budget_data, add_edit_home_budget_data, delete_home_budget_data, \
    get_home_budget_data_day_items, get_home_budget_data_graph
from Helper.helper_functions import load_remote_data, save_remote_data, set_remote_control_enabled, \
    connect_remote_id_with_account, verify_user
from Manager import dashboard, mqtt_connector, places
from Manager.api_key import *
from Manager.automation import *
from Manager.custom_voice_commands import get_voice_commands, add_edit_voice_command, delete_voice_command
from Manager.device import *
from Manager.gateway import *
from Manager.heating_scheme import *
from Manager.persons import get_persons, add_edit_person
from Manager.room import *
from Manager.scenes import add_edit_scene, delete_scene, get_all_scenes
from Manager.smart_speaker import get_smart_speakers
from Manager.user import *
from VoiceAssistant import *
from VoiceAssistant.voice_replace_manager import *
from Functions.graph_data import *
import Helper.permissions
from Functions.sensor_data import *
from Functions.system_info import *
from Functions.tv_data import *
from Functions.calendar import *
from updater import update_system, check_for_updates

def process_data(data, db):
    try:
        username = data['username']
        password = data['password']

        verified = verify_user(username, password)

        if not verified:
            return json.dumps({'result': 'wrongdata'})

        try:
            return handle_request(data, db)
        except Exception as e:
            traceback.print_exc()
            return
    except Exception, e:
        traceback.print_exc()
        if 'status' in data:
            if data['status'] == 'connectionok':
                print('connectionok')

def handle_request(request, db):
    response = None

    action = request['action']
    username = request['username']

    if('user_last_location' in request and request['user_last_location'] is not None):
        user_last_location = json.loads(request['user_last_location'])
    else:
        user_last_location = None


    #Roomdata
    if action == "login":
        rooms = room_data.get_rooms(username, db)

        remote_id = get_server_data("REMOTE_ID", db)

        response = {'remote_id': remote_id, 'rooms': rooms['rooms']}

    #Roomdata
    elif action == "getrooms":
        response = room_data.get_rooms(username, db)
    elif action == "getroomdata":
        response = room_data.get_room_data(username, request['room'], db)

    #Remote-ID
    elif action == "setremotedata":
        response = save_remote_data(username, request['remote_id'], request['linked_account'], db)
    elif action == "getremotedata":
        response = load_remote_data(username, db)
    elif action == "setremotecontrolenabled":
        response = set_remote_control_enabled(username, request['enabled'], db)
    elif action == "connectremoteidwithaccount":
        response = connect_remote_id_with_account(username, request['accountname'], request['accountsecret'], db)

    #Kalender
    elif action == "getcalendaritemdates":
        response = get_calendar_item_dates(username, request['year'], db)
    elif action == "getcalendardayitems":
        response = get_calendar_day_items(username, request['date'], db)
    elif action == "addeditcalendarentry":
        response = add_edit_entry(username, request['id'], request['name'], request['date'], request['start'], request['end'], request['note'], request['address'], db)
    elif action == "deletecalendarentry":
        response = delete_entry(username, request['id'], db);

    #Personen
    elif action == "getpersons":
        response = get_persons(db)
    elif action == "addeditperson":
        response = add_edit_person(username, request['id'], request['name'], request['nickname'], request['address'],
                                   request['latitude'], request['longitude'], request['phonenumber'], request['birthdate'], db)

    #RGB Lampen
    elif action == "setrgb":
        response = rgb_control(username, request['type'], request['id'], request['mode'], request['brightness'], request['color'], db)

    #RFID
    elif action == "getrfidtags":
        response = get_rfid_tags(username, db)
    elif action == "addeditrfidtag":
        response = add_edit_rfid_tag(username, request['name'], request['uuid'], request['type'], request['id'], db)
    elif action == "deleterfidtag":
        response = add_edit_rfid_tag(username, request['uuid'], db)
    elif action == "runrfidaction":
        response = run_rfid_action(username, request['uuid'], db)

    #Events
    elif action == "getevents":
        type = None
        if "type" in request:
            type = request['type']
        response = events.get_events(username, type, request['limit'], request['offset'], db)
    elif action == "geteventtypes":
        response = events.get_event_types(db)
    elif action == "addevent":
        response = events.add_event(request['type'], request['text'], db)
    elif action == "getunseenevents":
        response = events.get_unseen_events(username, db)

    #Permissions
    elif action == "getpermissions":
        response = Helper.permissions.get_permissions(request['user'], db)
    elif action == "setpermissions":
        response = Helper.permissions.set_permissions(username, request['user'], request['permissions'], db)

    #MQTT Anlernen => generate_device_data()
    elif action == "generatedevicedata":
        response = mqtt_connector.generate_device_data(username, request['location'], db)
    elif action == "savemqttdevice":
        response = mqtt_connector.save_mqtt_device(username, request['type'], request['location'], request['id'],
                                                   request['devicedata'], db)

    #Jalousie-Steuerung
    elif action == "setblinds":
        response = set_blinds(username, request['type'], request['id'], request['value'], db)
    elif action == "setroomblinds":
        response = set_room_blinds(username, request['location'], request['value'], db)
    elif action == "getallblinds":
        response = get_all_blinds(username, db)

    #Weather
    elif action == "getweather":
        response = weather.get_weather(request['daycount'], db)
    elif action == "getweathercitylist":
        response = weather.get_weather_city_list(db)
    elif action == "setweathercityid":
        response = weather.set_weather_city_id(username, request['id'])

    #Get graph data
    elif action == "getgraphdata":
        response = get_graph_data(username, request['room'], request['type'], request['id'], request['von'], request['bis'], db)

    #Get modes, set modes
    elif action == "getmodes":
        response = get_modes(username, request['room'], request['type'], request['device'], db)
    elif action == "setmodes":
        response = set_modes(username, request['type'], request['device'], request['zustand'], db)

    #Dimmer
    elif action == "setdimmer":
        response = dimmer.set_dimmer(username, request['type'], request['id'], request['value'], db)

    #Wake on Lan
    elif action == "wakeonlan":
        response = wake_on_lan(username, request['id'], db)
    elif action == "startxboxone":
        response = wake_xbox_on_lan(username, request['id'], db)

    #Systeminfo
    elif action == "getsysteminfo":
        response = get_system_info()

    #Chat
    elif action == "getchatmessages":
        response = chat.get_chat_messages(username, request['time'], request['limit'], db)
    elif action == "getchatimage":
        response = chat.get_chat_image(username, request['imageid'], db)
    elif action == "sendchatmessage":
        response = chat.send_chat_message(username, request['data'], db)

    #Dashboard
    elif action == "getuserdashboarditems":
        response = dashboard.get_user_dashboard_items(username, db)
    elif action == "getuserfavouritedevices":
        response = dashboard.get_user_favourite_devices(username, db)
    elif action == "edituserdashboard":
        response = dashboard.edit_user_dashboard(username, request['dashboarddata'], db)
    elif action == "getuserdashboard":
        response = dashboard.get_user_dashboard(username, db)

    #Energie-Daten
    elif action == "getenergydata":
        response = energy_data.get_energy_data(username, request['room'], request['devicetype'], request['deviceid'], request['von'], request['bis'], db)
    elif action == "getdeviceenergydata":
        response = energy_data.get_device_energy_data(username, request['room'], request['devicetype'], request['deviceid'], request['von'], request['bis'], db)
    elif action == "getenergycourse":
        response = energy_data.get_energy_course(username, request['room'], request['von'], request['bis'], db)
    elif action == "setpowercost":
        response = energy_data.set_power_cost(username, request['cost'], db)
    elif action == "getpowercost":
        response = energy_data.get_power_cost(username, db)

    #Sensor-Daten
    elif action == "getsensordata":
        type = None
        if 'type' in request: type = request['type']

        id = None
        if 'id' in request: id = request['id']

        showeinheit = None
        if 'showeinheit' in request: showeinheit = request['showeinheit']
        response = get_sensor_data(username, request['room'], type, id, showeinheit, db)

    #User-Manager
    elif action == "getusers":
        response = get_users(username, db)
    elif action == "deleteuser":
        response = delete_user(username, request['name'], db)
    elif action == "addedituser":
        response = add_edit_user(username, request['name'], request['psw'], request['ip'], request['permissions'], db)

    #Gateway-Manager
    elif action == "getgateways":
        response = get_gateways(username, db)
    elif action == "addeditgateway":
        response = add_edit_gateway(username, request['type'], request['usr'], request['psw'], request['changepw'], request['ip'], request['port'],  request['gateway_type'], db)
    elif action == "deletegateway":
        response = delete_gateway(username, request['type'], db)
    elif action == "getgatewaydevices":
        response = get_gateway_devices(username, request['type'], db)
    elif action == "connectgateway":
        response = connect_gateway(username, request['type'], request['ip'], db)

    #TV-Programm
    elif action == "settvchannels":
        response = set_tv_channels(username, request['channels'], db)
    elif action == "gettvplan":
        response = get_tv_plan(username, request['time'], db)
    elif action == "getalltvchannels":
        response = get_all_tv_channels(username, db)

    #Einkaufsliste
    elif action == "getshoppinglist":
        response = shopping_list.get_shopping_list(username, db)
    elif action == "addeditshoppinglistitem":
        response = shopping_list.add_edit_shopping_list_item(username, request['id'],
                                                             request['amount'], request['name'], db)
    elif action == "deleteshoppinglistitem":
        response = shopping_list.delete_shopping_list_item(username, request['id'], db)

    #Sprachassistent
    elif action == "voicecommand":
        response = voice_command(username, request['text'], user_last_location, None, db)
    elif action == "getvoicereplaceitems":
        response = get_voice_replace_items(username, db)
    elif action == "addeditvoicereplaceitem":
        response = add_edit_voice_replace_item(username, request['replacewith'], request['itemstoreplace'], db)
    elif action == "deletevoicereplaceitem":
        response = delete_voice_replace_item(username, request['replacewith'], db)

    #Smart Speakers
    elif action == "getsmartspeakers":
        response = get_smart_speakers(username, db)

    #Heizpläne
    elif action == "addeditheatingschemeitem":
        response = add_edit_heating_scheme_item(username, request['id'], request['time'], request['value'],
            request['active'], request['days'], request['data'],db)
    elif action == "deleteheatingschemeitem":
        response = delete_heating_scheme_item(username, request['id'], db)
    elif action == "getheatingschemeitems":
        response = get_heating_scheme_items(username, request['day'], request['rooms'], db)
    elif action == "setheatingschemeitemactive":
        response = set_heating_scheme_item_active(username, request['id'], request['active'], db)
    elif action == "getheatingschemeitemdata":
        response = get_heating_scheme_item_data(username, request['id'], db)
    elif action == "setheatingschemeactive":
        response = set_heating_scheme_active(username, request['active'], db)
    elif action == "isheatingschemeactive":
        response = is_heating_scheme_active(username, db)

    #API-Keys
    elif action == "getapikeydata":
        response = get_all_api_key_data(username, db)
    elif action == "setapikey":
        response = set_api_key(username, request['service'], request['apikey'], db)

    #Media Center
    elif action == "getmediacenters":
        response = media_center.get_media_centers(username, db)
    elif action == "mediacentercontrol":
        response = media_center.media_remote_action(request['type'], request['id'], request['remoteaction'], db)
    elif action == "mediacentersendtext":
        response = media_center.media_center_send_text(request['type'], request['id'], request['text'], db)
    elif action == "mediacentermusic":
        response = media_center.get_media_center_music(request['type'], request['id'],
                                                       request['limit'], request['offset'], db)
    elif action == "mediacenterartists":
        response = media_center.get_media_center_artists(request['type'], request['id'],
                                                         request['limit'], request['offset'], db)
    elif action == "mediacenteralbums":
        response = media_center.get_media_center_albums(request['type'], request['id'],
                                                        request['limit'], request['offset'], db)
    elif action == "mediacentermusicgenres":
        response = media_center.get_media_center_music_genres(request['type'], request['id'],
                                                              request['limit'], request['offset'], db)
    elif action == "mediacentertvshows":
        response = media_center.get_media_center_shows(request['type'], request['id'],
                                                       request['limit'], request['offset'], db)
    elif action == "mediacentertvshowseasons":
        response = media_center.get_media_center_show_seasons(request['type'], request['id'], request['limit'],
                                                              request['offset'], request['showid'], db)
    elif action == "mediacentertvshowepisodes":
        response = media_center.get_media_center_show_episodes(request['type'], request['id'], request['limit'],
                                                    request['offset'], request['showid'], request['seasonid'], db)
    elif action == "mediacentermovies":
        response = media_center.get_media_center_movies(request['type'], request['id'],
                                                        request['limit'], request['offset'], db)
    elif action == "mediacentermoviegenres":
        response = media_center.get_media_center_movie_genres(request['type'], request['id'],
                                                              request['limit'], request['offset'], db)
    elif action == "mediacenterplaying":
        response = media_center.get_media_menter_playing(request['type'], request['id'], db)

    #Firebase-Token aktualisieren
    elif action == "updatefcmtoken":
        response = set_user_fcm_token(username, request['token'], db)

    #Heizung
    elif action == "heatingcontrol":
        response = heating_control(username, request['type'], request['id'], request['value'], db)
    elif action == "controlroomheating":
        response = control_room_heating(username, request['location'], request['value'], db)
    elif action == "getthermostats":
        response = get_thermostats(username, request['room'], request['type'], request['id'], db)

    #Räume
    elif action == "addeditroom":
        response = add_edit_room(username, request['roomname'], request['location'], request['icon'], db)
    elif action == "moveitemsanddeleteoldroom":
        response = move_items_and_delete_old_room(username, request['oldroom'], request['newroom'], db)
    elif action == "deleteroomwithitems":
        response = delete_room_with_items(username, request['location'], db)

    # Geräte-Manager
    elif action == "addeditdevice":
        response = add_edit_device(username, request['id'], request['type'], request['data'], db)
    elif action == "deletedevice":
        response = delete_device(username, request['type'], request['id'], db)
    elif action == "getdevicedata":
        response = get_device_data(username, request['type'], request['id'], db)

    #AR-Control
    elif action == "arcontrol":
        response = ar_control.ar_control(username, request['imagedata'], db)
    elif action == "getarcontrolclasses":
        response = ar_control.get_ar_control_classes(db)
    elif action == "savearcontrolclass":
        response = ar_control.save_ar_control_class(username, request['id'], request['data'], request['classname'], db)
    elif action == "getarcontrolclassimages":
        response = ar_control.get_ar_control_class_images(request['class'], request['show'], request['offset'], db)
    elif action == "startarcontroltraining":
        response = ar_control.start_ar_training(username, db)
    elif action == "changearcontrolimageclass":
        response = ar_control.change_ar_image_class(request['ids'], request['newclass'], db)
    elif action == "getarcontrolimages":
        response = ar_control.get_ar_control_image(request['id'], db)
    elif action == "getarimageclassifierperformancesettings":
        response = ar_control.get_performance_settings(username, db)
    elif action == "setarimageclassifierperformancesettings":
        response = ar_control.set_performance_settings(username, request['data'], db)
    elif action == "uploadarcontrolimages":
        response = ar_control.upload_images(username, request['data'], request['class'], db)
    elif action == "deletearcontrolimages":
        response = ar_control.delete_ar_control_images(request['ids'], db)

    #Gesichtserkennung
    elif action == "getpeopleclasses":
        response = people_classifier.get_people_classes(db)
    elif action == "savepeopleclass":
        response = people_classifier.save_people_class(username, request['id'], request['data'], request['classname'], db)
    elif action == "startpeopletraining":
        response = people_classifier.start_people_training(username, db)
    elif action == "getpeopleimageclassifierperformancesettings":
        response = people_classifier.get_performance_settings(username, db)
    elif action == "setpeopleimageclassifierperformancesettings":
        response = people_classifier.set_performance_settings(username, request['data'], db)
    elif action == "changepeopleclassifierimageclass":
        response = people_classifier.change_people_image_class(request['ids'], request['newclass'], db)
    elif action == "getpeopleclassifierimage":
        response = people_classifier.get_people_image(request['id'], db)
    elif action == "getpeopleclassifierimages":
        response = people_classifier.get_people_images(request['class'], request['show'], request['offset'], db)
    elif action == "uploadpeopleimages":
        response = people_classifier.upload_images(username, request['data'], request['class'], db)
    elif action == "classifyperson":
        response = people_classifier.classify_person(request['imagedata'], db)
    elif action == "deletepeopleimages":
        response = people_classifier.delete_people_images(request['ids'], db)

    #Automation
    elif action == "getautomationrules":
        response = get_automations(username, request['location'], db)
    elif action == "addeditautomationrule":
        response = add_edit_automation_rule(username, request['location'], request['id'], request['name'],
                                            request['triggerdata'], request['conditiondata'], request['actiondata'], request['isactive'], db)
    elif action == "deleteautomationrule":
        response = delete_automation_rule(username, request['id'], db)
    #Eigene Sprachbefehle
    elif action == "getvoicecommands":
        response = get_voice_commands(db)
    elif action == "addeditvoicecommand":
        response = add_edit_voice_command(username, request['id'], request['name'], request['command_data'], request['response_data'], request['action_data'], db)
    elif action == "deletevoicecommand":
        response = delete_voice_command(username, request['id'], db)
    #Szenen
    elif action == "getallscenes":
        response = get_all_scenes(username, db)
    elif action == "getscenes":
        response = get_scenes(username, request['location'], db)
    elif action == "addeditscene":
        response = add_edit_scene(username, request['id'], request['name'], request['location'], request['action_data'], db)
    elif action == "deletescene":
        response = delete_scene(username, request['id'], db)
    elif action == "runscene":
        response = run_scene(username, request['id'], db)
    #Haushaltskasse
    elif action == "gethomebudgetdata":
        response = get_home_budget_data(username, request['startdate'], db)
    elif action == "gethomebudgetdatadayitems":
        response = get_home_budget_data_day_items(username, request['date'], db)
    elif action == "gethomebudgetdatagraph":
        response = get_home_budget_data_graph(username, request['startdate'], request['enddate'], db)
    elif action == "addedithomebudgetdata":
        response = add_edit_home_budget_data(username, request['id'], request['date'], request['info'], request['amount'], db)
    elif action == "deletehomebudgetdata":
        response = delete_home_budget_data(username, request['id'], db)
    #GPS data
    elif action == "updategps":
        response = gps_data.update_gps(username, request['time'], request['lat'], request['lng'], db)
    elif action == "getgpslocations":
        response = gps_data.get_gps_locations(username, db)
    #Places
    elif action == "addeditplace":
        response = places.add_edit_place(username, request['id'], request['name'], request['address'], request['latitude'], request['longitude'], db)
    elif action == "getmyplaces":
        response = places.get_my_places(username, db)
    elif action == "deleteplace":
        response = places.delete_place(username, request['id'], db)
    #Ernährungsmanager
    elif action == "submitfood":
        response = nutrition_data.submit_food(username, request['name'], request['calories'], request['portionsize'], request['portionunit'], request['protein'], request['fat'],
        request['saturated'], request['unsaturated'], request['carbs'], request['sugar'], request['ean'], db)
    elif action == "getusernutritionoverview":
        response = nutrition_data.get_user_nutrition_overview(username, db)
    elif action == "getuserdaynutritionitems":
        response = nutrition_data.get_user_day_nutrition_items(username, request['date'], db)
    elif action == "addedituserdaynutritionitem":
        response = nutrition_data.add_edit_user_day_nutrition_item(username, request['id'], request['date'], request['daytime'], request['name'],
                                                    request['eatenportionsize'], request['portionsize'], request['portionunit'],
                                         request['calories'], request['fat'], request['saturated'], request['unsaturated'],
                                                    request['carbs'], request['sugar'], request['protein'], db)
    elif action == "loadnutritionmanagersettings":
        response = nutrition_data.load_user_settings(username, db)
    elif action == "deletefooditem":
        response = nutrition_data.delete_food_item(username, request['id'], db)
    elif action == "savenutritionmanagersettings":
        response = nutrition_data.save_user_settings(username, request['height'], request['weight'], request['birthdate'], request['mode'], request['activity'], db)
    elif action == "movenutritionitem":
        response = nutrition_data.move_item(username, request['id'], request['date'], request['daytime'], request['deleteold'], db)
    # Updates
    elif action == "checkforupdates":
        response = check_for_updates(db)
    elif action == "updatesystem":
        response = start_new_thread(update_system, ())
    else:
        return {'result': 'nosuchaction'}

    #Ausgeben
    return json.dumps(response)

    '''
    //Kalender
        case "getcalendaritems":
            $result = getCalendarItems($_POST['cal_user'], $db);
            break;
        case "getcalendaritemsforday":
            $result = getCalendarItemsForDay($_POST['USERNAME'], $_POST['date'], $db);
            break;
        case "getcalendardataformonth":
            $result = getCalendarDataForMonth($_POST['USERNAME'], $_POST['month'], $db);
            break;
        case "getcalendariteminfo":
            $result = getCalendarItemInfo($_POST['id'], $db);
            break;
        case "addeditcalendaritem":
            $result = addEditCalendarItem($_POST['id'], $_POST['name'],
            $_POST['start'], $_POST['end'], $_POST['note'], $_POST['repeat'], $_POST['participants'], $db);
            break;
        case "deletecalendaritem":
            $result = deleteCalendarItem($_POST['id'], $db);
            break;
    '''

    '''
        case "runscene":
            $result = runScene($_POST['room'], $_POST['name'], $db);
            break;
        case "createscene":
            $result = createScene($_POST['devices'], $_POST['rooms'], $_POST['types'], $_POST['values'],
				$_POST['conditions'], $_POST['room'], $_POST['name'], $db);
            break;
        case "getscenes":
            $result = getScenes($_POST['room'], $db);
            break;
			
		//Noch nicht im Tutorial
		case "shouldshowmorninginfo":
			//$result = iotDeviceControl($_POST['device'], $_POST['room'], 'getinfo', "", $db);
			break;
		case "getmorninginfo":
			//$result = iotDeviceControl($_POST['device'], $_POST['room'], 'getinfo', "", $db);
			break;
		case "getmorninginfosettings":
			//$result = iotDeviceControl($_POST['device'], $_POST['room'], 'getinfo', "", $db);
			break;
		case "setmorninginfosettings":
			//$result = iotDeviceControl($_POST['device'], $_POST['room'], 'getinfo', "", $db);
			break;
		case "rfidvalidation":
			$result = rfidValidation($_POST['uid'], $db);
			break;
		case "rfidtrigger":
			$result = rfidTrigger($_POST['uid'], $_POST['triggerid'], $db);
			break;
		case "heatingcontrol":
			$result = heatingControl($_POST['room'], $_POST['type'], $_POST['id'], $_POST['value'], $db);
			break;
		case "getheatingdata":
			$result = getHeatingData($_POST['room'], $_POST['type'], $_POST['id'], $_POST['all_data'], $db);
			break;
		case "controldiydevice":
			$result = diyDeviceControl($_POST['device'], $_POST['room'], $_POST['diyaction'], $_POST['value'], $db);
			break;
		case "getdiyinfo":
			$result = diyDeviceControl($_POST['device'], $_POST['room'], 'getinfo', "", $db);
			break;
		case "getreeddata":
			$result = getReedData($_POST['room'], $_POST['type'], $_POST['id'], $db);
			break;
		case "addedittargetid":
			$result = addEditTargetID($_POST['username'], $_POST['deviceid'], $_POST['targetid'], $db);
			break;
        case "getpowermeterdata":
            $result = getSensorData($_POST['room'], $_POST['type'], $_POST['id'], $_POST['hide_einheit'], $db);
            break;
        case "getdimmer":
            $result = getDimmer($_POST['room'], $_POST['type'], $_POST['id'], $db);
            break;
        case "setdimmer":
            $result = setDimmer($_POST['room'], $_POST['type'], $_POST['id'], $_POST['value'], $db);
            break;
			
		//Stromverbrauch
		case "getenergydata":
			$result = getEnergyData($_POST['room'], $_POST['devicetype'], $_POST['deviceid'], $_POST['von'], $_POST['bis'], $db);
			break;
		case "getdeviceenergydata":
			$result = getDeviceEnergyData($_POST['type'], $_POST['device'], $_POST['von'], $_POST['bis'], $db);
			break;
		case "setpowercost":
			$result = setPowerCost($_POST['cost'], $db);
			break;
		case "getpowercost":
			$result = getPowerCost($db);
			break;
			
		//Überwachungskamera
		case "getsurveillancefootage":
			$result = getSurveillanceFootage($_POST['id'], $_POST['filterdata'], $_POST['offset'], $_POST['limit'], $db);
			break;
		case "getsurveillancethumbnail":
			$result = getSurveillanceThumbnail($_POST['id'], $db);
			break;
		case "getsurveillancefootagevideo":
			$result = getSurveillanceFootageVideo($_POST['id'], $db);
			break;
		case "getipcameradata":
			$result = getIpCameraData($_POST['room'], $_POST['id'], $db);
			break;
		
		//Türspion
		case "addpeepholeimages":
			$result = addPeepholeImages($_POST['imagedata'], $db);
			break;
		case "getpeepholeclassimages":
			$result = getPeepholeClassImages($_POST['class'], $_POST['show'], $_POST['offset'], $db);
			break;
		case "changepeepholeimageclass":
			$result = changePeepholeClass($_POST['ids'], $_POST['newclass'], $db);
			break;
		case "getpeepholeimage":
			$result = getPeepholeImage($_POST['id'], $db);
			break;
		case "addeditpeepholeclass":
			$result = addEditPeepHoleClass($_POST['id'], $_POST['name'], $db);
			break;
		case "deletepeepholeclass":
			$result = deletePeepHoleClass($_POST['id'], $db);
			break;
		
		//Bild-Klassifizierer Einstellungen
		case "getimageclassifierperformancesettings":
			$result = getImageClassifierPerformanceSettings($db);
			break;
		case "setimageclassifierperformancesettings":
			$result = setImageClassifierPerformanceSettings($_POST['data'], $db);
			break;
		
		//Manager
		case "getdevicedata":
			$result = getDeviceData($_POST['type'], $_POST['id'], $db);
			break;
		case "deletedevice":
			$result = deleteDevice($_POST['type'], $_POST['id'], $db);
			break;
		case "addeditdevice":
			$result = addEditDevice($_POST['id'], $_POST['type'], $_POST['data'], $db);
			break;
		
		//Kalender
		case "getcalendaritems":
			$result = getCalendarItems($_POST['cal_user'], $db);
			break;
		case "getcalendaritemsforday":
			$result = getCalendarItemsForDay($_POST['USERNAME'], $_POST['date'], $db);
			break;
		case "getcalendardataformonth":
			$result = getCalendarDataForMonth($_POST['USERNAME'], $_POST['month'], $db);
			break;
		case "getcalendariteminfo":
			$result = getCalendarItemInfo($_POST['id'], $db);
			break;
		case "addeditcalendaritem":
			$result = addEditCalendarItem($_POST['id'], $_POST['name'],
			$_POST['start'], $_POST['end'], $_POST['note'], $_POST['repeat'], $_POST['participants'], $db);
			break;
		case "deletecalendaritem":
			$result = deleteCalendarItem($_POST['id'], $db);
			break;
		
		//MediaCenter
		case "getmediacenters":
			$result = getMediaCenters($db);
			break;
		case "mediacentercontrol":
			$result = remoteAction($_POST['type'], $_POST['id'], $_POST['remoteaction'], $db);
			break;
		case "mediacentersendtext":
			$result = mediaCenterSendText($_POST['type'], $_POST['id'], $_POST['text'], $db);
			break;
		case "mediacentermusic":
			$result = getMediaCenterMusic($_POST['type'], $_POST['id'], $_POST['limit'], $_POST['offset'], $db);
			break;
		case "mediacenterartists":
			$result = getMediaCenterArtists($_POST['type'], $_POST['id'], $_POST['limit'], $_POST['offset'], $db);
			break;
		case "mediacenteralbums":
			$result = getMediaCenterAlbums($_POST['type'], $_POST['id'], $_POST['limit'], $_POST['offset'], $db);
			break;
		case "mediacentermusicgenres":
			$result = getMediaCenterMusicGenres($_POST['type'], $_POST['id'], $_POST['limit'], $_POST['offset'], $db);
			break;
		case "mediacentertvshows":
			$result = getMediaCenterShows($_POST['type'], $_POST['id'], $_POST['limit'], $_POST['offset'], $db);
			break;
		case "mediacentertvshowseasons":
			$result = getMediaCenterShowSeasons($_POST['type'], $_POST['id'], $_POST['limit'], $_POST['offset'], $_POST['showid'], $db);
			break;
		case "mediacentertvshowepisodes":
			$result = getMediaCenterShowEpisodes($_POST['type'], $_POST['id'], $_POST['limit'], $_POST['offset'], $_POST['showid'], $_POST['seasonid'], $db);
			break;
		case "mediacentermovies":
			$result = getMediaCenterMovies($_POST['type'], $_POST['id'], $_POST['limit'], $_POST['offset'], $db);
			break;
		case "mediacentermoviegenres":
			$result = getMediaCenterMovieGenres($_POST['type'], $_POST['id'], $_POST['limit'], $_POST['offset'], $db);
			break;
		case "mediacenterplaying":
			$result = getMediaCenterPlaying($_POST['type'], $_POST['id'], $db);
			break;
			
		//Update
		case "checkforupdates":
			$result = checkForUpdates($db);
			break;
		case "updatesystem":
			$result = updateSystem($db);
			break;
        '''