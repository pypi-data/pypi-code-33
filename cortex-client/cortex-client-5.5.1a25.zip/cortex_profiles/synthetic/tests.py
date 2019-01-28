from cortex_profiles.synthetic import defaults

def test_insight_distribution(f):

    derived_interactions = f.raw_insight_distributions(f.insights("abc"))
    for i in defaults.INTERACTION_CONFIG:
        assert len(derived_interactions[i["interaction"]]) == len(set(derived_interactions[i["interaction"]]))

    mutually_exclusive_pairs = [
        (i["interaction"], me)
        for i in defaults.INTERACTION_CONFIG
        for me in i["mutuallyExlusiveOf"]
        if i["mutuallyExlusiveOf"]
    ]
    print(mutually_exclusive_pairs)
    for me_a, me_b in mutually_exclusive_pairs:
        assert len(set(derived_interactions[me_a]).intersection(
            set(derived_interactions[me_b]))) == 0, "{} and {} are not mutually exclusive".format(me_a, me_b)

    print(f.insight_distributions(f.insights("abc")))


def test_insight_interaction_events(f):
    print(f.interactions("test-user-1", f.sessions("test-user-1"), f.insights(profileId="test-user-1")))



