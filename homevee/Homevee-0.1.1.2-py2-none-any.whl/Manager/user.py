#!/usr/bin/python
# -*- coding: utf-8 -*-
import json

from homevee.Helper.helper_functions import has_permission, hash_password
from homevee.Functions.room_data import get_rooms
from homevee.Manager.places import get_place


def set_user_fcm_token(username, token, db):
    with db:
        cur = db.cursor()

        try:
            cur.execute("INSERT INTO PUSH_NOTIFICATION_TOKENS (USERNAME, TOKEN) VALUES (:user, :token)",
                {'token':token, 'user': username})
        except:
            return {'result': 'ok'}

    return {'result': 'ok'}

def get_users(username, db):
    if not has_permission(username, "admin", db):
        return {'status': 'noadmin'}

    with db:
        # Nutzer laden
        cur = db.cursor()
        cur.execute("SELECT * FROM USERDATA")

        users = []

        room_array = get_rooms(username, db)['rooms']

        for user in cur.fetchall():
            permission_array = json.loads(user['PERMISSIONS'])['permissions']

            permission_output = []

            if "admin" in permission_array:
                permission_output.append({'name': "Administrator", 'key': "admin"})

            for room in room_array:
                if str(room['location']) in permission_array:
                    permission_output.append({'name': room['name'], 'key': room['location']})

            if user['AT_HOME']:
                at_home = "true"
            else:
                at_home = "false"

            user_current_place = get_place(user['CURRENT_LOCATION'], db)

            user_location = None
            if(user_current_place is not None):
                user_location = user_current_place['NAME']

            user_item = {'username': user['USERNAME'], 'permissions': permission_output,
                'ip': user['IP'], 'at_home': at_home, 'location': user_location}

            users.append(user_item)

        cur.close()

        return {'userdata': users}

def delete_user(username, user_to_delete, db):
    if not has_permission(username, "admin", db):
        return {'status': 'noadmin'}

    with db:
        cur = db.cursor()
        cur.execute("DELETE FROM USERDATA WHERE USERNAME == :user'", {'user': user_to_delete})

        cur.close()

        #Bedingung anpassen
        if True:
            #delete_target_ids(username, user_to_delete, db)
            return {'status': 'ok'}
        else:
            return {'status': 'admin'}

def add_edit_user(username, name, psw, ip, permissions, db):
    if not has_permission(username, "admin", db):
        return {'status': 'noadmin'}

    hashed_pw, salt = hash_password(psw)

    param_array = {'username': name, 'ip': ip, 'permissions': permissions, 'password': hashed_pw, 'salt':salt}
    param_array2 = {'username': name, 'ip': ip, 'permissions': permissions}

    with db:
        cur = db.cursor()

        print psw

        if psw == "" or psw is None:
            print "not updating password"
            cur.execute("UPDATE OR IGNORE 'userdata' SET USERNAME = :username, IP = :ip, PERMISSIONS = :permissions WHERE USERNAME == :username;",
                    param_array2)
        else:
            print "updating password"
            cur.execute("UPDATE OR IGNORE 'userdata' SET USERNAME = :username, IP = :ip, PERMISSIONS = :permissions, PASSWORD = :password, PW_SALT = :salt WHERE USERNAME == :username;",
                param_array)

        cur.execute("INSERT OR IGNORE INTO 'userdata' (USERNAME, PASSWORD, PW_SALT, IP, PERMISSIONS) VALUES (:username, :password, :salt, :ip, :permissions);",
            param_array)

    return {'status': 'ok'}



    '''
    $paramArray = array('username' => $name, 'ip' => $ip, 'permissions' => $permissions, 'password' => password_hash($psw, 1));
	$paramArray2 = array('username' => $name, 'ip' => $ip, 'permissions' => $permissions);
	
	//Nutzer bearbeiten bzw. hinzufügen
    
	if($psw == null || $psw == ""){
		$updateQuery = $db->prepare("UPDATE OR IGNORE 'userdata'
							SET USERNAME = :username, IP = :ip, PERMISSIONS = :permissions
							WHERE USERNAME == :username;");
		$updateQuery->execute($paramArray2);
	}
	else{
		$updateQuery = $db->prepare("UPDATE OR IGNORE 'userdata'
							SET USERNAME = :username, PASSWORD = :password, IP = :ip, PERMISSIONS = :permissions
							WHERE USERNAME == :username;");
		$updateQuery->execute($paramArray);
	}
	
	$insertQuery = $db->prepare("INSERT OR IGNORE INTO 'userdata' (USERNAME, PASSWORD, IP, PERMISSIONS)
							VALUES (:username, :password, :ip, :permissions);");
	
	$insertQuery->execute($paramArray);
	
	if($updateQuery == true && $insertQuery == true) return "ok";
	else return "error";
    '''