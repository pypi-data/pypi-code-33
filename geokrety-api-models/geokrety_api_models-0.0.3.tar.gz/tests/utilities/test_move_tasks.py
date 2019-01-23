
from geokrety_api_models import Geokret, Move, MoveComment, User
from geokrety_api_models.utilities.const import (GEOKRET_TYPE_TRADITIONAL,
                                                 MOVE_COMMENT_TYPE_COMMENT,
                                                 MOVE_COMMENT_TYPE_MISSING,
                                                 MOVE_TYPE_COMMENT,
                                                 MOVE_TYPE_DIPPED,
                                                 MOVE_TYPE_DROPPED,
                                                 MOVE_TYPE_GRABBED,
                                                 MOVE_TYPE_SEEN)
from geokrety_api_models.utilities.move_tasks import (update_geokret_and_moves,
                                                      update_geokret_holder,
                                                      update_geokret_total_moves_count,
                                                      update_move_country_and_altitude,
                                                      update_move_distances)

from .. import DatabaseTest


class TestMoveTasksHelper(DatabaseTest):

    def _blend(self):
        """Create mocked Geokret/User"""
        # Users
        self.admin = self.mixer.blend(User)
        self.user1 = self.mixer.blend(User)
        self.user2 = self.mixer.blend(User)
        self.user3 = self.mixer.blend(User)
        self.user4 = self.mixer.blend(User)

        self.geokret1 = self.mixer.blend(Geokret, type=GEOKRET_TYPE_TRADITIONAL,
                                         owner=self.user1, holder=self.user1, tracking_code="ABC123",
                                         created_on_datetime="2017-12-01T14:18:22")

        # Moves
        self.move8 = self.mixer.blend(Move, type=MOVE_TYPE_DROPPED, geokret=self.geokret1,
                                      author=self.user1, moved_on_datetime="2017-12-01T14:18:22",
                                      latitude=43.693633, longitude=6.860933)
        self.move6 = self.mixer.blend(Move, type=MOVE_TYPE_GRABBED, geokret=self.geokret1,
                                      author=self.user2, moved_on_datetime="2017-12-01T14:19:22")
        self.move7 = self.mixer.blend(Move, type=MOVE_TYPE_COMMENT, geokret=self.geokret1,
                                      author=self.user2, moved_on_datetime="2017-12-01T14:20:22")
        self.move1 = self.mixer.blend(Move, type=MOVE_TYPE_DROPPED, geokret=self.geokret1,
                                      author=self.user2, moved_on_datetime="2017-12-01T14:21:22",
                                      latitude=43.694483, longitude=6.85575)
        self.move5 = self.mixer.blend(Move, type=MOVE_TYPE_SEEN, geokret=self.geokret1,
                                      author=self.user3, moved_on_datetime="2017-12-01T14:22:22",
                                      latitude=43.701767, longitude=6.84085)
        self.move4 = self.mixer.blend(Move, type=MOVE_TYPE_DIPPED, geokret=self.geokret1,
                                      author=self.user4, moved_on_datetime="2017-12-01T14:23:22",
                                      latitude=43.6792, longitude=6.852933)

        self.move2 = self.mixer.blend(Move, type=MOVE_TYPE_COMMENT, geokret=self.geokret1,
                                      author=self.user1, moved_on_datetime="2017-12-01T14:24:22")
        self.move3 = self.mixer.blend(Move, type=MOVE_TYPE_DIPPED, geokret=self.geokret1,
                                      author=self.user4, moved_on_datetime="2017-12-01T14:25:22",
                                      latitude=43.704233, longitude=6.869833)
        self.move9 = self.mixer.blend(Move, type=MOVE_TYPE_COMMENT, geokret=self.geokret1,
                                      author=self.user3, moved_on_datetime="2017-12-01T14:28:22")

    def test_update_move_distances(self):
        """Check Move Tasks: compute move distances"""

        self._blend()

        # run the function
        update_move_distances(self.session, self.geokret1.id)
        self.session.commit()

        # Check in database
        moves = self.session.query(Move) \
            .filter(Move.geokret_id == self.geokret1.id) \
            .order_by(Move.moved_on_datetime.asc()).all()
        self.assertEqual(moves[0].distance, 0)
        self.assertEqual(moves[1].distance, 0)
        self.assertEqual(moves[2].distance, 0)
        self.assertEqual(moves[3].distance, int(round(0.428142805874)))
        self.assertEqual(moves[4].distance, int(round(1.44869620611)))
        self.assertEqual(moves[5].distance, int(round(2.69014884056)))
        self.assertEqual(moves[6].distance, 0)
        self.assertEqual(moves[7].distance, int(round(3.09681445874)))

    def test_update_geokret_total_distance(self):
        """Check Move Tasks: compute GeoKret total distance"""

        self._blend()

        # run the function
        update_move_distances(self.session, self.geokret1.id)
        self.session.commit()

        # Check in database
        self.assertEqual(self.geokret1.distance, 7)

    def test_update_geokret_caches_count(self):
        """Check Move Tasks: compute GeoKret total caches count"""

        self._blend()

        # run the function
        update_geokret_total_moves_count(self.session, self.geokret1.id)
        self.session.commit()

        # Check in database
        self.assertEqual(self.geokret1.caches_count, 5)

    def test_update_geokret_holder(self):
        """Check Move Tasks: compute GeoKret holder"""

        self._blend()

        # run the function
        update_geokret_holder(self.session, self.geokret1.id)
        self.session.commit()

        # Check in database
        self.assertEqual(self.geokret1.holder, self.user4)

    def test_update_geokret_last_position(self):
        """Check Move Tasks: compute GeoKret last position"""

        self._blend()

        # run the function
        update_move_distances(self.session, self.geokret1.id)
        self.session.commit()

        # Check in database
        self.assertEqual(self.geokret1.last_position_id, None)

    def test_update_geokret_last_move(self):
        """Check Move Tasks: compute GeoKret last move"""

        self._blend()

        # run the function
        update_move_distances(self.session, self.geokret1.id)
        self.session.commit()

        # Check in database
        self.assertEqual(self.geokret1.last_move_id, self.move9.id)

    def test_update_country_and_altitude(self):
        """Check Move Tasks: update country and altitude"""

        self._blend()

        # run the function
        update_move_country_and_altitude(self.session, self.move1.id)
        self.session.commit()

        # Check in database
        move = self.session.query(Move) \
            .get(self.move1.id)
        self.assertEqual(move.country, 'FR')
        self.assertNotEqual(move.altitude, '720')
        self.assertEqual(move.altitude, 720)

    def test_update_country_and_altitude_errors(self):
        """Check Move Tasks: update country and altitude failing api"""

        # Check api error responses
        user = self.mixer.blend(User)
        geokret = self.mixer.blend(Geokret, created_on_datetime="2017-12-01T17:17:17")
        another_move = self.mixer.blend(Move, type=MOVE_TYPE_DROPPED, geokret=geokret,
                                        author=user, moved_on_datetime="2017-12-01T17:17:17",
                                        latitude=42, longitude=42)
        # run the function
        update_move_country_and_altitude(self.session, another_move.id)

        # Check in database
        self.assertEqual(another_move.country, 'XYZ')
        self.assertEqual(another_move.altitude, '-2000')

    def test_update_geokret_missing_status(self):
        """Check Move Tasks: compute GeoKret missing status"""
        geokret = self.mixer.blend(Geokret,
                                   missing=False,
                                   created_on_datetime="2017-12-01T21:54:17")
        move1 = self.mixer.blend(Move,
                                 geokret=geokret, type=MOVE_TYPE_DROPPED,
                                 moved_on_datetime="2019-01-01T21:54:44")

        move2 = self.mixer.blend(Move,
                                 geokret=geokret, type=MOVE_TYPE_COMMENT,
                                 moved_on_datetime="2019-01-01T21:54:59")

        self.mixer.blend(MoveComment, move=move1, type=MOVE_COMMENT_TYPE_COMMENT)
        update_geokret_and_moves(self.session, geokret.id, [move1.id, move2.id])
        self.assertFalse(geokret.missing)

        self.mixer.blend(MoveComment, move=move2, type=MOVE_COMMENT_TYPE_COMMENT)
        update_geokret_and_moves(self.session, move2.geokret.id)
        self.assertFalse(geokret.missing)

        self.mixer.blend(MoveComment, move=move1, type=MOVE_COMMENT_TYPE_MISSING)
        update_geokret_and_moves(self.session, move1.geokret.id)
        self.assertTrue(geokret.missing)

        move3 = self.mixer.blend(Move, geokret=geokret, type=MOVE_TYPE_SEEN,
                                 moved_on_datetime="2019-01-01T22:29:07")
        update_geokret_and_moves(self.session, move3.geokret.id)
        self.assertFalse(geokret.missing)

        self.mixer.blend(MoveComment, move=move3, type=MOVE_COMMENT_TYPE_MISSING)
        update_geokret_and_moves(self.session, move3.geokret.id)
        self.assertTrue(geokret.missing)
