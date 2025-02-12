from setuptools import setup, find_packages

setup(
    name="reachy2_expert_agent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        line.strip()
        for line in open("requirements.txt")
        if line.strip() and not line.startswith("#")
    ],
    python_requires=">=3.10",
    author="Pollen Robotics",
    description="An intelligent assistant for the Reachy2 robot platform",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/pollen-robotics/reachy2_expert_agent",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Robotics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
    ],
) 