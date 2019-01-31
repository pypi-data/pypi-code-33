import setuptools

from sri.common import config

setuptools.setup(
    name = config.PACKAGE_NAME,

    version = config.VERSION,

    description = 'Graph and PSL based TA1 primitive for D3M',
    long_description = 'Graph and PSL based TA1 primitive for D3M',
    keywords = 'd3m_primitive',

    maintainer_email = config.EMAIL,
    maintainer = config.MAINTAINER,

    # The project's main homepage.
    url = config.REPOSITORY,

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        'Programming Language :: Python :: 3.6',
    ],

    # packages = setuptools.find_packages(exclude = ['contrib', 'docs', 'tests']),
    packages = [
        'sri',
        'sri.autoflow',
        'sri.baseline',
        'sri.common',
        'sri.graph',
        'sri.pipelines',
        'sri.psl',
        'sri.psl.cli',
        'sri.tpot',
    ],

    include_package_data = True,
    package_data = {
        'sri.psl.cli': [
            'psl-cli-CANARY-2.1.5.jar',
            'link_prediction_template.data',
            'link_prediction_template.psl'
            'general_relational_template.data',
            'general_relational_template.psl',
            'relational_timeseries_template.data',
            'relational_timeseries_template.psl',
        ]
    },

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires = [
        # Base
        'd3m', 'psutil',
        # TPOT
        'pathos', 'SRITPOT',
        # Testing
        'sripipeline',

        # Already provided by d3m (let d3m manage the exact versions):
        # 'networkx', 'numpy', 'pandas', 'scikit-learn',
    ],

    python_requires = '>=3.6',

    entry_points = {
        'd3m.primitives': [
            'sri.autoflow.Conditioner = sri.autoflow.conditioner:Conditioner',
            'sri.autoflow.DatasetTextReader = sri.autoflow.dataset_text_reader:DatasetTextReader',
            'sri.autoflow.StaticEnsembler = sri.autoflow.static_ensembler:StaticEnsembler',
            'sri.baseline.MeanBaseline = sri.baseline.mean:MeanBaseline',
            'sri.graph.CollaborativeFilteringParser = sri.graph.collaborative_filtering:CollaborativeFilteringParser',
            'sri.graph.CommunityDetectionParser = sri.graph.community_detection:CommunityDetectionParser',
            'sri.graph.GraphMatchingParser = sri.graph.graph_matching:GraphMatchingParser',
            'sri.graph.GraphTransformer = sri.graph.transform:GraphTransformer',
            'sri.graph.VertexNominationParser = sri.graph.vertex_nomination:VertexNominationParser',
            'sri.psl.CollaborativeFilteringLinkPrediction = sri.psl.collaborative_filtering_link_prediction:CollaborativeFilteringLinkPrediction',
            'sri.psl.CommunityDetection = sri.psl.community_detection:CommunityDetection',
            # Until we have preprocessing code to prepare the data, do not expose this entrypoint.
            # 'sri.psl.GeneralRelational = sri.psl.general_relational:GeneralRelational',
            'sri.psl.GeneralRelationalDataset = sri.psl.general_relational_dataset:GeneralRelationalDataset',
            'sri.psl.GraphMatchingLinkPrediction = sri.psl.graph_matching_link_prediction:GraphMatchingLinkPrediction',
            'sri.psl.LinkPrediction = sri.psl.link_prediction:LinkPrediction',
            'sri.psl.RelationalTimeseries = sri.psl.relational_timeseries:RelationalTimeseries',
            'sri.psl.VertexNomination = sri.psl.vertex_nomination:VertexNomination',
            'sri.tpot.StackingOperator = sri.tpot.stacking:StackingOperator',
            'sri.tpot.ZeroCount = sri.tpot.zerocount:ZeroCount',

            # TODO(eriq): Will be moved to common primitives when actually implemented.
            'data.GraphNodeSplitter = sri.graph.node_splitter:GraphNodeSplitter',
            'data.GraphToEdgeList = sri.graph.graph_to_edgelist:GraphToEdgeList',
            'data.EdgeListToGraph = sri.graph.edgelist_to_graph:EdgeListToGraph',
        ]
    }
)
