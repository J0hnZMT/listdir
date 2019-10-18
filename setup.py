from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='listdir',
      version='0.1',
      description='Store parent paths, File names, size and hashes of the selected dir to a csv file.',
      long_description=readme(),
      url='https://github.com/J0hnZMT/listdir',
      author='Johnzel Tuddao',
      author_email='tuddaojohnzel@gmail.com',
      license='MIT',
      classifiers=[
                  'Development Status :: 3 - Alpha',
                  'License :: MIT License',
                  'Intended Audience :: Education',
                  'Topic :: Security :: Cryptography',
                  'Topic :: System :: Archiving :: Compression',
                  'Programming Language :: Python 3',
                  'Programming Language :: Python 3.7'],
      keywords='listing of directory',
      packages=['listdir'],
      zip_safe=False,
      entry_points={
          'console_scripts': ['listdir=listdir.listdir:main'],
      },
      include_package_data=True
      )