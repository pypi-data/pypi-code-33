from setuptools import setup


setup(
    name="first-worker",
    version="0.1",
    description="First test worker printing some text.",
    packages=["first_worker"],
    entry_points={'skidward.workers': 'first = first_worker'}
)