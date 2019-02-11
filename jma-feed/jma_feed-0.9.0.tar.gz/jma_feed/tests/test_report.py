from jma_feed.report import Report


def describe_feed():
    def test_mete1_report_control(expect, report_samples):
        report_sample = report_samples[0]
        report = Report(report_sample)
        expect(report.control.title) == '府県天気概況'
        expect(report.control.status) == '通常'

    def test_mete2_report_control(expect, report_samples):
        report_sample = report_samples[1]
        report = Report(report_sample)
        expect(report.control.title) == '気象警報・注意報'
        expect(report.control.editorial_office) == '和歌山地方気象台'

    def test_seis1_report_control(expect, report_samples):
        report_sample = report_samples[2]
        report = Report(report_sample)
        expect(report.control.title) == '震源・震度に関する情報'
        expect(report.control.date_time) == '2019-02-10T00:57:21Z'

    def test_volc1_report_control(expect, report_samples):
        report_sample = report_samples[3]
        report = Report(report_sample)
        expect(report.control.title) == '降灰予報（定時）'
        expect(report.control.publishing_office) == '気象庁地震火山部'

    def test_mete1_report_head(expect, report_samples):
        report_sample = report_samples[0]
        report = Report(report_sample)
        expect(report.head.title) == '天気概況'
        expect(report.head.info_type) == '発表'
        expect(report.head.headline_text) == '千葉県では、１１日朝から１１日昼過ぎまで大雪や電線等への着雪に注意してください。'

    def test_mete2_report_head(expect, report_samples):
        report_sample = report_samples[1]
        report = Report(report_sample)
        expect(report.head.info_kind) == '気象警報・注意報'
        expect(report.head.headline_information_list[0].type) == '気象警報・注意報（府県予報区等）'
        expect(report.head.headline_information_list[0].items[0].areas[0].name) == '和歌山県'

    def test_seis1_report_head(expect, report_samples):
        report_sample = report_samples[2]
        report = Report(report_sample)
        expect(report.head.report_date_time) == '2019-02-10T09:57:00+09:00'
        expect(report.head.serial) == '1'

    def test_volc1_report_head(expect, report_samples):
        report_sample = report_samples[3]
        report = Report(report_sample)
        expect(report.head.info_kind_version) == '1.1_0'
        expect(report.head.headline_information_list[0].items[0].areas_code_type) == '火山名'
        expect(report.head.headline_information_list[0].items[0].kinds[0].name) == '降灰予報（定時）'

    def test_mete1_report_body(expect, report_samples):
        report_sample = report_samples[0]
        report = Report(report_sample)
        expect(report.body.target_area.code) == '120000'

    def test_mete2_report_body(expect, report_samples):
        report_sample = report_samples[1]
        report = Report(report_sample)
        expect(report.body.warnings[0].items[0].change_status) == '警報・注意報種別に変化有'
        expect(report.body.warnings[-1].items[-1].kinds[-1].name) == '強風注意報'

    def test_seis1_report_body(expect, report_samples):
        report_sample = report_samples[2]
        report = Report(report_sample)
        expect(report.body.earthquakes[0].arrival_time) == '2019-02-10T09:54:00+09:00'
        expect(report.body.earthquakes[0].hypocenter.area.name) == '岩手県沖'
        expect(report.body.comments.forecast_comment.text) == 'この地震による津波の心配はありません。'

    def test_volc1_report_body(expect, report_samples):
        report_sample = report_samples[3]
        report = Report(report_sample)
        expect(report.body.volcano_infos[0].items[-1].kind.name) == '降灰予報（定時）'
        expect(report.body.ash_infos[-1].start_time) == '2019-02-11T21:00:00+09:00'
        expect(report.body.ash_infos[-1].items[-1].areas[0].name) == '宮崎県小林市'
