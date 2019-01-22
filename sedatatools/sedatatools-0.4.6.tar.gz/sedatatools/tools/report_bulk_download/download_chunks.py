import requests
from lxml import etree as et
import argparse
import time
import pickle


def get_table_names_from_db(mf):
    docs = et.parse(mf)
    tables = docs.xpath('//table')
    tables_dic = {t.attrib['name']: t.attrib['DbTableSuffix'] for t in tables}
    return tables_dic


if __name__ == '__main__':
    # argument parser
    parser = argparse.ArgumentParser(
        description='Download data from reports system in chunks.',
        epilog='example usage: '
               'py download_chunks.py "C2000" "SF1" "SL795" '
               '"C:\Projects\Website-ASP.Net\pub\ReportData\Metadata\C2000 Metadata v2.6.2.xml" "c:\\vedad\\" 1 False')
    parser.add_argument('survey_name', help='Survey name e.g. ACS2016_5yr.')
    parser.add_argument('data_set_abbreviation', help='Data set abreviation.')
    parser.add_argument('geo_levels', help='Geo levels for which to download files.')
    parser.add_argument('meatadata_file', help='Full path to metadata file.')
    parser.add_argument('output_dir', help='Full path to output dir.')
    parser.add_argument('step', help='Number of tables in chunks.')
    parser.add_argument('GUID_v', help='Set to True if you want to get GUIS instead of the var names')
    args = parser.parse_args()

    # "C2000" "SF1" "SL795" "C:\Projects\Website-ASP.Net\pub\ReportData\Metadata\C2000 Metadata v2.6.2.xml" c:\vedad\ 1
    # survey name
    # example: survey = 'ACS2016_5yr'; sys.argv[1]
    survey = args.survey_name
    # data set abbreviation, sys.argv[2]
    # example: ds='ACS16_5yr'
    ds = args.data_set_abbreviation
    # geo name
    # example: geoName = ['SL140']; [sys.argv[3]]
    geoName = [args.geo_levels]
    # path to the metadata file
    # example:
    # metadata_file = 'C://Projects//Website-ASP.NET//pub//ReportData//Metadata//ACS 2016-5yr Metadata.xml' sys.argv[4]
    metadata_file = args.meatadata_file
    doc = et.parse(metadata_file)
    # path to output dir
    # example: path_to_out = '//prime/Datasets//ACS 2016_5yr//Maps//'; sys.argv[5]
    path_to_out = args.output_dir
    # step (number of tables do download in chunks); sys.argv[6]
    step = int(args.step)
    # guid vars
    GUID_vars = ''
    if args.GUID_v == 'True':
        GUID_vars = 'Guid=1&'

    # get all the variables from the data set
    table_list = list(doc.xpath("//SurveyDataset[@abbreviation='{}']/tables/table/@name".format(ds)))

    # exclude standard error variables
    table_list = [el for el in table_list if '_se' not in el]

    start_end = []

    # you can increase this number if you need it.
    # Step will download n number of variable in one file (in this case: 500)
    # step = 200
    st = 0
    for n, _ in enumerate(table_list):
        if n % step == 0 and n != 0 and step > 1:  # step > 1 to exclude cases when only one variable is needed
            start_end.append([table_list[st], table_list[n]])
            st = n + 1
            # for the last iteration, if less than n number
            if (len(table_list) - n) < step:
                start_end.append([table_list[n + 1], table_list[len(table_list) - 1]])
                break
        elif step == 1:
            start_end.append([table_list[st], table_list[st]])
            st = n + 1

    # all the summary levels you need
    # geoName = ['SL040', 'SL050', 'SL140', 'SL150', 'SL160', 'SL310', 'SL500', 'SL610', 'SL620', 'SL795', 'SL860',
    #            'SL950', 'SL960', 'SL970']

    table_names_in_db = get_table_names_from_db(metadata_file)
    try:
        finished_vars = pickle.load(open('finished_vars.pkl', 'rb'))
        print(f'starting from {finished_vars[-1]}')
    except (OSError, IOError) as e:
        print('Starting from the begining.')
        finished_vars = []

    for i in geoName:
        for ind, se in enumerate(start_end):
            tab_in_db_id = table_names_in_db[se[0]]
            if start_end in finished_vars or tab_in_db_id == 'geo':
                continue
            print(f'Processing geo {i} vars {se} ({tab_in_db_id, table_names_in_db[se[1]]}).')
            start_time = time.time()
            try:
                response = requests.get(
                'http://ec2-107-20-216-26.compute-1.amazonaws.com/pub/reportdata/DownloadCsvFileNow.aspx?survey=' +
                survey + '&ds=' + ds + '&startTableName=' + se[0] + '&endTableName=' + se[1] + '&geoName=' + i +
                '&filename=' + survey + '_' + i + '_ACS_part_' + str(ind) + '.csv&' + GUID_vars +
                'mirroredTables=false')
            except:
                delay = 180
                print(f'Connection broken, starting again in {delay} seconds!')
                time.sleep(delay)  # if connection is broken try again after "delay" seconds
                response = requests.get(
                    'http://ec2-107-20-216-26.compute-1.amazonaws.com/pub/reportdata/DownloadCsvFileNow.aspx?survey=' +
                    survey + '&ds=' + ds + '&startTableName=' + se[0] + '&endTableName=' + se[1] + '&geoName=' + i +
                    '&filename=' + survey + '_' + i + '_ACS_part_' + str(ind) + '.csv&' + GUID_vars +
                    'mirroredTables=false')

            if response.status_code == 200:
                if step == 1:
                    file_name = survey + i + '_' + se[0] + '_' + tab_in_db_id + '_part_' + str(ind) + '.csv'
                else:
                    file_name = survey + i + '_' + se[0] + '_' + se[1] + '_part_' + str(ind) +'.csv'

                with open(path_to_out + '\\' + file_name, 'wb') as f:
                    f.write(response.content)

            finished_vars.append(se)
            pickle.dump(finished_vars, open('finished_vars.pkl', 'wb'))

            print(f"Done in {(round(time.time() - start_time)/60, 2)} minutes!")