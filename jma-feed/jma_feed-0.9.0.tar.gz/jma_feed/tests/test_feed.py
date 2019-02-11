from jma_feed.feed import AtomFeed


def describe_feed():
    def test_id(expect, feed_samples):
        feed_sample = feed_samples[0]
        feed = AtomFeed(feed_sample)
        expect(feed.id) == 'urn:uuid:4e2e12c8-4601-3c0f-8c8a-75cc83dcf6ac'

    def test_title(expect, feed_samples):
        feed_sample = feed_samples[0]
        feed = AtomFeed(feed_sample)
        expect(feed.title) == '高頻度（定時）'

    def test_entry_id(expect, feed_samples):
        feed_sample = feed_samples[0]
        feed = AtomFeed(feed_sample)
        entry = feed.entries[0]
        expect(entry.id) == 'urn:uuid:d25c00b2-c23d-313c-830b-201eb7ada516'

    def test_entry_link(expect, feed_samples):
        feed_sample = feed_samples[0]
        feed = AtomFeed(feed_sample)
        entry = feed.entries[-1]
        expect(
            entry.link
        ) == 'http://www.data.jma.go.jp/developer/xml/data/352ef0d9-4f5d-36c7-bf0d-f2ffcc31c4e0.xml'
