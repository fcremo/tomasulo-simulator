import setuptools

setuptools.setup(
    name="tomasulo_simulator",
    version="0.0.1",
    author="Filippo Cremonese",
    author_email="",
    description="Tomasulo Algorithm simulation library",
    long_description="",
    long_description_content_type="text/markdown",
    url="https://github.com/fcremo/tomasulo-simulator",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    include_package_data=True,
    package_data={
        '': ["*.lark"]
    }
)
