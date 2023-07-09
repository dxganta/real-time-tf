from setuptools import setup, find_packages

setup(
    name="real-time-tf",
    version="0.1",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'realtime_tf = realtime_tf.realtime_tf:main',
        ],
    },
    install_requires=[
        'pylsl',
        'matplotlib',
        'numpy',
        'scipy'
    ],
)
