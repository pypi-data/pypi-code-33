"""Google admin reports SDK."""

# import json
import re

from bitsapiclient.helpers import get_list_items
from datetime import date, datetime, timedelta
from googleapiclient.discovery import build
from httplib2 import Http


class Reports(object):
    """Directory class."""

    def __init__(self):
        """Initialize a class instance."""

    def get_activities(self, user, app, credentials):
        """Return list of user activities."""
        reports = build('admin', 'reports_v1', credentials=credentials)

        params = {
            'userKey': user,
            'applicationName': app,
        }
        activities = reports.activities()
        request = activities.list(**params)
        return get_list_items(activities, request, 'items')

    def get_customer_reports(self, date, credentials, parameters=None):
        """Return list of customer usage reports."""
        reports = build('admin', 'reports_v1', credentials=credentials)

        params = {
            'date': date,
            'parameters': parameters,
        }
        usage_reports = reports.customerUsageReports()
        request = usage_reports.get(**params)

        google_usage_reports = []

        while request is not None:
            usage_reports_list = request.execute()

            for w in usage_reports_list.get('warnings', []):
                print('%s: %s' % (w['code'], w['message']))

            google_usage_reports += usage_reports_list.get('usageReports', [])
            request = usage_reports.get_next(request, usage_reports_list)

        return google_usage_reports

    def get_user_reports(self, user, date, credentials, parameters=None):
        """Return list of user usage reports."""
        reports = build('admin', 'reports_v1', credentials=credentials)

        params = {
            'date': date,
            'userKey': user,
            'parameters': parameters,
        }
        usage_reports = reports.userUsageReport()
        request = usage_reports.get(**params)

        google_usage_reports = []

        while request is not None:
            usage_reports_list = request.execute()
            google_usage_reports += usage_reports_list.get('usageReports', [])
            request = usage_reports.get_next(request, usage_reports_list)

        return google_usage_reports

    def gsuite_service_accounts_report(self, args, auth):
        """Process a text file of service accounts that have access to gsuite API."""
        m = auth.mongo()
        data = {}
        lines = []
        filename = './gsuite_service_accounts.txt'

        try:
            accounts_file = open(filename, 'r')
            lines = list(accounts_file.readlines())
            print('Opened file %s with %s lines.' % (
                filename,
                len(lines),
            ))
        except Exception as e:
            print('ERROR: Failed to open file: %s' % (filename))
            print(e)

        # deal with tabs
        entries = []
        for l in lines:
            fields = l.split('\t')
            for f in fields:
                entries.append(f.strip())

        # parse entries
        client_id = ''
        for e in entries:
            if re.match('Remove$', e):
                client_id = ''
                continue

            if not client_id:
                client_id = e
                data[client_id] = {
                    'name': client_id,
                    'scopes': [],
                }
            else:
                if re.search('"https://', e):
                    continue
                elif re.search('https://', e):
                    e = re.search(r'(?P<url>https?://[^\s]+)', e).group("url")
                elif len(e.split(' ')) > 1:
                    e = None
                if e:
                    data[client_id]['scopes'].append(e)

        # display entries
        print('Displaying service accounts and their scopes:')
        for client_id in sorted(data):
            print('  %s:' % (client_id))
            print('   * '+'\n   * '.join(sorted(data[client_id]['scopes'])))
            print

        # update mongo
        m.getCollection('gsuite_service_accounts', data)
        m.updateCollection('gsuite_service_accounts', data)

        # get all service accounts
        service_accounts = m.getCollection('google_service_accounts')
        client_ids = {}
        for name in service_accounts:
            a = service_accounts[name]
            client_id = a['oauth2ClientId']
            client_ids[client_id] = a

        # organize by scope
        scopes = {}
        for name in data:
            for scope in data[name]['scopes']:
                if scope not in scopes:
                    scopes[scope] = [name]
                else:
                    scopes[scope].append(name)

        # display data about scopes:
        print('Display scopes and their service accounts:')
        for scope in sorted(scopes):
            print('  %s:' % (scope))
            print('   * '+'\n   * '.join(sorted(scopes[scope])))
            print

        # checking service accounts
        projects = {}
        print('Checking service accounts...')
        for name in sorted(data):
            if name in client_ids:
                project_id = client_ids[name]['projectId']
                if project_id not in projects:
                    projects[project_id] = [name]
                else:
                    projects[project_id].append(name)
                print('  %s [%s]' % (name, project_id))
            elif '-' in name:
                project_num = name.split('-')[0]
                print('  %s [%s]' % (name, project_num))
            else:
                print('  %s' % (name))

    def deletions_report(self, auth):
        """Run a report of all upcoming deletions."""
        p = auth.people()
        people = p.getPeople()

        deletions = {}
        for pid in people:
            person = people[pid]
            # skip active people
            if not person['terminated']:
                continue
            # skip people with no end date
            if not person['end_date']:
                continue
            email = '%s@broadinstitute.org' % (person['username'])
            end_date = datetime.strptime(person['end_date'], '%Y-%m-%d').date()
            today = date.today()
            delete_date = (end_date + timedelta(days=90))
            # skip people who should already be deleted
            if delete_date < today:
                continue
            if delete_date in deletions:
                deletions[delete_date].append(email)
            else:
                deletions[delete_date] = [email]

        for delete_date in sorted(deletions):
            print('%s (%s):' % (
                delete_date,
                len(deletions[delete_date])
            ))
            for email in sorted(deletions[delete_date]):
                print('   * %s' % (email))
            print

    def licenses_report(self, auth):
        """Run a report of all licenses."""
        g = auth.google()
        s = auth.slack()

        http = g.auth_stored_credentials().authorize(Http())

        inventory = g.licensing().get_inventory()

        stats = {}
        for product in sorted(inventory):
            print('Retrieving licensing assignments for: %s' % (product))

            if product not in stats:
                stats[product] = {}
            try:
                assignments = g.licensing().get_product_assignments(product, http)
            except Exception as e:
                print(e)
                continue

            for a in assignments:
                sku = a['skuId']

                if sku in stats[product]:
                    stats[product][sku] += 1
                else:
                    stats[product][sku] = 1

        output = """
Google License Report:

G Suite Licenses:
  Enterprise: %s/%s [%s available]
  Lite: %s/%s [%s available]

G Suite Storage Licenses:
   20GB: %s/%s [%s available]
   50GB: %s/%s [%s available]
  200GB: %s/%s [%s available]
  400GB: %s/%s [%s available]

Chrome Device Management Licenses:
  Devices: %s/%s [%s available]
  Devices for Meetings: %s/%s [%s available]""" % (

            stats['Google-Apps']['1010020020'],
            inventory['Google-Apps']['1010020020'],
            inventory['Google-Apps']['1010020020'] - stats['Google-Apps']['1010020020'],

            stats['Google-Apps']['Google-Apps-Lite'],
            inventory['Google-Apps']['Google-Apps-Lite'],
            inventory['Google-Apps']['Google-Apps-Lite'] - stats['Google-Apps']['Google-Apps-Lite'],

            stats['Google-Drive-storage']['Google-Drive-storage-20GB'],
            inventory['Google-Drive-storage']['Google-Drive-storage-20GB'],
            inventory['Google-Drive-storage']['Google-Drive-storage-20GB'] - stats['Google-Drive-storage']['Google-Drive-storage-20GB'],

            stats['Google-Drive-storage']['Google-Drive-storage-50GB'],
            inventory['Google-Drive-storage']['Google-Drive-storage-50GB'],
            inventory['Google-Drive-storage']['Google-Drive-storage-50GB'] - stats['Google-Drive-storage']['Google-Drive-storage-50GB'],

            stats['Google-Drive-storage']['Google-Drive-storage-200GB'],
            inventory['Google-Drive-storage']['Google-Drive-storage-200GB'],
            inventory['Google-Drive-storage']['Google-Drive-storage-200GB'] - stats['Google-Drive-storage']['Google-Drive-storage-200GB'],

            stats['Google-Drive-storage']['Google-Drive-storage-400GB'],
            inventory['Google-Drive-storage']['Google-Drive-storage-400GB'],
            inventory['Google-Drive-storage']['Google-Drive-storage-400GB'] - stats['Google-Drive-storage']['Google-Drive-storage-400GB'],

            27,
            52,
            52 - 27,

            8,
            10,
            10 - 8,
        )

        print(output)
        s.post_message(s.notifications, output)
        # print json.dumps(inventory, indent=2, sort_keys=True)

    def quotas_report(self, auth):
        """Run a report of user quotas."""
        g = auth.google()
        # s = auth.slack()

        # get the most recent data
        query_date = date.today()
        params = [
            'accounts:drive_used_quota_in_mb:',
            'accounts:gmail_used_quota_in_mb',
            'accounts:gplus_photos_used_quota_in_mb',
            'accounts:total_quota_in_mb',
            'accounts:used_quota_in_mb',
            'accounts:used_quota_in_percentage',
        ]
        parameters = ','.join(params)
        report = None

        credentials = g.auth_service_account(g.scopes, g.sub_account)

        while not report:
            try:
                # print 'Trying %s...' % (query_date)
                report = self.get_user_reports(
                    'all',
                    str(query_date),
                    credentials,
                    parameters=parameters
                )
            except Exception:
                query_date = query_date - timedelta(1)
                # error = json.loads(e.content).get('error', {'message': None})
                # print error['message']

            errors = 0
            if report:
                # check report for parameters
                for user in report:
                    if 'parameters' not in user:
                        errors += 1
                if errors:
                    # print 'Skipping %s: %s out of %s users missing data.' % (
                    #     str(query_date),
                    #     errors,
                    #     len(report)
                    # )

                    # if too many errors, go back another day
                    if errors > (len(report) / 2):
                        report = None
                        query_date = query_date - timedelta(1)

        # print report

        print('Top Google Quotas data from: %s\n' % (query_date))

        data = {}

        # prep data
        for user in report:
            if 'parameters' not in user:
                continue

            email = user['entity']['userEmail']
            data[email] = {}

            for p in user['parameters']:
                name = p['name']
                value = p.get('intValue', 0)
                data[email][name] = int(value)

        # get users
        fields = 'nextPageToken,users(primaryEmail,name/fullName,suspended)'
        all_users = g.directory().get_users(credentials, fields=fields)
        google_users = {}
        for user in all_users:
            email = user['primaryEmail']
            google_users[email] = {
                'fullName': user.get('name', {}).get('fullName'),
                'suspended': user.get('suspended'),
            }

        # display report
        terms = []
        for email in sorted(
                data,
                key=lambda x: data[x].get('accounts:used_quota_in_percentage'),
                reverse=True,
        ):
            user = data[email]
            if user.get('accounts:used_quota_in_percentage', 0) > 80:
                if email not in google_users:
                    print('ERROR: User deleted: %s' % (email))
                    continue

                full_name = google_users[email]['fullName']
                suspended = google_users[email]['suspended']
                status = ''
                if suspended:
                    status = ' [SUSPENDED]'
                    terms.append(email)
                    continue

                # print '%s%% - %s <%s> (%s/%sGB = drive: %sGB + gmail: %sGB + photos: %sGB)' % (
                #     user['accounts:used_quota_in_percentage'],
                #     full_name,
                #     email.replace('@broadinstitute.org', ''),
                #     user['accounts:used_quota_in_mb']/1024,
                #     user['accounts:total_quota_in_mb']/1024,
                #     user['accounts:drive_used_quota_in_mb']/1024,
                #     user['accounts:gmail_used_quota_in_mb']/1024,
                #     user['accounts:gplus_photos_used_quota_in_mb']/1024,
                # )

                print('%s%% - %s <%s> (%s/%sGB)%s' % (
                    user.get('accounts:used_quota_in_percentage', 0),
                    full_name,
                    email.replace('@broadinstitute.org', ''),
                    user.get('accounts:used_quota_in_mb', 0)/1024,
                    user.get('accounts:total_quota_in_mb', 0)/1024,
                    status,
                    # user['accounts:drive_used_quota_in_mb']/1024,
                    # user['accounts:gmail_used_quota_in_mb']/1024,
                    # user['accounts:gplus_photos_used_quota_in_mb']/1024,
                ))

        if terms:
            print('\nSuspended users:\n')
        for email in terms:
            full_name = google_users[email]['fullName']
            user = data[email]
            print('%s%% - %s <%s> (%s/%sGB)%s' % (
                user.get('accounts:used_quota_in_percentage', 0),
                full_name,
                email.replace('@broadinstitute.org', ''),
                user.get('accounts:used_quota_in_mb', 0)/1024,
                user.get('accounts:total_quota_in_mb', 0)/1024,
                status,
                # user['accounts:drive_used_quota_in_mb']/1024,
                # user['accounts:gmail_used_quota_in_mb']/1024,
                # user['accounts:gplus_photos_used_quota_in_mb']/1024,
            ))

        inventory = {
            'Google-Drive-storage-20GB': 100,
            'Google-Drive-storage-50GB': 30,
            'Google-Drive-storage-200GB': 20,
            'Google-Drive-storage-400GB': 5,
            # 'Google-Drive-storage-1TB': 0,
            # 'Google-Drive-storage-2TB': 0,
            # 'Google-Drive-storage-4TB': 0,
            # 'Google-Drive-storage-8TB': 0,
            # 'Google-Drive-storage-16TB': 0,
        }

        http = g.auth_stored_credentials().authorize(Http())

        print('\nAvailable licenses:\n')
        licenses = g.licensing().get_product_assignments(
            'Google-Drive-storage',
            http
        )
        for l in sorted(licenses, key=lambda x: x['userId']):
            sku = l['skuId']
            # user = l['userId']
            inventory[sku] -= 1
            # print user, sku, data[user]['accounts:used_quota_in_percentage']

        for key in sorted(inventory, key=lambda x: int(re.sub('[-a-zA-Z]', '', x))):
            print('%s %s' % (
                ('%s:' % (key)).ljust(28),
                str(inventory[key]).rjust(2)
            ))

        # print json.dumps(inventory, indent=2, sort_keys=True)

        # print '\nUsed licenses:'
        # for l in sorted(licenses, key=lambda x: x['userId']):
        #     sku = l['skuId']
        #     user = l['userId']
        #     used = data[user]['accounts:used_quota_in_percentage']
        #     print user, sku, data[user]['accounts:used_quota_in_percentage']

    def credit_report(self, auth):
        """Parse the credit details from Google."""
        sheet = '17ZDjCwdPkg-NMlZsJPHpenNaZfNyLo4z_DxXo5ETYYY'
        rangeName = 'Debit, Credit by project!A:D'
        g = auth.google()
        credentials = g.auth_service_account(g.scopes, g.sub_account)

        billing_accounts = {}
        data = g.sheets().get_sheet(sheet, credentials, rangeName)
        values = data['values']

        header = [
            'project_id',
            'project_name',
            'billing_account',
            'credit',
            'debit',
            'total'
        ]
        output = [header]

        for row in values:
            if row[0] == 'Project Number':
                continue
            if not row[0]:
                continue

            debit = float(row[1])
            credit = float(row[2])
            total = float(row[3])

            project_name = 'projects/%s' % (row[0])

            try:
                project = g.billing().get_project_billinginfo(project_name, credentials)
            except Exception:
                print('Project not found: %s' % (project_name))
                newrow = [
                    row[0],
                    '',
                    '',
                    credit,
                    debit,
                    total
                ]
                output.append(newrow)
                continue

            billing_account = project.get('billingAccountName')

            project_query = """
                SELECT
                  billing_account_id
                FROM
                  `broad-gcp-billing.gcp_billing_export.gcp_billing_export_001AC2_2B914D_822931`
                WHERE
                  project.id = '%s'
                ORDER BY
                  start_time DESC
                LIMIT
                  1
            """

            if not billing_account:
                query = project_query % (project['projectId'])
                results = g.bq().query_job('broad-gcp-billing', query, credentials)
                if results:
                    billing_account = 'billingAccounts/%s' % (results[0]['f'][0]['v'])
                else:
                    print(query)
                    continue

            print(billing_account, row)

            if billing_account not in billing_accounts:
                billing_accounts[billing_account] = {
                    'credit': float(0),
                    'debit': float(0),
                    'total': float(0)
                }

            billing_accounts[billing_account]['debit'] += debit
            billing_accounts[billing_account]['credit'] += credit
            billing_accounts[billing_account]['total'] += total

            newrow = [
                row[0],
                project['projectId'],
                billing_account,
                credit,
                debit,
                total,
            ]

            output.append(newrow)

        outputRange = 'Output!A:F'
        body = {
            'majorDimension': 'ROWS',
            'range': outputRange,
            'values': output,
        }
        print(g.sheets().update_sheet(sheet, credentials, body, outputRange))
