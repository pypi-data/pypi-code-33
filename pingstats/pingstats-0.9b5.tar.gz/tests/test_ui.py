import pingstats
from pingstats import ui

from pingstats import Pings, X_COLUMN_SCALE, Y_ROW_SCALE, plot_pings


def test_pane():
    test_columns, test_rows = 100, 21
    test_pane = ui.Pane(test_columns, test_rows)

    assert test_pane.columns == test_columns
    assert test_pane.rows == test_rows


def test_pings_pane():
    test_columns, test_rows = 100, 21
    test_pings = Pings('127.0.0.1')

    test_object = ui.PingsPane(test_columns, test_rows, test_pings)

    assert test_object.columns == test_columns
    assert test_object.rows == test_rows
    for i, pings in enumerate(test_pings):
        assert test_object.average_data == test_pings.average_data
        assert test_object.realtime_data == test_pings.realtime_data

        if i == 10:
            break


class TestProgStatus:
    def test_init(self, capsys):
        self.test_columns, self.test_rows = 100, 21
        self.test_pings = Pings('127.0.0.1')

        self.test_object = ui.ProgStatus(self.test_columns, self.test_rows, self.test_pings)
        assert isinstance(self.test_object, ui.PingsPane)

        # FUNCTIONALITY TEST
        captured = capsys.readouterr()

        assert captured.out.count(pingstats.PROG_NAME and pingstats.__version__)
        assert captured.out.count(self.test_pings.address)
        assert captured.out.count('%s %s' % (pingstats.PROG_NAME, pingstats.__version__))
        assert captured.out.count('ping data from %s' % self.test_pings.address)

        left = '%s %s ' % (pingstats.PROG_NAME, pingstats.__version__)
        right = ' ping data from %s' % self.test_pings.address
        assert captured.out.count('-') == self.test_columns - len(left + right)

    def test_1_line(self, capsys):
        self.test_columns, self.test_rows = 100, 21
        self.test_pings = Pings('127.0.0.1')
        for i, ping in enumerate(self.test_pings):
            self.test_object = ui.ProgStatus(self.test_columns, self.test_rows, self.test_pings)
            captured = capsys.readouterr()
            assert len(captured.out.splitlines()) == 1
            if i == 50:
                break


class TestRealtimeStatus:
    def test_no_packets_dropped(self, capsys):
        test_columns, test_rows = 100, 21

        test_data = []
        for i in range(100):
            test_data.append(i)
            test_pings = Pings('127.0.0.1', realtime_data=test_data)
            test_object = ui.RealtimeStatus(test_columns, test_rows, test_pings)
            captured = capsys.readouterr()
            assert captured.out.count('Displaying %s total packets from %s' % (len(test_data), test_pings.address))

        test_columns, test_rows = 100, 21
        test_pings = Pings('127.0.0.1')
        for i, ping in enumerate(test_pings):
            test_object = ui.RealtimeStatus(test_columns, test_rows, test_pings)
            captured = capsys.readouterr()
            assert len(captured.out.splitlines()) == 1
            if i == 50:
                break

    def test_1_packet_dropped(self, capsys):
        test_columns, test_rows = 100, 21

        test_data = [-1]
        test_pings = Pings('127.0.0.1', realtime_data=test_data)
        test_object = ui.RealtimeStatus(test_columns, test_rows, test_pings)
        captured = capsys.readouterr()
        assert captured.out.count('1 packet dropped of %s' % len(test_data))

    def test_multiple_packets_dropped(self, capsys):
        test_columns, test_rows = 100, 21

        test_data = [-1, -1]
        for i in range(100):
            if i % 2:
                test_data.append(-1)
            else:
                test_data.append(1)

            test_pings = Pings('127.0.0.1', realtime_data=test_data)
            test_object = ui.RealtimeStatus(test_columns, test_rows, test_pings)
            captured = capsys.readouterr()
            assert captured.out.count('%s packets dropped of %s' % (test_data.count(-1), len(test_data)))

        test_data = [-1, -1]
        test_pings = Pings('127.0.0.1', realtime_data=test_data)
        for i, ping in enumerate(test_pings):
            test_object = ui.RealtimeStatus(test_columns, test_rows, test_pings)
            captured = capsys.readouterr()
            assert len(captured.out.splitlines()) == 1
            if i == 18:
                break


class TestAverageStatus:
    def test_connection_dropped(self, capsys):
        test_columns, test_rows = 100, 21

        test_data = [-1]
        for i in range(100):
            test_data.append(-1)
            test_pings = Pings('127.0.0.1', average_data=test_data)
            test_object = ui.AverageStatus(test_columns, test_rows, test_pings)
            captured = capsys.readouterr()
            assert captured.out.count('Connection dropped!')
            assert len(captured.out.splitlines()) == 1

    def test_display_average(self, capsys):
        test_columns, test_rows = 100, 21

        test_data = []
        for i in range(100):
            test_data.append(i)
            test_pings = Pings('127.0.0.1', average_data=test_data)
            test_object = ui.AverageStatus(test_columns, test_rows, test_pings)
            captured = capsys.readouterr()
            assert captured.out.count('Displaying the average of %s '
                                      'total packets from %s'
                                      % (len(test_data), test_pings.address))
            assert len(captured.out.splitlines()) == 1


