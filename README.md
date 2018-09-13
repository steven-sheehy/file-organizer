# file-organizer

Renames filename to a standardized format. This includes removing underscores, dashes and converting to title case.

## Test

```shell
python3 -m unittest
```

## Install

```shell
pip3 install titlecase
python3 setup.py install
```

## Execute

```shell
organizer -i ~/Downloads/
```

## Uninstall

```shell
sudo python setup.py install --record files.txt
cat files.txt | xargs rm -rf
```
