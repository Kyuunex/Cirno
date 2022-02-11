from distutils.core import setup

from cirno.manifest import VERSION

setup(
    name='cirno',
    packages=[
        'cirno',
        'cirno.cogs',
        'cirno.embeds',
        'cirno.modules',
        'cirno.reusables'
    ],
    version=VERSION,
    description='An osu! score tracking bot',
    author='Kyuunex',
    author_email='kyuunex@protonmail.ch',
    url='https://github.com/Kyuunex/Cirno',
    install_requires=[
        'discord.py[voice]==1.7.3',
        'aiosqlite',
        'aioosuapi @ git+https://github.com/Kyuunex/aioosuapi.git@1.2.1'
    ],
)