def test_raw_status(capsys):
    test_columns, test_rows = 100, 21
    test_pings = Pings('127.0.0.1')

    test_object = ui.RawStatus(test_columns, test_rows, test_pings)
    assert isinstance(test_object, ui.PingsPane)
    output = capsys.readouterr()
    assert output.out == test_pings.current_line.center(test_columns, '-') + '\n'
    assert len(output.out.splitlines()) == 1


class TestDroppedStatus:
    def test_init(self, capsys):
        test_columns, test_rows, test_data = 100, 21, [1, 2, 3]
        test_pings = Pings('127.0.0.1', realtime_data=test_data)
        test_object = ui.DroppedStatus(test_columns, test_rows, test_pings)
        assert isinstance(test_object, ui.PingsPane)

        # FUNCTIONALITY TEST
        captured = capsys.readouterr()

        assert captured.out.count(pingstats.PROG_NAME and pingstats.__version__)
        assert captured.out.count(test_pings.address)
        assert captured.out.count('%s %s' % (pingstats.PROG_NAME, pingstats.__version__))
        assert captured.out.count(' - %s' % test_pings.address)

    def test_display_dropped(self, capsys):
        test_columns, test_rows, test_data = 100, 21, [-1, -1, -1]
        test_pings = Pings('127.0.0.1', realtime_data=test_data)
        test_object = ui.DroppedStatus(test_columns, test_rows, test_pings)
        assert isinstance(test_object, ui.PingsPane)

        # FUNCTIONALITY TEST
        captured = capsys.readouterr()

        assert captured.out.count('%i packets dropped of %i from %s'
                                  % (test_data.count(-1), len(test_data), test_pings.address))


def test_plot_pane():
    test_columns, test_rows = 100, 21
    test_pings = Pings('127.0.0.1')

    test_object = ui.PlotPane(test_columns, test_rows, test_pings)

    assert test_object.columns == test_columns - X_COLUMN_SCALE
    assert test_object.rows == test_rows - Y_ROW_SCALE


def test_realtime_plot(capsys):
    test_data = [i for i in range(100)]
    test_columns, test_rows = 100, 21
    test_pings = Pings('127.0.0.1', realtime_data=test_data)

    test_object = ui.RealtimePlot(test_columns, test_rows, test_pings)

    assert isinstance(test_object, ui.PlotPane)

    result_captured = capsys.readouterr()

    plot_pings(test_data, test_columns - X_COLUMN_SCALE, test_rows - Y_ROW_SCALE)

    test_captured = capsys.readouterr()

    assert result_captured.out == test_captured.out


def test_average_plot(capsys):
    test_data = [i for i in range(100)]
    test_columns, test_rows = 100, 21
    test_pings = Pings('127.0.0.1', average_data=test_data)

    assert test_pings.average_data == test_data

    test_object = ui.AveragePlot(test_columns, test_rows, test_pings)

    assert isinstance(test_object, ui.PlotPane)

    result_captured = capsys.readouterr()

    plot_pings(test_data, test_columns - X_COLUMN_SCALE, test_rows - Y_ROW_SCALE)

    test_captured = capsys.readouterr()

    assert result_captured.out == test_captured.out


def test_realtime_pane(capsys):
    test_data = [i for i in range(100)]
    test_columns, test_rows = 100, 21
    test_pings = Pings('127.0.0.1', realtime_data=test_data)

    test_object = ui.RealtimePane(test_columns, test_rows, test_pings)

    assert isinstance(test_object, ui.PlotPane)

    result_captured = capsys.readouterr()

    plot_pings(test_data, test_columns - X_COLUMN_SCALE, test_rows - Y_ROW_SCALE)
    ui.RealtimeStatus(test_columns, test_rows, test_pings)

    test_captured = capsys.readouterr()
    assert len(test_captured.out.splitlines()) == len(test_captured.out.splitlines())


def test_average_pane(capsys):
    test_data = [i for i in range(100)]
    test_columns, test_rows = 100, 21
    test_pings = Pings('127.0.0.1', average_data=test_data)

    test_object = ui.AveragePane(test_columns, test_rows, test_pings)

    assert isinstance(test_object, ui.PlotPane)

    result_captured = capsys.readouterr()

    plot_pings(test_data, test_columns, test_rows)
    ui.AverageStatus(test_columns, test_rows, test_pings)

    test_captured = capsys.readouterr()
    # assert result_captured.out == test_captured.out  # CANNOT USE AS TEST, RESULTS NOT ALWAYS THE SAME IN HIPSTERPLOT

    assert len(test_captured.out.splitlines()) == len(test_captured.out.splitlines())

# pylama:ignore=W0612
