from setuptools import setup, find_packages

setup(
    name="real-time-tf",
    version="0.1",
    description="Real time time frequency plotting of EEG data from the Muse headset.",
    keywords="muse time-frequency eeg fft neuroscience",
    url="https://github.com/dxganta/real-time-tf",
    author="Diganta Kalita",
    author_email="digantakalita.ai@gmail.com",
    license="BSD (3-clause)",
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


# todo:
# Add documentation
# Add more options to the time-frequency calculation (like channel selection instead of averaging channels)
# Double check that the time-frequency algorithm is correct
# Update the data on neuroslack channel