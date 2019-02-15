from django.contrib.auth.models import User
from django.db import models

class CLDate(models.Model):
    class Meta:
        abstract = True

    active = models.BooleanField(default=True)
    last_modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s' % (self.__class__.__name__)


class Switch(CLDate):
    name = models.CharField(max_length=64)
    code = models.CharField(max_length=64, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    sorted = models.IntegerField(default=0)

    def get_code(self):
        if self.code:
            return self.code
        return self.name

    def __str__(self):
        return self.name


class Document(CLDate):
    user = models.ForeignKey(User)
    bug_entity = models.ManyToManyField('bugtrack.BugEntity')
    name = models.CharField(max_length=256)
    path = models.CharField(max_length=256)
    size = models.IntegerField(default=0)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class BugStatus(Switch):
    color = models.CharField(max_length=16, blank=True, null=True)
    bgcolor = models.CharField(max_length=16, blank=True, null=True)


class Priority(Switch):
    color = models.CharField(max_length=16, blank=True, null=True)
    is_bold = models.BooleanField(default=False)


class Severity(Switch):
    color = models.CharField(max_length=16, blank=True, null=True)
    is_bold = models.BooleanField(default=False)


class Category(Switch):
    color = models.CharField(max_length=16, blank=True, null=True)
    parent = models.CharField(max_length=16, blank=True, null=True)
    #User can add Bugs to this Category
    to_user = models.ManyToManyField(User, related_name='to_user')
    #User can read the Bugs from this Category
    to_user_ro = models.ManyToManyField(User, related_name='to_user_ro')
    
    def get_parent(self):
        try:
            return Category.objects.get(id=self.parent)
        except:
            return False

    def get_parent_tree(self):
        parents = []
        parent = self.get_parent()
        while parent:
            parents.append(parent)
            parent = parent.get_parent()
        return parents

    def get_children(self):
        return Category.objects.filter(parent=self.id)

    def get_children_tree(self):
        ret = []
        for child in self.get_children():
            ret.append(child)
            gct = child.get_children_tree()
            if gct:
                ret.extend(gct)
#            children = child.get_children()
#            while children:
#                for _child in children:
#                    ret.append(_child.get_children_tree())
        return ret

    def has_access(self, user):
        if self.to_user.filter(username=user.username):
            return True
        parent = self.get_parent()
        while parent:
            if parent.to_user.filter(username=user.username):
                return True
            parent = parent.get_parent()
        return False

    def has_access_ro(self, user):
        if self.to_user.filter(username=user.username) or \
                self.to_user_ro.filter(username=user.username):
            return True
        parent = self.get_parent()
        while parent:
            if parent.to_user.filter(username=user.username) or \
                    self.to_user_ro.filter(username=user.username):
                return True
            parent = parent.get_parent()
        return False

    def __str__(self):
        return "%s%s" % ('*' * len(self.get_parent_tree()), self.name)


class Bug(CLDate):
    user = models.ForeignKey(User)
    executor = models.ForeignKey(User, blank=True, null=True, \
            related_name='executor')
    tester = models.ForeignKey(User, blank=True, null=True, \
            related_name='tester')
    assigned_to = models.ForeignKey(User, related_name='assigned_to')
    category = models.ForeignKey(Category)
    priority = models.ForeignKey(Priority)
    severity = models.ForeignKey(Severity)
    bugstatus = models.ForeignKey(BugStatus)
    waiting_for_reply = models.BooleanField(default=False)
    #User can comment on this Bug
    to_user = models.ManyToManyField(User, related_name='bug_to_user')
    #User can watch this Bug
    to_user_ro = models.ManyToManyField(User, related_name='bug_to_user_ro')
    parent = models.CharField(max_length=8, blank=True, null=True, default='')
    depends_on = models.CharField(max_length=256, default='', \
            blank=True, null=True)
    subject = models.CharField(max_length=256)
    text = models.TextField()

    def can_be_edited(self, user):
        return True

    def can_be_commented(self, user):
        return True

    def get_parent(self):
        try:
            return Bug.objects.get(id=self.parent)
        except:
            return False

    def has_access(self, user):
        if self.to_user.filter(username=user.username):
            return True
        return self.category.has_access(user)

    def has_access_ro(self, user):
        if self.to_user.filter(username=user.username) or \
                self.to_user_ro.filter(username=user.username):
            return True
        return self.category.has_access_ro(user)


class BugEntity(CLDate):
    user = models.ForeignKey(User)
    bug = models.ForeignKey(Bug)
    safe = models.BooleanField(default=False)
    text = models.TextField(blank=True, null=True)
    new_status = models.BooleanField(default=False)
    new_assignment = models.BooleanField(default=False)
    private = models.BooleanField(default=False)


class SavedSearch(CLDate):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=128)
    search_phrase = models.CharField(max_length=1024)
    bgcolor = models.CharField(max_length=32, blank=True, null=True)