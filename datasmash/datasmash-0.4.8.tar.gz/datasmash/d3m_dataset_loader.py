"""
Class for loading datasets in the D3M format (v3.1.1)
"""
import os
import csv
import json
import warnings
import tempfile
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from imageio import imread, imwrite
from shutil import copytree, ignore_patterns, rmtree
from datasmash.utils import wait_for_file, smash


class D3MDatasetLoader(object):
    """

    """
    def __init__(self):
        self._train_dir = ''
        self._test_dir = ''

        train_json_path = ''
        test_json_path = ''
        self._train_doc = {}
        self._test_doc = {}

        self._is_raw_images = None
        self.tmp_dir = ''
        self.dataset_name = ''
        self.time_series_cols = []
        self.class_list = []
        self.index_class_map = {}
        self.channel_paths = []
        self.channel_problems = {}
        self.splitDataFrame=None
        self.bmp_dirs = {}
        self.bmp_ser_dirs = {}

    @staticmethod
    def _mkdir(directory):
        """

        """
        if os.path.isdir(directory):
            rmtree(directory)
        os.mkdir(directory)

    @staticmethod
    def _load_table(*, json_path):
        """

        """
        if not os.path.isfile(json_path):
            raise FileNotFoundError(json_path + ' does not exist')
        else:
            with open(json_path, 'r') as infile:
                dataset_doc = json.load(infile)
                infile.close()
            return dataset_doc

    def _save_img_array_as_bmp(self, img_array, original_image_name, *,
                               train_or_test):
        """
        create directory of .bmp files in our temporary directory,
        save converted image in this new directory
        """
        train_or_test_dir = os.path.join(self.tmp_dir, train_or_test)
        self._mkdir(train_or_test_dir)
        train_or_test_ts_dir = os.path.join(train_or_test_dir, 'timeseries')
        self._mkdir(train_or_test_ts_dir)
        self.bmp_ser_dirs[train_or_test] = train_or_test_ts_dir
        bmp_dir = (os.path.join(train_or_test_dir, 'bmp') + '_' +
            train_or_test)
        self._mkdir(bmp_dir)
        self.bmp_dirs[train_or_test] = bmp_dir

        bmp_outfile = original_image_name.split('.')[0] + '.bmp'
        bmp_outfile_path = os.path.join(bmp_dir, bmp_outfile)
        imwrite(bmp_outfile_path, img_array)

    def _convert_to_bmp(self, image_dir, *, train_or_test, axis=2):
        """
        iterate over non-.bmp images in raw image directory
        """
        if self.tmp_dir == '':
            prefix = self.dataset_name + '-'
            self.tmp_dir = tempfile.mkdtemp(prefix=prefix, dir='./')
        for image in os.listdir(image_dir):
            image_path = os.path.join(image_dir, image)
            img_array = imread(image_path)
            img_dim = img_array.shape
            if np.product(img_array.shape) > 16384:
                warnings.warn("image larger than 16384", UserWarning)

            # TODO: perhaps add RGB+ later as a multichannel problem
            #elif len(img_dim) == 3:
            #    for channel, img_array_ in enumerate(img_array[:,:,]):
            #        self._save_img_array_as_bmp(img_array_, image,
            #                                    str(channel),
            #                                    train_or_test=train_or_test)
            #if len(img_dim) == 2:
            self._save_img_array_as_bmp(img_array, image,
                                        train_or_test=train_or_test)

    def _serialize_bmp_dir(self, *, train_or_test, **kwargs):
        """
        iterate over .bmp files in and serialize each,
        save the result in a csv
        """
        bmp_dir = self.bmp_dirs[train_or_test]
        csv_dir = self.bmp_ser_dirs[train_or_test]
        for bmp_file in os.listdir(bmp_dir):
            csv_outfile = os.path.join(csv_dir, (bmp_file.split('.')[0] +
                                                 '.csv'))
            bmp_file_path = os.path.join(bmp_dir, bmp_file)
            serializer(bmp_file_path, outfile=csv_outfile, **kwargs)
            d3m_ts_format = pd.read_csv(csv_outfile, delimiter=' ',
                                        header=None, lineterminator=' ',
                                        comment='\n', names=['val'])
            d3m_ts_format.to_csv(csv_outfile, index_label='time')

    @staticmethod
    def _detect_if_images(doc):
        """

        """
        resTypes = set()
        for dR in doc["dataResources"]:
            resTypes.add(dR["resType"])
        if "image" in resTypes:
            return True
        else:
            return False

    def load_dataset(self, *, data, train_or_test, verbose=False, **kwargs):
        """

        """
        f = open("BUG.txt", "a")
        f.write(str(data))
        if not isinstance(data, str):
            f.write('Hacky loader\n')
            stri = str(data)
            str_list = stri.split('\'')
            for stri in str_list:
                if stri.find('file:///')>=0:
                    data = stri[7:]
        doc_json = 'datasetDoc.json'
        f.write(data)
        f.close()
        if data.find(os.path.join('dataset_TEST/datasetDoc.json')) != -1 or data.find(os.path.join('dataset_TRAIN/datasetDoc.json')) != -1:
            print("Old dataset loader")
            pass
        else:
            allFoldersInDir=os.listdir(data)
            if len([a for a in allFoldersInDir if a.find('problem') != -1])!=0 and \
                len([a for a in allFoldersInDir if a.find('dataset') != -1])!=0:
                allFoldersInDir=os.listdir(data)
                dataSetPath=data
                print('new dataset loader')
                problemFolderName=[a for a in allFoldersInDir if a.find('problem') != -1][0]
                datasetFolderName=[a for a in allFoldersInDir if a.find('dataset') != -1][0]
                problemJsonPath=os.path.join(dataSetPath, problemFolderName, 'problemDoc.json')
                data=os.path.join(dataSetPath, datasetFolderName,doc_json)
                splitsFile=self._load_table(json_path=problemJsonPath)['inputs']['dataSplits']['splitsFile']
                self.splitDataFrame = pd.read_csv(os.path.join(dataSetPath,problemFolderName,splitsFile))
                data=os.path.join(dataSetPath, datasetFolderName,doc_json)
            elif train_or_test=='train':
                print('old dataset loader TRAIN')
                data=os.path.join(data, 'TRAIN', 'dataset_TRAIN/datasetDoc.json')
            else:
                print('old dataset loader TEST')
                data=os.path.join(data, 'TEST', 'dataset_TEST/datasetDoc.json')
        if os.path.isfile(data):
            data_dir = os.path.dirname(os.path.realpath(data))
        elif os.path.isdir(data):
            data_dir = data
        print('os.path.isfile(data)',os.path.isfile(data))
        json_path = os.path.join(data_dir, doc_json)
        doc = self._load_table(json_path=json_path)
        self.dataset_name = doc['about']['datasetName'].replace(' ',
                                                                '_').replace('/',
                                                                             '-')

        if self._is_raw_images is None:
            self._is_raw_images = self._detect_if_images(doc)

        if verbose:
            options = ["'timeseries'", "'image'"]
            print("Dataset of type", options[int(self._is_raw_images)],
                  "detected.")

        if self._is_raw_images:
            image_resource = next(dR for dR in doc["dataResources"] if dR["resType"] ==
                                  "image")
            image_dir = image_resource["resPath"]
            image_dir_path = os.path.join(data_dir, image_dir)
            self._convert_to_bmp(image_dir_path, train_or_test=train_or_test)
            self._serialize_bmp_dir(train_or_test=train_or_test, **kwargs)
            for dR in doc["dataResources"]:
                if dR["resType"] == "image":
                    index = doc["dataResources"].index(dR)
                    doc["dataResources"][index]["resPath"] = 'timeseries/'
                    doc["dataResources"][index]["resType"] = 'timeseries'
                    doc["dataResources"][index]["resFormat"] = ['text/csv']
                    columns = [
                        {
                            "colIndex": 0,
                            "colName": "time",
                            "colType": "integer",
                            "role": ["timeIndicator"]
                        },
                        {
                            "colIndex": 1,
                            "colName": "val",
                            "colType": "real",
                            "role": ["attribute"]
                        }
                    ]
                    doc["dataResources"][index]["columns"] = columns
                    #dR["resPath"] = 'timeseries'
            mock_dir = os.path.join(self.tmp_dir, train_or_test)
            json_outfile = os.path.join(mock_dir, 'datasetDoc.json')
            with open(json_outfile, 'w+') as outfile:
                json.dump(doc, outfile, indent=4)
            table = next(dR for dR in doc["dataResources"] if dR["resType"] ==
                         "table")
            table_dir = table["resPath"]
            table_path = table_dir.split('/')[0]
            old_table_loc = os.path.join(data_dir, table_path)
            new_table_loc = os.path.join(mock_dir, table_path)
            copytree(old_table_loc, new_table_loc,
                     ignore=ignore_patterns('*.csv'))

            learningData_path = os.path.join(data_dir, table_dir)
            file_df = pd.read_csv(learningData_path)
            for dR in doc["dataResources"]:
                if dR["resType"] == "table":
                    attribute_col = self._role_col_name('attribute', dR)[0]
            file_df[attribute_col] = file_df[attribute_col].apply(lambda x:
                                                                      x.split('.')[0] + '.csv')
            new_learningData_path = os.path.join(mock_dir, table_dir)
            file_df.to_csv(new_learningData_path, index=False)
            data_dir = mock_dir

        if train_or_test.lower() == "train":
            self._train_dir = data_dir
            self._train_doc = doc
        elif train_or_test.lower() == "test":
            self._test_dir = data_dir
            self._test_doc = doc


    @property
    def train_dir(self):
        return self._train_dir

    @train_dir.setter
    def train_dir(self, root_dir):
        self._train_dir = root_dir

    @property
    def test_dir(self):
        return self._test_dir

    @test_dir.setter
    def test_dir(self, root_dir):
        self._test_dir = root_dir

    @staticmethod
    def _role_col_name(role, json_dict):
        """

        """
        column = []
        if "columns" in json_dict:
            column = [column["colName"] for column in json_dict["columns"] if role in
                    column["role"]]
        # temporary fix for incorrectly documented uu1_datasmash dataset
        else:
            column = ["value"]
        return column

    def _get_timeseries_col(self):
        """

        """
        time_series_doc = next(dR for dR in self._train_doc["dataResources"]
                               if dR["resType"] == 'timeseries')
        self.time_series_cols = self._role_col_name('attribute', time_series_doc)

    def _write_time_series(self, file_df, file_col, colName, resPath, lib_path):
        """
        file_df : dataframe with column that contains filenames of the
        timeseries
        file_col : name of the column of filenames
        colName : name of column that contains timeseries values
        resPath : name of directory that contains the files
        lib_path : name of the output library files
        """
        for file_ in file_df[file_col]:
            file_path = os.path.join(resPath, file_)

            time_series = pd.read_csv(file_path)[colName].dropna().tolist()
            if time_series != []:
                with open(lib_path, 'a') as outfile:
                    wr = csv.writer(outfile, delimiter=' ', quoting=csv.QUOTE_NONE)
                    wr.writerow(time_series)

    def write_libs(self, *, problem_type):
        """

        """
        print("In write_libs")
        self._get_timeseries_col()
        if self.tmp_dir == '':
            prefix = self.dataset_name + '-'
            self.tmp_dir = tempfile.mkdtemp(prefix=prefix, dir='./')
        table = next(dR for dR in self._train_doc["dataResources"]
                     if dR["resType"] == "table")
        #print('table',table)
        timeseries_path = next(dR for dR in self._train_doc["dataResources"]
                               if dR["resType"] == "timeseries")["resPath"]
        #print('timeseries_path',timeseries_path)
        columns = [column["colName"] for column in table["columns"]]
        index_col = self._role_col_name("index", table)
        ts_col = self._role_col_name("attribute", table)[0]  # "time_series_file"
        #print('ts_col',ts_col)
        class_col = self._role_col_name("suggestedTarget", table)

        table_path = table["resPath"]
        file_df = pd.read_csv(os.path.join(self._train_dir, table_path))
        if self.splitDataFrame is not None:
            file_df = pd.read_csv(os.path.join(self._train_dir, table_path)).join(self.splitDataFrame, rsuffix='_other')
            file_df = file_df[file_df['type'] == 'TRAIN']
        #print(file_df)
        # TODO: uncomment the following 8 lines once there actually are
        # unsupervised time series problems:

        #if problem_type.lower() == 'supervised':
        #    # currently does not support multilabel (i.e., assumes class_col has
        #    # only one element)
        #    class_col = class_col[0]
        #    self.class_list = sorted(file_df[class_col].unique().tolist())
        #    if not self.index_class_map:
        #        for index, class_ in enumerate(self.class_list):
        #            self.index_class_map[index] = class_

        # TODO: and remove the following 5 lines:

        class_col = class_col[0]
        self.class_list = sorted(file_df[class_col].unique().tolist())
        if not self.index_class_map:
            for index, class_ in enumerate(self.class_list):
                self.index_class_map[index] = class_

        # TODO - assumes "timeseries" as name of directory (could be images)
        timeseries_dir = os.path.join(self._train_dir, timeseries_path)
        for channel_num, time_series_col in enumerate(self.time_series_cols):
            lib_names = []
            channel_dir = 'channel_' + str(channel_num)
            channel_path = os.path.join(self.tmp_dir, channel_dir)
            self._mkdir(channel_path)
            self.channel_paths.append(channel_path)
            if problem_type.lower() == 'supervised':
                file_list = os.path.join(channel_path, 'library_list')
                for class_ in self.class_list:
                    lib_name = 'train_class_' + str(class_)
                    lib_path = os.path.join(channel_path, lib_name)
                    class_df = file_df[file_df[class_col] == class_]
                    num_time_series = len(class_df)

                    self._write_time_series(class_df, ts_col,
                                            time_series_col, timeseries_dir,
                                            lib_path)
                    with open(file_list, 'a') as outfile:
                        writer = csv.writer(outfile, delimiter=' ',
                                            quoting=csv.QUOTE_NONE)
                        writer.writerow([lib_name, class_, num_time_series])

                    lib_names.append(lib_path)
                wait_for_file(file_list)

            elif problem_type.lower() == 'unsupervised':
                dataset_path = os.path.join(channel_path, 'dataset')
                self._write_time_series(file_df, ts_col,
                                        time_series_col, timeseries_dir,
                                        dataset_path)
                lib_names.append(dataset_path)

            for lib_name in lib_names:
                wait_for_file(lib_name)

            self.channel_problems[channel_dir] = {}
            self.channel_problems[channel_dir]['test'] = None
            self.channel_problems[channel_dir]['raw_libs'] = lib_names
        if problem_type.lower() == 'supervised':
            return self.tmp_dir, self.channel_paths, self.channel_problems, self.class_list
        elif problem_type.lower() == 'unsupervised':
            return self.tmp_dir, self.channel_paths, len(file_df)
        
    def cluster_libs(self, lib_files, *, n_clusters, cluster_class=None):
        """

        """
        class_map = {}
        for channel_path in self.channel_paths:
            lib_names = []
            file_list = os.path.join(channel_path, 'library_list')
            os.remove(file_list)
            artificial_class = 0
            for class_, lib_file in zip(self.class_list, lib_files):
                lib_name = 'train_class_' + str(class_)
                lib_path = os.path.join(channel_path, lib_name)
                if isinstance(n_clusters, int):
                    n_clusters_list = [n_clusters]
                else:
                    n_clusters_list = n_clusters
                for n_clusters_ in n_clusters_list:
                    if cluster_class is None:
                        clf = KMeans(n_clusters=n_clusters_)
                    else:
                        clf = cluster_class(n_clusters=n_clusters_)

                    dst_path = lib_path + ".dst"
                    #smash(lib_path, outfile=dst_path)
                    smash(lib_file, outfile=dst_path)
                    distance_matrix = np.loadtxt(dst_path, dtype=float)
                    distance_matrix += distance_matrix.T

                    clusters = clf.fit_predict(distance_matrix)
                    clusters = pd.DataFrame(clusters,
                                            columns=['cluster'])
                    lib_data = pd.read_csv(lib_file, delimiter=' ',
                                           header=None)
                    lib_data = pd.concat([lib_data, clusters], axis=1)
                    cluster_list = sorted(lib_data['cluster'].unique().tolist())
                    for i in cluster_list:
                        sublib_data = lib_data[lib_data['cluster'] == i].iloc[:, :-1]
                        num_time_series = len(sublib_data)
                        sublib_name = lib_name + '_' + str(i)
                        sublib_path = os.path.join(channel_path,
                                                   sublib_name)
                        sublib_data.to_csv(sublib_path, sep=' ',
                                           header=False, index=False)
                        wait_for_file(sublib_path)
                        lib_names.append(sublib_path)
                        class_map[artificial_class] = class_

                        with open(file_list, 'a') as outfile:
                            writer = csv.writer(outfile, delimiter=' ',
                                                quoting=csv.QUOTE_NONE)
                            writer.writerow([sublib_name, artificial_class,
                                             num_time_series])
                            #print([sublib_name, artificial_class,
                            #       num_time_series])

                        artificial_class += 1

                    os.remove(dst_path)
                #os.remove(lib_path)


            channel_dir = channel_path.split('/')[-1]
            self.channel_problems[channel_dir]['test'] = None
            self.channel_problems[channel_dir]['raw_libs'] = lib_names

        self.index_class_map = class_map

    def write_test(self):
        """

        """
        print('in write_test')
        if not os.path.isdir(self.tmp_dir):
            os.mkdir(self.tmp_dir)
        test_dir = os.path.join(self.tmp_dir, 'test')
        self._mkdir(test_dir)
        table = next(dR for dR in self._test_doc["dataResources"] if dR["resType"] ==
                     "table")
        table_path = table["resPath"]
        timeseries_path = next(dR for dR in self._test_doc["dataResources"]
                               if dR["resType"] == "timeseries")["resPath"]
        ts_col = self._role_col_name("attribute", table)[0]  # "time_series_file"
        file_df = pd.read_csv(os.path.join(self._test_dir, table_path))
        timeseries_dir = os.path.join(self._test_dir, timeseries_path)
        if self.splitDataFrame is not None:
            file_df = pd.read_csv(os.path.join(self._train_dir, table_path)).join(self.splitDataFrame, rsuffix='_other')
            file_df = file_df[file_df['type'] == 'TEST']
        for time_series_col, channel_dir in zip(self.time_series_cols,
                                                self.channel_paths):
            channel_name = channel_dir.split('/')[-1]
            test_channel_dir = os.path.join(test_dir, channel_name)
            self._mkdir(test_channel_dir)
            test_channel_file = os.path.join(test_channel_dir, 'test')
            self._write_time_series(file_df, ts_col,
                                    time_series_col, timeseries_dir,
                                    test_channel_file)
            wait_for_file(test_channel_file)
            self.channel_problems[channel_name]['test'] = test_channel_file
        return self.channel_problems
