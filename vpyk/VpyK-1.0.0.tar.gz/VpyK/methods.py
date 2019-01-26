'''
import requests
from bs4 import requests

r = requests.get('https://vk.com/dev/methods').text
soup = BautifulSoup(r)

arr = soup.findAll('span', {'class': 'dev_methods_list_span'})

for a in arr:
    s += 'def {}(self):\n    pass\n\n\n'.format(a.text.replace('.', '_'))
'''
import json
import requests
import time

class methods:
    def test(self):
        print(self)
        print(self.logging)

    def reset_params(self):
        self.params = {
                  'access_token': self.token,
                  'v': self.v
                 }


    def account_ban(self, owner_id):
        while True:
            self.reset_params()
            self.params['owner_id'] = owner_id

            r = requests.get('https://api.vk.com/method/account.ban', params = self.params)
            r = json.loads(r.text)
            if r.get('response'):
                return r
            else:
                time.sleep(0.5)
                self.logging(r)

    def account_changePassword(self):
        pass


    def account_getActiveOffers(self):
        pass


    def account_getAppPermissions(self):
        pass


    def account_getBanned(self, offset, count):
        while True:
            self.reset_params()
            self.params['offset'] = offset
            self.params['count'] = count

            r = requests.get('https://api.vk.com/method/account.account.getBanned', params = self.params)
            r = json.loads(r.text)
            if r.get('response'):
                return r
            else:
                time.sleep(0.5)
                self.logging(r)

    def account_getCounters(self):
        pass


    def account_getInfo(self):
        pass


    def account_getProfileInfo(self):
        pass


    def account_getPushSettings(self):
        pass


    def account_registerDevice(self):
        pass


    def account_saveProfileInfo(self):
        pass


    def account_setInfo(self):
        pass


    def account_setNameInMenu(self):
        pass


    def account_setOffline(self):
        pass


    def account_setOnline(self):
        pass


    def account_setPushSettings(self):
        pass


    def account_setSilenceMode(self):
        pass


    def account_unban(self):
        pass


    def account_unregisterDevice(self, device_id, sandbox = 0):
        while True:
            self.reset_params()
            self.params['device_id'] = device_id
            self.params['sandbox'] = sandbox

            r = requests.get('https://api.vk.com/method/account.unregisterDevice', params = self.params)
            r = json.loads(r.text)
            if r.get('response'):
                return r
            else:
                time.sleep(0.5)
                self.logging(r)

    def appWidgets_getAppImageUploadServer(self):
        pass


    def appWidgets_getAppImages(self):
        pass


    def appWidgets_getGroupImageUploadServer(self):
        pass


    def appWidgets_getGroupImages(self):
        pass


    def appWidgets_getImagesById(self):
        pass


    def appWidgets_saveAppImage(self):
        pass


    def appWidgets_saveGroupImage(self):
        pass


    def appWidgets_update(self):
        pass


    def apps_deleteAppRequests(self):
        pass


    def apps_get(self):
        pass


    def apps_getCatalog(self):
        pass


    def apps_getFriendsList(self):
        pass


    def apps_getLeaderboard(self):
        pass


    def apps_getScopes(self):
        pass


    def apps_getScore(self):
        pass


    def apps_sendRequest(self):
        pass


    def auth_checkPhone(self):
        pass


    def auth_restore(self):
        pass


    def board_addTopic(self):
        pass


    def board_closeTopic(self):
        pass


    def board_createComment(self):
        pass


    def board_deleteComment(self):
        pass


    def board_deleteTopic(self):
        pass


    def board_editComment(self):
        pass


    def board_editTopic(self):
        pass


    def board_fixTopic(self):
        pass


    def board_getComments(self):
        pass


    def board_getTopics(self):
        pass


    def board_openTopic(self):
        pass


    def board_restoreComment(self):
        pass


    def board_unfixTopic(self):
        pass


    def database_getChairs(self):
        pass


    def database_getCities(self):
        pass


    def database_getCitiesById(self):
        pass


    def database_getCountries(self):
        pass


    def database_getCountriesById(self):
        pass


    def database_getFaculties(self):
        pass


    def database_getRegions(self):
        pass


    def database_getSchoolClasses(self):
        pass


    def database_getSchools(self):
        pass


    def database_getUniversities(self):
        pass


    def docs_add(self):
        pass


    def docs_delete(self):
        pass


    def docs_edit(self):
        pass


    def docs_get(self):
        pass


    def docs_getById(self):
        pass


    def docs_getMessagesUploadServer(self):
        pass


    def docs_getTypes(self):
        pass


    def docs_getUploadServer(self):
        pass


    def docs_getWallUploadServer(self):
        pass


    def docs_save(self):
        pass


    def docs_search(self):
        pass


    def execute(self):
        pass


    def fave_addGroup(self):
        pass


    def fave_addLink(self):
        pass


    def fave_addUser(self):
        pass


    def fave_getLinks(self):
        pass


    def fave_getMarketItems(self):
        pass


    def fave_getPhotos(self):
        pass


    def fave_getPosts(self):
        pass


    def fave_getUsers(self):
        pass


    def fave_getVideos(self):
        pass


    def fave_removeGroup(self):
        pass


    def fave_removeLink(self):
        pass


    def fave_removeUser(self):
        pass


    def friends_add(self):
        pass


    def friends_addList(self):
        pass


    def friends_areFriends(self):
        pass


    def friends_delete(self):
        pass


    def friends_deleteAllRequests(self):
        pass


    def friends_deleteList(self):
        pass


    def friends_edit(self):
        pass


    def friends_editList(self):
        pass


    def friends_get(self):
        pass


    def friends_getAppUsers(self):
        pass


    def friends_getByPhones(self):
        pass


    def friends_getLists(self):
        pass


    def friends_getMutual(self):
        pass


    def friends_getOnline(self):
        pass


    def friends_getRecent(self):
        pass


    def friends_getRequests(self):
        pass


    def friends_getSuggestions(self):
        pass


    def friends_search(self):
        pass


    def gifts_get(self):
        pass


    def groups_addCallbackServer(self):
        pass


    def groups_addLink(self):
        pass


    def groups_approveRequest(self):
        pass


    def groups_ban(self):
        pass


    def groups_create(self):
        pass


    def groups_deleteCallbackServer(self):
        pass


    def groups_deleteLink(self):
        pass


    def groups_disableOnline(self):
        pass


    def groups_edit(self):
        pass


    def groups_editCallbackServer(self):
        pass


    def groups_editLink(self):
        pass


    def groups_editManager(self):
        pass


    def groups_editPlace(self):
        pass


    def groups_enableOnline(self):
        pass


    def groups_get(self):
        pass


    def groups_getAddresses(self):
        pass


    def groups_getBanned(self):
        pass


    def groups_getById(self, group_ids=None, group_id=None, fields=None):
	    while True:
	            self.reset_params()
	            if group_ids: self.params['user_id'] = group_ids
	            if group_id: self.params['group_id'] = group_id
	            if fields: self.params['fields'] = fields

	            r = requests.get('https://api.vk.com/method/groups.getById', params = self.params)
	            r = json.loads(r.text)
	            if r.get('response'):
	                return r
	            else:
	                time.sleep(0.5)
	                self.logging(r)



    def groups_getCallbackConfirmationCode(self):
        pass


    def groups_getCallbackServers(self):
        pass


    def groups_getCallbackSettings(self):
        pass


    def groups_getCatalog(self):
        pass


    def groups_getCatalogInfo(self):
        pass


    def groups_getInvitedUsers(self):
        pass


    def groups_getInvites(self):
        pass


    def groups_getLongPollServer(self):
        pass


    def groups_getLongPollSettings(self):
        pass


    def groups_getMembers(self):
        pass


    def groups_getOnlineStatus(self):
        pass


    def groups_getRequests(self):
        pass


    def groups_getSettings(self):
        pass


    def groups_getTokenPermissions(self):
        pass


    def groups_invite(self):
        pass


    def groups_isMember(self):
        pass


    def groups_join(self):
        pass


    def groups_leave(self):
        pass


    def groups_removeUser(self):
        pass


    def groups_reorderLink(self):
        pass


    def groups_search(self):
        pass


    def groups_setCallbackSettings(self):
        pass


    def groups_setLongPollSettings(self):
        pass


    def groups_unban(self):
        pass


    def leadForms_create(self):
        pass


    def leadForms_delete(self):
        pass


    def leadForms_get(self):
        pass


    def leadForms_getLeads(self):
        pass


    def leadForms_getUploadURL(self):
        pass


    def leadForms_list(self):
        pass


    def leadForms_update(self):
        pass


    def likes_add(self):
        pass


    def likes_delete(self):
        pass


    def likes_getList(self):
        pass


    def likes_isLiked(self, user_id, _type, owner_id, item_id):
        while True:
            self.reset_params()
            self.params['user_id'] = user_id
            self.params['type'] = _type
            self.params['owner_id'] = owner_id
            self.params['item_id'] = item_id

            r = requests.get('https://api.vk.com/method/likes.isLiked', params = self.params)
            r = json.loads(r.text)
            if r.get('response'):
                return r
            else:
                time.sleep(0.5)
                self.logging(r)


    def market_add(self):
        pass


    def market_addAlbum(self):
        pass


    def market_addToAlbum(self):
        pass


    def market_createComment(self):
        pass


    def market_delete(self):
        pass


    def market_deleteAlbum(self):
        pass


    def market_deleteComment(self):
        pass


    def market_edit(self):
        pass


    def market_editAlbum(self):
        pass


    def market_editComment(self):
        pass


    def market_get(self):
        pass


    def market_getAlbumById(self):
        pass


    def market_getAlbums(self):
        pass


    def market_getById(self):
        pass


    def market_getCategories(self):
        pass


    def market_getComments(self):
        pass


    def market_removeFromAlbum(self):
        pass


    def market_reorderAlbums(self):
        pass


    def market_reorderItems(self):
        pass


    def market_report(self):
        pass


    def market_reportComment(self):
        pass


    def market_restore(self):
        pass


    def market_restoreComment(self):
        pass


    def market_search(self):
        pass


    def messages_addChatUser(self):
        pass


    def messages_allowMessagesFromGroup(self):
        pass


    def messages_createChat(self):
        pass


    def messages_delete(self):
        pass


    def messages_deleteChatPhoto(self):
        pass


    def messages_deleteConversation(self):
        pass


    def messages_denyMessagesFromGroup(self):
        pass


    def messages_edit(self):
        pass


    def messages_editChat(self):
        pass


    def messages_getByConversationMessageId(self):
        pass


    def messages_getById(self):
        pass


    def messages_getChat(self):
        pass


    def messages_getChatPreview(self):
        pass


    def messages_getConversationMembers(self):
        pass


    def messages_getConversations(self):
        pass


    def messages_getConversationsById(self):
        pass


    def messages_getHistory(self):
        pass


    def messages_getHistoryAttachments(self):
        pass


    def messages_getImportantMessages(self):
        pass


    def messages_getInviteLink(self):
        pass


    def messages_getLastActivity(self):
        pass


    def messages_getLongPollHistory(self):
        pass


    def messages_getLongPollServer(self):
        pass


    def messages_isMessagesFromGroupAllowed(self):
        pass


    def messages_joinChatByInviteLink(self):
        pass


    def messages_markAsAnsweredConversation(self):
        pass


    def messages_markAsImportant(self):
        pass


    def messages_markAsImportantConversation(self):
        pass


    def messages_markAsRead(self):
        pass


    def messages_pin(self):
        pass


    def messages_removeChatUser(self):
        pass


    def messages_restore(self):
        pass


    def messages_search(self):
        pass


    def messages_searchConversations(self):
        pass


    def messages_send(self):
        pass


    def messages_setActivity(self):
        pass


    def messages_setChatPhoto(self):
        pass


    def messages_unpin(self):
        pass


    def newsfeed_addBan(self):
        pass


    def newsfeed_deleteBan(self):
        pass


    def newsfeed_deleteList(self):
        pass


    def newsfeed_get(self):
        pass


    def newsfeed_getBanned(self):
        pass


    def newsfeed_getComments(self):
        pass


    def newsfeed_getDiscoverForContestant(self):
        pass


    def newsfeed_getLists(self):
        pass


    def newsfeed_getMentions(self):
        pass


    def newsfeed_getRecommended(self):
        pass


    def newsfeed_getSuggestedSources(self):
        pass


    def newsfeed_ignoreItem(self):
        pass


    def newsfeed_saveList(self):
        pass


    def newsfeed_search(self):
        pass


    def newsfeed_unignoreItem(self):
        pass


    def newsfeed_unsubscribe(self):
        pass


    def notes_add(self):
        pass


    def notes_createComment(self):
        pass


    def notes_delete(self):
        pass


    def notes_deleteComment(self):
        pass


    def notes_edit(self):
        pass


    def notes_editComment(self):
        pass


    def notes_get(self):
        pass


    def notes_getById(self):
        pass


    def notes_getComments(self):
        pass


    def notes_restoreComment(self):
        pass


    def notifications_get(self):
        pass


    def notifications_markAsViewed(self):
        pass


    def notifications_sendMessage(self):
        pass


    def pages_clearCache(self):
        pass


    def pages_get(self):
        pass


    def pages_getHistory(self):
        pass


    def pages_getTitles(self):
        pass


    def pages_getVersion(self):
        pass


    def pages_parseWiki(self):
        pass


    def pages_save(self):
        pass


    def pages_saveAccess(self):
        pass


    def photos_confirmTag(self):
        pass


    def photos_copy(self):
        pass


    def photos_createAlbum(self):
        pass


    def photos_createComment(self):
        pass


    def photos_delete(self):
        pass


    def photos_deleteAlbum(self):
        pass


    def photos_deleteComment(self):
        pass


    def photos_edit(self):
        pass


    def photos_editAlbum(self):
        pass


    def photos_editComment(self):
        pass


    def photos_get(self):
        pass


    def photos_getAlbums(self):
        pass


    def photos_getAlbumsCount(self):
        pass


    def photos_getAll(self):
        pass


    def photos_getAllComments(self):
        pass


    def photos_getById(self):
        pass


    def photos_getChatUploadServer(self):
        pass


    def photos_getComments(self):
        pass


    def photos_getMarketAlbumUploadServer(self):
        pass


    def photos_getMarketUploadServer(self):
        pass


    def photos_getMessagesUploadServer(self):
        pass


    def photos_getNewTags(self):
        pass


    def photos_getOwnerCoverPhotoUploadServer(self):
        pass


    def photos_getOwnerPhotoUploadServer(self):
        pass


    def photos_getTags(self):
        pass


    def photos_getUploadServer(self):
        pass


    def photos_getUserPhotos(self):
        pass


    def photos_getWallUploadServer(self):
        pass


    def photos_makeCover(self):
        pass


    def photos_move(self):
        pass


    def photos_putTag(self):
        pass


    def photos_removeTag(self):
        pass


    def photos_reorderAlbums(self):
        pass


    def photos_reorderPhotos(self):
        pass


    def photos_report(self):
        pass


    def photos_reportComment(self):
        pass


    def photos_restore(self):
        pass


    def photos_restoreComment(self):
        pass


    def photos_save(self):
        pass


    def photos_saveMarketAlbumPhoto(self):
        pass


    def photos_saveMarketPhoto(self):
        pass


    def photos_saveMessagesPhoto(self):
        pass


    def photos_saveOwnerCoverPhoto(self):
        pass


    def photos_saveOwnerPhoto(self):
        pass


    def photos_saveWallPhoto(self):
        pass


    def photos_search(self):
        pass


    def polls_addVote(self):
        pass


    def polls_create(self):
        pass


    def polls_deleteVote(self):
        pass


    def polls_edit(self):
        pass


    def polls_getBackgrounds(self):
        pass


    def polls_getById(self):
        pass


    def polls_getPhotoUploadServer(self):
        pass


    def polls_getVoters(self):
        pass


    def polls_savePhoto(self):
        pass


    def prettyCards_create(self):
        pass


    def prettyCards_delete(self):
        pass


    def prettyCards_edit(self):
        pass


    def prettyCards_get(self):
        pass


    def prettyCards_getById(self):
        pass


    def prettyCards_getUploadURL(self):
        pass


    def search_getHints(self):
        pass


    def stats_get(self):
        pass


    def stats_getPostReach(self):
        pass


    def stats_trackVisitor(self):
        pass


    def status_get(self):
        pass


    def status_set(self):
        pass


    def storage_get(self):
        pass


    def storage_getKeys(self):
        pass


    def storage_set(self):
        pass


    def stories_banOwner(self):
        pass


    def stories_delete(self):
        pass


    def stories_get(self):
        pass


    def stories_getBanned(self):
        pass


    def stories_getById(self):
        pass


    def stories_getPhotoUploadServer(self):
        pass


    def stories_getReplies(self):
        pass


    def stories_getStats(self):
        pass


    def stories_getVideoUploadServer(self):
        pass


    def stories_getViewers(self):
        pass


    def stories_hideAllReplies(self):
        pass


    def stories_hideReply(self):
        pass


    def stories_unbanOwner(self):
        pass


    def streaming_getServerUrl(self):
        pass


    def streaming_getSettings(self):
        pass


    def streaming_getStats(self):
        pass


    def streaming_getStem(self):
        pass


    def streaming_setSettings(self):
        pass


    def users_get(self):
        pass


    def users_getFollowers(self):
        pass


    def users_getSubscriptions(self):
        pass


    def users_isAppUser(self):
        pass


    def users_report(self):
        pass


    def users_search(self):
        pass


    def utils_checkLink(self):
        pass


    def utils_deleteFromLastShortened(self):
        pass


    def utils_getLastShortenedLinks(self):
        pass


    def utils_getLinkStats(self):
        pass


    def utils_getServerTime(self):
        pass


    def utils_getShortLink(self):
        pass


    def utils_resolveScreenName(self):
        pass


    def video_add(self):
        pass


    def video_addAlbum(self):
        pass


    def video_addToAlbum(self):
        pass


    def video_createComment(self):
        pass


    def video_delete(self):
        pass


    def video_deleteAlbum(self):
        pass


    def video_deleteComment(self):
        pass


    def video_edit(self):
        pass


    def video_editAlbum(self):
        pass


    def video_editComment(self):
        pass


    def video_get(self):
        pass


    def video_getAlbumById(self):
        pass


    def video_getAlbums(self):
        pass


    def video_getAlbumsByVideo(self):
        pass


    def video_getComments(self):
        pass


    def video_removeFromAlbum(self):
        pass


    def video_reorderAlbums(self):
        pass


    def video_reorderVideos(self):
        pass


    def video_report(self):
        pass


    def video_reportComment(self):
        pass


    def video_restore(self):
        pass


    def video_restoreComment(self):
        pass


    def video_save(self):
        pass


    def video_search(self):
        pass


    def wall_closeComments(self):
        pass


    def wall_createComment(self):
        pass


    def wall_delete(self):
        pass


    def wall_deleteComment(self):
        pass


    def wall_edit(self):
        pass


    def wall_editAdsStealth(self):
        pass


    def wall_editComment(self):
        pass


    def wall_get(self, owner_id, offset, count, domain=None, _filter='all', extended=None, fields=None):
        while True:
            self.reset_params()
            self.params['owner_id'] = owner_id
            self.params['offset'] = offset
            self.params['count'] = count
            self.params['filter'] = _filter

            if domain: self.params['domain'] = domain
            if extended: self.params['extended'] = extended
            if fields: self.params['fields'] = fields

            r = requests.get('https://api.vk.com/method/wall.get', params = self.params)
            r = json.loads(r.text)
            if r.get('response'):
                return r
            else:
                time.sleep(0.5)
                self.logging(r)

    def wall_getById(self):
        pass


    def wall_getComment(self):
        pass


    def wall_getComments(self):
        pass


    def wall_getReposts(self):
        pass


    def wall_openComments(self):
        pass


    def wall_pin(self):
        pass


    def wall_post(self):
        pass


    def wall_postAdsStealth(self):
        pass


    def wall_reportComment(self):
        pass


    def wall_reportPost(self):
        pass


    def wall_repost(self):
        pass


    def wall_restore(self):
        pass


    def wall_restoreComment(self):
        pass


    def wall_search(self):
        pass


    def wall_unpin(self):
        pass


    def widgets_getComments(self):
        pass


    def widgets_getPages(self):
        pass