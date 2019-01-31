# -*- coding: utf-8 -*-
from plone import api
from plone.memoize import ram
from plone.rfc822.interfaces import IPrimaryFieldInfo
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone.utils import safe_unicode
from zope.i18n import translate


class PrettyLinkAdapter(object):
    """Adapter that manage rendering the pretty link."""

    def __init__(self,
                 context,
                 showColors=True,
                 showIcons=True,
                 showContentIcon=False,
                 showLockedIcon=True,
                 contentValue='',
                 display_tag_title=True,
                 tag_title='',
                 maxLength=0,
                 target='_self',
                 appendToUrl='',
                 additionalCSSClasses=[],
                 isViewable=True,
                 **kwargs):
        self.context = context
        self.request = self.context.REQUEST
        self.portal_url = api.portal.get().absolute_url()
        # we set parameters in the init so it it reusable across every methods
        self.showColors = showColors
        self.showIcons = showIcons
        self.showContentIcon = showContentIcon
        self.showLockedIcon = showLockedIcon
        # value to use for the link, if not given, object's title will be used
        self.contentValue = contentValue
        # arbitrary tag_title, escape quotes
        self.tag_title = tag_title.replace("'", "&#39;")
        self.display_tag_title = display_tag_title
        # truncate link content to given maxLength if any
        self.maxLength = maxLength
        # target of the link : _blank, _self, ...
        self.target = target
        # append arbitrary to the rendered URL
        self.appendToUrl = appendToUrl
        # arbitrary css classes
        self.additionalCSSClasses = additionalCSSClasses
        self.kwargs = kwargs
        # we also manage the fact that we want to display an element that is
        # actually not reachable by current user...  In this case, we display
        # a <div> to the element with a help message...
        self.isViewable = isViewable
        # we may force isViewable to False even if user has the 'View' permission
        # on it, but if isViewable is True, we check if target is really viewable
        if isViewable:
            if not _checkPermission(View, self.context):
                self.isViewable = False
        self.notViewableHelpMessage = translate(
            'can_not_access_this_element',
            domain="imio.prettylink",
            context=self.request,
            default=u"<span class='discreet no_access'>(You can not access this element)</span>")

    def getLink_cachekey(method, self):
        '''cachekey method for self.getLink.'''
        is_locked = self._show_lock_icon()
        review_state = api.content.get_state(self.context, None)
        server_url = self.request.get('SERVER_URL', None)
        # cache by context, until modified, is_locked, state changed or server_url is different
        # + every parameters passed in __init__
        return (self.context, self.context.modified(), is_locked, review_state, server_url,
                self.showColors,
                self.showIcons,
                self.showContentIcon,
                self.showLockedIcon,
                self.contentValue,
                self.tag_title,
                self.display_tag_title,
                self.maxLength,
                self.target,
                self.appendToUrl,
                self.additionalCSSClasses,
                self.isViewable,
                self.kwargs)

    @ram.cache(getLink_cachekey)
    def getLink(self):
        """See docstring in interfaces.py."""
        return self._getLink()

    def _getLink(self):
        """Private method that does the link computation without the cachekey,
           this is done so it is possible to override the cachekey."""
        completeContent = safe_unicode(self.contentValue or self.context.Title())
        content = completeContent
        if self.maxLength:
            plone_view = self.context.restrictedTraverse('@@plone')
            ellipsis = self.kwargs.get('ellipsis', '...')
            content = plone_view.cropText(completeContent, self.maxLength, ellipsis)
        icons = self.showIcons and self._icons() or ''
        title = safe_unicode(self.tag_title or completeContent.replace("'", "&#39;"))
        icons_tag = icons and u"<span class='pretty_link_icons'>{0}</span>".format(icons) or ""
        if self.isViewable:
            url = self._get_url()
            return u"<a class='{0}'{1} href='{2}' target='{3}'>{4}" \
                   u"<span class='pretty_link_content'>{5}</span></a>" \
                   .format(self.CSSClasses(),
                           self.display_tag_title and u" title='{0}'".format(title) or '',
                           url,
                           self.target,
                           icons_tag,
                           safe_unicode(content))
        else:
            # append the notViewableHelpMessage
            content = u"{0} {1}".format(content, self.notViewableHelpMessage)
            return u"<div class='{0}'{1}>{2}<span class='pretty_link_content'>{3}</span></div>" \
                   .format(self.CSSClasses(),
                           self.display_tag_title and u" title='{0}'".format(title) or '',
                           icons_tag,
                           safe_unicode(content))

    def _get_url(self):
        """Compute the url to the content."""
        url = self.context.absolute_url()
        # add @@download to url if necessary, it is the case for dexterity files
        try:
            if IPrimaryFieldInfo(self.context):
                url = u'{0}/@@download'.format(url)
        except TypeError:
            pass
        return url + self.appendToUrl

    def CSSClasses(self):
        """See docstring in interfaces.py."""
        css_classes = list(self.additionalCSSClasses)
        css_classes.insert(0, 'pretty_link')
        if self.showColors:
            wft = api.portal.get_tool('portal_workflow')
            try:
                css_classes.append('state-{0}'.format(wft.getInfoFor(self.context, 'review_state')))
            except WorkflowException:
                # if self.context does not have a workflow, just pass
                pass
        # in case the contentIcon must be shown and it the icon
        # is shown by the generated contentttype-xxx class
        if self.showContentIcon:
            typeInfo = api.portal.get_tool('portal_types')[self.context.portal_type]
            if not typeInfo.icon_expr:
                css_classes.append('contenttype-{0}'.format(typeInfo.getId()))
        return ' '.join(css_classes)

    def _icons(self, **kwargs):
        """See docstring in interfaces.py."""
        icons = []

        # manage icons we want to be displayed before managed icons
        icons = icons + self._leadingIcons()

        # display the icon that shows that an element is currently locked by another user
        if self._show_lock_icon():
            icons.append(("lock_icon.png", translate("Locked", domain="plone", context=self.request)))

        # in case the contentIcon must be shown, the icon url is defined on the typeInfo
        if self.showContentIcon:
            typeInfo = api.portal.get_tool('portal_types')[self.context.portal_type]
            if typeInfo.icon_expr:
                # we assume that stored icon_expr is like string:${portal_url}/myContentIcon.png
                # or like string:${portal_url}/++resource++package/myContentIcon.png
                # we skip first part
                contentIcon = '/'.join(typeInfo.icon_expr.split('/')[1:])
                icons.append((contentIcon,
                              translate(typeInfo.title,
                                        domain=typeInfo.i18n_domain,
                                        context=self.request)))

        # manage icons we want to be displayed after managed icons
        icons = icons + self._trailingIcons()
        return ' '.join([u"<img title='{0}' src='{1}' />".format(
            safe_unicode(icon[1]).replace("'", "&#39;"),
            u"{0}/{1}".format(self.portal_url, icon[0]))
            for icon in icons])

    def _show_lock_icon(self):
        """ """
        return self.showLockedIcon and self.context.wl_isLocked()

    def _leadingIcons(self):
        """See docstring in interfaces.py."""
        return []

    def _trailingIcons(self):
        """See docstring in interfaces.py."""
        return []
