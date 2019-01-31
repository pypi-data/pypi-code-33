from setuptools import setup


version = {}
with open("datasmash/_version.py") as fp:
    exec(fp.read(), version)


setup(name='datasmash',
      version=version['__version__'],
      packages=['datasmash.bin', 'datasmash'],
      keywords='d3m_primitive',
      install_requires=['pandas', 'numpy==1.15.4', 'scikit-learn==0.20.2', 'imageio', 'd3m'],
      include_package_data=True,
      package_data={
          'bin':
              ['bin/smash',
               'bin/embed',
               'bin/smashmatch',
               'bin/Quantizer',
               'bin/serializer',
               'bin/genESeSS',
               'bin/genESeSS_feature',
               'bin/XgenESeSS'
              ]
      },

      # metadata for PyPI upload
      url='https://gitlab.datadrivendiscovery.org/uchicago/datasmash',
      download_url=('https://gitlab.datadrivendiscovery.org/uchicago/datasmash/archive/'
                    + version['__version__'] + '.tar.gz'),

      maintainer_email='virotaru@uchicago.edu',
      maintainer='Victor Rotaru',

      description=('Quantifier of universal similarity amongst arbitrary data'
                   + ' streams without a priori knowledge, features, or'
                   + ' training.'),

      classifiers=[
          "Programming Language :: Python :: 3"
      ],
      entry_points={
          'd3m.primitives': [
              'datasmash.d3m_SmashClassification=datasmash.d3m_classification:d3m_SmashClassification',
              'datasmash.d3m_CSmashClassification=datasmash.d3m_cclassification:d3m_CSmashClassification',
              'datasmash.d3m_GSmashClassification=datasmash.d3m_gclassification:d3m_GSmashClassification',
              'datasmash.d3m_CGSmashClassification=datasmash.d3m_cgclassification:d3m_CGSmashClassification',
              'datasmash.d3m_SmashClustering= datasmash.d3m_clustering:d3m_SmashClustering',
              'datasmash.d3m_SmashDistanceMetricLearning=datasmash.d3m_distance_metric_learning:d3m_SmashDistanceMetricLearning',
              'datasmash.d3m_SmashEmbedding= datasmash.d3m_embedding:d3m_SmashEmbedding',
              'datasmash.d3m_SmashFeaturization=datasmash.d3m_featurization:d3m_SmashFeaturization',
              'datasmash.d3m_XG1= datasmash.d3m_xgenesess:d3m_XG1',
              'datasmash.d3m_XG2= datasmash.d3m_genesess:d3m_XG2',
              'datasmash.PFSA_CATEGORICAL_FORCASTER= datasmash.d3m_PFSA_CATEGORICAL_FORCASTER:PFSA_CATEGORICAL_FORCASTER',
              'datasmash.PFSA_FORCASTER= datasmash.d3m_PFSA_FORCASTER:PFSA_FORCASTER',
              'datasmash.d3m_Quantizer=datasmash.d3m_quantizer:d3m_Quantizer'
          ],
      },
     )
