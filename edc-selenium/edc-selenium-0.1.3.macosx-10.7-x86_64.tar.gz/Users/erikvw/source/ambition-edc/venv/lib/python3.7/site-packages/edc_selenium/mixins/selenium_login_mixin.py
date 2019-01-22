from django.contrib.auth.models import User, Group
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.color import color_style
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .selenium_utils_mixin import SeleniumUtilsMixin

style = color_style()


class SeleniumLoginMixin(SeleniumUtilsMixin):

    def get_or_create_user(self, group_names=None, is_superuser=None, site_names=None):
        if group_names is None and is_superuser is None:
            is_superuser = True
        if is_superuser:
            try:
                user = User.objects.get(username='erik')
            except ObjectDoesNotExist:
                user = User.objects.create_superuser(
                    username='erik',
                    password='password',
                    email='erik@example.com')
            else:
                user.is_superuser = True
                user.save()
        else:
            try:
                user = User.objects.get(username='erik')
            except ObjectDoesNotExist:
                user = User.objects.create(
                    username='erik',
                    email='erik@example.com',
                    is_staff=True,
                    is_active=True)
            else:
                user.is_staff = True
                user.is_active = True
            user.set_password('password')
            user.save()

            for group in Group.objects.exclude(name__in=group_names):
                user.groups.remove(group)
            for group_name in group_names:
                group = Group.objects.get(name=group_name)
                user.groups.add(group)

        # add site to user profile allow login
        if not site_names:
            site_names = [site.name for site in Site.objects.all()]
        for site_name in site_names:
            site = Site.objects.get(name=site_name)
            user.userprofile.sites.add(site)
        return user

    def logout(self):
        element_id = f'logout'
        WebDriverWait(self.selenium, 20).until(
            EC.presence_of_element_located((By.ID, element_id)))
        self.selenium.find_element_by_id(element_id).click()
        element_name = f'username'
        self.wait_for(element_name, by=By.NAME)

    def login(self, group_names=None, is_superuser=None, site_names=None):
        """Edc login with custom template.
        """
        user = self.get_or_create_user(
            group_names=group_names,
            is_superuser=is_superuser,
            site_names=site_names)

        self.selenium.get('%s%s' % (self.live_server_url, '/accounts/login/'))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys(user.username)
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('password')
        self.selenium.find_element_by_xpath('//input[@value="Login"]').click()
        self.wait_for_edc()
