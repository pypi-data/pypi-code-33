import argparse
import pytz
import time
from datetime import datetime, timedelta

from .scrap import TimezoneScrapper


def format(dt: datetime) -> str:
    return dt.strftime('%a, %b %d, %Y %I:%M%p')


def main():
    parser = argparse.ArgumentParser(description='a command-line utility to convert unitx timestamp into human readable datetime.')
    parser.add_argument('ut_or_now', help='input now or a unix timestamp')
    parser.add_argument('--diff', '-d', action='store_true', help='time difference between input time and current time')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--timezone', '-tz', type=str, required=False, help='timezone info formatted as: GMT+8, or UTC+8')
    group.add_argument('--city', '-c', type=str, required=False, help='search local time of named city of input time')
    args = parser.parse_args()

    args_invalid = True
    ut = None

    if args.ut_or_now == 'now':
        ut = time.time()
        args_invalid = False
    else:
        try:
            ut = float(args.ut_or_now)
            if ut <= 1e10:
                args_invalid = False
            elif ut > 1e12 and ut <= 1e13:
                ut /= 1000
                args_invalid = False
        except:
            pass
    
    if args_invalid:
        print(u'\U0001F9D0',
              ' Your input seems invalid, the 1st arg should be either "now" or the unix timestamp (10-digit in seconds or 13-digit in milliseconds)')
    else:
        print(f'Unix Timestamp: {ut}')

        dt_local = datetime.fromtimestamp(ut)
        print(f'Local: {format(dt_local)}')

        dt_utc = datetime.utcfromtimestamp(ut)
        print(f'GMT  : {format(dt_utc)}')

        if args.diff:
            dt_now = datetime.now()
            
            diff = dt_local.timestamp() - dt_now.timestamp()

            ahead = True if diff > 0 else False

            diff_td = timedelta(seconds=abs(diff))
            diff_d = diff_td.days
            diff_s = diff_td.seconds

            diff_h = diff_s // 3600
            diff_s -= diff_h * 3600
            diff_m = diff_s // 60
            diff_s -= diff_m * 60

            diff_str = 'Given time is '
            if diff_d != 0:
                diff_str += f'{diff_d} days, '
            if diff_h != 0:
                diff_str += f'{diff_h} hrs, '
            if diff_m != 0:
                diff_str += f'{diff_m} mins, '
            diff_str += f'{diff_s} secs '
            diff_str += 'ahead' if ahead else 'ago'
            
            print(diff_str)
        
        if args.timezone:
            if args.timezone[:3].upper() not in ['GMT', 'UTC']:
                print(u'\U0001F925',
                      ' Please provide timezone formatted as: GMT+8, or UTC-9. Only GMT and UTC as prefix are accepted')
            else:
                tz_sign = args.timezone[3]
                tz_diff = int(args.timezone[4:])
                if tz_sign == '-':
                    dt_tz_ut = dt_utc.timestamp() - tz_diff * 3600
                elif tz_sign == '+':
                    dt_tz_ut = dt_utc.timestamp() + tz_diff * 3600
                
                dt_tz = datetime.fromtimestamp(dt_tz_ut)
                print(u'\U0001F60E',
                      f' The given time in {args.timezone} is: {format(dt_tz)}.')

        if args.city:
            print(u'\U0001F61B',
                  ' I am finding your city on popular search engines! Plz wait a sec...')
            
            ts = TimezoneScrapper(args.city)
            if ts.timezone:
                tz_sign = ts.timezone[0]
                tz_diff = int(ts.timezone[1:])
                if tz_sign == '-':
                    dt_city_ut = dt_utc.timestamp() - tz_diff * 3600
                elif tz_sign == '+':
                    dt_city_ut = dt_utc.timestamp() + tz_diff * 3600

                dt_city = datetime.fromtimestamp(dt_city_ut)
                print(u'\U0001F60E',
                      f' I suppose the given time in {args.city} is: {format(dt_city)}.'
                      ' I have 88% confidence with this result from search engines!')
            else:
                print(u'\U0001F925',
                      ' emmm... I cannot find your city on popular search engines!'
                      ' Could it be that the input has any typos?')


if __name__ == '__main__':
     main()
