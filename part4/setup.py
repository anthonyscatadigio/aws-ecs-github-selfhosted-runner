import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="deployment_cluster",
    version="0.0.1",

    description="ECS cluster for deploying an nginx tasks from github action runner",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="author",

    install_requires=[
        "aws-cdk.core==1.119.0",
    ],

    python_requires=">=3.6",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
