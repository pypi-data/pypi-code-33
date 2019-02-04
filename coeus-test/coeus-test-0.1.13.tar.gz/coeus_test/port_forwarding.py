import subprocess
import time

class PortForwarding:
    @staticmethod
    def setup_android_port_forwarding(port, forward_port, timeout=10):
        while timeout > 0:
            try:
                subprocess.call(
                    'adb forward tcp:' + str(forward_port) + ' tcp:' + str(port),
                    shell=True)
                break
            except Exception as e:
                timeout -= 1
                time.sleep(1)

        if timeout <= 0:
            raise Exception("Could not forward port.")


    @staticmethod
    def setup_ios_port_forwarding(port, forward_port, timeout=10):
        while timeout > 0:
            try:
                subprocess.Popen(['iproxy', str(forward_port), str(port)])
                break
            except Exception as e:
                timeout -= 1
                time.sleep(1)

        if timeout <= 0:
            raise Exception("Could not forward port.")