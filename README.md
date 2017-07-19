# Binary dependencies
This project builds zip files with executable dependencies for the master's runtime, and then uploads them to PyPi.

## Update or add dependencies
Edit the `build.py` with the wanted dependencies:
```
VERSIONS = (
    ('terraform', '0.9.11'),
    ('consul', '0.8.5')
)
```
Run `build.py`, which will download and create zips and update this README.
Then, do a commit and a GitHub release.

## Currently shipping
Built on: 2017-07-19 15:07:02.761506

| Name | Version | SHA256 |
| ---  | ------- | -----  |
| terraform (linux_amd64) | 0.9.11 | 413f629fe0e53442d83eda75ef7726d8e4b6d1482b88a86d30ff44ec127cb6b9 |
| terraform (windows_amd64) | 0.9.11 | 499e9afd9009382b038331bcd0d460e33b0366494d6b9bdb12ddfd1072245f63 |
| consul (linux_amd64) | 0.8.5 | 0d57a279375f00ead94751ebc4913da317911eb86db98efa367f1cf2f83fb9ff |
| consul (windows_amd64) | 0.8.5 | 3a886302d10fbec646486d44ef419cd9dcdecd19eb927e068d0f5120a0ae4d7b |

