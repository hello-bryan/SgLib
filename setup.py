from setuptools import setup, find_packages


def find_sub_packages(path, prefix):
    return [".".join([prefix, item]) for item in find_packages(where=path)]


setup(
    name='sg_lib',
    version='1.0.0',
    description='seunggeun.oh library',
    url='https://github.com/hello-bryan/SgLib',
    author='seunggeun',
    author_email='com.bryan.oh@gmail.com',
    license='seunggeun-oh',
    packages=[
        *find_sub_packages(path="seunggeun", prefix="seunggeun")
    ],
    zip_safe=False,
    include_package_data=True,
    package_data={'': ['*/config.yaml', 'config.json']},
    install_requires=[
        'requests>=2.25.1,<3',
        'selenium>=4.0.0',
        'beautifulsoup4>=4.0.1'
    ]
)

