from setuptools import setup


setup(
    name="second-worker",
    version="0.1",
    description="Second test worker printing some text.",
    packages=["second_worker"],
    entry_points={'skidward.workers': 'second = second_worker'}
)