

import unittest
import mtlib
import asyncio

import asynctest


DEVICE_IP = "192.168.1.209"

class AsyncTest(asynctest.TestCase):
    def setUp(self):
        pass

        
    async def test_state(self):
        d = mtlib.Device(DEVICE_IP)
        result = await d.async_get_state()    
        self.assertIn(result, ["ON","OFF"])


    @unittest.skip("Broken")
    def test_state_no_route(self):
        d = mtlib.Device("192.168.1.1")
        with self.assertRaises(mtlib.exceptions.NoRouteToHost):
            result = self.loop.run_until_complete( d.async_get_state() )   

    @unittest.skip("Broken")
    def test_state_connection_refused(self):
        d = mtlib.Device("192.168.1.3")
        with self.assertRaises(mtlib.exceptions.ConnectionRefused):
            result = self.loop.run_until_complete( d.async_get_state() )   

    #TEST takes 90+ seconds to complete!!!
    # def test_state_connection_timed_out(self):
    #     d = mtlib.Device("192.168.1.254")
    #     with self.assertRaises(mtlib.exceptions.CoapRequestTimedOut):
    #         result = self.loop.run_until_complete( d.async_get_state() )   


    @unittest.skip("Broken")
    def test_state_name_not_resolved(self):
        d = mtlib.Device("bad-host-name")
        with self.assertRaises(mtlib.exceptions.NameNotResolved):
            result = self.loop.run_until_complete( d.async_get_state() )   


    async def test_info(self):
        d = mtlib.Device(DEVICE_IP)
        result = await d.async_get_info() 
        self.assertIn("serial", result)
        self.assertIn("deviceName", result)
        self.assertIn("model", result)

    async def test_commands(self):
        d = mtlib.Device(DEVICE_IP)
        result = await d.async_send_command("ON")   
        self.assertEqual(result, True)
        result = await d.async_get_state() 
        self.assertEqual(result, "ON")


        result = await d.async_send_command("OFF    ")   
        self.assertEqual(result, True)
        result = await d.async_get_state()
        self.assertEqual(result, "OFF")


    @unittest.skip("Broken")
    def test_observation(self):

        obs_count = 0
        def cb(state):
            nonlocal obs_count
            self.assertIn(state, ["ON","OFF"])
            obs_count += 1

        async def test():
            d = mtlib.Device(DEVICE_IP)
            state = await d.async_observe_state(cb) #Start the observation
            self.assertIn(state, ["ON","OFF"])

            await d.async_toggle()
            await asyncio.sleep(1) #Sleep for a second to give time for the observation to arrive
            d.cancel_observe_state()

        self.loop.run_until_complete( test() )   

        self.assertEqual(obs_count, 1)




    @unittest.skip("Broken")
    def test_invalid_port(self):
        d = mtlib.Device(DEVICE_IP, 5555)
        with self.assertRaises(mtlib.exceptions.ConnectionRefused):
            result = self.loop.run_until_complete( d.async_get_state() )   




    @unittest.skip("Broken")
    def test_valid_port(self):
        d = mtlib.Device(DEVICE_IP, 5683)
        result = self.loop.run_until_complete( d.async_get_state() )   
        self.assertIn(result, ["ON","OFF"])





    @unittest.skip("Broken")
    def test_observe_no_route(self):
        def cb():
            pass

        d = mtlib.Device("192.168.1.1")
        with self.assertRaises(mtlib.exceptions.NoRouteToHost):
            result = self.loop.run_until_complete( d.async_observe_state(cb) )   


    async def test_observe(self):
        d = mtlib.Device(DEVICE_IP)
        count = 1
        async for state in d.async_observe():
            self.assertIn(state, ["ON","OFF"])
            
            count += 1
            if count > 4: break
            asyncio.sleep(3)
            await d.async_toggle()

        d.stop_observe()


# class SyncTest (unittest.TestCase):


#     def test_observe(self):
#         import time
#         def cb (state):
#             print(state)

#         d = mtlib.Device(DEVICE_IP)
#         d.observe(cb)
#         time.sleep(10)
#         d.stop_observe()

